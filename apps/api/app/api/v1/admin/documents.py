import os
import uuid
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.session import get_db
from app.models import Document, DocumentChunk, DocumentStatus, Collection, User, Job, JobStatus
from app.schemas import DocumentResponse, DocumentListResponse
from app.services.storage import get_storage_provider
from app.services.ingestion.pipeline import IngestionPipeline
from app.dependencies import require_admin
from app.config import settings

router = APIRouter(prefix="/admin/documents", tags=["Admin Documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


@router.get("", response_model=DocumentListResponse)
def list_documents(
    status: Optional[DocumentStatus] = None,
    collection_id: Optional[UUID] = None,
    department: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Document)

    if status:
        query = query.filter(Document.status == status)

    if collection_id:
        query = query.filter(Document.collection_id == collection_id)

    if department:
        query = query.join(Collection, Document.collection_id == Collection.id).filter(
            Collection.department == department
        )

    if search:
        query = query.filter(
            or_(
                Document.title.ilike(f"%{search}%"),
                Document.original_filename.ilike(f"%{search}%")
            )
        )

    total = query.count()
    items = query.order_by(Document.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return DocumentListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    collection_id: Optional[UUID] = Form(None),
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    filename = file.filename or "uploaded_document"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed formats: PDF, DOCX, TXT, MD"
        )

    file_content = await file.read()
    file_size = len(file_content)
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB"
        )

    doc_id = uuid.uuid4()
    storage_key = f"documents/{doc_id}/{filename}"

    # Store file
    import io
    storage = get_storage_provider()
    storage.upload(io.BytesIO(file_content), storage_key)

    doc = Document(
        id=doc_id,
        collection_id=collection_id,
        uploaded_by=current_admin.id,
        title=title or filename,
        original_filename=filename,
        mime_type=file.content_type or "application/octet-stream",
        storage_key=storage_key,
        file_size=file_size,
        status=DocumentStatus.UPLOADED,
        version=1
    )
    db.add(doc)

    # Create ingestion job
    job = Job(
        type="DOCUMENT_INGESTION",
        status=JobStatus.PENDING,
        user_id=current_admin.id,
        entity_id=doc.id,
        message="Queued for processing"
    )
    db.add(job)
    db.commit()
    db.refresh(doc)
    db.refresh(job)

    # Run ingestion
    pipeline = IngestionPipeline(db)
    pipeline.process_document(doc.id, job_id=job.id)
    db.refresh(doc)

    return doc


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: UUID,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return doc


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: UUID,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Delete storage file
    try:
        storage = get_storage_provider()
        storage.delete(doc.storage_key)
    except Exception:
        pass

    db.delete(doc)
    db.commit()
    return None


@router.post("/{document_id}/reindex", response_model=DocumentResponse)
def reindex_document(
    document_id: UUID,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    job = Job(
        type="DOCUMENT_REINDEX",
        status=JobStatus.PENDING,
        user_id=current_admin.id,
        entity_id=doc.id,
        message="Queued for re-indexing"
    )
    db.add(job)
    db.commit()

    pipeline = IngestionPipeline(db)
    pipeline.process_document(doc.id, job_id=job.id)
    db.refresh(doc)
    return doc


@router.post("/{document_id}/replace", response_model=DocumentResponse)
async def replace_document(
    document_id: UUID,
    file: UploadFile = File(...),
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    old_doc = db.query(Document).filter(Document.id == document_id).first()
    if not old_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Mark old document as SUPERSEDED
    old_doc.status = DocumentStatus.SUPERSEDED

    filename = file.filename or "updated_document"
    file_content = await file.read()
    new_doc_id = uuid.uuid4()
    storage_key = f"documents/{new_doc_id}/{filename}"

    import io
    storage = get_storage_provider()
    storage.upload(io.BytesIO(file_content), storage_key)

    new_doc = Document(
        id=new_doc_id,
        collection_id=old_doc.collection_id,
        uploaded_by=current_admin.id,
        title=old_doc.title,
        original_filename=filename,
        mime_type=file.content_type or "application/octet-stream",
        storage_key=storage_key,
        file_size=len(file_content),
        status=DocumentStatus.UPLOADED,
        version=old_doc.version + 1,
        parent_document_id=old_doc.id
    )
    db.add(new_doc)
    db.commit()

    pipeline = IngestionPipeline(db)
    pipeline.process_document(new_doc.id)
    db.refresh(new_doc)

    return new_doc
