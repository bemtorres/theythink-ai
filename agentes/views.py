"""Vistas y endpoints de la plataforma de agentes con Django."""

import json
import os
import uuid
from functools import wraps

from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.text import get_valid_filename
from django.views.decorators.csrf import csrf_exempt

from .services import (
    AgentDB,
    actualizar_avatar,
    actualizar_conocimiento,
    actualizar_fuente,
    actualizar_perfil,
    actualizar_rol,
    actualizar_usuario,
    asignar_grupo,
    borrar_memoria,
    cambiar_identidad,
    crear_agente,
    crear_fuente,
    crear_grupo,
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
    listar_catalogo_agentes,
    listar_fuentes,
    listar_grupos,
    listar_roles,
    listar_sesiones_agente,
    listar_todas_las_sesiones,
    listar_usuarios,
    migrar_conocimientos_legacy,
    obtener_agente,
    obtener_estadisticas_dashboard,
    obtener_fuente,
    obtener_fuentes_agente,
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
from .lib.catalog import presentar_agentes
from .seeders import IDENTIDADES

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "svg"}
INITIAL_PROFILE_TEMPLATE = "NOMBRE:\nAgente\n\nDESCRIPCIÓN:\nAgente inteligente de asistencia."

# Inicialización segura
inicializar()


# ----------------------------------------------------------------------
# Helpers de Autenticación y Utilidades
# ----------------------------------------------------------------------


