"""Health check API endpoints."""

from fastapi import APIRouter
from sqlalchemy import text

from app.core.constants import HEALTH_STATUS_OK
from app.db.session import SessionLocal

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health() -> dict[str, str]:
    """Return application liveness status."""
    return {"status": HEALTH_STATUS_OK}


@router.get("/ready")
def readiness() -> dict[str, str]:
    """Return readiness status after checking database connectivity."""
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {"status": HEALTH_STATUS_OK, "database": HEALTH_STATUS_OK}
