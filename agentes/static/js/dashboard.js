/**
 * Lógica del Dashboard Administrativo de THEYTHINK AI.
 * Gestión integral de Agentes, Bases de Conocimiento, Roles, Usuarios y Conversaciones.
 * Código escrito en inglés con comentarios y docstrings en español.
 */
(function () {
  "use strict";

  // Secciones del Dashboard y botones de pestañas
  var agentsSection = document.getElementById("dash-seccion-agentes");
  var sourcesSection = document.getElementById("dash-seccion-fuentes");
  var rolesSection = document.getElementById("dash-seccion-roles");
  var usersSection = document.getElementById("dash-seccion-usuarios");
  var historySection = document.getElementById("dash-seccion-historial");

  var tabAgentsButton = document.getElementById("btn-tab-dash-agentes");
  var tabSourcesButton = document.getElementById("btn-tab-dash-fuentes");
  var tabRolesButton = document.getElementById("btn-tab-dash-roles");
  var tabUsersButton = document.getElementById("btn-tab-dash-usuarios");
  var tabHistoryButton = document.getElementById("btn-tab-dash-historial");
  var createActionButton = document.getElementById("btn-accion-crear");

  // Modal Agente
  var agentModal = document.getElementById("modal-agente-dash");
  var agentForm = document.getElementById("form-agente-dash");
  var agentModalTitle = document.getElementById("titulo-modal-agente-dash");
  var agentModeInput = document.getElementById("dash-agente-modo");
  var agentNameInput = document.getElementById("dash-campo-nombre");
  var agentProfileInput = document.getElementById("dash-campo-perfil");
  var agentIdentitySelect = document.getElementById("dash-select-identidad");
  var agentCustomBlock = document.getElementById("dash-bloque-personalizada");
  var agentCustomPromptInput = document.getElementById("dash-identidad-custom");
  var agentSourcesList = document.getElementById("dash-lista-fuentes");
  var agentSaveButton = document.getElementById("btn-guardar-agente-dash");

  // Modal Base de Conocimiento
  var sourceModal = document.getElementById("modal-fuente-dash");
  var sourceForm = document.getElementById("form-fuente-dash");
  var sourceModalTitle = document.getElementById("titulo-modal-fuente-dash");
  var sourceIdInput = document.getElementById("dash-fuente-id");
  var sourceNameInput = document.getElementById("dash-fuente-nombre");
  var sourceContentInput = document.getElementById("dash-fuente-contenido");
  var sourceSaveButton = document.getElementById("btn-guardar-fuente-dash");

  // Modal Rol / Identidad
  var roleModal = document.getElementById("modal-rol-dash");
  var roleForm = document.getElementById("form-rol-dash");
  var roleModalTitle = document.getElementById("titulo-modal-rol-dash");
  var roleIdInput = document.getElementById("dash-rol-id");
  var roleKeyInput = document.getElementById("dash-rol-clave");
  var roleNameInput = document.getElementById("dash-rol-nombre");
  var roleDescInput = document.getElementById("dash-rol-descripcion");
  var rolePromptInput = document.getElementById("dash-rol-prompt");
  var roleSaveButton = document.getElementById("btn-guardar-rol-dash");

  // Modales Usuario (Show / Edit / Create)
  var showUserModal = document.getElementById("modal-show-usuario");
  var showUserAvatar = document.getElementById("show-usuario-avatar");
  var showUserName = document.getElementById("show-usuario-nombre");
  var showUserId = document.getElementById("show-usuario-id");
  var showUserRole = document.getElementById("show-usuario-rol");
  var showUserDate = document.getElementById("show-usuario-fecha");
  var currentShowUserId = null;

  var userModal = document.getElementById("modal-usuario-dash");
  var userForm = document.getElementById("form-usuario-dash");
  var userModalTitle = document.getElementById("titulo-modal-usuario-dash");
  var userIdInput = document.getElementById("dash-usuario-id");
  var userModeInput = document.getElementById("dash-usuario-modo");
  var userNameInput = document.getElementById("dash-usuario-nombre");
  var userRoleInput = document.getElementById("dash-usuario-rol");
  var userPasswordInput = document.getElementById("dash-usuario-password");
  var userPwdHelp = document.getElementById("dash-usuario-pwd-ayuda");
  var userSaveButton = document.getElementById("btn-guardar-usuario-dash");

  // Modal Mi Perfil
  var myProfileModal = document.getElementById("modal-mi-perfil");
  var myProfileForm = document.getElementById("form-mi-perfil");
  var profileNameInput = document.getElementById("perfil-nombre");
  var profilePasswordInput = document.getElementById("perfil-password");
  var profileSaveButton = document.getElementById("btn-guardar-mi-perfil");

  // Modal Confirmación Eliminar
  var deleteModal = document.getElementById("modal-eliminar-dash");
  var deleteTitle = document.getElementById("titulo-eliminar-dash");
  var deleteDesc = document.getElementById("desc-eliminar-dash");
  var deleteConfirmButton = document.getElementById("btn-confirmar-eliminar-dash");
  var deleteCallbackAction = null;

  // Visor de transcripciones
  var conversationsAgentFilter = document.getElementById("filtro-agente-conversaciones");
  var sessionsCounter = document.getElementById("contador-mantenedor-sesiones");
  var threadsList = document.getElementById("dash-lista-hilos");
  var viewerTitle = document.getElementById("visor-titulo-sesion");
  var viewerAgent = document.getElementById("visor-agente-sesion");
  var viewerAgentBadge = document.getElementById("visor-badge-agente");
  var viewerMessagesContainer = document.getElementById("visor-contenedor-mensajes");
  var viewerDeleteButton = document.getElementById("btn-eliminar-sesion-visor");
  var viewerOpenChatButton = document.getElementById("btn-abrir-chat-visor");
  var activeViewerSessionId = null;

  // Toast
  var toastElement = document.getElementById("toast");
  var toastContent = document.getElementById("toast-contenido");
  var toastIcon = document.getElementById("toast-icono");
  var toastText = document.getElementById("texto-toast");

  /**
   * Muestra un aviso emergente en la interfaz.
   * @param {string} message - Texto del aviso.
   * @param {string} [type='error'] - Tipo ('exito' o 'error').
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
    }, 4500);
    if (window.lucide) lucide.createIcons();
  }

  /**
   * Obtiene texto traducido con i18n o respaldo.
   */
  function getI18nText(key, params, fallback) {
    if (window.i18n && typeof window.i18n.t === "function") {
      var translated = window.i18n.t(key, params);
      if (translated && translated !== key) return translated;
    }
    return fallback || key;
  }

  // ------------------------------------------------------------------
  // Pestañas del Dashboard
  // ------------------------------------------------------------------

  /** Cambia la pestaña activa del dashboard */
  function switchDashboardTab(tab) {
    agentsSection.classList.toggle("hidden", tab !== "agentes");
    sourcesSection.classList.toggle("hidden", tab !== "fuentes");
    if (rolesSection) rolesSection.classList.toggle("hidden", tab !== "roles");
    if (usersSection) usersSection.classList.toggle("hidden", tab !== "usuarios");
    historySection.classList.toggle("hidden", tab !== "historial");

    var activeClass = "inline-flex items-center gap-2 rounded-xl bg-white/15 px-3.5 py-1.5 text-xs font-bold text-white shadow-sm transition";
    var inactiveClass = "inline-flex items-center gap-2 rounded-xl px-3.5 py-1.5 text-xs font-semibold text-zinc-400 transition hover:bg-white/5 hover:text-white";

    tabAgentsButton.className = tab === "agentes" ? activeClass : inactiveClass;
    tabSourcesButton.className = tab === "fuentes" ? activeClass : inactiveClass;
    if (tabRolesButton) tabRolesButton.className = tab === "roles" ? activeClass : inactiveClass;
    if (tabUsersButton) tabUsersButton.className = tab === "usuarios" ? activeClass : inactiveClass;
    tabHistoryButton.className = tab === "historial" ? activeClass : inactiveClass;

    if (tab === "agentes") {
      createActionButton.classList.remove("hidden");
      createActionButton.onclick = openCreateAgentModal;
      createActionButton.querySelector("span").textContent = getI18nText("dashboard.createAgent", null, "Nuevo Agente");
    } else if (tab === "fuentes") {
      createActionButton.classList.remove("hidden");
      createActionButton.onclick = openCreateSourceModal;
      createActionButton.querySelector("span").textContent = getI18nText("dashboard.createSource", null, "Nueva Base");
    } else if (tab === "roles") {
      createActionButton.classList.remove("hidden");
      createActionButton.onclick = openCreateRoleModal;
      createActionButton.querySelector("span").textContent = getI18nText("dashboard.createRole", null, "Nuevo Rol");
    } else if (tab === "usuarios") {
      createActionButton.classList.remove("hidden");
      createActionButton.onclick = openCreateUserModal;
      createActionButton.querySelector("span").textContent = getI18nText("dashboard.createUser", null, "Nuevo Usuario");
    } else {
      createActionButton.classList.add("hidden");
    }

    if (window.lucide) lucide.createIcons();
  }

  // ------------------------------------------------------------------
  // Módulo de Usuarios (Show -> Edit -> Update)
  // ------------------------------------------------------------------

  /** Muestra la ficha detallada de un usuario */
  function viewUserDetail(userId) {
    currentShowUserId = userId;
    fetch("/api/usuario/" + userId)
      .then(function (res) { return res.json(); })
      .then(function (u) {
        showUserAvatar.textContent = (u.usuario || "US").slice(0, 2).toUpperCase();
        showUserName.textContent = u.usuario;
        showUserId.textContent = "ID: " + u.id;
        showUserRole.textContent = u.rol === "admin" ? "Administrador" : "Usuario Estándar";
        showUserDate.textContent = u.creado_en ? u.creado_en.slice(0, 16) : "Reciente";

        showUserModal.classList.remove("hidden");
        showUserModal.classList.add("flex");
        if (window.lucide) lucide.createIcons();
      })
      .catch(function () {
        showToast("No se pudo cargar la ficha del usuario.");
      });
  }

  function closeUserDetailModal() {
    showUserModal.classList.add("hidden");
    showUserModal.classList.remove("flex");
    currentShowUserId = null;
  }

  function proceedToEditFromShow() {
    var id = currentShowUserId;
    closeUserDetailModal();
    if (id) openEditUserModal(id);
  }

  function openCreateUserModal() {
    userIdInput.value = "";
    userModeInput.value = "crear";
    userNameInput.value = "";
    userRoleInput.value = "usuario";
    userPasswordInput.value = "";
    userPasswordInput.required = true;
    userPwdHelp.textContent = "(obligatoria)";
    userModalTitle.textContent = getI18nText("dashboard.createUser", null, "Nuevo Usuario");

    userModal.classList.remove("hidden");
    userModal.classList.add("flex");
    setTimeout(function () { userNameInput.focus(); }, 50);
  }

  function openEditUserModal(userId) {
    fetch("/api/usuario/" + userId)
      .then(function (res) { return res.json(); })
      .then(function (u) {
        userIdInput.value = u.id;
        userModeInput.value = "editar";
        userNameInput.value = u.usuario;
        userRoleInput.value = u.rol || "usuario";
        userPasswordInput.value = "";
        userPasswordInput.required = false;
        userPwdHelp.textContent = "(dejar en blanco para mantener la actual)";
        userModalTitle.textContent = "Editar Usuario: " + u.usuario;

        userModal.classList.remove("hidden");
        userModal.classList.add("flex");
      })
      .catch(function () {
        showToast("No se pudo cargar la información del usuario.");
      });
  }

  function closeUserModal() {
    userModal.classList.add("hidden");
    userModal.classList.remove("flex");
  }

  userForm.addEventListener("submit", function (e) {
    e.preventDefault();
    userSaveButton.disabled = true;

    var mode = userModeInput.value;
    var id = userIdInput.value;
    var name = userNameInput.value.trim();
    var role = userRoleInput.value;
    var password = userPasswordInput.value.trim();

    if (!name) {
      showToast("El nombre de usuario es obligatorio.");
      userSaveButton.disabled = false;
      return;
    }
    if (mode === "crear" && !password) {
      showToast("La contraseña es obligatoria para un nuevo usuario.");
      userSaveButton.disabled = false;
      return;
    }

    var url = mode === "crear" ? "/api/usuarios" : "/api/usuario/" + id;
    var payload = { usuario: name, rol: role };
    if (password) payload.password = password;

    fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(function (res) { return res.json().then(function (d) { return { ok: res.ok, data: d }; }); })
      .then(function (result) {
        if (!result.ok) throw new Error(result.data.error || "Error al guardar el usuario.");
        closeUserModal();
        showToast(mode === "crear" ? "Usuario creado exitosamente." : "Usuario actualizado exitosamente.", "exito");
        setTimeout(function () { window.location.reload(); }, 600);
      })
      .catch(function (error) {
        showToast(error.message);
      })
      .finally(function () {
        userSaveButton.disabled = false;
      });
  });

  function confirmDeleteUser(userId, userName) {
    deleteTitle.textContent = "¿Eliminar usuario '" + userName + "'?";
    deleteDesc.textContent = "Se revocarán todos los permisos de acceso para esta cuenta. Esta acción no se puede deshacer.";
    deleteCallbackAction = function () {
      fetch("/api/usuario/" + userId, { method: "DELETE" })
        .then(function (res) { return res.json().then(function (d) { return { ok: res.ok, data: d }; }); })
        .then(function (result) {
          if (!result.ok) throw new Error(result.data.error || "No se pudo eliminar el usuario.");
          closeDeleteModal();
          showToast("Usuario eliminado.", "exito");
          setTimeout(function () { window.location.reload(); }, 600);
        })
        .catch(function (error) {
          showToast(error.message);
        });
    };
    deleteModal.classList.remove("hidden");
    deleteModal.classList.add("flex");
  }

  // ------------------------------------------------------------------
  // Modal Mi Perfil (Configurar Cuenta en Sesión)
  // ------------------------------------------------------------------
  function openMyProfileModal() {
    profilePasswordInput.value = "";
    myProfileModal.classList.remove("hidden");
    myProfileModal.classList.add("flex");
  }

  function closeMyProfileModal() {
    myProfileModal.classList.add("hidden");
    myProfileModal.classList.remove("flex");
  }

  myProfileForm.addEventListener("submit", function (e) {
    e.preventDefault();
    profileSaveButton.disabled = true;

    var name = profileNameInput.value.trim();
    var password = profilePasswordInput.value.trim();

    fetch("/api/perfil", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ usuario: name, password: password }),
    })
      .then(function (res) { return res.json().then(function (d) { return { ok: res.ok, data: d }; }); })
      .then(function (result) {
        if (!result.ok) throw new Error(result.data.error || "Error al actualizar perfil.");
        closeMyProfileModal();
        showToast("Perfil actualizado correctamente.", "exito");
        setTimeout(function () { window.location.reload(); }, 600);
      })
      .catch(function (error) {
        showToast(error.message);
      })
      .finally(function () {
        profileSaveButton.disabled = false;
      });
  });

  // ------------------------------------------------------------------
  // Manejo de Avatar e Imágenes
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
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (!d.ok) throw new Error(d.error || "Error al subir imagen.");
        updateAvatarUrlInput(d.url, prefix);
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

  // ------------------------------------------------------------------
  // Modal Agente (Crear / Editar)
  // ------------------------------------------------------------------
  function openCreateAgentModal() {
    agentModeInput.value = "crear";
    agentNameInput.value = "";
    agentNameInput.disabled = false;
    agentProfileInput.value = "";
    agentIdentitySelect.value = "";
    agentCustomPromptInput.value = "";
    agentCustomBlock.classList.add("hidden");
    agentModalTitle.textContent = getI18nText("dashboard.createAgent", null, "Crear Nuevo Agente");

    clearSelectedAvatar("dash");

    agentSourcesList.querySelectorAll("input[type=checkbox]").forEach(function (cb) {
      cb.checked = false;
    });

    agentModal.classList.remove("hidden");
    var backdrop = document.getElementById("drawer-agente-dash-backdrop");
    var panel = document.getElementById("drawer-agente-dash-panel");
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
    setTimeout(function () { agentNameInput.focus(); }, 100);
  }

  function openEditAgentModal(name) {
    fetch("/api/agente/" + encodeURIComponent(name))
      .then(function (res) { return res.json(); })
      .then(function (data) {
        agentModeInput.value = "editar";
        agentNameInput.value = data.nombre;
        agentNameInput.disabled = true;
        agentProfileInput.value = data.perfil || "";
        agentModalTitle.textContent = "Editar Agente: " + data.nombre;

        if (data.avatar_url) {
          updateAvatarUrlInput(data.avatar_url, "dash");
        } else {
          clearSelectedAvatar("dash");
          var initSpan = document.getElementById("dash-avatar-preview-initials");
          if (initSpan) initSpan.textContent = (data.nombre || "AG").slice(0, 2).toUpperCase();
        }

        var sourceIds = (data.fuentes || []).map(function (f) { return f.id; });
        agentSourcesList.querySelectorAll("input[type=checkbox]").forEach(function (cb) {
          cb.checked = sourceIds.indexOf(parseInt(cb.value, 10)) !== -1;
        });

        if (data.identidad.personalizada) {
          agentIdentitySelect.value = "personalizada";
          agentCustomPromptInput.value = data.identidad.prompt || "";
          agentCustomBlock.classList.remove("hidden");
        } else {
          agentIdentitySelect.value = data.identidad.clave || "";
          agentCustomPromptInput.value = "";
          agentCustomBlock.classList.add("hidden");
        }

        agentModal.classList.remove("hidden");
        var backdrop = document.getElementById("drawer-agente-dash-backdrop");
        var panel = document.getElementById("drawer-agente-dash-panel");
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
      })
      .catch(function () {
        showToast("No se pudo cargar la información del agente.");
      });
  }

  function closeAgentModal() {
    var backdrop = document.getElementById("drawer-agente-dash-backdrop");
    var panel = document.getElementById("drawer-agente-dash-panel");
    if (backdrop) {
      backdrop.classList.remove("opacity-100");
      backdrop.classList.add("opacity-0");
    }
    if (panel) {
      panel.classList.remove("translate-x-0");
      panel.classList.add("translate-x-full");
    }
    setTimeout(function () {
      agentModal.classList.add("hidden");
    }, 300);
  }

  agentIdentitySelect.addEventListener("change", function () {
    var isCustom = agentIdentitySelect.value === "personalizada";
    agentCustomBlock.classList.toggle("hidden", !isCustom);
    if (!isCustom) agentCustomPromptInput.value = "";
  });

  agentForm.addEventListener("submit", function (e) {
    e.preventDefault();
    agentSaveButton.disabled = true;

    var mode = agentModeInput.value;
    var name = agentNameInput.value.trim();
    var profile = agentProfileInput.value.trim();
    var custom = agentCustomPromptInput.value.trim();
    var key = agentIdentitySelect.value;
    var avatarUrl = document.getElementById("dash-campo-avatar-url") ? document.getElementById("dash-campo-avatar-url").value.trim() : "";

    var selectedSources = [];
    agentSourcesList.querySelectorAll("input[type=checkbox]:checked").forEach(function (cb) {
      selectedSources.push(parseInt(cb.value, 10));
    });

    var url = mode === "crear" ? "/api/agentes" : "/api/agente/" + encodeURIComponent(name) + "/editar";
    var payload = {
      nombre: name,
      perfil: profile,
      avatar_url: avatarUrl,
      fuentes: selectedSources,
    };

    if (custom) payload.identidad_custom = custom;
    else if (key && key !== "personalizada") payload.identidad = key;

    fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(function (res) { return res.json().then(function (d) { return { ok: res.ok, data: d }; }); })
      .then(function (result) {
        if (!result.ok) throw new Error(result.data.error || "Error al guardar el agente.");
        closeAgentModal();
        showToast("Agente guardado exitosamente.", "exito");
        setTimeout(function () { window.location.reload(); }, 600);
      })
      .catch(function (error) {
        showToast(error.message);
      })
      .finally(function () {
        agentSaveButton.disabled = false;
      });
  });

  // ------------------------------------------------------------------
  // Modal Base de Conocimiento (Crear / Editar)
  // ------------------------------------------------------------------
  function openCreateSourceModal() {
    sourceIdInput.value = "";
    sourceNameInput.value = "";
    sourceContentInput.value = "";
    sourceModalTitle.textContent = getI18nText("dashboard.createSource", null, "Nueva Base de Conocimiento");
    sourceModal.classList.remove("hidden");
    sourceModal.classList.add("flex");
    setTimeout(function () { sourceNameInput.focus(); }, 50);
  }

  function openEditSourceModal(id) {
    fetch("/api/fuentes/" + id)
      .then(function (res) { return res.json(); })
      .then(function (data) {
        sourceIdInput.value = data.id;
        sourceNameInput.value = data.nombre;
        sourceContentInput.value = data.contenido || "";
        sourceModalTitle.textContent = "Editar Base de Conocimiento";
        sourceModal.classList.remove("hidden");
        sourceModal.classList.add("flex");
      })
      .catch(function () {
        showToast("No se pudo cargar la base de conocimiento.");
      });
  }

  function closeSourceModal() {
    sourceModal.classList.add("hidden");
    sourceModal.classList.remove("flex");
  }

  sourceForm.addEventListener("submit", function (e) {
    e.preventDefault();
    sourceSaveButton.disabled = true;

    var id = sourceIdInput.value;
    var name = sourceNameInput.value.trim();
    var content = sourceContentInput.value.trim();

    if (!name) {
      showToast("Escribe un nombre para la base.");
      sourceSaveButton.disabled = false;
      return;
    }

    var url = id ? "/api/fuentes/" + id : "/api/fuentes";

    fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nombre: name, contenido: content }),
    })
      .then(function (res) { return res.json().then(function (d) { return { ok: res.ok, data: d }; }); })
      .then(function (result) {
        if (!result.ok) throw new Error(result.data.error || "Error al guardar la base.");
        closeSourceModal();
        showToast("Base de conocimiento guardada.", "exito");
        setTimeout(function () { window.location.reload(); }, 600);
      })
      .catch(function (error) {
        showToast(error.message);
      })
      .finally(function () {
        sourceSaveButton.disabled = false;
      });
  });

  // ------------------------------------------------------------------
  // Modal Rol e Identidad (Crear / Editar)
  // ------------------------------------------------------------------
  function openCreateRoleModal() {
    roleIdInput.value = "";
    roleKeyInput.value = "";
    roleKeyInput.disabled = false;
    roleNameInput.value = "";
    roleDescInput.value = "";
    rolePromptInput.value = "";
    roleModalTitle.textContent = getI18nText("dashboard.createRole", null, "Nuevo Rol / Identidad");
    roleModal.classList.remove("hidden");
    roleModal.classList.add("flex");
    setTimeout(function () { roleKeyInput.focus(); }, 50);
  }

  function openEditRoleModal(id) {
    fetch("/api/roles/" + id)
      .then(function (res) { return res.json(); })
      .then(function (data) {
        roleIdInput.value = data.id;
        roleKeyInput.value = data.clave;
        roleNameInput.value = data.nombre;
        roleDescInput.value = data.descripcion || "";
        rolePromptInput.value = data.prompt || "";
        roleModalTitle.textContent = "Editar Rol: " + data.nombre;
        roleModal.classList.remove("hidden");
        roleModal.classList.add("flex");
      })
      .catch(function () {
        showToast("No se pudo cargar la información del rol.");
      });
  }

  function closeRoleModal() {
    roleModal.classList.add("hidden");
    roleModal.classList.remove("flex");
  }

  roleForm.addEventListener("submit", function (e) {
    e.preventDefault();
    roleSaveButton.disabled = true;

    var id = roleIdInput.value;
    var key = roleKeyInput.value.trim().toLowerCase();
    var name = roleNameInput.value.trim();
    var desc = roleDescInput.value.trim();
    var prompt = rolePromptInput.value.trim();

    if (!key || !name || !prompt) {
      showToast("La clave, el nombre y el prompt son obligatorios.");
      roleSaveButton.disabled = false;
      return;
    }

    var url = id ? "/api/roles/" + id : "/api/roles";

    fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        clave: key,
        nombre: name,
        descripcion: desc,
        prompt: prompt,
      }),
    })
      .then(function (res) { return res.json().then(function (d) { return { ok: res.ok, data: d }; }); })
      .then(function (result) {
        if (!result.ok) throw new Error(result.data.error || "Error al guardar el rol.");
        closeRoleModal();
        showToast("Rol guardado exitosamente.", "exito");
        setTimeout(function () { window.location.reload(); }, 600);
      })
      .catch(function (error) {
        showToast(error.message);
      })
      .finally(function () {
        roleSaveButton.disabled = false;
      });
  });

  // ------------------------------------------------------------------
  // Confirmaciones de Eliminación
  // ------------------------------------------------------------------
  function confirmDeleteAgent(name) {
    deleteTitle.textContent = "¿Eliminar al agente '" + name + "'?";
    deleteDesc.textContent = "Se eliminará toda la memoria, perfil, hilos de chat y mensajes de este agente. Esta acción no se puede deshacer.";
    deleteCallbackAction = function () {
      fetch("/api/agente/" + encodeURIComponent(name), { method: "DELETE" })
        .then(function (r) { return r.json(); })
        .then(function () {
          closeDeleteModal();
          showToast("Agente eliminado.", "exito");
          setTimeout(function () { window.location.reload(); }, 600);
        })
        .catch(function () {
          showToast("No se pudo eliminar el agente.");
        });
    };
    deleteModal.classList.remove("hidden");
    deleteModal.classList.add("flex");
  }

  function confirmDeleteSource(id, name) {
    deleteTitle.textContent = "¿Eliminar base '" + name + "'?";
    deleteDesc.textContent = "Se desvinculará de todos los agentes que la utilizan.";
    deleteCallbackAction = function () {
      fetch("/api/fuentes/" + id, { method: "DELETE" })
        .then(function (r) { return r.json(); })
        .then(function () {
          closeDeleteModal();
          showToast("Base de conocimiento eliminada.", "exito");
          setTimeout(function () { window.location.reload(); }, 600);
        })
        .catch(function () {
          showToast("No se pudo eliminar la base.");
        });
    };
    deleteModal.classList.remove("hidden");
    deleteModal.classList.add("flex");
  }

  function confirmDeleteRole(id, name) {
    deleteTitle.textContent = "¿Eliminar rol '" + name + "'?";
    deleteDesc.textContent = "Los agentes que utilicen este rol se reasignarán automáticamente al rol Básico por defecto.";
    deleteCallbackAction = function () {
      fetch("/api/roles/" + id, { method: "DELETE" })
        .then(function (r) { return r.json(); })
        .then(function () {
          closeDeleteModal();
          showToast("Rol eliminado.", "exito");
          setTimeout(function () { window.location.reload(); }, 600);
        })
        .catch(function () {
          showToast("No se pudo eliminar el rol.");
        });
    };
    deleteModal.classList.remove("hidden");
    deleteModal.classList.add("flex");
  }

  function closeDeleteModal() {
    deleteModal.classList.add("hidden");
    deleteModal.classList.remove("flex");
    deleteCallbackAction = null;
  }

  deleteConfirmButton.addEventListener("click", function () {
    if (deleteCallbackAction) deleteCallbackAction();
  });

  // ------------------------------------------------------------------
  // Mantenedor de Conversaciones (Filtro, Explorador, Transcripciones)
  // ------------------------------------------------------------------
  function viewAgentConversations(name) {
    switchDashboardTab("historial");
    if (conversationsAgentFilter) {
      conversationsAgentFilter.value = name;
    }
    filterConversationsByAgent(name);
  }

  function filterConversationsByAgent(agentNameParam) {
    var url = agentNameParam ? "/api/sesiones?agente=" + encodeURIComponent(agentNameParam) : "/api/sesiones";
    fetch(url)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var sessions = data.sesiones || [];
        if (sessionsCounter) {
          sessionsCounter.textContent = sessions.length + " conversaciones";
        }
        threadsList.innerHTML = "";
        if (!sessions.length) {
          threadsList.innerHTML = '<p class="text-center text-xs text-zinc-500 py-12">No hay conversaciones registradas' + (agentNameParam ? ' para ' + agentNameParam : '') + '.</p>';
          return;
        }

        sessions.forEach(function (ses) {
          var btn = document.createElement("button");
          btn.className = "w-full text-left rounded-2xl border border-white/5 bg-white/[0.02] p-4 transition hover:border-[#1a73e8]/40 hover:bg-white/[0.06] focus:border-[#1a73e8] focus:bg-white/[0.06]";
          btn.innerHTML =
            '<div class="flex items-center justify-between">' +
            '  <span class="heroui-chip heroui-chip-primary text-[10px] py-0.5 px-2 font-bold">' + ses.agente_nombre + '</span>' +
            '  <span class="text-[11px] text-zinc-500">' + (ses.actualizado_en ? ses.actualizado_en.slice(0, 16) : "") + '</span>' +
            '</div>' +
            '<p class="mt-2 truncate text-xs font-bold text-white">' + ses.titulo + '</p>' +
            '<p class="mt-1 text-[11px] text-zinc-400 truncate">' + (ses.ultimo_mensaje || '(Sin mensajes aún)') + '</p>' +
            '<div class="mt-2 flex items-center gap-2 text-[10px] text-zinc-500">' +
            '  <i data-lucide="message-circle" class="h-3 w-3"></i>' +
            '  <span>' + ses.total_mensajes + ' mensaje(s)</span>' +
            '</div>';

          btn.addEventListener("click", function () {
            loadSessionTranscript(ses.id, ses.agente_nombre, ses.titulo);
          });
          threadsList.appendChild(btn);
        });

        if (window.lucide) lucide.createIcons();

        if (sessions[0]) {
          loadSessionTranscript(sessions[0].id, sessions[0].agente_nombre, sessions[0].titulo);
        }
      });
  }

  function loadSessionTranscript(sessionId, agentNameParam, title) {
    activeViewerSessionId = sessionId;
    viewerTitle.textContent = title || "Conversación";
    viewerAgent.textContent = "Historial completo con " + agentNameParam;
    
    viewerAgentBadge.textContent = agentNameParam;
    viewerAgentBadge.classList.remove("hidden");
    
    viewerDeleteButton.classList.remove("hidden");
    viewerOpenChatButton.classList.remove("hidden");
    viewerOpenChatButton.href = "/agente/" + encodeURIComponent(agentNameParam);

    viewerMessagesContainer.innerHTML = '<div class="py-12 text-center text-xs text-zinc-400">Cargando transcripción…</div>';

    fetch("/api/sesion/" + sessionId)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var messages = data.mensajes || [];
        viewerMessagesContainer.innerHTML = "";
        if (!messages.length) {
          viewerMessagesContainer.innerHTML = '<div class="py-12 text-center text-xs text-zinc-500">No hay mensajes en esta conversación aún.</div>';
          return;
        }

        messages.forEach(function (m) {
          var row = document.createElement("div");
          row.className = "flex " + (m.rol === "user" ? "justify-end" : "justify-start");
          
          var box = document.createElement("div");
          box.className = "max-w-[85%]";

          var bubble = document.createElement("div");
          if (m.rol === "user") {
            bubble.className = "rounded-2xl rounded-br-sm bg-[#1a73e8] px-4 py-3 text-xs text-white shadow";
            bubble.textContent = m.mensaje;
          } else {
            bubble.className = "rounded-2xl rounded-bl-sm border border-white/10 bg-[#1e1f20] px-4 py-3 text-xs leading-relaxed text-[#e3e3e3] shadow prose-chat";
            if (window.marked && window.DOMPurify) {
              bubble.innerHTML = DOMPurify.sanitize(marked.parse(m.mensaje, { breaks: true, gfm: true }));
            } else {
              bubble.textContent = m.mensaje;
            }
          }

          var meta = document.createElement("div");
          meta.className = "text-[10px] text-[#c4c7c5] mt-1 " + (m.rol === "user" ? "text-right" : "text-left");
          meta.textContent = (m.rol === "user" ? "Usuario" : agentNameParam) + " · " + (m.fecha || "") + " " + (m.hora || "");

          box.appendChild(bubble);
          box.appendChild(meta);
          row.appendChild(box);
          viewerMessagesContainer.appendChild(row);
        });

        viewerMessagesContainer.scrollTop = viewerMessagesContainer.scrollHeight;
      })
      .catch(function () {
        viewerMessagesContainer.innerHTML = '<div class="py-12 text-center text-xs text-[#f28b82]">Error al cargar la transcripción.</div>';
      });
  }

  function deleteSessionFromViewer() {
    if (!activeViewerSessionId) return;
    if (!confirm("¿Deseas eliminar este hilo de conversación del mantenedor?")) return;

    fetch("/api/sesion/" + activeViewerSessionId, { method: "DELETE" })
      .then(function (r) { return r.json(); })
      .then(function () {
        showToast("Conversación eliminada del mantenedor.", "exito");
        setTimeout(function () { window.location.reload(); }, 600);
      });
  }

  // Exposición de funciones en window para botones HTML
  window.cambiarTabDashboard = switchDashboardTab;
  window.verDetalleUsuario = viewUserDetail;
  window.cerrarModalShowUsuario = closeUserDetailModal;
  window.procederEditarDesdeShow = proceedToEditFromShow;
  window.abrirModalCrearUsuarioDash = openCreateUserModal;
  window.abrirModalEditarUsuarioDash = openEditUserModal;
  window.cerrarModalUsuarioDash = closeUserModal;
  window.confirmarEliminarUsuarioDash = confirmDeleteUser;
  window.abrirModalMiPerfil = openMyProfileModal;
  window.cerrarModalMiPerfil = closeMyProfileModal;
  window.subirAvatarArchivo = uploadAvatarFile;
  window.actualizarAvatarUrlInput = updateAvatarUrlInput;
  window.limpiarAvatarSeleccionado = clearSelectedAvatar;
  window.abrirModalCrearAgenteDash = openCreateAgentModal;
  window.abrirModalEditarAgenteDash = openEditAgentModal;
  window.cerrarModalAgenteDash = closeAgentModal;
  window.abrirModalCrearFuenteDash = openCreateSourceModal;
  window.abrirModalEditarFuenteDash = openEditSourceModal;
  window.cerrarModalFuenteDash = closeSourceModal;
  window.abrirModalCrearRolDash = openCreateRoleModal;
  window.abrirModalEditarRolDash = openEditRoleModal;
  window.cerrarModalRolDash = closeRoleModal;
  window.confirmarEliminarAgenteDash = confirmDeleteAgent;
  window.confirmarEliminarFuenteDash = confirmDeleteSource;
  window.confirmarEliminarRolDash = confirmDeleteRole;
  window.cerrarModalEliminarDash = closeDeleteModal;
  window.verConversacionesAgente = viewAgentConversations;
  window.filtrarConversacionesPorAgente = filterConversationsByAgent;
  window.cargarTranscripcionSesion = loadSessionTranscript;
  window.eliminarSesionDesdeVisor = deleteSessionFromViewer;

  // Escape para cerrar modales
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      closeAgentModal();
      closeSourceModal();
      closeRoleModal();
      closeUserDetailModal();
      closeUserModal();
      closeMyProfileModal();
      closeDeleteModal();
    }
  });
})();
