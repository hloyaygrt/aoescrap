from __future__ import annotations

import streamlit as st

from src.aoe4_api import (
    LEADERBOARD_OPTIONS,
    Aoe4ApiError,
    fetch_rm_2v2_games,
    parse_leaderboard,
    parse_profile_id,
)
from src.stats import build_opponent_civ_stats

HARDCODED_PATCH = 8338


st.set_page_config(page_title="AoE4 Opponent-Civ Stats", layout="wide")
st.title("AoE4 Opponent-Civ Stats")
st.write("Paste an AoE4World player URL or numeric profile ID.")

player_input = st.text_input(
    "Player URL or profile ID",
    placeholder="https://aoe4world.com/players/21742269-thaiyrgag/games?mode=rm_2v2",
)
leaderboard_input = st.selectbox(
    "Leaderboard",
    options=LEADERBOARD_OPTIONS,
    index=LEADERBOARD_OPTIONS.index("rm_2v2"),
)

try:
    leaderboard = parse_leaderboard(leaderboard_input)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

if "games_cache" not in st.session_state:
    st.session_state.games_cache = []
if "cache_key" not in st.session_state:
    st.session_state.cache_key = None

if st.button("Fetch games", type="primary"):
    try:
        profile_id = parse_profile_id(player_input)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    with st.spinner("Fetching games from AoE4World..."):
        try:
            games = fetch_rm_2v2_games(profile_id, leaderboard=leaderboard)
        except Aoe4ApiError as exc:
            st.error(f"Failed to fetch games: {exc}")
            st.stop()

    if not games:
        st.warning("No games found for this filter.")
        st.session_state.games_cache = []
        st.session_state.cache_key = None
        st.stop()

    st.session_state.games_cache = games
    st.session_state.cache_key = (profile_id, leaderboard_input)

try:
    current_profile_id = parse_profile_id(player_input)
except ValueError:
    current_profile_id = None

if st.session_state.cache_key == (current_profile_id, leaderboard_input):
    games = st.session_state.games_cache
    patch_options: list[int | None] = [None, HARDCODED_PATCH]
    patch_input = st.selectbox(
        "Patch",
        options=patch_options,
        format_func=lambda value: "ALL" if value is None else str(value),
    )
    selected_patch = patch_input
    filtered_games = [
        game for game in games if selected_patch is None or game.get("patch") == selected_patch
    ]
    if not filtered_games:
        st.warning("No games found for this patch.")
        st.stop()

    stats = build_opponent_civ_stats(filtered_games, current_profile_id)
    if not stats["rows"]:
        st.warning("No opponent civilization encounters were found.")
        st.stop()

    col1, col2, col3 = st.columns(3)
    col1.metric("Games Parsed", stats["total_games"])
    col2.metric("Opponent Civ Encounters", stats["total_encounters"])
    col3.metric("Unique Opponent Civs", stats["unique_civs"])

    st.dataframe(
        stats["rows"],
        hide_index=True,
        use_container_width=True,
        column_config={
            "civ": "Opponent Civ",
            "encounters": "Encounters",
            "wins": "Wins",
            "losses": "Losses",
            "win_pct": st.column_config.NumberColumn("Win %", format="%.2f%%"),
        },
    )
