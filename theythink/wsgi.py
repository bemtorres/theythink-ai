"""Configuración WSGI para el proyecto THEYTHINK AI en Django."""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "theythink.settings")

application = get_wsgi_application()
