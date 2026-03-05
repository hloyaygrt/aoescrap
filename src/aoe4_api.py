from __future__ import annotations

import re
from urllib.parse import urlparse

import requests

API_BASE_URL = "https://aoe4world.com/api/v0"
_PLAYERS_PATH_RE = re.compile(r"/players/(\d+)")
LEADERBOARD_OPTIONS = (
    "ALL",
    "rm_solo",
    "rm_team",
    "rm_1v1",
    "rm_2v2",
    "rm_3v3",
    "rm_4v4",
    "qm_1v1",
    "qm_2v2",
    "qm_3v3",
    "qm_4v4",
)


class Aoe4ApiError(RuntimeError):
    """Raised when AoE4World API requests fail."""


def parse_profile_id(value: str) -> int:
    """Parse AoE4World profile ID from numeric input or player URL."""
    text = value.strip()
    if not text:
        raise ValueError("Player URL/ID is required.")
    if text.isdigit():
        return int(text)

    parsed = urlparse(text if "://" in text else f"https://{text}")
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    if host != "aoe4world.com":
        raise ValueError("Expected an AoE4World player URL or numeric profile ID.")

    match = _PLAYERS_PATH_RE.search(parsed.path)
    if not match:
        raise ValueError("Could not find profile ID in AoE4World URL.")
    return int(match.group(1))


def parse_leaderboard(value: str) -> str | None:
    """Parse leaderboard selection; returns None for ALL."""
    selected = value.strip().lower()
    if selected == "all":
        return None
    if selected not in LEADERBOARD_OPTIONS[1:]:
        raise ValueError("Unsupported leaderboard option.")
    return selected


def fetch_rm_2v2_games(
    profile_id: int,
    leaderboard: str | None = "rm_2v2",
    session: requests.Session | None = None,
    per_page: int = 100,
    timeout: float = 20.0,
) -> list[dict]:
    """Fetch all games for a profile ID across all pages."""
    if profile_id <= 0:
        raise ValueError("Profile ID must be positive.")
    if per_page <= 0:
        raise ValueError("per_page must be positive.")

    client = session or requests.Session()
    should_close = session is None
    games: list[dict] = []
    page = 1
    url = f"{API_BASE_URL}/players/{profile_id}/games"

    try:
        while True:
            params = {"page": page, "limit": per_page}
            if leaderboard:
                params["leaderboard"] = leaderboard
            try:
                response = client.get(url, params=params, timeout=timeout)
            except requests.RequestException as exc:
                raise Aoe4ApiError("Failed to reach AoE4World API.") from exc

            if response.status_code != 200:
                detail = response.text.strip().replace("\n", " ")[:200]
                raise Aoe4ApiError(
                    f"AoE4World API returned {response.status_code}. {detail}"
                )

            try:
                payload = response.json()
            except ValueError as exc:
                raise Aoe4ApiError("AoE4World API returned invalid JSON.") from exc

            page_games = payload.get("games") or []
            if not isinstance(page_games, list):
                raise Aoe4ApiError("AoE4World API returned malformed games payload.")
            games.extend(page_games)

            count = int(payload.get("count", len(page_games)))
            total_count = payload.get("total_count")
            offset = payload.get("offset", (page - 1) * per_page)

            if count == 0 or not page_games:
                break
            if (
                isinstance(total_count, int)
                and isinstance(offset, int)
                and offset + count >= total_count
            ):
                break
            if isinstance(total_count, int) and len(games) >= total_count:
                break
            page += 1
    finally:
        if should_close:
            client.close()

    return games
