---
description: Fetch /openapi.json from the running server and sync docs/API.md with any route changes.
---

# docs-sync

Sync `docs/API.md` with the live OpenAPI spec from the running FastAPI server.

## Steps
0. Start the server:
```
make run
```
1. 
Fetch the live spec with the Bash tool:
   ```
   curl -s http://localhost:8000/openapi.json
   ```
   If the server is unreachable (empty output or connection refused), tell the user to run `make run` first and stop.

2. Read `docs/API.md` if it exists (it may not).

3. For each path+method in the spec extract: HTTP method, path, summary, request body schema, response schema (200/201), path/query parameters.

4. Rewrite `docs/API.md`:
   ```
   # API Reference
   _Auto-generated from /openapi.json — do not edit by hand._

   ## GET /notes/
   **Description:** List all notes
   **Response 200:** Array of NoteRead `{id, title, content}`
   ...
   ```

5. Print delta vs previous file content:
   - `+ METHOD /path` for new routes
   - `- METHOD /path` for removed routes
   - `~ METHOD /path` for changed schemas
   - "Initial generation — all routes are new." if no prior file existed

6. Write the updated `docs/API.md`.

7. Print: "docs/API.md updated. N routes documented."

8. Stop the server

## Safety notes
- Only reads from the server; only writes `docs/API.md`. Does not touch Python source files.
- Idempotent: running twice with no backend changes produces the same file.
- To undo: `git checkout docs/API.md` or delete the file.
