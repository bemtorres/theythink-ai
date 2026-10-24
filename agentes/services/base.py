"""Constantes y funciones utilitarias compartidas de la capa de servicios."""

import os
from datetime import datetime
from django.conf import settings

MODELO = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
HISTORIAL_RECIENTE = 10
SIN_MEMORIA = "SIN MEMORIA"
BASE_DATOS = str(settings.DATABASES["default"]["NAME"])


def _ahora_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _fecha_str():
    return datetime.now().strftime("%Y-%m-%d")


def _hora_str():
    return datetime.now().strftime("%H:%M:%S")


def avatar_local(nombre):
    """Avatar generado incluido en el proyecto, si existe para este identificador."""
    if nombre != os.path.basename(nombre) or "/" in nombre or "\\" in nombre:
        return ""
    archivo = nombre + "-v1.png"
    base_dir = settings.BASE_DIR
    ruta_app = base_dir / "agentes" / "static" / "avatars" / "generated" / archivo
    ruta_legacy = base_dir / "static" / "avatars" / "generated" / archivo
    if ruta_app.is_file() or ruta_legacy.is_file():
        return f"/static/avatars/generated/{archivo}"
    return ""


def inicializar():
    """No-op compatible con versiones anteriores; el esquema es gestionado por migraciones."""
    return True
