import asyncio
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP
from nba_api.live.nba.endpoints import scoreboard

# Initialize FastMCP server
mcp = FastMCP("PengchengMCP Server")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


class RateLimitError(Exception):
    """Raised when an upstream API rejects the request due to rate limits."""


async def make_nws_request(url: str, retries: int = 2) -> dict[str, Any] | None:
    """Make a request to the NWS API with backoff and clearer errors."""

    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    async with httpx.AsyncClient() as client:
        for attempt in range(retries + 1):
            try:
                response = await client.get(url, headers=headers, timeout=30.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                if status_code == 429:
                    if attempt < retries:
                        await asyncio.sleep(2**attempt)
                        continue
                    raise RateLimitError(
                        "The National Weather Service rate-limited the request. Please try again in a moment."
                    ) from exc
                if attempt < retries:
                    await asyncio.sleep(2**attempt)
                    continue
                raise
            except httpx.RequestError as exc:
                if attempt < retries:
                    await asyncio.sleep(2**attempt)
                    continue
                raise RuntimeError("Unable to reach the National Weather Service API") from exc


def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get("event", "Unknown")}
Area: {props.get("areaDesc", "Unknown")}
Severity: {props.get("severity", "Unknown")}
Description: {props.get("description", "No description available")}
Instructions: {props.get("instruction", "No specific instructions provided")}
"""


@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    try:
        data = await make_nws_request(url)
    except RateLimitError as exc:
        return str(exc)
    except Exception as exc:  # pragma: no cover - defensive guard for HTTP issues
        return f"Unable to fetch alerts: {exc}"

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    try:
        points_data = await make_nws_request(points_url)
    except RateLimitError as exc:
        return str(exc)
    except Exception as exc:
        return f"Unable to fetch forecast data for this location: {exc}"

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    try:
        forecast_data = await make_nws_request(forecast_url)
    except RateLimitError as exc:
        return str(exc)
    except Exception as exc:
        return f"Unable to fetch detailed forecast: {exc}"

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period["name"]}:
Temperature: {period["temperature"]}°{period["temperatureUnit"]}
Wind: {period["windSpeed"]} {period["windDirection"]}
Forecast: {period["detailedForecast"]}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)


def _format_team_line(team_data: dict[str, Any]) -> str:
    """Create a readable line for a team's record and score."""

    city = team_data.get("teamCity", "")
    name = team_data.get("teamName", "Team")
    wins = team_data.get("wins", 0)
    losses = team_data.get("losses", 0)
    score = team_data.get("score", 0)
    tri = team_data.get("teamTricode", "")
    return f"{city} {name} ({wins}-{losses}) [{tri}] - {score}"


def _format_leader_line(label: str, leader: dict[str, Any]) -> str:
    """Format the leading scorer/assist line for a team."""

    name = leader.get("name", "TBD")
    points = leader.get("points", 0)
    rebounds = leader.get("rebounds", 0)
    assists = leader.get("assists", 0)
    return f"{label}: {name} ({points} PTS / {rebounds} REB / {assists} AST)"


@mcp.tool()
async def get_today_nba_game() -> str:
    """Summaries of every NBA game scheduled for today."""

    try:
        board = scoreboard.ScoreBoard()
        raw_data = board.get_dict()
    except Exception as exc:  # pragma: no cover - network issues
        return f"Unable to retrieve today's NBA games: {exc}"

    scoreboard_data = raw_data.get("scoreboard", {})
    games = scoreboard_data.get("games", []) if scoreboard_data else []

    if not games:
        return "No NBA games are scheduled for today."

    summaries: list[str] = []
    for game in games:
        game_status = game.get("gameStatusText") or "Scheduled"
        game_clock = game.get("gameClock") or ""
        home_team = game.get("homeTeam", {})
        away_team = game.get("awayTeam", {})
        leaders = game.get("gameLeaders", {})
        home_leader = leaders.get("homeLeaders", {})
        away_leader = leaders.get("awayLeaders", {})

        status_line = game_status
        if game_clock:
            status_line = f"{game_status} — {game_clock}"

        summary = "\n".join(
            [
                status_line,
                _format_team_line(away_team),
                _format_team_line(home_team),
                _format_leader_line("Away leader", away_leader),
                _format_leader_line("Home leader", home_leader),
            ]
        )
        summaries.append(summary)

    return "\n---\n".join(summaries)


def main():
    # Initialize and run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
