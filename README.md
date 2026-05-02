# Vectorless RAG

A production-ready Retrieval-Augmented Generation (RAG) application that retrieves relevant content from uploaded documents and answers questions — without vector embeddings or a vector database. Retrieval is powered by PostgreSQL full-text search (tsvector) with multi-stage fallback.

## Features

- **Vectorless retrieval** — PostgreSQL FTS (`tsvector` + `ts_rank`) with 4-stage fallback: strict FTS → loose OR-FTS → ILIKE keyword scan → most-recent chunks
- **Multi-format ingestion** — PDF, CSV, Excel (.xlsx/.xls), Word (.docx), JSON, TXT, Markdown, HTML
- **LLM answers** — OpenAI GPT-4o-mini with source citations (filename + page number)
- **Auto schema** — tables and tsvector trigger created automatically on first startup; existing chunks backfilled
- **3-page UI** — Chat, Documents, Health status

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.9+, FastAPI 0.115, SQLAlchemy 2.0 async |
| Database | PostgreSQL (tsvector FTS, GIN index) |
| LLM | OpenAI API (`gpt-4o-mini`) |
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Doc Parsing | PyMuPDF, pandas, python-docx, BeautifulSoup |

## Project Structure

```
vectorless-rag-pageindex/
├── backend/
│   ├── api/routes/       # ingest, query, documents, health
│   ├── core/             # retriever, chunker, reranker, llm
│   ├── parsers/          # per-format parsers + router
│   ├── db/               # models, session, init (tables + trigger)
│   ├── schemas/          # Pydantic request/response models
│   ├── config.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Chat
│   │   ├── documents/page.tsx # Document management
│   │   └── health/page.tsx    # API & DB status
│   ├── components/
│   └── lib/api.ts
├── .env.example
└── README.md
```

## Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL running locally (any existing instance works)
- OpenAI API key

## Setup

### 1. Clone and configure environment

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=               # leave blank to use OS username (macOS default)
DB_PASSWORD=           # leave blank if no password set

OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

### 2. Create the database

If you don't have a database yet, create one in psql or DBeaver:

```sql
CREATE DATABASE vectorless_rag;
```

Tables and the tsvector trigger are created automatically on first backend startup — no migrations to run manually.

### 3. Start the backend

```bash
cd vectorless-rag-pageindex
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt

PYTHONPATH=. uvicorn backend.main:app --reload
```

Backend runs at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### 4. Start the frontend

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`.

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/ingest` | Upload a document (multipart/form-data) |
| `POST` | `/api/query` | Ask a question, get answer + sources |
| `GET` | `/api/documents` | List all ingested documents |
| `DELETE` | `/api/documents/{id}` | Delete a document and its chunks |
| `GET` | `/api/health` | API and database health check |

### Query request

```json
POST /api/query
{
  "question": "What are the key findings?",
  "top_k": 5
}
```

### Query response

```json
{
  "answer": "The key findings are...",
  "sources": [
    {
      "filename": "report.pdf",
      "page_number": 3,
      "snippet": "...",
      "score": 0.91
    }
  ],
  "model": "gpt-4o-mini",
  "usage": { "prompt_tokens": 512, "completion_tokens": 128, "total_tokens": 640 }
}
```

## Supported File Types

| Format | Extension(s) |
|---|---|
| PDF | `.pdf` |
| Word | `.docx`, `.doc` |
| Excel | `.xlsx`, `.xls` |
| CSV | `.csv` |
| JSON | `.json` |
| Plain text | `.txt`, `.md`, `.markdown` |
| HTML | `.html`, `.htm` |

Maximum file size: **50 MB**

## Retrieval Pipeline

```
Query
  │
  ├─ Stage 1: PostgreSQL tsvector FTS (all words must match)
  ├─ Stage 2: Loose FTS — any keyword matches (OR logic)
  ├─ Stage 3: ILIKE keyword scan (no tsvector required)
  └─ Stage 4: Most recent chunks (last resort)
        │
        ▼
  OpenAI re-ranking (top 10 → top 5)
        │
        ▼
  GPT-4o-mini answer generation
        │
        ▼
  Answer + source citations
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `vectorless_rag` | Database name |
| `DB_USER` | _(empty)_ | Database user (blank = OS username) |
| `DB_PASSWORD` | _(empty)_ | Database password |
| `OPENAI_API_KEY` | — | Required. Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model to use |
| `API_HOST` | `0.0.0.0` | Backend bind address |
| `API_PORT` | `8000` | Backend port |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins |
