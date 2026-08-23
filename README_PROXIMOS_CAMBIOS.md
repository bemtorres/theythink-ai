# Próximos Cambios — Hoja de Ruta de Desarrollo Profesional

> Documento vivo de planificación para evolucionar `agente_deepseek` (panel de agentes IA con DeepSeek)
> desde un prototipo funcional hacia un producto mantenible, seguro y escalable.

Este README NO reemplaza el `README.md` (guía de usuario/arranque). Aquí se define **qué cambiar, por qué y en qué orden**
para professionalizar el desarrollo. Cada ítem tiene prioridad (P0 = crítico, P1 = alto, P2 = medio, P3 = bajo)
y referencias a archivos reales del repositorio.

---

## 1. Estado actual (resumen)

| Capa | Estado |
|---|---|
| Backend | Flask monolítico (`app.py`, ~1.060 líneas), ~55 rutas, API JSON sin versionar. |
| Datos | SQLite directo vía `sqlite3`, sin ORM ni migraciones (`basededatos.py`, ~1.697 líneas). |
| Auth | Hashing scrypt correcto, pero **sin autorización por rol** y API mayormente abierta. |
| Frontend | Jinja + Tailwind CDN, i18n propio en JS para 6 idiomas (sólido). Sin bundler. |
| Calidad | Sin tests, sin lint/type-check, CI solo despliega a GitHub Pages. |

**Fortalezas a preservar:** hashing de contraseñas correcto, manejo de errores de la API DeepSeek robusto
(`basededatos.py:1507`), saneo XSS con `dompurify`, i18n desacoplado y bien aislado, validación básica de entradas.

---

## 2. Principios de desarrollo

1. **Seguridad por defecto:** todo endpoint mutador autenticado y autorizado; secretos fuera del repo.
2. **Una sola fuente de verdad:** eliminar capas de datos duplicadas y aliases.
3. **Reproducibilidad:** dependencias fijadas, entorno declarado, build determinista.
4. **Observabilidad:** logging estructurado y manejo centralizado de errores desde el día uno.
5. **Calidad automatizada:** tests + pipeline CI real antes de cada merge.
6. **API como contrato:** versionada, documentada y estable.

---

## 3. Hoja de ruta (por fases)

### Fase 1 — Seguridad (P0) 🔒
*Riesgo actual: cualquiera con acceso de red puede borrar agentes/usuarios; sesiones falsificables.*

- [ ] **Cerrar la API con autenticación global.** Añadir `before_request` que exija sesión (o token) en todos los `/api/*` mutadores. Hoy solo unos pocos llevan `@require_login` (`app.py:516, 946, 994`); el resto (crear/eliminar agentes `:537/:578`, fuentes `:1022/:1052`, roles, usuarios `:770/:820`, sesiones) está abierto.
- [ ] **Autorización por rol.** `require_login` solo valida sesión; el chequeo `if rol == "admin"` existe solo en `eliminar_usuario` (`basededatos.py:716`). Crear decorador `require_admin` y proteger `/admin/*` y la creación de usuarios/roles.
- [ ] **Externalizar y rotar secretos.** `app.py:78` usa `FLASK_SECRET_KEY` con fallback hardcodeado (`"minimind-secret-key-..."`). Forzar su presencia y rotar la `DEEPSEEK_API_KEY` real que vive en `.env` (no es placeholder).
- [ ] **Protección CSRF.** No hay Flask-WTF ni tokens; POST/PUT/DELETE mutan estado. Añadir `Flask-WTF` o tokens doble-submit para formularios web.
- [ ] **Rate limiting + protección de fuerza bruta** en `/login` (e.g. `Flask-Limiter`).
- [ ] **Servidor de producción.** `app.run(debug=True)` (`app.py:1060`) expone el debugger de Werkzeug. Sustituir por `gunicorn`/`waitress` y declararlo en dependencias.
- [ ] **Restringir uploads.** `.svg` está permitido (`app.py:82, 515`) y se sirve desde `static/`; limitar a raster o sanear SVG.

