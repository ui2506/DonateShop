from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'Change_this_key' # CHANGE KEY!

DEBUG = True # DISABLE IN PRODUCTION MODE!
APPEND_SLASH = True
SESSION_COOKIE_AGE = 7 * 24 * 60 * 60

ALLOWED_HOSTS = ['127.0.0.1', 'yourdomain.com'] # CHANGE TO YOUR DOMAIN
CSRF_TRUSTED_ORIGINS = ['https://yourdomain.com'] # CHANGE TO YOUR DOMAIN

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    'social_django',
    'rest_framework',
    'corsheaders',

    'api',
    'admin',
    'main',
    'donate',
    'faq',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'DonateShop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'DonateShop.wsgi.application'

# Change to your data dase

# DO NOT USE SQLLITE3 IN PRODUCTION!
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'default.db',
    },
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'website',
#         'USER': 'website_admin',
#         'PASSWORD': 'password',
#         'HOST': '127.0.0.1',
#         'PORT': '3306',
#         'OPTIONS': {
#             'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
#         }
#     }
# }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

API_KEY = ["CHANGE_API_KEY"] # CHANGE API KEY TO RANDOM
API_IP = ["127.0.0.1"] # CHANGE IP WHITE LIST FOR API

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'social_core.backends.steam.SteamOpenId',
    'django.contrib.auth.backends.ModelBackend',
)

# USE YOUR OWN PAYMENT SYSTEM AND CHANGE PAYMENT PROCESS IN /donate/views.py (def create_payment_v2)
ANTILOPAY_PROJECT_ID = ""
ANTILOPAY_SUCCESS_URL = ""
ANTILOPAY_FAIL_URL = ""
ANTILOPAY_SECRET_ID = ""
ANTILOPAY_SECRET_KEY = ""

SOCIAL_AUTH_STEAM_API_KEY = '622A802C0389AB64289C6F6CCE1722D2' # CHANGE TO YOUR STEAM API KEY
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
LOGIN_REDIRECT_URL = '/profile/'
LOGOUT_REDIRECT_URL = '/'

AUTH_USER_MODEL = "main.Player"

SOCIAL_AUTH_RAISE_EXCEPTIONS = False

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',

    'main.pipeline.get_or_create_steam_user',
    'main.pipeline.save_steam_id',

    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

USE_X_FORWARDED_HOST = True
X_FRAME_OPTIONS = "DENY"

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "access": {
            "format": "[{asctime}] {levelname:<7} {ip:<15} {os:<12} {browser:<15} {method:<6} {path} → {status}",
            "style": "{",
        },
        "django": {
            "format": "[{asctime}] {levelname:<7} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console_access": {
            "class": "logging.StreamHandler",
            "formatter": "access",
        },
        "console_django": {
            "class": "logging.StreamHandler",
            "formatter": "django",
        },
    },
    "loggers": {
        "access": {
            "handlers": ["console_access"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console_django"],
            "level": "INFO",
            "propagate": False,
        },
    },
}