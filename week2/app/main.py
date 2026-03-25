from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from . import database
from .routers import action_items, notes


def create_app() -> FastAPI:
    database.init()
    application = FastAPI(title="Action Item Extractor")

    @application.get("/", response_class=HTMLResponse)
    def index() -> str:
        html_path = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
        return html_path.read_text(encoding="utf-8")

    application.include_router(notes.router)
    application.include_router(action_items.router)

    static_dir = Path(__file__).resolve().parents[1] / "frontend"
    application.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    return application


app = create_app()
