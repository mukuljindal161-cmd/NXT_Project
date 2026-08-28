# College RAG Assistant — System Architecture

## Overview
The **College RAG Assistant** is a full-stack, enterprise-grade academic information assistant. It is built strictly on top of a deterministic Retrieval-Augmented Generation (RAG) pipeline to eliminate hallucinations and ensure every answer is backed by verifiable college records.

```
                         ┌─────────────────────┐
                         │   Student / Admin   │
                         └──────────┬──────────┘
                                    │
                                    v
                         ┌─────────────────────┐
                         │   Next.js Frontend  │
                         └──────────┬──────────┘
                                    │ HTTPS/SSE
                                    v
                         ┌─────────────────────┐
                         │     FastAPI API     │
                         └──────────┬──────────┘
                                    │
                   ┌────────────────┼──────────────────┐
                   │                │                  │
                   v                v                  v
            ┌────────────┐   ┌──────────────┐   ┌─────────────┐
            │ PostgreSQL │   │    Redis     │   │ File Storage│
            │ + pgvector │   │ Queue/Cache  │   │   (Local)   │
            │  (Vectors) │   └──────┬───────┘   └─────────────┘
            └──────┬─────┘          │
                   │                v
                   │       ┌────────────────┐
                   │       │ Celery / Worker│
                   │       └───────┬────────┘
                   │               │
                   └───────────────┘
```

## Core Components

### 1. Frontend (`apps/web`)
- **Framework**: Next.js 15+ (App Router)
- **Styling**: Tailwind CSS with custom academic SaaS palette, glassmorphism tokens, responsive sidebar.
- **Real-Time Streaming**: Native Server-Sent Events (SSE) consumer rendering incremental token deltas, progress indicators, and citations.
- **Pages**:
  - `/`: Engaging Landing Page with RAG architecture visualization.
  - `/login` & `/register`: Secure authentication.
  - `/chat` & `/chat/[conversationId]`: Student chat interface with multi-turn history, suggested questions, and feedback.
  - `/admin`: Dashboard with telemetry stats, document upload modal, collection management, and live ingestion job monitoring.

### 2. Backend API (`apps/api`)
- **Framework**: FastAPI (Python 3.12+)
- **ORM & DB**: SQLAlchemy 2.0 with PostgreSQL and `pgvector` extension.
- **Authentication**: Argon2id/bcrypt password hashing, HTTP-only secure cookie sessions, JWT verification, and role guards (`STUDENT`, `ADMIN`).
- **Layers**:
  - `API Layer`: Declarative routers with Pydantic validation.
  - `Service Layer`: Isolated business logic for RAG, Ingestion, Auth, and Storage.
  - `Repository / Data Layer`: Strict SQLAlchemy models and migration tracking.

### 3. Vector Database & Storage
- **PostgreSQL 16 + pgvector**: Stores high-dimensional vector embeddings (768-dim) in `document_chunks` table using cosine distance indexing (`<=>`).
- **Storage Layer**: Local filesystem storage provider with path traversal protections (easily swappable with Google Cloud Storage / AWS S3).
