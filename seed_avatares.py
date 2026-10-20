"""Asigna los retratos generados a los agentes existentes sin modificar sus perfiles.

Ejecutar desde el proyecto: python seed_avatares.py
El manifiesto conserva también los prompts usados para generar cada imagen.
"""

import json
from pathlib import Path

import basededatos as bd


def main():
    raiz = Path(__file__).resolve().parent
    carpeta = raiz / "static" / "avatars" / "generated"
    manifiesto = json.loads((carpeta / "manifest.json").read_text(encoding="utf-8"))
    bd.BASE_DATOS = str(raiz / "agentes.db")
    bd.inicializar()
    actualizados = 0
    for imagen in manifiesto["imagenes"]:
        nombre = imagen["agente"]
        archivo = imagen["archivo"]
        if Path(archivo).name != archivo or not (carpeta / archivo).is_file():
            raise ValueError(f"Archivo de avatar inválido o inexistente: {archivo}")
        if bd.existe_agente(nombre):
            bd.actualizar_avatar(nombre, f"/static/avatars/generated/{archivo}")
            actualizados += 1
    print(f"Avatares asignados: {actualizados}")


if __name__ == "__main__":
    main()
