import json
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User, Conversation, Message, Citation, MessageRole, MessageStatus
from app.schemas import SendMessageRequest, MessageResponse, QueryRequest
from app.services.rag.orchestrator import RAGOrchestrator, CitationBuilder
from app.dependencies import get_current_active_user

router = APIRouter(tags=["Chat & RAG"])


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
def send_message(
    conversation_id: UUID,
    payload: SendMessageRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # 1. Save student's user message
    user_msg = Message(
        conversation_id=conv.id,
        role=MessageRole.USER,
        content=payload.content,
        status=MessageStatus.COMPLETED
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # If first message, auto-title the conversation
    if conv.title == "New Conversation":
        auto_title = payload.content[:40].strip()
        if len(payload.content) > 40:
            auto_title += "..."
        conv.title = auto_title

    # 2. Retrieve history and execute RAG Orchestrator
    history = db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.created_at.asc()).all()

    orchestrator = RAGOrchestrator(db)
    answer_text, retrieved_chunks = orchestrator.process_query(
        question=payload.content,
        history=history,
        collection_id=payload.collection_id,
        department=payload.department
    )

    # 3. Save assistant message & citations
    assistant_msg = Message(
        conversation_id=conv.id,
        role=MessageRole.ASSISTANT,
        content=answer_text,
        status=MessageStatus.COMPLETED
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    citations = CitationBuilder.build_citations(assistant_msg.id, retrieved_chunks)
    for cit in citations:
        db.add(cit)

    db.commit()
    db.refresh(assistant_msg)

    return assistant_msg


@router.get("/conversations/{conversation_id}/messages/stream")
def stream_conversation_message(
    conversation_id: UUID,
    content: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Save user message
    user_msg = Message(
        conversation_id=conv.id,
        role=MessageRole.USER,
        content=content,
        status=MessageStatus.COMPLETED
    )
    db.add(user_msg)
    db.commit()

    if conv.title == "New Conversation":
        conv.title = (content[:40] + ("..." if len(content) > 40 else "")).strip()
        db.commit()

    history = db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.created_at.asc()).all()
    orchestrator = RAGOrchestrator(db)

    def sse_event_generator():
        accumulated_text = ""
        captured_chunks = []

        for chunk_event in orchestrator.stream_query(question=content, history=history):
            if "event: generation.delta" in chunk_event:
                try:
                    data_str = chunk_event.split("data: ")[1].strip()
                    accumulated_text += json.loads(data_str).get("text", "")
                except Exception:
                    pass
            elif "event: retrieval.completed" in chunk_event:
                try:
                    data_str = chunk_event.split("data: ")[1].strip()
                    captured_chunks = json.loads(data_str).get("chunks", [])
                except Exception:
                    pass

            yield chunk_event

        # Once streaming is complete, persist assistant message
        try:
            assistant_msg = Message(
                conversation_id=conv.id,
                role=MessageRole.ASSISTANT,
                content=accumulated_text or "No response generated.",
                status=MessageStatus.COMPLETED
            )
            db.add(assistant_msg)
            db.commit()
            db.refresh(assistant_msg)

            for idx, c in enumerate(captured_chunks):
                cit = Citation(
                    message_id=assistant_msg.id,
                    document_id=UUID(c["document_id"]) if c.get("document_id") else None,
                    chunk_id=UUID(c["chunk_id"]) if c.get("chunk_id") else None,
                    document_name=c.get("document_name", "Document"),
                    page_number=c.get("page"),
                    similarity_score=float(c.get("similarity", 1.0)),
                    citation_order=idx + 1
                )
                db.add(cit)
            db.commit()
        except Exception:
            db.rollback()

    return StreamingResponse(sse_event_generator(), media_type="text/event-stream")


@router.post("/chat/query")
def chat_query(
    payload: QueryRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    orchestrator = RAGOrchestrator(db)
    answer, chunks = orchestrator.process_query(
        question=payload.content,
        collection_id=payload.collection_id,
        department=payload.department
    )
    citations = [
        {
            "document_id": str(c.document_id),
            "document_name": c.document_title,
            "chunk_id": str(c.chunk_id),
            "page": c.page_number,
            "similarity": c.similarity_score
        }
        for c in chunks
    ]
    return {
        "answer": answer,
        "citations": citations
    }


@router.get("/chat/query/stream")
def chat_query_stream(
    content: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    orchestrator = RAGOrchestrator(db)
    return StreamingResponse(
        orchestrator.stream_query(question=content),
        media_type="text/event-stream"
    )
