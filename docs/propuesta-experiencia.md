# THEYTHINK AI — propuesta de experiencia

## Dirección

Convertir el inicio en un espacio para descubrir personajes y comenzar conversaciones.
La referencia pública es https://character.ai/. Su página depende de JavaScript y
no entregó contenido legible en esta revisión; esta propuesta no afirma reproducir
sus fuentes, medidas o interfaz actual. Usa patrones de descubrimiento y chat de
personajes, adaptados a los agentes y funciones existentes de THEYTHINK AI.

Prototipo revisable: `/static/preview/explorar.html`. Incluye los 24 agentes de la
base actual, sus retratos, búsqueda, filtros combinables, favoritos locales y un
panel de personaje con preguntas sugeridas. Es una vista de propuesta, no reemplaza
el inicio. Los enlaces de conversación llevan al chat existente y requieren sesión.

## Hallazgos del proyecto

| Prioridad | Evidencia | Cambio propuesto |
|---|---|---|
| Alta | `templates/index.html`: `catalogo-agentes` lleva `hidden` y queda después de características y pasos. | Mostrar personajes desde el primer viewport; trasladar la explicación de la plataforma a una sección secundaria. |
| Alta | Las tarjetas muestran `ag.nombre` y `ag.perfil.splitlines()[0]`, normalmente «NOMBRE:». | Nombre visible, función y descripción breve; conservar el identificador para rutas y persistencia. |
| Alta | Hay 24 avatares propios y un grupo MusicPro con 16 miembros. | Aprovechar retratos grandes, categorías y colección MusicPro como puntos de entrada. |
| Alta | El chat ya tiene hilos, memoria, streaming y selector de agentes. | Refinar su jerarquía visual sin rehacer la lógica: personaje arriba, conversación al centro, información en panel lateral. |
| Media | El listado de inicio carga fuentes, roles y sesiones por cada agente mediante `load_agent_data()`. | Crear una consulta resumida de catálogo y cargar el detalle al abrir el personaje. |
| Media | Imágenes PNG completas se usan también como miniaturas. | Conservar originales y preparar versiones WebP y tamaños de catálogo; aplicar lazy loading fuera de la primera fila. |
| Media | Estilos Google multicolor, luces difusas y controles administrativos dominan la presentación. | Superficies neutras, acento azul existente y administración en navegación secundaria. |
| Alta antes de publicar | Varias rutas de creación y edición no usan `require_login`; hay redirecciones a `dashboard_view` aunque el endpoint declarado es `pagina_dashboard`. | Revisar autenticación, autorización por rol y destinos de acceso como una etapa funcional separada, con pruebas. |

## Experiencia propuesta

### Explorar

Barra lateral con Explorar, Favoritos y colecciones. Buscador por nombre, función y
tema. Filtros por personajes, equipo de MusicPro y clientes; se combinan con grupo
y favoritos. Cada tarjeta tiene retrato, nombre, función y una descripción útil.
No se muestran métricas de popularidad, usuarios conectados o actividad inventadas.

### Conocer al personaje

Al pulsar una tarjeta se abre un panel con su identidad, grupo, descripción y tres
formas de iniciar la conversación. El botón «Abrir conversación» usa la ruta
existente. Las preguntas se pueden copiar: el prototipo no las envía a un modelo
ni inventa respuestas. Se identifica a los clientes de MusicPro como simulaciones.

### Conversar

La siguiente etapa adapta `templates/chat.html`: hilo de lectura centrado, menos
controles visibles a la vez, campo de mensaje amplio y panel de información bajo
demanda. Conservar sesiones, historial, memoria, fuentes, streaming y edición.
En móvil, la navegación se abre bajo demanda y el campo de mensaje queda accesible.

### MusicPro

Colección propia con jefes, trabajadores y clientes. Los filtros permiten elegir
a quién entrevistar según el objetivo: propuestas de módulos, problemas operativos
o experiencia del cliente. Las ocho experiencias de clientes son ficticias.
Una conversación grupal real sería una función posterior con selección de
participantes, turnos y reglas explícitas de memoria; agrupar agentes no la crea.

## Sistema visual propuesto

- Género: moderno y sobrio, con contenido protagonista.
- Estructura: barra lateral persistente y catálogo; panel de detalle superpuesto.
- Tipografía: Inter, ya disponible en el proyecto, con alternativa de sistema.
- Color: neutros cálidos en claro, carbón en oscuro y azul de la marca como acento.
- Retratos: originales generados, proporción consistente y rostros legibles.
- Interacción: foco visible, filtros con estado, vacío con acción de restablecer,
  teclado y cierre con Escape; movimiento breve con soporte de reducción.
- Responsive: una columna estrecha, dos en tablet y tres o cuatro en escritorio.

## Alcance de implementación tras revisar el prototipo

1. `templates/index.html`, `static/js/index.js` y un nuevo stylesheet de catálogo:
   integrar el explorador con datos del servidor y mantener los enlaces existentes.
2. `app.py` y `basededatos.py`: resumen eficiente de catálogo, metadatos de
   presentación y favoritos persistentes por usuario si se requieren entre dispositivos.
3. `templates/chat.html` y estilos acotados: mejorar lectura, perfil y navegación móvil.
4. `templates/dashboard.html`: editar título visible, descripción, preguntas y grupos.
5. Revisar permisos y acceso antes de exponer la aplicación fuera del entorno local.

No se propone cambiar de Flask a otro framework. La base SQLite, rutas y agentes
existentes permiten avanzar por etapas. No hay archivos de producción eliminados.

## Criterios de aceptación

- El catálogo es visible al abrir la aplicación y muestra nombres de personas.
- Búsqueda sin distinguir tildes; filtros combinables y estado vacío recuperable.
- MusicPro muestra 16 miembros: ocho empleados y ocho clientes.
- Favoritos conservados al recargar este navegador, sin afectar el historial.
- Navegación por teclado, diálogo con foco controlado y cierre con Escape.
- Sin desbordamiento horizontal a 320, 375, 414 y 768 píxeles.
- El cambio no envía mensajes automáticamente ni sustituye memorias o perfiles.
- Mantener pruebas de rutas, permisos y conversaciones al integrar la propuesta.

## Verificación del prototipo

Se comprobó en navegador: carga de 24 tarjetas, filtro de ocho clientes,
búsqueda «socrates» que encuentra «Sócrates», favoritos conservados tras recargar,
apertura de ficha y cierre con Escape, y cambio entre tema claro y oscuro.
Los cuatro marcos de prueba (320, 375, 414 y 768 px) no presentan desbordamiento
horizontal. Se corrigió durante la revisión el encuadre del bloque MusicPro en móvil.
Las capturas `explorar-preview.png` y `explorar-dark-preview.png` documentan la propuesta.
