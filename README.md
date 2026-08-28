# 🎓 College RAG Assistant

An AI-powered college information chatbot that uses **Retrieval-Augmented Generation (RAG)** to answer student queries from official college documents such as notices, PDFs, FAQs, academic calendars, fee documents, and policies.

---

## 1. Project Name

**College RAG Assistant**

**RAG-Based College Information Chatbot**

---

## 2. Problem Statement

Students often have difficulty finding information about college admissions, courses, fees, examinations, scholarships, hostel, library, placements, and other activities because the information is spread across multiple documents.

The **College RAG Assistant** provides a single AI-powered platform where students can ask questions in natural language and receive answers based on the college's uploaded documents, along with relevant sources.

---

## 3. Features

### Core Features

* User authentication
* Student and Admin roles
* AI-powered chat interface
* PDF/DOCX/TXT document upload
* Automatic document processing
* Text extraction and chunking
* Embedding generation
* Vector similarity search using pgvector
* RAG-based answer generation
* Source/reference display
* Unknown-question handling
* Chat history
* Admin document management
* Document re-indexing
* Streaming AI responses
* Responsive web interface

### Bonus Features

* Department-wise document collections
* Hybrid search
* Document re-ranking
* Answer feedback
* Suggested questions
* Admin analytics
* Multilingual support
* Document version management

---

## 4. Technology Stack

| Category        | Technologies                             |
| --------------- | ---------------------------------------- |
| Frontend        | Next.js, React, TypeScript, Tailwind CSS |
| Backend         | Python, FastAPI                          |
| Database        | PostgreSQL + pgvector                    |
| AI              | Google Gemini API                        |
| Embeddings      | Gemini Embedding API                     |
| Background Jobs | Celery + Redis                           |
| Storage         | Local Storage / Google Cloud Storage     |
| Authentication  | Secure Session-based Authentication      |
| Deployment      | Vercel + Cloud Backend                   |

---

## 5. Screenshots

### Home Page

![Home Page](<img width="1910" height="967" alt="image" src="https://github.com/user-attachments/assets/d60c71f7-ed40-4144-bc8b-51baed2fc617" />)

### Chat Interface

![Chat Interface](<img width="1917" height="971" alt="image" src="https://github.com/user-attachments/assets/8e44ba69-c068-4311-afc1-05b904533afc" />)

### RAG Answer with Sources

![RAG Answer](<img width="1917" height="971" alt="image" src="https://github.com/user-attachments/assets/752b9931-a68f-4648-81dc-0f4f2ba25ce2" />)

### Mobile View

![Mobile View](<img width="391" height="856" alt="image" src="https://github.com/user-attachments/assets/825c4cf4-09ca-4536-a530-665b1304e05e" />)

---

## 6. Live Demo

**Vercel URL:**
`[https://your-project.vercel.app](https://college-rag-assistant-theta.vercel.app/)`

---

## 7. Backend

**Backend/API URL:**
`https://your-backend-url.com`

---

## 8. Setup Instructions

### 1. Clone the repository

```bash
git clone <repository-url>
cd college-rag-chatbot
```

### 2. Install dependencies

Frontend:

```bash
cd apps/web
npm install
```

Backend:

```bash
cd apps/api
pip install -r requirements.txt
```

### 3. Configure environment variables

Create `.env` files using the provided `.env.example` files.

### 4. Start PostgreSQL and Redis

Using Docker:

```bash
docker compose up -d
```

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the backend

```bash
uvicorn app.main:app --reload
```

### 7. Start the frontend

```bash
npm run dev
```

The application will be available at:

```text
http://localhost:3000
```

---

## 9. Environment Variables Rquired

The following environment variables are required:

```env
DATABASE_URL=
REDIS_URL=
SECRET_KEY=
GEMINI_API_KEY=
LLM_MODEL=
EMBEDDING_MODEL=
STORAGE_PROVIDER=
STORAGE_BUCKET=
NEXT_PUBLIC_API_URL=
```
---

## RAG Pipeline

The core functionality of the project follows:

```text
College Documents
       ↓
Text Extraction
       ↓
Chunking
       ↓
Embeddings
       ↓
PostgreSQL + pgvector
       ↓
Semantic Search
       ↓
Relevant Context
       ↓
Google Gemini
       ↓
Answer + Sources
```

This ensures that the chatbot answers questions using the college's knowledge base rather than relying only on the LLM's general knowledge.

---

## Project Status

**Status:** 🚀 Completed

👨‍💻 Developer
Mukul Jindal

GitHub: https://github.com/mukuljindal161-cmd

LinkedIn: https://www.linkedin.com/in/mukuljindal07/

⭐ Feel free to explore and share your feedback!
