from pathlib import Path

import pytest

from puzzle_ai_employee.maze import MazeDifficulty, MazeGenerator, MazeRenderer, MazeSolver
from puzzle_ai_employee.maze.models import SUPPORTED_GRID_SIZES


def test_generates_supported_sizes_and_unique_solution():
    generator = MazeGenerator()
    solver = MazeSolver()
    for size in SUPPORTED_GRID_SIZES:
        maze = generator.generate(size, MazeDifficulty.MEDIUM, seed=size)
        assert maze.size == size
        assert len(maze.passages) == size * size - 1
        assert solver.has_exactly_one_solution(maze)
        solution = solver.solve(maze)
        assert solution[0] == maze.start
        assert solution[-1] == maze.end


@pytest.mark.parametrize("difficulty", list(MazeDifficulty))
def test_supports_all_difficulties(difficulty):
    maze = MazeGenerator().generate(15, difficulty, seed=123)
    assert maze.difficulty == difficulty
    assert MazeSolver().has_exactly_one_solution(maze)


def test_rejects_unsupported_grid_size():
    with pytest.raises(ValueError):
        MazeGenerator().generate(10)


def test_exports_svg_png_and_pdf_with_solution_pages(tmp_path: Path):
    maze = MazeGenerator().generate(15, MazeDifficulty.EASY, seed=42)
    renderer = MazeRenderer(cell_size=8, margin=4)
    svg = tmp_path / "maze.svg"
    svg_solution = tmp_path / "maze_solution.svg"
    png = tmp_path / "maze.png"
    png_solution = tmp_path / "maze_solution.png"
    pdf = tmp_path / "maze.pdf"
    pdf_solution = tmp_path / "maze_solution.pdf"

    renderer.export_svg(maze, svg)
    renderer.export_svg(maze, svg_solution, include_solution=True)
    renderer.export_png(maze, png)
    renderer.export_png(maze, png_solution, include_solution=True)
    renderer.export_pdf_page(maze, pdf)
    renderer.export_pdf_page(maze, pdf_solution, include_solution=True)

    assert svg.read_text().startswith('<svg xmlns="http://www.w3.org/2000/svg"')
    assert "<polyline" in svg_solution.read_text()
    assert png.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert png_solution.stat().st_size > png.stat().st_size
    assert pdf.read_bytes().startswith(b"%PDF-1.4")
    assert pdf_solution.read_bytes().startswith(b"%PDF-1.4")
