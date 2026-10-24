# THEYTHINK AI: A Modular Cognitive Agent Architecture with Persistent Active Memory, Decoupled Knowledge Retrieval, and Multi-Channel Simulation

<p align="center">
  <img src="theythinkai_logo.png" alt="THEYTHINK AI Logo" width="160" style="border-radius: 24px;" />
</p>

<p align="center">
  <strong>Autonomous, Modular, Multi-Persona Cognitive Platform powered by DeepSeek AI</strong><br>
  <em>Persistent Episodic Memory · Decoupled Knowledge Base Architecture · Dynamic Role Synthesis · Multi-Interface Simulation (Web, WhatsApp, Telegram)</em>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white" alt="Python Version" /></a>
  <a href="https://www.djangoproject.com/"><img src="https://img.shields.io/badge/Framework-Django-0C4B33?style=flat&logo=django&logoColor=white" alt="Django" /></a>
  <a href="https://www.sqlite.org/"><img src="https://img.shields.io/badge/Database-SQLite3-003B57?style=flat&logo=sqlite&logoColor=white" alt="SQLite" /></a>
  <a href="https://platform.deepseek.com/"><img src="https://img.shields.io/badge/LLM-DeepSeek_Chat-4D6BFE?style=flat" alt="DeepSeek AI" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=flat" alt="License: MIT" /></a>
</p>

---

## 🌐 Language Selection
- **[English Documentation (Current)](README.md)**
- **[Documentación en Español](README.es.md)**

---

