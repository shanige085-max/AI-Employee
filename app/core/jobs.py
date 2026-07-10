"""Background job manager for application lifecycle tasks."""

import asyncio
import logging
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)
JobCallable = Callable[[], Awaitable[None]]


class BackgroundJobManager:
    """Manage cooperative asyncio background jobs."""

    def __init__(self) -> None:
        self._tasks: set[asyncio.Task[None]] = set()

    def start(self, name: str, job: JobCallable, interval_seconds: float) -> None:
        """Start a recurring job if it is not already running."""
        if any(task.get_name() == name for task in self._tasks):
            return
        task = asyncio.create_task(self._run_forever(name, job, interval_seconds), name=name)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        logger.info("started background job %s", name)

    async def _run_forever(self, name: str, job: JobCallable, interval_seconds: float) -> None:
        while True:
            try:
                await job()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("background job %s failed", name)
            await asyncio.sleep(interval_seconds)

    async def stop(self) -> None:
        """Cancel all active jobs and wait for shutdown."""
        if not self._tasks:
            return
        for task in list(self._tasks):
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        logger.info("stopped background jobs")

    @property
    def active_jobs(self) -> list[str]:
        """Return active job names."""
        return sorted(task.get_name() for task in self._tasks if not task.done())


job_manager = BackgroundJobManager()


async def heartbeat_job() -> None:
    """Default lightweight heartbeat job."""
    logger.debug("background heartbeat")
