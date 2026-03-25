# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
make run      # Start the FastAPI server at http://localhost:8000 (API docs at /docs)
make test     # Run the full pytest suite
make format   # Auto-format with black + ruff --fix
make lint     # Lint with ruff (no auto-fix)
make seed     # Seed the SQLite database
```

Run a single test file:
```bash
PYTHONPATH=. pytest -q backend/tests/test_notes.py
```

Run a single test by name:
```bash
PYTHONPATH=. pytest -q backend/tests/test_notes.py::test_create_note
```

## Architecture

**Stack:** FastAPI backend + vanilla JS frontend + SQLite via SQLAlchemy ORM.

The frontend is served as static files from `/static` and talks to the backend REST API.

**Backend layers:**
- `backend/app/routers/` — route handlers (thin; delegate to db directly)
- `backend/app/models.py` — SQLAlchemy ORM models (`Note`, `ActionItem`)
- `backend/app/schemas.py` — Pydantic schemas for request/response validation
- `backend/app/db.py` — session factory; use `get_db()` for FastAPI dependency injection or `get_session()` as a context manager in scripts
- `backend/app/services/extract.py` — stateless text parsing utility

**Database:** SQLite at `./data/app.db` (override with `DATABASE_PATH` env var). Schema and seed data live in `data/seed.sql`; the app auto-seeds on first startup.

**Testing:** Tests use an in-memory SQLite database via pytest fixtures in `conftest.py`. The `get_db` dependency is overridden per-test so no persistent state leaks between tests.

**API endpoints:**
- `GET/POST /notes/` — list and create notes
- `GET /notes/{id}` — get single note
- `GET /notes/search?q=` — case-insensitive search across title and content
- `GET/POST /action-items/` — list and create action items
- `PUT /action-items/{id}/complete` — mark an item complete
