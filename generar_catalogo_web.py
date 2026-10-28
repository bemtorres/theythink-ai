"""Exporta el catálogo público de index.html desde la misma fuente del seeder.

Ejecutar al modificar personas.py: python generar_catalogo_web.py
El archivo generado se distribuye con el proyecto; los estudiantes no lo generan.
"""
import json
from pathlib import Path

from personas import EXPERIENCIAS_MUSIC_PRO, PERSONAS, PROYECTOS_MUSIC_PRO


def secciones(perfil):
    resultado, clave = {}, None
    for linea in perfil.splitlines():
        if linea.endswith(":") and linea.isupper():
            clave = linea[:-1]
            resultado[clave] = []
        elif clave and linea.strip():
            resultado[clave].append(linea)
    return {clave: "\n".join(lineas) for clave, lineas in resultado.items()}


def construir_catalogo():
    catalogo = []
    for persona in PERSONAS:
        identificador = persona["nombre"]
        campos = secciones(persona["perfil"])
        nombre = campos.get("NOMBRE", identificador)
        proyecto = next((p for p in PROYECTOS_MUSIC_PRO
                         if identificador.startswith(p["area"] + "_")), None)
        experiencia = next((e for e in EXPERIENCIAS_MUSIC_PRO
                            if e["nombre"] == nombre), None)
        profesion = campos.get("PROFESIÓN", campos.get("PROFESION",
                    campos.get("PROFESIÓN O PUESTO", campos.get("CONDICIÓN", nombre))))
        categoria = "music_pro" if proyecto else (
            "ciencia" if identificador in {"benjamin", "elon_musk", "albert_einstein", "nikola_tesla"}
            else "cultura" if identificador in {"hincha_colocolo", "hincha_udechile", "el_flaite_chileno"}
            else "filosofia")
        rol = ("Cliente" if "_cliente_" in identificador else
               "Trabajador entusiasta" if identificador.endswith("_contento") else
               "Jefe" if identificador.endswith("_jefe") else
               "Trabajador agotado" if proyecto else "Personaje")
        bases = persona.get("bases", [persona["fuente_nombre"]] if persona.get("fuente_nombre") else [])
        respuestas = {}
        if proyecto:
            bases = [proyecto["titulo"], rol]
            respuestas = {
                "problema": experiencia["experiencia"] if experiencia else proyecto["problemas"],
                "experiencia": experiencia["experiencia"] if experiencia else proyecto["ejemplo"],
                "mejor": experiencia["mejora"] if experiencia else proyecto["mejoras"],
                "validar": experiencia["validacion"] if experiencia else proyecto["criterios"],
            }
            if rol == "Jefe":
                respuestas["presupuesto"] = campos["PRESUPUESTO APROBADO DEL ESCENARIO"]
            saludo = (f"Soy {nombre}, {profesion}. "
                      + (experiencia["valora"] if experiencia else proyecto["ejemplo"]))
        else:
            saludo = f"Soy {nombre}. Puedes revisar mi perfil y mis temas en esta demostración."
        respuestas["default"] = (
            "Esta vista usa respuestas de ejemplo. Revisa mi ficha o prueba las preguntas sugeridas; "
            "para una entrevista abierta con DeepSeek, instala el proyecto e inicia sesión en la aplicación local."
        )
        catalogo.append({
            "id": identificador, "nombre": nombre, "persona": profesion,
            "categoria": categoria, "proyecto": proyecto["area"] if proyecto else None,
            "iniciales": "".join(p[0] for p in nombre.split()[:2]),
            "avatar_url": persona["avatar_url"].lstrip("/"),
            "avatar_color": "from-[#1a73e8] to-[#34a853]" if proyecto else "from-[#1a73e8] to-[#a142f4]",
            "rol_nombre": rol, "bases": bases, "perfil": persona["perfil"],
            "resumen": profesion, "estilo": persona.get("identidad_custom") or campos.get("FORMA DE COMUNICARSE", "Según su perfil."),
            "memorias": [], "saludo": saludo,
            "sugerencias": (["¿Cuál es tu presupuesto?", "¿Qué te gustaría mejorar?", "¿Cómo validar las mejoras?"]
                            if rol == "Jefe" else
                            ["¿Cómo ha sido tu experiencia?", "¿Qué te gustaría mejorar?", "¿Cómo validar las mejoras?"]
                            if proyecto else ["¿Cuál es tu experiencia?", "¿Qué temas conoces?"]),
            "respuestas": respuestas,
        })
    return catalogo


def main():
    destino = Path(__file__).resolve().parent / "static/js/catalogo-personas.js"
    destino.write_text(
        "// Generado desde personas.py por generar_catalogo_web.py. No editar a mano.\n"
        + "window.CATALOGO_PERSONAS = " + json.dumps(construir_catalogo(), ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    print(f"Catálogo web exportado: {len(PERSONAS)} personas.")


if __name__ == "__main__":
    main()
