# Local Development Guide

## Prerequisites
- **Python 3.12+**
- **Node.js 20+ / npm**
- **Docker & Docker Compose** (Recommended for PostgreSQL with `pgvector` and Redis)

## 1. Quick Start via Docker Compose
To spin up all services including PostgreSQL with `pgvector`, Redis, FastAPI, Worker, and Next.js frontend:

```bash
docker-compose up --build
```

Access:
- Frontend: http://localhost:3000
- Backend API Docs: http://localhost:8000/docs

## 2. Bare-Metal Local Development

### Step 1: Start Database & Cache
```bash
docker-compose up -d postgres redis
```

### Step 2: Setup Python Virtual Environment
```bash
# In project root
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r apps/api/requirements.txt
```

### Step 3: Run Database Migrations & Seed Data
```bash
cd apps/api
alembic upgrade head
cd ../..
python scripts/seed.py
```

### Step 4: Run Backend API
```bash
cd apps/api
uvicorn app.main:app --reload --port 8000
```

### Step 5: Run Next.js Frontend
```bash
cd apps/web
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000).

## 3. Running Automated Tests
```bash
pytest apps/api/tests
```
