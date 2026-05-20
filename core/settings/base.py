import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost'])

DJANGO_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

THIRD_PARTY_APPS = [
    'allauth',
    'allauth.account',
    # 'allauth.socialaccount',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_extensions',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.catalog',
    'apps.orders',
    'apps.plans',
    'apps.loyalty',
    'apps.events',
    'apps.dashboard',
    'apps.appointments',
    'apps.core_app',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'core.middleware.ForceIPMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'apps.dashboard.middleware.StaffRequiredMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.orders.context_processors.cart_processor',
                'apps.core_app.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Fortaleza'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'

# django-allauth
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
SITE_ID = 1
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'none'  # 'mandatory' em produção
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ── Allauth customizado ───────────────────────────────────────
ACCOUNT_ADAPTER           = 'core.adapters.GateenAccountAdapter'
ACCOUNT_SIGNUP_FORM_CLASS = 'apps.accounts.forms.CustomSignupForm'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Stripe
STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY', default='')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default='')

# Configurações do site
SITE_NAME = 'Gateen Petshop'
SITE_TAGLINE = 'Cuidando do seu pet com amor'

# ══════════════════════════════════════════════
# JAZZMIN — Configuração do painel administrativo
# ══════════════════════════════════════════════
JAZZMIN_SETTINGS = {
    # ── Identidade ────────────────────────────
    "site_title": "Gateen Admin",
    "site_header": "Gateen Petshop",
    "site_brand": "Gateen",
    "site_logo": "base/img/logo.svg",
    "site_logo_classes": "rounded-circle",
    "site_icon": "base/img/logo.svg",
    "welcome_sign": "Bem-vindo ao painel Gateen 🐾",
    "copyright": "Gateen Petshop © 2026",

    # ── Pesquisa global ───────────────────────
    "search_model": ["accounts.User", "catalog.Product", "orders.Order"],

    # ── Usuário no topo ───────────────────────
    "user_avatar": "avatar",

    # ── Menu topo ─────────────────────────────
    "topmenu_links": [
        {"name": "Ver site", "url": "/", "new_window": True,
         "icon": "fas fa-home"},
        {"name": "Dashboard", "url": "/dashboard/",
         "permissions": ["auth.view_user"], "icon": "fas fa-chart-bar"},
        {"model": "auth.User"},
    ],

    # ── Menu lateral ──────────────────────────
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "auth",
        "accounts",
        "catalog",
        "orders",
        "plans",
        "loyalty",
        "events",
    ],
    "icons": {
        "auth":                     "fas fa-users-cog",
        "auth.user":                "fas fa-user",
        "auth.Group":               "fas fa-users",
        "accounts.User":            "fas fa-user-circle",
        "accounts.Address":         "fas fa-map-marker-alt",
        "accounts.Pet":             "fas fa-paw",
        "catalog.Product":          "fas fa-box",
        "catalog.Category":         "fas fa-th",
        "catalog.Brand":            "fas fa-tag",
        "catalog.Stock":            "fas fa-cubes",
        "catalog.StockMovement":    "fas fa-exchange-alt",
        "orders.Order":             "fas fa-shopping-cart",
        "orders.CashRegister":      "fas fa-cash-register",
        "orders.CashTransaction":   "fas fa-receipt",
        "plans.ServicePlan":        "fas fa-star",
        "plans.UserPlan":           "fas fa-id-card",
        "loyalty.LoyaltyAccount":   "fas fa-gift",
        "loyalty.LoyaltyRule":      "fas fa-award",
        "events.Event":             "fas fa-calendar",
        "events.Promotion":         "fas fa-percent",
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",

    # ── Interface ─────────────────────────────
    "related_modal_active": True,
    "custom_css": None,
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
    "actions_sticky_top": True,
}