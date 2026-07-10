"""Base abstractions for PuzzleAI puzzle engines."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Mapping
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class PuzzleEngineMetadata:
    """Describes a puzzle engine without requiring puzzle generation."""

    engine_id: str
    name: str
    supported_difficulties: tuple[str, ...]
    supported_age_groups: tuple[str, ...]
    capabilities: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PuzzleRequest:
    """Input contract shared by all future puzzle generators."""

    topic: str
    difficulty: str
    age_group: str
    options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PuzzleBlueprint:
    """Architecture-only output describing how a puzzle would be generated later."""

    blueprint_id: str
    engine_id: str
    puzzle_type: str
    request: PuzzleRequest
    steps: tuple[str, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)


class BasePuzzleEngine(ABC):
    """Abstract base class for all puzzle engines.

    Module 3 intentionally provides planning/validation architecture only. Concrete
    subclasses must not generate final puzzle content until generation modules are
    introduced.
    """

    puzzle_type: str

    def __init__(self, metadata: PuzzleEngineMetadata) -> None:
        self._metadata = metadata

    @property
    def metadata(self) -> PuzzleEngineMetadata:
        """Return static metadata for the engine."""

        return self._metadata

    def validate_request(self, request: PuzzleRequest) -> None:
        """Validate common request fields before blueprint creation."""

        if not request.topic.strip():
            raise ValueError("Puzzle topic is required.")
        if request.difficulty not in self.metadata.supported_difficulties:
            raise ValueError(
                f"Difficulty '{request.difficulty}' is not supported by {self.metadata.name}."
            )
        if request.age_group not in self.metadata.supported_age_groups:
            raise ValueError(
                f"Age group '{request.age_group}' is not supported by {self.metadata.name}."
            )

    def create_blueprint(self, request: PuzzleRequest) -> PuzzleBlueprint:
        """Create an architecture-only blueprint for a future puzzle."""

        self.validate_request(request)
        return PuzzleBlueprint(
            blueprint_id=str(uuid4()),
            engine_id=self.metadata.engine_id,
            puzzle_type=self.puzzle_type,
            request=request,
            steps=self.planning_steps(request),
            metadata=self.blueprint_metadata(request),
        )

    @abstractmethod
    def planning_steps(self, request: PuzzleRequest) -> tuple[str, ...]:
        """Return high-level future generation steps for this puzzle type."""

    def blueprint_metadata(self, request: PuzzleRequest) -> Mapping[str, Any]:
        """Return optional engine-specific metadata for testable blueprints."""

        return {}
