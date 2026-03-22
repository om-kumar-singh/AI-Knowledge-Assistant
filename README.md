# AI Knowledge Assistant – Full-Stack RAG SaaS Platform

**Chat with your documents using AI (RAG-based system)**

---

## 🚀 Overview

**Problem:** Teams and individuals often struggle to pull clear answers from long PDFs, policies, and text documents. Keyword search misses nuance, and reading everything end-to-end does not scale.

**Solution:** An **AI-powered assistant** built on **Retrieval-Augmented Generation (RAG)**. Documents are chunked, embedded, and stored in a **vector database** so each user question retrieves the most relevant passages. A **local LLM** then produces **accurate, context-aware answers** grounded in those sources, with **multi-turn chat** and **session memory** for follow-up questions.

---

## 🧠 Features

- **Document upload** — PDF and TXT, with validation and local file storage  
- **Semantic search** — embedding-based retrieval over ingested chunks  
- **Conversational AI** — multi-turn chat in a modern web UI  
- **Source-aware responses** — answers tied to retrieved context (RAG)  
- **Chat history & session memory** — persisted messages keyed by `session_id`  
- **Full-stack app** — **Next.js** (App Router) frontend and **FastAPI** backend  

---

## 🏗️ Tech Stack

**Frontend**

- Next.js (App Router), TypeScript, Tailwind CSS  

**Backend**

- FastAPI, Python, Pydantic, SQLAlchemy  

**AI / ML**

- LangChain (loaders, text splitting, Chroma integration)  
- Hugging Face **Transformers** — **FLAN-T5** (`google/flan-t5-base`) for local text generation  
- **sentence-transformers** — `all-MiniLM-L6-v2` for embeddings  
- **ChromaDB** — persistent local vector store  

**Database**

- **PostgreSQL** (primary; SQL schema in-repo). SQLAlchemy can be pointed at **SQLite** for quick experiments via `DATABASE_URL`.  

**DevOps (optional)**

- Terraform (`infra/`), GitHub Actions CI (`.github/workflows/`)

---

## ⚙️ System Architecture

High-level data flow:

**Upload → Chunking → Embedding → Vector DB → Retrieval → LLM → Response**

1. Files are saved on disk and metadata is written to the relational DB.  
2. Text is split into chunks and embedded with a sentence-transformer model.  
3. Vectors are stored in **ChromaDB** (on-disk persistence).  
4. Each query is embedded; similar chunks are retrieved.  
5. Retrieved text plus **recent chat history** is passed to the **local LLM** to generate the final answer.  

---

## 🔄 Workflow

1. **Upload** a PDF or TXT document.  
2. **Chunk & embed** the text (LangChain + sentence-transformers).  
3. **Store** vectors in ChromaDB.  
4. User submits a **natural-language query**.  
5. **Retrieve** the top-k most relevant chunks.  
6. **Generate** an answer with the local LLM using context + conversation memory.  

---

## 📂 Folder Structure

```text
ai-knowledge-assistant/
├── .github/workflows/     # CI (frontend lint/build, backend install/compile)
├── backend/
│   ├── core/              # Settings & config
│   ├── db/                # SQLAlchemy engine, session, Base
│   ├── models/            # ORM + Pydantic schemas
│   ├── routes/            # API routers (health, upload, query, auth, …)
│   ├── services/          # LLM, chat, file upload helpers
│   ├── rag/               # Ingestion & retrieval (Chroma + embeddings)
│   ├── uploads/           # Local document storage
│   ├── main.py
│   └── requirements.txt
├── database/
│   └── schema.sql         # PostgreSQL DDL
├── frontend/
│   ├── app/               # Next.js App Router pages
│   ├── components/        # Chat UI, file upload, …
│   ├── lib/               # API client helpers
│   └── package.json
├── infra/                 # Terraform (skeleton)
└── README.md
```

---

## ▶️ How to Run Locally

**Frontend** (default: [http://localhost:3000](http://localhost:3000))

```bash
cd frontend
npm install
npm run dev
```

Optional: create `frontend/.env.local` with `NEXT_PUBLIC_API_URL=http://localhost:8000`.

**Backend** (default: [http://localhost:8000](http://localhost:8000))

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1  |  macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Copy `backend/.env.example` to `.env`, set `DATABASE_URL`, and apply `database/schema.sql` to PostgreSQL (or enable `AUTO_CREATE_TABLES` only for local experiments). API docs: [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 🚀 Future Improvements

- **User authentication** and per-user data isolation  
- **Cloud deployment** (e.g. AWS: API, DB, object storage, optional GPU)  
- **Streaming** LLM responses (SSE / WebSockets)  
- **UI/UX** polish: themes, accessibility, mobile layout, richer source citations  

---

## 🤝 Contribution / License

Contributions via pull requests are welcome.
