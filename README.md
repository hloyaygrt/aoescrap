# AoE4 Opponent-Civ Stats

Streamlit app that calculates your win rate against each opponent civilization using live data from AoE4World.

## Requirements

- Python 3.10+
- `pip`

## Setup

```bash
python3 -m pip install -r requirements.txt
```

## Run

```bash
python3 -m streamlit run app.py
```

## Usage

1. Paste either:
   - numeric profile ID (example: `21742269`), or
   - AoE4World player URL (example: `https://aoe4world.com/players/21742269-thaiyrgag/games?mode=rm_2v2`)
2. Select `Leaderboard` (`ALL` or a specific mode).
3. Click **Fetch games**.
4. Select `Patch`:
   - `ALL`
   - `8338` (hardcoded latest for now)
5. Review metrics and the per-civ table:
   - `encounters`: how many enemy slots used that civ against you
   - `wins` / `losses`: your outcomes in those encounters
   - `win_pct`: your win percentage for that civ

## Notes

- Source endpoint: `https://aoe4world.com/api/v0/players/{profile_id}/games` (optional `leaderboard` filter)
- Pagination is handled automatically until all pages are fetched.
