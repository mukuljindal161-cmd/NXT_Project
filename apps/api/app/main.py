import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models import User, UserRole, Collection, Document, DocumentChunk, DocumentStatus
from app.security.passwords import get_password_hash
from app.ai.providers import get_ai_provider
from app.middleware.logging import StructuredLoggingMiddleware
from app.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)

# API Routers
from app.api.v1.auth import router as auth_router
from app.api.v1.conversations import router as conversations_router
from app.api.v1.chat import router as chat_router
from app.api.v1.messages import router as messages_router
from app.api.v1.health import router as health_router
from app.api.v1.admin.documents import router as admin_documents_router
from app.api.v1.admin.collections import router as admin_collections_router
from app.api.v1.admin.jobs import router as admin_jobs_router
from app.api.v1.admin.analytics import router as admin_analytics_router

logger = logging.getLogger(__name__)


def auto_seed_if_empty():
    """Automatically seed demo users and sample documents on first deployment if DB is empty."""
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            logger.info("Fresh database detected. Auto-seeding initial users and knowledge base...")
            # 1. Admin
            admin = User(
                email="admin@example.edu",
                password_hash=get_password_hash("AdminPass123!"),
                full_name="Dr. Eleanor Vance (Dean of Academics)",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin)

            # 2. Student
            student = User(
                email="student@example.edu",
                password_hash=get_password_hash("StudentPass123!"),
                full_name="Alex Morgan (Undergraduate)",
                role=UserRole.STUDENT,
                is_active=True
            )
            db.add(student)
            db.commit()
            db.refresh(admin)

            # 3. Collection
            col = Collection(
                name="Academic Regulations & Fees",
                slug="academics-fees",
                department="Academic Affairs",
                description="Curriculum policies, grading scales, examination rules, and tuition schedules.",
                is_active=True
            )
            db.add(col)
            db.commit()
            db.refresh(col)

            # 4. Document
            doc = Document(
                collection_id=col.id,
                uploaded_by=admin.id,
                title="Academic Calendar and Fee Regulation Manual 2026-27",
                original_filename="Academic_Fees_Manual_2026.pdf",
                mime_type="application/pdf",
                storage_key="sample_docs/Academic_Fees_Manual_2026.pdf",
                file_size=1024 * 50,
                status=DocumentStatus.READY,
                version=1,
                page_count=2,
                chunk_count=2
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)

            ai_provider = get_ai_provider()
            chunks_text = [
                (1, "Academic Deadlines & Schedule", "For the Academic Year 2026-27, the Fall semester commences on August 10, 2026. Course registration and add/drop period closes on August 24, 2026. Mid-term examinations will take place from October 12 to October 18, 2026. Final semester examinations are scheduled between December 1 and December 15, 2026."),
                (2, "Tuition Fee Structure and Penalties", "The semester tuition fee for undergraduate engineering and science programs is $4,500 per term. The final date for fee payment without penalty is September 15, 2026. Payments submitted between September 16 and September 25 incur a late fee penalty of $50. Accounts unpaid by September 26 will result in temporary course deregistration.")
            ]

            for idx, (pg, sec, content) in enumerate(chunks_text):
                emb = ai_provider.embed(content)
                chunk = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=idx,
                    content=content,
                    page_number=pg,
                    section_title=sec,
                    token_count=len(content) // 4,
                    embedding=emb,
                    metadata_json={"page": pg, "section": sec}
                )
                db.add(chunk)
            db.commit()
            logger.info("Auto-seed completed successfully.")
    except Exception as e:
        logger.warning(f"Notice on auto-seed: {e}")
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables on startup if not present
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()
            except Exception:
                pass
        Base.metadata.create_all(bind=engine)
        auto_seed_if_empty()
    except Exception as e:
        logger.warning(f"Database startup notice: {e}")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Production-grade RAG College Information Assistant backend API",
    docs_url="/docs" if settings.ENABLE_OPENAPI else None,
    redoc_url="/redoc" if settings.ENABLE_OPENAPI else None,
    openapi_url="/openapi.json" if settings.ENABLE_OPENAPI else None,
    lifespan=lifespan
)

# Middleware
app.add_middleware(StructuredLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app|http://localhost:\d+|http://127.0.0.1:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Include Routers with /api/v1 prefix
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(conversations_router, prefix=settings.API_V1_STR)
app.include_router(chat_router, prefix=settings.API_V1_STR)
app.include_router(messages_router, prefix=settings.API_V1_STR)
app.include_router(admin_documents_router, prefix=settings.API_V1_STR)
app.include_router(admin_collections_router, prefix=settings.API_V1_STR)
app.include_router(admin_jobs_router, prefix=settings.API_V1_STR)
app.include_router(admin_analytics_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "documentation": "/docs",
        "health": f"{settings.API_V1_STR}/health"
    }
