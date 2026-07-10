"""HTTP middleware and exception handlers."""

import logging
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def install_error_handlers(app: FastAPI) -> None:
    """Register production-safe JSON error handlers."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"error": {"message": exc.detail, "type": "http_error"}})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"error": {"message": "Validation failed", "type": "validation_error", "details": exc.errors()}})

    @app.middleware("http")
    async def unhandled_exception_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
        request_id = request.headers.get("x-request-id", str(uuid4()))
        try:
            response = await call_next(request)
            response.headers["x-request-id"] = request_id
            return response
        except Exception:
            logger.exception("unhandled request error", extra={"request_id": request_id})
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": {"message": "Internal server error", "type": "internal_error", "request_id": request_id}})
