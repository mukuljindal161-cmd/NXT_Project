from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "app_name": settings.APP_NAME,
        "env": settings.APP_ENV
    }


@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    health_status = {
        "status": "ok",
        "components": {
            "database": "ok",
            "ai_provider": "ok",
            "storage": "ok"
        }
    }

    # Test Database
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        health_status["components"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    # Test Storage
    try:
        from app.services.storage import get_storage_provider
        storage = get_storage_provider()
        health_status["components"]["storage"] = "ok"
    except Exception as e:
        health_status["components"]["storage"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    return health_status
