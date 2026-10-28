/* Presentación estática. La demo usa respuestas del catálogo, no llamadas a IA. */
(() => {
  'use strict';
  const personas = window.CATALOGO_PERSONAS || [];
  const $ = id => document.getElementById(id);
  const normalizar = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const escapar = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[c]));
  let categoria = 'todos';
  let activa = personas.find(p => p.id === 'tienda_jefe') || personas[0];
  let historial = [];
  let respuestaPendiente;

  function renderCatalogo() {
    const consulta = normalizar($('filtro-busqueda-agente').value.trim());
    const lista = personas.filter(p =>
      (categoria === 'todos' || p.categoria === categoria || p.proyecto === categoria)
      && normalizar([p.nombre, p.persona, p.id, ...p.bases].join(' ')).includes(consulta));
    $('catalog-count').textContent = `${lista.length} de ${personas.length} personas${['tienda','sucursal','bodega','tarjetas'].includes(categoria) ? ' · ' + ({tienda:'Tienda en línea',sucursal:'Sucursal física',bodega:'Bodega',tarjetas:'Pagos'}[categoria]) : ''}`;
    $('grid-catalogo-agentes').innerHTML = lista.length ? lista.map(p => `
      <article class="person">
        <div class="person-main"><img src="${escapar(p.avatar_url)}" alt="${escapar(p.nombre)}" width="64" height="72" loading="lazy" decoding="async"><div class="person-info"><h3 title="${escapar(p.nombre)}">${escapar(p.nombre)}</h3><p>${escapar(p.persona)}</p></div></div>
        <div class="person-actions"><span class="person-tag">${escapar(p.categoria === 'music_pro' ? p.rol_nombre : 'Personaje de IA')}</span><button class="text-link" data-profile="${p.id}" aria-label="Ver perfil de ${escapar(p.nombre)}">Ver perfil ↗</button></div>
      </article>`).join('') : '<p class="empty">No encontramos personas con esa búsqueda. Prueba otro nombre o proyecto.</p>';
    document.querySelectorAll('[data-category]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.category === categoria || (b.dataset.category === 'music_pro' && ['tienda','sucursal','bodega','tarjetas'].includes(categoria)))));
  }

  function renderMensajes() {
    $('chat-messages-container').innerHTML = historial.map(m => `<div class="message ${m.rol === 'user' ? 'user' : ''}">${m.rol === 'assistant' ? `<div class="speaker">${escapar(activa.nombre)}</div>` : ''}${escapar(m.texto)}</div>`).join('');
    $('chat-messages-container').scrollTop = $('chat-messages-container').scrollHeight;
  }

  function seleccionarPersona(id, scroll = false) {
    const persona = personas.find(p => p.id === id);
    if (!persona) return;
    clearTimeout(respuestaPendiente);
    $('demo-form').querySelector('button').disabled = false;
    $('demo-form').removeAttribute('aria-busy');
    activa = persona;
    $('demo-person').value = id;
    $('chat-active-name').textContent = persona.nombre;
    $('chat-active-role').textContent = persona.rol_nombre;
    $('chat-active-avatar').src = persona.avatar_url;
    $('chat-active-avatar').alt = persona.nombre;
    $('chat-user-input').value = '';
    historial = [{rol:'assistant', texto:persona.saludo}];
    $('chat-prompt-suggestions').innerHTML = persona.sugerencias.map((s, i) => `<button data-suggestion="${i}">${escapar(s)}</button>`).join('');
    renderMensajes();
    if (scroll) {
      $('demo-chat').scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block:'center'});
      $('chat-user-input').focus({preventScroll:true});
    }
  }

  function enviar(texto) {
    if (!texto.trim() || $('demo-form').hasAttribute('aria-busy')) return;
    historial.push({rol:'user', texto:texto.trim()});
    $('chat-user-input').value = '';
    renderMensajes();
    $('demo-form').setAttribute('aria-busy','true');
    $('demo-form').querySelector('button').disabled = true;
    respuestaPendiente = setTimeout(() => {
      const consulta = normalizar(texto);
      const clave = Object.keys(activa.respuestas).find(k => k !== 'default' && consulta.includes(normalizar(k)));
      historial.push({rol:'assistant', texto:activa.respuestas[clave || 'default']});
      renderMensajes();
      $('demo-form').removeAttribute('aria-busy');
      $('demo-form').querySelector('button').disabled = false;
    }, 250);
  }

  function abrirPerfil(id) {
    const persona = personas.find(p => p.id === id);
    if (!persona) return;
    $('modal-agente-nombre').textContent = persona.nombre;
    $('modal-agente-rol').textContent = persona.rol_nombre;
    $('modal-agente-avatar').src = persona.avatar_url;
    $('modal-agente-avatar').alt = persona.nombre;
    $('modal-agente-perfil').textContent = persona.perfil;
    $('modal-btn-chatear').onclick = () => {
      $('modal-agente').close();
      seleccionarPersona(id, true);
    };
    $('modal-agente').showModal();
  }

  $('demo-person').innerHTML = ['Music Pro','Otras personas'].map((grupo, i) => `<optgroup label="${grupo}">${personas.filter(p => (p.categoria === 'music_pro') === (i === 0)).map(p => `<option value="${p.id}">${escapar(p.nombre)} · ${escapar(p.rol_nombre)}</option>`).join('')}</optgroup>`).join('');
  $('demo-person').addEventListener('change', e => seleccionarPersona(e.target.value));
  $('demo-form').addEventListener('submit', e => {e.preventDefault(); enviar($('chat-user-input').value);});
  $('chat-prompt-suggestions').addEventListener('click', e => {
    const button = e.target.closest('[data-suggestion]');
    if (button) enviar(activa.sugerencias[Number(button.dataset.suggestion)]);
  });
  $('clear-demo').addEventListener('click', () => seleccionarPersona(activa.id));
  $('export-demo').addEventListener('click', () => {
    const blob = new Blob([historial.map(m => `${m.rol === 'user' ? 'Tú' : activa.nombre}: ${m.texto}`).join('\n\n')], {type:'text/plain;charset=utf-8'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = `demo-${activa.id}.txt`; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  $('filtro-busqueda-agente').addEventListener('input', renderCatalogo);
  $('filtros-categoria').addEventListener('click', e => {
    const button = e.target.closest('[data-category]');
    if (button) {categoria = button.dataset.category; renderCatalogo();}
  });
  $('grid-catalogo-agentes').addEventListener('click', e => {
    const button = e.target.closest('[data-profile]');
    if (button) abrirPerfil(button.dataset.profile);
  });
  document.querySelectorAll('[data-project]').forEach(b => b.addEventListener('click', () => {
    categoria = b.dataset.project;
    $('filtro-busqueda-agente').value = '';
    renderCatalogo();
    $('catalogo').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'});
  }));
  $('close-profile').addEventListener('click', () => $('modal-agente').close());
  document.querySelectorAll('dialog').forEach(dialog => dialog.addEventListener('click', e => {
    const rect = dialog.getBoundingClientRect();
    if (e.target === dialog && (e.clientX < rect.left || e.clientX > rect.right || e.clientY < rect.top || e.clientY > rect.bottom)) dialog.close();
  }));

  const themeButton = $('toggle-theme');
  function actualizarTema() {
    themeButton.setAttribute('aria-label', `Cambiar a tema ${document.documentElement.dataset.mode === 'dark' ? 'claro' : 'oscuro'}`);
    themeButton.setAttribute('aria-pressed', String(document.documentElement.dataset.mode === 'dark'));
  }
  themeButton.addEventListener('click', () => {
    const modo = document.documentElement.dataset.mode === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.mode = modo;
    try {localStorage.setItem('theythink_tema', modo);} catch {}
    actualizarTema();
  });

  const destinos = [
    ['Qué puedes hacer', '#capacidades'], ['Music Pro', '#music-pro'],
    ['Actividad para estudiantes', '#actividad'], ['Personas y perfiles', '#catalogo'],
    ['Instalación', '#quickstart'], ['Demo interactiva', '#demo-chat'],
  ];
  function renderComandos() {
    const q = normalizar($('command-search').value);
    const resultados = destinos.filter(([nombre]) => normalizar(nombre).includes(q));
    $('command-results').innerHTML = resultados.length ? resultados.map(([nombre, href]) => `<a href="${href}">${nombre} ↗</a>`).join('') : '<p class="muted small">No encontramos esa sección.</p>';
  }
  function abrirComandos() {
    $('command-search').value = ''; renderComandos();
    $('command-palette').showModal(); $('command-search').focus();
  }
  $('open-command').addEventListener('click', abrirComandos);
  $('close-command').addEventListener('click', () => $('command-palette').close());
  $('command-search').addEventListener('input', renderComandos);
  $('command-results').addEventListener('click', e => {
    if (e.target.closest('a')) $('command-palette').close();
  });
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault(); $('command-palette').open ? $('command-palette').close() : abrirComandos();
    }
    if (!$('command-palette').open || !['ArrowDown','ArrowUp'].includes(e.key)) return;
    const links = [...$('command-results').querySelectorAll('a')];
    if (!links.length) return;
    e.preventDefault();
    const index = links.indexOf(document.activeElement);
    links[(index + (e.key === 'ArrowDown' ? 1 : -1) + links.length) % links.length].focus();
  });
  document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {
    button.disabled = true; button.setAttribute('aria-busy', 'true');
    try {
      await navigator.clipboard.writeText($('code-' + button.dataset.copy).textContent);
      button.textContent = 'Copiado ✓';
      $('copy-status').classList.remove('error'); $('copy-status').textContent = 'Comandos copiados.';
    } catch {
      $('copy-status').classList.add('error');
      $('copy-status').textContent = 'No se pudo acceder al portapapeles. Selecciona y copia los comandos directamente.';
    } finally {button.disabled = false; button.removeAttribute('aria-busy');}
  }));
  // Mantiene los puntos de entrada de la presentación anterior.
  window.seleccionarAgenteChat = seleccionarPersona;
  window.abrirModalAgente = abrirPerfil;
  window.seleccionarCategoria = cat => {categoria = cat; renderCatalogo();};
  window.filtrarAgentesCatalogo = renderCatalogo;
  actualizarTema(); renderCatalogo(); seleccionarPersona(activa.id);
})();
