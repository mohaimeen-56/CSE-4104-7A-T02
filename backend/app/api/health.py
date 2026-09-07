from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health_check(db: Session = Depends(get_db)):
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {type(e).__name__}"

    ai_configured = bool(
        (settings.AI_PROVIDER == "gemini" and settings.GEMINI_API_KEY) or
        (settings.AI_PROVIDER == "openai" and settings.OPENAI_API_KEY) or
        (settings.AI_PROVIDER == "deepseek" and settings.DEEPSEEK_API_KEY) or
        settings.AI_PROVIDER == "grounded"
    )

    is_healthy = db_status == "healthy"
    payload = {
        "status": "healthy" if is_healthy else "degraded",
        "project": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "ai_provider": settings.AI_PROVIDER,
        "ai_configured": ai_configured,
    }
    return JSONResponse(
        status_code=200 if is_healthy else 503,
        content=payload,
    )
