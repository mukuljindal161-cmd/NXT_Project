import os
import sys
from celery import Celery

# Add apps/api to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/api")))

from app.config import settings

celery_app = Celery(
    "college_rag_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="tasks.ingest_document")
def task_ingest_document(document_id_str: str, job_id_str: str = None):
    from uuid import UUID
    from app.db.session import SessionLocal
    from app.services.ingestion.pipeline import IngestionPipeline

    db = SessionLocal()
    try:
        pipeline = IngestionPipeline(db)
        doc_id = UUID(document_id_str)
        job_id = UUID(job_id_str) if job_id_str else None
        success = pipeline.process_document(doc_id, job_id)
        return {"success": success, "document_id": document_id_str}
    finally:
        db.close()
