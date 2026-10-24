"""Comando de Django para poblar los 16 perfiles de Music Pro (empleados y clientes).

Uso:
    python manage.py seed_musicpro
    python manage.py seed_musicpro --force
"""

from django.core.management.base import BaseCommand
from agentes.seeders import PERFILES_EMPRESA, seed_musicpro as crear_perfiles


class Command(BaseCommand):
    help = "Puebla o actualiza los dieciséis perfiles de Music Pro (empleados y clientes)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Actualiza perfil, conocimiento e identidad de los agentes existentes de Music Pro.",
        )

    def handle(self, *args, **options):
        force = options.get("force", False)
        self.stdout.write(self.style.NOTICE("Iniciando Seeder de Music Pro..."))

        creados, actualizados = crear_perfiles(forzar=force)

        self.stdout.write(self.style.SUCCESS(f"Perfiles creados: {len(creados)}"))
        for nombre in creados:
            self.stdout.write(f"  + {nombre}")

        self.stdout.write(self.style.SUCCESS(f"Perfiles actualizados: {len(actualizados)}"))
        for nombre in actualizados:
            self.stdout.write(f"  ~ {nombre}")

        sin_cambios = len(PERFILES_EMPRESA) - len(creados) - len(actualizados)
        self.stdout.write(f"Sin cambios: {sin_cambios}")
        self.stdout.write(
            self.style.SUCCESS(
                "Grupo MusicPro listo: bodega, tienda, tarjetas y transporte (jefe, trabajador y dos clientes por área)."
            )
        )
