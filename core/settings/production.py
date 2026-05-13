from .base import *
import dj_database_url

DEBUG = False

DATABASES = {
    'default': dj_database_url.config(default=env('DATABASE_URL'))
}

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'