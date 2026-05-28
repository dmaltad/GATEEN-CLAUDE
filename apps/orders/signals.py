"""
Signal de fidelidade + notificações por e-mail para pedidos.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction as db_transaction
from django.db.models import Q

from .models import Order

logger = logging.getLogger(__name__)


# ── Loyalty signal ────────────────────────────────────────────

@receiver(post_save, sender=Order)
def process_loyalty_on_order_save(sender, instance, created, **kwargs):
    if created:
        db_transaction.on_commit(lambda: _on_order_created(instance))
        return

    if instance.status == 'delivered':
        from apps.loyalty.models import LoyaltyTransaction
        already = LoyaltyTransaction.objects.filter(order=instance).exists()
        if not already:
            db_transaction.on_commit(lambda: _credit_points(instance))

    # E-mail de mudança de status (exceto na criação)
    db_transaction.on_commit(lambda: _email_order_status(instance))


def _on_order_created(order):
    _credit_points(order)
    _email_order_created(order)


# ── E-mail: pedido criado ─────────────────────────────────────

def _email_order_created(order):
    from apps.core_app.email_utils import send_gateen_email
    send_gateen_email(
        to_email      = order.user.email,
        subject       = f'Pedido #{order.order_number} recebido!',
        template_name = 'order_created',
        context       = {'order': order, 'user': order.user},
    )


# ── E-mail: status do pedido mudou ────────────────────────────

def _email_order_status(order):
    # Não envia e-mail para o status inicial 'pending' (já enviado em _on_order_created)
    if order.status == 'pending':
        return
    from apps.core_app.email_utils import send_gateen_email
    send_gateen_email(
        to_email      = order.user.email,
        subject       = f'Pedido #{order.order_number} — {order.get_status_display()}',
        template_name = 'order_status_changed',
        context       = {'order': order, 'user': order.user},
    )


# ── Fidelidade ────────────────────────────────────────────────

def _credit_points(order):
    from apps.loyalty.models import LoyaltyAccount, LoyaltyRule, LoyaltyTransaction
    from django.utils import timezone

    account, _ = LoyaltyAccount.objects.get_or_create(
        user=order.user,
        defaults={'points': 0, 'lifetime_points': 0, 'level': 'bronze'}
    )

    today = timezone.now().date()
    rules = LoyaltyRule.objects.filter(
        is_active=True,
        reward_type='loyalty_points',
    ).filter(
        Q(valid_from__isnull=True) | Q(valid_from__lte=today)
    ).filter(
        Q(valid_until__isnull=True) | Q(valid_until__gte=today)
    ).select_related('trigger_brand', 'trigger_product')

    total_earned = 0
    rule_log     = []

    for rule in rules:
        pts = _apply_rule(rule, order)
        if pts > 0:
            total_earned += pts
            rule_log.append(f'{rule.name}: +{pts}')

    if total_earned == 0 and order.total:
        total_earned = max(1, int(order.total))
        rule_log.append(f'Base R${order.total}: +{total_earned}')

    if total_earned <= 0:
        return

    account.points          += total_earned
    account.lifetime_points += total_earned
    account.save(update_fields=['points', 'lifetime_points'])
    account.update_level()

    LoyaltyTransaction.objects.create(
        account=account,
        transaction_type='earn',
        points=total_earned,
        description=(f'Pedido #{order.order_number} | ' + ' | '.join(rule_log))[:300],
        order=order,
    )

    logger.info('[Fidelidade] %s | +%d pts | %s', order.order_number, total_earned, order.user.email)


def _apply_rule(rule, order):
    fn = {
        'amount_spent':      _rule_amount_spent,
        'brand_purchase':    _rule_brand_purchase,
        'product_purchase':  _rule_product_purchase,
        'category_purchase': _rule_category_purchase,
    }.get(rule.rule_type)
    return fn(rule, order) if fn else 0

def _rule_amount_spent(rule, order):
    if not rule.trigger_amount or rule.trigger_amount <= 0:
        return 0
    if order.total < rule.trigger_amount:
        return 0
    return int(order.total / rule.trigger_amount) * rule.reward_points

def _rule_brand_purchase(rule, order):
    if not rule.trigger_brand_id:
        return 0
    qty = sum(
        item.quantity
        for item in order.items.select_related('product').all()
        if item.product.brand_id == rule.trigger_brand_id
    )
    return rule.reward_points if qty >= rule.trigger_quantity else 0

def _rule_product_purchase(rule, order):
    if not rule.trigger_product_id:
        return 0
    qty = sum(
        item.quantity for item in order.items.all()
        if item.product_id == rule.trigger_product_id
    )
    return rule.reward_points if qty >= rule.trigger_quantity else 0

def _rule_category_purchase(rule, order):
    if not rule.trigger_product_id:
        return 0
    cat_id = rule.trigger_product.category_id
    cat_total = sum(
        item.unit_price * item.quantity
        for item in order.items.select_related('product').all()
        if item.product.category_id == cat_id
    )
    min_val = rule.trigger_amount or 0
    return rule.reward_points if cat_total >= min_val else 0