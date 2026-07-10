import json
from pathlib import Path

from puzzleai.maze_book import BOOK_SIZES, Margins, MazeBookConfig, generate_book, generate_unique_mazes


def test_generated_mazes_are_unique_and_balanced():
    config = MazeBookConfig(maze_count=16, min_grid_size=9, max_grid_size=17, seed="unique-test")
    mazes = generate_unique_mazes(config)
    fingerprints = [m.fingerprint for m in mazes]
    assert len(fingerprints) == len(set(fingerprints))
    assert {m.difficulty for m in mazes} == {"easy", "medium", "hard", "expert"}
    assert all(m.solution for m in mazes)
    assert mazes[0].width <= mazes[-1].width


def test_book_size_and_margins_are_configurable():
    config = MazeBookConfig(book_size="6 x 9", margins=Margins(top=0.5, bottom=0.5, inner=0.8, outer=0.4))
    assert config.page_size_points() == BOOK_SIZES["6 x 9"]
    assert config.margins.points()["inner"] == 57.6


def test_generate_book_writes_all_required_assets(tmp_path: Path):
    config = MazeBookConfig(
        title="Test Maze Book",
        maze_count=3,
        min_grid_size=7,
        max_grid_size=9,
        seed="asset-test",
        storage_dir=tmp_path,
        cover_style="minimal",
    )
    metadata = generate_book(config)
    book_dir = tmp_path / metadata["book_id"]
    assert (book_dir / "book.pdf").is_file()
    assert (book_dir / "cover.jpg").is_file()
    assert (book_dir / "thumbnail.jpg").is_file()
    metadata_path = book_dir / "metadata.json"
    assert metadata_path.is_file()
    saved = json.loads(metadata_path.read_text())
    assert saved["maze_count"] == 3
    assert len(saved["unique_fingerprints"]) == len(set(saved["unique_fingerprints"]))
    assert saved["assets"]["pdf"].endswith("book.pdf")
