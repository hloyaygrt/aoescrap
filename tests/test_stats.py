from __future__ import annotations

from src.stats import build_opponent_civ_stats


def test_build_opponent_civ_stats_aggregates_per_occurrence() -> None:
    profile_id = 21742269
    games = [
        {
            "teams": [
                [
                    {"player": {"profile_id": profile_id, "result": "win", "civilization": "sengoku_daimyo"}},
                    {"player": {"profile_id": 100, "result": "win", "civilization": "french"}},
                ],
                [
                    {"player": {"profile_id": 200, "result": "loss", "civilization": "french"}},
                    {"player": {"profile_id": 201, "result": "loss", "civilization": "english"}},
                ],
            ]
        },
        {
            "teams": [
                [
                    {"player": {"profile_id": 300, "result": "win", "civilization": "french"}},
                    {"player": {"profile_id": 301, "result": "win", "civilization": "french"}},
                ],
                [
                    {"player": {"profile_id": profile_id, "result": "loss", "civilization": "sengoku_daimyo"}},
                    {"player": {"profile_id": 101, "result": "loss", "civilization": "ayyubids"}},
                ],
            ]
        },
    ]

    stats = build_opponent_civ_stats(games, profile_id)
    by_civ = {row["civ"]: row for row in stats["rows"]}

    assert stats["total_games"] == 2
    assert stats["total_encounters"] == 4
    assert by_civ["french"] == {
        "civ": "french",
        "encounters": 3,
        "wins": 1,
        "losses": 2,
        "win_pct": 33.33,
    }
    assert by_civ["english"] == {
        "civ": "english",
        "encounters": 1,
        "wins": 1,
        "losses": 0,
        "win_pct": 100.0,
    }


def test_duplicate_opponent_civ_in_same_game_counts_twice() -> None:
    profile_id = 21742269
    games = [
        {
            "teams": [
                [
                    {"player": {"profile_id": profile_id, "result": "win", "civilization": "sengoku_daimyo"}},
                    {"player": {"profile_id": 100, "result": "win", "civilization": "french"}},
                ],
                [
                    {"player": {"profile_id": 200, "result": "loss", "civilization": "french"}},
                    {"player": {"profile_id": 201, "result": "loss", "civilization": "french"}},
                ],
            ]
        }
    ]

    stats = build_opponent_civ_stats(games, profile_id)
    assert stats["rows"] == [
        {
            "civ": "french",
            "encounters": 2,
            "wins": 2,
            "losses": 0,
            "win_pct": 100.0,
        }
    ]


def test_game_without_target_profile_is_ignored() -> None:
    stats = build_opponent_civ_stats(
        [
            {
                "teams": [
                    [{"player": {"profile_id": 1, "result": "win", "civilization": "french"}}],
                    [{"player": {"profile_id": 2, "result": "loss", "civilization": "english"}}],
                ]
            }
        ],
        profile_id=21742269,
    )

    assert stats["total_games"] == 0
    assert stats["rows"] == []
