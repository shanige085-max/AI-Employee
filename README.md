# PuzzleAI Employee

Module 2 adds production-ready backend infrastructure for the PuzzleAI Employee service.

## Included capabilities

- Typed configuration manager using `pydantic-settings`.
- `.env` loading with process environment precedence.
- SQLite database engine/session initialization.
- SQLAlchemy `Employee` model.
- Alembic migration environment and initial employee table migration.
- Configurable console or JSON logging.
- Safe Settings API at `/api/v1/settings`.
- Liveness and readiness Health API at `/api/v1/health` and `/api/v1/health/ready`.
- JSON error handling middleware with request IDs.
- Async background job manager with lifecycle startup/shutdown.
- Central project constants.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
```

## Run locally

```bash
uvicorn app.main:app --reload
```

## Database

Initialize or upgrade the SQLite database with Alembic:

```bash
alembic upgrade head
```

The application also calls `init_db()` during startup so local development and tests have required tables.

## Configuration

Supported environment variables are documented in `.env.example`. Secret values must not be exposed from `Settings.safe_public_settings`; the Settings API only returns safe operational metadata.

## Testing

```bash
pytest
```
