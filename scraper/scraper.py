import argparse
import os
import sys
import pandas as pd
from mobfot import MobFot
from config import TEAM_ID, SUPABASE_SCHEMA, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_URL

client = MobFot()
_active_progress_prefix = None

OUTPUT_COLUMNS = {
    "fixtures": [
        "id",
        "page_url",
        "opponent",
        "opponent_id",
        "home_away",
        "display_tournament",
        "tournament",
        "tournament_id",
        "round",
        "result",
        "not_started",
        "status",
    ],
    "squad": [
        "id",
        "name",
        "position_group",
        "position",
        "shirt_number",
        "country_code",
        "country",
        "height",
        "age",
        "date_of_birth",
        "rating",
        "goals",
        "assists",
        "yellow_cards",
        "red_cards",
        "market_value",
    ],
    "player_stats": [
        "category",
        "category_display",
        "player_id",
        "player_name",
        "player_country",
        "team_id",
        "team_name",
        "rank",
        "value",
        "format",
    ],
    "team_info": [
        "team_id",
        "team_name",
        "team_short_name",
        "season",
        "selected_season",
    ],
    "league_table": [
        "league",
        "position",
        "team_id",
        "team_name",
        "played",
        "wins",
        "draws",
        "losses",
        "goals_for",
        "goals_against",
        "goal_difference",
        "points",
    ],
    "transfers": [
        "type",
        "player_id",
        "player_name",
        "position",
        "from_club",
        "from_club_id",
        "to_club",
        "to_club_id",
        "transfer_date",
        "fee",
        "market_value",
        "on_loan",
    ],
}

def get_team_data(team_id):
    print("Fetching team data...")
    return client.get_team(team_id)


def print_progress(prefix, current, total, width=30):
    global _active_progress_prefix

    total = max(int(total), 0)
    current = max(int(current), 0)
    if total == 0:
        if _active_progress_prefix is not None:
            print()
            _active_progress_prefix = None
        print(f"  {prefix}: [no items]")
        return

    ratio = min(max(current / total, 0), 1)
    if _active_progress_prefix is not None and _active_progress_prefix != prefix:
        print()

    filled = int(width * ratio)
    bar = "=" * filled + "." * (width - filled)
    print(
        f"\r  {prefix}: [{bar}] {current}/{total} ({ratio * 100:5.1f}%)",
        end="",
        flush=True,
    )

    if current >= total:
        print()
        _active_progress_prefix = None
    else:
        _active_progress_prefix = prefix


def format_label(name):
    return str(name).replace("_", " ").title()


def parse_fixtures(team_data):
    all_fixtures = []

    fixtures_data = team_data.get("fixtures", {})
    all_fixtures_dict = fixtures_data.get("allFixtures", {})
    fixtures_list = all_fixtures_dict.get("fixtures", [])
    total = len(fixtures_list)

    for idx, fixture in enumerate(fixtures_list, 1):
        opponent = fixture.get("opponent", {})
        tournament = fixture.get("tournament", {})
        result = fixture.get("result", {})
        if not isinstance(tournament, dict):
            tournament = {}

        # Round/matchday naming varies by competition payload.
        round_value = (
            fixture.get("round")
            or fixture.get("roundName")
            or fixture.get("matchDay")
            or fixture.get("matchday")
            or tournament.get("round")
            or tournament.get("roundName")
            or tournament.get("matchDay")
            or tournament.get("matchday")
        )

        row = {
            "id": fixture.get("id"),
            "page_url": fixture.get("pageUrl"),
            "opponent": opponent.get("name"),
            "opponent_id": opponent.get("id"),
            "home_away": fixture.get("home"),
            "display_tournament": fixture.get("displayTournament"),
            "tournament": tournament.get("name"),
            "tournament_id": tournament.get("id"),
            "round": round_value,
            "result": result.get("scoreStr") if isinstance(result, dict) else None,
            "not_started": fixture.get("notStarted"),
            "status": fixture.get("status"),
        }
        all_fixtures.append(row)
        print_progress("Fixtures", idx, total)

    return pd.DataFrame(all_fixtures)


