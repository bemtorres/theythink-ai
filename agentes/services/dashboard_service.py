"""Servicio de analítica y métricas para el dashboard y catálogo."""

from django.db import transaction
from agentes.models import (
    Agente,
    AgenteFuente,
    AgenteGrupo,
    Conversacion,
    FuenteConocimiento,
    Grupo,
    Rol,
    SesionChat,
    Usuario,
)
from .chat_service import listar_todas_las_sesiones
from .role_service import listar_roles
from .user_service import listar_usuarios


def listar_catalogo_agentes():
    """Consulta ligera de los campos públicos necesarios para descubrir agentes."""
    return list(Agente.objects.order_by("nombre").values("nombre", "perfil", "avatar_url"))


def obtener_estadisticas_dashboard():
    """Devuelve métricas y listados consolidados para el dashboard administrativo."""
    total_agentes = Agente.objects.count()
    total_fuentes = FuenteConocimiento.objects.count()
    total_roles = Rol.objects.count()
    total_usuarios = Usuario.objects.count()
    total_sesiones = SesionChat.objects.count()
    total_mensajes = Conversacion.objects.count()

    agentes_stats = []
    for a in Agente.objects.order_by("nombre"):
        agentes_stats.append({
            "id": a.id,
            "nombre": a.nombre,
            "perfil": a.perfil,
            "identidad_clave": a.identidad_clave,
            "identidad_custom": a.identidad_custom,
            "avatar_url": a.avatar_url,
            "memoria": a.memoria,
            "creado_en": a.creado_en,
            "total_sesiones": SesionChat.objects.filter(agente=a).count(),
            "total_mensajes": Conversacion.objects.filter(agente=a).count(),
            "total_fuentes": AgenteFuente.objects.filter(agente=a).count(),
        })

    ultimas_sesiones = []
    for s in SesionChat.objects.select_related("agente").order_by("-actualizado_en", "-id")[:12]:
        ultimas_sesiones.append({
            "id": s.id,
            "titulo": s.titulo,
            "creado_en": s.creado_en,
            "actualizado_en": s.actualizado_en,
            "agente_nombre": s.agente.nombre,
            "total_mensajes": Conversacion.objects.filter(sesion=s).count(),
        })

    return {
        "total_agentes": total_agentes,
        "total_fuentes": total_fuentes,
        "total_roles": total_roles,
        "total_usuarios": total_usuarios,
        "total_sesiones": total_sesiones,
        "total_mensajes": total_mensajes,
        "agentes": agentes_stats,
        "ultimas_sesiones": ultimas_sesiones,
        "todas_las_sesiones": listar_todas_las_sesiones(),
        "roles": listar_roles(),
        "usuarios": listar_usuarios(),
    }


def vaciar():
    """Elimina los datos de las tablas de la aplicación para permitir re-sembrado (--force)."""
    with transaction.atomic():
        Conversacion.objects.all().delete()
        SesionChat.objects.all().delete()
        AgenteFuente.objects.all().delete()
        AgenteGrupo.objects.all().delete()
        Agente.objects.all().delete()
        FuenteConocimiento.objects.all().delete()
        Grupo.objects.all().delete()
        Rol.objects.filter(es_sistema=0).delete()


def migrar_conocimientos_legacy():
    """Delegado hacia los seeders de personajes canónicos si no existiesen."""
    from agentes.seeders.seeder_runner import seed_characters
    seed_characters()
