"""Maze puzzle engine architecture."""

from __future__ import annotations

from typing import Any, Mapping

from .base import BasePuzzleEngine, PuzzleEngineMetadata, PuzzleRequest


class MazeEngine(BasePuzzleEngine):
    """Architecture-only engine for maze puzzle planning."""

    puzzle_type = "maze"

    def __init__(self) -> None:
        super().__init__(
            PuzzleEngineMetadata(
                engine_id="maze-engine-v1",
                name="Maze Engine",
                supported_difficulties=("easy", "medium", "hard"),
                supported_age_groups=("kids", "adults"),
                capabilities={"supports_solution_path": True, "generates_content": False},
            )
        )

    def planning_steps(self, request: PuzzleRequest) -> tuple[str, ...]:
        return (
            "select_grid_dimensions",
            "plan_start_and_finish_points",
            "reserve_solution_path_layer",
            "prepare_rendering_contract",
        )

    def blueprint_metadata(self, request: PuzzleRequest) -> Mapping[str, Any]:
        return {"requires_grid": True, "requires_answer_page": True}
