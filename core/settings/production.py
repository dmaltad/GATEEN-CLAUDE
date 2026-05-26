from .base import *
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['gateenpetshop.com.br'])

# ── Banco de dados ─────────────────────────────────────────────
DATABASES = {
    'default': dj_database_url.config(
        default=env('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ── Cache (Redis) ──────────────────────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'KEY_PREFIX': 'gateen',
        'TIMEOUT': 300,
    }
}

# Sessões no Redis (não consulta o banco a cada requisição)
SESSION_ENGINE     = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# ── Templates com cache em memória ─────────────────────────────
TEMPLATES[0].pop('APP_DIRS', None)
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

# ── Segurança ──────────────────────────────────────────────────
SECURE_BROWSER_XSS_FILTER   = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS             = 'DENY'

# False porque a Cloudflare já faz o redirect HTTP→HTTPS.
# True aqui causaria loop de redirecionamento.
SECURE_SSL_REDIRECT         = False

# Diz ao Django que a conexão é HTTPS mesmo chegando via proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE    = True
# ── HSTS ───────────────────────────────────────────────────────
# Cloudflare já faz o redirect, por isso SECURE_SSL_REDIRECT = False.
# O HSTS instrui os navegadores a sempre usarem HTTPS diretamente.
SECURE_HSTS_SECONDS           = 31536000  # 1 ano
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD           = True

# Silencia o warning do SSL_REDIRECT pois a Cloudflare já redireciona
SILENCED_SYSTEM_CHECKS = ['security.W008']
CSRF_TRUSTED_ORIGINS  = env.list('CSRF_TRUSTED_ORIGINS', default=[
    'https://gateenpetshop.com.br',
    'https://www.gateenpetshop.com.br',
])

# ── E-mail (Hostinger SMTP) ────────────────────────────────────
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = env('EMAIL_HOST',     default='smtp.hostinger.com')
EMAIL_PORT          = env.int('EMAIL_PORT', default=465)
EMAIL_USE_TLS       = env.bool('EMAIL_USE_TLS', default=False)
EMAIL_USE_SSL       = env.bool('EMAIL_USE_SSL', default=True)
EMAIL_HOST_USER     = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL  = 'Não Responda - Gateen Petshop <nao-responda@gateenpetshop.com.br>'
SERVER_EMAIL        = DEFAULT_FROM_EMAIL

ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

# ── Logging ────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/gateenpetshop/django.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}