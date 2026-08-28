from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models import User, Document, DocumentStatus, Message, MessageRole, Job, JobStatus, Citation
from app.schemas import AnalyticsOverviewResponse
from app.dependencies import require_admin

router = APIRouter(prefix="/admin/analytics", tags=["Admin Analytics"])


@router.get("/overview", response_model=AnalyticsOverviewResponse)
def get_analytics_overview(
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    total_users = db.query(User).count()
    total_documents = db.query(Document).count()
    ready_docs = db.query(Document).filter(Document.status == DocumentStatus.READY).count()
    processing_docs = db.query(Document).filter(Document.status == DocumentStatus.PROCESSING).count()
    failed_docs = db.query(Document).filter(Document.status == DocumentStatus.FAILED).count()
    total_questions = db.query(Message).filter(Message.role == MessageRole.USER).count()
    failed_jobs = db.query(Job).filter(Job.status == JobStatus.FAILED).count()

    avg_score = db.query(func.avg(Citation.similarity_score)).scalar() or 0.0

    return AnalyticsOverviewResponse(
        users=total_users,
        documents=total_documents,
        ready_documents=ready_docs,
        processing_documents=processing_docs,
        failed_documents=failed_docs,
        questions=total_questions,
        failed_jobs=failed_jobs,
        average_retrieval_score=round(float(avg_score), 3)
    )
