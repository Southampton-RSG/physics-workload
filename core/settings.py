# -*- encoding: utf-8 -*-
import os, random, string
from pathlib import Path
from typing import Any, Dict, List, Tuple

from decouple import AutoConfig, Csv

from django.contrib import messages


# Load settings.ini from the customisations dir
config: AutoConfig = AutoConfig()

PROJECT_DIR: Path = Path(__file__).parent  # physics-workload/core/
BASE_DIR: Path = Path(__file__).parent.parent  # physics-workload/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY: str = config('SECRET_KEY', default='None')
if not SECRET_KEY:
    SECRET_KEY = ''.join(random.choice( string.ascii_lowercase  ) for i in range( 32 ))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG: bool = config('DEBUG', default=False, cast=bool)

# HOSTs List
ALLOWED_HOSTS: List[str] = [
    'localhost',
    '127.0.0.1',
    '172.18.0.2',
    '0.0.0.0',
    'teaching.physics.soton.ac.uk',
    'srv04619.soton.ac.uk',
    'srv04619',
]
# Add here your deployment HOSTS
CSRF_TRUSTED_ORIGINS: List[str] = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://0.0.0.0:8000',
    'http://172.18.0.2:8000',
    'http://teaching.physics.soton.ac.uk'
    'http://srv04619.soton.ac.uk',
]

# Application definition
INSTALLED_APPS: List[str] = [
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
    'markdownify',

    'users',  # Enable the custom users app
    'app',  # Enable the inner app
]

if DEBUG:
    INSTALLED_APPS += [
        'django_fastdev',
        'django_pycharm_breakpoint',
    ]

MIDDLEWARE: List[str] = [
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

    'iommi.middleware',
]

ROOT_URLCONF: str = 'core.urls'
TEMPLATE_DIR: Path = BASE_DIR / "core" / "templates"  # ROOT dir for templates

TEMPLATES: List[Dict[str, Any]] = [
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

WSGI_APPLICATION: str = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES: Dict[str, Dict] = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'data' / 'db.sqlite3',
    }
}

################################################################################
# DJANGO CORE - AUTHENTICATION
# Password validators: https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators
################################################################################
AUTH_USER_MODEL: str = 'users.CustomUser'
AUTH_PASSWORD_VALIDATORS: List[Dict] = [
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

AUTHENTICATION_BACKENDS: List[str] = [
    'django.contrib.auth.backends.ModelBackend',
]

################################################################################
# DJANGO AUTH ADFS
################################################################################
LOGIN_URL: str = 'django_auth_adfs:login'
LOGIN_REDIRECT_URL: str = 'home'  # Route defined in app/urls.py
LOGOUT_REDIRECT_URL: str = 'home'  # Route defined in app/urls.py

adfs_client_id: str = config('ADFS_CLIENT_ID', default="None")
adfs_client_secret: str = config('ADFS_CLIENT_SECRET', default="None")
adfs_tenant_id: str = config('ADFS_TENANT_ID', default="None")

AUTH_ADFS: Dict[str, Any] = {
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
# Ensures that the URL uses HTTPS, even if Django is serving to Nginx over HTTP
SECURE_PROXY_SSL_HEADER: Tuple[str, str] = ("X-Forwarded-Proto", "https")

################################################################################
# DJANGO CORE - INTERNATIONALISATION
# https://docs.djangoproject.com/en/3.0/topics/i18n/
################################################################################
LANGUAGE_CODE: str = 'en-uk'
TIME_ZONE: str = 'GMT'
USE_I18N: bool = True
USE_L10N: bool = True
USE_TZ: bool = True

################################################################################
# DJANGO CORE - DIRECTORIES
################################################################################
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT: Path = BASE_DIR / 'staticfiles'
STATIC_URL: str = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS: Tuple[Path] = (
    BASE_DIR / 'app' / 'static',
)

################################################################################
# DJANGO CORE - DATABASE
################################################################################
# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"
EMAIL_BACKEND: str = 'django.core.mail.backends.console.EmailBackend'

################################################################################
# DJANGO CORE - MESSAGES
################################################################################
MESSAGE_TAGS: Dict[int, str] = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

################################################################################
# DJANGO CORE - SITES
################################################################################
SITE_ID: int = 1

################################################################################
# IOMMI
################################################################################
from iommi.style import Style
from app.style import floating_fields_style

IOMMI_DEFAULT_STYLE: Style = floating_fields_style
IOMMI_DEBUG: bool = config("DEBUG_IOMMI", default=False, cast=bool)
IOMMI_MAIN_MENU: str = 'app.urls.main_menu'

################################################################################
# DJANGO SIMPLE HISTORY
################################################################################
# We only want to take a snapshot on year end
SIMPLE_HISTORY_ENABLED: bool = False

################################################################################
# DJANGO PLOTLY DASH
################################################################################
# Allow embedding plots as iframes
X_FRAME_OPTIONS: str = 'SAMEORIGIN'

################################################################################
# DJANGO MARKDOWNIFY
################################################################################
MARKDOWNIFY: Dict[str, Any] = {
    "default": {
        "WHITELIST_TAGS": [
            'a',
            'abbr',
            'acronym',
            'b',
            'blockquote',
            'em',
            'i',
            'li',
            'ol',
            'p',
            'strong',
            'ul',
            'h1',
            'h2',
            'h3',
            'h4',
        ]
    }
}

################################################################################
# DJANGO CORE - LOGGING
################################################################################
from logging import LogRecord
LOG_DIRECTORY: Path = BASE_DIR / 'logs'


def skip_static_records(record: LogRecord) -> bool:
    """
    Skip log messages to the static file directory.

    :param record:
    :return:
    """
    return hasattr(record, 'message') and not 'GET /static/' in record.message


LOGGING: Dict[str, Any] = {
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
            "handlers": ["file_django"],
            "propagate": False,
        },
        "app": {
            "level": "DEBUG",
            "handlers": ["file_app"],
            "propagate": False,
        },
        "users": {
            "level": "DEBUG",
            "handlers": ["file_users"],
            "propagate": False,
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

ICON_HISTORY: str = 'clock-rotate-left'
ICON_EDIT: str = 'pencil'
ICON_DELETE: str = 'trash'
ICON_CREATE: str = 'plus'
