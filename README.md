# FotMob Scraper

Scrapes team data from FotMob and exports it to CSV files, with a Svelte UI to explore squad, fixtures, stats, and transfers.

## Demo

![App demo](docs/demo.gif)

## What It Scrapes

- Team overview and metadata
- Fixtures and match highlights
- Squad and lineup snapshots
- Player and team stat rankings
- Transfers
- League table and legend
- Venue, trophies, coach history, FAQs, tabs
- Full historical table rows and rules from linked archives
- Match page datasets scraped from public HTML hydration:
  - match details
  - match events
  - match stats
  - shot maps
  - match lineups
  - per-player match stats
- Player page datasets scraped from public HTML hydration:
  - player profiles
  - recent matches
  - career entries
  - market value history
  - trophies
  - trait comparisons

All generated CSVs are written to `data/`.

## Project Structure

- `scraper/scraper.py`: main scraping/export script
- `scraper/config.py`: loads `.env` values
- `scraper/supabase_sync.py`: optional Supabase sync logic
- `supabase/schema.sql`: SQL schema for Supabase Query Editor
- `data/`: generated CSV output
- `client/`: Svelte + Vite frontend

## Requirements

- Python 3.10+
- Node.js 18+

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env`:

```bash
cp .env.example .env
```

Set your team:

```env
TEAM_ID=9773
```

Optional Supabase sync env vars:

```env
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_SCHEMA=public
```

## Run Scraper

```bash
python3 scraper/scraper.py
```

Optional: sync every exported CSV dataset to Supabase in the same run:

```bash
python3 scraper/scraper.py --sync-supabase
```

Replace all synced rows for this team before inserting the new export:

```bash
python3 scraper/scraper.py --sync-supabase --overwrite-supabase
```

Expected outputs include:

- Core: `data/fixtures.csv`, `data/squad.csv`, `data/player_stats.csv`, `data/team_info.csv`, `data/league_table.csv`, `data/transfers.csv`
- Team depth: `data/player_stat_rankings.csv`, `data/team_stat_rankings.csv`, `data/match_highlights.csv`, `data/team_form.csv`, `data/top_players.csv`, `data/venue.csv`, `data/table_legend.csv`, `data/coach_history.csv`, `data/trophies.csv`, `data/historical_seasons.csv`, `data/historical_table_rows.csv`, `data/historical_table_rules.csv`, `data/faq.csv`, `data/tabs.csv`, `data/last_lineup.csv`, `data/last_lineup_players.csv`
- Match depth: `data/match_details.csv`, `data/match_events.csv`, `data/match_stats.csv`, `data/match_shots.csv`, `data/match_lineup_players.csv`, `data/match_player_stats.csv`
- Player depth: `data/player_profiles.csv`, `data/player_recent_matches.csv`, `data/player_career_entries.csv`, `data/player_market_values.csv`, `data/player_trophies.csv`, `data/player_traits.csv`

## Run Frontend

```bash
cd client
npm install
npm run dev
```

Open `http://localhost:5173`.

The client visualizes these exports across the existing `Overview`, `Squad`, `Fixtures`, `Stats`, `History`, `Transfers`, and `Raw Data` tabs, including player compare mode, role-specific summaries, mini trend charts, honor summaries, fixture shot maps, and card/track event timelines with filters.

## Supabase Schema

Run `supabase/schema.sql` in Supabase Query Editor before using `--sync-supabase`.
The schema drops and recreates all exported-data tables in `public`, with typed columns, primary keys on core entities, and indexes for common lookups.
Most relationship-heavy or analytics-heavy tables also get targeted indexes to keep syncs and queries scalable.
Default schema used by the scraper is `public`.

## Dependencies

- [`mobfot`](https://pypi.org/project/mobfot/)
- `pandas`
- `python-dotenv`
- `supabase`
- Svelte + Vite
