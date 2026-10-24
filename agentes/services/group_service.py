"""Servicio de agrupación de agentes."""

from django.db import transaction
from agentes.models import Agente, AgenteGrupo, Grupo


def crear_grupo(nombre):
    """Crea un grupo de agentes por nombre si no existe."""
    nombre = nombre.strip()
    if not nombre:
        raise ValueError("El nombre del grupo no puede estar vacío.")
    grupo, _ = Grupo.objects.get_or_create(nombre=nombre)
    return grupo.id


def obtener_grupo(grupo_id):
    """Devuelve el grupo por su ID o None."""
    grupo = Grupo.objects.filter(id=grupo_id).first()
    if not grupo:
        return None
    return {"id": grupo.id, "nombre": grupo.nombre}


def obtener_grupo_por_nombre(nombre):
    """Devuelve el grupo por su nombre o None."""
    grupo = Grupo.objects.filter(nombre=nombre.strip()).first()
    if not grupo:
        return None
    return {"id": grupo.id, "nombre": grupo.nombre}


def listar_grupos():
    """Devuelve los grupos existentes con la lista de nombres de sus agentes."""
    resultado = []
    for g in Grupo.objects.order_by("nombre"):
        nombres = list(
            AgenteGrupo.objects.filter(grupo=g)
            .select_related("agente")
            .order_by("agente__nombre")
            .values_list("agente__nombre", flat=True)
        )
        resultado.append({"id": g.id, "nombre": g.nombre, "agentes": nombres})
    return resultado


def asignar_grupo(agente_nombre, grupo_id):
    """Asocia un agente a un grupo (reemplaza cualquier asignación previa)."""
    agente = Agente.objects.filter(nombre=agente_nombre.strip().lower()).first()
    grupo = Grupo.objects.filter(id=grupo_id).first()
    if not agente or not grupo:
        return
    with transaction.atomic():
        AgenteGrupo.objects.filter(agente=agente).delete()
        AgenteGrupo.objects.create(agente=agente, grupo=grupo)


def obtener_grupo_agente(agente_nombre):
    """Devuelve el grupo al que pertenece el agente o None."""
    agente = Agente.objects.filter(nombre=agente_nombre.strip().lower()).first()
    if not agente:
        return None
    ag = AgenteGrupo.objects.filter(agente=agente).select_related("grupo").first()
    if not ag:
        return None
    return {"id": ag.grupo.id, "nombre": ag.grupo.nombre}


def listar_agentes_por_grupo(grupo_id):
    """Devuelve los nombres de agentes que pertenecen a un grupo."""
    return list(
        AgenteGrupo.objects.filter(grupo_id=grupo_id)
        .select_related("agente")
        .order_by("agente__nombre")
        .values_list("agente__nombre", flat=True)
    )
