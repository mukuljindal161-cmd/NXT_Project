from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Job, JobStatus, User
from app.schemas import JobResponse
from app.dependencies import require_admin

router = APIRouter(prefix="/admin/jobs", tags=["Admin Jobs"])


@router.get("", response_model=List[JobResponse])
def list_jobs(
    status: Optional[JobStatus] = None,
    type: Optional[str] = None,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Job)
    if status:
        query = query.filter(Job.status == status)
    if type:
        query = query.filter(Job.type == type)

    return query.order_by(Job.created_at.desc()).limit(100).all()


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: UUID,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.post("/{job_id}/cancel", response_model=JobResponse)
def cancel_job(
    job_id: UUID,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if job.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel a job with status {job.status}"
        )
    job.status = JobStatus.CANCELLED
    job.message = "Cancelled by administrator"
    db.commit()
    db.refresh(job)
    return job
