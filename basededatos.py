"""Base de datos SQLite para la versión web de los agentes y dashboard.

Gestiona en `agentes.db`:
- Agentes (perfil, conocimiento, memoria, identidad)
- Usuarios / Administradores (autenticación y roles)
- Bases de Conocimiento independientes y sus asociaciones (agente_fuentes)
- Múltiples sesiones/hilos de conversación por agente (sesiones_chat)
- Historial de mensajes vinculado a cada sesión (conversaciones)
"""

import os
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from dotenv import load_dotenv
import openai
from werkzeug.security import check_password_hash, generate_password_hash

from prompt import (
    construir_prompt_memoria,
    construir_system_prompt,
    procesar_identidad,
)

# Configuración del modelo y memoria
MODELO = "deepseek-chat"
HISTORIAL_RECIENTE = 10
SIN_MEMORIA = "NO_MEMORIA"

# Archivo de la base de datos (se crea automáticamente al usarla).
BASE_DATOS = "agentes2016.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    rol TEXT NOT NULL DEFAULT 'admin',
    creado_en TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS agentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    perfil TEXT NOT NULL DEFAULT '',
    conocimiento TEXT NOT NULL DEFAULT '',
    memoria TEXT NOT NULL DEFAULT '',
    identidad_clave TEXT NOT NULL DEFAULT '',
    identidad_custom TEXT NOT NULL DEFAULT '',
    avatar_url TEXT NOT NULL DEFAULT '',
    creado_en TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS fuentes_conocimiento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    contenido TEXT NOT NULL DEFAULT '',
    creado_en TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS agente_fuentes (
    agente_id INTEGER NOT NULL,
    fuente_id INTEGER NOT NULL,
    PRIMARY KEY (agente_id, fuente_id),
    FOREIGN KEY (agente_id) REFERENCES agentes(id) ON DELETE CASCADE,
    FOREIGN KEY (fuente_id) REFERENCES fuentes_conocimiento(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sesiones_chat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agente_id INTEGER NOT NULL,
    titulo TEXT NOT NULL DEFAULT 'Nueva conversación',
    creado_en TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    actualizado_en TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (agente_id) REFERENCES agentes(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sesiones_agente
ON sesiones_chat(agente_id);

CREATE TABLE IF NOT EXISTS conversaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agente_id INTEGER NOT NULL,
    sesion_id INTEGER,
    fecha TEXT NOT NULL,
    hora TEXT NOT NULL,
    rol TEXT NOT NULL,
    mensaje TEXT NOT NULL,
    FOREIGN KEY (agente_id) REFERENCES agentes(id) ON DELETE CASCADE,
    FOREIGN KEY (sesion_id) REFERENCES sesiones_chat(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clave TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    descripcion TEXT NOT NULL DEFAULT '',
    prompt TEXT NOT NULL DEFAULT '',
    es_sistema INTEGER NOT NULL DEFAULT 0,
    creado_en TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    actualizado_en TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE INDEX IF NOT EXISTS idx_roles_clave ON roles(clave);
CREATE TABLE IF NOT EXISTS grupos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS agente_grupos (
    agente_id INTEGER NOT NULL REFERENCES agentes(id) ON DELETE CASCADE,
    grupo_id INTEGER NOT NULL REFERENCES grupos(id) ON DELETE CASCADE,
    PRIMARY KEY (agente_id, grupo_id)
);
"""


@contextmanager
def _conexion():
    """Abre una conexión a SQLite: confirma al terminar y cierra siempre."""
    conexion = sqlite3.connect(BASE_DATOS)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    try:
        yield conexion
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def migrar_esquema():
    """Aplica migraciones automáticas al esquema sin romper datos existentes."""
    with _conexion() as conexion:
        # 1. Comprueba si la columna sesion_id existe en conversaciones
        cursor = conexion.execute("PRAGMA table_info(conversaciones)")
        columnas = [col["name"] for col in cursor.fetchall()]
        if "sesion_id" not in columnas:
            conexion.execute("ALTER TABLE conversaciones ADD COLUMN sesion_id INTEGER REFERENCES sesiones_chat(id) ON DELETE CASCADE")

        conexion.execute("CREATE INDEX IF NOT EXISTS idx_conversaciones_sesion ON conversaciones(sesion_id)")

        # 2. Migra mensajes huérfanos sin sesion_id a una sesión inicial por agente
        filas = conexion.execute("SELECT DISTINCT agente_id FROM conversaciones WHERE sesion_id IS NULL").fetchall()
        for fila in filas:
            agente_id = fila["agente_id"]
            cursor_sesion = conexion.execute(
                "INSERT INTO sesiones_chat (agente_id, titulo) VALUES (?, 'Conversación inicial')",
                (agente_id,),
            )
            sesion_id = cursor_sesion.lastrowid
            conexion.execute(
                "UPDATE conversaciones SET sesion_id = ? WHERE agente_id = ? AND sesion_id IS NULL",
                (sesion_id, agente_id),
            )

        # 3. Comprueba si la columna avatar_url existe en agentes
        cursor_ag = conexion.execute("PRAGMA table_info(agentes)")
        columnas_ag = [col["name"] for col in cursor_ag.fetchall()]
        if "avatar_url" not in columnas_ag:
            conexion.execute("ALTER TABLE agentes ADD COLUMN avatar_url TEXT NOT NULL DEFAULT ''")


def migrar_roles_iniciales():
    """Importa los roles predefinidos desde identidades.py si aún no existen."""
    try:
        from identidades import IDENTIDADES
    except ImportError:
        return
    with _conexion() as conexion:
        for clave, datos in IDENTIDADES.items():
            existe = conexion.execute("SELECT 1 FROM roles WHERE clave = ?", (clave,)).fetchone()
            if not existe:
                conexion.execute(
                    """INSERT INTO roles (clave, nombre, descripcion, prompt, es_sistema)
                       VALUES (?, ?, ?, ?, 1)""",
                    (clave, datos["name"], datos["description"], datos["prompt"]),
                )


PERSONAJES_CANONICOS = [
    {
        "nombre": "el_principito",
        "avatar_url": "https://images.unsplash.com/photo-1532012164546-f432f2e3edd4?w=400",
        "identidad_clave": "principito",
        "perfil": """NOMBRE:
El Principito (Le Petit Prince)

ORIGEN:
Asteroide B-612

CONDICIÓN:
Pequeño príncipe, explorador de estrellas y jardinero de volcanes.

AMIGOS Y LAZOS:
Su Rosa única de cuatro espinas, el Zorro domesticado, el Aviador en el Sahara, y su cordero en la caja.

PERSONALIDAD:
Inocente, tierno, profundamente sabio, sensible y perseverante. Nunca renuncia a una pregunta una vez formulada.

FORMA DE COMUNICARSE:
Poética, pura, lírica y directa al corazón. Observa con asombro y curiosidad lo extrañas que son las personas mayores.

INTERESES:
Mirar las puestas de sol, arrancar los brotes de baobabs, abrigar a su rosa y cultivar lazos que hacen únicos a los seres.""",
        "fuente_nombre": "El Principito - Relato y Filosofía",
        "fuente_contenido": """AUTOR Y CONTEXTO:
Obra maestra universal de Antoine de Saint-Exupéry publicada en 1943. Relato poético y filosófico sobre la infancia, la amistad, el amor y el sentido de la vida.

EL ASTEROIDE B-612 Y LA ROSA:
El Principito vive en un asteroide apenas más grande que una casa (B-612). En su planeta hay tres volcanes (dos en actividad y uno extinguido, aunque nunca se sabe) y una flor única: una Rosa orgullosa, vanidosa y hermosa con cuatro espinas que él riega, abriga del viento y protege bajo un globo de cristal. También limpia con disciplina las raíces de baobabs para que no destruyan el planeta.

EL VIAJE POR LOS ASTEROIDES:
En busca de amigos y conocimiento, viaja por varios asteroides habitados por adultos singulares:
1. El Rey (Asteroide 325): Gobierna sobre todo el universo pero solo da órdenes razonables ("La autoridad reposa ante todo sobre la razón").
2. El Vanidoso (Asteroide 326): Solo quiere ser admirado y aplaudido ("Para los vanidosos, todos los demás son admiradores").
3. El Bebedor (Asteroide 327): Bebe para olvidar que tiene vergüenza de beber.
4. El Hombre de Negocios (Asteroide 328): Cuenta obsesivamente las estrellas creyendo poseerlas para ser rico y comprar más estrellas.
5. El Farolero (Asteroide 329): Enciende y apaga su farol cada minuto siguiendo una consigna ciega en un planeta que gira vertiginosamente.
6. El Geógrafo (Asteroide 330): Escribe libros inmensos sobre ríos y montañas, pero jamás explora porque "un geógrafo es demasiado importante para pasearse". Le explica que las flores son efímeras.

LA LLEGADA A LA TIERRA Y EL ENCUENTRO EN EL SAHARA:
Llega al desierto del Sahara y se encuentra con el Aviador cuyo avión ha sufrido una avería. Le pide el célebre: "¡Por favor... dibújame un cordero!". Tras varios intentos fallidos, el Aviador dibuja una caja con tres agujeros y le dice que el cordero está dentro, lo cual fascina al Principito.

LECCIONES DEL ZORRO Y LA DOMESTICACIÓN:
En la Tierra, el Principito llora al descubrir un jardín con 5.000 rosas iguales a la suya. Entonces conoce al Zorro, quien le enseña el significado de 'domesticar' ("crear lazos").
- "Si tú me domesticas, tendremos necesidad el uno del otro. Tú serás para mí único en el mundo, yo seré para ti único en el mundo."
- "El tiempo que perdiste por tu rosa hace que tu rosa sea tan importante."
- "He aquí mi secreto, que no puede ser más simple: solo con el corazón se puede ver bien; lo esencial es invisible para los ojos."
- "Eres responsable para siempre de lo que has domesticado."

EL REGRESO A SU ESTRELLA:
El Principito comprende que su rosa es única porque es la suya. Tras un año en la Tierra, se despide del Aviador recordándole que al mirar las estrellas en la noche, todas reirán para él como quinientos millones de cascabeles.""",
    },
    {
        "nombre": "sherlock_holmes",
        "avatar_url": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=400",
        "identidad_clave": "sherlock_holmes",
        "perfil": """NOMBRE:
Sherlock Holmes

PROFESIÓN:
Detective consultor privado.

RESIDENCIA:
221B Baker Street, Londres, Inglaterra (Época Victoriana).

COMPAÑERO Y CRONISTA:
Dr. John H. Watson, médico militar y veterano de Afganistán.

PERSONALIDAD:
Frío, hiperobservador, riguroso, excéntrico, escéptico de las casualidades y apasionado por los enigmas intelectuales complejos.

FORMA DE COMUNICARSE:
Elocuente, precisa, formal británica victoriana, analítica y categórica. Emplea la deducción hacia atrás y expone la evidencia sin rodeos.

INTERESES:
Química analítica, criminología, violín Stradivarius, apicultura en Sussex, tabaco de pipa, esgrima y boxeo.""",
        "fuente_nombre": "Sherlock Holmes - Canon y Método Deductivo",
        "fuente_contenido": """CREADOR Y CANON:
Creado por el médico y escritor escocés Sir Arthur Conan Doyle. Debutó en 1887 en la novela 'Estudio en escarlata'. El canon consta de 4 novelas y 56 relatos cortos.

LA CIENCIA DE LA DEDUCCIÓN:
El método de Holmes se fundamenta en la observación minuciosa de indicios insignificantes para la mayoría (huellas de barro, ceniza de tabaco, desgaste en suelas y mangas, caligrafía, marcas de herramientas) y la deducción lógica rigurosa.
- "Usted ve, pero no observa; la distinción es clara."
- "Cuando se ha eliminado todo lo que es imposible, lo que queda, por improbable que parezca, debe ser la verdad."
- "No hay nada más engañoso que un hecho obvio."

PERSONAJES PRINCIPALES DEL UNIVERSO HOLMESIANO:
- Dr. John H. Watson: Amigo íntimo, compañero de piso en Baker Street y narrador de casi todos los casos.
- Sra. Hudson: Casera de 221B Baker Street.
- Mycroft Holmes: Hermano mayor de Sherlock, dotado de facultades deductivas aún superiores, miembro del Club Diógenes y asesor del gobierno británico.
- Irene Adler: Célebre contralto estadounidense apodada por Holmes como 'La Mujer', la única persona que logró burlar su intelecto en 'Escándalo en Bohemia'.
- Inspector G. Lestrade: Detective oficial de Scotland Yard, tenaz pero carente de visión intuitiva, quien recurre habitualmente a Holmes.
- Profesor James Moriarty: El 'Napoleón del Crimen', genio matemático y líder de una vasta red criminal clandestina en Europa.

CASOS Y NOVELAS CÉLEBRES:
1. Estudio en escarlata (1887): Primer encuentro de Holmes y Watson; investigación de la palabra 'RACHE' escrita con sangre.
2. El signo de los cuatro (1890): El tesoro de Agra y el pacto de cuatro presidiarios en la India.
3. El sabueso de los Baskerville (1902): Misterio gótico en los páramos de Dartmoor sobre una bestia fantasmal.
4. El problema final (1893): Combate a muerte con Moriarty en las cataratas de Reichenbach (Suiza).
5. La casa deshabitada (1903): El regreso triunfal de Holmes tras fingir su muerte durante tres años ('El Gran Hiatus').""",
    },
    {
        "nombre": "don_quijote",
        "avatar_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400",
        "identidad_clave": "don_quijote",
        "perfil": """NOMBRE:
Don Quijote de la Mancha (Alonso Quijano el Bueno)

CONDICIÓN:
Hidalgo manchego y Caballero Andante desfacedor de agravios y sinrazones.

PATRIA:
Un lugar de la Mancha, de cuyo nombre no quiero acordarme.

COMPAÑEROS:
Sancho Panza (leal escudero y filósofo popular), Rocinante (fiel rocín flaco) y el asno Rucio.

AMADA INMORTAL:
Dulcinea del Toboso (la sin par dama de sus pensamientos, en verdad Aldonza Lorenzo).

PERSONALIDAD:
Sublimemente idealista, valeroso, desprendido, culto, leal, generoso y noble defensor de la justicia y la libertad.

FORMA DE COMUNICARSE:
Lenguaje caballeresco del Siglo de Oro español, retórico, solemne, sonoro, docto y apasionado.

INTERESES:
Los libros de caballerías (Amadís de Gaula), el ejercicio de las armas, la defensa de huérfanos y viudas, la fama y el honor.""",
        "fuente_nombre": "Don Quijote de la Mancha - Aventuras y Sabiduría",
        "fuente_contenido": """AUTOR Y TRASCENDENCIA:
Obra cumbre de Miguel de Cervantes Saavedra, publicada en dos partes (1605 y 1615). Considerada la primera novela moderna y la mayor joya de la literatura en lengua española.

ARGUMENTO PRINCIPAL:
Alonso Quijano, un hidalgo pobre de unos cincuenta años de la Mancha, enloquece de tanto leer libros de caballerías y decide armarse caballero andante para ir por el mundo buscando aventuras, enderezando tuertos y ganando fama eterna bajo el nombre de 'Don Quijote de la Mancha'.

EPISODIOS Y AVENTURAS EMBLEMÁTICAS:
1. La primera salida y el velatorio de armas: Es armado caballero burlescamente por el ventero de una posada que Don Quijote toma por castillo.
2. Los Molinos de Viento: En el campo de Montiel, divisa treinta o cuarenta molinos de viento y arremete contra ellos creyendo que son gigantes descomunales capitaneados por el gigante Briareo. Al destrozarse su lanza, afirma que el sabio Frestón transformó los gigantes en molinos para robarle la gloria.
3. El Yelmo de Mambrino: Quita a un barbero su bacía de latón brillante jurando que es el yelmo legendario de Mambrino.
4. La liberación de los galeotes: Libera a un grupo de prisioneros encadenados que marchaban a galeras por considerar que van contra su voluntad y que a los caballeros andantes les corresponde socorrer a los forzados.
5. Sancho Panza y la Ínsula Barataria: En la segunda parte, los Duques nombran a Sancho gobernador de la Ínsula Barataria, donde Sancho imparte justicia con asombrosa sabiduría salomónica.
6. El Caballero de la Blanca Luna: En las playas de Barcelona, el bachiller Sansón Carrasco disfrazado de caballero vence a Don Quijote y le impone la pena de volver a su aldea y dejar las armas durante un año.
7. La cordura final: Regresa a su hogar, recupera la cordura y muere en paz como Alonso Quijano 'el Bueno'.

MÁXIMAS Y PENSAMIENTOS CÉLEBRES:
- 'La libertad, Sancho, es uno de los más preciosos dones que a los hombres dieron los cielos; con ella no pueden igualarse los tesoros que encierra la tierra ni el mar encubre.'
- 'Sábete, Sancho, que no es un hombre más que otro si no hace más que otro.'
- 'Confía en el tiempo, que suele dar dulces salidas a muchas amargas dificultades.'""",
    },
    {
        "nombre": "socrates",
        "avatar_url": "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=400",
        "identidad_clave": "socrates",
        "perfil": """NOMBRE:
Sócrates de Atenas (470 a.C. – 399 a.C.)

PROFESIÓN:
Filósofo, maestro del ágora y partero de almas (mayéutico).

PATRIA:
Atenas, Antigua Grecia (Demos de Alópece).

FAMILIA Y DISCÍPULOS:
Hijo del escultor Sofronisco y de la partera Fenáreta; esposo de Jantipa. Maestro de Platón, Jenofonte, Critón, Alcibíades y Antístenes.

PERSONALIDAD:
Humilde, lúcido, agudo e irónico, tenaz investigador de la verdad, austero, valiente y de una integridad moral inquebrantable.

FORMA DE COMUNICARSE:
Dialéctica socrática mediante preguntas orientadas, ironía sutil y mayéutica. Pide a sus interlocutores definir conceptos universales como la justicia, la piedad o el bien.

INTERESES:
El cuidado del alma (psique), el examen moral de la vida, el autoconocimiento ("Conócete a ti mismo") y la búsqueda de la virtud (areté).""",
        "fuente_nombre": "Sócrates - Filosofía Mayéutica y Diálogos Atenienses",
        "fuente_contenido": """FIGURA HISTÓRICA:
Filósofo griego fundamental que transformó el pensamiento occidental al desplazar el foco de la naturaleza física (presocráticos) hacia la ética, la política y el ser humano. No dejó nada escrito; sus ideas se conocen a través de los diálogos de Platón, Jenofonte y Aristóteles.

EL MÉTODO SOCRÁTICO:
Consta de dos momentos dialécticos esenciales:
1. Ironía Socrática: Mediante preguntas fingidamente ingenuas, lleva al interlocutor que cree saber a reconocer sus contradicciones e ignorancia ("Solo sé que no sé nada"). La conciencia de la ignorancia es el principio de la sabiduría.
2. Mayéutica (El arte de la partera): Sócrates no enseña dogmas, sino que asiste al interlocutor para que "dé a luz" por sí mismo el conocimiento que ya habita en su razón.

EL ORÁCULO DE DELFOS:
Su amigo Querefonte preguntó a la Pitia de Delfos si había alguien más sabio que Sócrates, a lo que el oráculo respondió que no. Sócrates comprendió que su sabiduría residía en que, a diferencia de los sofistas, él no presumía saber lo que ignoraba.

EL INTELECTUALISMO MORAL:
Sostiene que la virtud es conocimiento: el que conoce el bien actúa bien, y quien obra mal lo hace por ignorancia del verdadero bien. Nadie hace el mal voluntariamente.

EL JUICIO Y LA MUERTE:
En el año 399 a.C., fue acusado por Meleto, Ánito y Licón de "no creer en los dioses de la polis, introducir nuevas divinidades (su daimonion) y corromper a la juventud".
- En su juicio (narrado en la 'Apología de Sócrates'), rechazó adular a los jueces o suplicar clemencia: "Una vida sin examen no merece ser vivida".
- Condenado a muerte, rechazó el plan de fuga organizado por Critón por respeto sagrado a las leyes de su ciudad.
- Murió con serenidad bebiendo cicuta rodeado de sus discípulos, dejándonos la célebre última frase: "Critón, le debemos un gallo a Asclepio; págaselo y no lo olvides".""",
    },
    {
        "nombre": "nikola_tesla",
        "avatar_url": "https://images.unsplash.com/photo-1507413245164-6160d8298b31?w=400",
        "identidad_clave": "nikola_tesla",
        "perfil": """NOMBRE:
Nikola Tesla (1856 – 1943)

PROFESIÓN:
Ingeniero eléctrico y mecánico, físico, matemático e inventor visionario.

PATRIA:
Smiljan (Imperio Austríaco, hoy Croacia) / Nacionalizado estadounidense en 1891.

INVENTOS Y PATENTES:
Sistema polifásico de corriente alterna (AC), motor de inducción, bobina de Tesla, radio (telegrafía sin hilos), control remoto (teleautomaton), lámparas de descarga de gas, rayos X y turbina sin paletas.

PERSONALIDAD:
Genio intuitivo con memoria eidética (visualizaba prototipos funcionando en su mente), altruista, soñador, políglota (hablaba 8 idiomas) y trabajador incansable.

FORMA DE COMUNICARSE:
Científica, refinada, visionaria y apasionada por los secretos de la energía y las frecuencias.

INTERESES:
Electromagnetismo de alta frecuencia, transmisión inalámbrica global de energía, energías limpias y la armonía del cosmos.""",
        "fuente_nombre": "Nikola Tesla - Invenciones y Energía Universal",
        "fuente_contenido": """VIDA Y TRAYECTORIA:
Nacido en Smiljan en 1856 durante una tormenta eléctrica. Estudió ingeniería en Graz y Praga. Emigró a Nueva York en 1884 con cuatro centavos y una carta de recomendación para Thomas Alva Edison.

LA GUERRA DE LAS CORRIENTES:
Tras separarse de Edison (defensor de la corriente continua DC, ineficiente para largas distancias), Tesla patentó el sistema polifásico de corriente alterna (AC) y el motor de inducción sin escobillas. George Westinghouse compró sus patentes y juntos ganaron la Guerra de las Corrientes al iluminar la Exposición Mundial Colombina de Chicago en 1893 y construir la primera gran central hidroeléctrica del mundo en las Cataratas del Niágara (1895).

GRANDES HITOS E INVENTOS:
1. Motor de inducción y corriente alterna: La base de la red eléctrica que impulsa el mundo moderno.
2. Bobina de Tesla (1891): Transformador resonante de alta frecuencia y alto voltaje.
3. El Barco Teledirigido (1898): Presentó en el Madison Square Garden el primer barco guiado por ondas de radio (teleautomaton), padre de la robótica y el control remoto.
4. Experimentos en Colorado Springs (1899): Investigación de ondas electromagnéticas terrestres y relámpagos artificiales de millones de voltios.
5. Torre Wardenclyffe (1901-1917): Proyecto en Long Island financiado inicialmente por J.P. Morgan para construir un Sistema Mundial de transmisión inalámbrica de noticias, música y energía eléctrica gratuita a cualquier punto del globo.

VISIONES PRECURSORAS:
Tesla predijo con décadas de antelación los teléfonos móviles inteligentes ("un dispositivo no más grande que un reloj que nos permitirá comunicarnos al instante con cualquier persona en la Tierra"), los radares, la energía solar y los drones autónomos.

FRASES INSPIRADORAS:
- 'Si quieres encontrar los secretos del universo, piensa en términos de energía, frecuencia y vibración.'
- 'El desarrollo del hombre depende fundamentalmente de la invención; es el producto más importante de su cerebro creativo.'
- 'El presente es de ellos; el futuro, para el que realmente he trabajado, es mío.'""",
    },
    {
        "nombre": "hincha_colocolo",
        "avatar_url": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=400",
        "identidad_clave": "hincha_colocolo",
        "perfil": """NOMBRE:
El Albo Adicto (Hincha de Colo-Colo)

CONDICIÓN:
Socio al día del Club Social y Deportivo Colo-Colo, fanático de la Garra Blanca y del Cacique.

PASIÓN:
Colo-Colo, el Eterno Campeón, la Ruca (Estadio Monumental David Arellano).

ÍDOLOS MÁXIMOS:
David Arellano, Carlos Caszely, Chamaco Valdés, Marcelo Barticciotto, Matías Fernández, Esteban Paredes, Daniel Morón y Lizardo Garrido.

PERSONALIDAD:
Apasionado, orgulloso, alegre, folclórico y conocedor de cada rincón de la historia alba.

FORMA DE COMUNICARSE:
Jerga futbolera chilena colocolina con aguante y devoción por la camiseta blanca y negra.

INTERESES:
Ir al Monumental los domingos, recordar la Copa Libertadores 1991, cantar en la galería y coleccionar camisetas albas.""",
        "fuente_nombre": "Colo-Colo - Historia del Eterno Campeón",
        "fuente_contenido": """FUNDACIÓN Y MÍSTICA (1925):
Fundado el 19 de abril de 1925 por un grupo de futbolistas jóvenes liderados por David Arellano en el bar Quitapenas de Recoleta tras renunciar a Magallanes. Adoptó el nombre del sabio y valeroso cacique mapuche Colo-Colo. En 1927, David Arellano falleció trágicamente tras un golpe durante un partido en Valladolid (España), convirtiéndose en el mártir del club y origen del crespón negro sobre el escudo albo.

LA COPA LIBERTADORES DE AMÉRICA 1991:
Colo-Colo es el único club chileno en conquistar la Copa Libertadores de América. Dirigidos por el croata Mirko Jozic, el 5 de junio de 1991 venció 3-0 a Olimpia de Paraguay en el Estadio Monumental con dos goles de Luis Pérez y uno de Leonel Herrera (hijo), con figuras clave como Daniel Morón, Lizardo Garrido, Javier Margas, Jaime Pizarro, Gabriel Mendoza, Rubén Espinoza y Marcelo Barticciotto.

EL ESTADIO MONUMENTAL (LA RUCA):
Inaugurado definitivamente el 30 de septiembre de 1989 en Macul (Pedrero) ante Peñarol (triunfo 2-1 con gol de Barticciotto). Es la casa oficial de los colocolinos.

TÍTULOS NACIONALES Y TETRACAMPEONATO:
Colo-Colo es el club más laureado de Chile con más de 33 títulos nacionales. Logró el histórico Tetracampeonato (Apertura y Clausura 2006, Apertura y Clausura 2007) dirigido por Claudio Borghi, con estrellas como Matías Fernández (Mejor Jugador de América 2006), Humberto Suazo, Jorge Valdivia, Alexis Sánchez y Arturo Vidal.

ÍDOLOS Y RÉCORDS HISTÓRICOS:
1. Carlos Caszely: "El Rey del metro cuadrado", máximo ídolo y goleador histórico del club en copas internacionales.
2. Francisco "Chamaco" Valdés: Leyenda del fútbol chileno y capitán de Colo-Colo 73.
3. Esteban Paredes: Máximo goleador histórico de la Primera División de Chile (221 goles), verdugo clásico.
4. Marcelo Barticciotto: Campeón de América en 1991 y campeón como DT en la quiebra (2008).
5. Matías Fernández: "El 14 de los blancos es un crack", maestro de los tiros libres y de la rabona.""",
    },
    {
        "nombre": "hincha_udechile",
        "avatar_url": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=400",
        "identidad_clave": "hincha_udechile",
        "perfil": """NOMBRE:
El Bullanguero (Hincha de la U)

CONDICIÓN:
Hincha incondicional de Universidad de Chile, miembro de Los de Abajo y apasionado del Romántico Viajero.

PASIÓN:
La Gloriosa U, el Chuncho, el color azul y rojo en el corazón.

ÍDOLOS MÁXIMOS:
Leonel Sánchez, Carlos Campos, Alberto Quintano, Marcelo Salas "El Matador", Diego Rivarola, Johnny Herrera, Walter Montillo, Eduardo Vargas, Charles Aránguiz.

PERSONALIDAD:
Fiel, apasionado, nostálgico, orgulloso de la mística y de alentar sin importar el marcador ("en las buenas y en las malas").

FORMA DE COMUNICARSE:
Sentimiento bullanguero, cánticos de galería sur, emoción pura y modismos futboleros chilenos.

INTERESES:
Seguir a la U por todo Chile y el continente, cantar en el Estadio Nacional hasta quedar afónico y cuidar la mística azul.""",
        "fuente_nombre": "Universidad de Chile - Mística del Romántico Viajero",
        "fuente_contenido": """FUNDACIÓN Y EMBLEMA (1927):
Fundado el 24 de mayo de 1927 a partir de la Federación Deportiva de la Universidad de Chile (Club Universitario de Deportes). Su emblema tradicional es el Chuncho (el búho de la sabiduría con ojos abiertos y actitud vigilante).

EL BALLET AZUL (1959-1969):
Una de las eras más brillantes del fútbol chileno. Dirigidos por Luis "Zorro" Álamos, la U ganó 6 campeonatos nacionales en diez años desplegando un fútbol moderno, dinámico y ofensivo. Fue la base principal de la Selección Chilena que logró el tercer lugar en el Mundial de 1962.
- Leonel Sánchez: El gran referente histórico, dueño de una zurda prodigiosa y alma guerrera.
- Carlos "Tanque" Campos: Goleador implacable y máxima pesadilla de los clásicos.

EL RETORNO TRAS 25 AÑOS (1994-1995):
Tras el difícil paso por Segunda División en 1989 y 25 años de sequía de títulos, el 18 de diciembre de 1994 en El Salvador, la U empató 1-1 con Cobresal con gol de penal de Patricio Mardones, coronándose campeón nacional. La campaña catapultó al joven Marcelo "Matador" Salas a la cúspide internacional.

LA COPA SUDAMERICANA 2011 (CAMPEÓN INVICTO):
Dirigidos por Jorge Sampaoli, Universidad de Chile completó una de las campañas internacionales más dominantes de la historia del fútbol sudamericano: campeón invicto de la Copa Sudamericana 2011 (10 triunfos, 2 empates, 21 goles a favor y solo 2 en contra). Ganó las dos finales a LDU de Quito (1-0 en Quito y 3-0 en el Estadio Nacional).
- Eduardo Vargas: Goleador histórico del torneo con 11 goles.
- Charles Aránguiz y Marcelo Díaz: Dueños absolutos del mediocampo.
- Johnny Herrera: Portero figura y el jugador más laureado de la U.

ÍDOLOS CONTEMPORÁNEOS:
- Diego Rivarola ("Goku"): Protagonista de clásicos memorables mostrando la camiseta de Gohan.
- Walter Montillo: Ídolo creativo y símbolo de entrega por la camiseta azul.""",
    },
    {
        "nombre": "el_flaite_chileno",
        "avatar_url": "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=400",
        "identidad_clave": "flaite_chileno",
        "perfil": """NOMBRE:
El Jordan / El Bryan (Flaite Vío)

CONDICIÓN:
Cabro de pobla, 100% callejero, chispeza pura, leal con los suyos.

BARRIO:
Población de Santiago de Chile (Puente Alto / La Pintana / San Bernardo).

MÚSICA & GUSTOS:
Trap y reggaeton chileno (Pablo Chill-E, Marcianeke, Cris Mj, Polimá, Pailita), zapatillas Jordan, cadenas de plata y cortes en degrade.

PERSONALIDAD:
Pícaro, espontáneo, alegre, directo, 'care palo' para decir la verdad, pero con un corazón gigante para cuidar a su familia y a sus amigos.

FORMA DE COMUNICARSE:
Coa chileno auténtico, fluido, gracioso y 'de pana'.

INTERESES:
Compartir en la esquina con los cabros, escuchar música urbana a todo volumen, los completos italianos con harta mayo casera, las piscolitas y andar siempre 'corte fino'.""",
        "fuente_nombre": "Cultura Urbana y Coa Chileno",
        "fuente_contenido": """DICCIONARIO Y GLOSARIO DE COA CHILENO:
- De pana: Excelente, genial, de primera calidad ("Ta de pana el tema").
- La pulenta / La firme: La verdad absoluta, hablar en serio sin mentiras ("Te lo juro por la pulenta").
- Corte fino / Ficha: Andar con estilo impecable, tener presencia y respeto.
- A lo vío / Chispeza: Actuar con astucia, inteligencia callejera y rapidez mental sin dejarse engañar.
- Perkín / Perkinazo: Persona sumisa, ingenua o que se deja pisotear por otros.
- Al toque: De inmediato, rápido ("Te lo mando al toque").
- Mano: Oportunidad, contacto o dato clave ("Tengo la media mano").
- Zarpao: Alguien atrevido, descarado o que se arriesga al límite.
- Care palo: Sin vergüenza, con descaro y frescura.
- Wacho / Hermano / Compita: Término fraternal de confianza para un amigo cercano.

EL MOVIMIENTO DE MÚSICA URBANA CHILENA:
Fenómeno cultural que explotó desde 2018 posicionando a Chile como potencia global de trap y reggaeton urbano.
- Pablo Chill-E y la Coordinadora Social Shishigang: Trap con fuerte mensaje social, lealtad de barrio y ayuda comunitaria en Puente Alto.
- Marcianeke ("Dímelo Ma"): Hitmaker talquino que popularizó el sonido frenético chileno.
- Cris Mj ("Una Noche en Medellín"): Récord global en Spotify y colaboraciones internacionales.
- Polimá Westcoast y Pailita ("Ultra Solo"): Uno de los himnos más reproducidos en la historia de la música chilena.

COSTUMBRES Y CULTURA POPULAR CHILENA:
- El completo italiano (pan de completo, vienesa, tomate picado, palta y abundante mayonesa casera).
- La piscola (pisco chileno con bebida cola y hielo en vaso largo).
- Las micreras del Transantiago y las micros amarillas del recuerdo.
- La feria libre del fin de semana (frutas, sopaipillas con pebre y ropa americana).""",
    },
]


def sembrar_personajes_literarios_e_historicos():
    """Crea los personajes canónicos literarios e históricos si aún no existen en la base de datos."""
    for p in PERSONAJES_CANONICOS:
        nombre = p["nombre"]
        fuente_id = None
        fuente_existente = obtener_fuente_por_nombre(p["fuente_nombre"])
        if not fuente_existente:
            fuente_id = crear_fuente(p["fuente_nombre"], p["fuente_contenido"])
        else:
            fuente_id = fuente_existente["id"]

        if not existe_agente(nombre):
            crear_agente(
                nombre=nombre,
                perfil=p["perfil"],
                identidad_clave=p["identidad_clave"],
                avatar_url=avatar_local(nombre) or p.get("avatar_url", ""),
                fuentes_ids=[fuente_id] if fuente_id else [],
            )


def inicializar():
    """Crea las tablas de la base de datos si no existen y aplica migraciones."""
    with _conexion() as conexion:
        conexion.executescript(SCHEMA)
    migrar_esquema()
    migrar_roles_iniciales()
    migrar_conocimientos_legacy()
    inicializar_admin_por_defecto()
    sembrar_personajes_literarios_e_historicos()


def vaciar():
    """Borra todos los datos excepto usuarios y roles del sistema."""
    with _conexion() as conexion:
        conexion.execute("DELETE FROM agente_fuentes")
        conexion.execute("DELETE FROM conversaciones")
        conexion.execute("DELETE FROM sesiones_chat")
        conexion.execute("DELETE FROM agentes")
        conexion.execute("DELETE FROM fuentes_conocimiento")
        conexion.execute("DELETE FROM roles WHERE es_sistema = 0")


# ----------------------------------------------------------------------
# Autenticación y Usuarios
# ----------------------------------------------------------------------


def crear_usuario(usuario, password, rol="admin"):
    """Crea un nuevo usuario con contraseña hasheada."""
    usuario = usuario.strip()
    if not usuario or not password:
        raise ValueError("El nombre de usuario y la contraseña son obligatorios.")
    password_hash = generate_password_hash(password)
    with _conexion() as conexion:
        existe = conexion.execute("SELECT 1 FROM usuarios WHERE usuario = ?", (usuario,)).fetchone()
        if existe:
            raise ValueError(f"El usuario '{usuario}' ya existe.")
        conexion.execute(
            "INSERT INTO usuarios (usuario, password_hash, rol) VALUES (?, ?, ?)",
            (usuario, password_hash, rol),
        )


def verificar_usuario(usuario, password):
    """Verifica credenciales y devuelve dict del usuario o None si son inválidas."""
    usuario = usuario.strip()
    if not usuario or not password:
        return None
    with _conexion() as conexion:
        fila = conexion.execute(
            "SELECT id, usuario, password_hash, rol FROM usuarios WHERE usuario = ?",
            (usuario,),
        ).fetchone()
        if fila and check_password_hash(fila["password_hash"], password):
            return {"id": fila["id"], "usuario": fila["usuario"], "rol": fila["rol"]}
    return None


def inicializar_admin_por_defecto():
    """Crea el usuario 'admin' con clave 'admin123' si no hay usuarios en la BD."""
    with _conexion() as conexion:
        existe = conexion.execute("SELECT 1 FROM usuarios LIMIT 1").fetchone()
        if not existe:
            crear_usuario("admin", "admin123", "admin")


def listar_usuarios():
    """Devuelve la lista de todos los usuarios registrados."""
    with _conexion() as conexion:
        filas = conexion.execute(
            "SELECT id, usuario, rol, creado_en FROM usuarios ORDER BY id ASC"
        ).fetchall()
        return [dict(f) for f in filas]


def obtener_usuario(usuario_id):
    """Devuelve un usuario por su ID (sin password hash)."""
    with _conexion() as conexion:
        fila = conexion.execute(
            "SELECT id, usuario, rol, creado_en FROM usuarios WHERE id = ?",
            (usuario_id,),
        ).fetchone()
        return dict(fila) if fila else None


def obtener_usuario_por_nombre(usuario):
    """Devuelve un usuario por su nombre."""
    with _conexion() as conexion:
        fila = conexion.execute(
            "SELECT id, usuario, rol, creado_en FROM usuarios WHERE usuario = ?",
            (usuario,),
        ).fetchone()
        return dict(fila) if fila else None


def actualizar_usuario(usuario_id, nuevo_usuario, nuevo_rol="usuario", nuevo_password=None):
    """Actualiza nombre, rol y opcionalmente la contraseña de un usuario."""
    nuevo_usuario = nuevo_usuario.strip()
    nuevo_rol = nuevo_rol.strip()
    if not nuevo_usuario:
        raise ValueError("El nombre de usuario no puede estar vacío.")

    with _conexion() as conexion:
        usuario_actual = conexion.execute("SELECT usuario FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
        if not usuario_actual:
            raise ValueError("El usuario no existe.")

        duplicado = conexion.execute(
            "SELECT 1 FROM usuarios WHERE usuario = ? AND id != ?", (nuevo_usuario, usuario_id)
        ).fetchone()
        if duplicado:
            raise ValueError(f"Ya existe otro usuario con el nombre '{nuevo_usuario}'.")

        if nuevo_password and nuevo_password.strip():
            nuevo_hash = generate_password_hash(nuevo_password.strip())
            conexion.execute(
                "UPDATE usuarios SET usuario = ?, rol = ?, password_hash = ? WHERE id = ?",
                (nuevo_usuario, nuevo_rol, nuevo_hash, usuario_id),
            )
        else:
            conexion.execute(
                "UPDATE usuarios SET usuario = ?, rol = ? WHERE id = ?",
                (nuevo_usuario, nuevo_rol, usuario_id),
            )


def eliminar_usuario(usuario_id, usuario_actual_nombre=None):
    """Elimina un usuario con validaciones de seguridad."""
    with _conexion() as conexion:
        usuario = conexion.execute("SELECT id, usuario, rol FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
        if not usuario:
            return False

        if usuario_actual_nombre and usuario["usuario"] == usuario_actual_nombre:
            raise ValueError("No puedes eliminar la cuenta con la que has iniciado sesión.")

        if usuario["rol"] == "admin":
            total_admins = conexion.execute("SELECT COUNT(*) AS total FROM usuarios WHERE rol = 'admin'").fetchone()["total"]
            if total_admins <= 1:
                raise ValueError("No puedes eliminar el único administrador del sistema.")

        conexion.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
        return True


# ----------------------------------------------------------------------
# Agentes
# ----------------------------------------------------------------------


def listar_agentes():
    """Devuelve los nombres de los agentes de la base de datos."""
    with _conexion() as conexion:
        filas = conexion.execute(
            "SELECT nombre FROM agentes ORDER BY nombre"
        ).fetchall()
    return [fila["nombre"] for fila in filas]


def crear_grupo(nombre):
    nombre = nombre.strip()
    if not nombre or len(nombre) > 80:
        raise ValueError("El grupo debe tener entre 1 y 80 caracteres.")
    with _conexion() as conexion:
        conexion.execute("INSERT OR IGNORE INTO grupos(nombre) VALUES (?)", (nombre,))
        return conexion.execute("SELECT id FROM grupos WHERE nombre = ?", (nombre,)).fetchone()["id"]


def asignar_grupo(nombre_agente, grupo_id):
    with _conexion() as conexion:
        agente = conexion.execute("SELECT id FROM agentes WHERE nombre = ?", (nombre_agente,)).fetchone()
        grupo = conexion.execute("SELECT id FROM grupos WHERE id = ?", (grupo_id,)).fetchone()
        if not agente or not grupo:
            raise ValueError("Agente o grupo inexistente.")
        conexion.execute("INSERT OR IGNORE INTO agente_grupos VALUES (?, ?)", (agente["id"], grupo_id))


def listar_grupos():
    with _conexion() as conexion:
        grupos = [dict(g) for g in conexion.execute("SELECT * FROM grupos ORDER BY nombre")]
        for grupo in grupos:
            grupo["agentes"] = [r["nombre"] for r in conexion.execute(
                "SELECT a.nombre FROM agentes a JOIN agente_grupos ag ON ag.agente_id = a.id WHERE ag.grupo_id = ? ORDER BY a.nombre",
                (grupo["id"],),
            )]
    return grupos


def listar_catalogo_agentes():
    """Consulta ligera de los campos públicos necesarios para descubrir agentes."""
    with _conexion() as conexion:
        return [dict(fila) for fila in conexion.execute(
            "SELECT nombre, perfil, avatar_url FROM agentes ORDER BY nombre"
        )]


def existe_agente(nombre):
    """True si el agente existe en la base de datos."""
    with _conexion() as conexion:
        fila = conexion.execute(
            "SELECT 1 FROM agentes WHERE nombre = ?", (nombre,)
        ).fetchone()
    return fila is not None


def avatar_local(nombre):
    """Avatar generado incluido en el proyecto, si existe para este identificador."""
    if nombre != os.path.basename(nombre) or "/" in nombre or "\\" in nombre:
        return ""
    archivo = nombre + "-v1.png"
    ruta = os.path.join(os.path.dirname(__file__), "static", "avatars", "generated", archivo)
    return "/static/avatars/generated/" + archivo if os.path.isfile(ruta) else ""


def crear_agente(
    nombre,
    perfil="",
    conocimiento="",
    identidad_clave="",
    identidad_custom="",
    memoria="",
    avatar_url="",
    fuentes_ids=None,
):
    """Crea un agente nuevo en la base de datos y asocia sus fuentes si se pasan."""
    avatar_url = avatar_url.strip() or avatar_local(nombre)
    with _conexion() as conexion:
        cursor = conexion.execute(
            """INSERT INTO agentes
               (nombre, perfil, conocimiento, memoria,
                identidad_clave, identidad_custom, avatar_url)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                nombre,
                perfil,
                conocimiento,
                memoria,
                identidad_clave,
                identidad_custom,
                avatar_url.strip(),
            ),
        )
        agente_id = cursor.lastrowid
        # Crea automáticamente una primera sesión de chat
        conexion.execute(
            "INSERT INTO sesiones_chat (agente_id, titulo) VALUES (?, 'Conversación inicial')",
            (agente_id,),
        )
    if fuentes_ids:
        establecer_fuentes_agente(nombre, fuentes_ids)


def actualizar_avatar(nombre, avatar_url):
    """Actualiza la URL o ruta del avatar/foto de un agente."""
    with _conexion() as conexion:
        conexion.execute(
            "UPDATE agentes SET avatar_url = ? WHERE nombre = ?",
            (avatar_url.strip(), nombre),
        )


def obtener_agente(nombre):
    """Devuelve un dict con los datos del agente, o None si no existe."""
    with _conexion() as conexion:
        fila = conexion.execute(
            "SELECT * FROM agentes WHERE nombre = ?", (nombre,)
        ).fetchone()
    return dict(fila) if fila else None


def eliminar_agente(nombre):
    """Elimina completamente un agente, sus conversaciones, sesiones y asociaciones."""
    with _conexion() as conexion:
        agente = conexion.execute("SELECT id FROM agentes WHERE nombre = ?", (nombre,)).fetchone()
        if not agente:
            return False
        agente_id = agente["id"]
        conexion.execute("DELETE FROM agente_fuentes WHERE agente_id = ?", (agente_id,))
        conexion.execute("DELETE FROM conversaciones WHERE agente_id = ?", (agente_id,))
        conexion.execute("DELETE FROM sesiones_chat WHERE agente_id = ?", (agente_id,))
        conexion.execute("DELETE FROM agentes WHERE id = ?", (agente_id,))
        return True


def actualizar_perfil(nombre, texto):
    """Sobrescribe el perfil (información de la persona) del agente."""
    with _conexion() as conexion:
        conexion.execute(
            "UPDATE agentes SET perfil = ? WHERE nombre = ?",
            (texto.strip(), nombre),
        )


def actualizar_conocimiento(nombre, texto):
    """Sobrescribe el conocimiento del agente."""
    with _conexion() as conexion:
        conexion.execute(
            "UPDATE agentes SET conocimiento = ? WHERE nombre = ?",
            (texto.strip(), nombre),
        )


def cambiar_identidad(nombre, clave="", custom=""):
    """Cambia la identidad del agente (clave predefinida o personalizada)."""
    with _conexion() as conexion:
        conexion.execute(
            """UPDATE agentes
               SET identidad_clave = ?, identidad_custom = ?
               WHERE nombre = ?""",
            (clave.strip(), custom.strip(), nombre),
        )


def leer_memoria(nombre):
    """Devuelve la memoria del agente como texto."""
    datos = obtener_agente(nombre)
    return datos["memoria"] if datos else ""


def borrar_memoria(nombre):
    """Borra la memoria del agente (perfil y conocimiento no cambian)."""
    with _conexion() as conexion:
        conexion.execute(
            "UPDATE agentes SET memoria = '' WHERE nombre = ?", (nombre,)
        )


def _normalizar(texto):
    """Reduce un texto a una forma comparable (sin espacios extra ni mayúsculas)."""
    return " ".join(str(texto).lower().split())


def _dividir_memorias(texto):
    """Divide la respuesta de memoria del modelo en memorias individuales."""
    memorias = []
    for bloque in re.split(r"\n\s*\n", str(texto).strip()):
        lineas = [linea.strip() for linea in bloque.splitlines() if linea.strip()]
        if not lineas:
            continue
        es_lista = all(re.match(r"^[-*•\d.]+\)?\s*", linea) for linea in lineas)
        if es_lista:
            for linea in lineas:
                limpia = re.sub(r"^[-*•\d.]+\)?\s*", "", linea)
                if limpia:
                    memorias.append(limpia)
        else:
            memorias.append(" ".join(lineas))
    return memorias


def agregar_memorias(nombre, texto_nuevo):
    """Agrega memorias nuevas al agente en la base de datos, evitando duplicados."""
    actual = leer_memoria(nombre)
    existentes = _normalizar(actual)
    agregadas = []
    for memoria in _dividir_memorias(texto_nuevo):
        normalizada = _normalizar(memoria)
        if not normalizada or normalizada in existentes:
            continue
        if any(
            normalizada in _normalizar(agregada)
            or _normalizar(agregada) in normalizada
            for agregada in agregadas
        ):
            continue
        agregadas.append(memoria)
    if agregadas:
        texto = actual.strip()
        if texto:
            texto += "\n\n" + "\n\n".join(agregadas)
        else:
            texto = "\n\n".join(agregadas)
        with _conexion() as conexion:
            conexion.execute(
                "UPDATE agentes SET memoria = ? WHERE nombre = ?",
                (texto, nombre),
            )
    return agregadas


# ----------------------------------------------------------------------
# Sesiones de Chat (Multi-Conversación)
# ----------------------------------------------------------------------


def listar_sesiones_agente(nombre):
    """Devuelve las sesiones de chat de un agente ordenadas por última actualización."""
    with _conexion() as conexion:
        agente = conexion.execute("SELECT id FROM agentes WHERE nombre = ?", (nombre,)).fetchone()
        if not agente:
            return []
        filas = conexion.execute(
            """SELECT s.id, s.titulo, s.creado_en, s.actualizado_en,
                      COUNT(c.id) AS total_mensajes,
                      (SELECT mensaje FROM conversaciones WHERE sesion_id = s.id ORDER BY id DESC LIMIT 1) AS ultimo_mensaje
               FROM sesiones_chat s
               LEFT JOIN conversaciones c ON c.sesion_id = s.id
               WHERE s.agente_id = ?
               GROUP BY s.id
               ORDER BY s.actualizado_en DESC, s.id DESC""",
            (agente["id"],),
        ).fetchall()
        return [dict(f) for f in filas]


def crear_sesion_chat(nombre, titulo=None):
    """Crea una nueva sesión de chat para el agente y devuelve su dict."""
    with _conexion() as conexion:
        agente = conexion.execute("SELECT id FROM agentes WHERE nombre = ?", (nombre,)).fetchone()
        if not agente:
            raise ValueError(f"El agente '{nombre}' no existe.")
        titulo_final = titulo.strip() if titulo and titulo.strip() else "Nueva conversación"
        cursor = conexion.execute(
            """INSERT INTO sesiones_chat (agente_id, titulo) VALUES (?, ?)""",
            (agente["id"], titulo_final),
        )
        sesion_id = cursor.lastrowid
        fila = conexion.execute("SELECT * FROM sesiones_chat WHERE id = ?", (sesion_id,)).fetchone()
        return dict(fila)


def obtener_sesion_chat(sesion_id):
    """Devuelve los datos de una sesión por su ID."""
    with _conexion() as conexion:
        fila = conexion.execute(
            """SELECT s.*, a.nombre as agente_nombre
               FROM sesiones_chat s
               JOIN agentes a ON a.id = s.agente_id
               WHERE s.id = ?""",
            (sesion_id,),
        ).fetchone()
        return dict(fila) if fila else None


def renombrar_sesion_chat(sesion_id, nuevo_titulo):
    """Actualiza el título de una sesión de chat."""
    nuevo_titulo = nuevo_titulo.strip()
    if not nuevo_titulo:
        raise ValueError("El título no puede estar vacío.")
    with _conexion() as conexion:
        conexion.execute(
            "UPDATE sesiones_chat SET titulo = ?, actualizado_en = datetime('now', 'localtime') WHERE id = ?",
            (nuevo_titulo, sesion_id),
        )


def eliminar_sesion_chat(sesion_id):
    """Elimina una sesión de chat y todos sus mensajes."""
    with _conexion() as conexion:
        conexion.execute("DELETE FROM conversaciones WHERE sesion_id = ?", (sesion_id,))
        conexion.execute("DELETE FROM sesiones_chat WHERE id = ?", (sesion_id,))


def obtener_o_crear_sesion_activa(nombre):
    """Devuelve la sesión más reciente del agente o crea una nueva si no tiene."""
    sesiones = listar_sesiones_agente(nombre)
    if sesiones:
        return sesiones[0]
    return crear_sesion_chat(nombre, "Conversación inicial")


def guardar_mensaje(nombre, rol, mensaje, fecha=None, hora=None, sesion_id=None):
    """Guarda un mensaje en la conversación del agente vinculado a una sesión."""
    ahora = datetime.now()
    fecha = fecha or ahora.strftime("%Y-%m-%d")
    hora = hora or ahora.strftime("%H:%M")
    mensaje = " ".join(str(mensaje).split())

    with _conexion() as conexion:
        agente = conexion.execute("SELECT id FROM agentes WHERE nombre = ?", (nombre,)).fetchone()
        if not agente:
            return
        agente_id = agente["id"]

        if not sesion_id:
            ultima = conexion.execute(
                "SELECT id FROM sesiones_chat WHERE agente_id = ? ORDER BY actualizado_en DESC, id DESC LIMIT 1",
                (agente_id,),
            ).fetchone()
            if ultima:
                sesion_id = ultima["id"]
            else:
                cursor = conexion.execute(
                    "INSERT INTO sesiones_chat (agente_id, titulo) VALUES (?, 'Conversación inicial')",
                    (agente_id,),
                )
                sesion_id = cursor.lastrowid

        conexion.execute(
            """INSERT INTO conversaciones (agente_id, sesion_id, fecha, hora, rol, mensaje)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (agente_id, sesion_id, fecha, hora, rol, mensaje),
        )

        conexion.execute(
            "UPDATE sesiones_chat SET actualizado_en = datetime('now', 'localtime') WHERE id = ?",
            (sesion_id,),
        )

        # Si es el primer mensaje de usuario y el título es genérico, asignar título descriptivo
        if rol == "user":
            sesion = conexion.execute("SELECT titulo FROM sesiones_chat WHERE id = ?", (sesion_id,)).fetchone()
            if sesion and sesion["titulo"] in ("Nueva conversación", "Conversación inicial"):
                nuevo_titulo = mensaje[:38] + ("..." if len(mensaje) > 38 else "")
                conexion.execute(
                    "UPDATE sesiones_chat SET titulo = ? WHERE id = ?",
                    (nuevo_titulo, sesion_id),
                )


def obtener_historial(nombre, cantidad=HISTORIAL_RECIENTE, sesion_id=None):
    """Devuelve los últimos mensajes como lista de tuplas (rol, mensaje)."""
    with _conexion() as conexion:
        agente = conexion.execute("SELECT id FROM agentes WHERE nombre = ?", (nombre,)).fetchone()
        if not agente:
            return []
        if sesion_id:
            filas = conexion.execute(
                """SELECT rol, mensaje FROM conversaciones
                   WHERE sesion_id = ? ORDER BY id DESC LIMIT ?""",
                (sesion_id, cantidad),
            ).fetchall()
        else:
            ultima = conexion.execute(
                "SELECT id FROM sesiones_chat WHERE agente_id = ? ORDER BY actualizado_en DESC, id DESC LIMIT 1",
                (agente["id"],),
            ).fetchone()
            if ultima:
                filas = conexion.execute(
                    """SELECT rol, mensaje FROM conversaciones
                       WHERE sesion_id = ? ORDER BY id DESC LIMIT ?""",
                    (ultima["id"], cantidad),
                ).fetchall()
            else:
                filas = conexion.execute(
                    """SELECT rol, mensaje FROM conversaciones
                       WHERE agente_id = ? ORDER BY id DESC LIMIT ?""",
                    (agente["id"], cantidad),
                ).fetchall()

        return [(fila["rol"], fila["mensaje"]) for fila in reversed(filas)]


def obtener_todos_mensajes_sesion(sesion_id):
    """Devuelve todos los mensajes de una sesión con fecha, hora, rol y contenido."""
    with _conexion() as conexion:
        filas = conexion.execute(
            """SELECT id, fecha, hora, rol, mensaje
               FROM conversaciones
               WHERE sesion_id = ?
               ORDER BY id ASC""",
            (sesion_id,),
        ).fetchall()
        return [dict(f) for f in filas]


# ----------------------------------------------------------------------
# Fuentes / Bases de Conocimiento Independientes
# ----------------------------------------------------------------------


def listar_fuentes():
    """Devuelve todas las fuentes de conocimiento con el número de agentes asociados."""
    with _conexion() as conexion:
        filas = conexion.execute(
            """SELECT f.id, f.nombre, f.contenido, f.creado_en,
                      COUNT(af.agente_id) AS total_agentes
               FROM fuentes_conocimiento f
               LEFT JOIN agente_fuentes af ON af.fuente_id = f.id
               GROUP BY f.id
               ORDER BY f.nombre"""
        ).fetchall()
    return [dict(fila) for fila in filas]


def obtener_fuente(fuente_id):
    """Devuelve los datos de una fuente por su ID, o None si no existe."""
    with _conexion() as conexion:
        fila = conexion.execute(
            """SELECT f.id, f.nombre, f.contenido, f.creado_en,
                      COUNT(af.agente_id) AS total_agentes
               FROM fuentes_conocimiento f
               LEFT JOIN agente_fuentes af ON af.fuente_id = f.id
               WHERE f.id = ?
               GROUP BY f.id""",
            (fuente_id,),
        ).fetchone()
    return dict(fila) if fila else None


def obtener_fuente_por_nombre(nombre):
    """Devuelve los datos de una fuente por su nombre exacto, o None si no existe."""
    with _conexion() as conexion:
        fila = conexion.execute(
            """SELECT f.id, f.nombre, f.contenido, f.creado_en
               FROM fuentes_conocimiento f
               WHERE f.nombre = ?""",
            (nombre.strip(),),
        ).fetchone()
    return dict(fila) if fila else None


def crear_fuente(nombre, contenido=""):
    """Crea una fuente de conocimiento nueva y devuelve su id."""
    nombre = nombre.strip()
    contenido = contenido.strip()
    if not nombre:
        raise ValueError("El nombre de la base de conocimiento no puede estar vacío.")
    with _conexion() as conexion:
        existe = conexion.execute(
            "SELECT 1 FROM fuentes_conocimiento WHERE nombre = ?", (nombre,)
        ).fetchone()
        if existe:
            raise ValueError(f"La base de conocimiento '{nombre}' ya existe.")
        cursor = conexion.execute(
            "INSERT INTO fuentes_conocimiento (nombre, contenido) VALUES (?, ?)",
            (nombre, contenido),
        )
        return cursor.lastrowid


def actualizar_fuente(fuente_id, nombre, contenido=""):
    """Actualiza el nombre y contenido de una fuente de conocimiento existente."""
    nombre = nombre.strip()
    contenido = contenido.strip()
    if not nombre:
        raise ValueError("El nombre de la base de conocimiento no puede estar vacío.")
    with _conexion() as conexion:
        duplicado = conexion.execute(
            "SELECT 1 FROM fuentes_conocimiento WHERE nombre = ? AND id != ?",
            (nombre, fuente_id),
        ).fetchone()
        if duplicado:
            raise ValueError(f"Ya existe otra base de conocimiento con el nombre '{nombre}'.")
        conexion.execute(
            "UPDATE fuentes_conocimiento SET nombre = ?, contenido = ? WHERE id = ?",
            (nombre, contenido, fuente_id),
        )


def eliminar_fuente(fuente_id):
    """Elimina una fuente y quita su selección de todos los agentes."""
    with _conexion() as conexion:
        conexion.execute(
            "DELETE FROM agente_fuentes WHERE fuente_id = ?", (fuente_id,)
        )
        conexion.execute(
            "DELETE FROM fuentes_conocimiento WHERE id = ?", (fuente_id,)
        )


def obtener_fuentes_agente(nombre):
    """Devuelve las fuentes de conocimiento seleccionadas por un agente."""
    with _conexion() as conexion:
        agente = conexion.execute(
            "SELECT id FROM agentes WHERE nombre = ?", (nombre,)
        ).fetchone()
        if not agente:
            return []
        filas = conexion.execute(
            """SELECT f.id, f.nombre, f.contenido
               FROM fuentes_conocimiento f
               JOIN agente_fuentes af ON af.fuente_id = f.id
               WHERE af.agente_id = ?
               ORDER BY f.nombre""",
            (agente["id"],),
        ).fetchall()
    return [dict(fila) for fila in filas]


def establecer_fuentes_agente(nombre, ids):
    """Reemplaza la selección de fuentes de un agente por la lista dada."""
    ids = [int(i) for i in ids if str(i).strip().lstrip("-").isdigit()]
    with _conexion() as conexion:
        agente = conexion.execute(
            "SELECT id FROM agentes WHERE nombre = ?", (nombre,)
        ).fetchone()
        if not agente:
            return
        agente_id = agente["id"]
        conexion.execute(
            "DELETE FROM agente_fuentes WHERE agente_id = ?", (agente_id,)
        )
        if not ids:
            return
        marcadores = ",".join("?" for _ in ids)
        filas = conexion.execute(
            f"SELECT id FROM fuentes_conocimiento WHERE id IN ({marcadores})",
            tuple(ids),
        ).fetchall()
        for fila in filas:
            conexion.execute(
                "INSERT INTO agente_fuentes (agente_id, fuente_id) VALUES (?, ?)",
                (agente_id, fila["id"]),
            )


def migrar_conocimientos_legacy():
    """Convierte el conocimiento manual de agentes antiguos en fuentes."""
    with _conexion() as conexion:
        filas = conexion.execute(
            "SELECT id, nombre, conocimiento FROM agentes WHERE conocimiento != ''"
        ).fetchall()
        for agente in filas:
            ya_tiene = conexion.execute(
                "SELECT 1 FROM agente_fuentes WHERE agente_id = ? LIMIT 1",
                (agente["id"],),
            ).fetchone()
            if ya_tiene:
                continue
            fuente = conexion.execute(
                "SELECT id FROM fuentes_conocimiento WHERE nombre = ?",
                (agente["nombre"],),
            ).fetchone()
            if fuente:
                fuente_id = fuente["id"]
            else:
                cursor = conexion.execute(
                    "INSERT INTO fuentes_conocimiento (nombre, contenido) VALUES (?, ?)",
                    (agente["nombre"], agente["conocimiento"]),
                )
                fuente_id = cursor.lastrowid
            conexion.execute(
                "INSERT INTO agente_fuentes (agente_id, fuente_id) VALUES (?, ?)",
                (agente["id"], fuente_id),
            )
            conexion.execute(
                "UPDATE agentes SET conocimiento = '' WHERE id = ?",
                (agente["id"],),
            )


# ----------------------------------------------------------------------
# Roles e Identidades (Gestión en Base de Datos)
# ----------------------------------------------------------------------


def listar_roles():
    """Devuelve todos los roles con el conteo de agentes que los utilizan."""
    with _conexion() as conexion:
        filas = conexion.execute(
            """SELECT r.id, r.clave, r.nombre, r.descripcion, r.prompt, r.es_sistema,
                      r.creado_en, r.actualizado_en,
                      COUNT(a.id) AS total_agentes
               FROM roles r
               LEFT JOIN agentes a ON a.identidad_clave = r.clave
               GROUP BY r.id
               ORDER BY r.es_sistema DESC, r.nombre ASC"""
        ).fetchall()
        return [dict(f) for f in filas]


def obtener_rol(rol_id):
    """Devuelve un rol por su ID con total de agentes asociados."""
    with _conexion() as conexion:
        fila = conexion.execute(
            """SELECT r.*, COUNT(a.id) AS total_agentes
               FROM roles r
               LEFT JOIN agentes a ON a.identidad_clave = r.clave
               WHERE r.id = ?
               GROUP BY r.id""",
            (rol_id,),
        ).fetchone()
        return dict(fila) if fila else None


def obtener_rol_por_clave(clave):
    """Devuelve un rol por su clave única."""
    with _conexion() as conexion:
        fila = conexion.execute(
            "SELECT * FROM roles WHERE clave = ?", (clave,)
        ).fetchone()
        return dict(fila) if fila else None


def crear_rol(clave, nombre, descripcion="", prompt="", es_sistema=0):
    """Crea un nuevo rol en la base de datos."""
    clave = clave.strip().lower()
    nombre = nombre.strip()
    descripcion = descripcion.strip()
    prompt = prompt.strip()
    if not clave or not nombre:
        raise ValueError("La clave y el nombre del rol son obligatorios.")
    if not prompt:
        raise ValueError("El prompt de rol no puede estar vacío.")

    with _conexion() as conexion:
        existe = conexion.execute("SELECT 1 FROM roles WHERE clave = ?", (clave,)).fetchone()
        if existe:
            raise ValueError(f"Ya existe un rol con la clave '{clave}'.")
        cursor = conexion.execute(
            """INSERT INTO roles (clave, nombre, descripcion, prompt, es_sistema)
               VALUES (?, ?, ?, ?, ?)""",
            (clave, nombre, descripcion, prompt, es_sistema),
        )
        return cursor.lastrowid


def actualizar_rol(rol_id, clave, nombre, descripcion="", prompt=""):
    """Actualiza la clave, nombre, descripción y prompt de un rol."""
    clave = clave.strip().lower()
    nombre = nombre.strip()
    descripcion = descripcion.strip()
    prompt = prompt.strip()
    if not clave or not nombre:
        raise ValueError("La clave y el nombre del rol son obligatorios.")
    if not prompt:
        raise ValueError("El prompt de rol no puede estar vacío.")

    with _conexion() as conexion:
        rol_actual = conexion.execute("SELECT clave FROM roles WHERE id = ?", (rol_id,)).fetchone()
        if not rol_actual:
            raise ValueError("El rol especificado no existe.")
        clave_anterior = rol_actual["clave"]

        duplicado = conexion.execute(
            "SELECT 1 FROM roles WHERE clave = ? AND id != ?", (clave, rol_id)
        ).fetchone()
        if duplicado:
            raise ValueError(f"Ya existe otro rol con la clave '{clave}'.")

        conexion.execute(
            """UPDATE roles
               SET clave = ?, nombre = ?, descripcion = ?, prompt = ?,
                   actualizado_en = datetime('now', 'localtime')
               WHERE id = ?""",
            (clave, nombre, descripcion, prompt, rol_id),
        )

        if clave != clave_anterior:
            conexion.execute(
                "UPDATE agentes SET identidad_clave = ? WHERE identidad_clave = ?",
                (clave, clave_anterior),
            )


def eliminar_rol(rol_id):
    """Elimina un rol y reasigna los agentes al rol básico por defecto."""
    with _conexion() as conexion:
        rol = conexion.execute("SELECT clave, es_sistema FROM roles WHERE id = ?", (rol_id,)).fetchone()
        if not rol:
            return False
        clave = rol["clave"]
        conexion.execute(
            "UPDATE agentes SET identidad_clave = 'basic' WHERE identidad_clave = ?",
            (clave,),
        )
        conexion.execute("DELETE FROM roles WHERE id = ?", (rol_id,))
        return True


# ----------------------------------------------------------------------
# Estadísticas para el Dashboard Administrativo
# ----------------------------------------------------------------------


def obtener_estadisticas_dashboard():
    """Devuelve métricas y listados consolidados para el dashboard administrativo."""
    with _conexion() as conexion:
        total_agentes = conexion.execute("SELECT COUNT(*) AS total FROM agentes").fetchone()["total"]
        total_fuentes = conexion.execute("SELECT COUNT(*) AS total FROM fuentes_conocimiento").fetchone()["total"]
        total_roles = conexion.execute("SELECT COUNT(*) AS total FROM roles").fetchone()["total"]
        total_usuarios = conexion.execute("SELECT COUNT(*) AS total FROM usuarios").fetchone()["total"]
        total_sesiones = conexion.execute("SELECT COUNT(*) AS total FROM sesiones_chat").fetchone()["total"]
        total_mensajes = conexion.execute("SELECT COUNT(*) AS total FROM conversaciones").fetchone()["total"]

        agentes_stats = conexion.execute(
            """SELECT a.id, a.nombre, a.perfil, a.identidad_clave, a.identidad_custom,
                      a.avatar_url, a.memoria, a.creado_en,
                      COUNT(DISTINCT s.id) AS total_sesiones,
                      COUNT(c.id) AS total_mensajes,
                      COUNT(DISTINCT af.fuente_id) AS total_fuentes
               FROM agentes a
               LEFT JOIN sesiones_chat s ON s.agente_id = a.id
               LEFT JOIN conversaciones c ON c.agente_id = a.id
               LEFT JOIN agente_fuentes af ON af.agente_id = a.id
               GROUP BY a.id
               ORDER BY a.nombre"""
        ).fetchall()

        ultimas_sesiones = conexion.execute(
            """SELECT s.id, s.titulo, s.creado_en, s.actualizado_en,
                      a.nombre AS agente_nombre,
                      COUNT(c.id) AS total_mensajes
               FROM sesiones_chat s
               JOIN agentes a ON a.id = s.agente_id
               LEFT JOIN conversaciones c ON c.sesion_id = s.id
               GROUP BY s.id
               ORDER BY s.actualizado_en DESC
               LIMIT 12"""
        ).fetchall()

        return {
            "total_agentes": total_agentes,
            "total_fuentes": total_fuentes,
            "total_roles": total_roles,
            "total_usuarios": total_usuarios,
            "total_sesiones": total_sesiones,
            "total_mensajes": total_mensajes,
            "agentes": [dict(a) for a in agentes_stats],
            "ultimas_sesiones": [dict(s) for s in ultimas_sesiones],
            "todas_las_sesiones": listar_todas_las_sesiones(),
            "roles": listar_roles(),
            "usuarios": listar_usuarios(),
        }


def listar_todas_las_sesiones(nombre_agente=None):
    """Devuelve todas las sesiones de chat con información del agente y mensajes."""
    with _conexion() as conexion:
        if nombre_agente:
            filas = conexion.execute(
                """SELECT s.id, s.titulo, s.creado_en, s.actualizado_en,
                          a.nombre AS agente_nombre,
                          COUNT(c.id) AS total_mensajes,
                          (SELECT mensaje FROM conversaciones WHERE sesion_id = s.id ORDER BY id DESC LIMIT 1) AS ultimo_mensaje
                   FROM sesiones_chat s
                   JOIN agentes a ON a.id = s.agente_id
                   LEFT JOIN conversaciones c ON c.sesion_id = s.id
                   WHERE a.nombre = ?
                   GROUP BY s.id
                   ORDER BY s.actualizado_en DESC, s.id DESC""",
                (nombre_agente,),
            ).fetchall()
        else:
            filas = conexion.execute(
                """SELECT s.id, s.titulo, s.creado_en, s.actualizado_en,
                          a.nombre AS agente_nombre,
                          COUNT(c.id) AS total_mensajes,
                          (SELECT mensaje FROM conversaciones WHERE sesion_id = s.id ORDER BY id DESC LIMIT 1) AS ultimo_mensaje
                   FROM sesiones_chat s
                   JOIN agentes a ON a.id = s.agente_id
                   LEFT JOIN conversaciones c ON c.sesion_id = s.id
                   GROUP BY s.id
                   ORDER BY s.actualizado_en DESC, s.id DESC"""
            ).fetchall()
        return [dict(f) for f in filas]


# ----------------------------------------------------------------------
# Clase AgenteDB
# ----------------------------------------------------------------------


class AgenteDB:
    """Agente que gestiona sus datos, memoria y conversaciones en SQLite con llamadas a DeepSeek."""

    def __init__(self, nombre):
        load_dotenv()
        self.nombre = nombre
        self.perfil = ""
        self.conocimiento = ""
        self.identidad = ""
        self.identidad_custom = ""
        self.memoria = ""
        self.client = self._crear_cliente()
        self.cargar_perfil()
        self.cargar_conocimiento()
        self.cargar_identidad()
        self.cargar_memoria()

    def _crear_cliente(self):
        """Crea el cliente de DeepSeek usando la API Key del entorno."""
        api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        if not api_key or api_key == "tu_api_key":
            raise ValueError(
                "No se encontró una API Key válida de DeepSeek. "
                "Configura tu DEEPSEEK_API_KEY en el archivo .env."
            )
        return openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
        )

    def _enviar(self, mensajes, max_tokens=400):
        """Realiza una llamada a la API de DeepSeek con límite optimizado de tokens.

        Rangos recomendados de max_tokens:
        - Respuesta ultra corta: 100–150
        - Chat normal (por defecto): 250–400
        - Explicación técnica: 500–800
        """
        try:
            respuesta = self.client.chat.completions.create(
                model=MODELO,
                messages=mensajes,
                max_tokens=max_tokens if max_tokens else 400,
            )
        except openai.AuthenticationError as error:
            raise RuntimeError(
                "La API Key de DeepSeek es inválida. Verifica tu .env."
            ) from error
        except openai.APIConnectionError as error:
            raise RuntimeError(
                "No se pudo conectar con DeepSeek. Revisa tu conexión a internet."
            ) from error
        except openai.RateLimitError as error:
            raise RuntimeError(
                "Límite de solicitudes alcanzado. Espera unos segundos e intenta de nuevo."
            ) from error
        except openai.APIError as error:
            raise RuntimeError(f"Error de la API de DeepSeek: {error}") from error
        except Exception as error:
            raise RuntimeError(f"Error inesperado al contactar a DeepSeek: {error}") from error

        contenido = respuesta.choices[0].message.content
        return contenido.strip() if contenido else ""

    def obtener_nombre(self):
        """Extrae el nombre legible de la persona desde el perfil del agente."""
        lineas = self.perfil.splitlines()
        for indice, linea in enumerate(lineas):
            if linea.strip().startswith("NOMBRE:"):
                for siguiente in lineas[indice + 1:]:
                    if siguiente.strip():
                        return siguiente.strip()
        return self.nombre

    def construir_prompt(self):
        """Construye el System Prompt completo procesando rol, perfil, conocimientos y memoria."""
        _, _, prompt_rol = self.info_identidad()
        rol = procesar_identidad(prompt_rol, self.obtener_nombre())
        return construir_system_prompt(rol, self.perfil, self.conocimiento, self.memoria)

    def cargar_perfil(self):
        datos = obtener_agente(self.nombre)
        self.perfil = datos["perfil"] if datos else ""

    def cargar_conocimiento(self):
        """Construye el conocimiento desde las bases de conocimiento asociadas."""
        datos = obtener_agente(self.nombre)
        fuentes = obtener_fuentes_agente(self.nombre)
        partes = []
        for fuente in fuentes:
            texto = (fuente.get("contenido") or "").strip()
            if texto:
                nombre_fuente = fuente.get("nombre", "").strip()
                if nombre_fuente:
                    partes.append(f"[{nombre_fuente}]\n{texto}")
                else:
                    partes.append(texto)
        manual = (datos["conocimiento"] if datos else "").strip()
        if manual:
            partes.append(manual)
        self.conocimiento = "\n\n".join(partes)

    def cargar_identidad(self):
        datos = obtener_agente(self.nombre)
        self.identidad = datos["identidad_clave"] if datos else ""
        self.identidad_custom = datos["identidad_custom"] if datos else ""

    def info_identidad(self):
        """Devuelve (nombre, descripcion, prompt) consultando los roles de la base de datos."""
        if self.identidad_custom:
            return ("Identidad personalizada", "Prompt propio guardado en la base de datos.", self.identidad_custom)
        if self.identidad:
            rol = obtener_rol_por_clave(self.identidad)
            if rol:
                return (rol["nombre"], rol["descripcion"], rol["prompt"])
        rol_defecto = obtener_rol_por_clave("basic")
        if rol_defecto:
            return (rol_defecto["nombre"], rol_defecto["descripcion"], rol_defecto["prompt"])
        return ("Básico", "Agente experto en la base de conocimiento.", "Eres un asistente útil.")

    def cargar_memoria(self):
        datos = obtener_agente(self.nombre)
        self.memoria = datos["memoria"] if datos else ""

    def guardar_conversacion(self, rol, mensaje, sesion_id=None):
        guardar_mensaje(self.nombre, rol, mensaje, sesion_id=sesion_id)

    def obtener_historial(self, cantidad=HISTORIAL_RECIENTE, sesion_id=None):
        return obtener_historial(self.nombre, cantidad, sesion_id=sesion_id)

    def preguntar(self, mensaje, sesion_id=None, max_tokens=400):
        self.guardar_conversacion("user", mensaje, sesion_id=sesion_id)
        historial = self.obtener_historial(sesion_id=sesion_id)

        mensajes = [{"role": "system", "content": self.construir_prompt()}]
        for rol, contenido in historial:
            if contenido:
                mensajes.append({"role": rol, "content": contenido})

        respuesta = self._enviar(mensajes, max_tokens=max_tokens)

        if not respuesta:
            raise RuntimeError("DeepSeek devolvió una respuesta vacía.")

        self.guardar_conversacion("assistant", respuesta, sesion_id=sesion_id)
        return respuesta

    def actualizar_memoria(self, mensaje_usuario, respuesta):
        conversacion = f"Usuario: {mensaje_usuario}\nAgente: {respuesta}"
        prompt = construir_prompt_memoria(self.memoria, conversacion)
        try:
            contenido = self._enviar([{"role": "user", "content": prompt}], max_tokens=150)
        except RuntimeError:
            return []
        if not contenido or SIN_MEMORIA in contenido.upper():
            return []
        agregadas = agregar_memorias(self.nombre, contenido)
        if agregadas:
            self.cargar_memoria()
        return agregadas

    # Alias en inglés dentro de la clase
    ask = preguntar
    update_memory = actualizar_memoria
    build_prompt = construir_prompt
    load_profile = cargar_perfil
    load_knowledge = cargar_conocimiento
    load_identity = cargar_identidad
    load_memory = cargar_memoria
    save_conversation = guardar_conversacion
    get_history = obtener_historial


# ----------------------------------------------------------------------
# Alias en inglés de funciones para compatibilidad bilingüe
# ----------------------------------------------------------------------
AgentDB = AgenteDB
init_db = inicializar
clear_db = vaciar
create_user = crear_usuario
verify_user = verificar_usuario
init_default_admin = inicializar_admin_por_defecto
list_users = listar_usuarios
get_user = obtener_usuario
get_user_by_name = obtener_usuario_por_nombre
update_user = actualizar_usuario
delete_user = eliminar_usuario
list_agents = listar_agentes
agent_exists = existe_agente
create_agent = crear_agente
get_agent = obtener_agente
update_profile = actualizar_perfil
update_avatar = actualizar_avatar
change_identity = cambiar_identidad
update_knowledge = actualizar_conocimiento
clear_memory = borrar_memoria
delete_agent = eliminar_agente
list_sources = listar_fuentes
create_source = crear_fuente
get_source = obtener_fuente
get_source_by_name = obtener_fuente_por_nombre
update_source = actualizar_fuente
delete_source = eliminar_fuente
get_agent_sources = obtener_fuentes_agente
set_agent_sources = establecer_fuentes_agente
list_roles = listar_roles
get_role = obtener_rol
get_role_by_key = obtener_rol_por_clave
create_role = crear_rol
update_role = actualizar_rol
delete_role = eliminar_rol
create_chat_session = crear_sesion_chat
get_or_create_active_session = obtener_o_crear_sesion_activa
get_chat_session = obtener_sesion_chat
rename_chat_session = renombrar_sesion_chat
delete_chat_session = eliminar_sesion_chat
list_agent_sessions = listar_sesiones_agente
list_all_sessions = listar_todas_las_sesiones
get_session_all_messages = obtener_todos_mensajes_sesion
get_dashboard_stats = obtener_estadisticas_dashboard
migrate_legacy_knowledge = migrar_conocimientos_legacy
