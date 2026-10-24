"""Lógica de presentación del catálogo: datos públicos sin memorias ni historiales."""

import json
import re
from pathlib import Path

_metadata_file = Path(__file__).with_name("catalogo_metadata.json")
METADATA = json.loads(_metadata_file.read_text(encoding="utf-8")) if _metadata_file.is_file() else {}


def seccion(perfil, etiqueta):
    """Extrae el texto bajo una etiqueta de sección en el texto del perfil."""
    patron = r"(?:^|\n)" + re.escape(etiqueta) + r":\s*\n(.+?)(?=\n\s*\n|\Z)"
    resultado = re.search(patron, perfil or "", re.S)
    return resultado.group(1).strip() if resultado else ""


def presentar_agentes(filas, grupos):
    """Transforma los registros de agentes de la base de datos en modelos de presentación públicos."""
    membresias = {}
    for grupo in grupos:
        for nombre in grupo.get("agentes", []):
            membresias.setdefault(nombre, []).append(grupo["id"])
    nombres_grupos = {g["id"]: g["nombre"] for g in grupos}
    agentes = []
    for fila in filas:
        clave, perfil = fila["nombre"], fila["perfil"]
        meta = METADATA.get(clave, {})
        ids = membresias.get(clave, [])
        nombre = seccion(perfil, "NOMBRE").splitlines()
        nombre = nombre[0] if nombre else clave.replace("_", " ").title()
        descripcion = (
            seccion(perfil, "EXPERIENCIA SIMULADA")
            or seccion(perfil, "DESCRIPCIÓN")
            or meta.get("description")
            or seccion(perfil, "PERSONALIDAD")
            or "Una nueva perspectiva para tu próxima conversación."
        )
        agentes.append({
            "id": clave,
            "name": meta.get("display_name") or nombre,
            "role": meta.get("role") or seccion(perfil, "PROFESIÓN") or seccion(perfil, "PROFESION") or "Personaje de IA",
            "description": descripcion,
            "avatar": fila.get("avatar_url") or "",
            "groups": ids,
            "group": " · ".join(nombres_grupos[g] for g in ids),
            "category": meta.get("category", "personajes"),
            "starters": meta.get("starters", ["¿Cómo te presentarías?", "¿Qué temas te interesan?", "Cuéntame tu perspectiva."]),
        })
    destacados = [
        "el_principito", "tienda_jefe", "sherlock_holmes", "cliente_bodega_feliz",
        "socrates", "bodega_trabajador", "nikola_tesla", "cliente_tienda_problemas",
    ]
    agentes.sort(key=lambda a: (destacados.index(a["id"]) if a["id"] in destacados else len(destacados), a["name"]))
    return agentes
