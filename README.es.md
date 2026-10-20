# THEYTHINK AI: Arquitectura Cognitiva Modular de Agentes con Memoria Activa Persistente, Recuperación de Conocimiento Desacoplada y Simulación Multicanal

Consulta la [guía para crear nuevas personalidades](README.personalidades.md), con ejemplos de perfiles y seeders de Music Pro.

<p align="center">
  <img src="theythinkai_logo.png" alt="THEYTHINK AI Logo" width="160" style="border-radius: 24px;" />
</p>

<p align="center">
  <strong>Plataforma Cognitiva Autónoma, Modular y Multi-Persona impulsada por DeepSeek AI</strong><br>
  <em>Memoria Episódica Persistente · Arquitectura de Conocimiento Desacoplada · Síntesis Dinámica de Roles · Simulación Multicanal (Web, WhatsApp, Telegram)</em>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white" alt="Versión de Python" /></a>
  <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/Framework-Flask-000000?style=flat&logo=flask&logoColor=white" alt="Flask" /></a>
  <a href="https://www.sqlite.org/"><img src="https://img.shields.io/badge/Base_de_Datos-SQLite3-003B57?style=flat&logo=sqlite&logoColor=white" alt="SQLite" /></a>
  <a href="https://platform.deepseek.com/"><img src="https://img.shields.io/badge/LLM-DeepSeek_Chat-4D6BFE?style=flat" alt="DeepSeek AI" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/Licencia-MIT-green?style=flat" alt="Licencia: MIT" /></a>
</p>

---

## 🌐 Selección de Idioma
- **[English Documentation](README.md)**
- **[Documentación en Español (Actual)](README.es.md)**

---

