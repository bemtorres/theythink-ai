# Experiencia integrada

La apariencia aprobada está integrada en `/`. El prototipo original sigue disponible
en `/static/preview/explorar.html` como referencia y el inicio anterior está guardado
en `templates/index_legacy.html`.

## Catálogo

- Consulta los agentes y grupos actuales de SQLite; no depende del archivo del prototipo.
- Muestra nombres legibles, retratos, función y descripción breve.
- Busca sin distinguir mayúsculas ni tildes; combina categoría, grupo y favoritos.
- Los grupos se crean y asignan en el dashboard; aparecen en escritorio y móvil.
- Los favoritos se guardan en este navegador con una clave distinta por usuario;
  no se sincronizan entre dispositivos.
- Las tarjetas abren una ficha con preguntas para copiar y un enlace al chat.
- Si falta un retrato o falla su carga, muestra el logo del proyecto.
- El catálogo no descarga memorias, historiales ni listas de fuentes por personaje.

## Chat y administración

El chat utiliza el retrato y la presentación del agente al iniciar una sesión vacía.
Las sugerencias rellenan el campo de mensaje y requieren pulsar Enviar. El historial,
memoria, fuentes, Markdown y streaming conservan sus flujos existentes. El lateral
se oculta inicialmente en móvil y puede abrirse desde su botón. Las burbujas y el
campo de escritura usan superficies neutras. Acceso y dashboard reciben los tokens
tipográficos y de superficie del mismo sistema.

Se corrigieron los destinos de login que apuntaban a un endpoint inexistente del
dashboard. No se ha cambiado el modelo de permisos del proyecto.

## Mantener la presentación

`catalogo.py` interpreta el perfil del agente y construye los campos públicos.
`catalogo_metadata.json` contiene textos breves, categorías y preguntas de los
personajes iniciales. Un agente nuevo recibe valores derivados de su propio perfil.
Si escribes una sección `DESCRIPCIÓN:` en el perfil, se utiliza como descripción.
Los textos de presentación no cambian la identidad ni las instrucciones del modelo.

Los agentes iniciales reutilizan sus imágenes locales al sembrarse. Para restaurar
las asignaciones en una base existente: `python seed_avatares.py`.

## Verificación

```powershell
python -m unittest discover -s tests -v
node --check static/js/explorar.js
node --check static/js/chat.js
```

Las pruebas usan una base temporal: cubren consulta pública sin memorias, grupos,
agentes nuevos sin perfil, acceso al chat, dashboard, canales existentes y retratos
de los seeders. No consumen la API del modelo. La página
`/static/preview/responsive-live.html` permite revisar el inicio a 320, 375, 414 y 768 px.
