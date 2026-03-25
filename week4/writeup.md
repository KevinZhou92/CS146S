# Week 4 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 


## YOUR RESPONSES
### Automation #1 — `/docs-sync` (Custom Slash Command)

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Inspired by the "Docs sync" example in the assignment (Part I, Section A) and the Claude Code best-practices guide's recommendation to keep slash commands focused and idempotent. The command follows the principle of using `$ARGUMENTS`-free, single-responsibility workflows that are safe to re-run without side effects.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal:** Keep `docs/API.md` in sync with the live FastAPI server's OpenAPI spec automatically, eliminating manual documentation drift.
>
> **Inputs:** A running FastAPI server at `http://localhost:8000`.
>
> **Steps:**
> 1. Start the server with `make run` (if not already running).
> 2. Fetch the live spec via `curl -s http://localhost:8000/openapi.json`.
> 3. Read the existing `docs/API.md` (if present) to compute a diff.
> 4. For each path+method in the spec, extract: HTTP method, path, summary, request/response schemas, and parameters.
> 5. Rewrite `docs/API.md` with a structured reference section per endpoint.
> 6. Print a delta summary (`+` new routes, `-` removed routes, `~` changed schemas).
> 7. Stop the server.
>
> **Output:** Updated `docs/API.md` + a printed delta report (e.g. "docs/API.md updated. 10 routes documented.").

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> ```bash
> /docs-sync
> ```
> Expected output: a delta report listing new/changed/removed routes and a confirmation line.
>
> **Rollback:** `git checkout docs/API.md` or simply delete the file — the source of truth is always `/openapi.json` on the live server.
>
> **Safety:** Only reads from the server and only writes `docs/API.md`. Never touches Python source files. Idempotent: running twice with no backend changes produces the same file.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before:** After adding or modifying an API endpoint, a developer had to manually open the Swagger UI, copy each route's details, and hand-edit `docs/API.md` — error-prone and frequently skipped.
>
> **After:** Running `/docs-sync` regenerates the entire `docs/API.md` in seconds, guaranteed to match the live server. The delta report makes it immediately obvious if any routes were added, removed, or changed.

e. How you used the automation to enhance the starter application
> After the `/add-crud` automation added `PUT /notes/{id}` and `DELETE /notes/{id}` to the backend, `/docs-sync` was run to regenerate `docs/API.md`. It detected 10 routes (including the two new CRUD endpoints) and produced an accurate, up-to-date API reference — work that would have required manual editing of the docs file.


### Automation #2 — `/add-crud` (SubAgent TDD Pipeline)

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Inspired by the SubAgents overview at [docs.anthropic.com/en/docs/claude-code/sub-agents](https://docs.anthropic.com/en/docs/claude-code/sub-agents) and the "TestAgent + CodeAgent" example in the assignment (Part I, Section C). The pipeline enforces strict role separation — each agent has a narrow, clearly scoped job — following the best-practices recommendation to "use checklists/scratchpads, reset context between roles."

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal:** Add `PUT /notes/{id}`, `DELETE /notes/{id}`, input validation (422 on empty fields), and frontend Edit/Delete buttons via a test-driven, three-phase SubAgent pipeline.
>
> **Inputs:** None (operates on the existing codebase).
>
> **Phase 1 — TestAgent:**
> - Appends 7 failing tests to `backend/tests/test_notes.py` covering update, delete, and validation cases.
> - Runs pytest to confirm tests are *collected and fail* (not error).
> - Does NOT touch any source files under `backend/app/` or `frontend/`.
>
> **Phase 2 — CodeAgent:**
> - Updates `backend/app/schemas.py` with `NoteUpdate` (with `min_length=1` validation) and `Field`-validated `NoteCreate`.
> - Appends `update_note` and `delete_note` handlers to `backend/app/routers/notes.py`.
> - Adds Edit/Delete buttons to `frontend/app.js` inside `loadNotes()`.
> - Runs `make format` to auto-format.
> - Does NOT touch any test files.
>
> **Phase 3 — VerifierAgent (read-only):**
> - Runs the full pytest suite (`PYTHONPATH=. pytest -q backend/tests`).
> - Runs `make lint`.
> - Prints a final checklist if all checks pass, or reports the failure and stops.
>
> **Output:** All tests green, lint clean, and a checklist confirming each feature is implemented and tested. Suggests running `/docs-sync` as the next step.

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> ```bash
> /add-crud
> ```
> Expected output: Phase 1 reports 7 new failing tests; Phase 2 reports edits and format success; Phase 3 prints the green checklist.
>
> **Rollback:**
> ```bash
> git checkout backend/app/schemas.py backend/app/routers/notes.py frontend/app.js backend/tests/test_notes.py
> ```
>
> **Safety:** The pipeline is idempotent — running it a second time finds tests and handlers already present; Phase 3 still verifies everything is green. Phases run sequentially and stop on failure before proceeding.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before:** Adding CRUD endpoints required a developer to manually (1) write failing tests, (2) implement the schemas and route handlers, (3) update the frontend, (4) run tests, and (5) run the linter — typically across multiple context switches and easy to skip steps like validation or 404 handling.
>
> **After:** A single `/add-crud` invocation orchestrates all five steps automatically through role-specialized agents with strict separation of concerns, guaranteeing test-first development and a clean lint gate before declaring success.

e. How you used the automation to enhance the starter application
> The starter app only had `GET` and `POST /notes/` endpoints with no update or delete capability, and no field validation. Running `/add-crud` added full CRUD support (`PUT /notes/{id}`, `DELETE /notes/{id}`), enforced `min_length=1` validation on create/update (returning 422 on empty fields), and wired Edit/Delete buttons into the frontend — transforming the app from a read-heavy demo into a fully functional note manager.
