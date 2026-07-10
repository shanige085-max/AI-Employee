"""Book domain model for PuzzleAI publishing workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Mapping


class PublishStatus(StrEnum):
    """Supported publishing lifecycle states."""

    DRAFT = "draft"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    PUBLISHED = "published"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class BookAsset:
    """Represents an optional generated or uploaded book asset."""

    path: Path | None = None
    alt_text: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Book:
    """Book model covering content, assets, SEO, and publishing state."""

    title: str
    subtitle: str
    age_group: str
    topic: str
    difficulty: str
    interior_pages: list[Path] = field(default_factory=list)
    answer_pages: list[Path] = field(default_factory=list)
    cover: BookAsset = field(default_factory=BookAsset)
    seo: Mapping[str, Any] = field(default_factory=dict)
    featured_image: BookAsset = field(default_factory=BookAsset)
    pinterest_image: BookAsset = field(default_factory=BookAsset)
    pdf_path: Path | None = None
    publish_status: PublishStatus = PublishStatus.DRAFT

    def mark_status(self, status: PublishStatus) -> None:
        """Update the publishing status in a controlled way."""

        self.publish_status = status

    def add_interior_page(self, path: Path) -> None:
        """Register an interior page path."""

        self.interior_pages.append(path)

    def add_answer_page(self, path: Path) -> None:
        """Register an answer page path."""

        self.answer_pages.append(path)