## 📑 Table of Contents
1. [Abstract & Theoretical Framework](#-abstract--theoretical-framework)
2. [System Architecture](#-system-architecture)
3. [Core Technical Components](#-core-technical-components)
4. [Token Conservation & Inference Optimization](#-token-conservation--inference-optimization)
5. [Multi-Channel Interface Simulation](#-multi-channel-interface-simulation)
6. [Database Schema & Persistence Topology](#-database-schema--persistence-topology)
7. [Research & Future Development Vectors](#-research--future-development-vectors)
8. [Installation & Deployment](#-installation--deployment)
9. [License & Ethical Disclaimer](#-license--ethical-disclaimer)

---

## 🔬 Abstract & Theoretical Framework

Conversational Large Language Models (LLMs) fundamentally operate as stateless autoregressive transformers. In vanilla execution environments, they suffer from three chronic architectural limitations:
1. **Context Window Saturation & Drift:** Multi-turn dialogue rapidly exceeds attention bounds or dilutes system constraints.
2. **Knowledge Coupling:** Domain-specific knowledge is traditionally hardcoded into monolithic system prompts or fine-tuned weights, preventing dynamic multi-tenant knowledge sharing.
3. **Episodic Amnesia:** Models cannot retain facts across independent chat sessions without expensive retraining or complex vector infrastructure.

**THEYTHINK AI** introduces a lightweight, deterministic cognitive middleware engineered in Python and SQLite that decouples **Identity Roles**, **Static Knowledge Bases**, and **Dynamic Episodic Memory**. By running real-time fact extraction loops and enforcing token budgeting algorithms, the platform maintains longitudinal agent coherence while minimizing inference overhead against the **DeepSeek API**.

```
 +-------------------------------------------------------------------------+
 |                            USER INTERFACES                              |
 |   +--------------------+  +--------------------+  +-----------------+   |
 |   | Material Web UI    |  | WhatsApp Simulator |  | Telegram Sim    |   |
 |   +--------------------+  +--------------------+  +-----------------+   |
 +------------------------------------+------------------------------------+
                                      | HTTP / REST API
 +------------------------------------v------------------------------------+
 |                     CORE APPLICATION CONTROLLER                         |
 |                       (Django / Authentication)                         |
 +------------------+-----------------------------------+------------------+
                    |                                   |
 +------------------v------------------+ +--------------v------------------+
 |     PROMPT SYNTHESIS PIPELINE       | |    ACTIVE MEMORY EVALUATOR      |
 |  - Marker Substitution ([____])     | |  - Turn-by-Turn Fact Extractor  |
 |  - Conciseness Directive Enforcer   | |  - De-duplication Sanitizer     |
 +------------------+------------------+ +--------------+------------------+
                    |                                   |
 +------------------v-----------------------------------v------------------+
 |                       PERSISTENCE ENGINE (SQLite)                       |
 |    [Agents]   [Knowledge Bases]   [Roles]   [Users]   [Sessions]        |
 +------------------------------------+------------------------------------+
                                      | HTTPS (Payload + Token Bound)
 +------------------------------------v------------------------------------+
 |                       DEEPSEEK INFERENCE ENGINE                         |
 +-------------------------------------------------------------------------+
```

---

## 🏛️ System Architecture

THEYTHINK AI follows a layered, modular architecture:

### 1. Presentation & Multi-Channel Layer
- **Responsive Web Workspace:** Built with Tailwind CSS and Google Material You / HeroUI aesthetics, featuring zero-flicker dark/light themes and collapsible multi-thread navigation.
- **WhatsApp Mobile Simulator (`/admin/whatsaap`):** High-fidelity mobile canvas featuring real-time typing indicators, read receipts (`✓✓`), audio note waveforms, and contact management.
- **Telegram Mobile Simulator (`/admin/telegram`):** Bot-centric mobile view with `/start` command cards, quick bot keyboards, drawer menus, and inline copy shortcuts.

### 2. Cognitive Orchestration Layer (`app.py`, `basededatos.py`)
- Manages secure user authentication, role-based access control (RBAC), and session multi-threading.
- Coordinates between user queries, context retrieval, API calls, and background memory synthesis.

### 3. Dynamic Prompt Synthesis Engine (`prompt.py`, `identidades.py`)
- Dynamically compiles composite System Prompts by merging:
  $$\text{SystemPrompt} = \mathcal{T}_{\text{tokens}}\Big( \mathcal{R}(\text{Role}, \text{EntityName}) \oplus \text{Profile} \oplus \sum \text{KnowledgeSources} \oplus \text{ActiveMemory} \Big)$$
- Injects universal conciseness directives that force concise, highly factual outputs.

### 4. Episodic Memory Consolidation Loop
- At the conclusion of each dialogue turn, an asynchronous evaluation prompt inspects the exchange for novel persistent facts, updating the agent's SQLite memory table without duplicate redundancy.

---

## ⚡ Token Conservation & Inference Optimization

To maximize inference velocity and minimize operational API expenditure, THEYTHINK AI enforces deterministic token boundaries across three operational tiers:

| Response Tier | Recommended `max_tokens` | Algorithmic Application |
| :--- | :---: | :--- |
| **Ultra-Short / Memory Evaluation** | `100 – 150` | Background fact extraction and memory consolidation (`actualizar_memoria`). |
| **Standard Conversational Turn** | `250 – 400` | Default interactive chat threshold (`preguntar`, WhatsApp & Telegram messaging). |
| **Technical / In-Depth Synthesis** | `500 – 800` | Analytical explanations and code synthesis upon explicit parameter invocation. |

### Universal Behavioral Directive
Every System Prompt synthesized by `prompt.py` includes mandatory conciseness constraints:
- Deliver direct, clear, and focused responses.
- Utilize only the necessary information to resolve the prompt.
- Never repeat or rephrase the user's question.
- Omit conversational filler, unsolicited introductions, and redundant conclusions.
- Prioritize concise density (2 to 5 targeted sentences).

---

## 📱 Multi-Channel Interface Simulation

| Route | Interface Mode | Architectural Capabilities |
| :--- | :--- | :--- |
| `/agente/<name>` | **Desktop Web Canvas** | Multi-thread sidebar, hot-settings modal, language switcher (6 locales), live audit logs. |
| `/admin/whatsaap` | **WhatsApp Directory** | Mobile contact index, search filter, status stories carousel, unread badge indicators. |
| `/admin/whatsaap/<name>` | **WhatsApp Chat** | Smartphone viewport, typing simulator, message-level 1-click clipboard copy, audio note simulation. |
| `/admin/telegram` | **Telegram Directory** | Bot catalog, sliding navigation drawer, category tabs, real-time query filter. |
| `/admin/telegram/<name>` | **Telegram Chat** | Bot command keyboard (`/start`, `/bases`, `/resumen`, `/memoria`), inline message actions. |

---

## 🗄️ Database Schema & Persistence Topology

The persistence layer is managed within SQLite (`agentes.db`):

```sql
-- Core Agent Entity
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

-- Decoupled Knowledge Bases
CREATE TABLE fuentes_conocimiento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    contenido TEXT NOT NULL,
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- N:M Association Matrix (Agents <-> Knowledge Bases)
CREATE TABLE agente_fuentes (
    agente_id INTEGER REFERENCES agentes(id) ON DELETE CASCADE,
    fuente_id INTEGER REFERENCES fuentes_conocimiento(id) ON DELETE CASCADE,
    PRIMARY KEY (agente_id, fuente_id)
);

-- Dynamic System Roles & Personas
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clave TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    descripcion TEXT DEFAULT '',
    prompt TEXT NOT NULL,
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Multi-Thread Chat Sessions & Transcripts
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

## 🚀 Research & Future Development Vectors

The modular architecture of THEYTHINK AI provides a foundation for academic research and advanced engineering extensions:

1. **Multi-Agent Deliberation Networks:** Implementing consensus protocols where multiple agents (e.g., *Albert Einstein*, *Socrates*, and *Nikola Tesla*) engage in structured inter-agent debate rounds.
2. **Hybrid Dense/Sparse Vector RAG:** Integrating local SQLite vector extensions (`sqlite-vss` or ChromaDB) alongside the existing decoupled knowledge base engine.
3. **Autonomous Tool Augmentation (Function Calling):** Equipping agents with deterministic tool sandboxes for live web searching, Python code execution, and database querying.
4. **Speech-to-Speech Streaming Pipelines:** Connecting Whisper/WebAudio streaming input directly to low-latency neural TTS synthesis for native voice interaction in the mobile simulators.

---

## 📦 Installation & Deployment

Consult **[INSTALL.md](INSTALL.md)** for exhaustive deployment documentation.

### Rapid Setup (Windows 1-Click)
1. Run the automated installer:
   ```cmd
   install.bat
   ```
2. Start the platform anytime via:
   ```cmd
   iniciar.bat
   ```

### Manual Installation (All Platforms)
```bash
# 1. Initialize virtual environment
python -m venv venv
source venv/bin/activate       # Linux/macOS
.\venv\Scripts\activate        # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment credentials
cp .env.example .env           # Provide your DEEPSEEK_API_KEY in .env

# 4. Apply migrations and seed canonical agents
python manage.py migrate
python manage.py seed

# 5. Launch application server (Django)
python manage.py runserver 127.0.0.1:8000
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser. Default credentials: `admin` / `admin123`.
Django Admin Panel available at **[http://localhost:8000/django-admin/](http://localhost:8000/django-admin/)**.

---

## ⚖️ License & Ethical Disclaimer

This project is licensed under the **[MIT License](LICENSE)**.

> **AI Disclaimer:** Responses generated by agents are produced automatically by large language models (DeepSeek API). The development team and the THEYTHINK initiative assume no responsibility for the veracity, factual accuracy, or potential hallucinations of generated outputs. Users are explicitly warned **not to input real, sensitive, confidential, or proprietary personal data** into conversational streams or knowledge bases.