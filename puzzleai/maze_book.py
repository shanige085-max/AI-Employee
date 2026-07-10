"""Production-oriented maze book generator for PuzzleAI Employee.

The module generates unique maze interiors, covers, thumbnails, and metadata
under ``storage/books/`` without touching WordPress or Pinterest integrations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Literal


BookSizeName = Literal["US Letter", "A4", "8.5 x 11", "6 x 9"]
CoverStyle = Literal["classic", "modern", "kids", "minimal"]

BOOK_SIZES: dict[str, tuple[float, float]] = {
    "US Letter": (612, 792),
    "8.5 x 11": (612, 792),
    "A4": (595.2756, 841.8898),
    "6 x 9": (432, 648),
}

POINTS_PER_INCH = 72
DEFAULT_STORAGE = Path("storage/books")


@dataclass(frozen=True)
class Margins:
    top: float = 0.6
    bottom: float = 0.65
    inner: float = 0.75
    outer: float = 0.55

    def points(self) -> dict[str, float]:
        return {k: v * POINTS_PER_INCH for k, v in asdict(self).items()}


@dataclass(frozen=True)
class MazeBookConfig:
    title: str = "Maze Challenge Book"
    subtitle: str = "Unique hand-crafted style mazes for focus and fun"
    author: str = "PuzzleAI Employee"
    publisher: str = "PuzzleAI"
    copyright_holder: str = "PuzzleAI"
    book_size: BookSizeName = "US Letter"
    margins: Margins = field(default_factory=Margins)
    font_name: str = "Helvetica"
    cover_style: CoverStyle = "modern"
    maze_count: int = 40
    min_grid_size: int = 13
    max_grid_size: int = 29
    seed: str | None = None
    storage_dir: Path = DEFAULT_STORAGE

    def page_size_points(self) -> tuple[float, float]:
        if self.book_size not in BOOK_SIZES:
            raise ValueError(f"Unsupported book size: {self.book_size}")
        return BOOK_SIZES[self.book_size]

    def validate(self) -> None:
        if self.maze_count < 1:
            raise ValueError("maze_count must be at least 1")
        if self.min_grid_size < 7 or self.max_grid_size < self.min_grid_size:
            raise ValueError("grid sizes must be >= 7 and max >= min")
        for value in asdict(self.margins).values():
            if value < 0.25 or value > 2.0:
                raise ValueError("margins must be between 0.25 and 2.0 inches")


@dataclass(frozen=True)
class Maze:
    width: int
    height: int
    walls: frozenset[tuple[tuple[int, int], tuple[int, int]]]
    start: tuple[int, int]
    end: tuple[int, int]
    solution: tuple[tuple[int, int], ...]
    fingerprint: str
    difficulty: str
    branch_count: int
    dead_ends: int


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "maze-book"


def _edge(a: tuple[int, int], b: tuple[int, int]) -> tuple[tuple[int, int], tuple[int, int]]:
    return tuple(sorted((a, b)))  # type: ignore[return-value]


def _neighbors(cell: tuple[int, int], width: int, height: int) -> Iterable[tuple[int, int]]:
    x, y = cell
    if x > 0:
        yield (x - 1, y)
    if x < width - 1:
        yield (x + 1, y)
    if y > 0:
        yield (x, y - 1)
    if y < height - 1:
        yield (x, y + 1)


def _longest_path(open_edges: set, width: int, height: int, start: tuple[int, int]) -> list[tuple[int, int]]:
    parent = {start: None}
    stack = [start]
    order = []
    while stack:
        cell = stack.pop()
        order.append(cell)
        for n in _neighbors(cell, width, height):
            if n not in parent and _edge(cell, n) in open_edges:
                parent[n] = cell
                stack.append(n)
    far = max(order, key=lambda c: abs(c[0] - start[0]) + abs(c[1] - start[1]))
    path = []
    while far is not None:
        path.append(far)
        far = parent[far]
    return list(reversed(path))


def generate_maze(width: int, height: int, rng: random.Random, target: str) -> Maze:
    """Generate one perfect maze with loops tuned by target difficulty."""
    start = (0, 0)
    visited = {start}
    stack = [start]
    open_edges: set[tuple[tuple[int, int], tuple[int, int]]] = set()

    while stack:
        cell = stack[-1]
        choices = [n for n in _neighbors(cell, width, height) if n not in visited]
        if choices:
            # Bias toward longer corridors for better maze feel without making all mazes identical.
            last = stack[-2] if len(stack) > 1 else None
            if last and rng.random() < 0.58:
                dx, dy = cell[0] - last[0], cell[1] - last[1]
                straight = (cell[0] + dx, cell[1] + dy)
                if straight in choices:
                    nxt = straight
                else:
                    nxt = rng.choice(choices)
            else:
                nxt = rng.choice(choices)
            open_edges.add(_edge(cell, nxt))
            visited.add(nxt)
            stack.append(nxt)
        else:
            stack.pop()

    loop_rates = {"easy": 0.015, "medium": 0.035, "hard": 0.055, "expert": 0.075}
    for y in range(height):
        for x in range(width):
            for n in ((x + 1, y), (x, y + 1)):
                if n[0] < width and n[1] < height and _edge((x, y), n) not in open_edges:
                    if rng.random() < loop_rates[target]:
                        open_edges.add(_edge((x, y), n))

    solution = _longest_path(open_edges, width, height, start)
    end = solution[-1]
    degrees = [sum(1 for n in _neighbors((x, y), width, height) if _edge((x, y), n) in open_edges) for y in range(height) for x in range(width)]
    dead_ends = sum(1 for d in degrees if d == 1)
    branches = sum(1 for d in degrees if d >= 3)
    serial = f"{width}x{height}|{sorted(open_edges)}|{start}|{end}"
    fingerprint = hashlib.sha256(serial.encode()).hexdigest()
    return Maze(width, height, frozenset(open_edges), start, end, tuple(solution), fingerprint, target, branches, dead_ends)


def generate_unique_mazes(config: MazeBookConfig) -> list[Maze]:
    config.validate()
    rng = random.Random(config.seed or uuid.uuid4().hex)
    seen: set[str] = set()
    mazes: list[Maze] = []
    bands = ["easy", "medium", "hard", "expert"]
    attempts = 0
    while len(mazes) < config.maze_count:
        attempts += 1
        if attempts > config.maze_count * 75:
            raise RuntimeError("Unable to generate enough unique mazes")
        idx = len(mazes)
        target = bands[min(3, math.floor(idx / max(1, config.maze_count) * 4))]
        span = config.max_grid_size - config.min_grid_size
        base = config.min_grid_size + round(span * idx / max(1, config.maze_count - 1))
        size = max(7, base + rng.choice([-2, 0, 2]))
        if size % 2 == 0:
            size += 1
        maze = generate_maze(size, size, rng, target)
        if maze.fingerprint not in seen:
            seen.add(maze.fingerprint)
            mazes.append(maze)
    return mazes


def _pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _maze_pdf_commands(maze: Maze, x: float, y: float, size: float, show_solution: bool = False) -> list[str]:
    cell = size / max(maze.width, maze.height)
    cmds = ["0 0 0 RG", f"{max(0.65, cell * 0.06):.2f} w"]
    for gy in range(maze.height):
        for gx in range(maze.width):
            left, bottom = x + gx * cell, y + (maze.height - gy - 1) * cell
            def line(x1, y1, x2, y2):
                cmds.append(f"{x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S")
            if gx == 0:
                line(left, bottom, left, bottom + cell)
            if gy == 0:
                line(left, bottom + cell, left + cell, bottom + cell)
            if _edge((gx, gy), (gx + 1, gy)) not in maze.walls:
                line(left + cell, bottom, left + cell, bottom + cell)
            if _edge((gx, gy), (gx, gy + 1)) not in maze.walls:
                line(left, bottom, left + cell, bottom)
    # start/end markers
    cmds.append("0 0.55 0 rg")
    cmds.append(f"{x + cell/2:.2f} {y + size - cell/2:.2f} {cell*.18:.2f} 0 360 re f")
    cmds.append("0.85 0 0 rg")
    ex, ey = maze.end
    cmds.append(f"{x + ex*cell + cell*.32:.2f} {y + (maze.height-ey-1)*cell + cell*.32:.2f} {cell*.36:.2f} {cell*.36:.2f} re f")
    if show_solution:
        cmds.append("0.14 0.39 0.92 RG")
        cmds.append(f"{max(1.0, cell * 0.12):.2f} w")
        pts = [(x + px * cell + cell / 2, y + (maze.height - py - 1) * cell + cell / 2) for px, py in maze.solution]
        for a, b in zip(pts, pts[1:]):
            cmds.append(f"{a[0]:.2f} {a[1]:.2f} m {b[0]:.2f} {b[1]:.2f} l S")
    return cmds


def _text(x: float, y: float, text: str, size: int = 12, align: str = "left") -> str:
    escaped = _pdf_escape(text)
    if align == "center":
        # Approximate centering with standard Type1 font metrics.
        x = x - (len(text) * size * 0.25)
    return f"BT /F1 {size} Tf {x:.2f} {y:.2f} Td ({escaped}) Tj ET"


def _page_number_cmd(page_num: int, width: float, margin_bottom: float) -> str:
    return _text(width / 2, margin_bottom / 2, str(page_num), 9, "center")


def _write_minimal_pdf(path: Path, page_size: tuple[float, float], pages: list[list[str]], font_name: str) -> None:
    width, height = page_size
    objects: list[bytes] = [b"<< /Type /Catalog /Pages 2 0 R >>"]
    kids = " ".join(f"{3 + i*2} 0 R" for i in range(len(pages)))
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>".encode())
    for i, commands in enumerate(pages):
        page_obj = 3 + i*2
        content_obj = page_obj + 1
        objects.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width:.2f} {height:.2f}] /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /{font_name} >> >> >> /Contents {content_obj} 0 R >>".encode())
        stream = "\n".join(commands).encode()
        objects.append(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream")
    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for num, obj in enumerate(objects, 1):
        offsets.append(len(out))
        out.extend(f"{num} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(out)
    out.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode())
    out.extend(f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    path.write_bytes(out)


def write_pdf(path: Path, config: MazeBookConfig, mazes: list[Maze]) -> None:
    width, height = config.page_size_points()
    m = config.margins.points()
    pages: list[list[str]] = []
    page = 1
    pages.append([_text(width/2, height*.67, config.title, 26, "center"), _text(width/2, height*.62, config.subtitle, 14, "center"), _text(width/2, height*.55, f"By {config.author}", 14, "center"), _page_number_cmd(page, width, m["bottom"])]); page += 1
    year = datetime.now(timezone.utc).year
    pages.append([_text(m["inner"], height-m["top"]-20, "Copyright", 20), _text(m["inner"], height-m["top"]-55, config.title, 10), _text(m["inner"], height-m["top"]-71, f"Copyright © {year} {config.copyright_holder}.", 10), _text(m["inner"], height-m["top"]-87, "All rights reserved.", 10), _text(m["inner"], height-m["top"]-103, "Generated by PuzzleAI Employee.", 10), _page_number_cmd(page, width, m["bottom"])]); page += 1
    usable_w = width - m["inner"] - m["outer"]
    usable_h = height - m["top"] - m["bottom"] - 46
    box = min(usable_w, usable_h)
    for i, maze in enumerate(mazes, 1):
        cmds = [_text(m["inner"], height-m["top"], f"Maze {i}: {maze.difficulty.title()}", 15)]
        cmds += _maze_pdf_commands(maze, m["inner"] + (usable_w-box)/2, m["bottom"]+24, box)
        cmds.append(_page_number_cmd(page, width, m["bottom"])); pages.append(cmds); page += 1
    pages.append([_text(width/2, height*.72, "Solutions", 22, "center"), _page_number_cmd(page, width, m["bottom"])]); page += 1
    for i, maze in enumerate(mazes, 1):
        cmds = [_text(m["inner"], height-m["top"], f"Solution {i}", 12)] + _maze_pdf_commands(maze, m["inner"] + (usable_w-box)/2, m["bottom"]+24, box, True)
        cmds.append(_page_number_cmd(page, width, m["bottom"])); pages.append(cmds); page += 1
    pages.append([_text(width/2, height*.70, "More Free Puzzle Books", 24, "center"), _text(width/2, height*.64, "Visit PuzzleAI for new mazes, word searches, logic puzzles, and activity books.", 12, "center"), _page_number_cmd(page, width, m["bottom"])])
    _write_minimal_pdf(path, (width, height), pages, config.font_name)


def create_cover(path: Path, thumb_path: Path, config: MazeBookConfig) -> None:
    """Create cover and thumbnail images.

    Pillow is used when installed (declared as a project dependency). A tiny
    dependency-free raster fallback keeps tests and constrained workers usable.
    """
    palettes = {"modern": ((15, 23, 42), (56, 189, 248)), "classic": ((248, 250, 252), (17, 24, 39)), "kids": ((254, 243, 199), (249, 115, 22)), "minimal": ((255, 255, 255), (0, 0, 0))}
    bg, fg = palettes[config.cover_style]
    try:
        from PIL import Image, ImageDraw, ImageFont

        img = Image.new("RGB", (1600, 2400), bg)
        draw = ImageDraw.Draw(img)
        font_big = ImageFont.load_default(size=90)
        font_small = ImageFont.load_default(size=38)
        draw.text((120, 260), config.title, fill=fg, font=font_big)
        draw.text((120, 390), config.subtitle, fill=fg, font=font_small)
        for i in range(9):
            draw.rectangle((120 + i * 145, 760, 210 + i * 145, 1650), outline=fg, width=6)
        draw.text((120, 2050), f"By {config.author}", fill=fg, font=font_small)
        img.save(path, format="JPEG", quality=92)
        img.resize((400, 600)).save(thumb_path, format="JPEG", quality=88)
        return
    except ModuleNotFoundError:
        pass

    def ppm(width: int, height: int) -> bytes:
        data = bytearray(f"P6\n{width} {height}\n255\n".encode())
        for y in range(height):
            for x in range(width):
                stripe = ((x // max(1, width // 12)) + (y // max(1, height // 18))) % 2 == 0
                data.extend(fg if stripe and width * .12 < x < width * .88 and height * .34 < y < height * .72 else bg)
        return bytes(data)

    path.write_bytes(ppm(800, 1200))
    thumb_path.write_bytes(ppm(200, 300))


def generate_book(config: MazeBookConfig) -> dict:
    mazes = generate_unique_mazes(config)
    book_id = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{_slug(config.title)}-{uuid.uuid4().hex[:8]}"
    out = config.storage_dir / book_id
    out.mkdir(parents=True, exist_ok=False)
    pdf_path, cover_path, thumb_path, metadata_path = out / "book.pdf", out / "cover.jpg", out / "thumbnail.jpg", out / "metadata.json"
    write_pdf(pdf_path, config, mazes)
    create_cover(cover_path, thumb_path, config)
    metadata = {
        "book_id": book_id,
        "title": config.title,
        "subtitle": config.subtitle,
        "author": config.author,
        "publisher": config.publisher,
        "book_size": config.book_size,
        "margins_inches": asdict(config.margins),
        "font_name": config.font_name,
        "cover_style": config.cover_style,
        "maze_count": len(mazes),
        "unique_fingerprints": [m.fingerprint for m in mazes],
        "difficulty_distribution": {d: sum(1 for m in mazes if m.difficulty == d) for d in ["easy", "medium", "hard", "expert"]},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "assets": {"pdf": str(pdf_path), "cover": str(cover_path), "thumbnail": str(thumb_path)},
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a PuzzleAI maze book")
    parser.add_argument("--title", default=MazeBookConfig.title)
    parser.add_argument("--book-size", choices=list(BOOK_SIZES), default="US Letter")
    parser.add_argument("--maze-count", type=int, default=40)
    parser.add_argument("--font", default="Helvetica")
    parser.add_argument("--cover-style", choices=["classic", "modern", "kids", "minimal"], default="modern")
    parser.add_argument("--seed")
    args = parser.parse_args()
    print(json.dumps(generate_book(MazeBookConfig(title=args.title, book_size=args.book_size, maze_count=args.maze_count, font_name=args.font, cover_style=args.cover_style, seed=args.seed)), indent=2))

if __name__ == "__main__":
    main()
