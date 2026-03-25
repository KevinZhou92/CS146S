# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

All placeholder sections in this file have been completed.

## SUBMISSION DETAILS

Name: **Pengcheng Zhou** \
SUNet ID: **penzhou** \
Citations: **N/A – original implementation only.**

This assignment took me about **12** hours to do. 


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt: 
```
You are an excellent engineering developer. In extract_action_items function in the extract.py file, you need to implement an LLM-powered alternative, extract_action_items_llm(), that utilizes Ollama to perform action item extraction via a large language model.

Tips:
1. To produce structured outputs (i.e. JSON array of strings), use the "format" parameter.
2. Use ollama small model first, such as llama3.2-vision.
``` 

Generated Code Snippets:
```
week2/app/services/extract.py:3 added JSON handling, optional-typing imports, and Ollama-safe import guards to support LLM extraction.
week2/app/services/extract.py:17 introduced environment-driven defaults plus structured-output schema/prompt constants required by the new Ollama workflow.
week2/app/services/extract.py:63 switched heuristic extractor to reuse a shared _dedupe_preserve_order helper.
week2/app/services/extract.py:113 implemented extract_action_items_llm with validation, chat messages, structured-output call, and heuristic fallback.
week2/app/services/extract.py:166 added _extract_message_content to normalize Ollama responses.
week2/app/services/extract.py:179 added _coerce_action_items to parse JSON/string payloads into clean lists.
week2/app/services/extract.py:209 introduced _dedupe_preserve_order shared by both extraction paths.
week2/writeup.md:22 updated Exercise 1 prompt block with the exact instructions used (lines 25‑29 now filled in).
```

### Exercise 2: Add Unit Tests
Prompt: 
```
Write unit tests for extract_action_items_llm() covering multiple inputs (e.g., bullet lists, keyword-prefixed lines, empty input) in week2/tests/test_extract.py.
``` 

Generated Code Snippets:
```
week2/tests/test_extract.py:1-60 – Added `_mock_response` helper plus pytest cases for bullet lists, heuristic fallback when the model yields nothing, and empty-input handling.
```

### Exercise 3: Refactor Existing Code for Clarity
Prompt: 
```
Perform a refactor of the code in the backend, focusing in particular on well-defined API contracts/schemas, database layer cleanup, app lifecycle/configuration, error handling.
``` 

Generated/Modified Code Snippets:
```
week2/app/db.py:1-143 – Replaced ad-hoc helpers with a `Database` class handling connections, schema initialization, and typed row materialization.
week2/app/__init__.py:1-4 – Re-exported the `Database` type and singleton for dependency injection.
week2/app/main.py:1-33 – Added `create_app()`, centralized DB initialization, and static asset mounting.
week2/app/schemas.py:1-40 – Introduced FastAPI request/response models for extraction, action items, and notes.
week2/app/routers/action_items.py:1-72 – Updated endpoints to use Pydantic schemas, dependency-injected DB, LLM toggle, and consistent error handling.
week2/app/routers/notes.py:1-40 – Converted note endpoints to schema-driven handlers with dependency-injected DB access.
week2/app/routers/__init__.py:1-2 – Declared router exports to keep module discovery explicit.
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt: 
```
Use agentic mode to:
1. Integrate the LLM-powered extraction as a new endpoint and add an “Extract LLM” button on the frontend that targets it.
2. Expose an endpoint that lists all notes and add a “List Notes” button that fetches and renders them.
``` 

Generated Code Snippets:
```
week2/app/routers/action_items.py:1-88 – Added shared `_run_extraction` helper plus `/action-items/extract/llm` endpoint to call the LLM pipeline explicitly.
week2/app/routers/notes.py:1-36 – Introduced `GET /notes` handler returning the full note list via the schema models.
week2/frontend/index.html:1-120 – Added “Extract LLM” and “List Notes” buttons, refactored JS to reuse extraction logic, and rendered saved notes client-side.
```


### Exercise 5: Generate a README from the Codebase
Prompt: 
```
Use Cursor to analyze the current codebase and generate a well-structured README.md that covers:
- A brief overview of the project
- How to set up and run the project
- API endpoints and functionality
- Instructions for running the test suite
``` 

Generated Code Snippets:
```
README.md:1-124 – Replaced the stub repository instructions with a detailed overview, setup steps, API reference, frontend usage guide, and testing notes tailored to the Week 2 Action Item Extractor.
```


## SUBMISSION INSTRUCTIONS
1. Hit `Command (⌘) + F` (or `Ctrl + F`) to confirm no placeholder text remains in this file. If no results are found, congratulations – you've completed all required fields. 
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope. 
