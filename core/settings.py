# -*- encoding: utf-8 -*-
import os, random, string
from pathlib import Path
from decouple import AutoConfig, Csv


# Load settings.ini from the customisations dir
config = AutoConfig()


PROJECT_DIR = Path(__file__).parent  # physics-workload/core/
BASE_DIR = Path(__file__).parent.parent  # physics-workload/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='None')
if not SECRET_KEY:
    SECRET_KEY = ''.join(random.choice( string.ascii_lowercase  ) for i in range( 32 ))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG: bool = config('DEBUG', default=False, cast=bool)
DEBUG_ACCESS: bool = config('DEBUG_ACCESS', default=False, cast=bool)

# HOSTs List
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '172.18.0.2',
    '0.0.0.0',
    'teaching.physics.soton.ac.uk',
    'srv04619.soton.ac.uk',
    'srv04619',
]
# Add here your deployment HOSTS
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://0.0.0.0:8000',
    'http://172.18.0.2:8000',
    'http://teaching.physics.soton.ac.uk'
    'http://srv04619.soton.ac.uk',
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'simple_history',
    'iommi',
    'django_plotly_dash.apps.DjangoPlotlyDashConfig',
    'django_auth_adfs',

    'users',  # Enable the custom users app
    'app',  # Enable the inner app
]

MIDDLEWARE = [
    'iommi.live_edit.Middleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'iommi.sql_trace.Middleware',
    'iommi.profiling.Middleware',
    'iommi.experimental.main_menu.main_menu_middleware',

    'simple_history.middleware.HistoryRequestMiddleware',
    'app.middlewares.AjaxMiddleware',

    'iommi.middleware',
]

ROOT_URLCONF = 'core.urls'
LOGIN_REDIRECT_URL = "home"  # Route defined in app/urls.py
LOGOUT_REDIRECT_URL = "home"  # Route defined in app/urls.py
TEMPLATE_DIR = BASE_DIR / "core" / "templates"  # ROOT dir for templates

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
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

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'data' / 'db.sqlite3',
    }
}

################################################################################
# DJANGO CORE - AUTHENTICATION
# Password validators: https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators
################################################################################
AUTH_USER_MODEL = 'users.CustomUser'
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

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

################################################################################
# DJANGO AUTH ADFS
################################################################################
LOGIN_URL = '/oauth2/login'
adfs_client_id = config('ADFS_CLIENT_ID', default="None")
adfs_client_secret = config('ADFS_CLIENT_SECRET', default="None")
adfs_tenant_id = config('ADFS_TENANT_ID', default="None")

AUTH_ADFS = {
    'AUDIENCE': adfs_client_id,
    'CLIENT_ID': adfs_client_id,
    'CLIENT_SECRET': adfs_client_secret,
    'CLAIM_MAPPING': {
        'first_name': 'given_name',
        'last_name': 'family_name',
        'email': 'email'
    },
    'GROUPS_CLAIM': 'roles',
    'MIRROR_GROUPS': True,
    'USERNAME_CLAIM': 'upn',
    'TENANT_ID': adfs_tenant_id,
    'RELYING_PARTY_ID': adfs_client_id,
}
AUTHENTICATION_BACKENDS += [
    'django_auth_adfs.backend.AdfsAuthCodeBackend',
]

################################################################################
# DJANGO CORE - INTERNATIONALISATION
# https://docs.djangoproject.com/en/3.0/topics/i18n/
################################################################################
LANGUAGE_CODE = 'en-uk'
TIME_ZONE = 'GMT'
USE_I18N = True
USE_L10N = True
USE_TZ = True

################################################################################
# DJANGO CORE - DIRECTORIES
################################################################################
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    BASE_DIR / 'app' / 'static',
)

################################################################################
# DJANGO CORE - DATABASE
################################################################################
# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_REDIRECT_URL = '/'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

################################################################################
# DJANGO CORE - SITES:
################################################################################
SITE_ID = 1

################################################################################
# IOMMI
################################################################################
from app.style import base_style

IOMMI_DEFAULT_STYLE = base_style
IOMMI_DEBUG = config("DEBUG_IOMMI", default=False, cast=bool)
IOMMI_MAIN_MENU = 'app.pages.main_menu.main_menu'

################################################################################
# DJANGO SIMPLE HISTORY
################################################################################
# We only want to take a snapshot on year end
SIMPLE_HISTORY_ENABLED = False

################################################################################
# DJANGO PLOTLY DASH
################################################################################
# Allow embedding plots as iframes
X_FRAME_OPTIONS = 'SAMEORIGIN'

################################################################################
# DJANGO CORE - LOGGING
################################################################################
from logging import LogRecord
LOG_DIRECTORY = BASE_DIR / 'logs'

def skip_static_records(record: LogRecord) -> bool:
    """
    Skip log messages to the static file directory.

    :param record:
    :return:
    """
    return hasattr(record, 'message') and not 'GET /static/' in record.message


LOGGING = {
    "version": 1,  # the dictConfig format version
    "disable_existing_loggers": False,  # retain the default loggers
    "handlers": {
        "file_django": {
            "class": "logging.FileHandler",
            "filename": LOG_DIRECTORY / "django.log",
            "formatter": "verbose",
        },
        "file_app": {
            "class": "logging.FileHandler",
            "filename": LOG_DIRECTORY / "django.app.log",
            "formatter": "verbose",
        },
        "file_users": {
            "class": "logging.FileHandler",
            "filename": LOG_DIRECTORY / "django.users.log",
            "formatter": "verbose",
        },
        "console": {
            "class": "logging.StreamHandler",
        }
    },
    "loggers": {
        "": {
            "level": "DEBUG",
            "handlers": ["file_django", "console"],
        },
        "app": {
            "level": "DEBUG",
            "handlers": ["file_app", "console"],
        },
        "users": {
            "level": "DEBUG",
            "handlers": ["file_users", "console"],
        },
    },
    "formatters": {
        "verbose": {
            "format": "{name} {levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
}

################################################################################
# Settings specific to this project:
################################################################################
YEAR_MINIMUM_VALUE: int = 2000
HOURS_MAXIMUM_VALUE: int = 2000
