from __future__ import annotations

import random
from dataclasses import dataclass

from .models import Cell, Maze, MazeDifficulty, SUPPORTED_GRID_SIZES
from .solver import MazeSolver


@dataclass(frozen=True, slots=True)
class MazeGenerator:
    """Fast iterative depth-first perfect-maze generator."""

    solver: MazeSolver = MazeSolver()

    def generate(
        self,
        size: int,
        difficulty: MazeDifficulty | str = MazeDifficulty.MEDIUM,
        seed: int | None = None,
    ) -> Maze:
        if size not in SUPPORTED_GRID_SIZES:
            raise ValueError(f"unsupported maze size {size}; expected one of {SUPPORTED_GRID_SIZES}")
        difficulty = MazeDifficulty(difficulty)
        rng = random.Random(seed)

        start = self._start_for(difficulty, size)
        end = self._end_for(difficulty, size)
        visited = {start}
        stack = [start]
        passages: set[tuple[Cell, Cell]] = set()

        while stack:
            current = stack[-1]
            candidates = [cell for cell in current.neighbors(size) if cell not in visited]
            if not candidates:
                stack.pop()
                continue
            nxt = self._choose_neighbor(candidates, current, end, difficulty, rng)
            visited.add(nxt)
            passages.add((current, nxt))
            stack.append(nxt)

        maze = Maze(size, difficulty, frozenset(passages), start, end, seed)
        if not self.solver.has_exactly_one_solution(maze):
            raise RuntimeError("generated maze failed uniqueness verification")
        return maze

    @staticmethod
    def _start_for(difficulty: MazeDifficulty, size: int) -> Cell:
        return Cell(size // 2, 0) if difficulty is MazeDifficulty.EASY else Cell(0, 0)

    @staticmethod
    def _end_for(difficulty: MazeDifficulty, size: int) -> Cell:
        return Cell(size // 2, size - 1) if difficulty is MazeDifficulty.EASY else Cell(size - 1, size - 1)

    @staticmethod
    def _choose_neighbor(
        candidates: list[Cell],
        current: Cell,
        end: Cell,
        difficulty: MazeDifficulty,
        rng: random.Random,
    ) -> Cell:
        if difficulty is MazeDifficulty.HARD and len(candidates) > 1:
            # Prefer moves away from the exit early, producing longer, twistier solutions.
            return max(candidates, key=lambda c: (abs(c.row - end.row) + abs(c.col - end.col), rng.random()))
        if difficulty is MazeDifficulty.EASY and len(candidates) > 1:
            # Mildly bias toward the exit for shorter, more approachable paths.
            return min(candidates, key=lambda c: (abs(c.row - end.row) + abs(c.col - end.col), rng.random()))
        return rng.choice(candidates)
