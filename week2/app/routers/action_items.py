from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from ..db import Database, database
from ..schemas import (
    ActionItemDoneRequest,
    ActionItemDoneResponse,
    ActionItemModel,
    ExtractRequest,
    ExtractResponse,
)
from ..services.extract import extract_action_items, extract_action_items_llm


router = APIRouter(prefix="/action-items", tags=["action-items"])


def get_db() -> Database:
    return database


def _run_extraction(payload: ExtractRequest, db: Database, *, force_llm: bool = False) -> ExtractResponse:
    text = payload.text.strip()
    note_id: Optional[int] = None
    if payload.save_note:
        saved_note = db.insert_note(text)
        note_id = saved_note["id"]

    use_llm = force_llm or payload.use_llm
    extractor = extract_action_items_llm if use_llm else extract_action_items
    items = extractor(text)

    records = db.insert_action_items(items, note_id=note_id)
    response_items = [ActionItemModel(**row) for row in records]
    return ExtractResponse(note_id=note_id, items=response_items)


@router.post("/extract", response_model=ExtractResponse)
def extract(payload: ExtractRequest, db = Depends(get_db)) -> ExtractResponse:
    return _run_extraction(payload, db)


@router.post("/extract/llm", response_model=ExtractResponse)
def extract_llm(payload: ExtractRequest, db = Depends(get_db)) -> ExtractResponse:
    return _run_extraction(payload, db, force_llm=True)


@router.get("", response_model=list[ActionItemModel])
def list_all(note_id: Optional[int] = Query(default=None), db = Depends(get_db)):
    rows = db.list_action_items(note_id=note_id)
    return [ActionItemModel(**row) for row in rows]


@router.post("/{action_item_id}/done", response_model=ActionItemDoneResponse)
def mark_done(action_item_id: int, payload: ActionItemDoneRequest, db = Depends(get_db)):
    record = db.mark_action_item_done(action_item_id, payload.done)
    if record is None:
        raise HTTPException(status_code=404, detail="action item not found")
    return ActionItemDoneResponse(id=record["id"], done=record["done"])
