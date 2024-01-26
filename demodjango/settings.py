"""
Django settings for demodjango project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
import sys
import tempfile
from pathlib import Path
import dj_database_url
import environ
from dbt_copilot_python.network import setup_allowed_hosts
from dbt_copilot_python.utility import is_copilot
from django_log_formatter_asim import ASIMFormatter
from dotenv import load_dotenv

from dbt_copilot_python.database import database_url_from_env

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if (os.getenv("DEBUG") == "True") else False

ALLOWED_HOSTS = setup_allowed_hosts(["*"])
ACTIVE_CHECKS = [x.strip() for x in os.getenv("ACTIVE_CHECKS", "").split(",")]

DLFA_INCLUDE_RAW_LOG = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "asim_formatter": {
            "()": ASIMFormatter,
        },
    },
    "handlers": {
        "asim": {
            "class": "logging.StreamHandler",
            "formatter": "asim_formatter",
            'filters': ['request_id_context'],
        },
        "stdout": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
        },
    },
    "root": {
        "handlers": ["stdout"],
        "level": "DEBUG",
    },
    "loggers": {
        "django": {
            "handlers": [
                "asim",
            ],
            "level": "DEBUG",
            "propagate": True,
        },
        "django.request": {
            "handlers": [
                "asim",
            ],
            "level": "DEBUG",
            "propagate": True,
        },
        'requestlogs': {
            "handlers": [
                "asim",
            ],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'filters': {
        'request_id_context': {
            '()': 'requestlogs.logging.RequestIdContext',
        },
    },
}

DLFA_INCLUDE_RAW_LOG = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'requestlogs.middleware.RequestLogsMiddleware',
    'requestlogs.middleware.RequestIdMiddleware',
]

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'requestlogs.views.exception_handler',
}

ROOT_URLCONF = 'demodjango.urls'

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

WSGI_APPLICATION = 'demodjango.wsgi.application'

sqlite_db_root = BASE_DIR if is_copilot() else Path(tempfile.gettempdir())

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': sqlite_db_root / "demodjango.sqlite3",
    }
}

RDS_DATABASE_CREDENTIALS = os.getenv("RDS_DATABASE_CREDENTIALS", "")

if RDS_DATABASE_CREDENTIALS:
    DATABASES["rds"] = dj_database_url.config(
        default=database_url_from_env("RDS_DATABASE_CREDENTIALS")
    )

DATABASE_CREDENTIALS = os.getenv("DATABASE_CREDENTIALS", "")

if DATABASE_CREDENTIALS:
    DATABASES['aurora'] = dj_database_url.config(
        default=database_url_from_env("DATABASE_CREDENTIALS")
    )

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-uk'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
RESTRICT_ADMIN = env.bool("RESTRICT_ADMIN", True)

REDIS_ENDPOINT = os.getenv("REDIS_ENDPOINT")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "")
OPENSEARCH_ENDPOINT = os.getenv("OPENSEARCH_ENDPOINT", "")

# Celery
CELERY_BROKER_URL = os.getenv("REDIS_ENDPOINT")
if CELERY_BROKER_URL and CELERY_BROKER_URL.startswith("rediss://"):
    CELERY_BROKER_URL = f"{CELERY_BROKER_URL}?ssl_cert_reqs=CERT_REQUIRED"
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
