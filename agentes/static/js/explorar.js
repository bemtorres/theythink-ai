(function () {
  'use strict';
  const agents = JSON.parse(document.getElementById('catalog-data').textContent);
  const config = JSON.parse(document.getElementById('catalog-config').textContent);
  const storageKey = 'theythink-favorites:' + (config.user || 'guest');
  const groups = config.groups || [];
  const musicpro = groups.find(g => g.nombre === 'MusicPro');
  const byId = Object.fromEntries(agents.map(a => [a.id, a]));
  let favorites = [];
  try { const saved = JSON.parse(localStorage.getItem(storageKey) || '[]'); if (Array.isArray(saved)) favorites = saved.filter(id => byId[id]); } catch (_) {}
  let category = 'all', view = 'all', selectedGroup = config.initialGroup ?? null, opener;
  const cards = document.getElementById('cards'), search = document.getElementById('search');
  const dialog = document.getElementById('detail');
  const normalize = text => text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  function element(tag, className, text) { const el = document.createElement(tag); if (className) el.className = className; if (text) el.textContent = text; return el; }
  function protectImage(image) { image.addEventListener('error', () => { image.src = '/static/img/theythinkai_logo.png'; }, {once:true}); }
  function save() { try { localStorage.setItem(storageKey, JSON.stringify(favorites)); } catch (_) {} }
  function showDetail(agent, button) {
    opener = button;
    const content = document.getElementById('detail-content'); content.replaceChildren();
    const image = element('img', 'detail-photo'); image.src = agent.avatar || '/static/img/theythinkai_logo.png'; image.alt = agent.name; protectImage(image); content.append(image);
    const copy = element('div', 'detail-copy'); copy.append(element('span', 'eyebrow', agent.group || 'PERSONAJES'));
    const name = element('h2', '', agent.name); name.id = 'detail-name'; copy.append(name, element('span', 'card-role', agent.role), element('p', '', agent.description), element('h3', '', 'Una pregunta para empezar'));
    const status = element('div', 'copy-status'); status.setAttribute('role', 'status');
    const fallback = element('textarea', 'copy-fallback'); fallback.readOnly = true; fallback.hidden = true; fallback.setAttribute('aria-label', 'Pregunta para copiar');
    agent.starters.forEach(prompt => { const b = element('button', 'starter', prompt); b.type = 'button'; b.addEventListener('click', async () => { try { await navigator.clipboard.writeText(prompt); status.textContent = 'Pregunta copiada. Pégala al abrir la conversación.'; fallback.hidden = true; } catch (_) { fallback.value = prompt; fallback.hidden = false; fallback.focus(); fallback.select(); status.textContent = 'Selecciona y copia la pregunta para usarla en el chat.'; } }); copy.append(b); });
    copy.append(status, fallback);
    const link = element('a', 'start-chat', 'Abrir conversación ↗'); link.href = '/agente/' + encodeURIComponent(agent.id); copy.append(link); content.append(copy); dialog.showModal();
  }
  function render() {
    const query = normalize(search.value.trim());
    const filtered = agents.filter(a => (category === 'all' || a.category === category) && (selectedGroup === null || a.groups.includes(selectedGroup)) && (view !== 'favorites' || favorites.includes(a.id)) && normalize([a.name, a.role, a.description, a.id, a.group].join(' ')).includes(query));
    cards.replaceChildren();
    filtered.forEach(agent => {
      const card = element('article', 'card'); const open = element('button', 'card-open'); open.type = 'button'; open.setAttribute('aria-label', 'Conocer a ' + agent.name);
      const image = element('img', 'card-photo'); image.src = agent.avatar || '/static/img/theythinkai_logo.png'; image.alt = ''; image.loading = 'lazy'; image.width = 400; image.height = 334; protectImage(image); open.append(image);
      const copy = element('div', 'card-copy'); copy.append(element('span', 'card-tag', agent.group || 'Personajes'), element('h3', '', agent.name), element('p', 'card-role', agent.role), element('p', 'card-description', agent.description));
      const bottom = element('div', 'card-bottom'); bottom.append(element('span', '', 'Conoce su perspectiva'), element('span', '', '↗')); copy.append(bottom); open.append(copy); open.addEventListener('click', () => showDetail(agent, open));
      const favorite = element('button', 'favorite', favorites.includes(agent.id) ? '♥' : '♡'); favorite.type = 'button'; favorite.setAttribute('aria-label', 'Favorito: ' + agent.name); favorite.setAttribute('aria-pressed', String(favorites.includes(agent.id)));
      favorite.addEventListener('click', () => { favorites = favorites.includes(agent.id) ? favorites.filter(id => id !== agent.id) : [...favorites, agent.id]; save(); render(); const replacement = cards.querySelector('[data-agent="' + agent.id + '"] .favorite'); if (replacement) replacement.focus(); });
      card.dataset.agent = agent.id; card.append(open, favorite); cards.append(card);
    });
    document.getElementById('fav-count').textContent = favorites.length;
    document.getElementById('result-count').textContent = filtered.length + (filtered.length === 1 ? ' personaje' : ' personajes');
    document.getElementById('empty').hidden = filtered.length > 0;
    const group = groups.find(g => g.id === selectedGroup);
    document.getElementById('results-title').textContent = view === 'favorites' ? 'Tus voces favoritas' : group ? 'Conoce a ' + group.nombre : 'Encuentra tu próxima conversación';
    document.getElementById('results-subtitle').textContent = group ? 'Una perspectiva para cada pregunta.' : 'Personajes con una historia y una forma propia de ver las cosas.';
    document.querySelectorAll('[data-view]').forEach(b => { b.classList.toggle('active', b.dataset.view === view && selectedGroup === null); b.setAttribute('aria-pressed', String(b.dataset.view === view && selectedGroup === null)); });
    document.querySelectorAll('[data-category]').forEach(b => { b.classList.toggle('selected', b.dataset.category === category); b.setAttribute('aria-pressed', String(b.dataset.category === category)); });
    document.querySelectorAll('[data-group]').forEach(b => b.setAttribute('aria-pressed', String(Number(b.dataset.group) === selectedGroup)));
  }
  search.addEventListener('input', render);
  document.querySelectorAll('[data-category]').forEach(b => b.addEventListener('click', () => { category = b.dataset.category; render(); }));
  document.querySelectorAll('[data-view]').forEach(b => b.addEventListener('click', () => { view = b.dataset.view; selectedGroup = null; render(); }));
  function selectGroup(id) { selectedGroup = selectedGroup === id ? null : id; render(); }
  document.querySelectorAll('[data-group]').forEach(b => b.addEventListener('click', () => selectGroup(Number(b.dataset.group))));
  const exploreMusic = document.getElementById('explore-music');
  if (exploreMusic && musicpro) exploreMusic.addEventListener('click', () => selectGroup(musicpro.id));
  document.getElementById('reset').addEventListener('click', () => { category = 'all'; view = 'all'; selectedGroup = null; search.value = ''; render(); search.focus(); });
  document.getElementById('close-detail').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => { if (opener && opener.isConnected) opener.focus(); });
  dialog.addEventListener('click', e => { if (e.target === dialog) { const box = dialog.getBoundingClientRect(); if (e.clientX < box.left || e.clientX > box.right || e.clientY < box.top || e.clientY > box.bottom) dialog.close(); } });
  document.addEventListener('keydown', e => { if (e.key === '/' && !dialog.open && !['INPUT','TEXTAREA'].includes(document.activeElement.tagName)) { e.preventDefault(); search.focus(); } });
  document.getElementById('theme').addEventListener('click', () => { const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'; document.documentElement.dataset.theme = theme; try { localStorage.setItem('tema_preferido', theme); } catch (_) {} });
  render();
})();