def parse_squad(team_data):
    all_players = []

    squad_data = team_data.get("squad", {})
    squad_groups = squad_data.get("squad", [])

    total = sum(len(group.get("members", [])) for group in squad_groups)
    current = 0

    for group in squad_groups:
        position_group = group.get("title")
        members = group.get("members", [])

        for player in members:
            role = player.get("role", {})
            row = {
                "id": player.get("id"),
                "name": player.get("name"),
                "position_group": position_group,
                "position": role.get("fallback") if isinstance(role, dict) else role,
                "shirt_number": player.get("shirtNumber"),
                "country_code": player.get("ccode"),
                "country": player.get("cname"),
                "height": player.get("height"),
                "age": player.get("age"),
                "date_of_birth": player.get("dateOfBirth"),
                "rating": player.get("rating"),
                "goals": player.get("goals"),
                "assists": player.get("assists"),
                "yellow_cards": player.get("ycards"),
                "red_cards": player.get("rcards"),
                "market_value": player.get("transferValue"),
            }
            all_players.append(row)
            current += 1
            print_progress("Squad", current, total)

    return pd.DataFrame(all_players)


def parse_player_stats(team_data):
    all_stats = []

    stats_data = team_data.get("stats", {})
    categories = stats_data.get("players", [])

    total = sum(len(category.get("topThree", [])) for category in categories)
    current = 0

    for category in categories:
        category_name = category.get("name")
        category_header = category.get("header")

        for player in category.get("topThree", []):
            stat = player.get("stat", {})
            row = {
                "category": category_name,
                "category_display": category_header,
                "player_id": player.get("id"),
                "player_name": player.get("name"),
                "player_country": player.get("ccode"),
                "team_id": player.get("teamId"),
                "team_name": player.get("teamName"),
                "rank": player.get("rank"),
                "value": stat.get("value"),
                "format": stat.get("format"),
            }
            all_stats.append(row)
            current += 1
            print_progress("Player Stats", current, total)

    return pd.DataFrame(all_stats)


def parse_overview(team_data):
    overview = team_data.get("overview", {})

    team_info = {
        "team_id": team_data.get("details", {}).get("id"),
        "team_name": team_data.get("details", {}).get("name"),
        "team_short_name": team_data.get("details", {}).get("shortName"),
        "season": overview.get("season"),
        "selected_season": overview.get("selectedSeason"),
    }

    return pd.DataFrame([team_info])


def parse_table(team_data):
    tables = team_data.get("table", [])

    all_rows = []
    total = sum(len(table.get("tableData", [])) for table in tables)
    current = 0

    for table in tables:
        league_name = table.get("leagueName", "Unknown League")
        table_data = table.get("tableData", [])

        for idx, team in enumerate(table_data, 1):
            row = {
                "league": league_name,
                "position": team.get("position", idx),
                "team_id": team.get("id"),
                "team_name": team.get("name"),
                "played": team.get("played"),
                "wins": team.get("wins"),
                "draws": team.get("draws"),
                "losses": team.get("losses"),
                "goals_for": team.get("goalsFor"),
                "goals_against": team.get("goalsAgainst"),
                "goal_difference": team.get("goalDifference"),
                "points": team.get("points"),
            }
            all_rows.append(row)
            current += 1
            print_progress("League Table", current, total)

    return pd.DataFrame(all_rows)


