"""Fachada de la capa de servicios de la plataforma de agentes (Service Layer Pattern)."""

from .agent_service import (
    actualizar_avatar,
    actualizar_conocimiento,
    actualizar_memoria,
    actualizar_perfil,
    agregar_memorias,
    borrar_memoria,
    cambiar_identidad,
    crear_agente,
    eliminar_agente,
    existe_agente,
    listar_agentes,
    obtener_agente,
)
from .base import (
    BASE_DATOS,
    HISTORIAL_RECIENTE,
    MODELO,
    SIN_MEMORIA,
    avatar_local,
    inicializar,
)
from .chat_service import (
    crear_sesion_chat,
    eliminar_sesion_chat,
    guardar_mensaje,
    listar_sesiones_agente,
    listar_todas_las_sesiones,
    obtener_historial,
    obtener_o_crear_sesion_activa,
    obtener_sesion_chat,
    obtener_todos_mensajes_sesion,
    renombrar_sesion_chat,
)
from .dashboard_service import (
    listar_catalogo_agentes,
    migrar_conocimientos_legacy,
    obtener_estadisticas_dashboard,
    vaciar,
)
from .group_service import (
    asignar_grupo,
    crear_grupo,
    listar_agentes_por_grupo,
    listar_grupos,
    obtener_grupo,
    obtener_grupo_agente,
    obtener_grupo_por_nombre,
)
from .knowledge_service import (
    actualizar_fuente,
    crear_fuente,
    eliminar_fuente,
    establecer_fuentes_agente,
    listar_fuentes,
    obtener_fuente,
    obtener_fuente_por_nombre,
    obtener_fuentes_agente,
)
from .llm_service import AgentDB, AgenteDB
from .role_service import (
    actualizar_rol,
    crear_rol,
    eliminar_rol,
    listar_roles,
    obtener_rol,
    obtener_rol_por_clave,
)
from .user_service import (
    actualizar_usuario,
    crear_usuario,
    eliminar_usuario,
    inicializar_admin_por_defecto,
    listar_usuarios,
    obtener_usuario,
    obtener_usuario_por_nombre,
    verificar_usuario,
)

# Alias en inglés para compatibilidad bilingüe
init_db = inicializar
clear_db = vaciar
create_user = crear_usuario
verify_user = verificar_usuario
init_default_admin = inicializar_admin_por_defecto
list_users = listar_usuarios
get_user = obtener_usuario
get_user_by_name = obtener_usuario_por_nombre
update_user = actualizar_usuario
delete_user = eliminar_usuario
list_agents = listar_agentes
agent_exists = existe_agente
create_agent = crear_agente
get_agent = obtener_agente
update_profile = actualizar_perfil
update_avatar = actualizar_avatar
change_identity = cambiar_identidad
update_knowledge = actualizar_conocimiento
clear_memory = borrar_memoria
delete_agent = eliminar_agente
list_sources = listar_fuentes
create_source = crear_fuente
get_source = obtener_fuente
get_source_by_name = obtener_fuente_por_nombre
update_source = actualizar_fuente
delete_source = eliminar_fuente
get_agent_sources = obtener_fuentes_agente
set_agent_sources = establecer_fuentes_agente
list_roles = listar_roles
get_role = obtener_rol
get_role_by_key = obtener_rol_por_clave
create_role = crear_rol
update_role = actualizar_rol
delete_role = eliminar_rol
create_chat_session = crear_sesion_chat
get_or_create_active_session = obtener_o_crear_sesion_activa
get_chat_session = obtener_sesion_chat
rename_chat_session = renombrar_sesion_chat
delete_chat_session = eliminar_sesion_chat
list_agent_sessions = listar_sesiones_agente
list_all_sessions = listar_todas_las_sesiones
get_session_all_messages = obtener_todos_mensajes_sesion
get_dashboard_stats = obtener_estadisticas_dashboard
migrate_legacy_knowledge = migrar_conocimientos_legacy

__all__ = [
    # Base
    "BASE_DATOS",
    "HISTORIAL_RECIENTE",
    "MODELO",
    "SIN_MEMORIA",
    "avatar_local",
    "inicializar",
    # Usuarios
    "crear_usuario",
    "verificar_usuario",
    "obtener_usuario",
    "obtener_usuario_por_nombre",
    "listar_usuarios",
    "actualizar_usuario",
    "eliminar_usuario",
    "inicializar_admin_por_defecto",
    # Agentes
    "crear_agente",
    "obtener_agente",
    "listar_agentes",
    "existe_agente",
    "actualizar_perfil",
    "actualizar_conocimiento",
    "actualizar_memoria",
    "borrar_memoria",
    "actualizar_avatar",
    "cambiar_identidad",
    "eliminar_agente",
    "agregar_memorias",
    # Fuentes
    "crear_fuente",
    "obtener_fuente",
    "obtener_fuente_por_nombre",
    "listar_fuentes",
    "actualizar_fuente",
    "eliminar_fuente",
    "establecer_fuentes_agente",
    "obtener_fuentes_agente",
    # Sesiones y Chat
    "crear_sesion_chat",
    "obtener_sesion_chat",
    "obtener_o_crear_sesion_activa",
    "listar_sesiones_agente",
    "renombrar_sesion_chat",
    "eliminar_sesion_chat",
    "guardar_mensaje",
    "obtener_historial",
    "obtener_todos_mensajes_sesion",
    "listar_todas_las_sesiones",
    # Roles
    "crear_rol",
    "obtener_rol",
    "obtener_rol_por_clave",
    "listar_roles",
    "actualizar_rol",
    "eliminar_rol",
    # Grupos
    "crear_grupo",
    "obtener_grupo",
    "obtener_grupo_por_nombre",
    "listar_grupos",
    "asignar_grupo",
    "obtener_grupo_agente",
    "listar_agentes_por_grupo",
    # Dashboard & Catálogo
    "listar_catalogo_agentes",
    "obtener_estadisticas_dashboard",
    "vaciar",
    "migrar_conocimientos_legacy",
    # LLM
    "AgentDB",
    "AgenteDB",
    # Aliases
    "init_db",
    "clear_db",
    "create_user",
    "verify_user",
    "init_default_admin",
    "list_users",
    "get_user",
    "get_user_by_name",
    "update_user",
    "delete_user",
    "list_agents",
    "agent_exists",
    "create_agent",
    "get_agent",
    "update_profile",
    "update_avatar",
    "change_identity",
    "update_knowledge",
    "clear_memory",
    "delete_agent",
    "list_sources",
    "create_source",
    "get_source",
    "get_source_by_name",
    "update_source",
    "delete_source",
    "get_agent_sources",
    "set_agent_sources",
    "list_roles",
    "get_role",
    "get_role_by_key",
    "create_role",
    "update_role",
    "delete_role",
    "create_chat_session",
    "get_or_create_active_session",
    "get_chat_session",
    "rename_chat_session",
    "delete_chat_session",
    "list_agent_sessions",
    "list_all_sessions",
    "get_session_all_messages",
    "get_dashboard_stats",
    "migrate_legacy_knowledge",
]
