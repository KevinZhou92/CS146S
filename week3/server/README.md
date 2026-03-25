## Overview

This folder contains the MCP server implementation for Week 3. Everything runs via STDIO using FastMCP.

### Tools

1. `get_alerts(state: str)` – Fetches active National Weather Service alerts for a two-letter state code.
2. `get_forecast(latitude: float, longitude: float)` – Retrieves the next five forecast periods using the NWS `points` and `forecast` endpoints.
3. `get_today_nba_game()` – Summaries of today’s NBA games via `nba_api.live.nba.endpoints.scoreboard`.

Each tool returns human-readable strings suitable for MCP chat clients.

## Setup

```bash
cd week3/server
uv sync            # or python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

## Running Locally

```bash
uv run python main.py
```

Keep the process attached to STDIO; Claude Desktop or other MCP clients should launch it using the same command with `cwd` pointing here.

## Implementation Notes

- `main.py` centralizes HTTP helper logic with retries/backoff and custom error messages for API rate limits.
- NBA summaries format home/away lines plus leader stats to keep outputs concise.
- Logging should go to stderr if added later—stdout is reserved for the MCP transport.
