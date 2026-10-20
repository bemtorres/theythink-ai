"""Seeder de los dieciséis perfiles de Music Pro: empleados y clientes.

Uso:
    python musicpro.py          # crea los perfiles que faltan
    python musicpro.py --force  # también actualiza los perfiles existentes

Conserva los demás agentes, las memorias y las conversaciones.
"""

import argparse

from empresa import PERFILES_EMPRESA, crear_perfiles


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Actualiza perfil, conocimiento e identidad de los agentes de Music Pro existentes.",
    )
    args = parser.parse_args()
    creados, actualizados = crear_perfiles(forzar=args.force)

    print("Seeder Music Pro")
    for titulo, nombres in (("Creados", creados), ("Actualizados", actualizados)):
        print(f"{titulo}: {len(nombres)}")
        for nombre in nombres:
            print(f"  - {nombre}")
    print(f"Sin cambios: {len(PERFILES_EMPRESA) - len(creados) - len(actualizados)}")
    print("Grupo MusicPro: bodega, tienda, tarjetas y transporte; cada área tiene jefe, trabajador y dos clientes.")


if __name__ == "__main__":
    main()