## 📑 Tabla de Contenidos
1. [Resumen y Marco Teórico](#-resumen-y-marco-teórico)
2. [Arquitectura del Sistema](#-arquitectura-del-sistema)
3. [Componentes Técnicos Principales](#-componentes-técnicos-principales)
4. [Optimización de Inferencia y Control de Tokens](#-optimización-de-inferencia-y-control-de-tokens)
5. [Simulación de Interfaces Multicanal](#-simulación-de-interfaces-multicanal)
6. [Esquema de Base de Datos y Persistencia](#-esquema-de-base-de-datos-y-persistencia)
7. [Vectores de Investigación y Desarrollo Futuro](#-vectores-de-investigación-y-desarrollo-futuro)
8. [Instalación y Despliegue](#-instalación-y-despliegue)
9. [Licencia y Descargo Ético](#-licencia-y-descargo-ético)

---

## 🔬 Resumen y Marco Teórico

Los Modelos de Lenguaje Masivos (LLMs) operan fundamentalmente como transformadores autorregresivos sin estado interno persistente. En entornos de ejecución tradicionales, presentan tres limitaciones críticas:
1. **Saturación y Deriva de Contexto:** El diálogo multi-turno sobrepasa los límites de atención o diluye las directrices del sistema.
2. **Acoplamiento Rígido del Conocimiento:** Los datos de dominio suelen codificarse en prompts monolíticos o fine-tuning estático, impidiendo la reutilización flexible entre múltiples agentes.
3. **Amnesia Episódica:** Los modelos no retienen hechos aprendidos a través de sesiones de chat independientes sin costosos reentrenamientos.

**THEYTHINK AI** introduce una arquitectura cognitiva modular desarrollada en Python y SQLite que desacopla **Roles de Identidad**, **Bases de Conocimiento Temáticas** y **Memoria Episódica Activa**. Mediante ciclos de extracción y consolidación de hechos en tiempo real y directrices estrictas de presupuesto de tokens, la plataforma mantiene la coherencia longitudinal del agente minimizando el consumo de inferencia en la **API de DeepSeek**.

```
 +-------------------------------------------------------------------------+
 |                          INTERFACES DE USUARIO                          |
 |   +--------------------+  +--------------------+  +-----------------+   |
 |   | Canvas Web Google  |  | Simulador WhatsApp |  | Sim Telegram    |   |
 |   +--------------------+  +--------------------+  +-----------------+   |
 +------------------------------------+------------------------------------+
                                      | HTTP / REST API
 +------------------------------------v------------------------------------+
 |                    CONTROLADOR PRINCIPAL DEL SISTEMA                    |
 |                       (Flask / Autenticación)                           |
 +------------------+-----------------------------------+------------------+
                    |                                   |
 +------------------v------------------+ +--------------v------------------+
 |     PIPELINE DE SÍNTESIS DE PROMPT  | |     EVALUADOR DE MEMORIA ACTIVA |
 |  - Sustitución Dinámica ([____])    | |  - Extracción Hecho a Hecho     |
 |  - Inyección de Reglas de Concisión | |  - Desduplicación de Recuerdos  |
 +------------------+------------------+ +--------------+------------------+
                    |                                   |
 +------------------v-----------------------------------v------------------+
 |                      CAPA DE PERSISTENCIA (SQLite)                      |
 |     [Agentes]    [Bases Conocimiento]    [Roles]    [Historiales]       |
 +------------------------------------+------------------------------------+
                                      | HTTPS (Payload + Límite Tokens)
 +------------------------------------v------------------------------------+
 |                      MOTOR DE INFERENCIA DEEPSEEK                       |
 +-------------------------------------------------------------------------+
```

---

## 🏛️ Arquitectura del Sistema

El sistema implementa una arquitectura desacoplada por capas:

### 1. Capa de Presentación y Simulación Multicanal
- **Espacio de Trabajo Web:** Diseñado con Tailwind CSS y estética Material You / HeroUI, con alternancia de temas claro/oscuro sin parpadeo y gestión de hilos de chat.
- **Simulador Móvil de WhatsApp (`/admin/whatsaap`):** Entorno móvil interactivo con estados *"en línea"*, *"escribiendo..."*, doble check azul (`✓✓`), notas de voz simuladas y copiado con 1 clic.
- **Simulador Móvil de Telegram (`/admin/telegram`):** Vista estilo bot con tarjeta informativa, teclado de comandos (`/start`, `/bases`, `/resumen`, `/memoria`) y menú deslizable (*drawer*).

### 2. Capa de Control y Orquestación (`app.py`, `basededatos.py`)
- Gestión de autenticación segura, control de acceso basado en roles y segmentación multi-hilo de conversaciones.
- Coordinación entre entradas del usuario, consultas de contexto, peticiones a la API y consolidación de memoria en segundo plano.

### 3. Motor de Síntesis Dinámica de Prompts (`prompt.py`, `identidades.py`)
- Ensambla en tiempo de ejecución el System Prompt final:
  $$\text{SystemPrompt} = \mathcal{T}_{\text{tokens}}\Big( \mathcal{R}(\text{Rol}, \text{NombreEntidad}) \oplus \text{Perfil} \oplus \sum \text{BasesConocimiento} \oplus \text{MemoriaActiva} \Big)$$
- Inyecta de forma obligatoria las directrices universales de brevedad y economía de tokens.

### 4. Ciclo de Consolidación de Memoria Episódica
- Al finalizar cada turno de diálogo, un prompt de evaluación independiente identifica hechos nuevos sobre el usuario y los almacena en SQLite sin generar duplicados.

---

## ⚡ Optimización de Inferencia y Control de Tokens

Para optimizar costos y maximizar la velocidad de respuesta, el sistema parametriza y aplica los siguientes rangos de `max_tokens`:

| Tipo de Respuesta | `max_tokens` Recomendado | Aplicación en el Código |
| :--- | :---: | :--- |
| **Respuesta Ultra Corta / Memoria** | `100 – 150` | Evaluación y extracción de hechos para la memoria activa (`actualizar_memoria`). |
| **Chat Normal (Por Defecto)** | `250 – 400` | Conversación estándar e interacción en Web, WhatsApp y Telegram (`preguntar`). |
| **Explicación Técnica** | `500 – 800` | Síntesis analítica profunda y código estructurado bajo solicitud explícita. |

### Directriz Universal de Brevedad
Todo System Prompt generado por `prompt.py` incluye:
- Responde de forma breve, clara y directa.
- Utiliza únicamente la información necesaria para responder.
- No repitas la pregunta ni el contexto del usuario.
- Evita introducciones, conclusiones y explicaciones innecesarias de relleno.
- Prioriza respuestas de 2 a 5 frases concretas.

---

## 📱 Simulación de Interfaces Multicanal

| Ruta | Modo de Interfaz | Capacidades |
| :--- | :--- | :--- |
| `/agente/<nombre>` | **Canvas Web Desktop** | Selector de agentes con buscador integrado, barra lateral multi-hilo, modal de ajustes en vivo, selector i18n (6 idiomas). |
| `/admin/whatsaap` | **Directorio WhatsApp** | Lista general de contactos, buscador en vivo, historias de estado, insignias de rol. |
| `/admin/whatsaap/<nombre>` | **Chat WhatsApp** | Formato de smartphone, indicador escribiendo, botón de copiado por mensaje y de chat completo. |
| `/admin/telegram` | **Directorio Telegram** | Catálogo de bots, menú lateral (*drawer*), pestañas de categorías y filtro instantáneo. |
| `/admin/telegram/<nombre>` | **Chat Telegram** | Teclado de comandos interactivos, respuestas formateadas en Markdown. |

---

## 🗄️ Esquema de Base de Datos y Persistencia

La persistencia de datos reside en SQLite (`agentes.db`):

```sql
-- Entidad Principal de Agentes
CREATE TABLE agentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    perfil TEXT NOT NULL,
    conocimiento TEXT DEFAULT '',
    memoria TEXT DEFAULT '',
    identidad_clave TEXT DEFAULT '',
    identidad_custom TEXT DEFAULT '',
    avatar_url TEXT DEFAULT '',
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Fuentes y Bases de Conocimiento Desacopladas
CREATE TABLE fuentes_conocimiento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    contenido TEXT NOT NULL,
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Matriz de Asociación N:M (Agentes <-> Bases)
CREATE TABLE agente_fuentes (
    agente_id INTEGER REFERENCES agentes(id) ON DELETE CASCADE,
    fuente_id INTEGER REFERENCES fuentes_conocimiento(id) ON DELETE CASCADE,
    PRIMARY KEY (agente_id, fuente_id)
);

-- Roles y System Prompts
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clave TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    descripcion TEXT DEFAULT '',
    prompt TEXT NOT NULL,
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Sesiones Multi-Hilo y Mensajes
CREATE TABLE sesiones_chat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agente_nombre TEXT REFERENCES agentes(nombre) ON DELETE CASCADE,
    titulo TEXT NOT NULL,
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
    actualizado_en DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE conversaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agente_nombre TEXT NOT NULL,
    sesion_id INTEGER REFERENCES sesiones_chat(id) ON DELETE CASCADE,
    fecha TEXT NOT NULL,
    hora TEXT NOT NULL,
    rol TEXT NOT NULL,
    mensaje TEXT NOT NULL
);
```

---

## 🚀 Vectores de Investigación y Desarrollo Futuro

La arquitectura modular de THEYTHINK AI constituye una base sólida para extensiones de investigación y desarrollo avanzado:

1. **Redes de Deliberación Multi-Agente:** Protocolos de consenso donde múltiples agentes (por ejemplo, *Albert Einstein*, *Sócrates* y *Nikola Tesla*) debatan colaborativamente.
2. **RAG Híbrido Denso/Disperso:** Integración de extensiones vectoriales locales en SQLite (`sqlite-vss` o ChromaDB) junto al motor de bases temáticas.
3. **Aumento Autónomo con Herramientas (Function Calling):** Capacidad para que los agentes ejecuten código Python, consultas web y llamadas API en un sandbox seguro.
4. **Interacción por Voz Extremo a Extremo:** Integración de pipelines de streaming WebAudio + Whisper y síntesis neuronal para interacción por voz en tiempo real.

---

## 📦 Instalación y Despliegue

Consulta la guía detallada en **[INSTALL.md](INSTALL.md)**.

### Instalación Rápida Automática (Windows 1-Click)
1. Ejecuta el instalador automatizado:
   ```cmd
   install.bat
   ```
2. Inicia la aplicación en cualquier momento con:
   ```cmd
   iniciar.bat
   ```

### Instalación Manual (Todas las Plataformas)
```bash
# 1. Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate       # Linux/macOS
.\venv\Scripts\activate        # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env           # Ingresa tu DEEPSEEK_API_KEY en .env

# 4. Poblar datos iniciales y personajes canónicos
python seed.py

# 5. Iniciar servidor Flask
python app.py
```
Abre en tu navegador: **[http://localhost:5000](http://localhost:5000)**. Credenciales por defecto: `admin` / `admin123`.

---

## ⚖️ Licencia y Descargo Ético

Este proyecto se distribuye bajo la **[Licencia MIT](LICENSE)**.

> **Descargo de Responsabilidad de la IA:** Las respuestas generadas por los agentes son producidas de forma automatizada por modelos de lenguaje (API de DeepSeek). El equipo desarrollador y la iniciativa THEYTHINK no asumen responsabilidad por la veracidad o exactitud de las respuestas generadas. Se advierte expresamente **no ingresar datos personales reales sensibles, contraseñas o secretos comerciales** en las conversaciones ni en las bases de conocimiento.
