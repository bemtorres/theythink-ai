# Resumen de personas

El catálogo `personas.py` define **31 personas**: 3 ejemplos, 8 personajes y 20 perfiles Music Pro.

| Identificador | Nombre | Grupo |
|---|---|---|
| `benjamin` | Benjamin | Ejemplos |
| `elon_musk` | Elon Musk | Ejemplos |
| `albert_einstein` | Albert Einstein | Ejemplos |
| `el_principito` | El Principito (Le Petit Prince) | Personajes |
| `sherlock_holmes` | Sherlock Holmes | Personajes |
| `don_quijote` | Don Quijote de la Mancha (Alonso Quijano el Bueno) | Personajes |
| `socrates` | Sócrates de Atenas (470 a.C. – 399 a.C.) | Personajes |
| `nikola_tesla` | Nikola Tesla (1856 – 1943) | Personajes |
| `hincha_colocolo` | El Albo Adicto (Hincha de Colo-Colo) | Personajes |
| `hincha_udechile` | El Bullanguero (Hincha de la U) | Personajes |
| `el_flaite_chileno` | El Jordan / El Bryan (Flaite Vío) | Personajes |
| `tienda_jefe` | Andrea Quiroga | Music Pro |
| `tienda_trabajador` | María López | Music Pro |
| `sucursal_jefe` | Diego Fuentes | Music Pro |
| `sucursal_trabajador` | Jorge Rojas | Music Pro |
| `bodega_jefe` | Roberto Salinas | Music Pro |
| `bodega_trabajador` | Luis Paredes | Music Pro |
| `tarjetas_jefe` | Fernando Ríos | Music Pro |
| `tarjetas_trabajador` | Paula Vega | Music Pro |
| `tienda_cliente_1` | Camila Torres | Music Pro |
| `tienda_cliente_2` | Sebastián Herrera | Music Pro |
| `sucursal_cliente_1` | Valentina Soto | Music Pro |
| `sucursal_cliente_2` | Andrés Molina | Music Pro |
| `bodega_cliente_1` | Patricia Leiva | Music Pro |
| `bodega_cliente_2` | Rodrigo Campos | Music Pro |
| `tarjetas_cliente_1` | Daniela Fuentes | Music Pro |
| `tarjetas_cliente_2` | Felipe Araya | Music Pro |
| `tienda_trabajador_contento` | Javiera Muñoz | Music Pro |
| `sucursal_trabajador_contento` | Tomás Aguilera | Music Pro |
| `bodega_trabajador_contento` | Carolina Espinoza | Music Pro |
| `tarjetas_trabajador_contento` | Nicolás Vera | Music Pro |

## Roles

Ejemplos: Benjamin (desarrollo e IA), Elon Musk (tecnología y emprendimiento), Albert Einstein (física).

Personajes: El Principito (reflexión y vínculos), Sherlock Holmes (deducción), Don Quijote (caballería y justicia), Sócrates (filosofía), Nikola Tesla (electricidad e invención), hinchas de Colo-Colo y Universidad de Chile (fútbol), El Jordan / El Bryan (personaje de cultura urbana chilena).

Music Pro tiene cuatro proyectos: tienda en línea, sucursal física, bodega y pagos (BeatPay). Cada uno tiene un jefe experto, millonario y patrocinador de mejoras; un trabajador experto agotado por fallos del sistema; otro trabajador feliz con su trabajo, en un puesto distinto; y dos clientes amantes del servicio que quieren mejorarlo.

| Proyecto | Jefe | Trabajador | Presupuesto ficticio (CLP) | Plazo |
|---|---|---|---:|---|
| Tienda en línea | Andrea Quiroga | María López | $120.000.000 | 6 meses |
| Sucursal física | Diego Fuentes | Jorge Rojas | $85.000.000 | 5 meses |
| Gestión de bodega | Roberto Salinas | Luis Paredes | $160.000.000 | 8 meses |
| Pagos y BeatPay | Fernando Ríos | Paula Vega | $200.000.000 | 9 meses |

