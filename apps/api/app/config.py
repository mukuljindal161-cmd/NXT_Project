import json
import os
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Locate root .env
_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
_env_path = os.path.join(_base_dir, ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(_env_path, ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # App
    APP_ENV: str = "development"
    APP_NAME: str = "College RAG Assistant"
    APP_PORT: int = 8000
    WEB_PORT: int = 3000
    API_V1_STR: str = "/api/v1"
    ENABLE_OPENAPI: bool = True

    # Database & Cache
    DATABASE_URL: str = "sqlite:///./college_rag.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "default-dev-secret-key-change-in-production-1234567890"
    SESSION_COOKIE_NAME: str = "college_session"
    SESSION_COOKIE_SECURE: bool = False
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALGORITHM: str = "HS256"

    # AI Configuration
    LLM_PROVIDER: str = "gemini"  # 'gemini' | 'mock'
    LLM_MODEL: str = "gemini-3.6-flash"
    EMBEDDING_PROVIDER: str = "gemini"  # 'gemini' | 'mock'
    EMBEDDING_MODEL: str = "gemini-embedding-001"
    EMBEDDING_DIMENSIONS: int = 3072
    GEMINI_API_KEY: Optional[str] = None

    # Storage
    STORAGE_PROVIDER: str = "local"  # 'local' | 'gcs'
    STORAGE_DIR: str = "./data/storage"
    STORAGE_BUCKET: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    # RAG Parameters
    MAX_UPLOAD_SIZE_MB: int = 25
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 120
    TOP_K: int = 8
    SIMILARITY_THRESHOLD: float = 0.50

    # Feature flags
    ENABLE_HYBRID_SEARCH: bool = False
    ENABLE_RERANKING: bool = False

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",")]
        return v


settings = Settings()
