# Cómo crear nuevas personalidades

Una personalidad es un agente con un perfil, una forma de responder y conocimientos propios. Por ejemplo, dos agentes pueden conocer la misma bodega, pero uno responder como gerente y otro como operario.

## Qué define a una personalidad

| Campo | Para qué sirve | Ejemplo |
|---|---|---|
| `nombre` | Identificador único del agente. Usa minúsculas y guiones bajos. | `sucursal_supervisora` |
| `perfil` | Nombre de la persona, profesión, experiencia, carácter y objetivos. | Camila Torres, supervisora de sucursal |
| `conocimiento` | Información que necesita para responder sobre su trabajo. | Procedimientos de apertura, stock y devoluciones |
| `identidad_clave` | Clave de un rol existente. | `basic` |
| `identidad_custom` | Instrucciones personalizadas sobre cómo debe responder. | Tono cordial y explicaciones prácticas |

Para un estilo propio, utiliza `identidad_custom` y deja fuera `identidad_clave`. Para reutilizar un rol, utiliza su clave. No necesitas entrenar un modelo: el sistema incorpora estas instrucciones al contexto de la conversación.

## Opción 1: crear desde la aplicación

1. Inicia la aplicación con `python app.py` e inicia sesión.
2. En el dashboard, pulsa **Nuevo Agente**.
3. Escribe un identificador único, completa el perfil y selecciona el rol o las instrucciones personalizadas.
4. Asocia las bases de conocimiento que necesita y guarda el agente.
5. Abre una conversación para comprobar cómo responde.

## Opción 2: agregar una personalidad a Music Pro

Los perfiles de Music Pro se definen en `empresa.py`, dentro de la lista `PERFILES_EMPRESA`. El archivo `musicpro.py` carga esa lista; no es necesario duplicar allí los perfiles.

Agrega este diccionario antes del cierre `]` de `PERFILES_EMPRESA`. Separa cada diccionario del siguiente con una coma:

```python
    {
        "nombre": "sucursal_supervisora",
        "perfil": """NOMBRE:
Camila Torres

PROFESIÓN:
Supervisora de Sucursal de Music Pro.

EXPERIENCIA:
6 años coordinando ventas, reposición y atención al cliente.

PERSONALIDAD:
Organizada, cordial, resolutiva y exigente con los plazos.

FORMA DE COMUNICARSE:
Explica con ejemplos prácticos y propone pasos concretos.

OBJETIVOS:
Mantener el stock ordenado y resolver consultas de los clientes.""",
        "conocimiento": """Perfil de demostración de una sucursal de Music Pro.
Para revisar una diferencia de stock se compara el conteo físico
con los movimientos registrados de recepción, venta y devolución.
Las políticas comerciales deben cargarse desde documentación aprobada.""",
        "identidad_custom": (
            "Interpreta a Camila Torres, supervisora de sucursal de Music Pro. "
            "Responde con cordialidad y pasos concretos. "
            "Si desconoces una política, pide los antecedentes necesarios. "
            "No inventes stock, precios ni estados de pedidos."
        ),
    },
```

Este ejemplo contiene información de demostración: reemplázala por los procedimientos reales que quieras que conozca el agente. Escribir que conoce el inventario no lo conecta automáticamente a un sistema de stock en tiempo real.

Desde la carpeta del proyecto, activa el entorno virtual y ejecuta el seeder:

```powershell
.\venv\Scripts\Activate.ps1
python musicpro.py
```

El comando crea los perfiles que faltan. Puedes repetirlo sin duplicarlos. Si modificaste un perfil que ya estaba cargado, ejecuta:

```powershell
python musicpro.py --force
```

`--force` actualiza el perfil, conocimiento e identidad de todos los perfiles definidos en `PERFILES_EMPRESA`. Conserva las memorias, las conversaciones y los agentes ajenos a esa lista. Cambiar el texto de `empresa.py` por sí solo no actualiza un agente ya guardado: debes volver a ejecutar el seeder con esta opción.

## Opción 3: crear un seeder independiente

Para personalidades que no pertenecen a Music Pro, crea un archivo como `seed_personalidades.py` en la raíz del proyecto:

```python
import basededatos as bd


def main():
    bd.inicializar()
    nombre = "mentora_programacion"

    if bd.existe_agente(nombre):
        print(f"El agente {nombre} ya existe; no se modificó.")
        return

    bd.crear_agente(
        nombre=nombre,
        perfil="""NOMBRE:
Elena Soto
PROFESIÓN:
Mentora de programación.
PERSONALIDAD:
Paciente, curiosa y didáctica.
FORMA DE COMUNICARSE:
Explica paso a paso y usa ejemplos pequeños.""",
        conocimiento="Python utiliza indentación para delimitar bloques de código.",
        identidad_custom=(
            "Interpreta a Elena Soto, mentora de programación. "
            "Adapta tus explicaciones al nivel del usuario y comprueba "
            "su comprensión con una pregunta breve."
        ),
    )
    bd.migrar_conocimientos_legacy()
    print(f"Agente creado: {nombre}")


if __name__ == "__main__":
    main()
```

