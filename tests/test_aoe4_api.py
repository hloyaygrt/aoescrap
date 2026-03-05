from __future__ import annotations

import pytest

from src.aoe4_api import (
    fetch_rm_2v2_games,
    parse_leaderboard,
    parse_profile_id,
)


class _FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code
        self.text = ""

    def json(self) -> dict:
        return self._payload


class _FakeSession:
    def __init__(self, payloads_by_page: dict[int, dict]) -> None:
        self.payloads_by_page = payloads_by_page
        self.called_pages: list[int] = []
        self.called_params: list[dict] = []

    def get(self, _url: str, params: dict, timeout: float) -> _FakeResponse:  # noqa: ARG002
        page = params["page"]
        self.called_pages.append(page)
        self.called_params.append(dict(params))
        return _FakeResponse(self.payloads_by_page[page])


def test_parse_profile_id_accepts_numeric() -> None:
    assert parse_profile_id("21742269") == 21742269


def test_parse_profile_id_accepts_aoe4world_url() -> None:
    value = "https://aoe4world.com/players/21742269-thaiyrgag/games?mode=rm_2v2&page=3"
    assert parse_profile_id(value) == 21742269


def test_parse_profile_id_rejects_non_aoe4world_url() -> None:
    with pytest.raises(ValueError):
        parse_profile_id("https://example.com/players/21742269")


def test_parse_leaderboard_supports_all() -> None:
    assert parse_leaderboard("ALL") is None
    assert parse_leaderboard("rm_3v3") == "rm_3v3"


def test_parse_leaderboard_rejects_unknown_value() -> None:
    with pytest.raises(ValueError):
        parse_leaderboard("foo")


def test_fetch_rm_2v2_games_paginates_until_total_count() -> None:
    session = _FakeSession(
        {
            1: {"games": [{"game_id": 1}, {"game_id": 2}], "count": 2, "offset": 0, "total_count": 3},
            2: {"games": [{"game_id": 3}], "count": 1, "offset": 2, "total_count": 3},
        }
    )

    games = fetch_rm_2v2_games(21742269, session=session, per_page=2)
    assert [game["game_id"] for game in games] == [1, 2, 3]
    assert session.called_pages == [1, 2]


def test_fetch_rm_2v2_games_stops_on_empty_page() -> None:
    session = _FakeSession(
        {
            1: {"games": [{"game_id": 1}], "count": 1, "offset": 0, "total_count": 99},
            2: {"games": [], "count": 0, "offset": 1, "total_count": 99},
        }
    )

    games = fetch_rm_2v2_games(21742269, session=session, per_page=1)
    assert [game["game_id"] for game in games] == [1]
    assert session.called_pages == [1, 2]


def test_fetch_rm_2v2_games_omits_leaderboard_for_all() -> None:
    session = _FakeSession(
        {
            1: {"games": [{"game_id": 1}], "count": 1, "offset": 0, "total_count": 1},
        }
    )

    fetch_rm_2v2_games(21742269, leaderboard=None, session=session, per_page=1)
    assert "leaderboard" not in session.called_params[0]
