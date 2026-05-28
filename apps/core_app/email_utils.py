import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)


def send_gateen_email(to_email: str, subject: str, template_name: str, context: dict) -> bool:
    """
    Envia e-mail HTML + texto simples.
    Ignora endereços internos (@gateen.internal) de walk-in sem e-mail real.
    """
    if not to_email or to_email.endswith('@gateen.internal'):
        return False

    context.setdefault('site_name', 'Gateen Petshop')
    context.setdefault(
        'site_url',
        getattr(settings, 'SITE_URL', 'https://gateenpetshop.com.br')
    )

    try:
        html_body = render_to_string(f'emails/{template_name}.html', context)
        text_body = render_to_string(f'emails/{template_name}.txt',  context)

        msg = EmailMultiAlternatives(
            subject=f'[Gateen Petshop] {subject}',
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send()
        logger.info('E-mail enviado → %s | %s', to_email, subject)
        return True

    except Exception as exc:
        logger.error('Falha ao enviar e-mail → %s | %s | %s', to_email, subject, exc)
        return False