from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..db import Database, database
from ..schemas import NoteCreate, NoteRead


router = APIRouter(prefix="/notes", tags=["notes"])


def get_db() -> Database:
    return database


@router.get("", response_model=list[NoteRead])
def list_notes(db = Depends(get_db)) -> list[NoteRead]:
    rows = db.list_notes()
    return [NoteRead(**row) for row in rows]


@router.post("", response_model=NoteRead)
def create_note(payload: NoteCreate, db = Depends(get_db)) -> NoteRead:
    note = db.insert_note(payload.content)
    return NoteRead(**note)


@router.get("/{note_id}", response_model=NoteRead)
def get_single_note(note_id: int, db = Depends(get_db)) -> NoteRead:
    row = db.get_note(note_id)
    if row is None:
        raise HTTPException(status_code=404, detail="note not found")
    return NoteRead(**row)
