from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class MazeDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


SUPPORTED_GRID_SIZES = (15, 20, 25, 30)


@dataclass(frozen=True, slots=True)
class Cell:
    row: int
    col: int

    def neighbors(self, size: int) -> Iterable["Cell"]:
        if self.row > 0:
            yield Cell(self.row - 1, self.col)
        if self.col + 1 < size:
            yield Cell(self.row, self.col + 1)
        if self.row + 1 < size:
            yield Cell(self.row + 1, self.col)
        if self.col > 0:
            yield Cell(self.row, self.col - 1)


@dataclass(frozen=True, slots=True)
class Maze:
    size: int
    difficulty: MazeDifficulty
    passages: frozenset[tuple[Cell, Cell]]
    start: Cell
    end: Cell
    seed: int | None = None

    def has_passage(self, a: Cell, b: Cell) -> bool:
        return (a, b) in self.passages or (b, a) in self.passages

    @property
    def cells(self) -> int:
        return self.size * self.size