Ejecútalo desde la raíz del proyecto para usar el archivo `agentes.db` de la aplicación:

```powershell
python seed_personalidades.py
```

`bd.inicializar()` prepara la base y también carga los personajes canónicos del sistema que falten. `bd.crear_agente()` crea el agente y su primera sesión de chat. La migración de conocimientos convierte el conocimiento del agente en una fuente asociada para que la aplicación pueda utilizarlo.

## Comprobar el resultado

### Entrevistas para desarrollar los módulos de Music Pro

Los jefes están preparados para proponer funciones, priorizar una primera versión,
explicar integraciones y definir criterios de aceptación. Los trabajadores describen
problemas cotidianos del sistema, sus consecuencias y las mejoras que necesitan.
Cada área tiene un escenario de problemas y propuestas en `CONTEXTO_DESARROLLO`
de `empresa.py`. Son situaciones simuladas para levantar requisitos; reemplázalas
por hallazgos de entrevistas reales cuando estén disponibles.

Ejemplos de preguntas:

- Al jefe: «¿Qué propones para la primera versión de tu módulo y por qué?»
- Al jefe: «¿Cómo comprobaríamos que esa función cumple lo que necesitas?»
- Al trabajador: «¿Qué es lo peor del sistema actual durante tu turno?»
- Al trabajador: «Cuéntame cómo haces esa tarea hoy y cómo te gustaría hacerla».

Abre el agente y prueba preguntas como estas:

- «¿Cómo te llamas y cuál es tu trabajo?»
- «¿Cómo resolverías una diferencia de inventario?»
- «¿Cuántos productos tenemos ahora mismo?»

Comprueba que mantiene el carácter definido, utiliza sus conocimientos y no inventa datos operativos que no recibió. Si el tono no es el esperado, ajusta `FORMA DE COMUNICARSE` y `identidad_custom`. Si le falta información, amplía sus bases de conocimiento.

## Archivos de referencia

### Retratos de los agentes

Los retratos generados se guardan en `static/avatars/generated/`, uno por agente.
El archivo `manifest.json` de esa carpeta relaciona cada agente con su imagen y
conserva el prompt completo utilizado en la herramienta integrada de generación.
Los personajes ficticios tienen rostros inventados; los personajes históricos y
literarios tienen interpretaciones visuales de sus perfiles.

Para volver a asignar las imágenes a los agentes existentes después de recrear
la base de datos, ejecuta:

```powershell
python seed_avatares.py
```

Este comando cambia únicamente el avatar de los agentes incluidos en el manifiesto.

### Grupo MusicPro y clientes

`python musicpro.py` crea el grupo **MusicPro** y asigna sus 16 agentes:
ocho empleados y ocho clientes. Cada área tiene un cliente satisfecho y otro
que tuvo problemas. Los clientes son personajes ficticios para entrevistas de requisitos.

| Área | Cliente satisfecho | Cliente con problemas |
|---|---|---|
| Bodega | Valentina Pérez | Cristóbal Muñoz |
| Sucursal / tienda | Daniela Herrera | Matías Silva |
| Tarjetas | Francisca Morales | Sebastián Castro |
| Transporte | Camila Reyes | Nicolás Soto |

En el dashboard, **Grupos de agentes** permite crear grupos, añadir agentes y
filtrar el listado. Un agente puede pertenecer a varios grupos. El catálogo de
inicio también permite seleccionar MusicPro. Los grupos organizan agentes;
no crean automáticamente una conversación colectiva ni comparten sus memorias.

Para cambiar las experiencias de los clientes, edita `CLIENTES_MUSICPRO` en
`empresa.py` y ejecuta `python musicpro.py --force`.

- `musicpro.py`: comando para cargar o actualizar los perfiles de Music Pro.
- `empresa.py`: perfiles y conocimientos de las áreas de Music Pro.
- `basededatos.py`: funciones para crear, consultar y actualizar agentes.
- `identidades.py`: definiciones de los roles iniciales.
- `prompt.py`: combina rol, perfil, conocimientos y memoria en las instrucciones del modelo.

Evita usar `python seed.py --force` para agregar una personalidad: ese comando vacía la base antes de volver a cargar los datos generales. Para Music Pro utiliza `python musicpro.py` o `python musicpro.py --force`.
