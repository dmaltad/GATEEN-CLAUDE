from django.conf import settings


def site_settings(request):
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'Gateen Petshop'),
        'SITE_TAGLINE': getattr(settings, 'SITE_TAGLINE', 'Cuidando do seu pet com amor'),
    }