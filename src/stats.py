from __future__ import annotations

from collections import defaultdict
from typing import Any


def build_opponent_civ_stats(games: list[dict[str, Any]], profile_id: int) -> dict[str, Any]:
    """Aggregate per-opponent-civ encounter stats for a target profile."""
    civ_totals: dict[str, dict[str, int]] = defaultdict(
        lambda: {"encounters": 0, "wins": 0}
    )
    total_games = 0
    total_encounters = 0

    for game in games:
        teams = game.get("teams") or []
        player_team_idx, did_win = _find_player_team(teams, profile_id)
        if player_team_idx is None or did_win is None:
            continue

        total_games += 1
        for team_idx, team in enumerate(teams):
            if team_idx == player_team_idx:
                continue
            for member in team or []:
                civ = _extract_civ(member)
                civ_totals[civ]["encounters"] += 1
                civ_totals[civ]["wins"] += int(did_win)
                total_encounters += 1

    rows: list[dict[str, Any]] = []
    for civ, values in civ_totals.items():
        encounters = values["encounters"]
        wins = values["wins"]
        losses = encounters - wins
        win_pct = round((wins / encounters) * 100, 2) if encounters else 0.0
        rows.append(
            {
                "civ": civ,
                "encounters": encounters,
                "wins": wins,
                "losses": losses,
                "win_pct": win_pct,
            }
        )
    rows.sort(key=lambda row: (-row["encounters"], row["civ"]))

    return {
        "total_games": total_games,
        "total_encounters": total_encounters,
        "unique_civs": len(rows),
        "rows": rows,
    }


def _find_player_team(
    teams: list[Any], profile_id: int
) -> tuple[int | None, bool | None]:
    for team_idx, team in enumerate(teams):
        for member in team or []:
            player = member.get("player") or {}
            if player.get("profile_id") != profile_id:
                continue
            result = player.get("result")
            if result == "win":
                return team_idx, True
            if result == "loss":
                return team_idx, False
            return team_idx, None
    return None, None


def _extract_civ(member: dict[str, Any]) -> str:
    player = member.get("player") or {}
    civilization = player.get("civilization")
    if isinstance(civilization, str) and civilization:
        return civilization
    return "unknown"
