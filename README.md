# DashLite

**AI-Powered File Search & Intelligence Platform** — inspired by [Dropbox Dash](https://dash.dropbox.com)

DashLite is a full-stack application that indexes local files and makes them searchable with AI. It combines **hybrid search** (lexical + semantic with Reciprocal Rank Fusion), **RAG-based Q&A** with source citations, and a **multi-step AI agent** that can plan, execute, and synthesize across multiple documents.

## Architecture

DashLite mirrors the architecture described in Dropbox's engineering blog ["Building Dash: How RAG and AI agents help us meet the needs of businesses"](https://dropbox.tech/machine-learning/building-dash-rag-multi-step-ai-agents-business-users):

```
                         ┌──────────────────────┐
                         │     React Frontend    │
                         │   (Dashboard, Search, │
                         │    Ask AI, Agent)      │
                         └──────────┬─────────────┘
                                    │ REST + WebSocket
                         ┌──────────▼─────────────┐
                         │    FastAPI Backend      │
                         │                         │
                         │  ┌───────────────────┐  │
                         │  │  Hybrid Search     │  │
                         │  │  ┌──────┐ ┌─────┐ │  │
                         │  │  │FTS5  │ │Numpy│ │  │
                         │  │  │(BM25)│ │Vecs │ │  │
                         │  │  └──┬───┘ └──┬──┘ │  │
                         │  │     └──┬─────┘    │  │
                         │  │     RRF Fusion    │  │
                         │  └───────────────────┘  │
                         │                         │
                         │  ┌───────────────────┐  │
                         │  │   RAG Pipeline     │  │
                         │  │ Retrieve → Augment │  │
                         │  │    → Generate      │  │
                         │  └───────────────────┘  │
                         │                         │
                         │  ┌───────────────────┐  │
                         │  │  Multi-Step Agent  │  │
                         │  │ Plan → Execute     │  │
                         │  │   → Synthesize     │  │
                         │  └───────────────────┘  │
                         │                         │
                         │  ┌───────────────────┐  │
                         │  │ File Ingestion     │  │
                         │  │ PDF/DOCX/TXT/MD   │  │
                         │  │ Images (OCR)       │  │
                         │  └───────────────────┘  │
                         └─────────────────────────┘
                              │              │
                    ┌─────────▼──┐    ┌──────▼──────┐
                    │  SQLite    │    │  ChromaDB   │
                    │ (metadata  │    │ (vectors +  │
                    │  + FTS5)   │    │  embeddings)│
                    └────────────┘    └─────────────┘
```

### Key Technical Decisions

| Decision | Reasoning |
|----------|-----------|
| **Hybrid Search with RRF** | Combines keyword precision (FTS5/BM25) with semantic understanding (vector similarity), matching how Dropbox Dash retrieves results. Reciprocal Rank Fusion merges both rankings without needing learned weights. |
| **Plan-Execute-Synthesize Agent** | Mirrors Dash's two-phase agent architecture. The agent decomposes complex queries into tool-calling steps, executes them sequentially, and synthesizes a final answer. |
| **Local Embeddings (all-MiniLM-L6-v2)** | Free, fast (8ms/query), and competitive with API-based models when combined with hybrid search. No external dependency for embeddings. |
| **SQLite + Numpy Vector Store** | SQLite provides FTS5 for lexical search and metadata storage. A custom numpy-based vector store provides persistent cosine similarity search. Both are embedded (no external services needed). |
| **FastAPI + React** | Matches Dropbox's tech stack (Python backend, React frontend). FastAPI provides async support, automatic OpenAPI docs, and WebSocket support. |

## Features

- **File Ingestion** — Ingest PDFs, DOCX, TXT, Markdown, code files, and images (OCR via Tesseract)
- **Hybrid Search** — Lexical (FTS5/BM25) + Semantic (ChromaDB) search merged with Reciprocal Rank Fusion
- **RAG Q&A** — Ask natural language questions, get answers grounded in your files with source citations
- **Multi-Step Agent** — Plan → Execute → Synthesize across multiple documents with visible step timeline
- **Document Summarization** — One-click AI summarization of any indexed document
- **Real-time Updates** — File watcher + WebSocket for live indexing notifications
- **Activity Feed** — Dashboard showing file events, query history, and usage stats

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI, SQLAlchemy (async) |
| Frontend | React 18, TypeScript, Tailwind CSS, Vite |
| Vector DB | Numpy-based (persistent, zero-dependency) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| LLM | OpenAI GPT-4o-mini |
| Metadata DB | SQLite + FTS5 |
| File Watching | watchdog |
| Real-time | WebSocket (FastAPI) |

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key
- (Optional) Tesseract for image OCR

### Setup

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/dashlite.git
cd dashlite

# Backend
cd backend
pip install -r requirements.txt
cd ..

# Frontend
cd frontend
npm install
cd ..

# Configure
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Seed demo data
cd backend
python -c "
import asyncio, sys, os
sys.path.insert(0, '.')
os.chdir('..')
from demo.seed_data import seed
asyncio.run(seed())
"
cd ..

# Run
# Terminal 1:
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2:
cd frontend && npm run dev
```

Open http://localhost:5173

### Docker (Alternative)

```bash
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
docker-compose up
```

Open http://localhost:3000

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ingest` | Ingest a single file |
| POST | `/api/v1/ingest/directory` | Ingest all files in a directory |
| GET | `/api/v1/files` | List indexed files |
| GET | `/api/v1/files/stats` | File statistics |
| GET | `/api/v1/search?q=...` | Hybrid search |
| POST | `/api/v1/ask` | RAG Q&A with sources |
| POST | `/api/v1/ask/stream` | Streaming RAG via SSE |
| POST | `/api/v1/summarize/{id}` | Summarize a document |
| POST | `/api/v1/agent/query` | Multi-step agent |
| GET | `/api/v1/activity/feed` | Activity timeline |
| WS | `/api/v1/ws/updates` | Real-time updates |

## How It Works

### Hybrid Search (Dash-style)

```
Query → FTS5/BM25 (keyword match) ──┐
                                     ├─→ Reciprocal Rank Fusion → Top-N
Query → Vector Store (semantic) ────┘
```

RRF score = `Σ 1/(k + rank)` across both result lists. This balances exact keyword matches with semantic understanding — the same approach used by Dropbox Dash.

### Multi-Step Agent

```
Complex Query → [PLAN: GPT decomposes into 2-4 steps]
             → [EXECUTE: search → analyze → compare]
             → [SYNTHESIZE: combine into final answer]
```

The agent uses a planning phase to decompose queries, then executes each step using tools (search, summarize, compare, extract, analyze), and synthesizes results into a comprehensive answer.

## Project Structure

```
dashlite/
├── backend/
│   └── app/
│       ├── api/v1/endpoints/   # REST + WebSocket endpoints
│       ├── models/             # SQLAlchemy ORM models
│       ├── schemas/            # Pydantic request/response schemas
│       ├── services/           # Business logic
│       │   ├── search_service  # Hybrid search + RRF
│       │   ├── rag_service     # RAG pipeline
│       │   ├── agent_service   # Multi-step agent
│       │   ├── ingest_service  # File processing pipeline
│       │   └── ...
│       └── db/                 # Database setup
├── frontend/src/
│   ├── pages/                  # Dashboard, Search, Files, Ask, Agent
│   ├── components/             # Reusable UI components
│   ├── api/                    # API client modules
│   └── hooks/                  # Custom React hooks
└── demo/
    ├── sample_files/           # Pre-built demo documents
    └── seed_data.py            # One-command demo setup
```

## References

- [Building Dash: How RAG and AI agents help us meet the needs of businesses](https://dropbox.tech/machine-learning/building-dash-rag-multi-step-ai-agents-business-users)
- [How Dash uses context engineering for smarter AI](https://dropbox.tech/machine-learning/how-dash-uses-context-engineering-for-smarter-ai)
- [Selecting a model for semantic search at Dropbox scale](https://dropbox.tech/machine-learning/selecting-model-semantic-search-dropbox-ai)
