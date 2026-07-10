"""In-memory AI task queue foundation with retry-aware error recovery."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from typing import Any, Deque
from dataclasses import dataclass, field
from uuid import uuid4

from .status import JobRecord, JobStatus

TaskCallable = Callable[[JobRecord], Any]


@dataclass(slots=True)
class AITask:
    """A queued AI task and its execution callback."""

    name: str
    handler: TaskCallable
    payload: dict[str, Any] = field(default_factory=dict)
    record: JobRecord = field(default_factory=lambda: JobRecord(job_id=str(uuid4())))


class ErrorRecoveryPolicy:
    """Determines whether failed tasks should be retried."""

    def should_retry(self, record: JobRecord, error: Exception) -> bool:
        """Return True when the job has remaining retry attempts."""

        return record.attempts < record.max_attempts


class AITaskQueue:
    """Simple unit-test-ready queue for future AI workflow orchestration."""

    def __init__(self, recovery_policy: ErrorRecoveryPolicy | None = None) -> None:
        self._queue: Deque[AITask] = deque()
        self._jobs: dict[str, AITask] = {}
        self._recovery_policy = recovery_policy or ErrorRecoveryPolicy()

    def enqueue(self, name: str, handler: TaskCallable, payload: dict[str, Any] | None = None) -> JobRecord:
        """Queue a task and return its status record."""

        task = AITask(name=name, handler=handler, payload=payload or {})
        self._queue.append(task)
        self._jobs[task.record.job_id] = task
        return task.record

    def get_job(self, job_id: str) -> JobRecord:
        """Return current job status by identifier."""

        return self._jobs[job_id].record

    def run_next(self) -> JobRecord | None:
        """Run the next queued task synchronously for deterministic tests."""

        if not self._queue:
            return None
        task = self._queue.popleft()
        record = task.record
        record.attempts += 1
        record.transition(JobStatus.RUNNING)
        try:
            task.handler(record)
        except Exception as exc:  # noqa: BLE001 - intentional queue boundary for recovery.
            if self._recovery_policy.should_retry(record, exc):
                record.transition(JobStatus.RETRYING, error=str(exc))
                self._queue.append(task)
            else:
                record.transition(JobStatus.FAILED, error=str(exc))
            return record

        record.progress.update(record.progress.total, message="Completed")
        record.transition(JobStatus.COMPLETED)
        return record

    def run_all(self) -> tuple[JobRecord, ...]:
        """Run queued tasks until the queue is empty."""

        records: list[JobRecord] = []
        while self._queue:
            record = self.run_next()
            if record is not None:
                records.append(record)
        return tuple(records)
