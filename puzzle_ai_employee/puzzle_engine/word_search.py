"""Word search puzzle engine architecture."""

from __future__ import annotations

from typing import Any, Mapping

from .base import BasePuzzleEngine, PuzzleEngineMetadata, PuzzleRequest


class WordSearchEngine(BasePuzzleEngine):
    """Architecture-only engine for word search puzzle planning."""

    puzzle_type = "word_search"

    def __init__(self) -> None:
        super().__init__(
            PuzzleEngineMetadata(
                engine_id="word-search-engine-v1",
                name="Word Search Engine",
                supported_difficulties=("easy", "medium", "hard"),
                supported_age_groups=("kids", "adults"),
                capabilities={"supports_word_bank": True, "generates_content": False},
            )
        )

    def planning_steps(self, request: PuzzleRequest) -> tuple[str, ...]:
        return (
            "define_word_bank_contract",
            "select_grid_dimensions",
            "plan_word_placement_rules",
            "prepare_solution_overlay_contract",
        )

    def blueprint_metadata(self, request: PuzzleRequest) -> Mapping[str, Any]:
        return {"requires_word_bank": True, "requires_answer_page": True}