### Fase 2 — Arquitectura y calidad de datos (P1) 🧱
- [ ] **Unificar la capa de datos.** Hoy hay dos API duplicadas: funciones de módulo (`crear_agente`, `obtener_agente`…) y la clase `AgenteDB` (`:1477`) que re-implementa lo mismo y además llama a DeepSeek. Quedarse con **una** (recomendado: funciones de módulo + clase ligera de servicio de chat).
- [ ] **Eliminar el bloque de aliases** (`:1653–1696`, `AgentDB = AgenteDB`, `list_users = listar_usuarios`…) que solo añade superficie.
- [ ] **Eliminar lógica duplicada** `get_person_name` (`app.py:116`) vs `AgenteDB.obtener_nombre` (`basededatos.py:1541`); centralizar en un módulo `util/perfil.py`.
- [ ] **Migraciones formales.** `migrar_esquema()` (`:125`) es manual/frágil. Adoptar **Alembic** (o `yoyo`) sobre SQLite para evolución controlada del esquema.
- [ ] **ORM opcional.** Evaluar SQLAlchemy 2.0 para tipado y menos SQL ad-hoc; al menos añadir un pool de conexiones (hoy sin pool, cuello de botella en concurrencia).
- [ ] **Logging estructurado.** Añadir `logging` + `app.errorhandler` en `app.py`/`basededatos.py` (hoy no hay nada; auditoría/debug nulos).
- [ ] **Corregir typo de ruta** `whatsaap` duplicado junto a `whatsapp` (`app.py:260, 280, 303`); mantener redirección 301 y deprecar la mal escrita.

### Fase 3 — API como contrato (P1) 🔌
- [ ] **Versionar** (`/api/v1/...`) para poder evolucionar sin romper clientes.
- [ ] **Esquema de respuestas estable** con `pydantic` (ya presente en el venv por `openai`); validar entradas y documentar con OpenAPI (Flask-RESTful/FastAPI-lite o `flask-smorest`).
- [ ] **Manejo de errores centralizado** (un solo lugar que devuelve `{error, code}` consistente).
- [ ] **Tests de contrato** para cada endpoint (status, shape, authz).

### Fase 4 — Frontend robusto (P2) 🎨
- [ ] **Pipeline de build.** Tailwind CDN no es producción; migrar a Tailwind CLI/Vite con CSS purgado. Fijar versiones de Font Awesome/lucide/`marked`/`dompurify` (hoy usan `@latest`).
- [ ] **Tipado y lint JS** (`eslint` + `prettier`); los `i18n.extra.*.js` ya están bien aislados, mantener ese patrón.
- [ ] **Tests E2E** (Playwright) para el flujo crítico: login → dashboard → chat → logout.
- [ ] **Accesibilidad (a11y):** foco, ARIA y contraste en los modales/drawers.

### Fase 5 — Pruebas y CI real (P1) 🧪
- [ ] **Tests unitarios** para `basededatos.py` (CRUD, migraciones) y `prompt.py` (construcción de prompts).
- [ ] **Tests de integración** contra la app (Flask test client) cubriendo authz y flujo de chat (ya hay un patrón usable: `test_routes.py`).
- [ ] **CI verdadero** en `.github/workflows`: lint + type-check (`mypy`) + tests en cada PR. El actual `static.yml` solo despliega.
- [ ] **`requirements.txt` con versiones fijadas** (+ `requirements-dev.txt`); declarar `gunicorn`/`waitress`.

