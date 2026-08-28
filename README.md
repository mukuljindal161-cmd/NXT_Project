# 🎓 College RAG Assistant — Production Knowledge Base

A production-quality, enterprise-grade academic information assistant that answers student and administrative questions **strictly grounded in official institution documents** (PDFs, DOCX, TXT) using **Retrieval-Augmented Generation (RAG)** and **pgvector**.

---

## 🌟 Key Features

- **Strict Grounding & Zero Hallucination**: QueryRouter, Vector Similarity Thresholding (`>= 0.65`), and deterministic Evidence Validation prevent fabricated dates, fees, or policies.
- **Verifiable Source Citations**: Every answer displays clickable citations with document names, page numbers, and cosine similarity match scores.
- **Fast SSE Token Streaming**: Real-time response streaming with Server-Sent Events (SSE) and progressive UI rendering.
- **Role-Based Security**: Complete separation between student access and administrative control (document ingestion, collection partitioning, job tracking).
- **Multi-Format Ingestion**: Supports `.pdf`, `.docx`, `.txt`, and `.md` with page-aware extraction and structure-aware chunking.
- **Flexible AI Abstraction**: First-class support for **Google Gemini API** (`gemini-1.5-flash`, `text-embedding-004`) with deterministic offline Mock fallback for zero-config testing.

---

## 🏗️ Tech Stack

- **Frontend**: Next.js 15+ (App Router), React 19, TypeScript, Tailwind CSS, Lucide Icons, React-Markdown.
- **Backend API**: FastAPI (Python 3.12+), SQLAlchemy 2.0, Pydantic v2, Alembic, Uvicorn.
- **Database & Vectors**: PostgreSQL 16 with `pgvector` extension for 768-dimensional cosine vector similarity search.
- **Task Queue & Cache**: Celery & Redis.
- **Storage Layer**: Local filesystem storage with sanitization (or GCS/S3 in production).

---

## 🚀 Quick Start (Local Setup)

### Option 1: Run with Docker Compose (Recommended)

The easiest way to run the entire full-stack system is using Docker Compose:

1. **Clone & Navigate to the Project:**
   ```bash
   cd "c:\Users\Mukul Jindal\OneDrive\Desktop\Project Folder"
   ```

2. **Start All Services:**
   ```bash
   docker-compose up --build
   ```

3. **Access the Applications:**
   - **Frontend Web Portal**: [http://localhost:3000](http://localhost:3000)
   - **FastAPI Interactive Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **API Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

### Option 2: Run Bare-Metal (Python + Node.js)

#### 1. Start PostgreSQL (with pgvector) & Redis
```bash
docker-compose up -d postgres redis
```

#### 2. Backend Setup (FastAPI)
```bash
# Create and activate Python virtual environment
python -m venv venv
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r apps/api/requirements.txt

# Run Database Migrations
cd apps/api
alembic upgrade head
cd ../..

# Seed Database with Admin, Student & Sample College Documents
python scripts/seed.py

# Start FastAPI server
cd apps/api
uvicorn app.main:app --reload --port 8000
```

#### 3. Frontend Setup (Next.js)
Open a new terminal window:
```bash
cd apps/web
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🔐 Default Demo Accounts (Seed Data)

The seed script automatically populates test accounts and official college manuals (Academic Calendars, Fee Schedules, Hostel Rules, and Library Policies):

| Role | Email | Password | Permissions |
|---|---|---|---|
| **Admin** | `admin@example.edu` | `AdminPass123!` | Document upload/delete/reindex, Collections, Jobs, Analytics |
| **Student** | `student@example.edu` | `StudentPass123!` | Interactive grounded chat, Conversations history, Citations |

---

## 🧪 Running Automated Tests

Run the complete backend test suite:
```bash
pytest apps/api/tests
```

Run test suite with verbose output:
```bash
pytest apps/api/tests -v
```

---

## 📖 System Documentation

Detailed technical design and reference documents:
- [System Architecture](file:///c:/Users/Mukul%20Jindal/OneDrive/Desktop/Project%20Folder/docs/architecture.md)
- [RAG Pipeline & Grounding Rules](file:///c:/Users/Mukul%20Jindal/OneDrive/Desktop/Project%20Folder/docs/rag.md)
- [API Reference](file:///c:/Users/Mukul%20Jindal/OneDrive/Desktop/Project%20Folder/docs/api.md)
- [Local Development Guide](file:///c:/Users/Mukul%20Jindal/OneDrive/Desktop/Project%20Folder/docs/development.md)

---

## 🛡️ RAG Grounding Verification Flow

To verify that the system is strictly performing true RAG:
1. Sign in as `admin@example.edu` at [http://localhost:3000/login](http://localhost:3000/login).
2. Go to **Admin Console -> Documents** and upload a new PDF/DOCX policy.
3. Observe the ingestion job in **Ingestion Jobs** transitioning to `COMPLETED` and the document becoming `READY`.
4. Sign in as `student@example.edu` at [http://localhost:3000/chat](http://localhost:3000/chat).
5. Ask: *"What is the last date to submit the semester fee without penalty?"*
6. Notice the streaming answer citing the exact document name, page number, and similarity score.
7. Ask an unsupported question: *"How do I bake a pizza?"*
8. Notice the assistant strictly rejects off-topic queries in accordance with grounding rules.
