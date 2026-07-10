from __future__ import annotations

import json
import random
import re
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

PAGE_WIDTH = 612
PAGE_HEIGHT = 792
OUTPUT_ROOT = Path("generated/maze_books")


@dataclass(frozen=True)
class MazeBookRequest:
    topic: str
    difficulty: str
    pages: int
    age_group: str


@dataclass(frozen=True)
class GeneratedBook:
    pdf_path: Path
    cover_path: Path
    metadata_path: Path
    metadata: dict


def generate_maze_book(request: MazeBookRequest, output_root: Path = OUTPUT_ROOT) -> GeneratedBook:
    if request.pages < 1 or request.pages > 100:
        raise ValueError("pages must be between 1 and 100")
    if not request.topic.strip():
        raise ValueError("topic is required")
    if not request.difficulty.strip():
        raise ValueError("difficulty is required")
    if not request.age_group.strip():
        raise ValueError("age_group is required")

    book_id = f"{_slugify(request.topic)}-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    book_dir = output_root / book_id
    book_dir.mkdir(parents=True, exist_ok=True)

    size = _grid_size_for_difficulty(request.difficulty)
    mazes = []
    seed_base = hash((request.topic.lower(), request.difficulty.lower(), request.age_group.lower(), request.pages)) & 0xFFFFFFFF
    for index in range(request.pages):
        mazes.append(_generate_maze(size, size, seed_base + index))

    cover_path = book_dir / "cover.svg"
    pdf_path = book_dir / "maze-book.pdf"
    metadata_path = book_dir / "metadata.json"

    _write_cover_svg(cover_path, request)
    _write_pdf(pdf_path, request, mazes)

    metadata = {
        "id": book_id,
        "topic": request.topic,
        "difficulty": request.difficulty,
        "age_group": request.age_group,
        "maze_pages": request.pages,
        "solution_pages": request.pages,
        "cover_pages": 1,
        "pdf_pages": 1 + request.pages * 2,
        "grid_size": {"rows": size, "columns": size},
        "pdf_path": str(pdf_path),
        "cover_path": str(cover_path),
        "metadata_path": str(metadata_path),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return GeneratedBook(pdf_path, cover_path, metadata_path, metadata)


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "maze-book"


def _grid_size_for_difficulty(difficulty: str) -> int:
    normalized = difficulty.strip().lower()
    if normalized == "easy":
        return 10
    if normalized == "medium":
        return 14
    if normalized == "hard":
        return 18
    return 12


def _generate_maze(rows: int, cols: int, seed: int) -> dict:
    rng = random.Random(seed)
    walls = [[{"n": True, "e": True, "s": True, "w": True} for _ in range(cols)] for _ in range(rows)]
    visited = [[False] * cols for _ in range(rows)]
    parent: dict[tuple[int, int], tuple[int, int] | None] = {(0, 0): None}

    def carve(r: int, c: int) -> None:
        visited[r][c] = True
        directions = [("n", -1, 0, "s"), ("e", 0, 1, "w"), ("s", 1, 0, "n"), ("w", 0, -1, "e")]
        rng.shuffle(directions)
        for direction, dr, dc, opposite in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                walls[r][c][direction] = False
                walls[nr][nc][opposite] = False
                parent[(nr, nc)] = (r, c)
                carve(nr, nc)

    carve(0, 0)
    walls[0][0]["w"] = False
    walls[rows - 1][cols - 1]["e"] = False

    path = []
    cursor: tuple[int, int] | None = (rows - 1, cols - 1)
    while cursor is not None:
        path.append(cursor)
        cursor = parent[cursor]
    path.reverse()
    return {"rows": rows, "cols": cols, "walls": walls, "solution": path}


def _write_cover_svg(path: Path, request: MazeBookRequest) -> None:
    safe_topic = _xml_escape(request.topic)
    safe_subtitle = _xml_escape(f"{request.difficulty} mazes for {request.age_group}")
    path.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="612" height="792" viewBox="0 0 612 792">
  <rect width="612" height="792" fill="#fdf7e3"/>
  <rect x="54" y="54" width="504" height="684" rx="28" fill="#fff" stroke="#1f2937" stroke-width="6"/>
  <text x="306" y="170" text-anchor="middle" font-family="Arial, sans-serif" font-size="54" font-weight="700" fill="#111827">{safe_topic}</text>
  <text x="306" y="230" text-anchor="middle" font-family="Arial, sans-serif" font-size="30" fill="#374151">Maze Book</text>
  <text x="306" y="285" text-anchor="middle" font-family="Arial, sans-serif" font-size="22" fill="#6b7280">{safe_subtitle}</text>
  <path d="M156 430 h110 v-70 h95 v115 h95 v-70" fill="none" stroke="#2563eb" stroke-width="24" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="156" cy="430" r="18" fill="#16a34a"/>
  <polygon points="462,360 500,405 462,450" fill="#dc2626"/>
  <text x="306" y="660" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" fill="#111827">{request.pages} Mazes + {request.pages} Solutions</text>
</svg>''', encoding="utf-8")


def _xml_escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _write_pdf(path: Path, request: MazeBookRequest, mazes: list[dict]) -> None:
    pages = [_cover_page_commands(request)]
    pages.extend(_maze_page_commands(maze, f"Maze {i + 1}", False) for i, maze in enumerate(mazes))
    pages.extend(_maze_page_commands(maze, f"Solution {i + 1}", True) for i, maze in enumerate(mazes))
    _write_simple_pdf(path, pages)


def _cover_page_commands(request: MazeBookRequest) -> str:
    return "\n".join([
        "0.99 0.97 0.89 rg 0 0 612 792 re f",
        "0.12 0.16 0.22 RG 6 w 54 54 504 684 re S",
        _text(306, 620, request.topic, 44, center=True, bold=True),
        _text(306, 570, "Maze Book", 30, center=True, bold=True),
        _text(306, 528, f"{request.difficulty} mazes for {request.age_group}", 18, center=True),
        "0.15 0.39 0.92 RG 20 w 150 375 m 270 375 l 270 445 l 360 445 l 360 330 l 460 330 l S",
        "0.09 0.64 0.29 rg 132 357 36 36 re f",
        _text(306, 135, f"{request.pages} Mazes + {request.pages} Solutions", 20, center=True),
    ])


def _maze_page_commands(maze: dict, title: str, show_solution: bool) -> str:
    commands = [_text(306, 742, title, 26, center=True, bold=True)]
    rows, cols = maze["rows"], maze["cols"]
    box = 470
    cell = box / max(rows, cols)
    left = (PAGE_WIDTH - cols * cell) / 2
    top = 675
    commands.append("0 0 0 RG 2 w")
    for r in range(rows):
        for c in range(cols):
            x = left + c * cell
            y = top - r * cell
            w = maze["walls"][r][c]
            if w["n"]: commands.append(f"{x:.2f} {y:.2f} m {x + cell:.2f} {y:.2f} l S")
            if w["e"]: commands.append(f"{x + cell:.2f} {y:.2f} m {x + cell:.2f} {y - cell:.2f} l S")
            if w["s"]: commands.append(f"{x:.2f} {y - cell:.2f} m {x + cell:.2f} {y - cell:.2f} l S")
            if w["w"]: commands.append(f"{x:.2f} {y:.2f} m {x:.2f} {y - cell:.2f} l S")
    commands.append(_text(left - 28, top - cell * 0.65, "START", 10))
    commands.append(_text(left + cols * cell + 8, top - (rows - 0.5) * cell, "FINISH", 10))
    if show_solution:
        points = []
        for r, c in maze["solution"]:
            points.append((left + c * cell + cell / 2, top - r * cell - cell / 2))
        commands.append("0.86 0.15 0.15 RG 4 w")
        commands.append(" ".join([f"{points[0][0]:.2f} {points[0][1]:.2f} m"] + [f"{x:.2f} {y:.2f} l" for x, y in points[1:]]) + " S")
    return "\n".join(commands)


def _text(x: float, y: float, value: str, size: int, center: bool = False, bold: bool = False) -> str:
    escaped = value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    font = "F2" if bold else "F1"
    if center:
        approximate_width = len(value) * size * 0.27
        x -= approximate_width
    return f"BT /{font} {size} Tf {x:.2f} {y:.2f} Td ({escaped}) Tj ET"


def _write_simple_pdf(path: Path, page_commands: Iterable[str]) -> None:
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>", None, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>", b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>"]
    page_ids = []
    for commands in page_commands:
        stream = commands.encode("latin-1", "replace")
        content_id = len(objects) + 1
        objects.append(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream")
        page_id = len(objects) + 1
        page_ids.append(page_id)
        page = f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {content_id} 0 R >>".encode()
        objects.append(page)
    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode()

    data = bytearray(b"%PDF-1.4\n")
    offsets = []
    for index, obj in enumerate(objects, 1):
        offsets.append(len(data))
        data.extend(f"{index} 0 obj\n".encode())
        data.extend(obj or b"")
        data.extend(b"\nendobj\n")
    xref = len(data)
    data.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets:
        data.extend(f"{offset:010d} 00000 n \n".encode())
    data.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    path.write_bytes(data)
