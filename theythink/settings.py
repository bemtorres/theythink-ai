"""Configuración principal de Django para THEYTHINK AI."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    os.getenv("FLASK_SECRET_KEY", "theythink-django-secret-key-2026-auth"),
)

DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t", "yes")

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "agentes.apps.AgentesConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "theythink.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [
            BASE_DIR / "agentes" / "templates",
            BASE_DIR / "templates",
        ],
        "APP_DIRS": False,
        "OPTIONS": {
            "environment": "theythink.jinja2.environment",
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "agentes" / "templates",
            BASE_DIR / "templates",
        ],
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

WSGI_APPLICATION = "theythink.wsgi.application"
ASGI_APPLICATION = "theythink.asgi.application"

# Base de datos SQLite unificada con agentes2016.db
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "agentes2016.db",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-es"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "agentes" / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Permitir URLs con y sin barra final para compatibilidad con fetch API
APPEND_SLASH = False

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Configuración de carga de avatares
AVATAR_UPLOAD_FOLDER = BASE_DIR / "agentes" / "static" / "uploads" / "avatars"
os.makedirs(AVATAR_UPLOAD_FOLDER, exist_ok=True)
