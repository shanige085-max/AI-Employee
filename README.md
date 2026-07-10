# PuzzleAI Employee

PuzzleAI Employee is a production-minded FastAPI foundation for a future puzzle automation application. This repository intentionally contains only the application foundation; puzzle generators are not included yet.

## Tech Stack

- Python 3.12
- FastAPI
- SQLite
- SQLAlchemy 2.x
- Alembic
- Pydantic Settings
- Uvicorn

## Project Structure

```text
.
├── alembic/                 # Database migrations
│   ├── versions/
│   └── env.py
├── app/
│   ├── api/                 # REST API routing
│   ├── core/                # Configuration and logging
│   ├── db/                  # Database session and base metadata
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic services
│   └── main.py              # FastAPI application factory
├── tests/                   # Test package placeholder
├── .env.example             # Environment variable template
├── alembic.ini              # Alembic configuration
└── requirements.txt
```

## Getting Started

### 1. Create a virtual environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Update `.env` values as needed.

### 4. Run database migrations

```bash
alembic upgrade head
```

### 5. Run the API

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

- `GET /health` — application health check
- `GET /api/v1/health` — versioned health check

## Development Notes

- Configuration is loaded from environment variables and optional `.env` files.
- SQLite is configured by default for local development.
- SQLAlchemy metadata is wired into Alembic for future migrations.
- The modular package structure is ready for future domains, including puzzle generators, without adding generator code yet.
