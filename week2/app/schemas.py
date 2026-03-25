from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw meeting notes to analyze")
    save_note: bool = Field(False, description="Persist the original note before extraction")
    use_llm: bool = Field(
        False,
        description="When true, route extraction through the LLM-powered pipeline",
    )


class ActionItemModel(BaseModel):
    id: int
    text: str
    done: bool
    note_id: Optional[int] = Field(default=None, description="Source note identifier")
    created_at: str


class ExtractResponse(BaseModel):
    note_id: Optional[int] = Field(default=None, description="Saved note identifier, if any")
    items: List[ActionItemModel]


class ActionItemDoneRequest(BaseModel):
    done: bool = Field(True, description="Completion flag for the action item")


class ActionItemDoneResponse(BaseModel):
    id: int
    done: bool


class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1, description="Text body of the note")


class NoteRead(BaseModel):
    id: int
    content: str
    created_at: str

