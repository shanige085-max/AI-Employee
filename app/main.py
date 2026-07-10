"""FastAPI application factory for PuzzleAI Employee."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.jobs import heartbeat_job, job_manager
from app.core.logging import configure_logging
from app.core.middleware import install_error_handlers
from app.db.session import init_db


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    configure_logging(settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        init_db()
        if settings.background_jobs_enabled:
            job_manager.start("heartbeat", heartbeat_job, settings.background_job_interval_seconds)
        yield
        await job_manager.stop()

    app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
    install_error_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
