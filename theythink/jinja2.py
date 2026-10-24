"""Configuración del entorno Jinja2 para Django en THEYTHINK AI.

Proporciona compatibilidad completa con la sintaxis y filtros usados en las plantillas:
- url_for('static', filename='...')
- url_for('pagina_chat', nombre=...)
- url_for('inicio', grupo=...)
- filtro tojson
"""

import json
from urllib.parse import urlencode

from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment
from markupsafe import Markup


ENDPOINT_MAP = {
    "inicio": "inicio",
    "home_view": "inicio",
    "pagina_chat": "pagina_chat",
    "chat_view": "pagina_chat",
    "pagina_chat_whatsapp": "pagina_chat_whatsapp",
    "pagina_chat_whatsaap": "pagina_chat_whatsaap",
    "admin_whatsapp_lista": "admin_whatsapp_lista",
    "admin_whatsapp_lista_alt": "admin_whatsapp_lista_alt",
    "admin_whatsapp_chat": "admin_whatsapp_chat",
    "admin_whatsapp_chat_alt": "admin_whatsapp_chat_alt",
    "pagina_chat_telegram": "pagina_chat_telegram",
    "admin_telegram_lista": "admin_telegram_lista",
    "admin_telegram_chat": "admin_telegram_chat",
    "pagina_login": "pagina_login",
    "login_view": "pagina_login",
    "cerrar_sesion": "cerrar_sesion",
    "logout_action": "cerrar_sesion",
    "pagina_dashboard": "pagina_dashboard",
    "dashboard_view": "pagina_dashboard",
    "crear_grupo_view": "crear_grupo_view",
    "asignar_grupo_view": "asignar_grupo_view",
}


def custom_url_for(endpoint, **values):
    """Implementa url_for con soporte para estáticos y reversión de URLs de Django."""
    if endpoint == "static":
        filename = values.get("filename", "")
        return static(filename)

    target_name = ENDPOINT_MAP.get(endpoint, endpoint)
    kwargs = {}
    query_params = {}

    for k, v in values.items():
        if k in ("nombre", "sesion_id", "rol_id", "usuario_id", "fuente_id"):
            kwargs[k] = v
        else:
            query_params[k] = v

    try:
        url = reverse(target_name, kwargs=kwargs) if kwargs else reverse(target_name)
    except Exception:
        url = f"/{endpoint}"

    if query_params:
        url += f"?{urlencode(query_params)}"

    return url


def to_json_filter(value):
    """Serializa un objeto a JSON seguro para scripts y etiquetas HTML."""
    return Markup(json.dumps(value, ensure_ascii=False))


def environment(**options):
    """Crea y configura el entorno Jinja2 para las plantillas de Django."""
    env = Environment(**options)
    env.globals.update({
        "static": static,
        "url": reverse,
        "url_for": custom_url_for,
    })
    env.filters["tojson"] = to_json_filter
    return env
