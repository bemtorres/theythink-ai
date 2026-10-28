"""Seeder único. Catálogo: personas.py.

python seed.py          agrega personas faltantes sin sobrescribir existentes
python seed.py --update actualiza perfiles conservando chats y memoria
python seed.py --force  elimina datos de agentes y carga todo desde cero
"""

import basededatos as bd
from personas import PERSONAS, BASES_CONOCIMIENTO_EJEMPLO


# ----------------------------------------------------------------------
# Conversaciones de ejemplo (se agregan a agentes sin historial).
# ----------------------------------------------------------------------

CONVERSACIONES_EJEMPLO = [
    ("user", "Hola, ¿quién eres y a qué te dedicas?"),
    (
        "assistant",
        "Hola, soy un agente personal creado con DeepSeek. Puedo ayudarte "
        "a resolver dudas, explicarte conceptos paso a paso o simplemente "
        "conversar contigo. Dime, ¿qué te gustaría saber?",
    ),
    ("user", "¿Qué tecnologías o conocimientos tienes?"),
    (
        "assistant",
        "Conozco los temas de las bases de conocimiento que tengo asociadas. "
        "Pregúntame por ellos y te responderé con gusto.",
    ),
]


# ----------------------------------------------------------------------
# Creación de ejemplos y conversaciones
# ----------------------------------------------------------------------


CONVERSACIONES_PERSONAJES = {
    "el_principito": [
        ("user", "¡Hola Principito! ¿De dónde vienes y qué es lo más importante en la vida?"),
        (
            "assistant",
            "¡Hola! Vengo de mi pequeño asteroide B-612, donde tengo tres volcanes y una rosa única en el mundo. Las personas mayores a menudo se confunden con números y cosas extrañas, pero mi amigo el Zorro me enseñó el verdadero secreto: solo con el corazón se puede ver bien; lo esencial es invisible para los ojos. ¿Has mirado hoy las estrellas?",
        ),
    ],
    "sherlock_holmes": [
        ("user", "Buenos días, señor Holmes. ¿Cómo funciona su método deductivo?"),
        (
            "assistant",
            "Elemental. La mayoría de los hombres ven, pero no observan; la distinción es evidente. La ciencia de la deducción consiste en advertir los detalles que escapan a los demás: la ceniza de un cigarro, las huellas de barro o el desgaste en una manga. Cuando se elimina lo imposible, lo que queda, por improbable que parezca, debe ser la verdad. Dígame, ¿qué enigma le trae a Baker Street?",
        ),
    ],
    "don_quijote": [
        ("user", "Saludos, caballero. ¿Cuál es su sagrada misión en este mundo?"),
        (
            "assistant",
            "¡Sépase, noble amigo, que soy Don Quijote de la Mancha, desfacedor de tuertos y amparo de los menesterosos! Por la libertad y por la honra, así como por mi sin par señora Dulcinea del Toboso, se puede y debe aventurar la vida. Aunque los viles encantadores muden los gigantes en molinos de viento, jamás desmayará este brazo en defender la justicia y la virtud.",
        ),
    ],
    "socrates": [
        ("user", "Hola Sócrates. ¿Qué significa conocerse a uno mismo?"),
        (
            "assistant",
            "Salud, amigo mío. Conocerse a uno mismo es reconocer ante todo los límites del propio saber: solo sé que nada sé. Quien cree saber lo que ignora vive prisionero de una ilusión. ¿Acaso no es más valioso examinar nuestra alma y buscar la virtud cada día antes que perseguir las riquezas y la vana fama?",
        ),
    ],
    "nikola_tesla": [
        ("user", "Maestro Tesla, ¿cuál es el secreto del universo y de sus inventos?"),
        (
            "assistant",
            "Si quieres descubrir los secretos del universo, piensa en términos de energía, frecuencia y vibración. Todo lo que he creado —desde la corriente alterna polifásica y el motor de inducción hasta la bobina de alta tensión— nació primero en mi mente, funcionando a la perfección antes de tocar la materia. El presente es de ellos; el futuro, para el que realmente he trabajado, es de la humanidad entera.",
        ),
    ],
    "hincha_colocolo": [
        ("user", "¡Wena compa! ¿Por qué Colo-Colo es el equipo más grande de Chile?"),
        (
            "assistant",
            "¡Aguante el Cacique, hermano! Colo-Colo es Chile entero. Fundado en 1925 por el gran David Arellano en el bar Quitapenas, somos el Eterno Campeón con más de 33 estrellas y el único club chileno que tiene la Copa Libertadores de América ganada en la Ruca en 1991 con don Mirko Jozic. De Caszely y Chamaco hasta Barti, Matías y Esteban Paredes, ¡la historia alba se respeta siempre!",
        ),
    ],
    "hincha_udechile": [
        ("user", "¡Hola bullanguero! ¿Qué significa la mística de la Universidad de Chile?"),
        (
            "assistant",
            "¡Vamos la U, toda la vida! La mística azul no se compra con nada: es un sentimiento que se lleva en la sangre, alentando en las buenas y en las malas sin abandonar jamás. Desde el glorioso Ballet Azul de don Leonel Sánchez y el título heroico del 94 con el Matador Marcelo Salas, hasta la Copa Sudamericana 2011 invicta de don Jorge Sampaoli y Edu Vargas. ¡La Gloriosa U es alegría pura!",
        ),
    ],
    "el_flaite_chileno": [
        ("user", "Wena hermano, ¿cómo estai? Tírame la pulenta de cómo se vive el corte fino en la pobla."),
        (
            "assistant",
            "¡Wena compita, qué pasa! Aquí andamo' de pana po wacho, siempre a lo vío y con la chispeza al cien. En la pobla se vive con respeto y lealtad: zapatillas Jordan impecables, su corte en degrade fino, escuchando al Pablo Chill-E o al Cris Mj a todo chancho y compartiendo unos buenos tocomples con los cabros. Yo no le compro a los perkines, pero a los míos los banco a morir. ¿Qué querí' saber, hermano?",
        ),
    ],
}


