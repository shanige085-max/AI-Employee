"""Job status and progress primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class JobStatus(StrEnum):
    """AI task queue lifecycle states."""

    PENDING = "pending"
    RUNNING = "running"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class Progress:
    """Tracks percent completion and human-readable progress messages."""

    current: int = 0
    total: int = 1
    message: str = "Pending"

    @property
    def percent(self) -> float:
        """Return completion percentage from 0 to 100."""

        if self.total <= 0:
            return 0.0
        return min(100.0, max(0.0, (self.current / self.total) * 100))

    def update(self, current: int, total: int | None = None, message: str | None = None) -> None:
        """Update progress fields."""

        self.current = current
        if total is not None:
            self.total = total
        if message is not None:
            self.message = message


@dataclass(slots=True)
class JobRecord:
    """Current observable state for a queued task."""

    job_id: str
    status: JobStatus = JobStatus.PENDING
    progress: Progress = field(default_factory=Progress)
    attempts: int = 0
    max_attempts: int = 3
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def transition(self, status: JobStatus, error: str | None = None) -> None:
        """Move the job to a new lifecycle state."""

        self.status = status
        self.error = error
        self.updated_at = datetime.now(UTC)