### Fase 6 — Funcional y producto (P2/P3) 🚀
- [ ] **Roles granulares** (editor, viewer, admin) en lugar de admin/binario.
- [ ] **Multitenant / aislamiento de datos** por usuario u organización.
- [ ] **Auditoría:** tabla de eventos (quién creó/eliminó qué y cuándo) alimentada por el logging de Fase 2.
- [ ] **Externalizar `empresa.py`** (perfiles "Music Pro" hardcodeados) a datos configurables en BD/`identidades.py`.
- [ ] **Configuración en tiempo de ejecución** desde el nuevo módulo `/admin/config` (modelo, temperatura, límites de tokens) en lugar de solo lectura.
- [ ] **Backups y restore** de `agentes.db` automatizados.

---

## 4. Backlog concreto (referencias de archivo)

| # | Cambio | Archivo(s) | Prioridad |
|---|---|---|---|
| 1 | `before_request` que proteja `/api/*` mutadores | `app.py` | P0 |
| 2 | Decorador `require_admin`; proteger `/admin/*` | `app.py` | P0 |
| 3 | `FLASK_SECRET_KEY` obligatorio; sin fallback | `app.py:78` | P0 |
| 4 | CSRF tokens en formularios | `app.py`, `templates/*` | P0 |
| 5 | Rate limit en `/login` | `app.py` | P0 |
| 6 | Servidor WSGI (gunicorn/waitress) | `app.py:1060`, `requirements.txt` | P0 |
| 7 | Restringir `.svg` en uploads | `app.py:82,515` | P0 |
| 8 | Unificar capa datos (clase vs funciones) | `basededatos.py:1477,1653` | P1 |
| 9 | Eliminar aliases bilingües | `basededatos.py:1653–1696` | P1 |
| 10 | Centralizar parsing de `NOMBRE:` | `app.py:116`, `basededatos.py:1541` | P1 |
| 11 | Migraciones con Alembic | `basededatos.py:125,580` | P1 |
| 12 | Logging estructurado + errorhandlers | `app.py`, `basededatos.py` | P1 |
| 13 | Versionar API `/api/v1` | `app.py` | P1 |
| 14 | Validación con pydantic + OpenAPI | `app.py` | P1 |
| 15 | Build frontend (Vite/Tailwind CLI) | `base.html`, `static/*` | P2 |
| 16 | ESLint/Prettier | `static/js/*` | P2 |
| 17 | Tests E2E (Playwright) | nueva carpeta `tests/e2e` | P2 |
| 18 | Tests unit/integration + CI real | `tests/`, `.github/workflows` | P1 |
| 19 | `requirements.txt` fijado | `requirements.txt` | P1 |
| 20 | Roles granulares | `basededatos.py`, `app.py` | P2 |
| 21 | Auditoría de eventos | nueva tabla + logging | P2 |
| 22 | Externalizar `empresa.py` a BD | `empresa.py`, `identidades.py` | P3 |
| 23 | Config runtime en `/admin/config` | `app.py`, `dashboard.html` | P3 |

---

## 5. Estructura objetivo sugerida

```
agente_deepseek/
├── app.py                  # solo rutas web (thin controllers)
├── api/                    # blueprint /api/v1 con contratos pydantic
├── services/               # lógica de negocio (chat, agentes, usuarios)
├── data/                   # capa de datos única + modelos + migraciones (alembic)
├── domain/                 # entidades, prompts (prompt.py), identidades
├── security/               # auth, autorización, csrf, rate-limit
├── config/                 # settings tipados (pydantic-settings)
├── templates/  static/     # frontend (con build)
├── tests/                  # unit + integration + e2e
├── .github/workflows/      # CI: lint + type-check + tests + deploy
└── requirements*.txt       # runtime fijado + dev
```

---

## 6. Definición de "Hecho" (Definition of Done)

Un cambio se considera terminado cuando:
- Cumple los principios de la sección 2.
- Tiene tests que lo cubren (unitario y/o de integración).
- Pasa lint + type-check en CI.
- Documenta su comportamiento (docstring +, si afecta al usuario, `README.md`).
- No introduce secretos en el repo ni deja endpoints mutadores sin authz.

---

*Mantenido por el equipo de desarrollo. Actualizar al completar cada fase.*
