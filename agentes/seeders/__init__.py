"""Paquete de Seeders y datos iniciales para la base de datos."""

from .data_ejemplos import (
    AGENTES_EJEMPLO,
    BASES_CONOCIMIENTO_EJEMPLO,
    CONVERSACIONES_EJEMPLO,
    CONVERSACIONES_PERSONAJES,
)
from .data_musicpro import PERFILES_EMPRESA
from .data_personajes import PERSONAJES_CANONICOS
from .data_roles import IDENTIDADES
from .seeder_runner import (
    crear_perfiles,
    seed_admin,
    seed_all,
    seed_avatars,
    seed_characters,
    seed_conversations,
    seed_examples,
    seed_musicpro,
    seed_roles,
)

__all__ = [
    "IDENTIDADES",
    "PERFILES_EMPRESA",
    "PERSONAJES_CANONICOS",
    "AGENTES_EJEMPLO",
    "BASES_CONOCIMIENTO_EJEMPLO",
    "CONVERSACIONES_EJEMPLO",
    "CONVERSACIONES_PERSONAJES",
    "seed_admin",
    "seed_roles",
    "seed_characters",
    "seed_examples",
    "seed_musicpro",
    "crear_perfiles",
    "seed_avatars",
    "seed_conversations",
    "seed_all",
]