def require_login(view_func):
    """Decorador para proteger vistas que requieren autenticación de usuario."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("usuario"):
            if request.path.startswith("/api/"):
                return JsonResponse({"error": "No autorizado. Inicia sesión primero."}, status=401)
            next_param = request.get_full_path()
            return redirect(f"/login?next={next_param}")
        return view_func(request, *args, **kwargs)
    return wrapper


login_requerido = require_login


def has_api_key() -> bool:
    """Comprueba si existe una API Key de DeepSeek configurada."""
    key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    return bool(key) and key != "tu_api_key"


def get_person_name(agent_name: str, profile_text: str) -> str:
    """Extrae el nombre de la persona desde el perfil descriptivo."""
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
    """Carga y estructura los datos completos de un agente."""
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
        raise Http404(f"Agente '{agent_name}' no encontrado.")
    return agent_name


def parse_body(request) -> dict:
    """Extrae el payload JSON o form data de la petición."""
    if request.body:
        try:
            return json.loads(request.body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            pass
    return {k: v for k, v in request.POST.items()}


# ----------------------------------------------------------------------
# Vistas Públicas y de Chat
# ----------------------------------------------------------------------


def home_view(request):
    """Página principal de bienvenida y catálogo interactivo de agentes."""
    grupos = listar_grupos()
    agents = presentar_agentes(listar_catalogo_agentes(), grupos)
    grupo_param = request.GET.get("grupo")
    grupo_id = None
    if grupo_param is not None:
        try:
            grupo_id = int(grupo_param)
            grupo = next((g for g in grupos if g["id"] == grupo_id), None)
            if grupo is None:
                raise Http404("Grupo no encontrado")
        except ValueError:
            raise Http404("Parámetro de grupo inválido")

    return render(
        request,
        "index.html",
        {
            "agentes": agents,
            "grupos": grupos,
            "grupo_inicial": grupo_id,
            "identidades": IDENTIDADES,
            "tiene_api_key": has_api_key(),
            "usuario_actual": request.session.get("usuario"),
        },
    )


@require_login
def chat_view(request, nombre):
    """Página del chat interactivo con el agente seleccionado."""
    get_agent_or_404(nombre)
    agent_data = load_agent_data(nombre)
    grupos = listar_grupos()
    catalogo = presentar_agentes(listar_catalogo_agentes(), grupos)
    presentacion = next((a for a in catalogo if a["id"] == nombre), None)
    if not presentacion:
        raise Http404("Agente no encontrado en el catálogo.")
    active_session = obtener_o_crear_sesion_activa(nombre)
    roles = listar_roles()
    all_agents = listar_agentes()
    all_agents_info = [
        {
            "nombre": a["id"],
            "persona": a["name"],
            "avatar_url": a["avatar"],
            "iniciales": get_initials(a["name"]),
            "identidad": {"nombre": a["role"]},
        }
        for a in catalogo
    ]
    return render(
        request,
        "chat.html",
        {
            "agente": agent_data,
            "presentacion": presentacion,
            "sesion_activa": active_session,
            "sesiones": listar_sesiones_agente(nombre),
            "roles": roles,
            "todos_los_agentes": all_agents,
            "todos_los_agentes_info": all_agents_info,
            "identidades": IDENTIDADES,
            "tiene_api_key": has_api_key(),
            "usuario_actual": request.session.get("usuario"),
        },
    )


@require_login
def whatsapp_view(request, nombre):
    """Vista con interfaz móvil simulada estilo WhatsApp."""
    get_agent_or_404(nombre)
    agent_data = load_agent_data(nombre)
    active_session = obtener_o_crear_sesion_activa(nombre)
    messages = obtener_todos_mensajes_sesion(active_session["id"])
    return render(
        request,
        "whatsapp.html",
        {
            "agente": agent_data,
            "sesion_activa": active_session,
            "mensajes": messages,
            "tiene_api_key": has_api_key(),
            "usuario_actual": request.session.get("usuario"),
            "volver_url": "/admin/whatsaap",
        },
    )


@require_login
def admin_whatsapp_list_view(request):
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
    return render(
        request,
        "whatsapp_list.html",
        {
            "agentes": agents,
            "usuario_actual": request.session.get("usuario"),
            "tiene_api_key": has_api_key(),
        },
    )


@require_login
def admin_whatsapp_chat_view(request, nombre):
    """Chat con un agente específico dentro de /admin/whatsapp."""
    get_agent_or_404(nombre)
    agent_data = load_agent_data(nombre)
    active_session = obtener_o_crear_sesion_activa(nombre)
    messages = obtener_todos_mensajes_sesion(active_session["id"])
    return render(
        request,
        "whatsapp.html",
        {
            "agente": agent_data,
            "sesion_activa": active_session,
            "mensajes": messages,
            "tiene_api_key": has_api_key(),
            "usuario_actual": request.session.get("usuario"),
            "volver_url": "/admin/whatsaap",
        },
    )


@require_login
def telegram_view(request, nombre):
    """Vista con interfaz móvil simulada estilo Telegram."""
    get_agent_or_404(nombre)
    agent_data = load_agent_data(nombre)
    active_session = obtener_o_crear_sesion_activa(nombre)
    messages = obtener_todos_mensajes_sesion(active_session["id"])
    return render(
        request,
        "telegram.html",
        {
            "agente": agent_data,
            "sesion_activa": active_session,
            "mensajes": messages,
            "tiene_api_key": has_api_key(),
            "usuario_actual": request.session.get("usuario"),
            "volver_url": "/admin/telegram",
        },
    )


@require_login
def admin_telegram_list_view(request):
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
    return render(
        request,
        "telegram_list.html",
        {
            "agentes": agents,
            "usuario_actual": request.session.get("usuario"),
            "tiene_api_key": has_api_key(),
        },
    )


@require_login
def admin_telegram_chat_view(request, nombre):
    """Chat con un bot específico dentro de /admin/telegram."""
    get_agent_or_404(nombre)
    agent_data = load_agent_data(nombre)
    active_session = obtener_o_crear_sesion_activa(nombre)
    messages = obtener_todos_mensajes_sesion(active_session["id"])
    return render(
        request,
        "telegram.html",
        {
            "agente": agent_data,
            "sesion_activa": active_session,
            "mensajes": messages,
            "tiene_api_key": has_api_key(),
            "usuario_actual": request.session.get("usuario"),
            "volver_url": "/admin/telegram",
        },
    )


# ----------------------------------------------------------------------
# Autenticación (Login / Logout)
# ----------------------------------------------------------------------


@csrf_exempt
def login_view(request):
    """Página y procesamiento de inicio de sesión."""
    if request.method == "GET":
        if request.session.get("usuario"):
            next_url = request.GET.get("next") or "/dashboard"
            return redirect(next_url)
        return render(request, "login.html", {"next": request.GET.get("next", "")})

    # Procesar método POST
    payload = parse_body(request)
    username = (payload.get("usuario") or "").strip()
    password = (payload.get("password") or "").strip()
    next_url = (
        request.GET.get("next")
        or payload.get("next")
        or "/dashboard"
    )

    user_result = verificar_usuario(username, password)
    is_json = request.content_type == "application/json" or request.headers.get("x-requested-with") == "XMLHttpRequest"

    if not user_result:
        if is_json:
            return JsonResponse({"error": "Usuario o contraseña incorrectos."}, status=401)
        return render(
            request,
            "login.html",
            {"error": "Usuario o contraseña incorrectos.", "usuario": username, "next": next_url},
            status=401,
        )

    request.session["usuario"] = user_result["usuario"]
    request.session["rol"] = user_result["rol"]

    if is_json:
        return JsonResponse({"ok": True, "redirect": next_url})
    return redirect(next_url)


def logout_action(request):
    """Cierra la sesión del usuario actual."""
    request.session.flush()
    return redirect("/")


# ----------------------------------------------------------------------
# Dashboard Administrativo y Grupos
# ----------------------------------------------------------------------


@require_login
def dashboard_view(request):
    """Vista principal del Dashboard administrativo."""
    stats = obtener_estadisticas_dashboard()
    grupos = listar_grupos()
    grupo_param = request.GET.get("grupo")
    grupo_seleccionado = None
    if grupo_param is not None:
        try:
            grupo_seleccionado = int(grupo_param)
            grupo = next((g for g in grupos if g["id"] == grupo_seleccionado), None)
            if grupo is None:
                raise Http404("Grupo no encontrado")
            stats["agentes"] = [a for a in stats["agentes"] if a["nombre"] in grupo["agentes"]]
        except ValueError:
            raise Http404("Parámetro de grupo no válido")

    sources = listar_fuentes()
    roles = listar_roles()
    users = listar_usuarios()
    return render(
        request,
        "dashboard.html",
        {
            "stats": stats,
            "grupos": grupos,
            "grupo_seleccionado": grupo_seleccionado,
            "nombres_agentes": listar_agentes(),
            "fuentes": sources,
            "roles": roles,
            "usuarios": users,
            "identidades": IDENTIDADES,
            "usuario_actual": request.session.get("usuario"),
            "tiene_api_key": has_api_key(),
        },
    )


@csrf_exempt
@require_login
def crear_grupo_view(request):
    """Crea un nuevo grupo de agentes."""
    if request.method != "POST":
        return HttpResponse("Método no permitido", status=405)
    nombre = request.POST.get("nombre", "").strip()
    try:
        crear_grupo(nombre)
    except ValueError as exc:
        return HttpResponse(str(exc), status=400)
    return redirect("/dashboard")


@csrf_exempt
@require_login
def asignar_grupo_view(request):
    """Asigna un agente a un grupo."""
    if request.method != "POST":
        return HttpResponse("Método no permitido", status=405)
    try:
        grupo_id = int(request.POST.get("grupo_id", ""))
        agente = request.POST.get("agente", "").strip()
        asignar_grupo(agente, grupo_id)
    except (ValueError, TypeError) as exc:
        return HttpResponse(str(exc), status=400)
    return redirect(f"/dashboard?grupo={grupo_id}")


# ----------------------------------------------------------------------
# API JSON: Agentes y Métricas
# ----------------------------------------------------------------------


@require_login
def api_dashboard_stats(request):
    """Métricas del sistema para el panel de control."""
    return JsonResponse(obtener_estadisticas_dashboard())


@csrf_exempt
def api_get_agent(request, nombre):
    """Detalle de un agente en formato JSON."""
    get_agent_or_404(nombre)
    return JsonResponse(load_agent_data(nombre))


@csrf_exempt
@require_login
def api_upload_avatar(request):
    """Sube una imagen de avatar para un agente."""
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)

    file = request.FILES.get("avatar") or request.FILES.get("file")
    if not file or not file.name:
        return JsonResponse({"error": "No se envió ningún archivo de imagen."}, status=400)

    parts = file.name.rsplit(".", 1)
    if len(parts) < 2 or parts[1].lower() not in ALLOWED_EXTENSIONS:
        return JsonResponse({"error": "Formato no permitido. Usa PNG, JPG, JPEG, WEBP, GIF o SVG."}, status=400)

    extension = parts[1].lower()
    clean_base = get_valid_filename(parts[0])
    filename = f"{uuid.uuid4().hex[:12]}_{clean_base}.{extension}"
    target_path = os.path.join(settings.AVATAR_UPLOAD_FOLDER, filename)

    with open(target_path, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    relative_url = f"/static/uploads/avatars/{filename}"
    return JsonResponse({"ok": True, "url": relative_url})


@csrf_exempt
def api_create_agent(request):
    """Crea un nuevo agente en la base de datos."""
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)

    payload = parse_body(request)
    name = (payload.get("nombre") or "").strip()
    if not name:
        return JsonResponse({"error": "Escribe un nombre para el agente."}, status=400)
    if "/" in name or "\\" in name or name.startswith("."):
        return JsonResponse({"error": "El nombre no puede contener '/' ni '\\'."}, status=400)
    if name in listar_agentes():
        return JsonResponse({"error": f"El agente '{name}' ya existe."}, status=400)

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
    return JsonResponse({"ok": True, "nombre": name}, status=201)


@csrf_exempt
@require_login
def api_delete_agent(request, nombre):
    """Elimina un agente del sistema."""
    if request.method != "DELETE":
        return JsonResponse({"error": "Método no permitido."}, status=405)
    get_agent_or_404(nombre)
    success = eliminar_agente(nombre)
    if not success:
        return JsonResponse({"error": "No se pudo eliminar el agente."}, status=500)
    return JsonResponse({"ok": True, "mensaje": f"Agente '{nombre}' eliminado correctamente."})


@csrf_exempt
def api_update_agent_profile(request, nombre):
    """Actualiza el perfil descriptivo de un agente."""
    get_agent_or_404(nombre)
    payload = parse_body(request)
    text = (payload.get("perfil") or "").strip()
    if not text:
        return JsonResponse({"error": "El perfil no puede estar vacío."}, status=400)
    actualizar_perfil(nombre, text)
    return JsonResponse(load_agent_data(nombre))


@csrf_exempt
def api_update_agent_knowledge(request, nombre):
    """Actualiza la base de conocimiento directa del agente."""
    get_agent_or_404(nombre)
    payload = parse_body(request)
    text = (payload.get("conocimiento") or "").strip()
    actualizar_conocimiento(nombre, text)
    return JsonResponse(load_agent_data(nombre))


@csrf_exempt
def api_change_agent_identity(request, nombre):
    """Actualiza la identidad o rol del agente."""
    get_agent_or_404(nombre)
    payload = parse_body(request)
    custom_prompt = (payload.get("identidad_custom") or "").strip()
    role_key = (payload.get("identidad") or "").strip()
    valid_role = bool(obtener_rol_por_clave(role_key)) or role_key in IDENTIDADES

    if custom_prompt:
        cambiar_identidad(nombre, custom=custom_prompt)
    elif valid_role:
        cambiar_identidad(nombre, clave=role_key)
    else:
        return JsonResponse({"error": "Identidad o rol no válido."}, status=400)
    return JsonResponse(load_agent_data(nombre))


@csrf_exempt
def api_edit_agent(request, nombre):
    """Edición integral de un agente."""
    get_agent_or_404(nombre)
    payload = parse_body(request)
    profile = (payload.get("perfil") or "").strip()
    knowledge = (payload.get("conocimiento") or "").strip()
    custom_prompt = (payload.get("identidad_custom") or "").strip()
    role_key = (payload.get("identidad") or "").strip()
    avatar_url = payload.get("avatar_url")
    sources = payload.get("fuentes") or payload.get("fuentes_ids")
    valid_role = bool(obtener_rol_por_clave(role_key)) or role_key in IDENTIDADES

    if not profile:
        return JsonResponse({"error": "El perfil no puede estar vacío."}, status=400)
    if not custom_prompt and not valid_role and role_key:
        return JsonResponse({"error": "Identidad o rol no válido."}, status=400)

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

    return JsonResponse(load_agent_data(nombre))


@csrf_exempt
def api_clear_agent_memory(request, nombre):
    """Borra la memoria activa del agente."""
    get_agent_or_404(nombre)
    borrar_memoria(nombre)
    return JsonResponse({"ok": True})


# ----------------------------------------------------------------------
# API JSON: Roles e Identidades
# ----------------------------------------------------------------------


@csrf_exempt
@require_login
def api_roles_collection(request):
    """Lista y creación de roles."""
    if request.method == "GET":
        return JsonResponse({"roles": listar_roles()})

    if request.method == "POST":
        payload = parse_body(request)
        key = (payload.get("clave") or "").strip().lower()
        name = (payload.get("nombre") or "").strip()
        desc = (payload.get("descripcion") or "").strip()
        prompt = (payload.get("prompt") or "").strip()

        if not key or not name or not prompt:
            return JsonResponse({"error": "La clave, el nombre y el prompt son obligatorios."}, status=400)

        try:
            new_id = crear_rol(key, name, desc, prompt)
        except ValueError as error:
            return JsonResponse({"error": str(error)}, status=400)

        return JsonResponse(
            {"id": new_id, "clave": key, "nombre": name, "descripcion": desc, "prompt": prompt},
            status=201,
        )

    return JsonResponse({"error": "Método no permitido."}, status=405)


@csrf_exempt
@require_login
def api_role_item(request, rol_id):
    """Consulta, edición y eliminación de un rol específico."""
    if request.method == "GET":
        role = obtener_rol(rol_id)
        if not role:
            return JsonResponse({"error": "Rol no encontrado."}, status=404)
        return JsonResponse(role)

    if request.method in ("POST", "PUT"):
        payload = parse_body(request)
        key = (payload.get("clave") or "").strip().lower()
        name = (payload.get("nombre") or "").strip()
        desc = (payload.get("descripcion") or "").strip()
        prompt = (payload.get("prompt") or "").strip()

        if not key or not name or not prompt:
            return JsonResponse({"error": "La clave, el nombre y el prompt son obligatorios."}, status=400)

        try:
            actualizar_rol(rol_id, key, name, desc, prompt)
        except ValueError as error:
            return JsonResponse({"error": str(error)}, status=400)

        return JsonResponse({"id": rol_id, "clave": key, "nombre": name, "descripcion": desc, "prompt": prompt})

    if request.method == "DELETE":
        success = eliminar_rol(rol_id)
        if not success:
            return JsonResponse({"error": "No se pudo eliminar el rol."}, status=404)
        return JsonResponse({"ok": True})

    return JsonResponse({"error": "Método no permitido."}, status=405)


# ----------------------------------------------------------------------
# API JSON: Usuarios y Perfil Administrativo
# ----------------------------------------------------------------------


@csrf_exempt
@require_login
def api_users_collection(request):
    """Lista y creación de usuarios."""
    if request.method == "GET":
        return JsonResponse({"usuarios": listar_usuarios()})

    if request.method == "POST":
        payload = parse_body(request)
        username = (payload.get("usuario") or "").strip()
        password = (payload.get("password") or "").strip()
        role = (payload.get("rol") or "usuario").strip()

        if not username or not password:
            return JsonResponse({"error": "El nombre de usuario y la contraseña son obligatorios."}, status=400)

        try:
            crear_usuario(username, password, role)
        except ValueError as error:
            return JsonResponse({"error": str(error)}, status=400)

        created_user = obtener_usuario_por_nombre(username)
        return JsonResponse(created_user, status=201)

    return JsonResponse({"error": "Método no permitido."}, status=405)


@csrf_exempt
@require_login
def api_user_item(request, usuario_id):
    """Consulta, edición y eliminación de un usuario específico."""
    if request.method == "GET":
        user = obtener_usuario(usuario_id)
        if not user:
            return JsonResponse({"error": "Usuario no encontrado."}, status=404)
        return JsonResponse(user)

    if request.method in ("POST", "PUT"):
        payload = parse_body(request)
        username = (payload.get("usuario") or "").strip()
        role = (payload.get("rol") or "usuario").strip()
        password = (payload.get("password") or "").strip()

        if not username:
            return JsonResponse({"error": "El nombre de usuario no puede estar vacío."}, status=400)

        try:
            actualizar_usuario(usuario_id, username, role, nuevo_password=password if password else None)
        except ValueError as error:
            return JsonResponse({"error": str(error)}, status=400)

        active_user = request.session.get("usuario")
        user_db = obtener_usuario(usuario_id)
        if active_user and user_db:
            session_info = obtener_usuario_por_nombre(active_user)
            if session_info and session_info["id"] == usuario_id:
                request.session["usuario"] = user_db["usuario"]
                request.session["rol"] = user_db["rol"]

        return JsonResponse(user_db)

    if request.method == "DELETE":
        active_user = request.session.get("usuario")
        try:
            success = eliminar_usuario(usuario_id, usuario_actual_nombre=active_user)
            if not success:
                return JsonResponse({"error": "Usuario no encontrado."}, status=404)
        except ValueError as error:
            return JsonResponse({"error": str(error)}, status=400)
        return JsonResponse({"ok": True})

    return JsonResponse({"error": "Método no permitido."}, status=405)


@csrf_exempt
@require_login
def api_my_profile(request):
    """Perfil del usuario actualmente autenticado."""
    username = request.session.get("usuario")
    if not username:
        return JsonResponse({"error": "No autenticado."}, status=401)

    user_info = obtener_usuario_por_nombre(username)
    if not user_info:
        return JsonResponse({"error": "Usuario no encontrado."}, status=404)

    if request.method == "GET":
        return JsonResponse(user_info)

    if request.method == "POST":
        payload = parse_body(request)
        new_username = (payload.get("usuario") or username).strip()
        new_password = (payload.get("password") or "").strip()

        try:
            actualizar_usuario(
                user_info["id"],
                new_username,
                nuevo_rol=user_info["rol"],
                nuevo_password=new_password if new_password else None,
            )
            request.session["usuario"] = new_username
        except ValueError as error:
            return JsonResponse({"error": str(error)}, status=400)

        return JsonResponse(obtener_usuario(user_info["id"]))

    return JsonResponse({"error": "Método no permitido."}, status=405)


# ----------------------------------------------------------------------
# API JSON: Sesiones de Chat y Conversaciones
# ----------------------------------------------------------------------


@require_login
def api_all_sessions(request):
    """Lista todas las sesiones registradas en el sistema."""
    agent_filter = request.GET.get("agente")
    return JsonResponse({"sesiones": listar_todas_las_sesiones(agent_filter if agent_filter else None)})


@csrf_exempt
@require_login
def api_agent_sessions(request, nombre):
    """Lista o crea sesiones de chat asociadas a un agente."""
    get_agent_or_404(nombre)
    if request.method == "GET":
        return JsonResponse({"sesiones": listar_sesiones_agente(nombre)})

    if request.method == "POST":
        payload = parse_body(request)
        title = (payload.get("titulo") or "").strip()
        new_session = crear_sesion_chat(nombre, titulo=title if title else None)
        return JsonResponse(new_session, status=201)

    return JsonResponse({"error": "Método no permitido."}, status=405)


@csrf_exempt
@require_login
def api_session_item(request, sesion_id):
    """Consulta, renombrado o eliminación de una sesión."""
    chat_session = obtener_sesion_chat(sesion_id)
    if not chat_session:
        return JsonResponse({"error": "Conversación no encontrada."}, status=404)

    if request.method == "GET":
        messages = obtener_todos_mensajes_sesion(sesion_id)
        chat_session["mensajes"] = messages
        return JsonResponse(chat_session)

    if request.method in ("POST", "PUT"):
        payload = parse_body(request)
        title = (payload.get("titulo") or "").strip()
        if not title:
            return JsonResponse({"error": "El título no puede estar vacío."}, status=400)
        renombrar_sesion_chat(sesion_id, title)
        return JsonResponse({"ok": True, "id": sesion_id, "titulo": title})

    if request.method == "DELETE":
        eliminar_sesion_chat(sesion_id)
        return JsonResponse({"ok": True})

    return JsonResponse({"error": "Método no permitido."}, status=405)


@csrf_exempt
@require_login
def api_send_session_message(request, sesion_id):
    """Envía un mensaje a la sesión de chat y recibe respuesta del agente."""
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)

    chat_session = obtener_sesion_chat(sesion_id)
    if not chat_session:
        return JsonResponse({"error": "Conversación no encontrada."}, status=404)

    agent_name = chat_session["agente_nombre"]
    payload = parse_body(request)
    user_message = (payload.get("mensaje") or "").strip()
    if not user_message:
        return JsonResponse({"error": "El mensaje no puede estar vacío."}, status=400)

    custom_max_tokens = payload.get("max_tokens")
    try:
        max_tokens_val = int(custom_max_tokens) if custom_max_tokens else 400
    except (ValueError, TypeError):
        max_tokens_val = 400

    try:
        agent = AgentDB(agent_name)
    except ValueError as error:
        return JsonResponse({"error": str(error)}, status=400)

    try:
        assistant_response = agent.preguntar(user_message, sesion_id=sesion_id, max_tokens=max_tokens_val)
    except RuntimeError as error:
        return JsonResponse({"error": str(error)}, status=500)

    try:
        new_memories = agent.actualizar_memoria(user_message, assistant_response)
    except Exception:
        new_memories = []

    updated_session = obtener_sesion_chat(sesion_id)
    return JsonResponse(
        {
            "respuesta": assistant_response,
            "memoria_guardada": bool(new_memories),
            "sesion": updated_session,
        }
    )


@csrf_exempt
@require_login
def api_send_agent_message_fallback(request, nombre):
    """Envía mensaje al agente utilizando su sesión activa por defecto."""
    get_agent_or_404(nombre)
    active_session = obtener_o_crear_sesion_activa(nombre)
    return api_send_session_message(request, active_session["id"])


# ----------------------------------------------------------------------
# API JSON: Bases de Conocimiento
# ----------------------------------------------------------------------


@csrf_exempt
def api_sources_collection(request):
    """Lista o crea bases de conocimiento."""
    if request.method == "GET":
        return JsonResponse({"fuentes": listar_fuentes()})

    if request.method == "POST":
        payload = parse_body(request)
        name = (payload.get("nombre") or "").strip()
        content = (payload.get("contenido") or "").strip()
        if not name:
            return JsonResponse({"error": "Escribe un nombre para la base de conocimiento."}, status=400)
        try:
            new_id = crear_fuente(name, content)
        except ValueError as error:
            return JsonResponse({"error": str(error)}, status=400)
        return JsonResponse({"id": new_id, "nombre": name, "contenido": content}, status=201)

    return JsonResponse({"error": "Método no permitido."}, status=405)


@csrf_exempt
def api_source_item(request, fuente_id):
    """Consulta, edición y eliminación de una base de conocimiento."""
    if request.method == "GET":
        source = obtener_fuente(fuente_id)
        if not source:
            return JsonResponse({"error": "Base de conocimiento no encontrada."}, status=404)
        return JsonResponse(source)

    if request.method in ("POST", "PUT"):
        payload = parse_body(request)
        name = (payload.get("nombre") or "").strip()
        content = (payload.get("contenido") or "").strip()
        if not name:
            return JsonResponse({"error": "El nombre de la base de conocimiento no puede estar vacío."}, status=400)
        try:
            actualizar_fuente(fuente_id, name, content)
        except ValueError as error:
            return JsonResponse({"error": str(error)}, status=400)
        return JsonResponse({"id": fuente_id, "nombre": name, "contenido": content})

    if request.method == "DELETE":
        eliminar_fuente(fuente_id)
        return JsonResponse({"ok": True})

    return JsonResponse({"error": "Método no permitido."}, status=405)
