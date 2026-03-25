# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Environment Setup

Dependencies are defined in `../pyproject.toml` (repo root). Install from the repo root:
```bash
pip install -e .[dev]
```
Or activate the course conda environment: `conda activate cs146s`

## Commands

All `make` commands must be run from the `week5/` directory. The Makefile sets `PYTHONPATH=.` for all targets.

```bash
make run       # Start uvicorn dev server at http://localhost:8000 (--reload enabled)
make test      # Run all pytest tests
make lint      # ruff check (no auto-fix)
make format    # black + ruff --fix
make seed      # Manually re-seed the database (normally runs on first startup)
```

Run a single test file or test function:
```bash
PYTHONPATH=. pytest -q backend/tests/test_notes.py
PYTHONPATH=. pytest -q backend/tests/test_notes.py::test_create_and_list_notes
```

Frontend: `http://localhost:8000` | Interactive API docs: `http://localhost:8000/docs`

## Architecture

The app is a FastAPI backend that also serves a static vanilla JS frontend — there is no frontend build step.

**Request flow:** `main.py` → router (`routers/notes.py` or `routers/action_items.py`) → SQLAlchemy session via `get_db()` dependency → `models.py` → SQLite (`data/app.db`)

### Backend (`backend/app/`)

- **`main.py`**: App entry point. On startup, creates all DB tables and calls `apply_seed_if_needed()`. Mounts `frontend/` as static files at `/static` and serves `frontend/index.html` at `/`.
- **`db.py`**: SQLite engine + two session patterns:
  - `get_db()` — generator used as a FastAPI `Depends()` injection in route handlers
  - `get_session()` — context manager (`with get_session() as db:`) for use in scripts/services outside FastAPI
  - Database path defaults to `./data/app.db`, overridable via `DATABASE_PATH` in a `week5/.env` file.
- **`models.py`**: SQLAlchemy ORM — `Note` (id, title, content) and `ActionItem` (id, description, completed).
- **`schemas.py`**: Pydantic v2 request/response models. All `Read` schemas use `model_config = ConfigDict(from_attributes=True)` (or inner `class Config`).
- **`routers/notes.py`**: `GET /notes/`, `POST /notes/`, `GET /notes/search/?q=`, `GET /notes/{id}`
- **`routers/action_items.py`**: `GET /action-items/`, `POST /action-items/`, `PUT /action-items/{id}/complete`
- **`services/extract.py`**: Stateless text parsing — extracts action items from note content (lines ending in `!` or starting with `todo:`).

### Frontend (`frontend/`)

Pure HTML/CSS/vanilla JS. No build toolchain. `app.js` calls the JSON API directly using `fetch`. Served by FastAPI at `/static/*` and `/`.

### Tests (`backend/tests/`)

`conftest.py` creates a **temporary SQLite file** per test session and overrides `get_db` via `app.dependency_overrides`. Tests use `fastapi.testclient.TestClient`. No shared state between test runs.

### Seed (`data/seed.sql`)

Applied **only once** when `data/app.db` does not yet exist. To re-seed, delete `data/app.db` and restart, or run `make seed`.

## Linting & Formatting

Configured in `../pyproject.toml`:
- **black**: line-length 100, targets Python 3.10–3.12
- **ruff**: line-length 100; selects E, F, I, UP, B; ignores E501 (line length) and B008 (function call in default args)
- Pre-commit hooks run black, ruff --fix, end-of-file-fixer, and trailing-whitespace on commit
