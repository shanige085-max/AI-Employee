import logging
import sys

from app.core.config import settings


def configure_logging() -> None:
    """Configure process-wide structured-enough console logging."""
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )
