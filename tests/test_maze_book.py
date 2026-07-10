import json
import tempfile
import unittest
from pathlib import Path

from maze_book.generator import MazeBookRequest, generate_maze_book


class MazeBookGeneratorTests(unittest.TestCase):
    def test_generates_pdf_cover_and_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            book = generate_maze_book(
                MazeBookRequest(topic="Animals", difficulty="Easy", pages=10, age_group="Kids"),
                output_root=Path(tmp),
            )

            self.assertTrue(book.pdf_path.exists())
            self.assertTrue(book.cover_path.exists())
            self.assertTrue(book.metadata_path.exists())
            self.assertTrue(book.pdf_path.read_bytes().startswith(b"%PDF-1.4"))
            self.assertIn("<svg", book.cover_path.read_text(encoding="utf-8"))

            metadata = json.loads(book.metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(metadata["maze_pages"], 10)
            self.assertEqual(metadata["solution_pages"], 10)
            self.assertEqual(metadata["cover_pages"], 1)
            self.assertEqual(metadata["pdf_pages"], 21)

    def test_rejects_invalid_page_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                generate_maze_book(MazeBookRequest("Animals", "Easy", 0, "Kids"), Path(tmp))


if __name__ == "__main__":
    unittest.main()
