# THEYTHINK AI — sistema visual

Diseño aprobado a partir del explorador de personajes. Aplicar este sistema a las
vistas del producto; ampliar los tokens cuando haga falta, sin cambiar por página.

- Género: moderno y sobrio; personajes y conversación como contenido principal.
- Estructura: explorador con barra lateral, retratos y panel de perfil; chat con
  historial lateral, lectura centrada y controles secundarios bajo demanda.
- Tipografía: Inter para títulos y cuerpo, alternativa system-ui; títulos rectos.
- Superficies: fondo cálido `#faf9f7`, panel `#ffffff`, lateral `#f1f0ed`;
  oscuro carbón `#18191c`, panel `#232428`, lateral `#141518`.
- Texto: `#202126` en claro y `#f2f1ef` en oscuro; acento azul de la marca.
- Tokens: `static/css/explorar.css` para el catálogo, `static/css/experiencia.css`
  para adaptar las vistas Jinja existentes. Mantener las funciones y rutas.
- Controles: foco visible, botones sin saltos de línea, radios moderados, estados
  vacíos recuperables y mensajes de error claros. Favoritos locales por usuario.
- Movimiento: transiciones cortas, sin animaciones decorativas; respetar reduced-motion.
- Responsive: verificar 320, 375, 414, 768 px y escritorio; evitar overflow horizontal.
- Contenido: nombres legibles, función y descripción breve. No inventar métricas.
- Las preguntas sugeridas preparan el texto; solo el envío explícito inicia una respuesta.
