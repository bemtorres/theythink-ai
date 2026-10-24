"""Configuración ASGI para el proyecto THEYTHINK AI en Django."""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "theythink.settings")

application = get_asgi_application()
