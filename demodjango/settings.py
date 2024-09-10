"""
Django settings for demodjango project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import sys
from pathlib import Path

import environ
import sentry_sdk
from dbt_copilot_python.database import database_from_env
from dbt_copilot_python.network import setup_allowed_hosts
from django.urls import reverse_lazy
from django_log_formatter_asim import ASIMFormatter
from dotenv import find_dotenv
from sentry_sdk.integrations.django import DjangoIntegration

env_file = find_dotenv(usecwd=True)

if env_file:
    environ.Env.read_env(env_file)

env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = setup_allowed_hosts(["*"])

ACTIVE_CHECKS = [el.strip() for el in env("ACTIVE_CHECKS", default="").split(",")]

IS_API = env("IS_API", default="False") == "True"

DLFA_INCLUDE_RAW_LOG = True

BASIC_AUTH_USERNAME = env("BASIC_AUTH_USERNAME", default="")
BASIC_AUTH_PASSWORD = env("BASIC_AUTH_PASSWORD", default="")

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
            "filters": ["request_id_context"],
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
        "requestlogs": {
            "handlers": [
                "asim",
            ],
            "level": "INFO",
            "propagate": False,
        },
    },
    "filters": {
        "request_id_context": {
            "()": "requestlogs.logging.RequestIdContext",
        },
    },
}

DLFA_INCLUDE_RAW_LOG = True

# Application definition

INSTALLED_APPS = [
    "django_celery_beat",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "authbroker_client",
    "app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "requestlogs.middleware.RequestLogsMiddleware",
    "requestlogs.middleware.RequestIdMiddleware",
]

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "requestlogs.views.exception_handler",
}

ROOT_URLCONF = "demodjango.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "demodjango.wsgi.application"

# Django requires a default database. If RDS is present make it the default
# database to enable celery-beat
RDS_POSTGRES_CREDENTIALS = env("RDS_POSTGRES_CREDENTIALS", default="")
if RDS_POSTGRES_CREDENTIALS:
    DATABASES = database_from_env("RDS_POSTGRES_CREDENTIALS")
    # Because it comes in from the environment as postgres, not postgresql...
    DATABASES["default"]["ENGINE"] = "django.db.backends.postgresql"
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "demodjango.sqlite",
        }
    }

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-uk"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
RESTRICT_ADMIN = env.bool("RESTRICT_ADMIN", default=True)

REDIS_ENDPOINT = env("REDIS_ENDPOINT", default="")
S3_BUCKET_NAME = env("S3_BUCKET_NAME", default="")
OPENSEARCH_ENDPOINT = env("OPENSEARCH_ENDPOINT", default="")

# Celery
CELERY_BROKER_URL = env("REDIS_ENDPOINT", default="")
if CELERY_BROKER_URL and CELERY_BROKER_URL.startswith("rediss://"):
    CELERY_BROKER_URL = f"{CELERY_BROKER_URL}?ssl_cert_reqs=CERT_REQUIRED"
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"

# authbroker config
AUTHBROKER_URL = env("AUTHBROKER_URL", default="")
AUTHBROKER_CLIENT_ID = env("AUTHBROKER_CLIENT_ID", default="")
AUTHBROKER_CLIENT_SECRET = env("AUTHBROKER_CLIENT_SECRET", default="")
AUTHBROKER_STAFF_SSO_SCOPE = env("AUTHBROKER_STAFF_SSO_SCOPE", default="")
AUTHBROKER_ANONYMOUS_PATHS = env.list("AUTHBROKER_ANONYMOUS_PATHS", default=[])
AUTHBROKER_ANONYMOUS_URL_NAMES = env.list("AUTHBROKER_ANONYMOUS_URL_NAMES", default=[])
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "authbroker_client.backends.AuthbrokerBackend",
]
LOGIN_URL = reverse_lazy("authbroker_client:login")
LOGIN_REDIRECT_URL = reverse_lazy("index")

SENTRY_DSN = env("SENTRY_DSN", default="")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
    )

STATIC_S3_ENDPOINT = env("STATIC_S3_ENDPOINT")
