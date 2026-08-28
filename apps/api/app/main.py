from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.db.base import Base
from app.db.session import engine
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables on startup if not present
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            # Try to create pgvector extension if postgres
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()
            except Exception:
                pass
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Database startup connection notice: {e}")
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
