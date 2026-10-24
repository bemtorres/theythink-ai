"""Módulo de utilidades y lógica de dominio de la plataforma."""

from .catalog import METADATA, presentar_agentes, seccion
from .prompt import (
    construir_prompt_memoria,
    construir_system_prompt,
    procesar_identidad,
)

__all__ = [
    "METADATA",
    "presentar_agentes",
    "seccion",
    "construir_prompt_memoria",
    "construir_system_prompt",
    "procesar_identidad",
]
