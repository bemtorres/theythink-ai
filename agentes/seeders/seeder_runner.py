"""Ejecutores de Seeders para poblar datos iniciales en la base de datos con Django ORM."""

import json
from pathlib import Path
from django.conf import settings

from agentes.models import Agente, FuenteConocimiento, Grupo, Rol, Usuario
from agentes.services import (
    actualizar_avatar,
    actualizar_conocimiento,
    actualizar_fuente,
    actualizar_perfil,
    asignar_grupo,
    avatar_local,
    cambiar_identidad,
    crear_agente,
    crear_fuente,
    crear_grupo,
    crear_rol,
    existe_agente,
    guardar_mensaje,
    inicializar_admin_por_defecto,
    listar_agentes,
    obtener_fuente_por_nombre,
    obtener_grupo_por_nombre,
    obtener_historial,
    obtener_rol_por_clave,
    vaciar,
)
from .data_ejemplos import (
    AGENTES_EJEMPLO,
    BASES_CONOCIMIENTO_EJEMPLO,
    CONVERSACIONES_EJEMPLO,
    CONVERSACIONES_PERSONAJES,
)
from .data_musicpro import PERFILES_EMPRESA
from .data_personajes import PERSONAJES_CANONICOS
from .data_roles import IDENTIDADES


def seed_admin():
    """Siembra el usuario administrador inicial."""
    inicializar_admin_por_defecto()


def seed_roles():
    """Siembra todos los roles canónicos de sistema a partir de IDENTIDADES."""
    creados = 0
    for clave, datos in IDENTIDADES.items():
        if not obtener_rol_por_clave(clave):
            crear_rol(
                clave=clave,
                nombre=datos["name"],
                descripcion=datos.get("description", ""),
                prompt=datos.get("prompt", ""),
                es_sistema=True,
            )
            creados += 1
    return creados


def seed_characters():
    """Siembra los personajes canónicos (literarios e históricos)."""
    creados = []
    for p in PERSONAJES_CANONICOS:
        nombre = p["nombre"]
        f_existente = obtener_fuente_por_nombre(p["fuente_nombre"])
        if not f_existente:
            f_id = crear_fuente(p["fuente_nombre"], p["fuente_contenido"])
        else:
            f_id = f_existente["id"]

        if not existe_agente(nombre):
            avatar = avatar_local(nombre) or p.get("avatar_url", "")
            crear_agente(
                nombre=nombre,
                perfil=p["perfil"],
                identidad_clave=p.get("identidad_clave", ""),
                avatar_url=avatar,
                fuentes_ids=[f_id] if f_id else [],
            )
            creados.append(nombre)
        else:
            ag = Agente.objects.filter(nombre=nombre).first()
            if ag and not ag.avatar_url:
                local_av = avatar_local(nombre)
                if local_av:
                    ag.avatar_url = local_av
                    ag.save(update_fields=["avatar_url"])
    return creados


def seed_examples():
    """Siembra las bases de conocimiento y agentes de ejemplo base."""
    base_map = {}
    for base in BASES_CONOCIMIENTO_EJEMPLO:
        try:
            fuente_id = crear_fuente(base["nombre"], base["contenido"])
            base_map[base["nombre"]] = fuente_id
        except ValueError:
            f = obtener_fuente_por_nombre(base["nombre"])
            if f:
                base_map[base["nombre"]] = f["id"]

    creados = []
    for ejemplo in AGENTES_EJEMPLO:
        nombre = ejemplo["nombre"]
        if not existe_agente(nombre):
            fuentes_ids = [
                base_map[b_nom] for b_nom in ejemplo.get("bases", []) if b_nom in base_map
            ]
            crear_agente(
                nombre=nombre,
                perfil=ejemplo["perfil"],
                identidad_clave=ejemplo.get("identidad_clave", ""),
                identidad_custom=ejemplo.get("identidad_custom", ""),
                fuentes_ids=fuentes_ids,
            )
            creados.append(nombre)
    return creados


def seed_musicpro(forzar=False):
    """Siembra o actualiza los 16 perfiles de la empresa Music Pro y los asocia a su grupo."""
    grupo = obtener_grupo_por_nombre("MusicPro")
    grupo_id = grupo["id"] if grupo else crear_grupo("MusicPro")

    creados = []
    actualizados = []
    for perfil in PERFILES_EMPRESA:
        nombre = perfil["nombre"]
        contenido = perfil.get("conocimiento", "")
        if not existe_agente(nombre):
            crear_agente(
                nombre=nombre,
                perfil=perfil["perfil"],
                conocimiento=contenido,
                identidad_clave=perfil.get("identidad_clave", ""),
                identidad_custom=perfil.get("identidad_custom", ""),
            )
            creados.append(nombre)
        elif forzar:
            actualizar_perfil(nombre, perfil["perfil"])
            actualizar_conocimiento(nombre, contenido)
            cambiar_identidad(
                nombre,
                clave=perfil.get("identidad_clave", ""),
                custom=perfil.get("identidad_custom", ""),
            )
            fuente = obtener_fuente_por_nombre(nombre)
            if fuente:
                actualizar_fuente(fuente["id"], nombre, contenido)
            actualizados.append(nombre)
        asignar_grupo(nombre, grupo_id)

    # Asegura personajes literarios e históricos si no existiesen
    seed_characters()
    return creados, actualizados


# Alias para compatibilidad con código existente
crear_perfiles = seed_musicpro


def seed_avatars():
    """Asigna los avatares generados desde el manifiesto de avatares a los agentes."""
    raiz = settings.BASE_DIR
    carpeta = raiz / "agentes" / "static" / "avatars" / "generated"
    if not (carpeta / "manifest.json").is_file():
        carpeta = raiz / "static" / "avatars" / "generated"
    manifiesto_path = carpeta / "manifest.json"

    if not manifiesto_path.is_file():
        return 0

    manifiesto = json.loads(manifiesto_path.read_text(encoding="utf-8"))
    actualizados = 0
    for imagen in manifiesto.get("imagenes", []):
        nombre = imagen["agente"]
        archivo = imagen["archivo"]
        archivo_path = carpeta / archivo

        if not archivo_path.is_file():
            continue

        if existe_agente(nombre):
            actualizar_avatar(nombre, f"/static/avatars/generated/{archivo}")
            actualizados += 1

    return actualizados


def seed_conversations():
    """Siembra conversaciones iniciales para los agentes que no tengan historial."""
    sembrados = []
    for nombre in listar_agentes():
        if obtener_historial(nombre, cantidad=1):
            continue
        mensajes = CONVERSACIONES_PERSONAJES.get(nombre, CONVERSACIONES_EJEMPLO)
        for rol, mensaje in mensajes:
            guardar_mensaje(nombre, rol, mensaje)
        sembrados.append(nombre)
    return sembrados


def seed_all(forzar=False):
    """Ejecuta todos los seeders en orden respetando dependencias."""
    if forzar:
        vaciar()

    seed_admin()
    seed_roles()
    seed_examples()
    seed_characters()
    creados_mp, act_mp = seed_musicpro(forzar=forzar)
    act_av = seed_avatars()
    sembrados_conv = seed_conversations()

    return {
        "agentes_musicpro_creados": len(creados_mp),
        "agentes_musicpro_actualizados": len(act_mp),
        "avatares_asignados": act_av,
        "conversaciones_sembradas": len(sembrados_conv),
        "total_agentes": len(listar_agentes()),
    }
