from datetime import datetime
from typing import List, Optional, Any, Dict
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from app.models import UserRole, DocumentStatus, MessageRole, MessageStatus, JobStatus, FeedbackRating


# Generic Response Wrappers
class APIResponse(BaseModel):
    data: Any
    request_id: Optional[str] = None


class APIErrorDetail(BaseModel):
    code: str
    message: str
    request_id: Optional[str] = None


class APIErrorResponse(BaseModel):
    error: APIErrorDetail


# Auth Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Collection Schemas
class CollectionCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    slug: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None


class CollectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None


class CollectionResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    department: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Document Schemas
class DocumentResponse(BaseModel):
    id: UUID
    collection_id: Optional[UUID] = None
    uploaded_by: Optional[UUID] = None
    title: str
    original_filename: str
    mime_type: str
    file_size: int
    checksum: Optional[str] = None
    status: DocumentStatus
    version: int
    parent_document_id: Optional[UUID] = None
    page_count: Optional[int] = None
    chunk_count: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    items: List[DocumentResponse]
    total: int
    page: int
    page_size: int


# Citation & Chat Schemas
class CitationResponse(BaseModel):
    id: Optional[UUID] = None
    document_id: Optional[UUID] = None
    document_name: str
    chunk_id: Optional[UUID] = None
    page_number: Optional[int] = None
    similarity_score: float
    citation_order: int = 1

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    status: MessageStatus
    created_at: datetime
    citations: List[CitationResponse] = []

    class Config:
        from_attributes = True


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1)
    collection_id: Optional[UUID] = None
    department: Optional[str] = None


class QueryRequest(BaseModel):
    content: str = Field(min_length=1)
    collection_id: Optional[UUID] = None
    department: Optional[str] = None


class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"


class ConversationUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class ConversationResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[MessageResponse]] = None

    class Config:
        from_attributes = True


class FeedbackCreate(BaseModel):
    rating: FeedbackRating
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: UUID
    message_id: UUID
    user_id: UUID
    rating: FeedbackRating
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Job Schemas
class JobResponse(BaseModel):
    id: UUID
    type: str
    status: JobStatus
    user_id: Optional[UUID] = None
    entity_id: Optional[UUID] = None
    progress: int
    message: Optional[str] = None
    error_message: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Analytics Schemas
class AnalyticsOverviewResponse(BaseModel):
    users: int
    documents: int
    ready_documents: int
    processing_documents: int
    failed_documents: int
    questions: int
    failed_jobs: int
    average_retrieval_score: float
