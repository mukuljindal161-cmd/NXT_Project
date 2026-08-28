from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Message, Citation, Feedback, User
from app.schemas import CitationResponse, FeedbackCreate, FeedbackResponse
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/messages", tags=["Messages & Citations"])


@router.get("/{message_id}/citations", response_model=List[CitationResponse])
def get_message_citations(
    message_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    return msg.citations


@router.post("/{message_id}/feedback", response_model=FeedbackResponse)
def submit_message_feedback(
    message_id: UUID,
    payload: FeedbackCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    # Check if already submitted feedback
    existing = db.query(Feedback).filter(Feedback.message_id == message_id, Feedback.user_id == current_user.id).first()
    if existing:
        existing.rating = payload.rating
        existing.comment = payload.comment
        db.commit()
        db.refresh(existing)
        return existing

    fb = Feedback(
        message_id=message_id,
        user_id=current_user.id,
        rating=payload.rating,
        comment=payload.comment
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb
