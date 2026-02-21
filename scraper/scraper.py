import os
import pandas as pd
from mobfot import MobFot
from config import TEAM_ID

client = MobFot()
_active_progress_prefix = None

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
    if df.empty:
        print(f"  ⚠ No data for {label}")
        return False

    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)

    filepath = os.path.join(output_dir, f"{filename}.csv")
    df.to_csv(filepath, index=False)
    print(f"  ✓ {label} saved: {filepath}")
    return True


def main():
    if not TEAM_ID:
        print("Error: TEAM_ID not set in .env file")
        return

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

    print(f"\nDone! Data saved to: data/")


if __name__ == "__main__":
    main()
