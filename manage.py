#!/usr/bin/env python
"""Utilidad de línea de comandos de Django para tareas administrativas."""
import os
import sys


def main():
    """Ejecuta tareas administrativas."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "theythink.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. Asegúrate de que esté instalado y "
            "disponible en tu variable de entorno PYTHONPATH."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
