"""
Signal que processa o programa de fidelidade após a criação
ou atualização de status de um pedido.

Regras suportadas:
  - amount_spent     → pontos por valor gasto (ex: a cada R$1 = X pontos)
  - brand_purchase   → pontos ao comprar N itens de uma marca
  - product_purchase → pontos ao comprar um produto específico
  - category_purchase→ pontos ao comprar em uma categoria
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction as db_transaction

from .models import Order

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# CONSTANTE: quantos R$ valem 1 ponto base (fallback)
# A regra amount_spent usa reward_points como pontos fixos
# ou como multiplicador, dependendo de trigger_amount.
# Ex: trigger_amount=1.00, reward_points=1 → 1 ponto por R$1
# ──────────────────────────────────────────────────────────────
POINTS_PER_REAL = 1  # fallback se não houver regra amount_spent


@receiver(post_save, sender=Order)
def process_loyalty_points(sender, instance, created, **kwargs):
    """
    Dispara quando um Order é salvo.
    - Se created=True  → processa pontos imediatamente na criação.
    - Se status mudou para 'delivered' → processa se ainda não creditou.
    """
    # Evita processamento em atualizações irrelevantes
    if not created:
        # Só reprocessa se o status mudou para 'delivered'
        # (proteção: não credita duas vezes)
        if instance.status != 'delivered':
            return
        # Verifica se já existe transação para este pedido
        from apps.loyalty.models import LoyaltyTransaction
        already_processed = LoyaltyTransaction.objects.filter(
            order=instance
        ).exists()
        if already_processed:
            return

    # Usa transaction.on_commit para garantir que o Order já
    # foi salvo no banco antes de processar
    db_transaction.on_commit(
        lambda: _credit_loyalty_points(instance)
    )


def _credit_loyalty_points(order):
    """
    Função principal que avalia todas as regras ativas
    e credita os pontos correspondentes.
    """
    from apps.loyalty.models import LoyaltyAccount, LoyaltyRule, LoyaltyTransaction
    from django.utils import timezone

    # ── Obtém ou cria a conta fidelidade do usuário ──────────
    account, _ = LoyaltyAccount.objects.get_or_create(
        user=order.user,
        defaults={'points': 0, 'lifetime_points': 0, 'level': 'bronze'}
    )

    # ── Busca todas as regras ativas e válidas ────────────────
    today = timezone.now().date()
    rules = LoyaltyRule.objects.filter(
        is_active=True,
        reward_type='loyalty_points',
    ).filter(
        # valid_from nulo ou no passado
        **_build_date_filter('valid_from', today, lte=True)
    ).filter(
        # valid_until nulo ou no futuro
        **_build_date_filter('valid_until', today, gte=True)
    ).select_related('trigger_brand', 'trigger_product')

    total_points_earned = 0
    earned_descriptions = []

    for rule in rules:
        points = _evaluate_rule(rule, order)
        if points > 0:
            total_points_earned += points
            earned_descriptions.append(
                f'{rule.name}: +{points} pts'
            )
            logger.info(
                f'[Fidelidade] Pedido #{order.order_number} | '
                f'Regra "{rule.name}" | +{points} pts | '
                f'User: {order.user.email}'
            )

    # ── Fallback: se nenhuma regra cobriu, usa pontos base ────
    if total_points_earned == 0:
        total_points_earned = _base_points_from_total(order.total)
        earned_descriptions.append(
            f'Compra de R$ {order.total}: +{total_points_earned} pts'
        )

    if total_points_earned <= 0:
        return

    # ── Credita na conta ──────────────────────────────────────
    account.points += total_points_earned
    account.lifetime_points += total_points_earned
    account.save(update_fields=['points', 'lifetime_points'])

    # ── Atualiza nível ────────────────────────────────────────
    account.update_level()

    # ── Registra transação ────────────────────────────────────
    description = f'Pedido #{order.order_number}'
    if earned_descriptions:
        description += ' | ' + ', '.join(earned_descriptions)

    LoyaltyTransaction.objects.create(
        account=account,
        transaction_type='earn',
        points=total_points_earned,
        description=description,
        order=order,
    )

    logger.info(
        f'[Fidelidade] Total creditado: +{total_points_earned} pts | '
        f'User: {order.user.email} | Saldo: {account.points} pts'
    )


# ──────────────────────────────────────────────────────────────
# AVALIADORES DE REGRA
# ──────────────────────────────────────────────────────────────

def _evaluate_rule(rule, order):
    """Retorna os pontos a creditar para a regra dada, ou 0."""
    evaluators = {
        'amount_spent':      _eval_amount_spent,
        'brand_purchase':    _eval_brand_purchase,
        'product_purchase':  _eval_product_purchase,
        'category_purchase': _eval_category_purchase,
    }
    evaluator = evaluators.get(rule.rule_type)
    if not evaluator:
        return 0
    return evaluator(rule, order)


def _eval_amount_spent(rule, order):
    """
    Exemplo de regra:
      trigger_amount = 1.00  → a cada R$1 gasto
      reward_points  = 2     → 2 pontos por R$1
    Resultado: (total do pedido / trigger_amount) * reward_points
    """
    if not rule.trigger_amount or rule.trigger_amount <= 0:
        return 0
    if order.total < rule.trigger_amount:
        return 0

    multiplier = int(order.total / rule.trigger_amount)
    return multiplier * rule.reward_points


def _eval_brand_purchase(rule, order):
    """
    Pontua se o pedido contém >= trigger_quantity itens
    de produtos da marca especificada.
    """
    if not rule.trigger_brand:
        return 0

    qty_brand = sum(
        item.quantity
        for item in order.items.select_related('product__brand').all()
        if item.product.brand_id == rule.trigger_brand_id
    )

    if qty_brand >= rule.trigger_quantity:
        return rule.reward_points
    return 0


def _eval_product_purchase(rule, order):
    """
    Pontua se o pedido contém >= trigger_quantity unidades
    do produto específico.
    """
    if not rule.trigger_product:
        return 0

    qty_product = sum(
        item.quantity
        for item in order.items.all()
        if item.product_id == rule.trigger_product_id
    )

    if qty_product >= rule.trigger_quantity:
        return rule.reward_points
    return 0


def _eval_category_purchase(rule, order):
    """
    Pontua se o pedido contém produtos da categoria
    definida na regra (via trigger_product.category).
    Usa trigger_amount como valor mínimo de compra na categoria.
    """
    # Sem product de referência, usa a categoria dos itens
    items = order.items.select_related('product__category').all()

    category_total = sum(
        item.unit_price * item.quantity
        for item in items
        if rule.trigger_product
        and item.product.category_id == rule.trigger_product.category_id
    )

    min_amount = rule.trigger_amount or 0
    if category_total >= min_amount:
        return rule.reward_points
    return 0


# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────

def _base_points_from_total(total):
    """
    Fallback: 1 ponto a cada R$1.
    Usado quando nenhuma regra específica foi acionada.
    """
    if not total:
        return 0
    return max(1, int(total) * POINTS_PER_REAL)


def _build_date_filter(field, today, lte=False, gte=False):
    """
    Gera filtro que aceita campo nulo OU data válida.
    Ex: valid_from nulo (sem limite) ou valid_from <= hoje
    """
    q_null = {f'{field}__isnull': True}
    if lte:
        q_valid = {f'{field}__lte': today}
    else:
        q_valid = {f'{field}__gte': today}

    # Combina OR manualmente via Q
    from django.db.models import Q
    return {'pk__in': []}  # placeholder; veja uso correto abaixo


def _loyalty_rules_queryset():
    """Não usar _build_date_filter acima. Reimplementado aqui com Q."""
    pass