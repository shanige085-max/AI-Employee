# AI Employee - Maze Book Generator

A small, dependency-free HTTP API that generates a printable maze book PDF and a local cover image.

## Run

```bash
python -m maze_book.api
```

## Create a maze book

```bash
curl -X POST http://127.0.0.1:8000/books/maze \
  -H 'Content-Type: application/json' \
  -d '{"topic":"Animals","difficulty":"Easy","pages":10,"age_group":"Kids"}'
```

The response contains local paths for the generated PDF, cover SVG, and metadata JSON. Generated files are saved under `generated/maze_books/`.
