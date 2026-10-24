"""Mapeo de URLs para la aplicación Agentes."""

from django.urls import re_path
from . import views

def agent_detail_dispatcher(request, nombre):
    if request.method == "DELETE":
        return views.api_delete_agent(request, nombre)
    return views.api_get_agent(request, nombre)

urlpatterns = [
    # Vistas Web Principales
    re_path(r"^$", views.home_view, name="inicio"),
    re_path(r"^agente/(?P<nombre>[^/]+)/?$", views.chat_view, name="pagina_chat"),
    re_path(r"^agente/(?P<nombre>[^/]+)/whatsapp/?$", views.whatsapp_view, name="pagina_chat_whatsapp"),
    re_path(r"^agente/(?P<nombre>[^/]+)/whatsaap/?$", views.whatsapp_view, name="pagina_chat_whatsaap"),
    re_path(r"^admin/whatsapp/?$", views.admin_whatsapp_list_view, name="admin_whatsapp_lista"),
    re_path(r"^admin/whatsaap/?$", views.admin_whatsapp_list_view, name="admin_whatsapp_lista_alt"),
    re_path(r"^admin/whatsapp/(?P<nombre>[^/]+)/?$", views.admin_whatsapp_chat_view, name="admin_whatsapp_chat"),
    re_path(r"^admin/whatsaap/(?P<nombre>[^/]+)/?$", views.admin_whatsapp_chat_view, name="admin_whatsapp_chat_alt"),
    re_path(r"^agente/(?P<nombre>[^/]+)/telegram/?$", views.telegram_view, name="pagina_chat_telegram"),
    re_path(r"^admin/telegram/?$", views.admin_telegram_list_view, name="admin_telegram_lista"),
    re_path(r"^admin/telegram/(?P<nombre>[^/]+)/?$", views.admin_telegram_chat_view, name="admin_telegram_chat"),

    # Autenticación y Dashboard
    re_path(r"^login/?$", views.login_view, name="pagina_login"),
    re_path(r"^logout/?$", views.logout_action, name="cerrar_sesion"),
    re_path(r"^dashboard/?$", views.dashboard_view, name="pagina_dashboard"),
    re_path(r"^admin/?$", views.dashboard_view, name="admin_dashboard"),
    re_path(r"^grupos/?$", views.crear_grupo_view, name="crear_grupo_view"),
    re_path(r"^grupos/asignar/?$", views.asignar_grupo_view, name="asignar_grupo_view"),

    # API REST JSON
    re_path(r"^api/dashboard/stats/?$", views.api_dashboard_stats, name="api_dashboard_stats"),
    re_path(r"^api/upload/avatar/?$", views.api_upload_avatar, name="api_upload_avatar"),
    re_path(r"^api/agentes/?$", views.api_create_agent, name="api_create_agent"),
    re_path(r"^api/agente/(?P<nombre>[^/]+)/?$", agent_detail_dispatcher, name="api_agent_detail"),
    re_path(r"^api/agente/(?P<nombre>[^/]+)/perfil/?$", views.api_update_agent_profile, name="api_update_agent_profile"),
    re_path(r"^api/agente/(?P<nombre>[^/]+)/conocimiento/?$", views.api_update_agent_knowledge, name="api_update_agent_knowledge"),
    re_path(r"^api/agente/(?P<nombre>[^/]+)/identidad/?$", views.api_change_agent_identity, name="api_change_agent_identity"),
    re_path(r"^api/agente/(?P<nombre>[^/]+)/editar/?$", views.api_edit_agent, name="api_edit_agent"),
    re_path(r"^api/agente/(?P<nombre>[^/]+)/limpiar/?$", views.api_clear_agent_memory, name="api_clear_agent_memory"),

    # API: Roles e Identidades
    re_path(r"^api/roles/?$", views.api_roles_collection, name="api_roles_collection"),
    re_path(r"^api/roles/(?P<rol_id>\d+)/?$", views.api_role_item, name="api_role_item"),

    # API: Usuarios y Perfil
    re_path(r"^api/usuarios/?$", views.api_users_collection, name="api_users_collection"),
    re_path(r"^api/usuario/(?P<usuario_id>\d+)/?$", views.api_user_item, name="api_user_item"),
    re_path(r"^api/perfil/?$", views.api_my_profile, name="api_my_profile"),

    # API: Sesiones y Mensajes
    re_path(r"^api/sesiones/?$", views.api_all_sessions, name="api_all_sessions"),
    re_path(r"^api/agente/(?P<nombre>[^/]+)/sesiones/?$", views.api_agent_sessions, name="api_agent_sessions"),
    re_path(r"^api/sesion/(?P<sesion_id>\d+)/?$", views.api_session_item, name="api_session_item"),
    re_path(r"^api/sesion/(?P<sesion_id>\d+)/mensaje/?$", views.api_send_session_message, name="api_send_session_message"),
    re_path(r"^api/agente/(?P<nombre>[^/]+)/mensaje/?$", views.api_send_agent_message_fallback, name="api_send_agent_message_fallback"),

    # API: Fuentes de Conocimiento
    re_path(r"^api/fuentes/?$", views.api_sources_collection, name="api_sources_collection"),
    re_path(r"^api/fuentes/(?P<fuente_id>\d+)/?$", views.api_source_item, name="api_source_item"),
]
