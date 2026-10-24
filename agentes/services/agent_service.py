"""Servicio de dominio para la gestión del ciclo de vida de los agentes."""

from django.db import transaction
from agentes.models import Agente, AgenteFuente, FuenteConocimiento
from .base import _ahora_str, avatar_local


def crear_agente(
    nombre,
    perfil="",
    conocimiento="",
    identidad_clave="",
    identidad_custom="",
    memoria="",
    avatar_url="",
    fuentes_ids=None,
):
    """Crea un agente nuevo en la base de datos y asocia sus fuentes si se pasan."""
    nombre = nombre.strip().lower()
    avatar_url = avatar_url.strip() or avatar_local(nombre)

    if Agente.objects.filter(nombre=nombre).exists():
        raise ValueError(f"El agente '{nombre}' ya existe.")

    with transaction.atomic():
        agente = Agente.objects.create(
            nombre=nombre,
            perfil=perfil,
            conocimiento=conocimiento,
            identidad_clave=identidad_clave,
            identidad_custom=identidad_custom,
            memoria=memoria,
            avatar_url=avatar_url,
            creado_en=_ahora_str(),
        )

        if fuentes_ids:
            for fuente_id in fuentes_ids:
                fuente = FuenteConocimiento.objects.filter(id=fuente_id).first()
                if fuente:
                    AgenteFuente.objects.create(agente=agente, fuente=fuente)

    return agente.id


def obtener_agente(nombre_o_id):
    """Devuelve los datos del agente como diccionario o None."""
    if isinstance(nombre_o_id, int) or (isinstance(nombre_o_id, str) and nombre_o_id.isdigit()):
        agente = Agente.objects.filter(id=int(nombre_o_id)).first()
    else:
        agente = Agente.objects.filter(nombre=str(nombre_o_id).strip().lower()).first()

    if not agente:
        return None

    return {
        "id": agente.id,
        "nombre": agente.nombre,
        "perfil": agente.perfil,
        "conocimiento": agente.conocimiento,
        "memoria": agente.memoria,
        "identidad_clave": agente.identidad_clave,
        "identidad_custom": agente.identidad_custom,
        "avatar_url": agente.avatar_url,
        "creado_en": agente.creado_en,
    }


def listar_agentes():
    """Devuelve los nombres de todos los agentes registrados."""
    return list(Agente.objects.order_by("nombre").values_list("nombre", flat=True))


def existe_agente(nombre):
    """True si el agente existe en la base de datos."""
    return Agente.objects.filter(nombre=str(nombre).strip().lower()).exists()


def actualizar_perfil(nombre, perfil):
    """Actualiza el texto del perfil de un agente."""
    Agente.objects.filter(nombre=nombre.strip().lower()).update(perfil=perfil)


def actualizar_conocimiento(nombre, conocimiento):
    """Actualiza el conocimiento directo de un agente."""
    Agente.objects.filter(nombre=nombre.strip().lower()).update(conocimiento=conocimiento)


def actualizar_memoria(nombre, memoria):
    """Actualiza la memoria de un agente."""
    Agente.objects.filter(nombre=nombre.strip().lower()).update(memoria=memoria)


def borrar_memoria(nombre):
    """Limpia la memoria de un agente."""
    Agente.objects.filter(nombre=nombre.strip().lower()).update(memoria="")


def actualizar_avatar(nombre, avatar_url):
    """Actualiza la URL del avatar de un agente."""
    Agente.objects.filter(nombre=nombre.strip().lower()).update(avatar_url=avatar_url.strip())


def cambiar_identidad(nombre, clave="", custom=""):
    """Cambia la identidad asignada a un agente."""
    Agente.objects.filter(nombre=nombre.strip().lower()).update(
        identidad_clave=clave.strip(),
        identidad_custom=custom.strip(),
    )


def eliminar_agente(nombre):
    """Elimina un agente y todos sus registros en cascada."""
    deleted, _ = Agente.objects.filter(nombre=nombre.strip().lower()).delete()
    return deleted > 0


def agregar_memorias(nombre, texto_memorias):
    """Agrega memorias nuevas al agente sin duplicar las existentes."""
    agente = Agente.objects.filter(nombre=nombre.strip().lower()).first()
    if not agente:
        return []

    lineas_existentes = {
        linea.strip().lower()
        for linea in agente.memoria.splitlines()
        if linea.strip()
    }

    nuevas = []
    for linea in texto_memorias.strip().splitlines():
        linea_limpia = linea.strip()
        if not linea_limpia:
            continue
        if linea_limpia.lower() not in lineas_existentes:
            if not linea_limpia.startswith("- "):
                linea_limpia = f"- {linea_limpia}"
            nuevas.append(linea_limpia)
            lineas_existentes.add(linea_limpia.lower())

    if nuevas:
        actual = agente.memoria.strip()
        agente.memoria = f"{actual}\n" + "\n".join(nuevas) if actual else "\n".join(nuevas)
        agente.save(update_fields=["memoria"])

    return nuevas
