from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .generator import MazeBookRequest, generate_maze_book


class MazeBookHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        if self.path.rstrip("/") != "/books/maze":
            self._send_json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            request = MazeBookRequest(
                topic=str(payload.get("topic", "")).strip(),
                difficulty=str(payload.get("difficulty", "")).strip(),
                pages=int(payload.get("pages", 10)),
                age_group=str(payload.get("age_group", "")).strip(),
            )
            book = generate_maze_book(request)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self._send_json(400, {"error": str(exc)})
            return
        self._send_json(201, {"pdf": str(book.pdf_path), "cover": str(book.cover_path), "metadata": book.metadata})

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        self._send_json(404, {"error": "not found"})

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), MazeBookHandler)
    print(f"Maze Book API listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
