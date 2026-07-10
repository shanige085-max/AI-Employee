"""Crossword puzzle engine architecture."""

from __future__ import annotations

from typing import Any, Mapping

from .base import BasePuzzleEngine, PuzzleEngineMetadata, PuzzleRequest


class CrosswordEngine(BasePuzzleEngine):
    """Architecture-only engine for crossword puzzle planning."""

    puzzle_type = "crossword"

    def __init__(self) -> None:
        super().__init__(
            PuzzleEngineMetadata(
                engine_id="crossword-engine-v1",
                name="Crossword Engine",
                supported_difficulties=("easy", "medium", "hard"),
                supported_age_groups=("kids", "adults"),
                capabilities={"supports_clues": True, "generates_content": False},
            )
        )

    def planning_steps(self, request: PuzzleRequest) -> tuple[str, ...]:
        return (
            "define_answer_and_clue_contract",
            "select_grid_dimensions",
            "plan_intersections",
            "prepare_numbering_and_solution_contract",
        )

    def blueprint_metadata(self, request: PuzzleRequest) -> Mapping[str, Any]:
        return {"requires_clues": True, "requires_answer_page": True}
