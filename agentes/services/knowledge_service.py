"""Servicio de fuentes y bases de conocimiento de agentes."""

from django.db import transaction
from agentes.models import Agente, AgenteFuente, FuenteConocimiento
from .base import _ahora_str


def crear_fuente(nombre, contenido=""):
    """Crea una nueva fuente de conocimiento."""
    nombre = nombre.strip()
    if not nombre:
        raise ValueError("El nombre de la fuente no puede estar vacío.")
    if FuenteConocimiento.objects.filter(nombre=nombre).exists():
        raise ValueError(f"La fuente '{nombre}' ya existe.")
    fuente = FuenteConocimiento.objects.create(
        nombre=nombre,
        contenido=contenido,
        creado_en=_ahora_str(),
    )
    return fuente.id


def obtener_fuente(fuente_id):
    """Devuelve una fuente de conocimiento por su ID."""
    fuente = FuenteConocimiento.objects.filter(id=fuente_id).first()
    if not fuente:
        return None
    return {
        "id": fuente.id,
        "nombre": fuente.nombre,
        "contenido": fuente.contenido,
        "creado_en": fuente.creado_en,
    }


def obtener_fuente_por_nombre(nombre):
    """Devuelve una fuente de conocimiento por su nombre."""
    fuente = FuenteConocimiento.objects.filter(nombre=nombre.strip()).first()
    if not fuente:
        return None
    return {
        "id": fuente.id,
        "nombre": fuente.nombre,
        "contenido": fuente.contenido,
        "creado_en": fuente.creado_en,
    }


def listar_fuentes():
    """Devuelve todas las fuentes de conocimiento."""
    return [
        {
            "id": f.id,
            "nombre": f.nombre,
            "contenido": f.contenido,
            "creado_en": f.creado_en,
        }
        for f in FuenteConocimiento.objects.order_by("nombre")
    ]


def actualizar_fuente(fuente_id, nombre, contenido):
    """Actualiza el nombre y contenido de una fuente."""
    nombre = nombre.strip()
    if not nombre:
        raise ValueError("El nombre de la fuente no puede estar vacío.")
    if FuenteConocimiento.objects.filter(nombre=nombre).exclude(id=fuente_id).exists():
        raise ValueError(f"Ya existe otra fuente con el nombre '{nombre}'.")
    FuenteConocimiento.objects.filter(id=fuente_id).update(nombre=nombre, contenido=contenido)


def eliminar_fuente(fuente_id):
    """Elimina una fuente de conocimiento."""
    deleted, _ = FuenteConocimiento.objects.filter(id=fuente_id).delete()
    return deleted > 0


def establecer_fuentes_agente(agente_id_o_nombre, fuentes_ids):
    """Reemplaza las fuentes asociadas a un agente."""
    if isinstance(agente_id_o_nombre, int) or (isinstance(agente_id_o_nombre, str) and agente_id_o_nombre.isdigit()):
        agente = Agente.objects.filter(id=int(agente_id_o_nombre)).first()
    else:
        agente = Agente.objects.filter(nombre=str(agente_id_o_nombre).strip().lower()).first()

    if not agente:
        return

    with transaction.atomic():
        AgenteFuente.objects.filter(agente=agente).delete()
        for fid in (fuentes_ids or []):
            fuente = FuenteConocimiento.objects.filter(id=fid).first()
            if fuente:
                AgenteFuente.objects.create(agente=agente, fuente=fuente)


def obtener_fuentes_agente(agente_id_o_nombre):
    """Devuelve las fuentes asociadas a un agente."""
    if isinstance(agente_id_o_nombre, int) or (isinstance(agente_id_o_nombre, str) and agente_id_o_nombre.isdigit()):
        agente = Agente.objects.filter(id=int(agente_id_o_nombre)).first()
    else:
        agente = Agente.objects.filter(nombre=str(agente_id_o_nombre).strip().lower()).first()

    if not agente:
        return []

    af_list = AgenteFuente.objects.filter(agente=agente).select_related("fuente").order_by("fuente__nombre")
    return [
        {
            "id": af.fuente.id,
            "nombre": af.fuente.nombre,
            "contenido": af.fuente.contenido,
        }
        for af in af_list
    ]
