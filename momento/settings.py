from datetime import timedelta
from pathlib import Path

from configurations import Configuration
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent


class Base(Configuration):
    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = "django-insecure-_qj56ync!$b*vwm2gc$5x4$^4kz$*9o$v%^iuvva4^w5_3qdxz"

    DJANGO_APPS = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    ]

    THIRD_PARTY_APPS = [
        "rest_framework",
        "drf_spectacular",
        "rest_framework_simplejwt",
        "corsheaders",
        "drf_standardized_errors",
    ]

    LOCAL_APPS = ["user", "post"]

    INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "corsheaders.middleware.CorsMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

    ROOT_URLCONF = "momento.urls"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [BASE_DIR / "templates"],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

    AUTH_USER_MODEL = "user.User"

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/5.2/howto/static-files/

    STATIC_URL = "static/"

    AUTHENTICATION_BACKENDS = [
        "momento.core.authentication.AuthenticationBackend",
        "django.contrib.auth.backends.ModelBackend",
    ]

    # Rest framework
    REST_FRAMEWORK = {
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework_simplejwt.authentication.JWTAuthentication",
        ],
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
        "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
        "PAGE_SIZE": 10,
    }

    # DRF Spectacular
    SPECTACULAR_SETTINGS = {
        "TITLE": "Momento",
        "DESCRIPTION": "Momento API",
        "VERSION": "1.0.0",
    }

    # Email Settings
    EMAIL_BACKEND = config(
        "email_backend", "django.core.mail.backends.smtp.EmailBackend"
    )
    EMAIL_USE_TLS = config("email_use_tls", True)
    EMAIL_HOST = config("email_host", "smtp.gmail.com")
    EMAIL_HOST_USER = config("email_user", "iamnasir345@gmail.com")
    EMAIL_HOST_PASSWORD = config("email_password", "pzhdowuzvtwjifvj")
    EMAIL_PORT = config("email_port", 587)

    DEFAULT_FROM_EMAIL = config("default_from_email", "nasir@momento.com")

    SIMPLE_JWT = {
        "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
        "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
        "ROTATE_REFRESH_TOKENS": False,
        "BLACKLIST_AFTER_ROTATION": False,
        "UPDATE_LAST_LOGIN": True,
    }


class Dev(Base):
    DEBUG = True
    ALLOWED_HOSTS = ["*"]
    CORS_ORIGIN_ALLOW_ALL = True
    DRF_STANDARDIZED_ERRORS = {"ENABLE_IN_DEBUG_FOR_UNHANDLED_EXCEPTIONS": True}

    # Media files
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

    # Static files
    STATIC_ROOT = BASE_DIR / "static"
