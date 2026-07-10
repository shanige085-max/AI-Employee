from __future__ import annotations

import struct
import zlib
from pathlib import Path

from .models import Cell, Maze
from .solver import MazeSolver


class MazeRenderer:
    def __init__(self, cell_size: int = 24, margin: int = 24, wall_width: int = 2) -> None:
        self.cell_size = cell_size
        self.margin = margin
        self.wall_width = wall_width
        self.solver = MazeSolver()

    def export_svg(self, maze: Maze, path: str | Path, include_solution: bool = False) -> None:
        Path(path).write_text(self.to_svg(maze, include_solution), encoding="utf-8")

    def export_png(self, maze: Maze, path: str | Path, include_solution: bool = False) -> None:
        width, height, pixels = self._rasterize(maze, include_solution)
        Path(path).write_bytes(_encode_png(width, height, pixels))

    def export_pdf_page(self, maze: Maze, path: str | Path, include_solution: bool = False) -> None:
        svg_lines = self._wall_segments(maze)
        page = 612.0
        scale = min(500.0 / self._maze_px(maze), 1.0)
        offset = (page - self._maze_px(maze) * scale) / 2
        commands = ["q", f"{scale:.3f} 0 0 {scale:.3f} {offset:.3f} {offset:.3f} cm", "2 w"]
        if include_solution:
            commands.append("0.85 0.10 0.10 RG 4 w")
            commands.extend(self._solution_pdf_commands(maze))
            commands.append("0 0 0 RG 2 w")
        commands.extend(f"{x1} {self._maze_px(maze)-y1} m {x2} {self._maze_px(maze)-y2} l S" for x1, y1, x2, y2 in svg_lines)
        commands.append("Q")
        _write_simple_pdf(Path(path), "\n".join(commands), page, page)

    def to_svg(self, maze: Maze, include_solution: bool = False) -> str:
        size_px = self._maze_px(maze)
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{size_px}" height="{size_px}" viewBox="0 0 {size_px} {size_px}">', '<rect width="100%" height="100%" fill="white"/>']
        if include_solution:
            points = " ".join(f"{self.margin + c.col*self.cell_size + self.cell_size/2},{self.margin + c.row*self.cell_size + self.cell_size/2}" for c in self.solver.solve(maze))
            parts.append(f'<polyline points="{points}" fill="none" stroke="#d22" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
        for x1, y1, x2, y2 in self._wall_segments(maze):
            parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="black" stroke-width="{self.wall_width}" stroke-linecap="square"/>')
        parts.append("</svg>")
        return "\n".join(parts)

    def _maze_px(self, maze: Maze) -> int:
        return self.margin * 2 + maze.size * self.cell_size

    def _wall_segments(self, maze: Maze) -> list[tuple[int, int, int, int]]:
        m, cs = self.margin, self.cell_size
        segments = []
        for r in range(maze.size):
            for c in range(maze.size):
                cell = Cell(r, c)
                x, y = m + c * cs, m + r * cs
                top_is_entrance = r == 0 and cell == maze.start
                left_is_entrance = c == 0 and cell == maze.start and r != 0
                right_is_exit = c + 1 == maze.size and cell == maze.end and r != maze.size - 1
                bottom_is_exit = r + 1 == maze.size and cell == maze.end

                if r == 0 and not top_is_entrance:
                    segments.append((x, y, x + cs, y))
                if c == 0 and not left_is_entrance:
                    segments.append((x, y, x, y + cs))
                if c + 1 < maze.size:
                    if not maze.has_passage(cell, Cell(r, c + 1)):
                        segments.append((x + cs, y, x + cs, y + cs))
                elif not right_is_exit:
                    segments.append((x + cs, y, x + cs, y + cs))
                if r + 1 < maze.size:
                    if not maze.has_passage(cell, Cell(r + 1, c)):
                        segments.append((x, y + cs, x + cs, y + cs))
                elif not bottom_is_exit:
                    segments.append((x, y + cs, x + cs, y + cs))
        return segments

    def _solution_pdf_commands(self, maze: Maze) -> list[str]:
        total = self._maze_px(maze)
        pts = [(self.margin + c.col*self.cell_size + self.cell_size/2, total - (self.margin + c.row*self.cell_size + self.cell_size/2)) for c in self.solver.solve(maze)]
        return [f"{pts[0][0]:.1f} {pts[0][1]:.1f} m"] + [f"{x:.1f} {y:.1f} l S" for x, y in pts[1:]]

    def _rasterize(self, maze: Maze, include_solution: bool) -> tuple[int, int, list[bytearray]]:
        size = self._maze_px(maze)
        pixels = [bytearray([255, 255, 255] * size) for _ in range(size)]
        def draw(
            x1: int,
            y1: int,
            x2: int,
            y2: int,
            color: tuple[int, int, int],
            width: int,
        ) -> None:
            steps = max(abs(x2 - x1), abs(y2 - y1), 1)
            for i in range(steps + 1):
                x = round(x1 + (x2 - x1) * i / steps)
                y = round(y1 + (y2 - y1) * i / steps)
                for yy in range(max(0, y - width // 2), min(size, y + width // 2 + 1)):
                    for xx in range(max(0, x - width // 2), min(size, x + width // 2 + 1)):
                        pixels[yy][xx * 3 : xx * 3 + 3] = bytes(color)
        if include_solution:
            pts = [(self.margin + c.col*self.cell_size + self.cell_size//2, self.margin + c.row*self.cell_size + self.cell_size//2) for c in self.solver.solve(maze)]
            for a, b in zip(pts, pts[1:]):
                draw(*a, *b, (210, 30, 30), 4)
        for seg in self._wall_segments(maze):
            draw(*seg, (0, 0, 0), self.wall_width)
        return size, size, pixels


def _encode_png(width: int, height: int, rows: list[bytearray]) -> bytes:
    raw = b"".join(b"\x00" + bytes(row) for row in rows)
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack("!I", len(data)) + kind + data + struct.pack("!I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack("!IIBBBBB", width, height, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b"")


def _write_simple_pdf(path: Path, stream: str, width: float, height: float) -> None:
    data = stream.encode("ascii")
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>", f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width} {height}] /Contents 4 0 R >>".encode(), b"<< /Length " + str(len(data)).encode() + b" >>\nstream\n" + data + b"\nendstream"]
    out = bytearray(b"%PDF-1.4\n") ; offsets=[]
    for i,obj in enumerate(objects,1):
        offsets.append(len(out)); out += f"{i} 0 obj\n".encode()+obj+b"\nendobj\n"
    xref=len(out); out += f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode()
    out += b"".join(f"{o:010d} 00000 n \n".encode() for o in offsets)
    out += f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    path.write_bytes(out)
