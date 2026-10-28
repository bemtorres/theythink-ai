"""Servidor web Flask de los agentes personales inteligentes con DeepSeek AI.

Incluye:
- Chat interactivo multi-hilo con streaming y memoria continua.
- Gestión de agentes, identidades dinámicas y bases de conocimiento.
- Sistema de autenticación de usuarios con hashing de contraseñas.
- Dashboard administrativo con métricas y visor de transcripciones.
- Soporte para internacionalización i18n en 6 idiomas.
"""

import os
import uuid
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

from basededatos import (
    AgentDB,
    AgenteDB,
    actualizar_avatar,
    actualizar_conocimiento,
    actualizar_fuente,
    actualizar_perfil,
    actualizar_rol,
    actualizar_usuario,
    borrar_memoria,
    cambiar_identidad,
    crear_agente,
    crear_fuente,
    crear_rol,
    crear_sesion_chat,
    crear_usuario,
    eliminar_agente,
    eliminar_fuente,
    eliminar_rol,
    eliminar_sesion_chat,
    eliminar_usuario,
    establecer_fuentes_agente,
    inicializar,
    listar_agentes,
    listar_fuentes,
    listar_roles,
    listar_sesiones_agente,
    listar_todas_las_sesiones,
    listar_usuarios,
    migrar_conocimientos_legacy,
    obtener_agente,
    obtener_estadisticas_dashboard,
    obtener_fuente,
    obtener_fuentes_agente,
    obtener_historial,
    obtener_o_crear_sesion_activa,
    obtener_rol,
    obtener_rol_por_clave,
    obtener_sesion_chat,
    obtener_todos_mensajes_sesion,
    obtener_usuario,
    obtener_usuario_por_nombre,
    renombrar_sesion_chat,
    verificar_usuario,
)
from identidades import IDENTIDADES

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "minimind-secret-key-agentes-2026-auth")

AVATAR_UPLOAD_FOLDER = os.path.join(app.static_folder, "uploads", "avatars")
os.makedirs(AVATAR_UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "svg"}

# Límite de mensajes visibles en el historial del chat
VISIBLE_HISTORY_LIMIT = 60

# Perfil inicial por defecto para agentes creados sin descripción
INITIAL_PROFILE_TEMPLATE = "NOMBRE:\nAgente\n\nDESCRIPCIÓN:\nAgente inteligente de asistencia."

# Inicialización de tablas y carga de personas faltantes desde el seeder único
from seed import sembrar_personas

sembrar_personas()


