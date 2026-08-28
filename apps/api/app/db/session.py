import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.config import settings

logger = logging.getLogger("rag_db")


def create_resilient_engine():
    db_url = settings.DATABASE_URL
    try:
        # Test connection if PostgreSQL
        if "postgresql" in db_url:
            test_engine = create_engine(db_url, pool_pre_ping=True, connect_args={"connect_timeout": 2})
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to PostgreSQL database.")
            return test_engine
    except Exception as e:
        logger.warning(
            f"Could not connect to PostgreSQL at '{db_url}' ({e}). Falling back to local SQLite database."
        )

    # Resolve absolute path for college_rag.db so it is unified across all directories
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    db_path = os.path.join(base_dir, "college_rag.db").replace("\\", "/")
    sqlite_url = f"sqlite:///{db_path}"
    return create_engine(sqlite_url, connect_args={"check_same_thread": False})


engine = create_resilient_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
