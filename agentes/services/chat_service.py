"""Servicio de sesiones de chat e historial de conversaciones."""

from agentes.models import Agente, Conversacion, SesionChat
from .base import HISTORIAL_RECIENTE, _ahora_str, _fecha_str, _hora_str


def crear_sesion_chat(agente_nombre, titulo="Nueva conversación"):
    """Crea una nueva sesión de chat para un agente."""
    agente = Agente.objects.filter(nombre=agente_nombre.strip().lower()).first()
    if not agente:
        raise ValueError(f"El agente '{agente_nombre}' no existe.")
    ahora = _ahora_str()
    sesion = SesionChat.objects.create(
        agente=agente,
        titulo=titulo.strip() or "Nueva conversación",
        creado_en=ahora,
        actualizado_en=ahora,
    )
    return sesion.id


def obtener_sesion_chat(sesion_id):
    """Devuelve los datos de una sesión por su ID."""
    sesion = SesionChat.objects.filter(id=sesion_id).select_related("agente").first()
    if not sesion:
        return None
    return {
        "id": sesion.id,
        "agente_id": sesion.agente.id,
        "agente_nombre": sesion.agente.nombre,
        "titulo": sesion.titulo,
        "creado_en": sesion.creado_en,
        "actualizado_en": sesion.actualizado_en,
    }


def obtener_o_crear_sesion_activa(agente_nombre):
    """Devuelve la sesión más reciente del agente o crea una si no existe."""
    agente = Agente.objects.filter(nombre=agente_nombre.strip().lower()).first()
    if not agente:
        raise ValueError(f"El agente '{agente_nombre}' no existe.")

    sesion = SesionChat.objects.filter(agente=agente).order_by("-actualizado_en", "-id").first()
    if not sesion:
        sid = crear_sesion_chat(agente.nombre, "Conversación inicial")
        return obtener_sesion_chat(sid)

    return {
        "id": sesion.id,
        "agente_id": sesion.agente.id,
        "agente_nombre": sesion.agente.nombre,
        "titulo": sesion.titulo,
        "creado_en": sesion.creado_en,
        "actualizado_en": sesion.actualizado_en,
    }


def listar_sesiones_agente(agente_nombre):
    """Devuelve todas las sesiones de un agente ordenadas por actualización."""
    agente = Agente.objects.filter(nombre=agente_nombre.strip().lower()).first()
    if not agente:
        return []

    sesiones = (
        SesionChat.objects.filter(agente=agente)
        .order_by("-actualizado_en", "-id")
    )
    resultado = []
    for s in sesiones:
        ultimo = Conversacion.objects.filter(sesion=s).order_by("-id").first()
        resultado.append({
            "id": s.id,
            "titulo": s.titulo,
            "creado_en": s.creado_en,
            "actualizado_en": s.actualizado_en,
            "agente_nombre": agente.nombre,
            "total_mensajes": Conversacion.objects.filter(sesion=s).count(),
            "ultimo_mensaje": ultimo.mensaje if ultimo else None,
        })
    return resultado


def renombrar_sesion_chat(sesion_id, nuevo_titulo):
    """Cambia el título de una sesión de chat."""
    nuevo_titulo = (nuevo_titulo or "").strip() or "Conversación"
    SesionChat.objects.filter(id=sesion_id).update(
        titulo=nuevo_titulo,
        actualizado_en=_ahora_str(),
    )


def eliminar_sesion_chat(sesion_id):
    """Elimina una sesión de chat y sus mensajes."""
    deleted, _ = SesionChat.objects.filter(id=sesion_id).delete()
    return deleted > 0


def guardar_mensaje(agente_nombre, rol, mensaje, sesion_id=None):
    """Guarda un mensaje en el historial del agente."""
    agente = Agente.objects.filter(nombre=agente_nombre.strip().lower()).first()
    if not agente:
        raise ValueError(f"El agente '{agente_nombre}' no existe.")

    sesion = None
    if sesion_id:
        sesion = SesionChat.objects.filter(id=sesion_id, agente=agente).first()
    if not sesion:
        activa = obtener_o_crear_sesion_activa(agente.nombre)
        sesion = SesionChat.objects.get(id=activa["id"])

    conv = Conversacion.objects.create(
        agente=agente,
        sesion=sesion,
        fecha=_fecha_str(),
        hora=_hora_str(),
        rol=rol,
        mensaje=mensaje,
    )
    SesionChat.objects.filter(id=sesion.id).update(actualizado_en=_ahora_str())
    return conv.id


def obtener_historial(agente_nombre, cantidad=HISTORIAL_RECIENTE, sesion_id=None):
    """Devuelve los últimos N mensajes de la conversación como lista de tuplas (rol, mensaje)."""
    agente = Agente.objects.filter(nombre=agente_nombre.strip().lower()).first()
    if not agente:
        return []

    qs = Conversacion.objects.filter(agente=agente)
    if sesion_id:
        qs = qs.filter(sesion_id=sesion_id)

    mensajes = list(qs.order_by("-id")[:cantidad])
    mensajes.reverse()
    return [(m.rol, m.mensaje) for m in mensajes]


def obtener_todos_mensajes_sesion(sesion_id):
    """Devuelve todos los mensajes de una sesión ordenados cronológicamente."""
    mensajes = Conversacion.objects.filter(sesion_id=sesion_id).order_by("id")
    return [
        {
            "id": m.id,
            "agente_id": m.agente.id,
            "sesion_id": m.sesion_id,
            "fecha": m.fecha,
            "hora": m.hora,
            "rol": m.rol,
            "mensaje": m.mensaje,
        }
        for m in mensajes
    ]


def listar_todas_las_sesiones(nombre_agente=None):
    """Devuelve todas las sesiones de chat con información del agente y mensajes."""
    qs = SesionChat.objects.select_related("agente")
    if nombre_agente:
        qs = qs.filter(agente__nombre=nombre_agente.strip().lower())
    qs = qs.order_by("-actualizado_en", "-id")

    resultado = []
    for s in qs:
        ultimo = Conversacion.objects.filter(sesion=s).order_by("-id").first()
        resultado.append({
            "id": s.id,
            "titulo": s.titulo,
            "creado_en": s.creado_en,
            "actualizado_en": s.actualizado_en,
            "agente_nombre": s.agente.nombre,
            "total_mensajes": Conversacion.objects.filter(sesion=s).count(),
            "ultimo_mensaje": ultimo.mensaje if ultimo else None,
        })
    return resultado