def require_login(f):
    """Decorador de seguridad para proteger rutas que requieren autenticación."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("usuario"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "No autorizado. Inicia sesión primero."}), 401
            return redirect(url_for("pagina_login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function


# Alias en español para el decorador
login_requerido = require_login


def has_api_key() -> bool:
    """Comprueba si existe una API Key de DeepSeek configurada en las variables de entorno."""
    key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    return bool(key) and key != "tu_api_key"


def get_person_name(agent_name: str, profile_text: str) -> str:
    """Extrae el nombre de la persona o entidad desde el perfil del agente."""
    lines = profile_text.splitlines()
    for index, line in enumerate(lines):
        if line.strip().startswith("NOMBRE:"):
            for next_line in lines[index + 1:]:
                if next_line.strip():
                    return next_line.strip()
    return agent_name


def get_initials(name_text: str) -> str:
    """Calcula las iniciales para el avatar visual del agente o usuario."""
    parts = [part for part in name_text.split() if part]
    if not parts:
        return "A"
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def get_avatar_color(agent_name: str) -> str:
    """Asigna una paleta de color determinista según el nombre del agente."""
    palette = ["violet", "fuchsia", "indigo", "sky", "emerald", "rose"]
    return palette[sum(ord(char) for char in agent_name) % len(palette)]


def get_identity_info(role_key: str, custom_prompt: str) -> dict:
    """Obtiene la información de rol e identidad consultando la base de datos."""
    if custom_prompt.strip():
        return {
            "nombre": "Identidad personalizada",
            "descripcion": "Prompt propio guardado como identidad personalizada.",
            "prompt": custom_prompt,
            "personalizada": True,
            "clave": "",
        }
    if role_key:
        role = obtener_rol_por_clave(role_key)
        if role:
            return {
                "nombre": role["nombre"],
                "descripcion": role["descripcion"],
                "prompt": role["prompt"],
                "personalizada": False,
                "clave": role["clave"],
            }
    default_role = obtener_rol_por_clave("basic")
    if default_role:
        return {
            "nombre": default_role["nombre"],
            "descripcion": default_role["descripcion"],
            "prompt": default_role["prompt"],
            "personalizada": False,
            "clave": "basic",
        }
    return {
        "nombre": "Básico",
        "descripcion": "Agente experto en la base de conocimiento.",
        "prompt": "Eres un modelo de inteligencia artificial experto...",
        "personalizada": False,
        "clave": "basic",
    }


def load_agent_data(agent_name: str) -> dict | None:
    """Carga y estructura los datos completos de un agente para renderizado o API."""
    data = obtener_agente(agent_name)
    if not data:
        return None
    person_name = get_person_name(agent_name, data["perfil"])
    return {
        "nombre": agent_name,
        "persona": person_name,
        "iniciales": get_initials(person_name),
        "color": get_avatar_color(agent_name),
        "avatar_url": data.get("avatar_url", "") or "",
        "perfil": data["perfil"],
        "conocimiento": data["conocimiento"],
        "memoria": data["memoria"],
        "creado_en": data["creado_en"],
        "identidad": get_identity_info(
            data["identidad_clave"], data["identidad_custom"]
        ),
        "fuentes": obtener_fuentes_agente(agent_name),
        "todas_fuentes": listar_fuentes(),
        "sesiones": listar_sesiones_agente(agent_name),
        "roles": listar_roles(),
    }


def get_agent_or_404(agent_name: str) -> str:
    """Verifica la existencia del agente o lanza error 404."""
    if agent_name not in listar_agentes():
        abort(404)
    return agent_name


# ----------------------------------------------------------------------
# Vistas Públicas y de Chat
# ----------------------------------------------------------------------


@app.get("/", endpoint="inicio")
def home_view():
    """Página principal de bienvenida y catálogo interactivo."""
    agents = [load_agent_data(name) for name in listar_agentes()]
    sources = listar_fuentes()
    roles = listar_roles()
    return render_template(
        "index.html",
        agentes=agents,
        fuentes=sources,
        roles=roles,
        identidades=IDENTIDADES,
        tiene_api_key=has_api_key(),
        usuario_actual=session.get("usuario"),
    )


@app.get("/agente/<nombre>", endpoint="pagina_chat")
@require_login
def chat_view(nombre):
    """Página del chat interactivo con el agente seleccionado."""
    get_agent_or_404(nombre)
    agent_data = load_agent_data(nombre)
    active_session = obtener_o_crear_sesion_activa(nombre)
    roles = listar_roles()
    all_agents = listar_agentes()
    all_agents_info = [load_agent_data(name) for name in all_agents]
    return render_template(
        "chat.html",
        agente=agent_data,
        sesion_activa=active_session,
        sesiones=listar_sesiones_agente(nombre),
        roles=roles,
        todos_los_agentes=all_agents,
        todos_los_agentes_info=all_agents_info,
        identidades=IDENTIDADES,
        tiene_api_key=has_api_key(),
        usuario_actual=session.get("usuario"),
    )


@app.get("/agente/<nombre>/whatsaap", endpoint="pagina_chat_whatsaap")
@app.get("/agente/<nombre>/whatsapp", endpoint="pagina_chat_whatsapp")
@require_login
def whatsapp_view(nombre):
    """Vista con interfaz móvil simulada estilo WhatsApp."""
    get_agent_or_404(nombre)
    agent_data = load_agent_data(nombre)
    active_session = obtener_o_crear_sesion_activa(nombre)
    messages = obtener_todos_mensajes_sesion(active_session["id"])
    return render_template(
        "whatsapp.html",
        agente=agent_data,
        sesion_activa=active_session,
        mensajes=messages,
        tiene_api_key=has_api_key(),
        usuario_actual=session.get("usuario"),
        volver_url="/admin/whatsaap",
    )


@app.get("/admin/whatsaap", endpoint="admin_whatsapp_lista_alt")
@app.get("/admin/whatsapp", endpoint="admin_whatsapp_lista")
@require_login
def admin_whatsapp_list_view():
    """Lista de contactos y chats estilo WhatsApp."""
    agents = [load_agent_data(name) for name in listar_agentes()]
    for ag in agents:
        sessions = ag.get("sesiones") or []
        if sessions:
            ag["ultimo_mensaje"] = sessions[0].get("titulo") or "Conversación iniciada"
            ag["ultima_hora"] = sessions[0].get("actualizado_en", "")[11:16] or "10:42"
        else:
            first_line = (ag.get("perfil") or "").splitlines()
            ag["ultimo_mensaje"] = first_line[0] if first_line else "Disponible"
            ag["ultima_hora"] = "10:00"
    return render_template(
        "whatsapp_list.html",
        agentes=agents,
        usuario_actual=session.get("usuario"),
        tiene_api_key=has_api_key(),
    )


@app.get("/admin/whatsaap/<nombre>", endpoint="admin_whatsapp_chat_alt")
@app.get("/admin/whatsapp/<nombre>", endpoint="admin_whatsapp_chat")
@require_login
def admin_whatsapp_chat_view(nombre):
    """Chat con un agente específico dentro de /admin/whatsapp."""
    get_agent_or_404(nombre)
    agent_data = load_agent_data(nombre)
    active_session = obtener_o_crear_sesion_activa(nombre)
    messages = obtener_todos_mensajes_sesion(active_session["id"])
    return render_template(
        "whatsapp.html",
        agente=agent_data,
        sesion_activa=active_session,
        mensajes=messages,
        tiene_api_key=has_api_key(),
        usuario_actual=session.get("usuario"),
        volver_url="/admin/whatsaap",
    )


@app.get("/agente/<nombre>/telegram", endpoint="pagina_chat_telegram")
@require_login
def telegram_view(nombre):
    """Vista con interfaz móvil simulada estilo Telegram."""
    get_agent_or_404(nombre)
    agent_data = load_agent_data(nombre)
    active_session = obtener_o_crear_sesion_activa(nombre)
    messages = obtener_todos_mensajes_sesion(active_session["id"])
    return render_template(
        "telegram.html",
        agente=agent_data,
        sesion_activa=active_session,
        mensajes=messages,
        tiene_api_key=has_api_key(),
        usuario_actual=session.get("usuario"),
        volver_url="/admin/telegram",
    )


@app.get("/admin/telegram", endpoint="admin_telegram_lista")
@require_login
def admin_telegram_list_view():
    """Lista de contactos y bots estilo Telegram."""
    agents = [load_agent_data(name) for name in listar_agentes()]
    for ag in agents:
        sessions = ag.get("sesiones") or []
        if sessions:
            ag["ultimo_mensaje"] = sessions[0].get("titulo") or "Conversación iniciada"
            ag["ultima_hora"] = sessions[0].get("actualizado_en", "")[11:16] or "10:42"
        else:
            first_line = (ag.get("perfil") or "").splitlines()
            ag["ultimo_mensaje"] = first_line[0] if first_line else "Bot activo"
            ag["ultima_hora"] = "10:00"
    return render_template(
        "telegram_list.html",
        agentes=agents,
        usuario_actual=session.get("usuario"),
        tiene_api_key=has_api_key(),
    )


@app.get("/admin/telegram/<nombre>", endpoint="admin_telegram_chat")
@require_login
def admin_telegram_chat_view(nombre):
    """Chat con un bot específico dentro de /admin/telegram."""
    get_agent_or_404(nombre)
    agent_data = load_agent_data(nombre)
    active_session = obtener_o_crear_sesion_activa(nombre)
    messages = obtener_todos_mensajes_sesion(active_session["id"])
    return render_template(
        "telegram.html",
        agente=agent_data,
        sesion_activa=active_session,
        mensajes=messages,
        tiene_api_key=has_api_key(),
        usuario_actual=session.get("usuario"),
        volver_url="/admin/telegram",
    )



# ----------------------------------------------------------------------
# Autenticación (Login / Logout)
# ----------------------------------------------------------------------


@app.get("/login", endpoint="pagina_login")
def login_view():
    """Página de inicio de sesión."""
    if session.get("usuario"):
        next_url = request.args.get("next") or url_for("dashboard_view")
        return redirect(next_url)
    return render_template("login.html", next=request.args.get("next", ""))


@app.post("/login")
def login_action():
    """Procesa las credenciales enviadas por el formulario o API de Login."""
    payload = request.get_json(silent=True) or request.form
    username = (payload.get("usuario") or "").strip()
    password = (payload.get("password") or "").strip()
    next_url = request.args.get("next") or (payload.get("next") if isinstance(payload, dict) else "") or url_for("dashboard_view")

    user_result = verificar_usuario(username, password)
    if not user_result:
        if request.is_json:
            return jsonify({"error": "Usuario o contraseña incorrectos."}), 401
        return render_template("login.html", error="Usuario o contraseña incorrectos.", usuario=username, next=next_url), 401

    session["usuario"] = user_result["usuario"]
    session["rol"] = user_result["rol"]

    if request.is_json:
        return jsonify({"ok": True, "redirect": next_url})
    return redirect(next_url)


@app.get("/logout", endpoint="cerrar_sesion")
def logout_action():
    """Cierra la sesión del usuario actual."""
    session.clear()
    return redirect(url_for("inicio"))


# ----------------------------------------------------------------------
# Dashboard Administrativo
# ----------------------------------------------------------------------


def _render_dashboard(default_tab="agentes"):
    """Renderiza el panel administrativo mostrando la sección indicada por defecto.

    Las secciones (agentes, fuentes, roles, usuarios, historial, config) se
    exponen como módulos independientes vía las rutas /admin/*.
    """
    stats = obtener_estadisticas_dashboard()
    # Enriquecer cada agente con persona (NOMBRE del perfil) e iniciales para el dashboard
    for ag in stats.get("agentes", []):
        try:
            ag["persona"] = get_person_name(ag.get("nombre", ""), ag.get("perfil", "") or "")
            ag["iniciales"] = get_initials(ag["persona"] or ag.get("nombre", ""))
        except Exception:
            ag["persona"] = ag.get("nombre", "")
            ag["iniciales"] = get_initials(ag.get("nombre", ""))
    return render_template(
        "dashboard.html",
        stats=stats,
        fuentes=listar_fuentes(),
        roles=listar_roles(),
        usuarios=listar_usuarios(),
        identidades=IDENTIDADES,
        usuario_actual=session.get("usuario"),
        tiene_api_key=has_api_key(),
        default_tab=default_tab,
    )


@app.get("/dashboard", endpoint="pagina_dashboard")
@app.get("/admin")
@require_login
def dashboard_view():
    """Vista principal del Dashboard: muestra primero los agentes creados."""
    return _render_dashboard("agentes")


@app.get("/admin/knowledge", endpoint="admin_knowledge")
@require_login
def admin_knowledge_view():
    """Módulo: Bases de Conocimiento del sistema."""
    return _render_dashboard("fuentes")


@app.get("/admin/identities", endpoint="admin_identities")
@require_login
def admin_identities_view():
    """Módulo: Roles e Identidades del sistema."""
    return _render_dashboard("roles")


@app.get("/admin/users", endpoint="admin_users")
@require_login
def admin_users_view():
    """Módulo: Gestión de usuarios del sistema."""
    return _render_dashboard("usuarios")


@app.get("/admin/config", endpoint="admin_config")
@require_login
def admin_config_view():
    """Módulo: Configuración general del sistema."""
    return _render_dashboard("config")


@app.get("/api/dashboard/stats")
@require_login
def api_dashboard_stats():
    """Endpoint API para obtener métricas generales del sistema."""
    return jsonify(obtener_estadisticas_dashboard())


# ----------------------------------------------------------------------
# API JSON: Agentes
# ----------------------------------------------------------------------


@app.get("/api/agente/<nombre>")
def api_get_agent(nombre):
    """Obtiene los datos detallados de un agente en JSON."""
    get_agent_or_404(nombre)
    return jsonify(load_agent_data(nombre))


@app.post("/api/upload/avatar")
@require_login
def api_upload_avatar():
    """Sube una imagen de avatar para un agente."""
    if "avatar" not in request.files and "file" not in request.files:
        return jsonify({"error": "No se envió ningún archivo de imagen."}), 400
    file = request.files.get("avatar") or request.files.get("file")
    if not file or not file.filename:
        return jsonify({"error": "Nombre de archivo inválido."}), 400

    parts = file.filename.rsplit(".", 1)
    if len(parts) < 2 or parts[1].lower() not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Formato no permitido. Usa PNG, JPG, JPEG, WEBP, GIF o SVG."}), 400

    extension = parts[1].lower()
    filename = f"{uuid.uuid4().hex[:12]}_{secure_filename(parts[0])}.{extension}"
    target_path = os.path.join(AVATAR_UPLOAD_FOLDER, filename)
    file.save(target_path)
    relative_url = f"/static/uploads/avatars/{filename}"
    return jsonify({"ok": True, "url": relative_url})


@app.post("/api/agentes")
def api_create_agent():
    """Crea un nuevo agente en la base de datos."""
    payload = request.get_json(silent=True) or {}
    name = (payload.get("nombre") or "").strip()
    if not name:
        return jsonify({"error": "Escribe un nombre para el agente."}), 400
    if "/" in name or "\\" in name or name.startswith("."):
        return jsonify({"error": "El nombre no puede contener '/' ni '\\'."}), 400
    if name in listar_agentes():
        return jsonify({"error": f"El agente '{name}' ya existe."}), 400

    profile = (payload.get("perfil") or "").strip()
    knowledge = (payload.get("conocimiento") or "").strip()
    role_key = (payload.get("identidad") or "").strip()
    custom_identity = (payload.get("identidad_custom") or "").strip()
    avatar_url = (payload.get("avatar_url") or "").strip()
    sources = payload.get("fuentes") or payload.get("fuentes_ids") or []

    source_ids = []
    if isinstance(sources, list):
        for val in sources:
            try:
                source_ids.append(int(val))
            except (TypeError, ValueError):
                continue

    valid_role = bool(obtener_rol_por_clave(role_key)) or role_key in IDENTIDADES
    crear_agente(
        nombre=name,
        perfil=profile if profile else INITIAL_PROFILE_TEMPLATE,
        conocimiento=knowledge,
        identidad_clave=role_key if valid_role else "",
        identidad_custom=custom_identity,
        avatar_url=avatar_url,
        fuentes_ids=source_ids,
    )
    migrar_conocimientos_legacy()
    return jsonify({"ok": True, "nombre": name}), 201


@app.delete("/api/agente/<nombre>")
@require_login
def api_delete_agent(nombre):
    """Elimina un agente y todos sus registros asociados."""
    get_agent_or_404(nombre)
    success = eliminar_agente(nombre)
    if not success:
        return jsonify({"error": "No se pudo eliminar el agente."}), 500
    return jsonify({"ok": True, "mensaje": f"Agente '{nombre}' eliminado correctamente."})


@app.post("/api/agente/<nombre>/perfil")
def api_update_agent_profile(nombre):
    """Actualiza el perfil descriptivo del agente."""
    get_agent_or_404(nombre)
    payload = request.get_json(silent=True) or {}
    text = (payload.get("perfil") or "").strip()
    if not text:
        return jsonify({"error": "El perfil no puede estar vacío."}), 400
    actualizar_perfil(nombre, text)
    return jsonify(load_agent_data(nombre))


@app.post("/api/agente/<nombre>/conocimiento")
def api_update_agent_knowledge(nombre):
    """Actualiza el conocimiento directo del agente."""
    get_agent_or_404(nombre)
    payload = request.get_json(silent=True) or {}
    text = (payload.get("conocimiento") or "").strip()
    actualizar_conocimiento(nombre, text)
    return jsonify(load_agent_data(nombre))


@app.post("/api/agente/<nombre>/identidad")
def api_change_agent_identity(nombre):
    """Cambia el rol o prompt de identidad del agente."""
    get_agent_or_404(nombre)
    payload = request.get_json(silent=True) or {}
    custom_prompt = (payload.get("identidad_custom") or "").strip()
    role_key = (payload.get("identidad") or "").strip()
    valid_role = bool(obtener_rol_por_clave(role_key)) or role_key in IDENTIDADES
    if custom_prompt:
        cambiar_identidad(nombre, custom=custom_prompt)
    elif valid_role:
        cambiar_identidad(nombre, clave=role_key)
    else:
        return jsonify({"error": "Identidad o rol no válido."}), 400
    return jsonify(load_agent_data(nombre))


@app.post("/api/agente/<nombre>/editar")
def api_edit_agent(nombre):
    """Actualiza de forma integral el perfil, avatar, fuentes y rol del agente."""
    get_agent_or_404(nombre)
    payload = request.get_json(silent=True) or {}
    profile = (payload.get("perfil") or "").strip()
    knowledge = (payload.get("conocimiento") or "").strip()
    custom_prompt = (payload.get("identidad_custom") or "").strip()
    role_key = (payload.get("identidad") or "").strip()
    avatar_url = payload.get("avatar_url")
    sources = payload.get("fuentes") or payload.get("fuentes_ids")
    valid_role = bool(obtener_rol_por_clave(role_key)) or role_key in IDENTIDADES

    if not profile:
        return jsonify({"error": "El perfil no puede estar vacío."}), 400
    if not custom_prompt and not valid_role and role_key:
        return jsonify({"error": "Identidad o rol no válido."}), 400

    actualizar_perfil(nombre, profile)
    actualizar_conocimiento(nombre, knowledge)
    if avatar_url is not None:
        actualizar_avatar(nombre, str(avatar_url).strip())

    if isinstance(sources, list):
        source_ids = []
        for val in sources:
            try:
                source_ids.append(int(val))
            except (TypeError, ValueError):
                continue
        establecer_fuentes_agente(nombre, source_ids)
    if custom_prompt:
        cambiar_identidad(nombre, custom=custom_prompt)
    else:
        cambiar_identidad(nombre, clave=role_key)
    return jsonify(load_agent_data(nombre))


@app.post("/api/agente/<nombre>/limpiar")
def api_clear_agent_memory(nombre):
    """Borra todos los recuerdos almacenados en la memoria activa del agente."""
    get_agent_or_404(nombre)
    borrar_memoria(nombre)
    return jsonify({"ok": True})


# ----------------------------------------------------------------------
# API JSON: Roles e Identidades
# ----------------------------------------------------------------------


@app.get("/api/roles")
@require_login
def api_list_roles():
    """Lista todos los roles e identidades registrados."""
    return jsonify({"roles": listar_roles()})


@app.get("/api/roles/<int:rol_id>")
@require_login
def api_get_role(rol_id):
    """Obtiene el detalle de un rol por su ID."""
    role = obtener_rol(rol_id)
    if not role:
        return jsonify({"error": "Rol no encontrado."}), 404
    return jsonify(role)


@app.post("/api/roles")
@require_login
def api_create_role():
    """Crea un nuevo rol o identidad en SQLite."""
    payload = request.get_json(silent=True) or {}
    key = (payload.get("clave") or "").strip().lower()
    name = (payload.get("nombre") or "").strip()
    desc = (payload.get("descripcion") or "").strip()
    prompt = (payload.get("prompt") or "").strip()

    if not key or not name or not prompt:
        return jsonify({"error": "La clave, el nombre y el prompt son obligatorios."}), 400

    try:
        new_id = crear_rol(key, name, desc, prompt)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    return jsonify({"id": new_id, "clave": key, "nombre": name, "descripcion": desc, "prompt": prompt}), 201


@app.route("/api/roles/<int:rol_id>", methods=["POST", "PUT"])
@require_login
def api_update_role(rol_id):
    """Actualiza la información y prompt de un rol existente."""
    payload = request.get_json(silent=True) or {}
    key = (payload.get("clave") or "").strip().lower()
    name = (payload.get("nombre") or "").strip()
    desc = (payload.get("descripcion") or "").strip()
    prompt = (payload.get("prompt") or "").strip()

    if not key or not name or not prompt:
        return jsonify({"error": "La clave, el nombre y el prompt son obligatorios."}), 400

    try:
        actualizar_rol(rol_id, key, name, desc, prompt)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    return jsonify({"id": rol_id, "clave": key, "nombre": name, "descripcion": desc, "prompt": prompt})


@app.delete("/api/roles/<int:rol_id>")
@require_login
def api_delete_role(rol_id):
    """Elimina un rol personalizado."""
    success = eliminar_rol(rol_id)
    if not success:
        return jsonify({"error": "No se pudo eliminar el rol."}), 404
    return jsonify({"ok": True})


# ----------------------------------------------------------------------
# API JSON: Usuarios y Perfil Administrativo
# ----------------------------------------------------------------------


@app.get("/api/usuarios")
@require_login
def api_list_users():
    """Lista todos los usuarios del sistema."""
    return jsonify({"usuarios": listar_usuarios()})


@app.get("/api/usuario/<int:usuario_id>")
@require_login
def api_get_user(usuario_id):
    """Obtiene la ficha de un usuario específico."""
    user = obtener_usuario(usuario_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado."}), 404
    return jsonify(user)


@app.post("/api/usuarios")
@require_login
def api_create_user():
    """Crea una nueva cuenta de usuario."""
    payload = request.get_json(silent=True) or {}
    username = (payload.get("usuario") or "").strip()
    password = (payload.get("password") or "").strip()
    role = (payload.get("rol") or "usuario").strip()

    if not username or not password:
        return jsonify({"error": "El nombre de usuario y la contraseña son obligatorios."}), 400

    try:
        crear_usuario(username, password, role)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    created_user = obtener_usuario_por_nombre(username)
    return jsonify(created_user), 201


@app.route("/api/usuario/<int:usuario_id>", methods=["POST", "PUT"])
@require_login
def api_update_user(usuario_id):
    """Actualiza datos y/o contraseña de un usuario."""
    payload = request.get_json(silent=True) or {}
    username = (payload.get("usuario") or "").strip()
    role = (payload.get("rol") or "usuario").strip()
    password = (payload.get("password") or "").strip()

    if not username:
        return jsonify({"error": "El nombre de usuario no puede estar vacío."}), 400

    try:
        actualizar_usuario(usuario_id, username, role, nuevo_password=password if password else None)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    # Si se actualizó el propio usuario activo, sincronizar sesión
    active_user = session.get("usuario")
    user_db = obtener_usuario(usuario_id)
    if active_user and user_db:
        session_info = obtener_usuario_por_nombre(active_user)
        if session_info and session_info["id"] == usuario_id:
            session["usuario"] = user_db["usuario"]
            session["rol"] = user_db["rol"]

    return jsonify(user_db)


@app.delete("/api/usuario/<int:usuario_id>")
@require_login
def api_delete_user(usuario_id):
    """Elimina una cuenta de usuario."""
    active_user = session.get("usuario")
    try:
        success = eliminar_usuario(usuario_id, usuario_actual_nombre=active_user)
        if not success:
            return jsonify({"error": "Usuario no encontrado."}), 404
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    return jsonify({"ok": True})


@app.get("/api/perfil")
@require_login
def api_get_my_profile():
    """Obtiene el perfil del usuario autenticado."""
    username = session.get("usuario")
    if not username:
        return jsonify({"error": "No autenticado."}), 401
    user = obtener_usuario_por_nombre(username)
    if not user:
        return jsonify({"error": "Usuario no encontrado."}), 404
    return jsonify(user)


@app.post("/api/perfil")
@require_login
def api_update_my_profile():
    """Actualiza el nombre y/o contraseña propia del usuario autenticado."""
    username = session.get("usuario")
    user_info = obtener_usuario_por_nombre(username)
    if not user_info:
        return jsonify({"error": "Usuario no encontrado."}), 404

    payload = request.get_json(silent=True) or {}
    new_username = (payload.get("usuario") or username).strip()
    new_password = (payload.get("password") or "").strip()

    try:
        actualizar_usuario(
            user_info["id"],
            new_username,
            nuevo_rol=user_info["rol"],
            nuevo_password=new_password if new_password else None,
        )
        session["usuario"] = new_username
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    return jsonify(obtener_usuario(user_info["id"]))


# ----------------------------------------------------------------------
# API JSON: Sesiones de Chat (Multi-Conversación)
# ----------------------------------------------------------------------


@app.get("/api/sesiones")
@require_login
def api_list_all_sessions():
    """Lista todas las sesiones de conversación, opcionalmente filtradas por agente."""
    agent_filter = request.args.get("agente")
    return jsonify({"sesiones": listar_todas_las_sesiones(agent_filter if agent_filter else None)})


@app.get("/api/agente/<nombre>/sesiones")
@require_login
def api_list_agent_sessions(nombre):
    """Lista todas las sesiones de chat de un agente específico."""
    get_agent_or_404(nombre)
    return jsonify({"sesiones": listar_sesiones_agente(nombre)})


@app.post("/api/agente/<nombre>/sesiones")
@require_login
def api_create_agent_session(nombre):
    """Crea un nuevo hilo de conversación para un agente."""
    get_agent_or_404(nombre)
    payload = request.get_json(silent=True) or {}
    title = (payload.get("titulo") or "").strip()
    new_session = crear_sesion_chat(nombre, titulo=title if title else None)
    return jsonify(new_session), 201


@app.get("/api/sesion/<int:sesion_id>")
@require_login
def api_get_session(sesion_id):
    """Obtiene una sesión de chat y sus mensajes."""
    chat_session = obtener_sesion_chat(sesion_id)
    if not chat_session:
        return jsonify({"error": "Conversación no encontrada."}), 404
    messages = obtener_todos_mensajes_sesion(sesion_id)
    chat_session["mensajes"] = messages
    return jsonify(chat_session)


@app.put("/api/sesion/<int:sesion_id>")
@require_login
def api_rename_session(sesion_id):
    """Renombra el título de una conversación."""
    chat_session = obtener_sesion_chat(sesion_id)
    if not chat_session:
        return jsonify({"error": "Conversación no encontrada."}), 404
    payload = request.get_json(silent=True) or {}
    title = (payload.get("titulo") or "").strip()
    if not title:
        return jsonify({"error": "El título no puede estar vacío."}), 400
    renombrar_sesion_chat(sesion_id, title)
    return jsonify({"ok": True, "id": sesion_id, "titulo": title})


@app.delete("/api/sesion/<int:sesion_id>")
@require_login
def api_delete_session(sesion_id):
    """Elimina una sesión de chat y sus mensajes asociados."""
    chat_session = obtener_sesion_chat(sesion_id)
    if not chat_session:
        return jsonify({"error": "Conversación no encontrada."}), 404
    eliminar_sesion_chat(sesion_id)
    return jsonify({"ok": True})


@app.post("/api/sesion/<int:sesion_id>/mensaje")
@require_login
def api_send_session_message(sesion_id):
    """Envía un mensaje a la sesión de chat y obtiene respuesta de DeepSeek."""
    chat_session = obtener_sesion_chat(sesion_id)
    if not chat_session:
        return jsonify({"error": "Conversación no encontrada."}), 404

    agent_name = chat_session["agente_nombre"]
    payload = request.get_json(silent=True) or {}
    user_message = (payload.get("mensaje") or "").strip()
    if not user_message:
        return jsonify({"error": "El mensaje no puede estar vacío."}), 400

    custom_max_tokens = payload.get("max_tokens")
    try:
        max_tokens_val = int(custom_max_tokens) if custom_max_tokens else 400
    except (ValueError, TypeError):
        max_tokens_val = 400

    try:
        agent = AgentDB(agent_name)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    try:
        assistant_response = agent.preguntar(user_message, sesion_id=sesion_id, max_tokens=max_tokens_val)
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 500

    try:
        new_memories = agent.actualizar_memoria(user_message, assistant_response)
    except Exception:
        new_memories = []

    # Recargar datos actualizados de la sesión
    updated_session = obtener_sesion_chat(sesion_id)

    return jsonify(
        {
            "respuesta": assistant_response,
            "memoria_guardada": bool(new_memories),
            "sesion": updated_session,
        }
    )


# Compatibilidad retroactiva para endpoint de mensaje sin sesion_id explícito
@app.post("/api/agente/<nombre>/mensaje")
@require_login
def api_send_agent_message_fallback(nombre):
    """Envía un mensaje al agente usando su sesión activa por defecto."""
    get_agent_or_404(nombre)
    active_session = obtener_o_crear_sesion_activa(nombre)
    return api_send_session_message(active_session["id"])


# ----------------------------------------------------------------------
# API JSON: Bases de Conocimiento
# ----------------------------------------------------------------------


@app.get("/api/fuentes")
def api_list_sources():
    """Lista todas las bases de conocimiento."""
    return jsonify({"fuentes": listar_fuentes()})


@app.get("/api/fuentes/<int:fuente_id>")
def api_get_source(fuente_id):
    """Obtiene el contenido de una base de conocimiento."""
    source = obtener_fuente(fuente_id)
    if not source:
        return jsonify({"error": "Base de conocimiento no encontrada."}), 404
    return jsonify(source)


@app.post("/api/fuentes")
def api_create_source():
    """Crea una nueva base de conocimiento."""
    payload = request.get_json(silent=True) or {}
    name = (payload.get("nombre") or "").strip()
    content = (payload.get("contenido") or "").strip()
    if not name:
        return jsonify({"error": "Escribe un nombre para la base de conocimiento."}), 400
    try:
        new_id = crear_fuente(name, content)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    return jsonify({"id": new_id, "nombre": name, "contenido": content}), 201


@app.route("/api/fuentes/<int:fuente_id>", methods=["POST", "PUT"])
def api_update_source(fuente_id):
    """Actualiza el nombre y contenido de una base de conocimiento."""
    payload = request.get_json(silent=True) or {}
    name = (payload.get("nombre") or "").strip()
    content = (payload.get("contenido") or "").strip()
    if not name:
        return jsonify({"error": "El nombre de la base de conocimiento no puede estar vacío."}), 400
    try:
        actualizar_fuente(fuente_id, name, content)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    return jsonify({"id": fuente_id, "nombre": name, "contenido": content})


@app.delete("/api/fuentes/<int:fuente_id>")
def api_delete_source(fuente_id):
    """Elimina una base de conocimiento."""
    eliminar_fuente(fuente_id)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True)