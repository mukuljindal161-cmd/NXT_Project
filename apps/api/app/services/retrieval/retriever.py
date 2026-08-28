import os
import json
import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, func
import numpy as np
from app.models import Document, DocumentChunk, DocumentStatus
from app.ai.providers import get_ai_provider
from app.config import settings

logger = logging.getLogger(__name__)


class RetrievedChunk(BaseModel):
    chunk_id: UUID
    document_id: UUID
    document_title: str
    content: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    similarity_score: float
    token_count: int
    metadata_json: Optional[Dict[str, Any]] = None


class Retriever:
    def __init__(self, db: Session):
        self.db = db
        self.ai_provider = get_ai_provider()

    def retrieve(
        self,
        query: str,
        collection_id: Optional[UUID] = None,
        department: Optional[str] = None,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ) -> List[RetrievedChunk]:
        k = top_k or settings.TOP_K
        threshold = similarity_threshold if similarity_threshold is not None else settings.SIMILARITY_THRESHOLD

        # 1. Generate query embedding via AI Provider (e.g. Gemini text-embedding-004 / gemini-embedding-001)
        query_vector = self.ai_provider.embed(query)

        # Check if database is PostgreSQL with pgvector support
        dialect_name = self.db.bind.dialect.name if self.db.bind else "sqlite"

        if dialect_name == "postgresql":
            try:
                return self._retrieve_pgvector(query_vector, collection_id, department, k, threshold)
            except Exception as e:
                logger.warning(f"PostgreSQL pgvector query failed: {e}. Falling back to in-memory cosine matching.")

        # SQLite or In-Memory Vector Search
        return self._retrieve_in_memory(query_vector, query, collection_id, department, k, threshold)

    def _retrieve_pgvector(
        self,
        query_vector: List[float],
        collection_id: Optional[UUID],
        department: Optional[str],
        k: int,
        threshold: float
    ) -> List[RetrievedChunk]:
        distance_col = DocumentChunk.embedding.cosine_distance(query_vector).label("distance")

        stmt = (
            select(
                DocumentChunk,
                Document.title.label("document_title"),
                Document.id.label("doc_id"),
                distance_col
            )
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(
                and_(
                    Document.status == DocumentStatus.READY,
                    DocumentChunk.embedding.isnot(None)
                )
            )
        )

        if collection_id:
            stmt = stmt.where(Document.collection_id == collection_id)

        if department:
            from app.models import Collection
            stmt = stmt.join(Collection, Document.collection_id == Collection.id, isouter=True).where(
                Collection.department == department
            )

        stmt = stmt.order_by(distance_col.asc()).limit(k * 2)
        results = self.db.execute(stmt).all()

        retrieved: List[RetrievedChunk] = []
        seen_texts = set()

        for row in results:
            if hasattr(row, "DocumentChunk"):
                chunk = row.DocumentChunk
                doc_title = row.document_title
                doc_id = row.doc_id
                distance = float(row.distance) if row.distance is not None else 1.0
            else:
                chunk, doc_title, doc_id, distance = row[0], row[1], row[2], float(row[3]) if row[3] is not None else 1.0

            similarity = max(0.0, min(1.0, 1.0 - distance))
            if similarity < threshold:
                continue

            normalized = chunk.content.strip()
            if normalized in seen_texts:
                continue
            seen_texts.add(normalized)

            retrieved.append(
                RetrievedChunk(
                    chunk_id=chunk.id,
                    document_id=doc_id,
                    document_title=doc_title,
                    content=chunk.content,
                    page_number=chunk.page_number,
                    section_title=chunk.section_title,
                    similarity_score=round(similarity, 4),
                    token_count=chunk.token_count,
                    metadata_json=chunk.metadata_json
                )
            )
            if len(retrieved) >= k:
                break

        return retrieved

    def _retrieve_in_memory(
        self,
        query_vector: List[float],
        query: str,
        collection_id: Optional[UUID],
        department: Optional[str],
        k: int,
        threshold: float
    ) -> List[RetrievedChunk]:
        stmt = (
            select(
                DocumentChunk,
                Document.title.label("document_title"),
                Document.id.label("doc_id")
            )
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(Document.status == DocumentStatus.READY)
        )

        if collection_id:
            stmt = stmt.where(Document.collection_id == collection_id)

        if department:
            from app.models import Collection
            stmt = stmt.join(Collection, Document.collection_id == Collection.id, isouter=True).where(
                Collection.department == department
            )

        rows = self.db.execute(stmt).all()
        if not rows:
            return []

        q_vec = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            q_norm = 1e-9

        scored_candidates = []
        seen_texts = set()

        for row in rows:
            chunk = row.DocumentChunk if hasattr(row, "DocumentChunk") else row[0]
            doc_title = row.document_title if hasattr(row, "document_title") else row[1]
            doc_id = row.doc_id if hasattr(row, "doc_id") else row[2]

            raw_emb = chunk.embedding
            if isinstance(raw_emb, str):
                try:
                    raw_emb = json.loads(raw_emb)
                except Exception:
                    raw_emb = None

            if raw_emb and isinstance(raw_emb, (list, tuple)):
                c_vec = np.array(raw_emb, dtype=np.float32)

                # Ensure dimensions match before dot product
                if len(q_vec) != len(c_vec):
                    min_dim = min(len(q_vec), len(c_vec))
                    q_sub = q_vec[:min_dim]
                    c_sub = c_vec[:min_dim]
                    q_n = np.linalg.norm(q_sub) or 1e-9
                    c_n = np.linalg.norm(c_sub) or 1e-9
                    sim = float(np.dot(q_sub, c_sub) / (q_n * c_n))
                else:
                    c_norm = np.linalg.norm(c_vec) or 1e-9
                    sim = float(np.dot(q_vec, c_vec) / (q_norm * c_norm))
            else:
                # Keyword overlap fallback
                query_words = set(w.lower() for w in query.split() if len(w) > 3)
                chunk_words = set(w.lower() for w in chunk.content.split())
                if query_words and chunk_words:
                    overlap = len(query_words.intersection(chunk_words))
                    sim = min(1.0, 0.4 + (overlap / len(query_words)) * 0.5)
                else:
                    sim = 0.0

            normalized = chunk.content.strip()
            if normalized in seen_texts:
                continue
            seen_texts.add(normalized)

            if sim >= threshold:
                scored_candidates.append((sim, chunk, doc_title, doc_id))

        # Sort descending by similarity
        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        retrieved: List[RetrievedChunk] = []
        for sim, chunk, doc_title, doc_id in scored_candidates[:k]:
            retrieved.append(
                RetrievedChunk(
                    chunk_id=chunk.id,
                    document_id=doc_id,
                    document_title=doc_title,
                    content=chunk.content,
                    page_number=chunk.page_number,
                    section_title=chunk.section_title,
                    similarity_score=round(sim, 4),
                    token_count=chunk.token_count,
                    metadata_json=chunk.metadata_json
                )
            )

        return retrieved
