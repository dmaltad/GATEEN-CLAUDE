import socket
import re
from allauth.account.adapter import DefaultAccountAdapter


# Domínios claramente inválidos / descartáveis comuns
_BLOCKLIST = {
    'mailinator.com', 'guerrillamail.com', 'tempmail.com', 'throwam.com',
    'sharklasers.com', 'guerrillamailblock.com', 'grr.la', 'guerrillamail.info',
    'spam4.me', 'yopmail.com', 'dispostable.com', 'trashmail.com',
    'trashmail.me', 'trashmail.net', 'discard.email', 'fakeinbox.com',
}

_EMAIL_RE = re.compile(
    r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
)


def _domain_has_dns(domain: str) -> bool:
    """
    Verifica se o domínio possui pelo menos um registro DNS resolvível.
    Não garante que a caixa existe, mas filtra domínios inexistentes.
    """
    try:
        socket.setdefaulttimeout(3)
        socket.getaddrinfo(domain, None)
        return True
    except (socket.gaierror, socket.herror, OSError):
        return False


class GateenAccountAdapter(DefaultAccountAdapter):

    # ── Validação de e-mail ───────────────────────────────────
    def clean_email(self, email: str) -> str:
        from django.core.exceptions import ValidationError

        email = super().clean_email(email)
        email_lower = email.lower()

        # 1. Formato básico
        if not _EMAIL_RE.match(email_lower):
            raise ValidationError(
                'Informe um endereço de e-mail válido (ex: nome@dominio.com).'
            )

        # 2. Domínio descartável
        domain = email_lower.split('@')[1]
        if domain in _BLOCKLIST:
            raise ValidationError(
                'E-mails temporários ou descartáveis não são permitidos. '
                'Use seu e-mail pessoal ou corporativo.'
            )

        # 3. Domínio com DNS válido
        if not _domain_has_dns(domain):
            raise ValidationError(
                f'O domínio "@{domain}" não parece existir. '
                'Verifique se digitou o e-mail corretamente.'
            )

        return email

    # ── Redirecionamento pós-login ────────────────────────────
    def get_login_redirect_url(self, request):
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

    # ── Merge de carrinho anônimo → usuário ───────────────────
    def login(self, request, user):
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
                session_key=anon_key, user__isnull=True,
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

    # ── Limite de 2 e-mails por usuário ──────────────────────
    def add_email(self, request, email):
        from allauth.account.models import EmailAddress
        count = EmailAddress.objects.filter(user=request.user).count()
        if count >= 2:
            from django.contrib import messages
            messages.error(
                request,
                'Você pode ter no máximo 2 e-mails cadastrados.'
            )
            return None
        return super().add_email(request, email)