Los presupuestos son parte de la simulación, incluyen contingencia y se mantienen estables entre respuestas. Cada perfil contiene problemas actuales, un caso cotidiano, mejoras y criterios de aceptación. El jefe negocia alcance y aprueba prioridades; el trabajador propone mejoras y valida los flujos sin comprometer fondos.

## Una sola carga inicial

El estudiante ejecuta `install.bat` y el instalador llama a `python seed.py`: carga las 31 personas, sus conocimientos y las conversaciones de ejemplo, incluidos los 20 perfiles de Music Pro. No necesita ejecutar otro seeder ni comandos de actualización.

En una instalación manual, basta con `python seed.py` y luego `python app.py`. Las definiciones están en `personas.py` y toda la carga está en `seed.py`. No existe un seeder separado de empresa. Volver a ejecutar la carga agrega los faltantes sin duplicar personas ni conversaciones.

## Alcance y correcciones

Las carpetas `__old__/agents/` contienen versiones antiguas de Benjamin, Elon Musk y Albert Einstein: no son personas adicionales. Sus historiales y memorias no se importan automáticamente. Las personas creadas desde la interfaz viven en SQLite y no están incluidas en este inventario del código. Los usuarios de acceso y plantillas de identidad tampoco son personas precargadas.

Antes SQLite creaba ocho personajes durante la inicialización, haciendo que el seeder saliera antes de cargar el resto. El modo `--force` los eliminaba sin reponerlos. Se retiró esa creación implícita de la capa de datos y se centralizó la carga en `seed.py`, con todas las definiciones en `personas.py`.

## Clientes y trabajadores entusiastas

Los clientes narran experiencias distintas, lo que valoran, los problemas que vivieron, sus propuestas y cómo comprobarían una mejora. Los nuevos trabajadores disfrutan su trabajo, colaboran con su equipo y detectan fallos desde un puesto diferente al del trabajador agotado. Todos tienen una conversación inicial propia y se cargan con el mismo seeder.

| Proyecto | Persona | Rol |
|---|---|---|
| Tienda en línea | Camila Torres | Guitarrista y compradora habitual desde el móvil |
| Tienda en línea | Sebastián Herrera | Productor musical que compra equipos de audio para su estudio |
| Sucursal física | Valentina Soto | Estudiante de violín y visitante frecuente de la sucursal |
| Sucursal física | Andrés Molina | Baterista que retira compras web en el local |
| Gestión de bodega | Patricia Leiva | Directora de una academia de música que recibe pedidos por volumen |
| Gestión de bodega | Rodrigo Campos | Dueño de una sala de ensayo que compra amplificadores y repuestos |
| Pagos y BeatPay | Daniela Fuentes | Aficionada a conciertos y usuaria habitual de BeatPay |
| Pagos y BeatPay | Felipe Araya | DJ que usa los medios de pago de Music Pro para renovar su equipo |
| Tienda en línea | Javiera Muñoz | Especialista de Catálogo y Contenido Digital |
| Sucursal física | Tomás Aguilera | Asesor de Instrumentos y Coordinador de Demostraciones |
| Gestión de bodega | Carolina Espinoza | Inspectora de Recepción y Control de Calidad |
| Pagos y BeatPay | Nicolás Vera | Especialista de Integraciones y Monitoreo de Pagos |

## Imágenes de todas las personas

Las 31 personas del catálogo tienen un avatar individual local en `static/img/personas/`: 20 de Music Pro y 11 de ejemplos y personajes. El catálogo asigna su `avatar_url` y el seeder lo incluye automáticamente en la instalación inicial. No se descargan imágenes externas al instalar. Consulta la [galería completa](static/img/personas/README.md) y la [galería Music Pro](static/img/personas/music_pro/README.md). Los prompts y la herramienta utilizada están registrados junto a las imágenes en `prompts.json`.
