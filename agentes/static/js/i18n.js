/**
 * Motor de Internacionalización (i18n) para la plataforma THEYTHINK AI.
 * 
 * Permite cambiar dinámicamente entre 6 idiomas:
 * - Español (es)
 * - English (en)
 * - Français (fr)
 * - Português (pt)
 * - 한국어 (ko)
 * - 中文 (zh)
 * 
 * Persiste la preferencia en localStorage ('theythink_lang') y traduce
 * elementos de forma reactiva en el DOM.
 */

(function (root, factory) {
  if (typeof define === "function" && define.amd) {
    define([], factory);
  } else if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.i18n = factory();
  }
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  // Idioma por defecto y lista de idiomas soportados
  var DEFAULT_LANGUAGE = "es";
  var SUPPORTED_LANGUAGES = ["es", "en", "fr", "pt", "ko", "zh"];
  var STORAGE_KEY = "theythink_lang";

  // Metadatos de idiomas con nombres nativos, insignias y subtítulos regionales
  var LANGUAGE_METADATA = {
    es: { code: "es", name: "Español", shortName: "ES", subtitle: "España / Latinoamérica", badgeBg: "bg-[#EA4335]/15 text-[#EA4335] dark:bg-[#EA4335]/25 dark:text-[#f28b82]" },
    en: { code: "en", name: "English", shortName: "EN", subtitle: "United States / Global", badgeBg: "bg-[#1a73e8]/15 text-[#1a73e8] dark:bg-[#4285F4]/25 dark:text-[#8ab4f8]" },
    fr: { code: "fr", name: "Français", shortName: "FR", subtitle: "France / Europe", badgeBg: "bg-[#a142f4]/15 text-[#a142f4] dark:bg-[#a142f4]/25 dark:text-[#d7aefb]" },
    pt: { code: "pt", name: "Português", shortName: "PT", subtitle: "Brasil / Portugal", badgeBg: "bg-[#34A853]/15 text-[#34A853] dark:bg-[#34A853]/25 dark:text-[#81c995]" },
    ko: { code: "ko", name: "한국어", shortName: "KO", subtitle: "대한민국 (Korean)", badgeBg: "bg-[#FBBC04]/20 text-[#b06000] dark:bg-[#FBBC04]/30 dark:text-[#fdd663]" },
    zh: { code: "zh", name: "中文", shortName: "ZH", subtitle: "简体中文 (Chinese)", badgeBg: "bg-[#EA4335]/15 text-[#d93025] dark:bg-[#EA4335]/25 dark:text-[#f28b82]" },
  };

  // Diccionarios de traducción para cada idioma
  var TRANSLATIONS = {
    // -------------------------------------------------------------
    // ESPAÑOL (es)
    // -------------------------------------------------------------
    es: {
      common: {
        appName: "THEYTHINK AI",
        tagline: "Plataforma Inteligente de Agentes Autónomos",
        save: "Guardar",
        saving: "Guardando…",
        cancel: "Cancelar",
        delete: "Eliminar",
        edit: "Editar",
        create: "Crear",
        view: "Ver",
        close: "Cerrar",
        search: "Buscar…",
        actions: "Acciones",
        connected: "Conectado",
        configureApiKey: "Configurar API Key",
        loading: "Cargando…",
        success: "Éxito",
        error: "Error",
        confirm: "Confirmar",
        back: "Volver",
        logout: "Cerrar sesión",
        login: "Iniciar sesión",
        adminAccess: "Acceso Administrador",
        dashboard: "Dashboard",
        publicHome: "Inicio Público",
        home: "Inicio",
        developedBy: "Desarrollado por",
        lightMode: "Modo claro",
        darkMode: "Modo oscuro",
        switchTheme: "Cambiar modo claro / oscuro",
        selectLanguage: "Seleccionar idioma",
        total: "Total",
        active: "Activo",
        system: "Sistema",
        custom: "Personalizado",
        allRightsReserved: "Todos los derechos reservados",
      },
      nav: {
        brandSubtitle: "Plataforma de Agentes",
        goToDashboard: "Dashboard",
        loginAction: "Iniciar Sesión",
        logoutAction: "Cerrar Sesión",
        adminBadge: "ADMIN",
        myProfile: "Mi Cuenta",
      },
      hero: {
        badge: "Plataforma Inteligente de Agentes Autónomos",
        titlePrefix: "Inteligencia Artificial con",
        titleHighlight: "Memoria y Conocimiento",
        titleSuffix: "Especializado",
        description: "Interactúa con agentes inteligentes que aprenden de cada conversación, consultan bases documentales modulares y adoptan roles a medida.",
        ctaDashboard: "Ir al Panel Administrativo",
        ctaCatalog: "Ver Agentes Disponibles",
        ctaLogin: "Iniciar Sesión para Chatear",
        ctaExplore: "Explorar Capacidades",
      },
      features: {
        badge: "Capacidades Principales",
        title: "Todo lo que puedes lograr en la plataforma",
        subtitle: "Diseñado con arquitectura modular para resolver problemas con memoria activa y fuentes temáticas.",
        f1Title: "Memoria Viva y Aprendizaje",
        f1Desc: "El agente retiene datos clave, preferencias y aprendizajes de interacciones previas, ofreciendo continuidad y contexto en cada diálogo.",
        f1Foot: "Retención automática de hechos",
        f2Title: "Bases de Conocimiento Temáticas",
        f2Desc: "Carga manual o masiva de documentos y manuales independientes. Asocia múltiples bases a los agentes para dotarlos de información precisa.",
        f2Foot: "Conocimiento desacoplado",
        f3Title: "Roles e Identidades en Tiempo Real",
        f3Desc: "Ajusta el estilo comunicativo (profesor, analista, creador de relatos, mentor) y pule los System Prompts directamente desde SQLite.",
        f3Foot: "Edición y pulido de prompts",
        f4Title: "Hilos de Conversación Aislados",
        f4Desc: "Crea múltiples sesiones de chat con cada agente. Titulación automática, renombrado y exploración de transcripciones sin saturar contexto.",
        f4Foot: "Historiales independientes",
        f5Title: "Motor AI de Alto Rendimiento",
        f5Desc: "Respuestas rápidas, análisis estructurados en Markdown enriquecido, bloques de código legibles y alta capacidad de síntesis.",
        f5Foot: "Formato rico y fluidez",
        f6Title: "Administración & Usuarios",
        f6Desc: "Dashboard integral para gestionar agentes, bases, roles y usuarios con el flujo completo de inspección (Show), edición (Edit) y actualización (Update).",
        f6Foot: "Control total y seguridad",
      },
      howItWorks: {
        badge: "Flujo Simple",
        title: "Comienza a conversar en 3 pasos",
        step1Num: "1",
        step1Title: "Elige o Crea un Agente",
        step1Desc: "Selecciona el perfil o crea un nuevo agente según el tema que necesitas resolver.",
        step2Num: "2",
        step2Title: "Asocia Conocimiento",
        step2Desc: "Vincula bases temáticas con manuales o documentos para que el agente los consulte.",
        step3Num: "3",
        step3Title: "Inicia la Conversación",
        step3Desc: "Interactúa en múltiples hilos y disfruta de respuestas contextuales con memoria activa.",
      },
      catalog: {
        badge: "Catálogo Activo",
        title: "Agentes Listos para Conversar",
        subtitle: "Selecciona un agente para abrir un hilo de chat",
        manageDashboard: "Gestionar en Dashboard",
        chatWith: "Chatear con {name}",
        loginToChat: "Iniciar sesión para chatear",
        noAgents: "No hay agentes registrados en este momento.",
        defaultDescription: "Agente especializado listo para responder.",
      },
      loginPage: {
        title: "Iniciar Sesión",
        subtitle: "Inicia sesión para interactuar con tus agentes y gestionar la plataforma",
        userLabel: "Usuario",
        userPlaceholder: "ej. admin",
        passwordLabel: "Contraseña",
        passwordPlaceholder: "••••••••",
        defaultCredentialsTitle: "Credenciales por defecto:",
        defaultUser: "Usuario:",
        defaultPass: "Contraseña:",
        submitButton: "Ingresar",
        backToHome: "Volver a la página principal",
        invalidCredentials: "Credenciales inválidas. Verifica tu usuario y contraseña.",
      },
      chat: {
        newChat: "Nueva Conversación",
        searchHistory: "Buscar en historial…",
        emptyHistory: "No hay mensajes en esta sesión. ¡Comienza a escribir!",
        renameChat: "Renombrar Conversación",
        renamePrompt: "Introduce el nuevo título del hilo:",
        deleteChatTitle: "¿Eliminar Conversación?",
        deleteChatConfirm: "¿Estás seguro de eliminar este hilo de conversación?",
        agentSettings: "Ajustes del Agente",
        manageAgent: "Gestionar Agente",
        clearMemory: "Limpiar memoria",
        clearMemoryTitle: "¿Limpiar Memoria del Agente?",
        clearMemoryConfirm: "Se eliminarán todas las notas acumuladas en la memoria activa de este agente.",
        basesCount: "{count} base(s)",
        enterToSend: "Enter ↵ para enviar",
        shiftEnter: "Shift+Enter para nueva línea",
        typePlaceholder: "Escribe tu mensaje a {name}… (Shift+Enter para nueva línea)",
        copiedToast: "Código copiado al portapapeles",
        copyCode: "Copiar",
        copyMessage: "Copiar mensaje",
        memoryUpdated: "Memoria del agente actualizada",
        memoryCleared: "Memoria eliminada correctamente",
        agentUpdated: "Agente actualizado exitosamente",
        sessionRenamed: "Conversación renombrada",
        sessionDeleted: "Conversación eliminada",
        thinking: "Generando respuesta…",
        continuousMemoryFooter: "Memoria Continua respaldada en SQLite",
      },
      dashboard: {
        title: "THEYTHINK AI Dashboard",
        subtitle: "Agentes, Bases, Roles, Usuarios y Conversaciones",
        kpiAgents: "Agentes",
        kpiSources: "Bases de Conocimiento",
        kpiRoles: "Roles & Identidades",
        kpiUsers: "Usuarios",
        kpiMessages: "Mensajes Totales",
        tabAgents: "Agentes",
        tabSources: "Bases de Conocimiento",
        tabRoles: "Roles & Prompts",
        tabUsers: "Usuarios",
        tabConversations: "Conversaciones",
        createAgent: "Nuevo Agente",
        createSource: "Nueva Base",
        createRole: "Nuevo Rol",
        createUser: "Nuevo Usuario",
        tableName: "Nombre",
        tableRole: "Rol",
        tableSources: "Bases Asociadas",
        tableUpdated: "Actualizado",
        tableActions: "Acciones",
        tableContentLength: "Tamaño",
        tableCreated: "Creado",
        tableKey: "Clave",
        tableType: "Tipo",
        tableMessages: "Mensajes",
        tableAgent: "Agente",
        tableTitle: "Título",
        noData: "No hay registros disponibles.",
      },
    },

    // -------------------------------------------------------------
    // ENGLISH (en)
    // -------------------------------------------------------------
    en: {
      common: {
        appName: "THEYTHINK AI",
        tagline: "Autonomous Intelligent Agents Platform",
        save: "Save",
        saving: "Saving…",
        cancel: "Cancel",
        delete: "Delete",
        edit: "Edit",
        create: "Create",
        view: "View",
        close: "Close",
        search: "Search…",
        actions: "Actions",
        connected: "Connected",
        configureApiKey: "Configure API Key",
        loading: "Loading…",
        success: "Success",
        error: "Error",
        confirm: "Confirm",
        back: "Back",
        logout: "Log out",
        login: "Log in",
        adminAccess: "Admin Access",
        dashboard: "Dashboard",
        publicHome: "Public Home",
        home: "Home",
        developedBy: "Developed by",
        lightMode: "Light mode",
        darkMode: "Dark mode",
        switchTheme: "Toggle light / dark mode",
        selectLanguage: "Select language",
        total: "Total",
        active: "Active",
        system: "System",
        custom: "Custom",
        allRightsReserved: "All rights reserved",
      },
      nav: {
        brandSubtitle: "Agents Platform",
        goToDashboard: "Dashboard",
        loginAction: "Log In",
        logoutAction: "Log Out",
        adminBadge: "ADMIN",
        myProfile: "My Account",
      },
      hero: {
        badge: "Autonomous Intelligent Agents Platform",
        titlePrefix: "Artificial Intelligence with",
        titleHighlight: "Memory and Knowledge",
        titleSuffix: "Specialization",
        description: "Interact with intelligent agents that learn from every conversation, consult modular document repositories, and adopt tailored roles.",
        ctaDashboard: "Open Admin Dashboard",
        ctaCatalog: "View Available Agents",
        ctaLogin: "Log In to Start Chatting",
        ctaExplore: "Explore Capabilities",
      },
      features: {
        badge: "Core Capabilities",
        title: "Everything you can achieve on the platform",
        subtitle: "Engineered with modular architecture to solve problems using active memory and domain knowledge sources.",
        f1Title: "Active Memory & Learning",
        f1Desc: "The agent retains key facts, preferences, and learnings from past chats, delivering continuity and context across every dialogue.",
        f1Foot: "Automatic fact retention",
        f2Title: "Domain Knowledge Bases",
        f2Desc: "Manual or bulk upload of decoupled manuals and documents. Attach multiple knowledge bases to empower agents with accurate information.",
        f2Foot: "Decoupled domain knowledge",
        f3Title: "Real-Time Roles & Identities",
        f3Desc: "Fine-tune communicative styles (teacher, analyst, storyteller, mentor) and refine System Prompts directly inside SQLite.",
        f3Foot: "Prompt editing and tuning",
        f4Title: "Isolated Conversation Threads",
        f4Desc: "Spawn multiple chat sessions per agent. Automatic titling, renaming, and transcript exploration without context pollution.",
        f4Foot: "Independent chat histories",
        f5Title: "High-Performance AI Engine",
        f5Desc: "Ultra-fast responses, structured Markdown analysis, syntax-highlighted code blocks, and high synthesis capability.",
        f5Foot: "Rich format and fluidity",
        f6Title: "Administration & Users",
        f6Desc: "Comprehensive dashboard to manage agents, knowledge bases, roles, and users with complete inspection (Show), edit (Edit), and update flows.",
        f6Foot: "Complete control and security",
      },
      howItWorks: {
        badge: "Simple Workflow",
        title: "Start chatting in 3 steps",
        step1Num: "1",
        step1Title: "Select or Create an Agent",
        step1Desc: "Pick an existing persona or create a brand new agent suited for your specific task.",
        step2Num: "2",
        step2Title: "Attach Knowledge Bases",
        step2Desc: "Link domain knowledge collections with manuals or files for the agent to reference.",
        step3Num: "3",
        step3Title: "Start the Conversation",
        step3Desc: "Chat across isolated threads and experience contextual responses with persistent memory.",
      },
      catalog: {
        badge: "Active Catalog",
        title: "Agents Ready to Chat",
        subtitle: "Select an agent to start a new chat thread",
        manageDashboard: "Manage in Dashboard",
        chatWith: "Chat with {name}",
        loginToChat: "Log in to chat",
        noAgents: "No agents currently registered.",
        defaultDescription: "Specialized intelligent agent ready to assist.",
      },
      loginPage: {
        title: "Log In",
        subtitle: "Sign in to interact with your agents and manage the platform",
        userLabel: "Username",
        userPlaceholder: "e.g. admin",
        passwordLabel: "Password",
        passwordPlaceholder: "••••••••",
        defaultCredentialsTitle: "Default credentials:",
        defaultUser: "Username:",
        defaultPass: "Password:",
        submitButton: "Sign In",
        backToHome: "Back to home page",
        invalidCredentials: "Invalid credentials. Please verify your username and password.",
      },
      chat: {
        newChat: "New Conversation",
        searchHistory: "Search history…",
        emptyHistory: "No messages in this session yet. Start typing!",
        renameChat: "Rename Conversation",
        renamePrompt: "Enter the new title for this thread:",
        deleteChatTitle: "Delete Conversation?",
        deleteChatConfirm: "Are you sure you want to permanently delete this chat thread?",
        agentSettings: "Agent Settings",
        manageAgent: "Manage Agent",
        clearMemory: "Clear memory",
        clearMemoryTitle: "Clear Agent Memory?",
        clearMemoryConfirm: "All accumulated facts and notes in this agent's active memory will be erased.",
        basesCount: "{count} base(s)",
        enterToSend: "Enter ↵ to send",
        shiftEnter: "Shift+Enter for new line",
        typePlaceholder: "Type your message to {name}… (Shift+Enter for new line)",
        copiedToast: "Code copied to clipboard",
        copyCode: "Copy",
        copyMessage: "Copy message",
        memoryUpdated: "Agent memory successfully updated",
        memoryCleared: "Agent memory cleared successfully",
        agentUpdated: "Agent updated successfully",
        sessionRenamed: "Conversation renamed",
        sessionDeleted: "Conversation deleted",
        thinking: "Generating response…",
        continuousMemoryFooter: "Continuous Persistent Memory backed by SQLite",
      },
      dashboard: {
        title: "THEYTHINK AI Dashboard",
        subtitle: "Agents, Knowledge Bases, Roles, Users & Conversations",
        kpiAgents: "Agents",
        kpiSources: "Knowledge Bases",
        kpiRoles: "Roles & Identities",
        kpiUsers: "Users",
        kpiMessages: "Total Messages",
        tabAgents: "Agents",
        tabSources: "Knowledge Bases",
        tabRoles: "Roles & Prompts",
        tabUsers: "Users",
        tabConversations: "Conversations",
        createAgent: "New Agent",
        createSource: "New Knowledge Base",
        createRole: "New Role",
        createUser: "New User",
        tableName: "Name",
        tableRole: "Role",
        tableSources: "Attached Sources",
        tableUpdated: "Updated",
        tableActions: "Actions",
        tableContentLength: "Size",
        tableCreated: "Created",
        tableKey: "Key",
        tableType: "Type",
        tableMessages: "Messages",
        tableAgent: "Agent",
        tableTitle: "Title",
        noData: "No records found.",
      },
    },

    // -------------------------------------------------------------
    // FRANÇAIS (fr)
    // -------------------------------------------------------------
    fr: {
      common: {
        appName: "THEYTHINK AI",
        tagline: "Plateforme Intelligente d'Agents Autonomes",
        save: "Enregistrer",
        saving: "Enregistrement…",
        cancel: "Annuler",
        delete: "Supprimer",
        edit: "Modifier",
        create: "Créer",
        view: "Voir",
        close: "Fermer",
        search: "Rechercher…",
        actions: "Actions",
        connected: "Connecté",
        configureApiKey: "Configurer la Clé API",
        loading: "Chargement…",
        success: "Succès",
        error: "Erreur",
        confirm: "Confirmer",
        back: "Retour",
        logout: "Se déconnecter",
        login: "Se connecter",
        adminAccess: "Accès Administrateur",
        dashboard: "Tableau de Bord",
        publicHome: "Accueil Public",
        home: "Accueil",
        developedBy: "Développé par",
        lightMode: "Mode clair",
        darkMode: "Mode sombre",
        switchTheme: "Basculer le mode clair / sombre",
        selectLanguage: "Choisir la langue",
        total: "Total",
        active: "Actif",
        system: "Système",
        custom: "Personnalisé",
        allRightsReserved: "Tous droits réservés",
      },
      nav: {
        brandSubtitle: "Plateforme d'Agents",
        goToDashboard: "Tableau de Bord",
        loginAction: "Connexion",
        logoutAction: "Déconnexion",
        adminBadge: "ADMIN",
        myProfile: "Mon Compte",
      },
      hero: {
        badge: "Plateforme Intelligente d'Agents Autonomes",
        titlePrefix: "Intelligence Artificielle avec",
        titleHighlight: "Mémoire et Connaissances",
        titleSuffix: "Spécialisées",
        description: "Interagissez avec des agents intelligents qui apprennent de chaque conversation, consultent des bases documentaires modulaires et adoptent des rôles sur mesure.",
        ctaDashboard: "Ouvrir le Tableau de Bord",
        ctaCatalog: "Voir les Agents Disponibles",
        ctaLogin: "Se Connecter pour Discuter",
        ctaExplore: "Explorer les Capacités",
      },
      features: {
        badge: "Capacités Principales",
        title: "Tout ce que vous pouvez accomplir sur la plateforme",
        subtitle: "Conçu avec une architecture modulaire pour résoudre vos défis avec mémoire active et sources thématiques.",
        f1Title: "Mémoire Active & Apprentissage",
        f1Desc: "L'agent retient les faits clés et les préférences des conversations antérieures, offrant continuité et pertinence à chaque échange.",
        f1Foot: "Rétention automatique des faits",
        f2Title: "Bases de Connaissances Thématiques",
        f2Desc: "Téléversement manuel ou en masse de documents découplés. Associez plusieurs bases aux agents pour des informations exactes.",
        f2Foot: "Connaissances découplées",
        f3Title: "Rôles & Identités en Temps Réel",
        f3Desc: "Ajustez le style de communication (enseignant, analyste, conteur, coach) et peaufinez les Prompts Système directement dans SQLite.",
        f3Foot: "Édition et ajustement des prompts",
        f4Title: "Fils de Conversation Isolés",
        f4Desc: "Créez plusieurs sessions par agent. Titrage automatique, renommage et consultation des transcriptions sans saturer le contexte.",
        f4Foot: "Historiques indépendants",
        f5Title: "Moteur IA Haute Performance",
        f5Desc: "Réponses ultra-rapides, analyses Markdown structurées, blocs de code lisibles et grande capacité de synthèse.",
        f5Foot: "Format riche et grande fluidité",
        f6Title: "Administration & Utilisateurs",
        f6Desc: "Tableau de bord complet pour gérer agents, bases, rôles et utilisateurs avec flux complet d'inspection, édition et mise à jour.",
        f6Foot: "Contrôle total et sécurité",
      },
      howItWorks: {
        badge: "Flux Simple",
        title: "Commencez à échanger en 3 étapes",
        step1Num: "1",
        step1Title: "Choisissez ou Créez un Agent",
        step1Desc: "Sélectionnez un profil existant ou créez un nouvel agent selon votre besoin.",
        step2Num: "2",
        step2Title: "Associez des Connaissances",
        step2Desc: "Liez des bases thématiques contenant des manuels ou documents de référence.",
        step3Num: "3",
        step3Title: "Démarrez la Conversation",
        step3Desc: "Échangez dans des fils isolés et profitez de réponses contextuelles avec mémoire active.",
      },
      catalog: {
        badge: "Catalogue Actif",
        title: "Agents Prêts à Échanger",
        subtitle: "Sélectionnez un agent pour démarrer un fil de discussion",
        manageDashboard: "Gérer dans le Tableau de Bord",
        chatWith: "Discuter avec {name}",
        loginToChat: "Se connecter pour discuter",
        noAgents: "Aucun agent enregistré pour le moment.",
        defaultDescription: "Agent intelligent spécialisé prêt à répondre.",
      },
      loginPage: {
        title: "Connexion",
        subtitle: "Connectez-vous pour échanger avec vos agents et gérer la plateforme",
        userLabel: "Nom d'utilisateur",
        userPlaceholder: "ex. admin",
        passwordLabel: "Mot de passe",
        passwordPlaceholder: "••••••••",
        defaultCredentialsTitle: "Identifiants par défaut :",
        defaultUser: "Utilisateur :",
        defaultPass: "Mot de passe :",
        submitButton: "Se connecter",
        backToHome: "Retour à la page d'accueil",
        invalidCredentials: "Identifiants invalides. Veuillez vérifier votre nom d'utilisateur et mot de passe.",
      },
      chat: {
        newChat: "Nouvelle Conversation",
        searchHistory: "Rechercher dans l'historique…",
        emptyHistory: "Aucun message dans cette session. Commencez à écrire !",
        renameChat: "Renommer la Conversation",
        renamePrompt: "Entrez le nouveau titre du fil :",
        deleteChatTitle: "Supprimer la Conversation ?",
        deleteChatConfirm: "Êtes-vous sûr de vouloir supprimer définitivement ce fil de discussion ?",
        agentSettings: "Paramètres de l'Agent",
        manageAgent: "Gérer l'Agent",
        clearMemory: "Effacer la mémoire",
        clearMemoryTitle: "Effacer la Mémoire de l'Agent ?",
        clearMemoryConfirm: "Toutes les informations stockées dans la mémoire active de cet agent seront effacées.",
        basesCount: "{count} base(s)",
        enterToSend: "Entrée ↵ pour envoyer",
        shiftEnter: "Maj+Entrée pour nouvelle ligne",
        typePlaceholder: "Écrivez votre message à {name}… (Maj+Entrée pour nouvelle ligne)",
        copiedToast: "Code copié dans le presse-papiers",
        copyCode: "Copier",
        copyMessage: "Copier le message",
        memoryUpdated: "Mémoire de l'agent mise à jour",
        memoryCleared: "Mémoire effacée avec succès",
        agentUpdated: "Agent mis à jour avec succès",
        sessionRenamed: "Conversation renommée",
        sessionDeleted: "Conversation supprimée",
        thinking: "Génération de la réponse…",
        continuousMemoryFooter: "Mémoire Continue Persistante hébergée sur SQLite",
      },
      dashboard: {
        title: "THEYTHINK AI Dashboard",
        subtitle: "Agents, Bases, Rôles, Utilisateurs et Conversations",
        kpiAgents: "Agents",
        kpiSources: "Bases de Connaissances",
        kpiRoles: "Rôles & Identités",
        kpiUsers: "Utilisateurs",
        kpiMessages: "Messages Totaux",
        tabAgents: "Agents",
        tabSources: "Bases de Connaissances",
        tabRoles: "Rôles & Prompts",
        tabUsers: "Utilisateurs",
        tabConversations: "Conversations",
        createAgent: "Nouvel Agent",
        createSource: "Nouvelle Base",
        createRole: "Nouveau Rôle",
        createUser: "Nouvel Utilisateur",
        tableName: "Nom",
        tableRole: "Rôle",
        tableSources: "Bases Associées",
        tableUpdated: "Mis à jour",
        tableActions: "Actions",
        tableContentLength: "Taille",
        tableCreated: "Créé le",
        tableKey: "Clé",
        tableType: "Type",
        tableMessages: "Messages",
        tableAgent: "Agent",
        tableTitle: "Titre",
        noData: "Aucun enregistrement trouvé.",
      },
    },

    // -------------------------------------------------------------
    // PORTUGUÊS (pt)
    // -------------------------------------------------------------
    pt: {
      common: {
        appName: "THEYTHINK AI",
        tagline: "Plataforma Inteligente de Agentes Autônomos",
        save: "Salvar",
        saving: "Salvando…",
        cancel: "Cancelar",
        delete: "Excluir",
        edit: "Editar",
        create: "Criar",
        view: "Visualizar",
        close: "Fechar",
        search: "Buscar…",
        actions: "Ações",
        connected: "Conectado",
        configureApiKey: "Configurar Chave API",
        loading: "Carregando…",
        success: "Sucesso",
        error: "Erro",
        confirm: "Confirmar",
        back: "Voltar",
        logout: "Sair",
        login: "Entrar",
        adminAccess: "Acesso Administrador",
        dashboard: "Painel",
        publicHome: "Início Público",
        home: "Início",
        developedBy: "Desenvolvido por",
        lightMode: "Modo claro",
        darkMode: "Modo escuro",
        switchTheme: "Alternar modo claro / escuro",
        selectLanguage: "Selecionar idioma",
        total: "Total",
        active: "Ativo",
        system: "Sistema",
        custom: "Personalizado",
        allRightsReserved: "Todos os direitos reservados",
      },
      nav: {
        brandSubtitle: "Plataforma de Agentes",
        goToDashboard: "Painel",
        loginAction: "Entrar",
        logoutAction: "Sair",
        adminBadge: "ADMIN",
        myProfile: "Minha Conta",
      },
      hero: {
        badge: "Plataforma Inteligente de Agentes Autônomos",
        titlePrefix: "Inteligência Artificial com",
        titleHighlight: "Memória e Conhecimento",
        titleSuffix: "Especializado",
        description: "Interaja com agentes inteligentes que aprendem com cada conversa, consultam bases de dados modulares e assumem papéis personalizados.",
        ctaDashboard: "Ir para o Painel Administrativo",
        ctaCatalog: "Ver Agentes Disponíveis",
        ctaLogin: "Entrar para Conversar",
        ctaExplore: "Explorar Recursos",
      },
      features: {
        badge: "Principais Recursos",
        title: "Tudo o que você pode alcançar na plataforma",
        subtitle: "Projetado com arquitetura modular para resolver desafios com memória ativa e bases de conhecimento especializadas.",
        f1Title: "Memória Ativa e Aprendizado",
        f1Desc: "O agente retém dados essenciais, preferências e aprendizados de diálogos anteriores, garantindo contexto contínuo.",
        f1Foot: "Retenção automática de fatos",
        f2Title: "Bases de Conhecimento Temáticas",
        f2Desc: "Envio manual ou em lote de documentos e manuais independentes. Associe múltiplas bases aos agentes para respostas precisas.",
        f2Foot: "Conhecimento desacoplado",
        f3Title: "Papéis e Identidades em Tempo Real",
        f3Desc: "Ajuste estilos comunicativos (professor, analista, narrador, mentor) e personalize Prompts de Sistema no SQLite.",
        f3Foot: "Edição e ajuste de prompts",
        f4Title: "Tópicos de Conversa Isolados",
        f4Desc: "Crie múltiplas sessões por agente. Titulação automática, renomeação e histórico sem poluir o contexto.",
        f4Foot: "Históricos independentes",
        f5Title: "Motor de IA de Alta Performance",
        f5Desc: "Respostas ultra-rápidas, formatação Markdown estruturada, blocos de código legíveis e alta síntese.",
        f5Foot: "Formatação rica e fluidez",
        f6Title: "Administração & Usuários",
        f6Desc: "Painel completo para gerenciar agentes, bases, papéis e usuários com fluxo de visualização, edição e atualização.",
        f6Foot: "Controle total e segurança",
      },
      howItWorks: {
        badge: "Fluxo Simples",
        title: "Comece a conversar em 3 passos",
        step1Num: "1",
        step1Title: "Escolha ou Crie um Agente",
        step1Desc: "Selecione um perfil pronto ou crie um novo agente sob medida.",
        step2Num: "2",
        step2Title: "Associe Conhecimento",
        step2Desc: "Vincule bases temáticas com manuais ou arquivos de consulta.",
        step3Num: "3",
        step3Title: "Inicie a Conversa",
        step3Desc: "Converse em tópicos isolados e aproveite respostas contextuais com memória ativa.",
      },
      catalog: {
        badge: "Catálogo Ativo",
        title: "Agentes Prontos para Conversar",
        subtitle: "Selecione um agente para abrir uma sessão de chat",
        manageDashboard: "Gerenciar no Painel",
        chatWith: "Conversar com {name}",
        loginToChat: "Faça login para conversar",
        noAgents: "Nenhum agente cadastrado no momento.",
        defaultDescription: "Agente inteligente pronto para ajudar.",
      },
      loginPage: {
        title: "Iniciar Sessão",
        subtitle: "Entre para conversar com seus agentes e gerenciar a plataforma",
        userLabel: "Usuário",
        userPlaceholder: "ex. admin",
        passwordLabel: "Senha",
        passwordPlaceholder: "••••••••",
        defaultCredentialsTitle: "Credenciais padrão:",
        defaultUser: "Usuário:",
        defaultPass: "Senha:",
        submitButton: "Entrar",
        backToHome: "Voltar para a página inicial",
        invalidCredentials: "Credenciais inválidas. Verifique seu usuário e senha.",
      },
      chat: {
        newChat: "Nova Conversa",
        searchHistory: "Buscar no histórico…",
        emptyHistory: "Nenhuma mensagem nesta sessão. Comece a digitar!",
        renameChat: "Renomear Conversa",
        renamePrompt: "Digite o novo título da conversa:",
        deleteChatTitle: "Excluir Conversa?",
        deleteChatConfirm: "Tem certeza de que deseja excluir permanentemente este histórico de conversa?",
        agentSettings: "Configurações do Agente",
        manageAgent: "Gerenciar Agente",
        clearMemory: "Limpar memória",
        clearMemoryTitle: "Limpar Memória do Agente?",
        clearMemoryConfirm: "Todas as informações acumuladas na memória ativa deste agente serão removidas.",
        basesCount: "{count} base(s)",
        enterToSend: "Enter ↵ para enviar",
        shiftEnter: "Shift+Enter para nova linha",
        typePlaceholder: "Escreva sua mensagem para {name}… (Shift+Enter para nova linha)",
        copiedToast: "Código copiado para a área de transferência",
        copyCode: "Copiar",
        copyMessage: "Copiar mensagem",
        memoryUpdated: "Memória do agente atualizada com sucesso",
        memoryCleared: "Memória limpa com sucesso",
        agentUpdated: "Agente atualizado com sucesso",
        sessionRenamed: "Conversa renomeada",
        sessionDeleted: "Conversa excluída",
        thinking: "Gerando resposta…",
        continuousMemoryFooter: "Memória Contínua Persistente armazenada em SQLite",
      },
      dashboard: {
        title: "THEYTHINK AI Dashboard",
        subtitle: "Agentes, Bases de Conhecimento, Papéis, Usuários e Conversas",
        kpiAgents: "Agentes",
        kpiSources: "Bases de Conhecimento",
        kpiRoles: "Papéis & Identidades",
        kpiUsers: "Usuários",
        kpiMessages: "Mensagens Totais",
        tabAgents: "Agentes",
        tabSources: "Bases de Conhecimento",
        tabRoles: "Papéis & Prompts",
        tabUsers: "Usuários",
        tabConversations: "Conversas",
        createAgent: "Novo Agente",
        createSource: "Nova Base",
        createRole: "Novo Papel",
        createUser: "Novo Usuário",
        tableName: "Nome",
        tableRole: "Papel",
        tableSources: "Bases Associadas",
        tableUpdated: "Atualizado",
        tableActions: "Ações",
        tableContentLength: "Tamanho",
        tableCreated: "Criado em",
        tableKey: "Chave",
        tableType: "Tipo",
        tableMessages: "Mensagens",
        tableAgent: "Agente",
        tableTitle: "Título",
        noData: "Nenhum registro encontrado.",
      },
    },

    // -------------------------------------------------------------
    // 한국어 (ko)
    // -------------------------------------------------------------
    ko: {
      common: {
        appName: "THEYTHINK AI",
        tagline: "지능형 자율 에이전트 플랫폼",
        save: "저장",
        saving: "저장 중…",
        cancel: "취소",
        delete: "삭제",
        edit: "수정",
        create: "생성",
        view: "보기",
        close: "닫기",
        search: "검색…",
        actions: "작업",
        connected: "연결됨",
        configureApiKey: "API 키 설정",
        loading: "로딩 중…",
        success: "성공",
        error: "오류",
        confirm: "확인",
        back: "뒤로 가기",
        logout: "로그아웃",
        login: "로그인",
        adminAccess: "관리자 로그인",
        dashboard: "대시보드",
        publicHome: "홈페이지",
        home: "홈",
        developedBy: "개발자:",
        lightMode: "라이트 모드",
        darkMode: "다크 모드",
        switchTheme: "라이트 / 다크 모드 전환",
        selectLanguage: "언어 선택",
        total: "전체",
        active: "활성",
        system: "시스템",
        custom: "커스텀",
        allRightsReserved: "모든 권리 보유",
      },
      nav: {
        brandSubtitle: "에이전트 플랫폼",
        goToDashboard: "대시보드",
        loginAction: "로그인",
        logoutAction: "로그아웃",
        adminBadge: "관리자",
        myProfile: "내 계정",
      },
      hero: {
        badge: "지능형 자율 에이전트 플랫폼",
        titlePrefix: "인공지능과",
        titleHighlight: "지속적인 기억 및 지식",
        titleSuffix: "의 결합",
        description: "모든 대화에서 학습하고 모듈형 문서 저장소를 참조하며 맞춤형 역할을 수행하는 지능형 에이전트와 대화하세요.",
        ctaDashboard: "관리자 대시보드 이동",
        ctaCatalog: "사용 가능한 에이전트 보기",
        ctaLogin: "대화 시작을 위한 로그인",
        ctaExplore: "핵심 기능 살펴보기",
      },
      features: {
        badge: "핵심 역량",
        title: "플랫폼에서 실현할 수 있는 모든 것",
        subtitle: "활성 기억과 주제별 지식 소스를 활용하여 문제를 해결하는 모듈형 아키텍처로 설계되었습니다.",
        f1Title: "생생한 기억과 자율 학습",
        f1Desc: "에이전트가 이전 대화의 핵심 사실, 선호도 및 학습 내용을 기억하여 맥락과 연속성을 유지합니다.",
        f1Foot: "핵심 사실 자동 보존",
        f2Title: "주제별 지식 저장소",
        f2Desc: "독립적인 매뉴얼과 문서들을 개별 또는 일괄 업로드하고 여러 에이전트에 연결하여 정확한 지식을 제공합니다.",
        f2Foot: "독립된 도메인 지식",
        f3Title: "실시간 역할 및 페르소나",
        f3Desc: "교사, 분석가, 이야기꾼, 코치 등 소통 스타일을 조정하고 시스템 프롬프트를 SQLite에서 실시간으로 다듬을 수 있습니다.",
        f3Foot: "프롬프트 즉각 수정 및 최적화",
        f4Title: "독립된 다중 대화 스레드",
        f4Desc: "에이전트별로 여러 대화 세션을 생성하고 자동 제목 지정 및 기록 관리가 가능합니다.",
        f4Foot: "독립적인 대화 기록",
        f5Title: "고성능 AI 엔진",
        f5Desc: "초고속 응답, 서식화된 마크다운 분석, 코드 블록 가독성 및 뛰어난 요약 능력을 제공합니다.",
        f5Foot: "풍부한 서식과 빠른 속도",
        f6Title: "관리 및 사용자 제어",
        f6Desc: "조회, 수정, 업데이트 흐름을 통해 에이전트, 지식 베이스, 역할 및 사용자를 완벽히 제어하는 대시보드를 제공합니다.",
        f6Foot: "완벽한 제어 및 보안",
      },
      howItWorks: {
        badge: "간단한 진행 단계",
        title: "3단계로 시작하는 대화",
        step1Num: "1",
        step1Title: "에이전트 선택 또는 생성",
        step1Desc: "해결하려는 분야에 맞춰 기존 프로필을 선택하거나 새로운 에이전트를 생성합니다.",
        step2Num: "2",
        step2Title: "지식 베이스 연결",
        step2Desc: "에이전트가 참조할 매뉴얼이나 문서가 담긴 지식 저장소를 연결합니다.",
        step3Num: "3",
        step3Title: "대화 시작",
        step3Desc: "독립된 스레드에서 대화하고 활성 기억을 기반으로 한 맥락적 응답을 경험하세요.",
      },
      catalog: {
        badge: "활성 에이전트 목록",
        title: "대화 준비가 완료된 에이전트",
        subtitle: "에이전트를 선택하여 새로운 대화 스레드를 시작하세요",
        manageDashboard: "대시보드에서 관리",
        chatWith: "{name}와(과) 대화하기",
        loginToChat: "대화하려면 로그인하세요",
        noAgents: "현재 등록된 에이전트가 없습니다.",
        defaultDescription: "사용자를 도울 준비가 된 지능형 에이전트입니다.",
      },
      loginPage: {
        title: "로그인",
        subtitle: "에이전트와 대화하고 플랫폼을 관리하려면 로그인하세요",
        userLabel: "사용자명",
        userPlaceholder: "예: admin",
        passwordLabel: "비밀번호",
        passwordPlaceholder: "••••••••",
        defaultCredentialsTitle: "기본 계정 정보:",
        defaultUser: "아이디:",
        defaultPass: "비밀번호:",
        submitButton: "로그인",
        backToHome: "메인 페이지로 돌아가기",
        invalidCredentials: "잘못된 계정 정보입니다. 사용자명과 비밀번호를 확인해주세요.",
      },
      chat: {
        newChat: "새 대화",
        searchHistory: "대화 기록 검색…",
        emptyHistory: "이 세션에 메시지가 없습니다. 메시지를 입력해보세요!",
        renameChat: "대화 제목 변경",
        renamePrompt: "대화 스레드의 새 제목을 입력하세요:",
        deleteChatTitle: "대화를 삭제하시겠습니까?",
        deleteChatConfirm: "이 대화 스레드를 영구적으로 삭제하시겠습니까?",
        agentSettings: "에이전트 설정",
        manageAgent: "에이전트 관리",
        clearMemory: "기억 초기화",
        clearMemoryTitle: "에이전트 기억을 초기화하시겠습니까?",
        clearMemoryConfirm: "이 에이전트의 활성 메모리에 저장된 모든 기억이 삭제됩니다.",
        basesCount: "지식 베이스 {count}개",
        enterToSend: "Enter ↵ 전송",
        shiftEnter: "Shift+Enter 줄바꿈",
        typePlaceholder: "{name}에게 메시지를 입력하세요… (Shift+Enter 줄바꿈)",
        copiedToast: "코드가 클립보드에 복사되었습니다",
        copyCode: "복사",
        copyMessage: "메시지 복사",
        memoryUpdated: "에이전트 메모리가 성공적으로 업데이트되었습니다",
        memoryCleared: "에이전트 메모리가 성공적으로 초기화되었습니다",
        agentUpdated: "에이전트가 성공적으로 수정되었습니다",
        sessionRenamed: "대화 제목이 변경되었습니다",
        sessionDeleted: "대화가 삭제되었습니다",
        thinking: "답변을 생성하는 중입니다…",
        continuousMemoryFooter: "SQLite 기반 지속적 활성 메모리 지원",
      },
      dashboard: {
        title: "THEYTHINK AI 대시보드",
        subtitle: "에이전트, 지식 저장소, 역할, 사용자 및 대화 관리",
        kpiAgents: "에이전트",
        kpiSources: "지식 베이스",
        kpiRoles: "역할 & 프롬프트",
        kpiUsers: "사용자",
        kpiMessages: "전체 메시지 수",
        tabAgents: "에이전트",
        tabSources: "지식 저장소",
        tabRoles: "역할 & 프롬프트",
        tabUsers: "사용자",
        tabConversations: "대화 목록",
        createAgent: "새 에이전트",
        createSource: "새 지식 베이스",
        createRole: "새 역할",
        createUser: "새 사용자",
        tableName: "이름",
        tableRole: "역할",
        tableSources: "연결된 지식",
        tableUpdated: "최종 수정",
        tableActions: "관리",
        tableContentLength: "용량",
        tableCreated: "생성일",
        tableKey: "식별 키",
        tableType: "유형",
        tableMessages: "메시지 수",
        tableAgent: "에이전트",
        tableTitle: "제목",
        noData: "등록된 데이터가 없습니다.",
      },
    },

    // -------------------------------------------------------------
    // 中文 (zh)
    // -------------------------------------------------------------
    zh: {
      common: {
        appName: "THEYTHINK AI",
        tagline: "智能自主代理平台",
        save: "保存",
        saving: "保存中…",
        cancel: "取消",
        delete: "删除",
        edit: "编辑",
        create: "创建",
        view: "查看",
        close: "关闭",
        search: "搜索…",
        actions: "操作",
        connected: "已连接",
        configureApiKey: "配置 API 密钥",
        loading: "加载中…",
        success: "成功",
        error: "错误",
        confirm: "确认",
        back: "返回",
        logout: "退出登录",
        login: "登录",
        adminAccess: "管理员登录",
        dashboard: "控制面板",
        publicHome: "公共首页",
        home: "首页",
        developedBy: "开发者：",
        lightMode: "浅色模式",
        darkMode: "深色模式",
        switchTheme: "切换浅色 / 深色模式",
        selectLanguage: "选择语言",
        total: "总计",
        active: "活跃",
        system: "系统内置",
        custom: "自定义",
        allRightsReserved: "版权所有",
      },
      nav: {
        brandSubtitle: "智能代理平台",
        goToDashboard: "控制面板",
        loginAction: "登录",
        logoutAction: "退出登录",
        adminBadge: "管理员",
        myProfile: "我的账户",
      },
      hero: {
        badge: "智能自主代理平台",
        titlePrefix: "融合",
        titleHighlight: "持久记忆与专业知识",
        titleSuffix: "的人工智能",
        description: "与智能代理实时对话。每个代理均具备持续记忆能力，支持关联模块化文档知识库并定制个性化角色设定。",
        ctaDashboard: "进入管理面板",
        ctaCatalog: "浏览可用代理",
        ctaLogin: "登录开始对话",
        ctaExplore: "探索核心能力",
      },
      features: {
        badge: "核心能力",
        title: "平台助您实现的无限可能",
        subtitle: "采用模块化架构设计，结合动态记忆与专业知识库，精准解决复杂场景需求。",
        f1Title: "动态记忆与持续学习",
        f1Desc: "代理可记住历史对话中的关键信息与用户偏好，确保每次对话都具备上下文连贯性。",
        f1Foot: "自动事实持久化存储",
        f2Title: "模块化专业知识库",
        f2Desc: "支持手动录入或批量上传文档。每个代理可关联多个独立知识库，提供准确专业的解答。",
        f2Foot: "解耦式专业知识",
        f3Title: "实时角色与提示词定制",
        f3Desc: "灵活调整对话风格（导师、分析师、故事家、教练），直接在 SQLite 中优化系统提示词。",
        f3Foot: "提示词即时微调",
        f4Title: "隔离式多对话线程",
        f4Desc: "每个代理可创建独立的对话会话，支持自动生成标题、重命名及历史回溯，互不干扰。",
        f4Foot: "独立历史记录",
        f5Title: "高性能 AI 引擎",
        f5Desc: "极速响应、丰富的 Markdown 排版、清晰的代码块高亮与强大的内容总结能力。",
        f5Foot: "丰富排版与极速体验",
        f6Title: "全局管理与用户权限",
        f6Desc: "一体化控制面板，支持代理、知识库、角色与用户的全生命周期管理（查看、编辑、更新与删除）。",
        f6Foot: "全面掌控与安全保障",
      },
      howItWorks: {
        badge: "极简流程",
        title: "三步开启智能对话",
        step1Num: "1",
        step1Title: "选择或创建代理",
        step1Desc: "选择已有的专业代理或根据业务需求创建全新角色。",
        step2Num: "2",
        step2Title: "关联知识库",
        step2Desc: "为代理挂载包含专业手册或参考资料的主题知识库。",
        step3Num: "3",
        step3Title: "开启智能对话",
        step3Desc: "在独立会话中畅快交流，体验带记忆增强的智能交互。",
      },
      catalog: {
        badge: "当前代理目录",
        title: "已就绪的智能代理",
        subtitle: "选择代理即可开启专属对话线程",
        manageDashboard: "在控制面板中管理",
        chatWith: "与 {name} 对话",
        loginToChat: "登录后开启对话",
        noAgents: "暂无已注册的智能代理。",
        defaultDescription: "准备就绪的专业智能代理。",
      },
      loginPage: {
        title: "登录平台",
        subtitle: "登录以与智能代理对话并管理平台资源",
        userLabel: "用户名",
        userPlaceholder: "例如：admin",
        passwordLabel: "密码",
        passwordPlaceholder: "••••••••",
        defaultCredentialsTitle: "默认登录凭据：",
        defaultUser: "用户名：",
        defaultPass: "密码：",
        submitButton: "立即登录",
        backToHome: "返回主页",
        invalidCredentials: "用户名或密码错误，请重新输入。",
      },
      chat: {
        newChat: "新建对话",
        searchHistory: "搜索历史记录…",
        emptyHistory: "此会话暂无消息，快来发送第一条信息吧！",
        renameChat: "重命名对话",
        renamePrompt: "请输入对话的新标题：",
        deleteChatTitle: "删除此对话？",
        deleteChatConfirm: "确定要彻底删除该对话线程吗？",
        agentSettings: "代理配置",
        manageAgent: "管理代理",
        clearMemory: "清理记忆",
        clearMemoryTitle: "清空代理记忆？",
        clearMemoryConfirm: "将永久清空此代理在活跃内存中存储的所有记忆事实。",
        basesCount: "{count} 个知识库",
        enterToSend: "Enter ↵ 发送",
        shiftEnter: "Shift+Enter 换行",
        typePlaceholder: "给 {name} 发送消息… (Shift+Enter 换行)",
        copiedToast: "代码已复制到剪贴板",
        copyCode: "复制",
        copyMessage: "复制消息",
        memoryUpdated: "代理记忆已成功更新",
        memoryCleared: "代理记忆已成功清空",
        agentUpdated: "代理配置已成功更新",
        sessionRenamed: "对话已重命名",
        sessionDeleted: "对话已删除",
        thinking: "正在思考并生成回复…",
        continuousMemoryFooter: "由 SQLite 驱动的持续持久化记忆",
      },
      dashboard: {
        title: "THEYTHINK AI 控制面板",
        subtitle: "代理、知识库、角色、用户与对话综合管理",
        kpiAgents: "智能代理",
        kpiSources: "知识库",
        kpiRoles: "角色与提示词",
        kpiUsers: "系统用户",
        kpiMessages: "累计消息数",
        tabAgents: "代理管理",
        tabSources: "知识库管理",
        tabRoles: "角色与提示词",
        tabUsers: "用户管理",
        tabConversations: "对话记录",
        createAgent: "新建代理",
        createSource: "新建知识库",
        createRole: "新建角色",
        createUser: "新建用户",
        tableName: "名称",
        tableRole: "角色设定",
        tableSources: "关联知识库",
        tableUpdated: "更新时间",
        tableActions: "操作",
        tableContentLength: "容量大小",
        tableCreated: "创建时间",
        tableKey: "标识键",
        tableType: "类型",
        tableMessages: "消息数量",
        tableAgent: "所属代理",
        tableTitle: "会话标题",
        noData: "暂无相关记录。",
      },
    },
  };

  // Variable de estado para el idioma actual
  var currentLanguage = DEFAULT_LANGUAGE;
  var listeners = [];

  /**
   * Obtiene el valor anidado de un objeto según la ruta con puntos (ej. "hero.title").
   * @param {Object} obj - Objeto de traducciones.
   * @param {string} path - Ruta en formato clave.subclave.
   * @returns {*} Valor encontrado o undefined.
   */
  function getNestedValue(obj, path) {
    if (!obj || !path) return undefined;
    var parts = path.split(".");
    var current = obj;
    for (var i = 0; i < parts.length; i++) {
      if (current === undefined || current === null) return undefined;
      current = current[parts[i]];
    }
    return current;
  }

  /**
   * Traduce una clave con parámetros opcionales.
   * @param {string} key - Clave de traducción (ej. "common.save" o "chat.typePlaceholder").
   * @param {Object} [params] - Parámetros para reemplazar marcadores como {name}.
   * @returns {string} Texto traducido o la clave si no existe.
   */
  function translate(key, params) {
    var langDict = TRANSLATIONS[currentLanguage] || TRANSLATIONS[DEFAULT_LANGUAGE];
    var val = getNestedValue(langDict, key);

    // Si no se encuentra en el idioma actual, busca en el idioma por defecto
    if (val === undefined && currentLanguage !== DEFAULT_LANGUAGE) {
      val = getNestedValue(TRANSLATIONS[DEFAULT_LANGUAGE], key);
    }

    if (val === undefined) {
      return key;
    }

    if (typeof val !== "string") {
      return val;
    }

    // Reemplazo de parámetros {variable}
    if (params && typeof params === "object") {
      Object.keys(params).forEach(function (paramKey) {
        var regex = new RegExp("\\{" + paramKey + "\\}", "g");
        val = val.replace(regex, params[paramKey]);
      });
    }

    return val;
  }

  /**
   * Actualiza todos los elementos del DOM que contengan atributos de internacionalización:
   * - data-i18n: Reemplaza textContent o innerHTML.
   * - data-i18n-placeholder: Reemplaza el placeholder de inputs/textareas.
   * - data-i18n-title: Reemplaza el atributo title.
   * - data-i18n-params: JSON con parámetros dinámicos.
   */
  function translateDocument() {
    document.documentElement.lang = currentLanguage;

    // Traducir elementos de texto
    var elements = document.querySelectorAll("[data-i18n]");
    elements.forEach(function (el) {
      var key = el.getAttribute("data-i18n");
      var paramsAttr = el.getAttribute("data-i18n-params");
      var params = null;
      if (paramsAttr) {
        try {
          params = JSON.parse(paramsAttr);
        } catch (e) {
          // Ignorar error de parseo
        }
      }
      var translated = translate(key, params);
      if (translated !== key) {
        // Preservar hijos con iconos si es necesario o actualizar texto directo
        if (el.children.length === 0) {
          el.textContent = translated;
        } else {
          // Si tiene icono (como <i>), buscar un span hijo o actualizar nodo de texto
          var textSpan = el.querySelector("[data-i18n-text]") || el.querySelector("span:not([class*='icon'])");
          if (textSpan) {
            textSpan.textContent = translated;
          } else {
            // Actualiza el último nodo de texto
            var childNodes = el.childNodes;
            var updated = false;
            for (var i = childNodes.length - 1; i >= 0; i--) {
              if (childNodes[i].nodeType === Node.TEXT_NODE && childNodes[i].textContent.trim() !== "") {
                childNodes[i].textContent = " " + translated.trim() + " ";
                updated = true;
                break;
              }
            }
            if (!updated) {
              el.textContent = translated;
            }
          }
        }
      }
    });

    // Traducir placeholders
    var placeholderElements = document.querySelectorAll("[data-i18n-placeholder]");
    placeholderElements.forEach(function (el) {
      var key = el.getAttribute("data-i18n-placeholder");
      var paramsAttr = el.getAttribute("data-i18n-params");
      var params = null;
      if (paramsAttr) {
        try {
          params = JSON.parse(paramsAttr);
        } catch (e) {}
      }
      var translated = translate(key, params);
      if (translated !== key) {
        el.setAttribute("placeholder", translated);
      }
    });

    // Traducir títulos (tooltips)
    var titleElements = document.querySelectorAll("[data-i18n-title]");
    titleElements.forEach(function (el) {
      var key = el.getAttribute("data-i18n-title");
      var translated = translate(key);
      if (translated !== key) {
        el.setAttribute("title", translated);
      }
    });

    // Actualizar todos los selectores de idioma en la página
    updateLanguageSelectors();

    // Re-renderizar iconos de Lucide si están disponibles
    if (window.lucide && typeof window.lucide.createIcons === "function") {
      window.lucide.createIcons();
    }
  }

  /**
   * Cierra todos los menús desplegables de idioma abiertos en el documento.
   */
  function closeAllDropdowns() {
    document.querySelectorAll("[data-i18n-dropdown]").forEach(function (dropdown) {
      var menu = dropdown.querySelector(".language-dropdown-menu");
      var chevron = dropdown.querySelector(".language-dropdown-chevron");
      if (menu) menu.classList.add("hidden");
      if (chevron) chevron.classList.remove("rotate-180");
    });
  }

  /**
   * Alterna la apertura / cierre de un dropdown específico.
   * @param {HTMLElement} dropdownElement - Elemento contenedor con data-i18n-dropdown.
   */
  function toggleDropdown(dropdownElement) {
    var menu = dropdownElement.querySelector(".language-dropdown-menu");
    var chevron = dropdownElement.querySelector(".language-dropdown-chevron");
    if (!menu) return;
    var isHidden = menu.classList.contains("hidden");
    closeAllDropdowns();
    if (isHidden) {
      menu.classList.remove("hidden");
      if (chevron) chevron.classList.add("rotate-180");
      if (window.lucide) window.lucide.createIcons();
    }
  }

  /**
   * Actualiza el valor visual de los selectores y dropdowns de idioma en el DOM.
   */
  function updateLanguageSelectors() {
    var meta = LANGUAGE_METADATA[currentLanguage] || LANGUAGE_METADATA[DEFAULT_LANGUAGE];

    // 1. Actualizar insignias y nombres en triggers de dropdowns
    document.querySelectorAll(".language-current-code").forEach(function (el) {
      el.textContent = meta.shortName;
      el.className = "language-current-code uppercase font-extrabold text-[10px] px-1.5 py-0.5 rounded-md transition-colors " + meta.badgeBg;
    });

    document.querySelectorAll(".language-current-name").forEach(function (el) {
      el.textContent = meta.name;
    });

    // 2. Actualizar opciones y checkmarks en dropdowns
    document.querySelectorAll("[data-i18n-dropdown]").forEach(function (dropdown) {
      dropdown.querySelectorAll("[data-lang-code]").forEach(function (opt) {
        var code = opt.getAttribute("data-lang-code");
        var isSelected = code === currentLanguage;
        var checkIcon = opt.querySelector(".language-check-icon");

        if (isSelected) {
          opt.classList.add("bg-black/5", "dark:bg-white/10", "font-bold");
          opt.classList.remove("font-medium");
          if (checkIcon) checkIcon.classList.remove("hidden");
        } else {
          opt.classList.remove("bg-black/5", "dark:bg-white/10", "font-bold");
          opt.classList.add("font-medium");
          if (checkIcon) checkIcon.classList.add("hidden");
        }
      });
    });

    // 3. Soporte para selectores HTML nativos residuales si existieran
    document.querySelectorAll(".language-select-input").forEach(function (select) {
      select.value = currentLanguage;
    });

    // Cerrar menús flotantes
    closeAllDropdowns();
  }

  /**
   * Establece un nuevo idioma activo y actualiza la interfaz.
   * @param {string} lang - Código del idioma ('es', 'en', 'fr', 'pt', 'ko', 'zh').
   */
  function setLanguage(lang) {
    if (!lang || SUPPORTED_LANGUAGES.indexOf(lang) === -1) {
      lang = DEFAULT_LANGUAGE;
    }
    currentLanguage = lang;
    try {
      localStorage.setItem(STORAGE_KEY, lang);
    } catch (e) {
      // Ignorar error de acceso a localStorage
    }

    translateDocument();

    // Notificar a observadores registrados
    listeners.forEach(function (fn) {
      try {
        fn(currentLanguage);
      } catch (err) {
        console.error("Error en listener de i18n:", err);
      }
    });
  }

  /**
   * Obtiene el idioma actualmente activo.
   * @returns {string} Código del idioma ('es', 'en', etc.).
   */
  function getLanguage() {
    return currentLanguage;
  }

  /**
   * Registra un callback que se ejecuta cuando cambia el idioma.
   * @param {Function} callback - Función listener.
   */
  function onLanguageChange(callback) {
    if (typeof callback === "function") {
      listeners.push(callback);
    }
  }

  /**
   * Genera el HTML del componente dropdown premium de selección de idioma.
   * @param {string} [dropdownId] - ID del elemento contenedor.
   * @param {string} [alignment='right'] - Alineación del menú desplegable ('right' o 'left').
   * @returns {string} Fragmento HTML del dropdown de idiomas.
   */
  function renderDropdownHtml(dropdownId, alignment) {
    var id = dropdownId || "i18n-dropdown-" + Math.random().toString(36).substr(2, 9);
    var alignClass = (alignment === "left") ? "left-0 origin-top-left" : "right-0 origin-top-right";
    var meta = LANGUAGE_METADATA[currentLanguage] || LANGUAGE_METADATA[DEFAULT_LANGUAGE];

    var optionsHtml = SUPPORTED_LANGUAGES.map(function (code) {
      var item = LANGUAGE_METADATA[code];
      var isSelected = code === currentLanguage;
      return (
        '<button type="button" onclick="window.i18n.setLanguage(\'' + code + '\')" ' +
        'class="language-option-btn w-full flex items-center justify-between gap-2.5 rounded-xl px-2.5 py-2 text-left text-xs transition ' +
        (isSelected ? 'bg-black/5 dark:bg-white/10 font-bold' : 'hover:bg-black/5 dark:hover:bg-white/5 font-medium') + '" ' +
        'data-lang-code="' + code + '">' +
        '  <div class="flex items-center gap-2.5 min-w-0">' +
        '    <span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-lg ' + item.badgeBg + ' font-bold text-[10px]">' + item.shortName + '</span>' +
        '    <div class="min-w-0 flex-1">' +
        '      <p class="text-xs text-[#202124] dark:text-white leading-none font-bold">' + item.name + '</p>' +
        '      <p class="text-[10px] text-[#5f6368] dark:text-[#c4c7c5] mt-0.5 truncate">' + item.subtitle + '</p>' +
        '    </div>' +
        '  </div>' +
        '  <i data-lucide="check" class="language-check-icon h-3.5 w-3.5 text-[#1a73e8] dark:text-[#8ab4f8] shrink-0 ' + (isSelected ? '' : 'hidden') + '"></i>' +
        '</button>'
      );
    }).join("");

    return (
      '<div id="' + id + '" class="relative inline-block text-left language-dropdown" data-i18n-dropdown>' +
      '  <button type="button" class="language-dropdown-btn inline-flex items-center gap-2 rounded-xl border border-black/10 dark:border-white/10 bg-white/80 dark:bg-[#1e1f20]/80 backdrop-blur-md px-3 py-1.5 text-xs font-semibold text-[#202124] dark:text-white shadow-sm hover:bg-black/5 dark:hover:bg-white/10 transition active:scale-95">' +
      '    <i data-lucide="globe" class="h-3.5 w-3.5 text-[#1a73e8] dark:text-[#8ab4f8] shrink-0"></i>' +
      '    <span class="language-current-code uppercase font-extrabold text-[10px] px-1.5 py-0.5 rounded-md ' + meta.badgeBg + '">' + meta.shortName + '</span>' +
      '    <span class="language-current-name hidden sm:inline text-xs font-semibold text-[#202124] dark:text-[#e3e3e3]">' + meta.name + '</span>' +
      '    <i data-lucide="chevron-down" class="language-dropdown-chevron h-3 w-3 text-[#5f6368] dark:text-[#c4c7c5] transition-transform duration-200"></i>' +
      '  </button>' +
      '  <div class="language-dropdown-menu hidden absolute ' + alignClass + ' mt-2 w-56 rounded-2xl border border-black/10 dark:border-white/10 bg-white/95 dark:bg-[#1e1f20]/95 p-1.5 shadow-2xl backdrop-blur-xl z-50 transition-all duration-150 animate-fade-in">' +
      '    <div class="px-2.5 py-1.5 text-[10px] font-bold uppercase tracking-wider text-[#5f6368] dark:text-[#c4c7c5] border-b border-black/5 dark:border-white/5 mb-1" data-i18n="common.selectLanguage">' +
      (TRANSLATIONS[currentLanguage].common.selectLanguage || "Seleccionar Idioma") +
      '    </div>' +
      optionsHtml +
      '  </div>' +
      '</div>'
    );
  }

  /**
   * Inicializa el sistema de internacionalización y eventos globales.
   */
  function init() {
    var savedLang = null;
    try {
      savedLang = localStorage.getItem(STORAGE_KEY);
    } catch (e) {}

    // Si no hay idioma guardado, detectar el del navegador
    if (!savedLang && navigator && navigator.language) {
      var navLang = navigator.language.slice(0, 2).toLowerCase();
      if (SUPPORTED_LANGUAGES.indexOf(navLang) !== -1) {
        savedLang = navLang;
      }
    }

    setLanguage(savedLang || DEFAULT_LANGUAGE);

    // Manejo de eventos de clic global para dropdowns interactivos
    document.addEventListener("DOMContentLoaded", function () {
      translateDocument();

      // Clics en botones trigger de dropdowns
      document.addEventListener("click", function (e) {
        var dropdown = e.target.closest("[data-i18n-dropdown]");
        if (dropdown) {
          var btn = e.target.closest(".language-dropdown-btn");
          if (btn) {
            e.preventDefault();
            e.stopPropagation();
            toggleDropdown(dropdown);
          }
        } else {
          closeAllDropdowns();
        }
      });

      // Cerrar al pulsar Escape
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
          closeAllDropdowns();
        }
      });

      // Compatibilidad con selectores residuales
      document.querySelectorAll(".language-select-input").forEach(function (select) {
        select.addEventListener("change", function (e) {
          setLanguage(e.target.value);
        });
      });
    });
  }

  // Ejecutar inicialización inmediata
  init();

  return {
    t: translate,
    translate: translate,
    setLanguage: setLanguage,
    getLanguage: getLanguage,
    onLanguageChange: onLanguageChange,
    translateDocument: translateDocument,
    renderSelectorHtml: renderDropdownHtml,
    renderDropdownHtml: renderDropdownHtml,
    toggleDropdown: toggleDropdown,
    closeAllDropdowns: closeAllDropdowns,
    supportedLanguages: SUPPORTED_LANGUAGES,
    metadata: LANGUAGE_METADATA,
  };
});
