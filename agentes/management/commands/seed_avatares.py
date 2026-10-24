"""Comando de Django para asignar los retratos generados a los agentes existentes."""

from django.core.management.base import BaseCommand
from agentes.seeders import seed_avatars


class Command(BaseCommand):
    help = "Asigna los retratos generados a los agentes existentes a partir del manifiesto de avatares."

    def handle(self, *args, **options):
        actualizados = seed_avatars()
        self.stdout.write(self.style.SUCCESS(f"Avatares generados asignados exitosamente: {actualizados}"))
