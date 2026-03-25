# Week 3 – Weather & NBA MCP Server

This week’s assignment implements a local Model Context Protocol (MCP) server (STDIO transport) that exposes real-world data via three tools:

- **`get_alerts`** – active weather alerts for a U.S. state (National Weather Service `alerts/active/area/{state}`).
- **`get_forecast`** – short-term point forecast for latitude/longitude pairs (NWS `points/{lat},{lon}` + `forecast`).
- **`get_today_nba_game`** – formatted summaries for every NBA game scheduled today (NBA Live Stats `scoreboard/todaysScoreboard_00.json`).

All code lives in `week3/server/`, with `main.py` as the entrypoint using `FastMCP`. The server is designed for STDIO clients like Claude Desktop, Cursor, or the OpenAI MCP Inspector.

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or `pip`
- macOS/Linux shell that can launch the MCP server process

No API keys are required—both upstream APIs are public but do enforce rate limits. The implementation adds exponential backoff and clear error messaging for HTTP 429 responses.

## Install & Run

```bash
cd week3/server
# Install dependencies (choose one)
uv sync            # recommended
# or: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# Launch the STDIO MCP server
uv run python main.py
```

The process stays attached to STDIO, so keep it running while your MCP client connects.

## MCP Client Configuration (Claude Desktop example)

Add an entry to `cline_mcp_settings.json` (Path: `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`):

```jsonc
{
  "mcpServers": {
    "week3-weather-nba": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "main.py"
      ],
      "cwd": "/Users/penzhou/Desktop/Github/modern-software-dev-assignments/week3/server"
    }
  }
}
```

Restart Claude Desktop (or reload MCP servers) so it discovers the new STDIO server.

## Tool Reference

| Tool | Parameters | External API Calls | Notes |
| --- | --- | --- | --- |
| `get_alerts` | `state: str` (two-letter code) | `https://api.weather.gov/alerts/active/area/{state}` | Returns a readable list of alert event name, area, severity, description, and instructions. Handles HTTP/network errors with clear messages and retries on transient failures. |
| `get_forecast` | `latitude: float`, `longitude: float` | `https://api.weather.gov/points/{lat},{lon}` → follow-up `forecast` URL | Provides the next five forecast periods (name, temperature, wind, detailed forecast). Surfaces rate-limit warnings if the NWS API responds with 429. |
| `get_today_nba_game` | _none_ | `https://stats.nba.com/stats/scoreboard/todaysScoreboard_00.json` via `nba_api` | Returns formatted summaries per game: status/clock, away/home lines, and top performers. Gracefully handles upstream failures and no-game days. |

## Example Invocation Flow

1. Start the server: `uv run python main.py` (keep it running).
2. In Claude Desktop, open a chat and run `/mcp tools` to ensure `week3-weather-nba` is visible.
3. Trigger tools via natural prompts, e.g.:
   - “Use `get_alerts` for CA to see current advisories.”
   - “Call `get_forecast` for 37.7749, -122.4194.”
   - “What are today’s NBA games? Use `get_today_nba_game`.”
4. Review the structured response returned by the MCP tool invocation.

## Troubleshooting & Resilience

- **429 rate limits** – The server retries twice with exponential backoff and then surfaces a friendly message asking you to retry later.
- **Network failures** – HTTP client errors are caught and reported instead of crashing the MCP process.
- **No games scheduled** – The NBA tool returns an explanatory string rather than raw JSON.
- **Logging** – FastMCP keeps stdout reserved for the protocol; use stderr logging if you extend functionality.

For more implementation details (including developer notes), see `week3/server/README.md` and the source code in `week3/server/main.py`.
