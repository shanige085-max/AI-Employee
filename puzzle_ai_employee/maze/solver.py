from __future__ import annotations

from collections import deque

from .models import Cell, Maze


class MazeSolver:
    """Solves perfect mazes and verifies the single path from start to end."""

    def solve(self, maze: Maze) -> list[Cell]:
        parents: dict[Cell, Cell | None] = {maze.start: None}
        queue: deque[Cell] = deque([maze.start])

        while queue:
            current = queue.popleft()
            if current == maze.end:
                break
            for neighbor in current.neighbors(maze.size):
                if neighbor not in parents and maze.has_passage(current, neighbor):
                    parents[neighbor] = current
                    queue.append(neighbor)

        if maze.end not in parents:
            raise ValueError("maze has no solution")

        path: list[Cell] = []
        cursor: Cell | None = maze.end
        while cursor is not None:
            path.append(cursor)
            cursor = parents[cursor]
        path.reverse()
        return path

    def has_exactly_one_solution(self, maze: Maze) -> bool:
        # A connected acyclic grid graph has exactly one path between any two cells.
        if len(maze.passages) != maze.cells - 1:
            return False

        seen = {maze.start}
        queue: deque[Cell] = deque([maze.start])
        while queue:
            current = queue.popleft()
            for neighbor in current.neighbors(maze.size):
                if neighbor not in seen and maze.has_passage(current, neighbor):
                    seen.add(neighbor)
                    queue.append(neighbor)
        return len(seen) == maze.cells and bool(self.solve(maze))
