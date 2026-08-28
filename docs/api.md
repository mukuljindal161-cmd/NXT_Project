# API Reference

Base URL: `/api/v1`

## Health & Auth
- `GET /health` — Simple health probe
- `GET /health/ready` — Readiness check for DB, Storage & AI
- `POST /auth/register` — Register a new student account
- `POST /auth/login` — Sign in and receive session cookie + JWT
- `POST /auth/logout` — Invalidate session
- `GET /auth/me` — Return current authenticated user

## Conversations & Chat
- `GET /conversations` — List current user's conversations
- `POST /conversations` — Create a new conversation
- `GET /conversations/{id}` — Get conversation details with messages
- `PATCH /conversations/{id}` — Update conversation title
- `DELETE /conversations/{id}` — Delete own conversation
- `POST /conversations/{id}/messages` — Submit message and run RAG pipeline
- `GET /conversations/{id}/messages/stream` — SSE endpoint for real-time answer streaming
- `POST /chat/query` — One-shot question answering
- `GET /chat/query/stream` — One-shot SSE stream

## Messages & Feedback
- `GET /messages/{message_id}/citations` — List retrieved sources used for an answer
- `POST /messages/{message_id}/feedback` — Submit thumbs-up/down rating and comment

## Admin Operations (`ADMIN` Role Required)
- `GET /admin/documents` — Search and filter indexed documents
- `POST /admin/documents` — Upload and ingest PDF/DOCX/TXT
- `GET /admin/documents/{id}` — View document metadata and status
- `DELETE /admin/documents/{id}` — Delete document and associated chunks
- `POST /admin/documents/{id}/reindex` — Trigger background re-indexing
- `POST /admin/documents/{id}/replace` — Replace with a new version
- `GET /admin/collections` — List departmental collections
- `POST /admin/collections` — Create knowledge collection
- `DELETE /admin/collections/{id}` — Delete collection
- `GET /admin/jobs` — Monitor background ingestion tasks
- `GET /admin/analytics/overview` — Telemetry statistics (users, docs, queries, avg similarity)
