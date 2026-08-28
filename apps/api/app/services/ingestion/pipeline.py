import logging
import hashlib
from datetime import datetime, timezone
from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session

from app.models import Document, DocumentChunk, DocumentStatus, Job, JobStatus
from app.services.storage import get_storage_provider
from app.services.ingestion.parsers import get_document_parser
from app.services.ingestion.chunker import StructureAwareChunker
from app.ai.providers import get_ai_provider

logger = logging.getLogger(__name__)


class IngestionPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.storage = get_storage_provider()
        self.chunker = StructureAwareChunker()
        self.ai_provider = get_ai_provider()

    def process_document(self, document_id: UUID, job_id: Optional[UUID] = None) -> bool:
        doc = self.db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            logger.error(f"Document {document_id} not found.")
            return False

        job = None
        if job_id:
            job = self.db.query(Job).filter(Job.id == job_id).first()

        try:
            # 1. Update status to PROCESSING
            doc.status = DocumentStatus.PROCESSING
            doc.error_message = None
            if job:
                job.status = JobStatus.RUNNING
                job.started_at = datetime.now(timezone.utc)
                job.progress = 10
                job.message = "Downloading file from storage"
            self.db.commit()

            # 2. Download file content
            file_bytes = self.storage.download(doc.storage_key)
            doc.checksum = hashlib.sha256(file_bytes).hexdigest()

            # 3. Text Extraction
            if job:
                job.progress = 25
                job.message = "Extracting text and document structure"
                self.db.commit()

            parser = get_document_parser(doc.original_filename, doc.mime_type)
            parsed_doc = parser.parse(file_bytes, doc.original_filename)
            doc.page_count = parsed_doc.page_count

            # 4. Chunking
            if job:
                job.progress = 50
                job.message = "Splitting text into semantic chunks"
                self.db.commit()

            generated_chunks = self.chunker.chunk_document(parsed_doc)
            if not generated_chunks:
                raise ValueError("No text could be extracted or chunked from the uploaded document.")

            # 5. Delete existing chunks if re-indexing
            self.db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()
            self.db.commit()

            # 6. Embedding generation
            if job:
                job.progress = 70
                job.message = f"Generating vector embeddings for {len(generated_chunks)} chunks"
                self.db.commit()

            chunk_texts = [c.content for c in generated_chunks]
            embeddings = self.ai_provider.embed_batch(chunk_texts)

            # 7. Store chunks + vectors in DB
            for idx, (gen_chunk, emb) in enumerate(zip(generated_chunks, embeddings)):
                db_chunk = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=gen_chunk.chunk_index,
                    content=gen_chunk.content,
                    page_number=gen_chunk.page_number,
                    section_title=gen_chunk.section_title,
                    token_count=gen_chunk.token_count,
                    embedding=emb,
                    metadata_json=gen_chunk.metadata
                )
                self.db.add(db_chunk)

            doc.chunk_count = len(generated_chunks)
            doc.status = DocumentStatus.READY
            doc.error_message = None

            if job:
                job.status = JobStatus.COMPLETED
                job.progress = 100
                job.message = f"Successfully indexed {len(generated_chunks)} chunks."
                job.completed_at = datetime.now(timezone.utc)

            self.db.commit()
            logger.info(f"Document {document_id} ingestion completed with {len(generated_chunks)} chunks.")
            return True

        except Exception as e:
            logger.exception(f"Ingestion failed for document {document_id}: {e}")
            self.db.rollback()
            doc.status = DocumentStatus.FAILED
            doc.error_message = str(e)
            if job:
                job.status = JobStatus.FAILED
                job.error_message = str(e)
                job.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            return False
