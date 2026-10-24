"""Servicio de roles e identidades del sistema."""

from django.db import transaction
from agentes.models import Agente, Rol
from .base import _ahora_str


def crear_rol(clave, nombre, descripcion="", prompt="", es_sistema=False):
    """Crea un nuevo rol en la base de datos."""
    clave = clave.strip().lower()
    nombre = nombre.strip()
    if not clave or not nombre:
        raise ValueError("La clave y el nombre del rol son obligatorios.")
    if not prompt.strip():
        raise ValueError("El prompt de rol no puede estar vacío.")
    if Rol.objects.filter(clave=clave).exists():
        raise ValueError(f"Ya existe un rol con la clave '{clave}'.")
    ahora = _ahora_str()
    rol = Rol.objects.create(
        clave=clave,
        nombre=nombre,
        descripcion=descripcion.strip(),
        prompt=prompt.strip(),
        es_sistema=1 if es_sistema else 0,
        creado_en=ahora,
        actualizado_en=ahora,
    )
    return rol.id


def obtener_rol(rol_id):
    """Devuelve un rol por su ID."""
    rol = Rol.objects.filter(id=rol_id).first()
    if not rol:
        return None
    return {
        "id": rol.id,
        "clave": rol.clave,
        "nombre": rol.nombre,
        "descripcion": rol.descripcion,
        "prompt": rol.prompt,
        "es_sistema": rol.es_sistema,
        "creado_en": rol.creado_en,
        "actualizado_en": rol.actualizado_en,
    }


def obtener_rol_por_clave(clave):
    """Devuelve un rol por su clave técnica."""
    rol = Rol.objects.filter(clave=clave.strip().lower()).first()
    if not rol:
        return None
    return {
        "id": rol.id,
        "clave": rol.clave,
        "nombre": rol.nombre,
        "descripcion": rol.descripcion,
        "prompt": rol.prompt,
        "es_sistema": rol.es_sistema,
        "creado_en": rol.creado_en,
        "actualizado_en": rol.actualizado_en,
    }


def listar_roles():
    """Devuelve todos los roles ordenados por nombre."""
    return [
        {
            "id": r.id,
            "clave": r.clave,
            "nombre": r.nombre,
            "descripcion": r.descripcion,
            "prompt": r.prompt,
            "es_sistema": r.es_sistema,
            "creado_en": r.creado_en,
            "actualizado_en": r.actualizado_en,
        }
        for r in Rol.objects.order_by("nombre")
    ]


def actualizar_rol(rol_id, clave, nombre, descripcion="", prompt=""):
    """Actualiza la clave, nombre, descripción y prompt de un rol."""
    clave = clave.strip().lower()
    nombre = nombre.strip()
    descripcion = descripcion.strip()
    prompt = prompt.strip()
    if not clave or not nombre:
        raise ValueError("La clave y el nombre del rol son obligatorios.")
    if not prompt:
        raise ValueError("El prompt de rol no puede estar vacío.")

    rol = Rol.objects.filter(id=rol_id).first()
    if not rol:
        raise ValueError("El rol especificado no existe.")

    clave_anterior = rol.clave
    if Rol.objects.filter(clave=clave).exclude(id=rol_id).exists():
        raise ValueError(f"Ya existe otro rol con la clave '{clave}'.")

    with transaction.atomic():
        rol.clave = clave
        rol.nombre = nombre
        rol.descripcion = descripcion
        rol.prompt = prompt
        rol.actualizado_en = _ahora_str()
        rol.save()

        if clave != clave_anterior:
            Agente.objects.filter(identidad_clave=clave_anterior).update(identidad_clave=clave)


def eliminar_rol(rol_id):
    """Elimina un rol y reasigna los agentes al rol básico por defecto."""
    rol = Rol.objects.filter(id=rol_id).first()
    if not rol:
        return False
    with transaction.atomic():
        Agente.objects.filter(identidad_clave=rol.clave).update(identidad_clave="basic")
        rol.delete()
    return True
