---
description: Add PUT/DELETE /notes endpoints and validation via a three-phase SubAgent TDD pipeline (TestAgent → CodeAgent → VerifierAgent).
---

# add-crud

Add `PUT /notes/{id}`, `DELETE /notes/{id}`, request validation, and frontend Edit/Delete buttons using a TDD SubAgent pipeline.

## Phase 1 — TestAgent (write failing tests only)

Launch a SubAgent with these instructions:

> You are TestAgent. Your ONLY job is to append new failing tests to `backend/tests/test_notes.py`. Do NOT touch any source files under `backend/app/` or `frontend/`.
>
> Append the following test functions to `backend/tests/test_notes.py`. Use the same `client` fixture already imported via conftest.
>
> Tests to add:
>
> **PUT /notes/{id}**
> - `test_update_note`: POST a note, then PUT `/notes/{id}` with `{"title": "Updated"}`, assert 200 and `data["title"] == "Updated"`.
> - `test_update_note_not_found`: PUT `/notes/99999` with `{"title": "x"}`, assert 404.
> - `test_update_note_empty_title`: POST a note, then PUT `/notes/{id}` with `{"title": ""}`, assert 422.
>
> **DELETE /notes/{id}**
> - `test_delete_note`: POST a note, DELETE `/notes/{id}`, assert 204. Then GET `/notes/{id}` and assert 404.
> - `test_delete_note_not_found`: DELETE `/notes/99999`, assert 404.
>
> **POST /notes/ validation**
> - `test_create_note_empty_title`: POST `/notes/` with `{"title": "", "content": "x"}`, assert 422.
> - `test_create_note_empty_content`: POST `/notes/` with `{"title": "x", "content": ""}`, assert 422.
>
> After appending, run:
> ```
> PYTHONPATH=. pytest -q backend/tests/test_notes.py
> ```
> Confirm the new tests are collected and FAIL (not error). Report results.

Wait for Phase 1 to complete before proceeding to Phase 2.

## Phase 2 — CodeAgent (implement features, never touch tests)

Launch a SubAgent with these instructions:

> You are CodeAgent. Implement the backend and frontend changes below. Do NOT touch any files under `backend/tests/`.
>
> **1. `backend/app/schemas.py`** — replace current content with:
> ```python
> from typing import Optional
>
> from pydantic import BaseModel, Field
>
>
> class NoteCreate(BaseModel):
>     title: str = Field(..., min_length=1)
>     content: str = Field(..., min_length=1)
>
>
> class NoteRead(BaseModel):
>     id: int
>     title: str
>     content: str
>
>     class Config:
>         from_attributes = True
>
>
> class NoteUpdate(BaseModel):
>     title: Optional[str] = Field(None, min_length=1)
>     content: Optional[str] = Field(None, min_length=1)
>
>
> class ActionItemCreate(BaseModel):
>     description: str
>
>
> class ActionItemRead(BaseModel):
>     id: int
>     description: str
>     completed: bool
>
>     class Config:
>         from_attributes = True
> ```
>
> **2. `backend/app/routers/notes.py`** — add `NoteUpdate` to the imports line, then append these two handlers at the end of the file:
> ```python
> @router.put("/{note_id}", response_model=NoteRead)
> def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_db)):
>     note = db.get(Note, note_id)
>     if not note:
>         raise HTTPException(status_code=404, detail="Note not found")
>     if payload.title is not None:
>         note.title = payload.title
>     if payload.content is not None:
>         note.content = payload.content
>     db.flush()
>     db.refresh(note)
>     return NoteRead.model_validate(note)
>
>
> @router.delete("/{note_id}", status_code=204)
> def delete_note(note_id: int, db: Session = Depends(get_db)):
>     note = db.get(Note, note_id)
>     if not note:
>         raise HTTPException(status_code=404, detail="Note not found")
>     db.delete(note)
>     db.flush()
> ```
>
> **3. `frontend/app.js`** — inside `loadNotes()`, replace the `li.textContent = ...` line with:
> ```javascript
>     li.textContent = `${n.title}: ${n.content}`;
>
>     const editBtn = document.createElement('button');
>     editBtn.textContent = 'Edit';
>     editBtn.onclick = async () => {
>       const newTitle = window.prompt('New title:', n.title);
>       if (newTitle === null) return;
>       const newContent = window.prompt('New content:', n.content);
>       if (newContent === null) return;
>       await fetchJSON(`/notes/${n.id}`, {
>         method: 'PUT',
>         headers: { 'Content-Type': 'application/json' },
>         body: JSON.stringify({ title: newTitle, content: newContent }),
>       });
>       loadNotes();
>     };
>     li.appendChild(editBtn);
>
>     const delBtn = document.createElement('button');
>     delBtn.textContent = 'Delete';
>     delBtn.onclick = async () => {
>       if (!window.confirm(`Delete "${n.title}"?`)) return;
>       await fetch(`/notes/${n.id}`, { method: 'DELETE' });
>       loadNotes();
>     };
>     li.appendChild(delBtn);
> ```
>
> After all edits, run `make format` to auto-format. Report any errors.

Wait for Phase 2 to complete before proceeding to Phase 3.

## Phase 3 — VerifierAgent (read-only quality checks)

Launch a SubAgent with these instructions:

> You are VerifierAgent. Run these checks in order and report results:
>
> 1. Run full test suite:
>    ```
>    PYTHONPATH=. pytest -q backend/tests
>    ```
>    All tests must pass (including the new ones from Phase 1).
>
> 2. Run linter:
>    ```
>    make lint
>    ```
>    Must exit with no errors.
>
> 3. If both pass, print this checklist:
>    ```
>    ✅ PUT /notes/{id} — implemented and tested
>    ✅ DELETE /notes/{id} — implemented and tested
>    ✅ POST /notes/ validation (422 on empty fields) — implemented and tested
>    ✅ Frontend Edit/Delete buttons — implemented
>    ✅ All tests green
>    ✅ Lint clean
>
>    Next step: run /docs-sync to regenerate docs/API.md with the new routes.
>    ```
>
> 4. If any check fails, print the failure output and stop without printing the checklist.
>
> Do NOT modify any files.

## Notes
- Phases run sequentially: Phase 1 → Phase 2 → Phase 3.
- If any phase fails, stop and report the error to the user before proceeding.
- The pipeline is idempotent: running `/add-crud` a second time will find tests already present and handlers already implemented; Phase 3 will still verify everything is green.
