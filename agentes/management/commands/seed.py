"""Comando de Django para poblar la base de datos con agentes, roles y conocimiento inicial.

Uso:
    python manage.py seed
    python manage.py seed --force
"""

from django.core.management.base import BaseCommand
from agentes.seeders import seed_all, seed_avatars, seed_musicpro
from agentes.services import listar_agentes


class Command(BaseCommand):
    help = "Puebla la base de datos con agentes, roles, bases de conocimiento y conversaciones iniciales."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Vacía la base de datos y vuelve a sembrar todos los agentes y perfiles.",
        )

    def handle(self, *args, **options):
        forzar = options.get("force", False)

        existentes = listar_agentes()
        if existentes and not forzar:
            self.stdout.write(
                f"La base de datos ya contiene {len(existentes)} agente(s). "
                "Usa 'python manage.py seed --force' si deseas reiniciar todo."
            )
            seed_musicpro(forzar=False)
            seed_avatars()
            return

        if forzar:
            self.stdout.write(self.style.WARNING("Vaciando base de datos y re-sembrando todo (--force)..."))

        res = seed_all(forzar=forzar)
        self.stdout.write(
            self.style.SUCCESS(
                f"Base de datos completamente sembrada y lista: {res['total_agentes']} agentes disponibles, "
                f"{res['avatares_asignados']} avatares asignados."
            )
        )
