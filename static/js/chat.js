/**
 * Lógica del Chat Interactivo con DeepSeek AI: Hilos, Memoria, Gestión e Internacionalización.
 * Código escrito en inglés con comentarios descriptivos en español.
 */
(function () {
  "use strict";

  // Elementos principales del DOM
  var messagesContainer = document.getElementById("mensajes");
  var messageForm = document.getElementById("form-mensaje");
  var messageInput = document.getElementById("campo-mensaje");
  var sendButton = document.getElementById("boton-enviar");
  var sidebarSessionsList = document.getElementById("lista-sesiones-sidebar");
  var sidebarElement = document.getElementById("chat-sidebar");

  // Modales
  var renameModal = document.getElementById("modal-renombrar-sesion");
  var renameSessionIdInput = document.getElementById("renombrar-sesion-id");
  var renameTitleInput = document.getElementById("campo-renombrar-titulo");

  var clearMemoryModal = document.getElementById("modal-limpiar-memoria");
  var agentSettingsModal = document.getElementById("modal-gestion-agente");
  var agentSettingsForm = document.getElementById("form-gestion-agente");
  var identitySelect = document.getElementById("editar-identidad");
  var customIdentityBlock = document.getElementById("bloque-identidad-custom");

  // Identificadores del contexto actual
  var agentName = document.body.dataset.agente;
  var activeSessionId = parseInt(document.body.dataset.sesionId, 10) || null;
  var presentationElement = document.getElementById('character-presentation');
  var characterInfo = presentationElement ? JSON.parse(presentationElement.textContent) : {name: agentName};

  // Notificaciones flotantes (Toast)
  var toastElement = document.getElementById("toast");
  var toastContent = document.getElementById("toast-contenido");
  var toastIcon = document.getElementById("toast-icono");
  var toastText = document.getElementById("texto-toast");

  /**
   * Muestra un aviso emergente en la interfaz.
   * @param {string} message - Mensaje a mostrar.
   * @param {string} [type='error'] - Tipo de aviso ('exito' o 'error').
   */
  function showToast(message, type) {
    var isSuccess = type === "exito" || type === "success";
    toastText.textContent = message;
    toastContent.className =
      "flex items-center gap-2.5 rounded-2xl px-5 py-3 text-sm font-semibold text-white shadow-2xl " +
      (isSuccess ? "bg-[#34A853]" : "bg-[#EA4335]");
    toastIcon.setAttribute("data-lucide", isSuccess ? "check-circle-2" : "alert-circle");
    toastElement.classList.remove("hidden");
    clearTimeout(toastElement._timer);
    toastElement._timer = setTimeout(function () {
      toastElement.classList.add("hidden");
    }, 4000);
    if (window.lucide) lucide.createIcons();
  }

  /**
   * Obtiene una traducción a través de i18n con respaldo por defecto.
   */
  function getI18nText(key, params, fallback) {
    if (window.i18n && typeof window.i18n.t === "function") {
      var translated = window.i18n.t(key, params);
      if (translated && translated !== key) return translated;
    }
    return fallback || key;
  }

  // ------------------------------------------------------------------
  // Control de Barra Lateral y Selector de Agente
  // ------------------------------------------------------------------

  /** Alterna la visibilidad del sidebar en pantallas móviles */
  function toggleSidebar() {
    if (sidebarElement) {
      sidebarElement.classList.toggle("hidden");
    }
  }

  /** Cambia el agente activo redirigiendo a su vista correspondiente */
  function changeActiveAgent(newAgentName) {
    if (newAgentName && newAgentName !== agentName) {
      window.location.href = "/agente/" + encodeURIComponent(newAgentName);
    }
  }

  /** Filtra los hilos en el sidebar según el texto buscado */
  function filterSidebarThreads(query) {
    var q = (query || "").toLowerCase().trim();
    document.querySelectorAll("#lista-sesiones-sidebar [data-sesion-item]").forEach(function (el) {
      var title = (el.dataset.sesionTitulo || "").toLowerCase();
      el.classList.toggle("hidden", q !== "" && title.indexOf(q) === -1);
    });
  }

  /** Aplica una sugerencia de prompt rápido al campo de mensaje */
  function useSuggestion(text) {
    messageInput.value = text;
    messageInput.focus();
    messageInput.dispatchEvent(new Event("input"));
  }

  /** Copia texto al portapapeles y muestra indicador */
  function copyToClipboard(text, buttonElement) {
    if (!navigator.clipboard) return;
    navigator.clipboard.writeText(text).then(function () {
      var originalHtml = buttonElement.innerHTML;
      var copiedText = getI18nText("chat.copiedToast", null, "¡Copiado!");
      buttonElement.innerHTML = '<i data-lucide="check" class="h-3 w-3 inline text-[#34A853]"></i> <span class="text-[#34A853]">' + copiedText + '</span>';
      if (window.lucide) lucide.createIcons();
      setTimeout(function () {
        buttonElement.innerHTML = originalHtml;
        if (window.lucide) lucide.createIcons();
      }, 2000);
    });
  }

  // ------------------------------------------------------------------
  // Carga y Renderizado de Mensajes
  // ------------------------------------------------------------------

  /** Carga los mensajes de la sesión activa desde la API */
  function loadSessionMessages(sessionId) {
    var loadingText = getI18nText("common.loading", null, "Cargando conversación…");
    messagesContainer.innerHTML =
      '<div class="flex h-64 items-center justify-center text-xs text-[#5f6368] dark:text-[#c4c7c5]">' +
      '  <span class="animate-pulse">' + loadingText + '</span>' +
      '</div>';

    fetch("/api/sesion/" + sessionId)
      .then(function (response) { return response.json(); })
      .then(function (data) {
        messagesContainer.innerHTML = "";
        var messages = data.mensajes || [];

        if (!messages.length) {
          renderWelcomeScreen();
          return;
        }

        messages.forEach(function (m) {
          renderMessage(m.rol, m.mensaje, m.fecha, m.hora);
        });

        scrollToBottom();
      })
      .catch(function () {
        messagesContainer.innerHTML =
          '<div class="flex h-full items-center justify-center text-xs text-[#d93025] dark:text-[#f28b82]">' +
          getI18nText("common.error", null, "Error al cargar la conversación.") +
          '</div>';
      });
  }

  /** Renderiza la pantalla inicial de bienvenida con sugerencias de preguntas */
  function renderWelcomeScreen() {
    var dataElement = document.getElementById('character-presentation');
    var person = dataElement ? JSON.parse(dataElement.textContent) : {name: agentName, starters: []};
    messagesContainer.replaceChildren();
    var welcome = document.createElement('div'); welcome.className = 'chat-welcome';
    var image = document.createElement('img'); image.src = person.avatar || '/static/img/theythinkai_logo.png'; image.alt = person.name;
    var title = document.createElement('h3'); title.textContent = person.name;
    var role = document.createElement('p'); role.className = 'welcome-role'; role.textContent = person.role || '';
    var description = document.createElement('p'); description.textContent = person.description || '';
    var starters = document.createElement('div'); starters.className = 'welcome-starters';
    (person.starters || []).forEach(function (prompt) {
      var button = document.createElement('button'); button.type = 'button'; button.textContent = prompt;
      button.addEventListener('click', function () { useSuggestion(prompt); }); starters.appendChild(button);
    });
    welcome.append(image, title, role, description, starters); messagesContainer.appendChild(welcome);
  }

  /** Convierte Markdown a HTML sanitizado. */
  function marcar(texto) {
    if (window.marked && window.DOMPurify) {
      return DOMPurify.sanitize(marked.parse(texto, { breaks: true, gfm: true }));
    }
    var div = document.createElement("div");
    div.textContent = texto;
    return div.innerHTML.replace(/\n/g, "<br>");
  }

  /** Renderiza una burbuja de mensaje individual */
  function renderMessage(role, text, date, time) {
    var isUser = role === "user";
    var row = document.createElement("div");
    row.className = "flex " + (isUser ? "justify-end" : "justify-start") + " animate-fade-in";

    var box = document.createElement("div");
    box.className = "max-w-[90%] sm:max-w-[80%] lg:max-w-[70%]";

    var bubble = document.createElement("div");
    if (isUser) {
      bubble.className = "rounded-3xl rounded-br-sm bg-[#1a73e8] px-5 py-3.5 text-sm text-white shadow-md";
      bubble.textContent = text;
    } else {
      bubble.className = "rounded-3xl rounded-bl-sm border border-black/10 dark:border-white/10 bg-white dark:bg-[#1e1f20] px-5 py-4 text-sm leading-relaxed text-[#202124] dark:text-[#e3e3e3] shadow-sm prose-chat";
      bubble.innerHTML = marcar(text);
    }

    var footer = document.createElement("div");
    footer.className = "mt-1.5 flex items-center justify-between text-[10px] text-[#5f6368] dark:text-[#c4c7c5] px-1";

    var copyLabel = getI18nText("chat.copyCode", null, "Copiar");

    var author = document.createElement('span');
    author.textContent = (isUser ? 'Tú' : characterInfo.name) + (time ? ' · ' + time : '');
    if (isUser) author.className = 'ml-auto';
    footer.appendChild(author);
    if (!isUser) {
      var copyButton = document.createElement('button');
      copyButton.type = 'button';
      copyButton.className = 'inline-flex items-center gap-1 text-[11px]';
      copyButton.textContent = copyLabel;
      copyButton.addEventListener('click', function () { copyToClipboard(text, copyButton); });
      footer.appendChild(copyButton);
    }

    row.classList.add("message-row");
    box.classList.add("message-box");
    bubble.classList.add(isUser ? "message-user" : "message-assistant");
    box.appendChild(bubble);
    box.appendChild(footer);
    row.appendChild(box);
    messagesContainer.appendChild(row);

    if (window.lucide) lucide.createIcons();
  }

  /** Renderiza el indicador de carga animado de 4 colores Google */
  function renderLoadingBubble() {
    var row = document.createElement("div");
    row.id = "burbuja-cargando";
    row.className = "flex justify-start animate-fade-in";
    var thinkingText = getI18nText("chat.thinking", null, "Generando respuesta…");

    row.innerHTML =
      '<div class="flex items-center gap-2 rounded-3xl rounded-bl-sm border border-black/10 dark:border-white/10 bg-white dark:bg-[#1e1f20] px-5 py-3.5 shadow-sm text-xs text-[#5f6368] dark:text-[#c4c7c5]">' +
      '  <div class="flex items-center gap-1">' +
      '    <span class="h-2 w-2 animate-bounce rounded-full bg-[#4285F4]"></span>' +
      '    <span class="h-2 w-2 animate-bounce rounded-full bg-[#EA4335] [animation-delay:0.15s]"></span>' +
      '    <span class="h-2 w-2 animate-bounce rounded-full bg-[#FBBC04] [animation-delay:0.3s]"></span>' +
      '    <span class="h-2 w-2 animate-bounce rounded-full bg-[#34A853] [animation-delay:0.45s]"></span>' +
      '  </div>' +
      '  <span>' + thinkingText + '</span>' +
      '</div>';
    messagesContainer.appendChild(row);
    scrollToBottom();
  }

  /** Remueve la burbuja de carga */
  function removeLoadingBubble() {
    var element = document.getElementById("burbuja-cargando");
    if (element) element.remove();
  }

  /** Desplaza el contenedor de mensajes hasta el final */
  function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  // ------------------------------------------------------------------
  // Enviar Mensaje y Auto-Crecimiento de Textarea
  // ------------------------------------------------------------------
  messageInput.addEventListener("input", function () {
    this.style.height = "auto";
    this.style.height = Math.min(this.scrollHeight, 180) + "px";
  });

  messageInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      messageForm.requestSubmit();
    }
  });

  messageForm.addEventListener("submit", function (e) {
    e.preventDefault();
    var text = messageInput.value.trim();
    if (!text || sendButton.disabled) return;

    if (!activeSessionId) {
      showToast(getI18nText("chat.emptyHistory", null, "No hay una conversación activa."));
      return;
    }

    // Limpiar pantalla de bienvenida si estaba activa
    var welcomeHeader = messagesContainer.querySelector("h3");
    if (welcomeHeader && welcomeHeader.textContent.indexOf("¡Hola!") !== -1) {
      messagesContainer.innerHTML = "";
    }

    var now = new Date();
    var time = now.getHours().toString().padStart(2, "0") + ":" + now.getMinutes().toString().padStart(2, "0");
    renderMessage("user", text, null, time);
    scrollToBottom();

    messageInput.value = "";
    messageInput.style.height = "auto";
    sendButton.disabled = true;
    renderLoadingBubble();

    fetch("/api/sesion/" + activeSessionId + "/mensaje", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mensaje: text }),
    })
      .then(function (response) {
        return response.json().then(function (data) { return { ok: response.ok, data: data }; });
      })
      .then(function (result) {
        removeLoadingBubble();
        if (!result.ok) throw new Error(result.data.error || "Error al comunicarse con DeepSeek.");

        renderMessage("assistant", result.data.respuesta, null, time);
        if (result.data.memoria_guardada) {
          showToast(getI18nText("chat.memoryUpdated", null, "Memoria del agente actualizada"), "exito");
        }

        updateSidebarSessions();
      })
      .catch(function (error) {
        removeLoadingBubble();
        showToast(error.message);
      })
      .finally(function () {
        sendButton.disabled = false;
        setTimeout(function () { messageInput.focus(); }, 50);
      });
  });

  // ------------------------------------------------------------------
  // Gestión de Sesiones (Hilos)
  // ------------------------------------------------------------------

  /** Crea una nueva sesión de chat y la activa */
  function createNewConversation() {
    fetch("/api/agente/" + encodeURIComponent(agentName) + "/sesiones", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    })
      .then(function (response) { return response.json(); })
      .then(function (session) {
        activeSessionId = session.id;
        document.body.dataset.sesionId = session.id;
        loadSessionMessages(session.id);
        updateSidebarSessions();
        showToast(getI18nText("chat.newChat", null, "Nueva conversación iniciada."), "exito");
        setTimeout(function () { messageInput.focus(); }, 50);
      })
      .catch(function () {
        showToast("No se pudo iniciar una nueva conversación.");
      });
  }

  /** Cambia la conversación activa a la sesión especificada */
  function switchActiveSession(sessionId) {
    if (sessionId === activeSessionId) return;
    activeSessionId = sessionId;
    document.body.dataset.sesionId = sessionId;
    loadSessionMessages(sessionId);
    updateSidebarSessions();
  }

  /** Actualiza la lista de hilos en la barra lateral */
  function updateSidebarSessions() {
    fetch("/api/agente/" + encodeURIComponent(agentName) + "/sesiones")
      .then(function (response) { return response.json(); })
      .then(function (data) {
        var sessions = data.sesiones || [];
        sidebarSessionsList.innerHTML = "";

        sessions.forEach(function (s) {
          var isActive = s.id === activeSessionId;
          var div = document.createElement("div");
          div.setAttribute("data-sesion-item", s.id);
          div.setAttribute("data-sesion-titulo", s.titulo);
          div.className =
            "group relative flex items-center justify-between rounded-xl border p-2.5 transition " +
            (isActive
              ? "border-[#1a73e8] bg-[#1a73e8]/10 font-bold text-[#1a73e8] dark:text-[#8ab4f8]"
              : "border-transparent hover:bg-black/5 dark:hover:bg-white/5 text-[#202124] dark:text-[#e3e3e3]");

          var safeTitle = (s.titulo || "").replace(/'/g, "\\'");
          div.innerHTML =
            '<button onclick="window.cambiarSesionActiva(' + s.id + ')" class="min-w-0 flex-1 text-left">' +
            '  <p class="truncate text-xs" title="' + safeTitle + '">' + s.titulo + '</p>' +
            '  <p class="mt-0.5 text-[10px] text-[#5f6368] dark:text-[#c4c7c5] font-normal">' + s.total_mensajes + ' msgs · ' + (s.actualizado_en ? s.actualizado_en.slice(0, 10) : "") + '</p>' +
            '</button>' +
            '<div class="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition">' +
            '  <button onclick="window.abrirModalRenombrarSesion(' + s.id + ', \'' + safeTitle + '\')" title="Renombrar" class="rounded-lg p-1 text-[#5f6368] dark:text-[#c4c7c5] hover:bg-black/10 dark:hover:bg-white/10 hover:text-black dark:hover:text-white"><i data-lucide="pencil" class="h-3 w-3"></i></button>' +
            '  <button onclick="window.confirmarEliminarSesion(' + s.id + ')" title="Eliminar" class="rounded-lg p-1 text-[#5f6368] dark:text-[#c4c7c5] hover:bg-[#EA4335]/20 hover:text-[#d93025] dark:hover:text-[#f28b82]"><i data-lucide="trash-2" class="h-3 w-3"></i></button>' +
            '</div>';

          sidebarSessionsList.appendChild(div);
        });

        if (window.lucide) lucide.createIcons();
      });
  }

  /** Abre el modal para renombrar una sesión */
  function openRenameModal(sessionId, currentTitle) {
    renameSessionIdInput.value = sessionId;
    renameTitleInput.value = currentTitle || "";
    renameModal.classList.remove("hidden");
    renameModal.classList.add("flex");
    setTimeout(function () { renameTitleInput.focus(); }, 50);
  }

  /** Cierra el modal de renombrado */
  function closeRenameModal() {
    renameModal.classList.add("hidden");
    renameModal.classList.remove("flex");
  }

  /** Guarda el nuevo título de la sesión */
  function saveRenameSession() {
    var id = renameSessionIdInput.value;
    var newTitle = renameTitleInput.value.trim();
    if (!newTitle) {
      showToast("El título no puede estar vacío.");
      return;
    }

    fetch("/api/sesion/" + id, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ titulo: newTitle }),
    })
      .then(function (response) { return response.json(); })
      .then(function () {
        closeRenameModal();
        showToast(getI18nText("chat.sessionRenamed", null, "Conversación renombrada"), "exito");
        updateSidebarSessions();
      })
      .catch(function () {
        showToast("Error al renombrar la conversación.");
      });
  }

  /** Confirma y ejecuta la eliminación de una sesión */
  function confirmDeleteSession(sessionId) {
    var confirmMessage = getI18nText("chat.deleteChatConfirm", null, "¿Estás seguro de eliminar este hilo de conversación?");
    if (!confirm(confirmMessage)) return;

    fetch("/api/sesion/" + sessionId, { method: "DELETE" })
      .then(function (response) { return response.json(); })
      .then(function () {
        showToast(getI18nText("chat.sessionDeleted", null, "Conversación eliminada"), "exito");
        if (sessionId === activeSessionId) {
          fetch("/api/agente/" + encodeURIComponent(agentName) + "/sesiones")
            .then(function (res) { return res.json(); })
            .then(function (d) {
              if (d.sesiones && d.sesiones.length) {
                switchActiveSession(d.sesiones[0].id);
              } else {
                createNewConversation();
              }
            });
        } else {
          updateSidebarSessions();
        }
      })
      .catch(function () {
        showToast("Error al eliminar la conversación.");
      });
  }

  // ------------------------------------------------------------------
  // Drawer de Gestión Integral del Agente (Slide-Over Panel)
  // ------------------------------------------------------------------
  function openAgentSettings() {
    if (!agentSettingsModal) return;
    agentSettingsModal.classList.remove("hidden");
    var backdrop = document.getElementById("drawer-agente-backdrop");
    var panel = document.getElementById("drawer-agente-panel");
    requestAnimationFrame(function () {
      if (backdrop) {
        backdrop.classList.remove("opacity-0");
        backdrop.classList.add("opacity-100");
      }
      if (panel) {
        panel.classList.remove("translate-x-full");
        panel.classList.add("translate-x-0");
      }
    });
    if (window.lucide) lucide.createIcons();
  }

  function closeAgentSettings() {
    if (!agentSettingsModal) return;
    var backdrop = document.getElementById("drawer-agente-backdrop");
    var panel = document.getElementById("drawer-agente-panel");
    if (backdrop) {
      backdrop.classList.remove("opacity-100");
      backdrop.classList.add("opacity-0");
    }
    if (panel) {
      panel.classList.remove("translate-x-0");
      panel.classList.add("translate-x-full");
    }
    setTimeout(function () {
      agentSettingsModal.classList.add("hidden");
    }, 300);
  }

  function switchSettingsTab(tabName) {
    var tabs = ["perfil", "fuentes", "rol", "memoria"];
    tabs.forEach(function (t) {
      var section = document.getElementById("tab-gestion-" + t);
      var button = document.getElementById("btn-tab-modal-" + t);
      if (section) section.classList.toggle("hidden", t !== tabName);
      if (button) {
        if (t === tabName) {
          button.className = "px-4 py-2 rounded-xl font-bold bg-black/10 dark:bg-white/15 text-[#202124] dark:text-white transition shrink-0";
        } else {
          button.className = "px-4 py-2 rounded-xl font-semibold text-[#5f6368] dark:text-[#c4c7c5] hover:text-black dark:hover:text-white transition shrink-0";
        }
      }
    });
    if (window.lucide) lucide.createIcons();
  }

  if (identitySelect) {
    identitySelect.addEventListener("change", function () {
      if (customIdentityBlock) {
        customIdentityBlock.classList.toggle("hidden", identitySelect.value !== "personalizada");
      }
    });
  }

  // ------------------------------------------------------------------
  // Manejo de Avatar e Imágenes en Chat
  // ------------------------------------------------------------------
  function uploadAvatarFile(input, prefix) {
    if (!input.files || !input.files[0]) return;
    var file = input.files[0];
    var formData = new FormData();
    formData.append("avatar", file);

    showToast("Subiendo imagen…", "exito");
    fetch("/api/upload/avatar", {
      method: "POST",
      body: formData,
    })
      .then(function (response) { return response.json(); })
      .then(function (data) {
        if (!data.ok) throw new Error(data.error || "Error al subir imagen.");
        updateAvatarUrlInput(data.url, prefix);
        showToast("Imagen cargada con éxito.", "exito");
      })
      .catch(function (err) {
        showToast(err.message);
      });
  }

  function updateAvatarUrlInput(url, prefix) {
    var cleanUrl = (url || "").trim();
    var previewImg = document.getElementById(prefix + "-avatar-preview-img");
    var previewInitials = document.getElementById(prefix + "-avatar-preview-initials");
    var urlField = document.getElementById(prefix + "-campo-avatar-url");
    var urlInputField = document.getElementById(prefix + "-campo-avatar-url-input");

    if (urlField) urlField.value = cleanUrl;
    if (urlInputField && urlInputField.value !== cleanUrl) urlInputField.value = cleanUrl;

    if (previewImg && previewInitials) {
      if (cleanUrl) {
        previewImg.src = cleanUrl;
        previewImg.classList.remove("hidden");
        previewInitials.classList.add("hidden");
      } else {
        previewImg.src = "";
        previewImg.classList.add("hidden");
        previewInitials.classList.remove("hidden");
      }
    }
  }

  function clearSelectedAvatar(prefix) {
    updateAvatarUrlInput("", prefix);
    var inputFile = document.getElementById(prefix + "-input-avatar-file");
    if (inputFile) inputFile.value = "";
  }

  if (agentSettingsForm) {
    agentSettingsForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var profile = document.getElementById("editar-perfil").value.trim();
      var customPrompt = document.getElementById("editar-identidad-custom").value.trim();
      var roleKey = identitySelect.value;
      var avatarUrl = document.getElementById("chat-campo-avatar-url") ? document.getElementById("chat-campo-avatar-url").value.trim() : "";

      var selectedSources = [];
      document.querySelectorAll("input[name=editar_fuentes]:checked").forEach(function (cb) {
        selectedSources.push(parseInt(cb.value, 10));
      });

      var payload = { perfil: profile, avatar_url: avatarUrl, fuentes: selectedSources };
      if (roleKey === "personalizada") payload.identidad_custom = customPrompt;
      else payload.identidad = roleKey;

      fetch("/api/agente/" + encodeURIComponent(agentName) + "/editar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })
        .then(function (response) { return response.json(); })
        .then(function () {
          closeAgentSettings();
          showToast(getI18nText("chat.agentUpdated", null, "Agente actualizado exitosamente"), "exito");
          setTimeout(function () { window.location.reload(); }, 500);
        })
        .catch(function () {
          showToast("Error al actualizar el agente.");
        });
    });
  }

  // ------------------------------------------------------------------
  // Limpieza de Memoria
  // ------------------------------------------------------------------
  function openClearMemoryModal() {
    clearMemoryModal.classList.remove("hidden");
    clearMemoryModal.classList.add("flex");
  }

  function closeClearMemoryModal() {
    clearMemoryModal.classList.add("hidden");
    clearMemoryModal.classList.remove("flex");
  }

  function executeClearMemory() {
    fetch("/api/agente/" + encodeURIComponent(agentName) + "/limpiar", { method: "POST" })
      .then(function (response) { return response.json(); })
      .then(function () {
        closeClearMemoryModal();
        if (agentSettingsModal) closeAgentSettings();
        showToast(getI18nText("chat.memoryCleared", null, "Memoria eliminada correctamente"), "exito");
        setTimeout(function () { window.location.reload(); }, 500);
      });
  }

  /** Alterna la apertura/cierre del dropdown de selección de agente */
  function toggleAgentDropdown(e) {
    if (e) e.stopPropagation();
    var menu = document.getElementById("menu-agentes-dropdown");
    var chevron = document.getElementById("chevron-agent-dropdown");
    if (!menu) return;
    var isOpen = !menu.classList.contains("hidden");
    if (isOpen) {
      menu.classList.add("hidden");
      if (chevron) chevron.style.transform = "rotate(0deg)";
    } else {
      menu.classList.remove("hidden");
      if (chevron) chevron.style.transform = "rotate(180deg)";
      var searchInput = document.getElementById("input-buscar-agente-header");
      if (searchInput) {
        searchInput.value = "";
        filterHeaderAgents("");
        setTimeout(function () { searchInput.focus(); }, 50);
      }
    }
  }

  /** Filtra los agentes en el dropdown del header en tiempo real */
  function filterHeaderAgents(query) {
    var q = (query || "").toLowerCase().trim();
    var items = document.querySelectorAll(".agente-header-opcion");
    var visibleCount = 0;
    items.forEach(function (el) {
      var nom = (el.dataset.agenteItem || "").toLowerCase();
      var per = (el.dataset.agentePersona || "").toLowerCase();
      var rol = (el.dataset.agenteRol || "").toLowerCase();
      var match = nom.indexOf(q) !== -1 || per.indexOf(q) !== -1 || rol.indexOf(q) !== -1;
      el.classList.toggle("hidden", !match);
      if (match) visibleCount++;
    });
    var noMsg = document.getElementById("no-agentes-header-msg");
    if (noMsg) noMsg.classList.toggle("hidden", visibleCount > 0);
  }

  // Exposición de funciones en window para compatibilidad hacia atrás
  window.toggleSidebarChat = toggleSidebar;
  window.cambiarAgenteActivo = changeActiveAgent;
  window.toggleAgentDropdown = toggleAgentDropdown;
  window.filtrarAgentesHeader = filterHeaderAgents;
  window.filtrarHilosSidebar = filterSidebarThreads;
  window.usarSugerencia = useSuggestion;
  window.copiarTexto = copyToClipboard;
  window.crearNuevaConversacion = createNewConversation;
  window.cambiarSesionActiva = switchActiveSession;
  window.abrirModalRenombrarSesion = openRenameModal;
  window.cerrarModalRenombrarSesion = closeRenameModal;
  window.guardarRenombrarSesion = saveRenameSession;
  window.confirmarEliminarSesion = confirmDeleteSession;
  window.abrirModalGestionAgente = openAgentSettings;
  window.cerrarModalGestionAgente = closeAgentSettings;
  window.cambiarTabModalGestion = switchSettingsTab;
  window.subirAvatarArchivo = uploadAvatarFile;
  window.actualizarAvatarUrlInput = updateAvatarUrlInput;
  window.limpiarAvatarSeleccionado = clearSelectedAvatar;
  window.abrirModalLimpiarMemoria = openClearMemoryModal;
  window.cerrarModalLimpiarMemoria = closeClearMemoryModal;
  window.ejecutarLimpiarMemoria = executeClearMemory;

  var mobileSidebar = window.matchMedia("(max-width: 767px)");
  function syncSidebar() { if (sidebarElement) sidebarElement.classList.toggle("hidden", mobileSidebar.matches); }
  syncSidebar();
  mobileSidebar.addEventListener("change", syncSidebar);

  // Carga inicial de mensajes
  if (activeSessionId) {
    loadSessionMessages(activeSessionId);
  } else {
    createNewConversation();
  }

  // Cierre al hacer clic fuera del dropdown de agentes
  document.addEventListener("click", function (e) {
    var dropdown = document.getElementById("dropdown-agentes-header");
    var menu = document.getElementById("menu-agentes-dropdown");
    var chevron = document.getElementById("chevron-agent-dropdown");
    if (dropdown && menu && !dropdown.contains(e.target)) {
      menu.classList.add("hidden");
      if (chevron) chevron.style.transform = "rotate(0deg)";
    }
  });

  // Tecla Escape para modales y dropdowns
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      var menu = document.getElementById("menu-agentes-dropdown");
      var chevron = document.getElementById("chevron-agent-dropdown");
      if (menu) {
        menu.classList.add("hidden");
        if (chevron) chevron.style.transform = "rotate(0deg)";
      }
      closeAgentSettings();
      closeClearMemoryModal();
      closeRenameModal();
    }
  });
})();
