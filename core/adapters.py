"""
Adapter customizado do django-allauth para a Gateen Petshop.

  1. Redireciona staff → /dashboard/ após login (respeita ?next=)
  2. Mescla carrinho anônimo com o carrinho do usuário no login
"""
from allauth.account.adapter import DefaultAccountAdapter


class GateenAccountAdapter(DefaultAccountAdapter):

    # ── Redirecionamento pós-login ────────────────────────
    def get_login_redirect_url(self, request):
        # Respeita ?next= se for URL interna segura
        next_url = (
            request.GET.get('next') or
            request.POST.get('next') or
            ''
        ).strip()

        if next_url and next_url.startswith('/') and not next_url.startswith('//'):
            return next_url

        if request.user.is_staff:
            return '/dashboard/'
        return '/'

    # ── Merge de carrinho anônimo → usuário ───────────────
    def login(self, request, user):
        # Captura chave da sessão anônima ANTES de o allauth regenerar a sessão
        anon_key = request.session.session_key
        super().login(request, user)
        self._merge_anonymous_cart(request, user, anon_key)

    @staticmethod
    def _merge_anonymous_cart(request, user, anon_key):
        if not anon_key:
            return
        try:
            from apps.orders.models import Cart, CartItem

            anon_cart = Cart.objects.filter(
                session_key=anon_key,
                user__isnull=True,
            ).first()

            if not anon_cart or not anon_cart.items.exists():
                return

            user_cart, _ = Cart.objects.get_or_create(user=user)

            for anon_item in anon_cart.items.select_related('product').all():
                user_item = user_cart.items.filter(product=anon_item.product).first()
                if user_item:
                    user_item.quantity += anon_item.quantity
                    user_item.save(update_fields=['quantity'])
                else:
                    anon_item.cart = user_cart
                    anon_item.save(update_fields=['cart'])

            anon_cart.delete()

        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning(
                'Erro ao mesclar carrinho anônimo: %s', exc
            )

    # ── Limite de 2 e-mails por usuário ──────────────────
    def add_email(self, request, email):
        from allauth.account.models import EmailAddress
        count = EmailAddress.objects.filter(user=request.user).count()
        if count >= 2:
            from django.contrib import messages
            messages.error(
                request,
                'Você pode ter no máximo 2 e-mails cadastrados '
                '(e-mail principal + e-mail de recuperação).'
            )
            return None
        return super().add_email(request, email)