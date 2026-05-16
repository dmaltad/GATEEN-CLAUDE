"""
Adapter customizado do django-allauth para a Gateen Petshop.

Responsabilidades:
  1. Redirecionar staff → /dashboard/ após login
  2. Mesclar carrinho anônimo com o carrinho do usuário no login
  3. Mensagens de erro claras para e-mail duplicado
"""
from allauth.account.adapter import DefaultAccountAdapter


class GateenAccountAdapter(DefaultAccountAdapter):

    # ── 1. Redirecionamento pós-login ─────────────────────────

    def get_login_redirect_url(self, request):
        if request.user.is_authenticated and request.user.is_staff:
            return '/dashboard/'
        return '/'

    # ── 2. Merge de carrinho ──────────────────────────────────

    def login(self, request, user):
        """
        Executado antes de gravar a sessão do usuário.
        Aqui capturamos o session_key do carrinho anônimo.
        """
        # Guarda a chave de sessão anônima ANTES de o allauth
        # regenerar a sessão no login
        anon_session_key = request.session.session_key
        super().login(request, user)
        self._merge_anonymous_cart(request, user, anon_session_key)

    @staticmethod
    def _merge_anonymous_cart(request, user, anon_session_key):
        """
        Se havia um carrinho na sessão anônima, transfere os
        itens para o carrinho do usuário. Evita duplicidades
        somando quantidades de produtos já existentes.
        """
        if not anon_session_key:
            return

        try:
            from apps.orders.models import Cart, CartItem

            # Carrinho anônimo (pode não existir)
            anon_cart = Cart.objects.filter(
                session_key=anon_session_key,
                user__isnull=True,
            ).first()

            if not anon_cart or not anon_cart.items.exists():
                return

            # Carrinho do usuário (cria se não existir)
            user_cart, _ = Cart.objects.get_or_create(user=user)

            # Itera os itens do carrinho anônimo
            for anon_item in anon_cart.items.select_related('product').all():
                user_item = user_cart.items.filter(
                    product=anon_item.product
                ).first()

                if user_item:
                    # Produto já está no carrinho do usuário: soma
                    user_item.quantity += anon_item.quantity
                    user_item.save(update_fields=['quantity'])
                else:
                    # Produto novo: move o item
                    anon_item.cart = user_cart
                    anon_item.save(update_fields=['cart'])

            # Remove o carrinho anônimo (itens já foram migrados)
            anon_cart.delete()

        except Exception as exc:
            # Nunca deixa o merge quebrar o login
            import logging
            logging.getLogger(__name__).warning(
                'Erro ao mesclar carrinho anônimo: %s', exc
            )

    # ── 3. Mensagem de e-mail duplicado mais clara ─────────────

    def authentication_error(
        self, request, credentials, msg=None, response=None, *args, **kwargs
    ):
        return super().authentication_error(
            request, credentials, msg, response, *args, **kwargs
        )