def parse_transfers(team_data):
    transfers_data = team_data.get("transfers", {}).get("data", {})

    all_transfers = []
    total = sum(
        len(transfer_list)
        for transfer_list in transfers_data.values()
        if isinstance(transfer_list, list)
    )
    current = 0

    for transfer_type, transfer_list in transfers_data.items():
        if not isinstance(transfer_list, list):
            continue

        for transfer in transfer_list:
            position = transfer.get("position", {})
            fee = transfer.get("fee", {})

            row = {
                "type": transfer_type,
                "player_id": transfer.get("playerId"),
                "player_name": transfer.get("name"),
                "position": position.get("label")
                if isinstance(position, dict)
                else position,
                "from_club": transfer.get("fromClub"),
                "from_club_id": transfer.get("fromClubId"),
                "to_club": transfer.get("toClub"),
                "to_club_id": transfer.get("toClubId"),
                "transfer_date": transfer.get("transferDate"),
                "fee": fee.get("feeText") if isinstance(fee, dict) else None,
                "market_value": transfer.get("marketValue"),
                "on_loan": transfer.get("onLoan"),
            }
            all_transfers.append(row)
            current += 1
            print_progress("Transfers", current, total)

    return pd.DataFrame(all_transfers)


def save_csv(df, filename):
    label = format_label(filename)
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)

    filepath = os.path.join(output_dir, f"{filename}.csv")
    export_df = df.reindex(columns=OUTPUT_COLUMNS.get(filename, list(df.columns)))
    export_df.to_csv(filepath, index=False)

    if export_df.empty:
        print(f"  ⚠ No data for {label}; wrote empty file: {filepath}")
        return False

    print(f"  ✓ {label} saved: {filepath}")
    return True


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch FotMob team data and export CSV files."
    )
    parser.add_argument(
        "--sync-supabase",
        action="store_true",
        help="Also sync scraped data to Supabase.",
    )
    return parser.parse_args()


def validate_supabase_env():
    missing = []
    if not SUPABASE_URL:
        missing.append("SUPABASE_URL")
    if not SUPABASE_SERVICE_ROLE_KEY:
        missing.append("SUPABASE_SERVICE_ROLE_KEY")
    return missing


def main():
    args = parse_args()

    if not TEAM_ID:
        print("Error: TEAM_ID not set in .env file")
        return 1

    if args.sync_supabase:
        missing_vars = validate_supabase_env()
        if missing_vars:
            print(
                "Error: --sync-supabase requires env vars: "
                + ", ".join(missing_vars)
            )
            return 1

    print(f"Fetching data for team ID: {TEAM_ID}\n")

    team_data = get_team_data(TEAM_ID)

    print("\nProcessing data...")

    fixtures_df = parse_fixtures(team_data)
    save_csv(fixtures_df, "fixtures")

    squad_df = parse_squad(team_data)
    save_csv(squad_df, "squad")

    stats_df = parse_player_stats(team_data)
    save_csv(stats_df, "player_stats")

    team_info_df = parse_overview(team_data)
    save_csv(team_info_df, "team_info")

    table_df = parse_table(team_data)
    save_csv(table_df, "league_table")

    transfers_df = parse_transfers(team_data)
    save_csv(transfers_df, "transfers")

    dataframes = {
        "fixtures": fixtures_df,
        "squad": squad_df,
        "player_stats": stats_df,
        "team_info": team_info_df,
        "league_table": table_df,
        "transfers": transfers_df,
    }

    if args.sync_supabase:
        try:
            source_team_id = int(TEAM_ID)
        except ValueError:
            print("Error: TEAM_ID must be an integer for Supabase sync")
            return 1

        print("\nSyncing data to Supabase...")
        try:
            from supabase_sync import sync_to_supabase

            sync_summary = sync_to_supabase(
                dataframes=dataframes,
                source_team_id=source_team_id,
                supabase_url=SUPABASE_URL,
                supabase_service_role_key=SUPABASE_SERVICE_ROLE_KEY,
                schema=SUPABASE_SCHEMA,
            )
        except Exception as exc:
            print(f"Error: Supabase sync failed: {exc}")
            return 1

        for table_name, result in sync_summary.items():
            label = format_label(table_name)
            print(f"  ✓ {label} synced: {result['inserted_rows']} rows")

    print(f"\nDone! Data saved to: data/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
