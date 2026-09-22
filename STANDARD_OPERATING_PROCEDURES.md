# 📖 Standard Operating Procedures (SOP) & Architecture Guide

Welcome to the **AI Advance RAG & Live Web Search Application**! This comprehensive guide provides a complete end-to-end breakdown of the application architecture, file directory structure, data flows, dependencies, setup instructions, database schemas, pipeline tracing, evaluation metrics, and deployment steps.





---

## 📋 Table of Contents
1. [🌟 Application Overview](#-application-overview)
2. [🏗️ Architecture & Technical Stack](#️-architecture--technical-stack)
3. [📊 System Data Flow Diagrams](#-system-data-flow-diagrams)
4. [📁 Complete Directory & File Guide](#-complete-directory--file-guide)
5. [📦 Key Packages & Libraries Used](#-key-packages--libraries-used)
6. [🚀 Step-by-Step Beginner Guide (Local to Web Deployment)](#-step-by-step-beginner-guide-local-to-web-deployment)
   - [Step 1: System Prerequisites](#step-1-system-prerequisites)
   - [Step 2: Virtual Environment Setup](#step-2-virtual-environment-setup)
   - [Step 3: Ollama Setup (Local LLM)](#step-3-ollama-setup-local-llm)
   - [Step 4: Launch Application Server](#step-4-launch-application-server)
   - [Step 5: Managing Busy Ports & Troubleshooting](#step-5-managing-busy-ports--troubleshooting)
   - [Step 6: Make Application Publicly Live via `npx` Tunnel](#step-6-make-application-publicly-live-via-npx-tunnel)
7. [⚙️ Centralized LLM & System Settings Management](#️-centralized-llm--system-settings-management)
8. [📂 SQLite Database Architecture & `chat_history_records` Table](#-sqlite-database-architecture--chat_history_records-table)
9. [📈 Real-Time RAG Evaluation & Response Metrics Card](#-real-time-rag-evaluation--response-metrics-card)
10. [🔁 Collapsible Pipeline Trace Panel](#-collapsible-pipeline-trace-panel)
11. [📊 Chat History & Retrieval Analytics Viewport & CSV Export](#-chat-history--retrieval-analytics-viewport--csv-export)
12. [💬 ChatGPT & Claude Style Chat History & Sidebar](#-chatgpt--claude-style-chat-history--sidebar)
13. [✨ Typography, Question/Context Cards & Clean Markdown](#-typography-questioncontext-cards--clean-markdown)
14. [🤖 Dynamic LLM-Based Greetings](#-dynamic-llm-based-greetings)
15. [🔍 Complete Features Breakdown](#-complete-features-breakdown)
16. [🌐 Website Knowledge Ingestion & Management Dashboard](#-website-knowledge-ingestion--management-dashboard)
17. [⚙️ Production Qdrant Scalability & Batching Ingestion](#-production-qdrant-scalability--batching-ingestion)
18. [💬 Persistent Response Metrics & Prompt Action Syncing](#-persistent-response-metrics--prompt-action-syncing)
19. [👍 RAG Learning & Retrieval Feedback Manager](#-rag-learning--retrieval-feedback-manager)

---

## 🌟 Application Overview

The **AI Advance RAG Application** is a production-grade Enterprise Retrieval-Augmented Generation (RAG) platform with multi-modal document ingestion, hybrid vector retrieval, live Web Search synthesis, real-time pipeline step tracing, RAG response metrics evaluation, relational chat history analytics, and centralized settings management.

### Key Capabilities:
- **Local & Cloud LLMs:** Runs locally using **Ollama** (Llama 3, Mistral, Phi-3) without needing any cloud API keys, while supporting API integrations for **OpenAI (GPT-4o)**, **Google Gemini**, **Anthropic Claude**, **Groq (LLaMA 3.3 70B)**, and **xAI Grok**.
- **Real-Time Response Metrics:** Every assistant turn evaluates and displays **Correctness %** (Answer Relevance), **Faithfulness %** (Context Groundedness), **Groundedness %** (Context Relevance), **Confidence %**, **Time Taken (seconds)**, and estimated **Token Cost** directly on the message bubble.
- **Collapsible Pipeline Trace Panel:** A collapsible bottom panel positioned below the prompt box tracks every backend step in real-time (Query Classification, Rewriting, Embedding Generation, Hybrid Search, Context Assembly, LLM Execution, and Evaluation).
- **Chat History & Retrieval Analytics Viewport:** Accessible via top-right header button (`<button id="top-history-btn">`). Features a **`← Back to RAG App`** button to return instantly to the active chat viewport. Stores 12 detailed relational columns in SQLite (`chat_history_records` table) with filterable search and **📥 CSV Export** (`/api/history/csv`).
- **ChatGPT & Claude Style Sidebar:** Sleek, minimal left sidebar dedicated exclusively to recent conversations with inline title renaming (`PUT /api/chats/{chat_id}`) and instant deletion (`DELETE /api/chats/{chat_id}`).
- **Snapshot-Style Formatting & Artifact Stripping:** Headings are rendered in crisp white bold typography (`Step X: ...`), sublabels (`The LLM receives:`, `Then generates:`), and structured Question/Context blocks inside dark rounded containers with monospace text and an inline copy button. Raw `#` and `*` markdown artifacts are automatically stripped.
- **Fixed Configuration Drawer Alignment:** Zero-gap, hardware-accelerated CSS transform positioning (`position: fixed; right: 0; transform: translateX(100%) -> translateX(0)`) ensuring the right drawer slides smoothly without leaving blank black space gaps.
- **Centralized Settings Single Source of Truth:** Synchronized LLM provider, sub-model selection, API keys, retriever params, and system prompt across UI & backend (`GET/PUT /api/settings`).
- **Hybrid Vector Retrieval:** Combines dense embeddings (via **Qdrant** / **FAISS** with `nomic-embed-text`) with sparse keyword retrieval (BM25) for high context relevance.

---

## 🏗️ Architecture & Technical Stack

```
+---------------------------------------------------------------------------------------+
|                              FRONTEND INTERFACE                                       |
|  - Modern Single-Page App (HTML5 + Glassmorphism CSS + Vanilla JavaScript ES6)        |
|  - Main Chat Viewport, Pipeline Trace Panel, & Chat History Analytics Viewport        |
+---------------------------------------------------------------------------------------+
                                           │  HTTP / REST API
                                           ▼
+---------------------------------------------------------------------------------------+
|                              BACKEND (FastAPI / Python 3.12+)                         |
|  - main.py / router.py                                                                |
|  - Routes: /api/chats, /api/documents, /api/search, /api/settings, /api/history       |
+---------------------------------------------------------------------------------------+
       │                                     │                                    │
       ▼                                     ▼                                    ▼
+-----------------------+   +-------------------------------+   +-----------------------+
|  LLM FACTORY & ROUTER |   |   HYBRID VECTOR RETRIEVAL     |   | RELATIONAL SQLITE DB  |
| - Ollama (Local)      |   | - Qdrant Vector DB (Dense)    |   | - chat_history.db     |
| - OpenAI (GPT-4o)     |   | - FAISS Store                 |   | - chat_history_records|
| - Gemini / Claude     |   | - BM25 Sparse Search          |   |   (12 Detailed Cols)  |
| - Groq / xAI Grok     |   | - BAAI BGE Reranker           |   | - CSV Export Engine   |
+-----------------------+   +-------------------------------+   +-----------------------+
```

### Core Technologies:
- **Backend Framework:** FastAPI (Python 3.12+)
- **ASGI Server:** Uvicorn (`http://0.0.0.0:8000`)
- **Database Engine:** SQLite (Stored in `backend/data/database_files/chat_history.db`)
- **Vector Stores:** Qdrant (Collection: `knowledge_base`, `long_term_memory`) & FAISS
- **Embeddings:** HuggingFace / Nomic (`nomic-embed-text`) & PyTorch
- **Reranker:** BAAI/bge-reranker-base
- **Frontend Stack:** HTML5, Modern Glassmorphism CSS, Vanilla ES6 JavaScript

---

## 📊 System Data Flow Diagrams

### 1. RAG Query & Pipeline Trace Flow:
```
User Prompt (Local/Web Mode)
  ──► Step 1: Query Classification (Intent: KNOWLEDGE / CODING / GREETING / etc.)
  ──► Step 2: Query Rewriting (Optimizes prompt for semantic search)
  ──► Step 3: Embedding Generation (Generates nomic-embed-text vector preview)
  ──► Step 4: Semantic & Keyword Search (Qdrant Dense + BM25 Fusion)
  ──► Step 5: Context Assembly (Formats retrieved snippets & citations)
  ──► Step 6: Send to LLM (Model status & execution)
  ──► Step 7: RAG Evaluation (Calculates Correctness, Faithfulness, Groundedness)
  ──► Log Detailed Record to SQLite `chat_history_records` Table
  ──► Return Response + Metrics Card + Pipeline Trace + Citations
```

### 2. Relational Analytics & CSV Export Flow:
```
User Clicks Top-Right "Chat History" Button (<button id="top-history-btn">)
  ──► Switches to `#history-viewport` (Hides Chat Viewport)
  ──► API Fetch: `GET /api/history`
  ──► Renders 12 Detailed Columns into Data Table
  ──► Click "Export CSV": Triggers `GET /api/history/csv`
  ──► Downloads `chat_history_analytics.csv` file directly for analysis
  ──► Click "← Back to RAG App": Switches back to active chat session
```

---

## 📁 Complete Directory & File Guide

```
AI_Advance_RAG_App/
│
├── backend/                        # Python Backend Source Code
│   ├── main.py                     # Entry point for FastAPI application
│   ├── settings.py                 # Pydantic environment configuration & settings
│   ├── lifespan.py                 # Application startup/shutdown lifespan tasks
│   ├── requirements.txt            # Python dependencies package list
│   │
│   ├── api/                        # API Routing Layer
│   │   ├── router.py               # Central APIRouter registering all sub-routers
│   │   └── routes/                 # Endpoint implementations
│   │       ├── chat.py             # Chat creation, messaging, memory, RAG generation, /api/history
│   │       ├── documents.py        # File upload, document listing, indexing, deletion
│   │       ├── search.py           # Google/DuckDuckGo live web search & synthesis
│   │       ├── settings.py         # Centralized system settings GET & PUT API
│   │       ├── url.py              # Webpage URL loader and vector indexer
│   │       ├── performance.py      # Real-time metrics & dashboard endpoint
│   │       └── health.py           # Server status health check
│   │
│   ├── memory/                     # SQLite Conversation & Registry Store
│   │   └── memory_service.py       # Manages conversations, messages, and chat_history_records table
│   │
│   ├── llm/                        # LLM Model Providers Layer
│   │   ├── config.py               # LLM Configuration dataclass
│   │   ├── factory.py              # Dynamic LLM provider instantiation factory
│   │   └── providers/              # Specific LLM Provider Implementations (Ollama, OpenAI, Gemini, Claude, Grok)
│   │
│   ├── services/                   # Core RAG Business Logic Services
│   │   ├── embedding_service.py    # Embedding generation using nomic-embed-text
│   │   ├── chunking/               # Semantic, Token, and Sentence Chunking modules
│   │   ├── ingestion/              # Loaders for PDF, DOCX, CSV, Text, Web URLs, and Image OCR
│   │   ├── retrieval/              # Dense, Sparse, Metadata Filtering, Query Rewriter
│   │   ├── generation/             # Prompt Builder & Answer Generator
│   │   └── vector_store/           # Qdrant and FAISS vector store managers
│   │
│   └── data/                       # Structured Data Repositories
│       ├── csv/ docx/ images/ pdf/ pptx/ txt/ xlsx/
│       └── database_files/         # Organized SQLite storage (chat_history.db, WAL files)
│
├── frontend/                       # Web Client Source Files
│   ├── index.html                  # Main Single Page App structure (Chat Viewport & History Viewport)
│   ├── style.css                   # Glassmorphism styling, metrics cards, pipeline trace, data tables
│   └── app.js                      # Core JS logic, pipeline panel handlers, history table renderer, API client
│
├── .env                            # Active environment variables store (API Keys, URLs)
├── start_tunnel.py                 # Helper Python script to expose local server via npx tunnel
├── Dockerfile                      # Container build configuration
├── docker-compose.yml              # Multi-container orchestration configuration
└── STANDARD_OPERATING_PROCEDURES.md# Complete System SOP & Developer Documentation
```

---

## 📦 Key Packages & Libraries Used

### Backend Dependencies (`backend/requirements.txt`):
| Package | Purpose |
|---|---|
| `fastapi` | High-performance Web API framework |
| `uvicorn[standard]` | Lightning-fast ASGI web server |
| `pydantic` / `pydantic-settings` | Data validation and `.env` settings management |
| `qdrant-client` | Client for Qdrant Vector Database |
| `faiss-cpu` | High-efficiency similarity search vector index |
| `torch` / `transformers` | Machine learning runtime for embeddings & reranking |
| `sentence-transformers` | HuggingFace embedding models (`nomic-embed-text`) |
| `pypdf` / `python-docx` / `python-pptx` | Document text extraction |
| `httpx` | Async HTTP client for cloud LLM API requests |
| `pytesseract` / `easyocr` / `Pillow` | Optical Character Recognition (OCR) for images |
| `beautifulsoup4` / `requests` | Web scraping and HTML parsing |

---

## 🚀 Step-by-Step Beginner Guide (Local to Web Deployment)

### Step 1: System Prerequisites
Ensure your machine has the following installed:
- **Python 3.12+**: Check using `python3 --version`
- **Node.js & npx**: Check using `npx --version`
- **Ollama**: Download from [ollama.com](https://ollama.com)

---

### Step 2: Virtual Environment Setup
Open your terminal and navigate to the project directory:

```bash
cd /Users/kanaram/Desktop/AI_Advance_RAG_App
```

Create and activate a Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

Install required packages:
```bash
pip install -r backend/requirements.txt
```

---

### Step 3: Ollama Setup (Local LLM)
Start Ollama and pull the default Llama 3 model:
```bash
ollama run llama3
```

---

### Step 4: Launch Application Server
To start the AI RAG server locally on port **8000**, run:

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Open your browser and navigate to:
👉 **`http://localhost:8000`**

---

### Step 5: Managing Busy Ports & Troubleshooting

If you encounter an error saying `Port 8000 is already in use`, run these commands:

1. **Check process using port 8000:**
   ```bash
   lsof -i :8000
   ```

2. **Terminate the process on port 8000 instantly:**
   ```bash
   kill -9 $(lsof -t -i :8000)
   ```

3. **1-Line Force-Restart Command:**
   ```bash
   lsof -ti :8000 | xargs kill -9 2>/dev/null; python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

---

### Step 6: Make Application Publicly Live via `npx` Tunnel

To share your application live on the internet:
```bash
npx localtunnel --port 8000
```

---

## ⚙️ Centralized LLM & System Settings Management

The application features a centralized Settings Service (`GET /api/settings` and `PUT /api/settings`):
- **Single Source of Truth:** Updating the active LLM provider or model from either the Settings Modal or Prompt Space LLM dropdown updates both immediately.
- **Persistence Across Sessions:** Selections and API keys are saved dynamically into `os.environ` and `.env`, maintaining state across browser refreshes and server restarts.

---

## 📂 SQLite Database Architecture & `chat_history_records` Table

All conversation histories, messages, document registries, and full analytics records are managed via SQLite inside **`backend/data/database_files/chat_history.db`**.

### `chat_history_records` Relational Schema:
```sql
CREATE TABLE IF NOT EXISTS chat_history_records (
    id TEXT PRIMARY KEY,
    timestamp_ist TEXT NOT NULL,
    user_prompt TEXT NOT NULL,
    retrieved_response TEXT NOT NULL,
    response_metrics TEXT,       -- JSON string of correctness, faithfulness, groundedness, confidence
    timetaken_s REAL,             -- Latency in seconds
    similarity_score REAL,        -- Top similarity score (or NULL)
    llm_model TEXT NOT NULL,      -- LLM model used
    memory_source TEXT,           -- 'Long-Term Memory', 'Short-Term Memory', 'None'
    files_used TEXT,              -- Filename(s) or NULL
    chunks_used TEXT,             -- Chunk IDs or NULL
    search_source TEXT NOT NULL,  -- 'Vector DB (Local)', 'Google / Web Search', 'LLM Direct Knowledge', 'Direct Attachment'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

## 📈 Real-Time RAG Evaluation & Response Metrics Card

Every assistant response automatically calculates and displays a **Response Metrics** card:
- **Correctness %:** Answer relevance score evaluating how well the answer addresses the prompt.
- **Faithfulness %:** Groundedness score measuring if facts in the answer are strictly supported by context.
- **Groundedness %:** Context relevance score evaluating context precision.
- **Confidence %:** Overall weighted average of all three metrics.
- **Time Taken:** Total response latency in seconds (e.g. `1.85s`).
- **Token Cost:** Estimated cost based on model provider pricing (e.g. `$0.0000 (Local)` or `~$0.0005`).

---

## 🔁 Collapsible Pipeline Trace Panel

The collapsible panel below the prompt space box displays real-time execution steps:
1. **Query Classification:** Identifies query intent (Knowledge, Coding, Greeting, etc.).
2. **Query Rewriting:** Rewrites prompt for semantic precision.
3. **Embedding Generation:** Converts prompt into vector embedding (shows dimension and vector sample).
4. **Semantic & Keyword Search:** Executes dense vector + BM25 sparse search.
5. **Context Assembly:** Assembles retrieved document chunks.
6. **Send to LLM:** Transmits context + prompt to active model.
7. **RAG Evaluation:** Computes final metrics.

---

## 📊 Chat History & Retrieval Analytics Viewport & CSV Export

- **Top Right Access:** Click the `<button id="top-history-btn">` in the header bar to launch the analytics view.
- **`← Back to RAG App` Button:** Positioned on the top-left to return instantly to your active chat session.
- **12 Relational Columns Table:** Displays `Unique ID`, `Timestamp (IST)`, `User Prompt`, `Retrieved Response`, `Response Metrics`, `Time Taken (s)`, `Similarity Score`, `LLM Model`, `Memory Source`, `File(s) Used`, `Chunk(s) Used`, and `Search Source`. Automatically populates `NULL` where applicable.
- **CSV Download:** Click **`📥 Export CSV`** (`/api/history/csv`) to download `chat_history_analytics.csv` for data science and auditing.

---

## 💬 ChatGPT & Claude Style Chat History & Sidebar

- **Minimalist Layout:** Unnecessary navigation menus have been removed, devoting the sidebar exclusively to recent chat history.
- **Inline Title Renaming:** Double-click or click the pencil icon to rename chat titles inline (`PUT /api/chats/{chat_id}`) with **Save (✓)** and **Cancel (✕)** buttons.
- **Instant Chat Deletion:** Click the trash icon to delete conversations from the SQLite database (`DELETE /api/chats/{chat_id}`).

---

## ✨ Typography, Question/Context Cards & Clean Markdown

- **Clean Headings:** Headings (`Step X: ...`) render in bold white text (`#ffffff`, `15.5px`) without raw `#` artifacts.
- **Sublabels & Cards:** `The LLM receives:` and `Then generates:` sublabels frame a dark rounded card (`rgba(255, 255, 255, 0.03)`) containing `Question:` and `Context:` with an inline top-right **Copy** button.
- **Artifact Stripping:** All stray `#` and `*` raw markdown characters are stripped from retrieved context and model outputs.

---

## 🤖 Dynamic LLM-Based Greetings

Simple user greetings (`hi`, `hello`, `hey`, `good morning`) bypass database retrieval for maximum speed and are answered directly by your active LLM model without hardcoded static messages.

---

## 🔍 Complete Features Breakdown

1. **Response Metrics Card on Message Bubbles:** Real-time Correctness, Faithfulness, Groundedness, Confidence, Latency, and Token Cost.
2. **Collapsible Pipeline Trace Panel:** Real-time 7-step execution trace below prompt box.
3. **Chat History & Retrieval Analytics Viewport:** 12-column relational data table with IST timestamps, similarity scores, memory/search sources, filter bar, and CSV export.
4. **`← Back to RAG App` Navigation:** Seamlessly switch between Analytics and Chat.
5. **ChatGPT / Claude Style Sidebar:** Dedicated conversation list with inline rename and delete.
6. **Zero-Gap Configuration Drawer:** Fixed hardware-accelerated drawer sliding flush against right viewport edge.
7. **Snapshot Formatting & Clean Text:** Monospace Question/Context cards, styled sublabels, and raw artifact stripping.
8. **Webpage URL & Document Ingestion:** Index public URLs and multi-modal files into Qdrant & FAISS.
9. **Centralized Settings & Persistence:** Synchronized LLM provider selection and API keys across sessions.
10. **Website Knowledge Ingestion Dashboard**: Global seeded config and user URL crawler panel with sitemap extraction, rate-limiting, and aggregate JSON backups.
11. **Production Qdrant Support**: Configures remote host connection and batched upserts to avoid lock contention and memory exhaustion.
12. **Persistent Response Metrics**: SQLite message metrics column storage to render RAG evaluation values even across app reloads.

---

## 🌐 Website Knowledge Ingestion & Management Dashboard

Introduced a modular website crawling and vector indexing pipeline accessible via the top-right globe icon:
- **Dashboard Interface (`/website`)**: An administration panel hosting KPI stats (Discovered, Crawled, Chunks, Embeddings), a submission form, a global config switcher to permit/block user-supplied ingestion, and an auto-refreshing list of active crawled websites with download and delete controls.
- **Auto-Discovery Sitemap Crawler**: Automatically extracts all URLs from a target `sitemap.xml`. If missing, it crawls the domain recursively up to a configurable depth and page limit. Handles robots.txt validation, removes duplicate URLs, respects server rate limits (polite rest timers), and strips script/menus/boilerplate tags.
- **Aggregate JSON backups**: Once a website is crawled, the system saves all pages into `backend/data/json/{website_friendly_name}.json` as a single file. Deleting a registered site automatically removes its JSON file.
- **Direct JSON Auto-Ingestion**: Placing any previously crawled dataset file inside `backend/data/json/` directory triggers the auto-sync watcher engine. It reads the custom page array format, parses title headers and content blocks, and indexes them directly into the vector database without re-crawling.

---

## ⚙️ Production Qdrant Scalability & Batching Ingestion

Optimized the backend for processing terabytes (TBs) of enterprise documentation:
- **Connection Routing**: Supports connecting to a remote **Qdrant Server cluster** by configuring the `QDRANT_URL` and `QDRANT_API_KEY` settings or environment variables, avoiding filesystem locking issues on concurrent background requests.
- **Batched Point Upserting**: The vector ingestion client splits point lists into small batches (default `100` points per request) to prevent memory overflows, HTTP timeouts, and gRPC payload size errors during large document uploads.
- **RAG Token Optimization**: Restricts retrieved knowledge fragments to top 3 matching chunks, significantly reducing prompt token count and API costs.

---

## 💬 Persistent Response Metrics & Prompt Action Syncing

Improved usability and data persistence in the chat view:
- **SQLite Schema Migration**: Added a persistent `metrics` column to the `messages` table. On startup, the system performs a backward-compatible migration (`ALTER TABLE messages ADD COLUMN metrics TEXT`) to preserve RAG response stats permanently.
- **Unconditional User Action Buttons**: User prompt boxes immediately display Copy, Edit, and Google Search buttons.
- **Dynamic Message ID Syncing**: While the model is generating, prompts use a temporary ID. Once saved, the response payload returns the final database user message ID, which updates the DOM element dynamically, allowing immediate editing and resubmitting.
- **Edit Loading Locks**: Shows warning toast notifications if the user attempts to edit a prompt while the assistant response is still streaming.

---

## 👍 RAG Learning & Retrieval Feedback Manager

The system incorporates a reinforcement feedback system to evaluate and improve RAG answer generation quality over time:
- **Interaction Data Logs**: Every user query and assistant response is logged as an interaction record inside `backend/data/query_dataset/`.
- **Feedback Collection Endpoint (`POST /api/dataset/feedback`)**: Users can submit positive (thumbs up) or negative (thumbs down) ratings for any assistant response. The rating updates the interaction record in the JSON store.
- **Analytics & Statistics (`GET /api/dataset/stats`)**: Computes real-time analytics including total query volume, total positive vs negative feedback count, and total disk size of the dataset.
- **Dataset Queries (`GET /api/dataset/queries`)**: Provides filtered access to recorded interactions, supporting date ranges, feedback type filters (all, positive, negative, unrated), and conversation ID scoping.
- **Data Export (`GET /api/dataset/export`)**: Allows administrators to export the filtered interaction database as a structured JSON payload for fine-tuning, training custom LLMs, or auditing RAG retrieval health.

---
*Created for AI RAG Developers, Contributors & Enterprise Teams.*


---

---

# 📂 Appendix: Complete File-by-File Purpose & Feature Responsibility Guide

> **Why this section exists:** Every file in this project was created for a specific reason. This section explains — file by file — *why* it was created, *what it is responsible for* inside the RAG pipeline, and *which end-user feature(s) it powers*. Read this before modifying any file, to understand downstream impact.

---

## 🏗️ Entry Points & Configuration

---

### `backend/main.py`
**Why created:** This is the FastAPI application factory — the single entry point for the entire backend.

**Responsibilities:**
- Creates the `FastAPI()` app instance with lifespan context
- Mounts CORS middleware (allows frontend on any origin to call the API)
- Mounts `StaticFiles` for serving the `frontend/` folder as a web server
- Registers all API routes from `backend/api/router.py`
- Serves specific HTML page routes: `/` → `index.html`, `/performance` → `performance.html`, etc.
- Defines the `/health` endpoint returning `{"status": "healthy"}`

**Features enabled:**
- The entire web application runs because of this file
- The browser can access `http://localhost:8000` and receive the frontend
- CORS allows the HTML/JS frontend to call `/api/*` endpoints without browser blocks

---

### `backend/lifespan.py`
**Why created:** FastAPI's lifespan system needed a dedicated place to run startup and shutdown logic without blocking request handling.

**Responsibilities:**
- On startup: Seeds default website URLs (LangChain, CrewAI, FastAPI docs) into SQLite
- Runs the **initial knowledge base scan** 2 seconds after startup (ingests any new files in `backend/data/`)
- Launches the **10-second background auto-sync watcher** (`auto_sync_watcher`) as an asyncio task
- Handles Windows-safe UTF-8 console output via `safe_print()`

**Features enabled:**
- Auto-sync: Drop a PDF into `backend/data/pdf/` → it gets embedded and indexed automatically within 10 seconds, without any manual action
- Default knowledge base population on first run

---

### `backend/settings.py`
**Why created:** All configuration (API keys, model names, database URLs, retrieval parameters) needed a single, typed, validated source of truth — not scattered `os.getenv()` calls across every file.

**Responsibilities:**
- Defines the `Settings` Pydantic model with all typed env vars
- Reads `.env` file via `python-dotenv` and maps to typed Python attributes
- Provides `settings.LLM_PROVIDER`, `settings.GEMINI_API_KEY`, `settings.DATABASE_URL`, `settings.CHUNK_SIZE`, etc.
- Exposes `settings.BACKEND_DIR` and `settings.BASE_DIR` as `Path` objects for consistent file resolution

**Features enabled:**
- Every service uses `from backend.settings import settings` → guaranteed typed config
- If a developer adds a new `.env` key, they add it here and get full type checking
- `GET /api/settings` reads from this object and `PUT /api/settings` writes back to `.env`

---

### `backend/dependencies.py`
**Why created:** FastAPI routes need shared singleton objects (database connections, LLM engines) that should NOT be re-instantiated per request.

**Responsibilities:**
- `get_memory()`: Thread-safe double-checked locking singleton for `MemoryService` (SQLite)
- `get_retrieval_service()`: Thread-safe singleton for `RetrievalEngine`
- `get_settings()`: LRU-cached settings instance
- `get_database()`: Yields a SQLAlchemy `Session` per request, closes after

**Features enabled:**
- SQLite is only opened once, not per API call — prevents database lock contention
- All FastAPI routes can do `memory = Depends(get_memory)` to get the shared instance
- Retrieval engine (which loads BAAI reranker model) is loaded once, not per query

---

## 🔌 API Layer

---

### `backend/api/router.py`
**Why created:** One central file to register all API sub-routers, preventing scattered `app.include_router()` calls across `main.py`.

**Responsibilities:**
- Imports every route module and adds it to the main `api_router`
- Applies tag names and prefixes (e.g., `prefix="/website"`, `tags=["Website Ingestion"]`)
- Provides a single import point: `main.py` only imports this one router

**Features enabled:**
- Adding a new API module only requires one line here
- Swagger UI (`/docs`) auto-discovers all routes from here

---

### `backend/api/routes/chat.py`
**Why created:** Handles the core conversation model — creating, reading, deleting, renaming chats, and running the full RAG pipeline on each message.

**Responsibilities:**
- `POST /api/chats` → creates new conversation in SQLite
- `GET /api/chats/{id}/messages` → loads chat history for display
- `POST /api/chats/{id}/messages` → **the main RAG pipeline endpoint** — runs classification, retrieval, generation, evaluation, persists everything
- `GET /api/history` → returns the 12-column `chat_history_records` analytics table
- `GET /api/history/csv` → streams analytics as a downloadable CSV file

**Features enabled:**
- Multi-turn conversation persistence
- The "Send" button in the UI calls this endpoint — it is the heart of the application
- Chat history analytics table (12-column view with search/filter)
- CSV export of all interactions

---

### `backend/api/routes/documents.py`
**Why created:** Handles all document ingestion entry points from the UI — file upload, URL, and paste.

**Responsibilities:**
- `POST /api/documents/upload` → accepts file(s), calls `IngestionEngine.ingest_file()`
- `GET /api/documents` → lists all indexed documents from SQLite
- `DELETE /api/documents/{id}` → removes document from Qdrant vectors AND SQLite registry
- `POST /api/paste` → ingests raw text content directly
- `POST /api/url` → ingests a webpage by URL

**Features enabled:**
- The upload panel in the UI (drag-drop + file picker)
- Delete button on the document list
- URL and paste ingestion modes
- Document count shown on the dashboard

---

### `backend/api/routes/search.py`
**Why created:** Provides free web search using DuckDuckGo HTML scraping — no API key required, no cost.

**Responsibilities:**
- `fetch_ddg_results()` → POST to DuckDuckGo HTML endpoint, regex-parse results (no DuckDuckGo API)
- `POST /api/search` → calls fetch, sends results to the active LLM for synthesis
- Handles the `SearchRequest` schema (query, model, chat_id)

**Features enabled:**
- When the query classifier detects `WEB_SEARCH` intent, this endpoint is called instead of the RAG pipeline
- "Searching the web..." step visible in the pipeline trace panel
- Real-time web answers for questions about current events, live data, etc.

---

### `backend/api/routes/settings.py`
**Why created:** The entire application's LLM configuration should be changeable at runtime from the UI, without restarting the server.

**Responsibilities:**
- `GET /api/settings` → reads all current settings (provider, model, keys, retrieval params, system prompt)
- `PUT /api/settings` → writes changes back to the `.env` file on disk AND updates the in-memory `settings` object
- Auto-infers the provider from the model name when updating

**Features enabled:**
- The Settings drawer in the UI (top-right gear icon)
- Switch from Ollama to Gemini mid-session without restart
- System prompt customization persisted across server restarts

---

### `backend/api/routes/website_ingestion.py`
**Why created:** Website crawling is a long-running background operation that needs its own CRUD API for tracking and management.

**Responsibilities:**
- `POST /api/website` → starts background crawl thread, creates `crawled_websites` record
- `GET /api/website` → lists all crawled websites with status
- `GET /api/website/{id}/status` → progress stats (pages discovered, chunks created, embeddings)
- `DELETE /api/website/{id}` → removes website, deletes its JSON backup file, removes Qdrant vectors
- `POST /api/website/{id}/crawl` → restarts a crawl

**Features enabled:**
- The Website Crawler page (`/website`) in the UI
- "Crawl Status" progress cards per website
- Knowledge base from entire documentation websites (LangChain docs, FastAPI docs, etc.)

---

### `backend/api/routes/performance.py`
**Why created:** Provides aggregated performance metrics that the dashboard needs — pulled from both Qdrant and SQLite.

**Responsibilities:**
- Queries SQLite `documents` table for file list
- Queries Qdrant `knowledge_base` collection for total chunk/point count
- Calls `memory.get_eval_stats()` for historical RAG evaluation averages
- Returns combined JSON: `{total_chunks, total_files, documents, historical, current}`

**Features enabled:**
- Performance Dashboard (`/performance`) — total chunks, document count, eval history charts

---

### `backend/api/routes/governance.py`
**Why created:** Enterprise systems need immutable audit trails to track who did what to which resource.

**Responsibilities:**
- `POST /api/governance/audit` → creates timestamped audit log record
- `GET /api/governance/audit` → returns all audit logs
- `GET /api/governance/audit/{resource_type}/{resource_id}` → filtered logs for one resource

**Features enabled:**
- Audit log viewer in the UI
- Compliance traceability (who deleted a document, who changed settings)
- Foundation for regulatory compliance requirements

---

### `backend/api/routes/jobs.py`
**Why created:** Long-running operations (bulk crawls, re-indexing) need to be trackable without blocking the HTTP response.

**Responsibilities:**
- `POST /api/jobs/{job_type}` → creates a job record with PENDING status
- `GET /api/jobs/{job_id}` → returns current status, progress %, message
- `PUT /api/jobs/{job_id}` → updates job progress (called by the async worker itself)

**Features enabled:**
- Background job progress bars in the UI
- Non-blocking long operations (start crawl → get job_id → poll status)

---

## 🧠 LLM Provider Layer

---

### `backend/llm/factory.py`
**Why created:** The application supports 6 different LLM providers. Without a factory, every service would need `if/elif` provider logic duplicated everywhere.

**Responsibilities:**
- `LLMFactory.get_llm_by_model(model_name)` → detects provider from model name string patterns
- `LLMFactory.create(provider, model, api_key, temperature)` → instantiates the correct provider class
- Used by: `GenerationEngine`, `QueryRewriter`, `EvaluationService`, `ContextBuilder`

**Features enabled:**
- Switching from Gemini to GPT-4o only requires changing `.env` — no code changes
- Every feature that calls an LLM (chat, rewrite, evaluate, web search synthesis) routes through here

---

### `backend/llm/providers/base.py`
**Why created:** All LLM providers must implement the same interface (`chat(messages) -> str`) so they're interchangeable.

**Responsibilities:**
- Defines abstract `BaseLLMProvider` with `async def chat(messages: list) -> str`
- All 6 provider files extend this class

**Features enabled:**
- Provider-agnostic code everywhere else — `llm.chat(messages)` works regardless of provider

---

### `backend/llm/providers/ollama.py`
**Why created:** Enables completely free, offline, local LLM inference — no API key, no cost, no internet.

**Responsibilities:**
- Connects to locally running Ollama server (`http://localhost:11434`)
- Sends chat messages to `ollama.AsyncClient().chat()`
- Supports any model installed via `ollama pull` (llama3, mistral, phi3, etc.)

**Features enabled:**
- Zero-cost local RAG with no cloud dependency
- Privacy-preserving — documents and queries never leave the machine

---

### `backend/llm/providers/gemini.py`
**Why created:** Google Gemini is the most cost-effective cloud LLM with a generous free tier (Flash model).

**Responsibilities:**
- Uses `google.genai` SDK (new GenAI client)
- Builds `Contents` objects from message history
- Calls `client.models.generate_content()`
- Also provides Gemini embeddings via `text-embedding-004`

**Features enabled:**
- `gemini-2.5-flash` as the recommended default cloud model
- Gemini-powered embedding generation as an alternative to Ollama

---

### `backend/llm/providers/groq.py`
**Why created:** Groq provides the fastest inference speeds for open-source models at free-tier pricing.

**Responsibilities:**
- Uses OpenAI-compatible Groq API client (`groq` SDK)
- Sends messages to `llama-3.3-70b-versatile` (or other Groq-hosted models)

**Features enabled:**
- Ultra-fast responses (100+ tokens/second)
- Free-tier access to LLaMA 3.3 70B quality without paying OpenAI prices

---

### `backend/llm/prompts.py`
**Why created:** System prompts for the RAG assistant need to be consistent, centrally maintained, and not scattered across individual files.

**Responsibilities:**
- Stores the base RAG system prompt (instructs LLM to only answer from context)
- Used by `PromptBuilder` when assembling the final messages array
- Customizable via `PUT /api/settings` (user can override the system prompt)

**Features enabled:**
- Consistent assistant persona across all conversations
- The "System Prompt" field in the Settings drawer

---

## 💾 Memory & Database Layer

---

### `backend/memory/memory_service.py`
**Why created:** The application needs a fast, embedded database for chat state that doesn't require PostgreSQL infrastructure to run locally.

**Responsibilities:**
- Creates and manages all SQLite tables: `conversations`, `messages`, `documents`, `rag_evaluation`, `chat_history_records`
- Runs schema migrations on startup (adds new columns backward-compatibly)
- Provides CRUD methods: `create_conversation()`, `add_message()`, `list_documents()`, `add_chat_history_record()`, `get_eval_stats()`
- WAL mode enabled: `PRAGMA journal_mode=WAL` — allows reads while writes are happening

**Features enabled:**
- All conversation persistence (sidebar history, message reload on refresh)
- The 12-column analytics table (`chat_history_records`)
- RAG evaluation score history charts on the performance dashboard
- Document registry for the "Documents" panel

---

### `backend/database/base.py`
**Why created:** SQLAlchemy 2.0 requires a `DeclarativeBase` that all ORM models inherit from.

**Responsibilities:**
- Defines `Base = DeclarativeBase()` — the parent class for all ORM models
- Imported by every model file in `backend/database/models/`

**Features enabled:**
- `Base.metadata.create_all(engine)` creates all PostgreSQL/SQLite tables on startup
- Alembic migration tool uses `Base.metadata` to auto-detect schema changes

---

### `backend/database/database.py`
**Why created:** The database engine (connection pool) should be created once and reused, not created per request.

**Responsibilities:**
- Reads `DATABASE_URL` from settings
- Creates `engine = create_engine(DATABASE_URL, ...)` with appropriate pool settings
- For SQLite: adds `check_same_thread=False` (required for async use)
- Calls `Base.metadata.create_all(engine)` to auto-create all ORM tables on startup

**Features enabled:**
- PostgreSQL or SQLite support with zero code changes — just change `DATABASE_URL` in `.env`
- All ORM tables (documents, chunks, knowledge_assets, etc.) created automatically on first run

---

### `backend/database/session.py`
**Why created:** FastAPI dependency injection needs a function that yields a database session and closes it properly after each request.

**Responsibilities:**
- Creates `SessionLocal = sessionmaker(bind=engine, ...)` — a session factory
- `get_db()` generator: opens a session, yields it to the route, closes it in `finally`
- Used as `db: Session = Depends(get_database)` in route files

**Features enabled:**
- Every API route that touches PostgreSQL/SQLite gets a fresh, properly closed session
- Prevents connection leaks — session always closes even if an exception occurs

---

## 📊 Database Models (SQLAlchemy ORM → PostgreSQL / SQLite)

---

### `backend/database/models/document_model.py`
**Why created:** The system needs a relational registry of all ingested documents — separate from SQLite's simpler `documents` table — with richer metadata and FK relationships.

**Responsibilities:**
- Maps to `documents` table (PostgreSQL or SQLite via DATABASE_URL)
- Columns: `id`, `name`, `file_type`, `file_size`, `file_path`, `source_type`, `status`, `created_at`
- Has a one-to-many relationship with `ChunkModel`

**Data flowing in:** Every time a file is uploaded, pasted, or URL-ingested via `DocumentSQLRepository.create()`

**Features enabled:**
- Knowledge Catalog document listing
- Document management (list, delete, filter by type)
- PGAdmin: inspect the `documents` table to see all indexed files

---

### `backend/database/models/chunk_model.py`
**Why created:** Individual text chunks need to be persisted relationally (linked to their parent document) for traceability and catalog browsing.

**Responsibilities:**
- Maps to `chunks` table
- Columns: `chunk_id`, `document_id` (FK → documents.id), `chunk_index`, `content`, `metadata_json`, `created_at`
- `chunk_index` preserves original document ordering

**Data flowing in:** `ChunkSQLRepository.create_many()` called during every ingestion, after `DocumentChunker` splits the document

**Features enabled:**
- Chunk-level catalog browsing in the UI
- Tracing which exact text chunk answered a user's question
- PGAdmin: inspect `chunks` table to see all stored text segments per document

---

### `backend/database/models/knowledge_asset.py` (catalog)
**Why created:** A higher-level catalog layer above raw documents, providing status tracking (pending/indexed/failed) and source type classification.

**Responsibilities:**
- Maps to `knowledge_assets` table
- Columns: `id`, `name`, `description`, `source_type` (FILE/URL/WEBSITE/PASTE), `status`, `asset_metadata`, `created_at`
- Created/updated by `CatalogSyncService` after each successful ingestion

**Data flowing in:** `catalog_sync_service.py` creates one `knowledge_asset` record per ingested document

**Features enabled:**
- Knowledge Catalog page — shows all assets with their source type and status
- Filtering assets by source (uploaded files vs crawled websites vs pasted content)
- PGAdmin: inspect `knowledge_assets` for a business-level view of what's in the knowledge base

---

### `backend/database/models/ingestion_history.py`
**Why created:** Enterprise systems need an immutable audit trail of every ingestion event — what was ingested, when, and whether it succeeded or failed.

**Responsibilities:**
- Maps to `ingestion_history` table
- Columns: `id`, `document_name`, `source_type`, `status` (SUCCESS/FAILED), `chunks_created`, `error_message`, `created_at`

**Data flowing in:** `IngestionHistorySQLRepository.create()` called at the end of every `IngestionService` run

**Features enabled:**
- Ingestion Audit Trail page in the UI
- Debugging failed ingestions (error_message column shows exactly what failed)
- PGAdmin: inspect `ingestion_history` to audit all document processing events

---

### `backend/database/models/website_ingestion.py`
**Why created:** Website crawl jobs are stateful (they can be running, completed, or failed) and need their state persisted across server restarts.

**Responsibilities:**
- Maps to `crawled_websites` table
- Columns: `id`, `url`, `website_name`, `status`, `discovered_pages_count`, `processed_pages_count`, `failed_pages_count`, `total_chunks`, `total_embeddings`, `json_backup_path`, `created_at`, `updated_at`

**Data flowing in:** `website_ingestion.py` route creates record; `WebsiteCrawlerService` updates it during crawl

**Features enabled:**
- Website crawler management page (`/website`)
- Status cards showing crawl progress in real-time
- PGAdmin: inspect `crawled_websites` to see crawl history and outcomes

---

### `backend/database/models/evaluation_model.py`
**Why created:** Structured evaluation results (beyond simple SQLite metrics) need a proper relational home for querying and reporting.

**Responsibilities:**
- Maps to `evaluations` table
- Columns: `id`, `query`, `response`, `context_relevance`, `faithfulness`, `answer_relevance`, `confidence`, `latency_ms`, `model_used`, `created_at`

**Data flowing in:** `EvaluationSQLRepository.create()` called after `calculate_rag_metrics()` returns scores

**Features enabled:**
- Evaluation results page in the UI
- Historical evaluation trend charts on the performance dashboard
- PGAdmin: inspect `evaluations` to analyze RAG quality over time

---

## 🔍 Retrieval Services (Why Each File Exists)

---

### `backend/services/retrieval/dense_retriever.py`
**Why created:** Semantic search based on meaning (not keywords) requires embedding-based similarity search — which is what dense retrieval provides.

**Responsibilities:**
- Converts the (rewritten) query into a 768-dim embedding via `EmbeddingService`
- Calls `QdrantService.search(query_vector, top_k)` to find cosine-similar chunks
- Returns `RetrievalResponse` with ranked `Document` objects

**Features enabled:**
- Finding conceptually related chunks even when exact keywords don't match
- "What is the refund policy?" finds chunks about "returns and money-back" without those exact words

---

### `backend/services/retrieval/sparse_retriever.py`
**Why created:** Dense retrieval misses exact keyword matches (e.g., product codes, names, technical terms). BM25 (sparse retrieval) fills this gap.

**Responsibilities:**
- Maintains an in-memory `BM25Okapi` corpus built from all indexed chunks
- `retrieve(request)` → scores all chunks by BM25 keyword relevance
- Returns top-K BM25-ranked documents

**Features enabled:**
- Exact keyword matching: "Find document with code ABC-123" → BM25 finds it even if embedding similarity is low
- Combined with dense retrieval via RRF fusion for best-of-both-worlds results

---

### `backend/services/retrieval/score_fusion.py`
**Why created:** Dense and sparse retrieval each produce separate ranked lists. They need to be merged intelligently without bias toward either.

**Responsibilities:**
- Implements **Reciprocal Rank Fusion (RRF)**: score = Σ (1 / (k + rank_i)) for each result list
- `fuse(dense_docs, sparse_docs)` → combined, deduplicated, re-ranked list
- RRF constant `k=60` prevents top-1 results from dominating too heavily

**Features enabled:**
- Hybrid retrieval mode — the default strategy that outperforms either dense or sparse alone
- "Hybrid Strategy" label visible in the pipeline trace panel

---

### `backend/services/retrieval/query_rewriter.py`
**Why created:** Raw user queries are often ambiguous, too short, or use informal language. Rewriting them improves retrieval precision significantly.

**Responsibilities:**
- Sends user query to active LLM with a rewrite prompt: "Expand abbreviations, remove filler words, preserve intent"
- Returns cleaned, precise query used for actual vector search
- Falls back to original query if LLM is unavailable

**Features enabled:**
- "Query Rewritten" step in the RAG pipeline trace
- Better retrieval even for vague queries like "how do I set this up?" → "step-by-step setup instructions for initial configuration"

---

### `backend/services/retrieval/reranker.py`
**Why created:** Vector similarity search is approximate — top-K results are not always the most relevant. Cross-encoder reranking scores each chunk against the full query for precision.

**Responsibilities:**
- Loads `BAAI/bge-reranker-base` via `sentence_transformers.CrossEncoder`
- For each (query, chunk) pair: computes a relevance score using the full transformer cross-attention
- Re-sorts chunks by cross-encoder score
- Caps final output at `top_k` (default 3) to control LLM token cost

**Features enabled:**
- Much more precise final context — the LLM receives only the most relevant chunks
- "Reranked to top-3 chunks" step in the pipeline trace
- Reduces hallucination by ensuring context is tightly relevant

---

### `backend/services/retrieval/context_builder.py`
**Why created:** Raw chunk text needs to be formatted into a readable context string that the LLM can understand and reference.

**Responsibilities:**
- Takes reranked `Document` list and formats each chunk with source labels
- Produces a single `context` string like: `[Source: document.pdf]\nChunk content...\n---\n`
- Used by `ContextCompressor` to trim if too long

**Features enabled:**
- The "Context Card" shown in the pipeline trace panel ("The LLM receives:")
- Source attribution in assistant responses

---

### `backend/services/retrieval/source_grounding.py`
**Why created:** Users need to know which documents and pages were used to generate an answer — for trust, verification, and compliance.

**Responsibilities:**
- Takes the final reranked `Document` list
- Extracts: source filename, chunk index, relevance score, page number if available
- Returns a `sources` list attached to the `RetrievalResponse`

**Features enabled:**
- Citation cards shown below each assistant response bubble
- "Sources: document.pdf (chunk 3, score: 0.87)" in the UI

---

### `backend/services/retrieval/strategies/hybrid_strategy.py`
**Why created:** The full 7-step retrieval pipeline (rewrite → dense → sparse → fuse → filter → rerank → build context) needs to be orchestrated in a single, testable class.

**Responsibilities:**
- Instantiates all sub-retrievers: `QueryRewriter`, `DenseRetriever`, `SparseRetriever`, `ScoreFusion`, `MetadataFilter`, `Reranker`, `ContextBuilder`, `SourceGrounding`
- Calls each step in sequence, recording timing metrics at each stage
- Returns `(RetrievalResponse, context_string)` tuple

**Features enabled:**
- The default RAG pipeline — called for every `DOCUMENT_QUESTION`, `COMPANY_KNOWLEDGE`, `TECHNICAL_KNOWLEDGE` query
- Per-step latency metrics (query_rewrite_ms, dense_retrieval_ms, reranking_ms, etc.) shown in trace panel

---

### `backend/services/retrieval/strategies/multi_query_strategy.py`
**Why created:** A single rewritten query may still miss relevant chunks. Generating multiple query variants covers more semantic territory.

**Responsibilities:**
- Uses `QueryRewriter.generate_search_queries()` to produce 5 semantically different query variants
- Runs dense retrieval in parallel for all 5 variants
- Merges and deduplicates results, applies reranking on the combined pool

**Features enabled:**
- `RETRIEVAL_STRATEGY=multi_query` in `.env` (the default setting)
- Better recall for complex questions with multiple sub-aspects

---

### `backend/services/retrieval/strategies/hyde_strategy.py`
**Why created:** For highly abstract or conceptual questions, generating a hypothetical answer first and then searching for similar real chunks can outperform direct query search.

**Responsibilities:**
- Sends query to LLM: "Write a short document that would answer this question"
- Embeds the hypothetical document text (not the query itself)
- Performs dense search with the hypothetical document embedding
- Finds chunks that are semantically similar to "what the answer should look like"

**Features enabled:**
- `RETRIEVAL_STRATEGY=hyde` in `.env`
- Improved retrieval for abstract/theoretical questions

---

## 📥 Ingestion Services (Why Each File Exists)

---

### `backend/services/ingestion_service.py`
**Why created:** The ingestion pipeline has 5 distinct steps (extract → chunk → embed → vectorize → register) that must be coordinated for 4 different input sources (upload, URL, paste, local file).

**Responsibilities:**
- `ingest_upload(file, memory)` → handles `UploadFile` from HTTP
- `ingest_url(url, memory)` → calls `WebLoader`, then full pipeline
- `ingest_pasted_content(title, content, memory)` → treats paste as a text document
- `ingest_local_file(path, memory)` → auto-sync path (called by `KnowledgeBaseLoader`)
- Orchestrates: `DocumentExtractor` → `DocumentChunker` → `EmbeddingService` → `VectorStoreFactory` → `MemoryService` → `CatalogSyncService`

**Features enabled:**
- Every ingestion entry point in the UI (upload, URL, paste)
- Auto-sync of files dropped into `backend/data/`

---

### `backend/services/ingestion/loader_factory.py`
**Why created:** 8 different file formats each need a different extraction library. A factory pattern avoids if/elif chains across the codebase.

**Responsibilities:**
- `LoaderFactory.get_loader(file_extension)` → returns the correct loader instance
- Mapping: `.pdf` → `PdfLoader`, `.docx` → `DocxLoader`, `.xlsx` → `ExcelLoader`, etc.
- Raises `UnsupportedFormatError` for unknown extensions

**Features enabled:**
- Universal file support — adding a new format only requires one new loader class + one mapping line here
- All 8 supported formats (PDF, DOCX, XLSX, CSV, PPTX, TXT, images, URL) work through this factory

---

### `backend/services/ingestion/pdf_loader.py`
**Why created:** PDF is the most common document format in enterprise settings. PyPDF provides page-by-page extraction without heavy dependencies.

**Responsibilities:**
- Opens PDF with `PdfReader`
- Extracts text from every page
- Returns combined text string with page separator markers
- Preserves page number metadata for citations

**Features enabled:**
- PDF upload → text extracted → chunked → embedded → searchable in RAG
- "page 3" citation accuracy in responses

---

### `backend/services/ingestion/image_loader.py`
**Why created:** Many enterprise documents arrive as screenshots, scanned PDFs rendered as images, or photo captures of physical documents. OCR is the only way to extract text from these.

**Responsibilities:**
- Primary OCR: `EasyOCR` (neural network based — handles handwriting, complex layouts)
- Secondary OCR: `pytesseract` (Tesseract-based, fast for clean printed text)
- Pre-processing: `OpenCV CLAHE` (Contrast Limited Adaptive Histogram Equalization) to enhance low-contrast images before OCR
- Resizes very large images for performance

**Features enabled:**
- Screenshot attachments in the chat → text extracted and used as context
- Image files in `backend/data/images/` → auto-synced and made searchable
- "Visual Analysis" query classification handles image-heavy queries

---

### `backend/services/ingestion/web_loader.py`
**Why created:** URL ingestion needs HTML-aware extraction that removes navigation, ads, footers, and scripts — keeping only meaningful content text.

**Responsibilities:**
- `requests.get(url)` with browser User-Agent header (avoids bot blocking)
- `BeautifulSoup` strips: `<script>`, `<style>`, `<nav>`, `<footer>`, `<header>`, `<iframe>`
- Returns clean text body of the webpage

**Features enabled:**
- `POST /api/url` — ingest any public URL into the knowledge base
- Web search result synthesis (used in search route)
- Website crawler content extraction

---

### `backend/services/document_chunker.py`
**Why created:** Large documents can't be sent to embedding models or LLMs whole — they must be split into small, meaningful segments. The chunking strategy profoundly affects retrieval quality.

**Responsibilities:**
- `DocumentChunker.chunk(text, strategy)` → delegates to `ChunkerFactory`
- `ChunkerFactory.create(strategy)` → returns `RecursiveChunker`, `SemanticChunker`, `TokenChunker`, or `SentenceSplitter`
- Default: `RecursiveChunker` with `size=2000`, `overlap=400`
- `ChunkValidator` checks minimum chunk length (rejects empty/trivial chunks)

**Features enabled:**
- The "Chunking" step in the ingestion pipeline
- `CHUNK_SIZE` and `CHUNK_OVERLAP` settings in the Settings drawer
- Chunk size directly affects: retrieval precision, LLM context quality, token cost

---

### `backend/services/chunking/recursive_chunker.py`
**Why created:** The default chunking strategy — splits on paragraph breaks, then sentence breaks, then character breaks — preserving the most natural text boundaries possible.

**Responsibilities:**
- Uses LangChain's `RecursiveCharacterTextSplitter`
- Tries to split on `\n\n` first, then `\n`, then `. `, then ` `, then character-by-character
- Maintains `overlap` characters between consecutive chunks so context isn't lost at boundaries

**Features enabled:**
- The primary chunking strategy for all file types
- Overlap ensures a sentence that spans two chunks isn't lost from retrieval

---

### `backend/services/chunking/semantic_chunker.py`
**Why created:** Recursive splitting can cut across concept boundaries. Semantic chunking splits at points where the *meaning* changes, not just the character count.

**Responsibilities:**
- Generates embeddings for each sentence
- Finds points where cosine similarity between consecutive sentences drops sharply (topic changes)
- Splits at these low-similarity boundaries

**Features enabled:**
- Better chunk coherence for long, complex documents
- Activated via `CHUNKING_STRATEGY=semantic` in `.env`

---

### `backend/services/embedding_service.py`
**Why created:** Three different embedding providers (Ollama, OpenAI, Gemini) need a unified interface, with automatic fallback.

**Responsibilities:**
- `generate_embeddings(texts)` → calls the configured embedding provider
- Provider priority: Ollama (if running) → OpenAI (if key set) → Gemini (if key set) → SHA-256 fallback
- Returns `list[list[float]]` — a list of 768-dim embedding vectors
- SHA-256 fallback: generates deterministic 768-dim vector from text hash (enables testing without any embedding service)

**Features enabled:**
- Every document ingestion generates embeddings for vector search
- Every query during retrieval generates a query embedding for similarity search
- The system still works (degraded quality) even if Ollama isn't running and no API keys are set

---

### `backend/services/knowledge_base_loader.py`
**Why created:** Developers and users should be able to add documents to the knowledge base by simply dropping files into a folder — without using the UI upload feature.

**Responsibilities:**
- `discover_files()` → recursively scans `backend/data/` for all supported file extensions
- Skips `.db`, `.db-wal`, `.db-shm` files and `processed/` directories
- `sync_knowledge_base(memory)` → compares discovered files against SQLite `documents` table → ingests only new files
- Called on startup AND every 10 seconds by `auto_sync_watcher` in `lifespan.py`

**Features enabled:**
- **Drop-to-index**: Place any supported file in `backend/data/` → it's auto-indexed within 10 seconds
- Startup population: pre-loaded knowledge bases work out of the box
- De-duplication: files are never ingested twice (checked by path AND filename)

---

### `backend/services/website_crawler_service.py`
**Why created:** Crawling an entire website involves many steps (robots.txt, sitemap, recursive page discovery, HTML cleaning, rate limiting) that need a dedicated, stateful service.

**Responsibilities:**
- `start_crawl(url, website_id, db)` → launches background `threading.Thread` (not async, to avoid blocking event loop)
- Step 1: Fetches and respects `robots.txt`
- Step 2: Discovers `sitemap.xml` → parses all `<loc>` URLs
- Step 3: If no sitemap, recursive link-following (max 50 pages, depth 3)
- Step 4: Per-page `WebLoader` extraction (strips nav/footer/scripts)
- Step 5: Rate limiting with `time.sleep()` between requests
- Step 6: Generates structured JSON array → saves to `backend/data/json/{name}.json`
- Step 7: Chunks + embeds + indexes into Qdrant
- Step 8: Updates `crawled_websites` DB record with final counts

**Features enabled:**
- The Website Crawler page (`/website`) — submit any URL and it crawls the whole site
- LangChain/FastAPI docs as a default knowledge source
- JSON backups allow re-indexing without re-crawling

---

## 📊 Evaluation & Generation Services

---

### `backend/services/evaluation_service.py`
**Why created:** RAG quality cannot be assumed — it must be measured automatically on every response so developers can monitor degradation over time.

**Responsibilities:**
- `calculate_rag_metrics(query, context, response, model, api_key)` → computes all evaluation scores
- **Word-overlap method** (always available, no LLM needed): Jaccard-style token overlap between query/context/response
- **LLM judge method** (cloud models only): Sends structured eval prompt to LLM, parses JSON score `{"context_relevance": 85, "faithfulness": 92, ...}`
- Writes results to `rag_evaluation` SQLite table AND `evaluations` PostgreSQL table
- Returns `metrics` dict attached to every message response

**Features enabled:**
- Metrics card on every assistant bubble (Correctness %, Faithfulness %, Confidence %, etc.)
- Historical evaluation charts on the performance dashboard
- Automated quality monitoring — no human evaluation needed per query

---

### `backend/services/generation/prompt_builder.py`
**Why created:** The LLM prompt structure (system instructions + context + conversation history + user query) is complex and must be assembled identically every time.

**Responsibilities:**
- Assembles the `messages` array sent to any LLM provider
- Format: `[{role: system, content: system_prompt}, ...history_messages..., {role: user, content: query_with_context}]`
- Injects the retrieved `context` string into the user message
- Respects conversation history length limits (trims old messages to stay within token budget)

**Features enabled:**
- Consistent RAG prompt structure regardless of which LLM is active
- Conversation memory — the LLM sees previous turns, enabling follow-up questions

---

### `backend/services/generation/citation_manager.py`
**Why created:** After the LLM generates a response, source citations need to be formatted and appended in a consistent, readable way.

**Responsibilities:**
- Takes the `sources` list from `SourceGroundingService`
- Formats each source: filename, chunk index, relevance score
- Appends citation block to the assistant response

**Features enabled:**
- "Sources:" section below each assistant response
- Verifiability — users can see exactly which documents were used

---

### `backend/services/generation/guardrails.py`
**Why created:** The system needs a basic safety layer to detect and refuse unsafe, harmful, or out-of-scope queries.

**Responsibilities:**
- Checks query against known unsafe patterns (violence, illegal requests, etc.)
- Returns `is_safe: bool` + optional refusal message
- Works without LLM — pure rule-based checks

**Features enabled:**
- `UNSAFE_REQUEST` query classification branch (bypasses RAG, returns refusal)
- Basic content safety without requiring a separate moderation API

---

## 🗄️ PostgreSQL / PGAdmin Data Flow Guide

---

### How PostgreSQL Connects

```
.env: DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/rag_db
          |
          v
backend/database/database.py
  -> create_engine(DATABASE_URL)
  -> engine = SQLAlchemy Engine (connection pool)
  -> Base.metadata.create_all(engine)   <- creates all tables on first run
          |
          v
backend/database/session.py
  -> SessionLocal = sessionmaker(bind=engine)
  -> get_db() -> yields Session -> used by API routes
```

### PostgreSQL Tables and What Populates Them

| PostgreSQL Table | Populated By | When | PGAdmin Query to Inspect |
|---|---|---|---|
| `documents` | `DocumentSQLRepository.create()` | Every file upload, URL, paste, auto-sync | `SELECT * FROM documents ORDER BY created_at DESC;` |
| `chunks` | `ChunkSQLRepository.create_many()` | After every document is chunked | `SELECT * FROM chunks WHERE document_id='<id>' ORDER BY chunk_index;` |
| `knowledge_assets` | `CatalogSyncService.sync()` | After every successful ingestion | `SELECT name, source_type, status FROM knowledge_assets;` |
| `ingestion_history` | `IngestionHistorySQLRepository.create()` | After every ingestion attempt (success or fail) | `SELECT document_name, status, error_message FROM ingestion_history ORDER BY created_at DESC;` |
| `crawled_websites` | `website_ingestion.py` route + `WebsiteCrawlerService` | On website submit and during crawl | `SELECT url, status, processed_pages_count, total_chunks FROM crawled_websites;` |
| `evaluations` | `EvaluationSQLRepository.create()` | After every RAG query evaluation | `SELECT query, context_relevance, faithfulness, answer_relevance FROM evaluations ORDER BY created_at DESC;` |
| `knowledge_reviews` | `KnowledgeReviewService` | When admin submits for review | `SELECT * FROM knowledge_reviews WHERE status='pending';` |
| `recommendations` | `RecommendationService` | AI-generated improvement suggestions | `SELECT * FROM recommendations ORDER BY created_at DESC;` |

### Setting Up PGAdmin to Inspect the Database

1. **Install PGAdmin** from [pgadmin.org](https://www.pgadmin.org/download/)
2. **Register a Server** in PGAdmin:
   - Right-click `Servers` → `Register` → `Server`
   - Name: `RAG Database`
   - Connection: Host `localhost`, Port `5432`, Database `rag_db`, Username `postgres`, Password `YourPassword`
3. **Navigate to Tables**:
   - Expand: `Servers` → `RAG Database` → `Databases` → `rag_db` → `Schemas` → `public` → `Tables`
4. **Query Tool**: Right-click any table → `View/Edit Data` → `All Rows`
5. **Run Custom Queries**: Tools → `Query Tool` → paste SQL → Execute (F5)

### Useful PGAdmin SQL Queries for Debugging

```sql
-- See all indexed documents with their chunk counts
SELECT d.name, d.file_type, d.source_type, d.status, COUNT(c.chunk_id) as chunk_count
FROM documents d
LEFT JOIN chunks c ON d.id = c.document_id
GROUP BY d.id, d.name, d.file_type, d.source_type, d.status
ORDER BY d.created_at DESC;

-- See RAG evaluation quality over time
SELECT DATE(created_at) as date,
       AVG(context_relevance) as avg_context_relevance,
       AVG(faithfulness) as avg_faithfulness,
       AVG(answer_relevance) as avg_answer_relevance,
       COUNT(*) as query_count
FROM evaluations
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- See all crawled websites and their status
SELECT website_name, url, status, discovered_pages_count,
       processed_pages_count, failed_pages_count, total_chunks
FROM crawled_websites
ORDER BY created_at DESC;

-- See recent ingestion history (successes and failures)
SELECT document_name, source_type, status, chunks_created, error_message, created_at
FROM ingestion_history
ORDER BY created_at DESC
LIMIT 50;

-- Find documents with zero chunks (failed chunking)
SELECT d.name, d.file_type, d.created_at
FROM documents d
WHERE NOT EXISTS (
    SELECT 1 FROM chunks c WHERE c.document_id = d.id
);
```

### SQLite vs PostgreSQL: What Goes Where

| Data | Database | File/Table | Why |
|---|---|---|---|
| Chat conversations & messages | SQLite | `chat_history.db / conversations, messages` | Fast, embedded, no infra needed for chat |
| 12-column analytics records | SQLite | `chat_history.db / chat_history_records` | High-write analytics log |
| RAG evaluation scores (simple) | SQLite | `chat_history.db / rag_evaluation` | Quick reads for dashboard chart |
| Document registry (rich) | PostgreSQL | `documents` table | Relational FK to chunks, enterprise-grade |
| Text chunks | PostgreSQL | `chunks` table | FK to documents, browsable catalog |
| Knowledge assets | PostgreSQL | `knowledge_assets` table | Business-level catalog with status tracking |
| Ingestion audit trail | PostgreSQL | `ingestion_history` table | Enterprise compliance requirement |
| Website crawl jobs | PostgreSQL | `crawled_websites` table | Stateful job with FK relationships |
| Evaluation results (rich) | PostgreSQL | `evaluations` table | Full schema with model tracking |
| Audit logs | PostgreSQL | (governance tables) | Immutable compliance records |

---

## 🎯 End-to-End Feature → File Responsibility Map

| User-Facing Feature | Files Responsible |
|---|---|
| **Send a chat message (RAG)** | `routes/chat.py` → `ingestion_service.py` (attach) → `retrieval/strategies/hybrid_strategy.py` → `generation/prompt_builder.py` → `llm/factory.py` → `evaluation_service.py` → `memory_service.py` |
| **Upload a PDF** | `routes/documents.py` → `ingestion_service.py` → `ingestion/pdf_loader.py` → `document_chunker.py` → `embedding_service.py` → `qdrant_service.py` → `document_sql_repository.py` → `catalog_sync_service.py` |
| **Search the web** | `routes/search.py` (fetch_ddg_results) → `llm/factory.py` → LLM synthesis |
| **Auto-index dropped file** | `lifespan.py` (watcher) → `knowledge_base_loader.py` → `ingestion_service.py` → full pipeline |
| **Crawl a website** | `routes/website_ingestion.py` → `website_crawler_service.py` → `web_loader.py` → `document_chunker.py` → `embedding_service.py` → `qdrant_service.py` |
| **Switch LLM provider** | `routes/settings.py` (PUT) → `settings.py` (.env write) → `llm/factory.py` (next request) |
| **View eval scores on bubble** | `evaluation_service.py` → `messages.metrics` (SQLite) → `routes/chat.py` (GET messages) → `assistant.js` (render) |
| **12-col analytics table** | `routes/chat.py` (GET /api/history) → `memory_service.chat_history_records` → `analytics.js` (render) |
| **Rerank results** | `retrieval/reranker.py` (BAAI/bge-reranker-base cross-encoder) |
| **Settings drawer** | `routes/settings.py` → `settings.py` → `js/pages/settings.js` + `js/components/config_drawer.js` |
| **Knowledge catalog** | `routes/document_catalog.py` → `database/models/knowledge_asset.py` → `catalog/services/asset_service.py` |
| **Audit log** | `routes/governance.py` → `services/governance/audit_service.py` → PostgreSQL governance tables |
| **Performance dashboard** | `routes/performance.py` → Qdrant (chunk count) + SQLite `rag_evaluation` + `documents` |

---

*This appendix is a living reference document. Update it whenever a new file is added or a file's responsibilities change.*
*AI Enterprise RAG Application v2.0 — Complete File Purpose Guide*


---

---

# 🏛️ Architecture Diagram & End-to-End Pipeline

---

## System Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║                              BROWSER / CLIENT LAYER                                      ║
║                                                                                          ║
║   ┌──────────────────────────────────────────────────────────────────────────────────┐   ║
║   │  index.html          performance.html       dataset.html       website.html      │   ║
║   │  (RAG Chat +         (KPI Dashboard +       (Query Logs +      (Web Crawler +    │   ║
║   │   Pipeline Trace)     Eval Charts)           Feedback)          Ingestion UI)    │   ║
║   └────────────────────────────┬─────────────────────────────────────────────────────┘   ║
║                                │                                                          ║
║   ┌────────────────────────────┴─────────────────────────────────────────────────────┐   ║
║   │                    MODULAR JS / CSS LAYER                                         │   ║
║   │  api.js  state.js  rbac.js  app.js                                               │   ║
║   │  components/: header  sidebar  config_drawer  modal  toast  charts  data_table   │   ║
║   │  pages/:     assistant  dashboard  upload  settings  analytics  catalog  audit    │   ║
║   │  css/:       variables  base  layout  components  pages                          │   ║
║   └──────────────────────────────────────────────────────────────────────────────────┘   ║
╚════════════════════════════════╤═════════════════════════════════════════════════════════╝
                                 │  HTTP REST / JSON  (port 8000)
                                 │
╔════════════════════════════════▼═════════════════════════════════════════════════════════╗
║                         FASTAPI BACKEND  (Python 3.12+ / Uvicorn)                        ║
║                      backend/main.py  ←──────────►  backend/lifespan.py                  ║
║                                                                                           ║
║  ┌─────────────────────────────────────────────────────────────────────────────────────┐ ║
║  │                          API ROUTER LAYER  (backend/api/router.py)                  │ ║
║  │                                                                                     │ ║
║  │  /api/chats      /api/documents    /api/search     /api/settings  /api/history     │ ║
║  │  /api/website    /api/dataset      /api/feedback   /api/review    /api/evaluation  │ ║
║  │  /api/governance /api/jobs         /api/versioning /api/catalog   /api/performance │ ║
║  │  /api/database   /api/export       /api/ingestion-history         /api/health      │ ║
║  └───────────┬───────────────────────────┬───────────────────┬───────────────────────┘ ║
║              │                           │                   │                           ║
║  ┌───────────▼──────────┐   ┌────────────▼───────────┐   ┌──▼────────────────────────┐ ║
║  │   LLM FACTORY LAYER  │   │   RAG PIPELINE LAYER   │   │   GOVERNANCE LAYER        │ ║
║  │   backend/llm/       │   │   backend/services/    │   │                           │ ║
║  │                      │   │                        │   │   Audit Service           │ ║
║  │  LLMFactory          │   │   IngestionService     │   │   RBAC Service            │ ║
║  │   ├─ OllamaProvider  │   │   RetrievalService     │   │   Approval Service        │ ║
║  │   ├─ OpenAIProvider  │   │   GenerationService    │   │   JobService              │ ║
║  │   ├─ GeminiProvider  │   │   EvaluationService    │   │   VersionService          │ ║
║  │   ├─ ClaudeProvider  │   │   EmbeddingService     │   │   ReviewService           │ ║
║  │   ├─ GroqProvider    │   │   ChunkingService      │   │   RecommendService        │ ║
║  │   └─ GrokProvider    │   │   DatasetService       │   │   CatalogSyncService      │ ║
║  └──────────────────────┘   └───────────┬────────────┘   └───────────────────────────┘ ║
║                                         │                                                 ║
╚═════════════════════════════════════════│═════════════════════════════════════════════════╝
                                          │
              ┌───────────────────────────┼────────────────────────────────┐
              │                           │                                │
╔═════════════▼═════════════╗ ╔═══════════▼═══════════════════╗ ╔══════════▼═══════════════╗
║    VECTOR STORE LAYER     ║ ║    RELATIONAL DATABASE LAYER   ║ ║   EMBEDDING LAYER        ║
║                           ║ ║                                ║ ║                          ║
║  HybridService            ║ ║  SQLite (WAL Mode)             ║ ║  EmbeddingService        ║
║   ├─ QdrantService        ║ ║  (chat_history.db)             ║ ║   ├─ Ollama              ║
║   │   collection:         ║ ║   ├─ conversations             ║ ║   │   nomic-embed-text   ║
║   │   knowledge_base      ║ ║   ├─ messages (+ metrics)      ║ ║   │   768-dim            ║
║   │   768-dim cosine      ║ ║   ├─ documents                 ║ ║   ├─ OpenAI              ║
║   │   batch: 100 pts      ║ ║   ├─ rag_evaluation            ║ ║   │   text-embedding-3   ║
║   ├─ FAISSService         ║ ║   └─ chat_history_records      ║ ║   ├─ Gemini              ║
║   │   local index         ║ ║                                ║ ║   │   text-embedding-004 ║
║   └─ SparseRetriever      ║ ║  PostgreSQL (via SQLAlchemy)   ║ ║   └─ SHA-256 Fallback   ║
║       rank-bm25 BM25      ║ ║   ├─ documents                 ║ ║      (768-dim hash)      ║
║                           ║ ║   ├─ chunks                    ║ ╚══════════════════════════╝
║  Reranker                 ║ ║   ├─ knowledge_assets          ║
║   BAAI/bge-reranker-base  ║ ║   ├─ evaluations               ║ ╔══════════════════════════╗
║   Cross-Encoder           ║ ║   ├─ ingestion_history         ║ ║  LOCAL FILESYSTEM        ║
╚═══════════════════════════╝ ║   ├─ crawled_websites          ║ ║                          ║
                              ║   ├─ knowledge_reviews         ║ ║  backend/data/           ║
                              ║   ├─ recommendations           ║ ║   ├─ pdf/ docx/ xlsx/    ║
                              ║   └─ audit_logs                ║ ║   ├─ csv/ txt/ images/   ║
                              ╚════════════════════════════════╝ ║   ├─ json/ (web crawls)  ║
                                                                 ║   ├─ query_dataset/      ║
                                                                 ║   └─ database_files/     ║
                                                                 ║  backend/qdrant_db/      ║
                                                                 ╚══════════════════════════╝
```

---

## End-to-End RAG Pipeline Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│               COMPLETE END-TO-END RAG REQUEST → RESPONSE PIPELINE                       │
└─────────────────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────────┐
  │                     USER INPUT (Browser)                          │
  │   Text Prompt  +  Optional Attachments (images / PDF / DOCX)     │
  │   POST /api/chats/{id}/messages                                   │
  └───────────────────────────────┬──────────────────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │  STEP 1: ATTACHMENT        │
                    │  PRE-PROCESSING            │
                    │                            │
                    │  Image  → EasyOCR + CLAHE  │
                    │  PDF    → PyPDF decode     │
                    │  DOCX   → python-docx      │
                    │  XLSX   → openpyxl+pandas  │
                    │  Text   → pass-through     │
                    │                            │
                    │  Output: extracted_text    │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │  STEP 2: QUERY             │
                    │  CLASSIFICATION            │
                    │  classify_query()          │
                    │                            │
                    │  14 Intent Categories:     │
                    │  GREETING | SMALL_TALK     │
                    │  WEB_SEARCH | CODING       │
                    │  DOCUMENT_QUESTION         │
                    │  COMPANY_KNOWLEDGE         │
                    │  DATABASE_QUERY            │
                    │  VISUAL_ANALYSIS           │
                    │  ANALYTICS_REQUEST         │
                    │  UNSAFE_REQUEST ...        │
                    └─────────────┬─────────────┘
                                  │
           ┌──────────────────────┼────────────────────────┐
           │                      │                        │
           ▼                      ▼                        ▼
  ┌────────────────┐   ┌─────────────────────┐   ┌────────────────────┐
  │  GREETING /    │   │  WEB_SEARCH BRANCH  │   │  RAG BRANCH        │
  │  SMALL_TALK    │   │                     │   │  (continues below) │
  │                │   │  fetch_ddg_results()│   │                    │
  │  Direct LLM    │   │  DuckDuckGo HTML    │   │                    │
  │  call, no RAG  │   │  parse 6 results   │   │                    │
  │  Low latency   │   │       ↓            │   │                    │
  │       ↓        │   │  LLM synthesis     │   │                    │
  │  Response      │   │  from web snippets │   │                    │
  └────────────────┘   └─────────────────────┘   └────────────────────┘
                                                           │
                                           ┌───────────────▼───────────────┐
                                           │  STEP 3: QUERY REWRITING      │
                                           │                               │
                                           │  Strategy: MULTI_QUERY        │
                                           │  QueryRewriter.rewrite()      │
                                           │   → LLM expands, clarifies    │
                                           │   → removes filler words      │
                                           │                               │
                                           │  MultiQueryStrategy           │
                                           │   → generates 5 variants      │
                                           │   → parallel retrieval        │
                                           │                               │
                                           │  HyDE (optional)              │
                                           │   → generates hypothetical    │
                                           │     answer document           │
                                           └───────────────┬───────────────┘
                                                           │
                                           ┌───────────────▼───────────────┐
                                           │  STEP 4: HYBRID RETRIEVAL     │
                                           │                               │
                                           │  ┌─────────────────────────┐ │
                                           │  │ DENSE RETRIEVAL         │ │
                                           │  │ EmbeddingService        │ │
                                           │  │  → nomic-embed-text     │ │
                                           │  │  → 768-dim vector       │ │
                                           │  │ QdrantService.search()  │ │
                                           │  │  → cosine similarity    │ │
                                           │  │  → top-20 candidates    │ │
                                           │  └────────────┬────────────┘ │
                                           │               │              │
                                           │  ┌────────────▼────────────┐ │
                                           │  │ SPARSE RETRIEVAL        │ │
                                           │  │ SparseRetriever         │ │
                                           │  │  → rank-bm25 BM25       │ │
                                           │  │  → keyword matching     │ │
                                           │  │  → top-20 candidates    │ │
                                           │  └────────────┬────────────┘ │
                                           │               │              │
                                           │  ┌────────────▼────────────┐ │
                                           │  │ SCORE FUSION (RRF)      │ │
                                           │  │ ScoreFusion.fuse()      │ │
                                           │  │  → Reciprocal Rank      │ │
                                           │  │    Fusion (k=60)        │ │
                                           │  │  → deduplicate results  │ │
                                           │  │  → merged ranked list   │ │
                                           │  └────────────┬────────────┘ │
                                           │               │              │
                                           │  ┌────────────▼────────────┐ │
                                           │  │ METADATA FILTER         │ │
                                           │  │ MetadataFilter.filter() │ │
                                           │  │  → file/type/source     │ │
                                           │  │    filters applied      │ │
                                           │  └────────────┬────────────┘ │
                                           │               │              │
                                           │  ┌────────────▼────────────┐ │
                                           │  │ CROSS-ENCODER RERANKING │ │
                                           │  │ Reranker.rerank()       │ │
                                           │  │  BAAI/bge-reranker-base │ │
                                           │  │  → scores each (query,  │ │
                                           │  │    chunk) pair          │ │
                                           │  │  → sorts by relevance   │ │
                                           │  │  → returns top-K=3      │ │
                                           │  └────────────┬────────────┘ │
                                           └───────────────┼───────────────┘
                                                           │
                                           ┌───────────────▼───────────────┐
                                           │  STEP 5: CONTEXT ASSEMBLY     │
                                           │                               │
                                           │  ContextBuilder.build()       │
                                           │   → formats chunks with       │
                                           │     [Source: filename] labels │
                                           │                               │
                                           │  ContextCompressor            │
                                           │   → trims to token budget     │
                                           │                               │
                                           │  SourceGrounding.build()      │
                                           │   → extracts citation list    │
                                           │   → filename, chunk_idx,      │
                                           │     relevance score           │
                                           └───────────────┬───────────────┘
                                                           │
                                           ┌───────────────▼───────────────┐
                                           │  STEP 6: LLM GENERATION       │
                                           │                               │
                                           │  PromptBuilder.build()        │
                                           │   → system prompt             │
                                           │   + conversation history      │
                                           │   + retrieved context         │
                                           │   + user query                │
                                           │                               │
                                           │  GenerationEngine.generate()  │
                                           │   LLMFactory.get_llm()        │
                                           │   ┌───────────────────────┐   │
                                           │   │ Ollama / OpenAI /     │   │
                                           │   │ Gemini / Claude /     │   │
                                           │   │ Groq / Grok           │   │
                                           │   └───────────┬───────────┘   │
                                           │               │               │
                                           │  CitationManager.append()     │
                                           │   → appends sources to reply  │
                                           │                               │
                                           │  Guardrails.check()           │
                                           │   → safety content filter     │
                                           └───────────────┬───────────────┘
                                                           │
                                           ┌───────────────▼───────────────┐
                                           │  STEP 7: RAG EVALUATION       │
                                           │  calculate_rag_metrics()      │
                                           │                               │
                                           │  Word-overlap scoring:        │
                                           │  context_relevance            │
                                           │   = query ∩ context / query   │
                                           │  faithfulness                 │
                                           │   = response ∩ context        │
                                           │     / response                │
                                           │  answer_relevance             │
                                           │   = query ∩ response / query  │
                                           │  confidence                   │
                                           │   = weighted average          │
                                           │                               │
                                           │  Cloud LLM Judge (optional):  │
                                           │   → JSON score 0-100          │
                                           │   → overrides word-overlap    │
                                           └───────────────┬───────────────┘
                                                           │
                                           ┌───────────────▼───────────────┐
                                           │  STEP 8: PERSIST & RESPOND    │
                                           │                               │
                                           │  SQLite (memory_service):     │
                                           │   messages.metrics ← scores   │
                                           │   rag_evaluation ← latency    │
                                           │   chat_history_records ← all  │
                                           │                               │
                                           │  PostgreSQL (SQLAlchemy):     │
                                           │   evaluations ← full schema   │
                                           └───────────────┬───────────────┘
                                                           │
                                                           ▼
                    ┌──────────────────────────────────────────────────────┐
                    │               HTTP RESPONSE TO BROWSER               │
                    │                                                       │
                    │  {                                                    │
                    │    response: "LLM generated answer text...",         │
                    │    citations: [{source, chunk_idx, score}, ...],     │
                    │    metrics: {                                         │
                    │      correctness: 0.87,                              │
                    │      faithfulness: 0.92,                             │
                    │      groundedness: 0.84,                             │
                    │      confidence: 0.88,                               │
                    │      time_taken_s: 1.85,                             │
                    │      token_cost: "$0.0005"                           │
                    │    },                                                 │
                    │    pipeline_trace: [step1..step7]                    │
                    │  }                                                    │
                    └──────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════════════════
                   DOCUMENT INGESTION PIPELINE (Parallel / Background)
═══════════════════════════════════════════════════════════════════════════════════════════

  ┌──────────────────────────────────────────────────────────────────────┐
  │             INGESTION TRIGGER (one of 4 entry points)                │
  │                                                                       │
  │  A. Upload UI  →  POST /api/documents/upload  →  UploadFile          │
  │  B. URL Input  →  POST /api/url               →  webpage URL         │
  │  C. Paste      →  POST /api/paste             →  raw text content    │
  │  D. Auto-Sync  →  lifespan.py watcher (10s)  →  backend/data/ file  │
  └────────────────────────────────┬─────────────────────────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   IngestionEngine            │
                    │   (thin orchestrator facade) │
                    │   → delegates to             │
                    │     IngestionService         │
                    └──────────────┬──────────────┘
                                   │
          ┌───────────────┬────────┴──────────────┬───────────────┐
          ▼               ▼                        ▼               ▼
  ┌──────────────┐ ┌─────────────┐ ┌──────────────────┐ ┌────────────────┐
  │ STEP 1:      │ │ STEP 2:     │ │ STEP 3:          │ │ STEP 4:        │
  │ TEXT         │ │ CHUNKING    │ │ EMBEDDING        │ │ VECTOR STORE   │
  │ EXTRACTION   │ │             │ │                  │ │ INDEXING       │
  │              │ │ Chunker     │ │ EmbeddingService │ │                │
  │ LoaderFactory│ │ Factory:    │ │                  │ │ QdrantService  │
  │              │ │             │ │  Ollama:         │ │  add_documents │
  │ .pdf →       │ │ Recursive   │ │  nomic-embed-text│ │  100 pts/batch │
  │  PdfLoader   │ │ (default)   │ │  (768-dim)       │ │                │
  │ .docx →      │ │ size=2000   │ │                  │ │ FAISSService   │
  │  DocxLoader  │ │ overlap=400 │ │  OpenAI:         │ │  update index  │
  │ .xlsx →      │ │             │ │  text-embedding  │ │                │
  │  ExcelLoader │ │ Semantic    │ │  -3-small/large  │ │ SparseRetriever│
  │ .csv  →      │ │ embedding   │ │                  │ │  BM25 corpus   │
  │  CsvLoader   │ │ based split │ │  Gemini:         │ │  update        │
  │ .pptx →      │ │             │ │  text-embedding  │ │                │
  │  MdLoader    │ │ Token       │ │  -004            │ └────────────────┘
  │ .txt  →      │ │ token-aware │ │                  │
  │  TextLoader  │ │             │ │  Fallback:       │
  │ image →      │ │ Sentence    │ │  SHA-256 hash    │
  │  ImageLoader │ │ boundaries  │ │  (768-dim)       │
  │  (EasyOCR)   │ │             │ │                  │
  │ URL   →      │ │ ChunkVal-   │ └──────────────────┘
  │  WebLoader   │ │ idator ✓    │
  └──────────────┘ └─────────────┘
          │
          └─────────────────────────────────────────────────────────────────┐
                                                                            │
  ┌─────────────────────────────────────────────────────────────────────────▼──────────┐
  │                          STEP 5: PERSISTENCE & CATALOG                              │
  │                                                                                     │
  │  DocumentSQLRepository.create()                                                     │
  │   → PostgreSQL documents table: {id, name, file_type, source_type, status, path}   │
  │                                                                                     │
  │  ChunkSQLRepository.create_many()                                                   │
  │   → PostgreSQL chunks table: {chunk_id, document_id, chunk_index, content, meta}   │
  │                                                                                     │
  │  IngestionHistorySQLRepository.create()                                             │
  │   → PostgreSQL ingestion_history: {doc_name, status, chunks_created, error_msg}    │
  │                                                                                     │
  │  MemoryService.register_document()                                                  │
  │   → SQLite documents table: {id, name, type, path, size}                          │
  │                                                                                     │
  │  CatalogSyncService.sync()                                                          │
  │   → PostgreSQL knowledge_assets: {name, source_type, status, asset_metadata}       │
  └─────────────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════════════════
                         WEBSITE CRAWLER PIPELINE
═══════════════════════════════════════════════════════════════════════════════════════════

  POST /api/website {url}
       │
       ▼
  WebsiteCrawlerService.start_crawl()
  [Runs in background threading.Thread — non-blocking]
       │
       ├─► 1. robots.txt fetch & validation
       ├─► 2. sitemap.xml discovery → parse all <loc> URLs
       │       If no sitemap: recursive link crawl (max 50 pages, depth 3)
       ├─► 3. Per-page: requests.get() + BeautifulSoup
       │       strip <script> <style> <nav> <footer> → clean text
       ├─► 4. Rate limiting: polite delays between requests
       ├─► 5. Build page JSON array: [{url, title, content}, ...]
       ├─► 6. Save → backend/data/json/{website_name}.json
       ├─► 7. DocumentChunker (heading-aware chunking)
       ├─► 8. EmbeddingService → generate_embeddings()
       ├─► 9. QdrantService.add_documents() (batched 100/batch)
       ├─► 10. CatalogSyncService → knowledge_assets record
       └─► 11. Update crawled_websites table: status/counts/timestamps

═══════════════════════════════════════════════════════════════════════════════════════════
                     STARTUP SEQUENCE (lifespan.py)
═══════════════════════════════════════════════════════════════════════════════════════════

  Server starts (uvicorn)
       │
       ├─► FastAPI app created (main.py)
       ├─► CORS middleware registered
       ├─► StaticFiles mounted (frontend/)
       ├─► API routes registered (api/router.py)
       │
       └─► lifespan() starts:
             ├─► MemoryService() → create_tables() (SQLite + WAL mode)
             ├─► Base.metadata.create_all(engine) (PostgreSQL ORM tables)
             ├─► Seed default websites into SQLite (LangChain, CrewAI, FastAPI)
             ├─► await asyncio.sleep(2)
             ├─► KnowledgeBaseLoader.sync_knowledge_base() [initial scan]
             └─► asyncio.create_task(auto_sync_watcher(memory, 10s)) [background]

  Every 10 seconds (background):
       KnowledgeBaseLoader.discover_files() → backend/data/
       Compare vs SQLite documents table
       Auto-ingest any new files found
```

---

*Architecture diagrams appended to Standard Operating Procedures — AI Enterprise RAG Application v2.0*


---

---

# 🗄️ PostgreSQL & PGAdmin — Complete Setup, Data Flow & Operations Guide

> **This section is your complete reference for everything PostgreSQL-related in this project** — how to install it, connect PGAdmin, understand which data lands in which table, write useful queries, and troubleshoot common issues.

---

## Why PostgreSQL is Used in This Project

The application uses **two databases in parallel**:

| Database | Purpose | Managed By |
|---|---|---|
| **SQLite** (`chat_history.db`) | Chat conversations, messages, RAG evaluation scores, 12-col analytics | `MemoryService` (direct SQL) |
| **PostgreSQL** (via `DATABASE_URL`) | Documents, chunks, knowledge catalog, ingestion history, website crawls, evaluations, governance | SQLAlchemy 2.0 ORM |

**Why PostgreSQL for the ORM tables?**
- Enterprise-grade: handles concurrent writes from multiple users without locks
- FK-enforced relationships (chunks → documents, reviews → documents)
- Full SQL power: JOINs, aggregations, range queries on evaluation history
- PGAdmin provides a visual GUI to inspect all data without writing any code
- Can be swapped to SQLite for local dev just by changing `DATABASE_URL` in `.env`

---

## Step 1 — Install PostgreSQL

### Mac (Homebrew):
```bash
brew install postgresql@16
brew services start postgresql@16

# Verify it's running
psql --version
pg_isready
```

### Windows (Installer):
1. Download from: https://www.postgresql.org/download/windows/
2. Run the installer — defaults are fine
3. **Remember the password you set for the `postgres` user** — you'll need it
4. PostgreSQL installs as a Windows Service and starts automatically

### Verify PostgreSQL is running:
```bash
# Mac/Linux
pg_isready -h localhost -p 5432

# Windows PowerShell
Test-NetConnection -ComputerName localhost -Port 5432
```

---

## Step 2 — Create the Database

### Mac/Linux terminal:
```bash
# Connect as postgres superuser
psql -U postgres

# Inside psql shell:
CREATE DATABASE rag_db;
\l          -- list all databases (verify rag_db appears)
\q          -- quit
```

### Windows PowerShell (after PostgreSQL install):
```powershell
# Open psql (may need to add to PATH first)
psql -U postgres

# Inside psql shell:
CREATE DATABASE rag_db;
\l
\q
```

---

## Step 3 — Configure .env

Update your project `.env` file at `AI_RAG_V3/.env`:

```env
# Replace the SQLite line with PostgreSQL:
DATABASE_URL=postgresql+psycopg2://postgres:YourPassword@localhost:5432/rag_db

# Keep everything else the same:
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash
GEMINI_API_KEY=your-key
```

When you start the server, SQLAlchemy reads this URL and automatically creates all tables.

---

## Step 4 — Install PGAdmin

PGAdmin is the official GUI tool to visually browse your PostgreSQL data.

### Download:
- Mac: https://www.pgadmin.org/download/pgadmin-4-macos/
- Windows: https://www.pgadmin.org/download/pgadmin-4-windows/

### Connect PGAdmin to your database:

1. Open PGAdmin 4
2. In the left panel, right-click **Servers** → **Register** → **Server...**
3. Fill in the form:

**General tab:**
```
Name: RAG App Database
```

**Connection tab:**
```
Host name/address:  localhost
Port:               5432
Maintenance database: postgres
Username:           postgres
Password:           YourPassword   (the one you set during install)
```

4. Click **Save**
5. Expand: `Servers` → `RAG App Database` → `Databases` → `rag_db` → `Schemas` → `public` → `Tables`

You will see all tables created automatically when the FastAPI server first started.

---

## PostgreSQL Tables — What Data Goes Where

### Table: `documents`

**Populated by:** `DocumentSQLRepository.create()` in `backend/services/document_management/document_sql_repository.py`

**Triggered when:** Any file is uploaded via UI, URL is ingested, text is pasted, or auto-sync picks up a file from `backend/data/`

**Data it stores:**
```sql
SELECT id, name, file_type, source_type, status, file_size, file_path, created_at
FROM documents
ORDER BY created_at DESC;
```

| Column | Example Value | Meaning |
|---|---|---|
| `id` | `a3f7b2c1-...` | UUID primary key |
| `name` | `company_policy.pdf` | Original filename |
| `file_type` | `pdf` | File extension |
| `source_type` | `FILE` / `URL` / `PASTE` / `WEBSITE` | Where it came from |
| `status` | `indexed` | Processing status |
| `file_size` | `245780` | Bytes |
| `created_at` | `2026-08-16 14:30:00` | Ingestion timestamp |

---

### Table: `chunks`

**Populated by:** `ChunkSQLRepository.create_many()` in `backend/services/document_management/chunk_sql_repository.py`

**Triggered when:** Every document is split into chunks during ingestion (after `DocumentChunker` runs)

**Data it stores:**
```sql
SELECT chunk_id, document_id, chunk_index, LEFT(content, 100) as preview, created_at
FROM chunks
WHERE document_id = 'your-document-uuid'
ORDER BY chunk_index;
```

| Column | Example | Meaning |
|---|---|---|
| `chunk_id` | `chunk-001-a3f7...` | UUID of this specific chunk |
| `document_id` | `a3f7b2c1-...` | FK → documents.id |
| `chunk_index` | `0`, `1`, `2`, `3` | Position in original document |
| `content` | `"The refund policy states..."` | Raw text content of this chunk |
| `metadata_json` | `{"page": 3, "source": "policy.pdf"}` | Source metadata |

**Useful query — find all chunks for a document:**
```sql
SELECT d.name, c.chunk_index, LEFT(c.content, 150) as preview
FROM documents d
JOIN chunks c ON d.id = c.document_id
WHERE d.name = 'company_policy.pdf'
ORDER BY c.chunk_index;
```

---

### Table: `knowledge_assets`

**Populated by:** `CatalogSyncService.sync()` in `backend/catalog/services/catalog_sync_service.py`

**Triggered when:** Every successful ingestion → one `knowledge_asset` record per document

**Data it stores:**
```sql
SELECT name, source_type, status, created_at
FROM knowledge_assets
ORDER BY created_at DESC;
```

| Column | Example | Meaning |
|---|---|---|
| `name` | `company_policy.pdf` | Asset display name |
| `source_type` | `FILE` / `URL` / `WEBSITE` / `PASTE` | Origin type |
| `status` | `indexed` / `pending` / `failed` | Catalog status |
| `asset_metadata` | JSON blob | Extra metadata (URL, page count, etc.) |

---

### Table: `ingestion_history`

**Populated by:** `IngestionHistorySQLRepository.create()` in `backend/services/ingestion_history/`

**Triggered when:** After every ingestion attempt — whether it succeeded or failed

**Data it stores:**
```sql
SELECT document_name, source_type, status, chunks_created, error_message, created_at
FROM ingestion_history
ORDER BY created_at DESC
LIMIT 20;
```

| Column | Example | Meaning |
|---|---|---|
| `document_name` | `report_q4.pdf` | Name of document attempted |
| `source_type` | `FILE` | How it was ingested |
| `status` | `SUCCESS` / `FAILED` | Outcome |
| `chunks_created` | `14` | How many chunks were generated |
| `error_message` | `NULL` or `"OCR failed: timeout"` | Error detail if failed |

**Useful query — find all failed ingestions:**
```sql
SELECT document_name, error_message, created_at
FROM ingestion_history
WHERE status = 'FAILED'
ORDER BY created_at DESC;
```

---

### Table: `crawled_websites`

**Populated by:** `website_ingestion.py` route (creates record) + `WebsiteCrawlerService` (updates during crawl)

**Triggered when:** User submits a URL on the Website Crawler page (`/website`)

**Data it stores:**
```sql
SELECT website_name, url, status,
       discovered_pages_count, processed_pages_count, failed_pages_count,
       total_chunks, total_embeddings, created_at
FROM crawled_websites
ORDER BY created_at DESC;
```

| Column | Example | Meaning |
|---|---|---|
| `url` | `https://docs.langchain.com` | Root URL submitted |
| `website_name` | `langchain_docs` | Derived name for the crawl |
| `status` | `running` / `completed` / `failed` | Current crawl state |
| `discovered_pages_count` | `142` | Pages found via sitemap |
| `processed_pages_count` | `138` | Successfully scraped + indexed |
| `failed_pages_count` | `4` | Pages that errored |
| `total_chunks` | `2743` | Chunks indexed into Qdrant |
| `json_backup_path` | `backend/data/json/langchain.json` | Local backup file location |

---

### Table: `evaluations`

**Populated by:** `EvaluationSQLRepository.create()` in `backend/services/evaluation/evaluation_sql_repository.py`

**Triggered when:** After every RAG query that runs through `calculate_rag_metrics()`

**Data it stores:**
```sql
SELECT query, context_relevance, faithfulness, answer_relevance,
       confidence, latency_ms, model_used, created_at
FROM evaluations
ORDER BY created_at DESC
LIMIT 10;
```

| Column | Example | Meaning |
|---|---|---|
| `query` | `"What is our refund policy?"` | The user's original question |
| `context_relevance` | `0.87` | How relevant retrieved chunks were |
| `faithfulness` | `0.92` | How grounded response is in context |
| `answer_relevance` | `0.84` | How relevant the answer is to the query |
| `confidence` | `0.88` | Weighted average of all three |
| `latency_ms` | `1850.4` | Total response time in milliseconds |
| `model_used` | `gemini-2.5-flash` | LLM that generated the answer |

---

### Table: `knowledge_reviews`

**Populated by:** `KnowledgeReviewService` when admin queues documents for review

**Data it stores:**
```sql
SELECT * FROM knowledge_reviews WHERE status = 'pending';
```

---

### Table: `recommendations`

**Populated by:** AI-generated retrieval improvement suggestions

**Data it stores:**
```sql
SELECT title, description, priority, status, created_at
FROM recommendations
ORDER BY priority DESC, created_at DESC;
```

---

## Useful PGAdmin SQL Queries for Developers

Open PGAdmin → right-click `rag_db` → **Query Tool** → paste any query below → press **F5** to run.

### 1. Full document summary with chunk counts:
```sql
SELECT
    d.name,
    d.file_type,
    d.source_type,
    d.status,
    COUNT(c.chunk_id) AS chunk_count,
    d.created_at
FROM documents d
LEFT JOIN chunks c ON d.id = c.document_id
GROUP BY d.id, d.name, d.file_type, d.source_type, d.status, d.created_at
ORDER BY d.created_at DESC;
```

### 2. RAG evaluation quality trend by day:
```sql
SELECT
    DATE(created_at) AS date,
    ROUND(AVG(context_relevance)::numeric, 3)  AS avg_context_relevance,
    ROUND(AVG(faithfulness)::numeric, 3)        AS avg_faithfulness,
    ROUND(AVG(answer_relevance)::numeric, 3)    AS avg_answer_relevance,
    ROUND(AVG(confidence)::numeric, 3)          AS avg_confidence,
    ROUND(AVG(latency_ms)::numeric, 0)          AS avg_latency_ms,
    COUNT(*)                                    AS total_queries
FROM evaluations
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

### 3. All crawled websites and their progress:
```sql
SELECT
    website_name,
    url,
    status,
    discovered_pages_count,
    processed_pages_count,
    failed_pages_count,
    total_chunks,
    total_embeddings,
    created_at
FROM crawled_websites
ORDER BY created_at DESC;
```

### 4. Recent ingestion history — successes and failures:
```sql
SELECT
    document_name,
    source_type,
    status,
    chunks_created,
    COALESCE(error_message, 'None') AS error,
    created_at
FROM ingestion_history
ORDER BY created_at DESC
LIMIT 50;
```

### 5. Documents with zero chunks (failed chunking — investigate these):
```sql
SELECT d.name, d.file_type, d.source_type, d.created_at
FROM documents d
WHERE NOT EXISTS (
    SELECT 1 FROM chunks c WHERE c.document_id = d.id
)
ORDER BY d.created_at DESC;
```

### 6. Worst-performing queries (lowest confidence scores):
```sql
SELECT
    LEFT(query, 80) AS query_preview,
    ROUND(confidence::numeric, 3) AS confidence,
    ROUND(context_relevance::numeric, 3) AS context_relevance,
    ROUND(faithfulness::numeric, 3) AS faithfulness,
    ROUND(latency_ms::numeric, 0) AS latency_ms,
    model_used,
    created_at
FROM evaluations
WHERE confidence < 0.6
ORDER BY confidence ASC
LIMIT 20;
```

### 7. Knowledge asset catalog overview:
```sql
SELECT
    source_type,
    status,
    COUNT(*) AS asset_count
FROM knowledge_assets
GROUP BY source_type, status
ORDER BY source_type, status;
```

### 8. Full text search inside chunks (find which chunks contain a keyword):
```sql
SELECT
    d.name AS document,
    c.chunk_index,
    LEFT(c.content, 200) AS chunk_preview
FROM chunks c
JOIN documents d ON c.document_id = d.id
WHERE c.content ILIKE '%refund policy%'
ORDER BY d.name, c.chunk_index;
```

---

## SQLite vs PostgreSQL — Quick Reference

| Data | Database | File / Table | Access Method |
|---|---|---|---|
| Conversations | SQLite | `chat_history.db / conversations` | MemoryService SQL |
| Chat messages + metrics | SQLite | `chat_history.db / messages` | MemoryService SQL |
| 12-col analytics records | SQLite | `chat_history.db / chat_history_records` | MemoryService SQL |
| RAG eval scores (lightweight) | SQLite | `chat_history.db / rag_evaluation` | MemoryService SQL |
| Document registry | SQLite | `chat_history.db / documents` | MemoryService SQL |
| Document registry (rich) | PostgreSQL | `documents` | SQLAlchemy ORM |
| Text chunks | PostgreSQL | `chunks` | SQLAlchemy ORM |
| Knowledge catalog | PostgreSQL | `knowledge_assets` | SQLAlchemy ORM |
| Ingestion audit trail | PostgreSQL | `ingestion_history` | SQLAlchemy ORM |
| Website crawl jobs | PostgreSQL | `crawled_websites` | SQLAlchemy ORM |
| Evaluation results (full schema) | PostgreSQL | `evaluations` | SQLAlchemy ORM |
| Knowledge review queue | PostgreSQL | `knowledge_reviews` | SQLAlchemy ORM |
| AI recommendations | PostgreSQL | `recommendations` | SQLAlchemy ORM |

---

## How to Access SQLite Data (chat_history.db)

The SQLite file is at: `backend/data/database_files/chat_history.db`

### Option A — DB Browser for SQLite (GUI, recommended):
- Download: https://sqlitebrowser.org/dl/
- Open: File → Open Database → navigate to `chat_history.db`
- Browse tables on the "Browse Data" tab

### Option B — Python (command line):
```bash
python -c "
import sqlite3
conn = sqlite3.connect('backend/data/database_files/chat_history.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
print('Tables:', [r[0] for r in cursor.fetchall()])
cursor.execute('SELECT COUNT(*) FROM chat_history_records')
print('Analytics records:', cursor.fetchone()[0])
conn.close()
"
```

### Option C — SQLite CLI:
```bash
# Mac/Linux
sqlite3 backend/data/database_files/chat_history.db

# Inside sqlite3 shell:
.tables                              -- list all tables
SELECT COUNT(*) FROM conversations;  -- count chats
SELECT * FROM chat_history_records LIMIT 5;
.quit
```

---

## Troubleshooting PostgreSQL

### "Connection refused" error:
```bash
# Mac — check if PostgreSQL is running
brew services list | grep postgresql
brew services start postgresql@16

# Windows — check Windows Services
Get-Service -Name postgresql*
Start-Service -Name postgresql-x64-16
```

### "password authentication failed":
```bash
# Reset postgres user password
psql -U postgres
ALTER USER postgres PASSWORD 'NewPassword';
\q
# Then update DATABASE_URL in .env with new password
```

### "database rag_db does not exist":
```bash
psql -U postgres -c "CREATE DATABASE rag_db;"
# Then restart the FastAPI server — tables auto-create
```

### Tables missing after server start:
```bash
# Check the DATABASE_URL is correct in .env
python -c "
from backend.settings import settings
print('DATABASE_URL:', settings.DATABASE_URL)
"

# Manually trigger table creation:
python -c "
from backend.database.database import engine, Base
Base.metadata.create_all(engine)
print('Tables created')
"
```

### See all tables created in PostgreSQL:
```sql
-- Run in PGAdmin Query Tool:
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

---

*PostgreSQL & PGAdmin section — AI Enterprise RAG Application v2.0*
*Reference this section any time you need to inspect, query, or troubleshoot the relational database layer.*
