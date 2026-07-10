"""Settings API endpoints."""

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("")
def read_settings() -> dict[str, object]:
    """Return safe, non-secret runtime settings."""
    return get_settings().safe_public_settings