def sembrar_conversaciones():
    """Agrega una conversación de ejemplo a los agentes sin historial.

    Devuelve la lista de nombres que recibieron una conversación.
    """
    sembrados = []
    for nombre in bd.listar_agentes():
        if bd.obtener_historial(nombre, cantidad=1):
            continue
        persona = next((p for p in PERSONAS if p['nombre'] == nombre), {})
        mensajes = persona.get('conversacion_ejemplo') or CONVERSACIONES_PERSONAJES.get(nombre, CONVERSACIONES_EJEMPLO)
        for rol, mensaje in mensajes:
            bd.guardar_mensaje(nombre, rol, mensaje)
        sembrados.append(nombre)
    return sembrados


# ----------------------------------------------------------------------
# Punto de entrada
# ----------------------------------------------------------------------


def sembrar_personas(personas=None, actualizar=False):
    """Carga faltantes; actualizar=True restaura perfiles sin borrar chats."""
    bd.inicializar()
    creados, actualizados = [], []
    bases = {b["nombre"]: b["contenido"] for b in BASES_CONOCIMIENTO_EJEMPLO}
    for persona in PERSONAS if personas is None else personas:
        nombre = persona["nombre"]
        existe = bd.existe_agente(nombre)
        if existe and not actualizar:
            continue
        fuentes = {}
        for base in persona.get("bases", []):
            fuentes[base] = bases[base]
        if persona.get("fuente_nombre"):
            fuentes[persona["fuente_nombre"]] = persona["fuente_contenido"]
        if persona.get("conocimiento"):
            fuentes["Music Pro - " + nombre.split("_")[0]] = persona["conocimiento"]
        ids = []
        for titulo, contenido in fuentes.items():
            fuente = bd.obtener_fuente_por_nombre(titulo)
            if fuente:
                fuente_id = fuente["id"]
                if actualizar:
                    bd.actualizar_fuente(fuente_id, titulo, contenido)
            else:
                fuente_id = bd.crear_fuente(titulo, contenido)
            ids.append(fuente_id)
        if not existe:
            bd.crear_agente(
                nombre=nombre, perfil=persona["perfil"],
                identidad_clave=persona.get("identidad_clave", ""),
                identidad_custom=persona.get("identidad_custom", ""),
                avatar_url=persona.get("avatar_url", ""), fuentes_ids=ids,
            )
            creados.append(nombre)
        else:
            bd.actualizar_perfil(nombre, persona["perfil"])
            bd.cambiar_identidad(nombre, clave=persona.get("identidad_clave", ""),
                                custom=persona.get("identidad_custom", ""))
            bd.actualizar_avatar(nombre, persona.get("avatar_url", ""))
            bd.actualizar_conocimiento(nombre, "")
            bd.establecer_fuentes_agente(nombre, ids)
            actualizados.append(nombre)
    return creados, actualizados


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Seeder único de personas y conversaciones.")
    parser.add_argument("--force", action="store_true",
                        help="Vacía agentes, fuentes y chats antes de cargar el catálogo completo.")
    parser.add_argument("--update", action="store_true",
                        help="Actualiza perfiles del catálogo conservando conversaciones y memoria.")
    args = parser.parse_args()
    bd.inicializar()
    if args.force:
        bd.vaciar()
    creados, actualizados = sembrar_personas(actualizar=args.update)
    sembrados = sembrar_conversaciones()
    print(f"Personas creadas: {len(creados)}; actualizadas: {len(actualizados)}.")
    print(f"Conversaciones de ejemplo agregadas: {len(sembrados)}.")
    print(f"Base de datos lista: {bd.BASE_DATOS} ({len(bd.listar_agentes())} personas).")


if __name__ == "__main__":
    main()
