import argparse
import gzip
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

import pandas as pd
from mobfot import MobFot

from config import (
    SUPABASE_SCHEMA,
    SUPABASE_SERVICE_ROLE_KEY,
    SUPABASE_URL,
    TEAM_ID,
)

client = MobFot()
_active_progress_prefix = None
_url_cache = {}
_text_cache = {}

OUTPUT_COLUMNS = {
    "fixtures": [
        "id",
        "page_url",
        "opponent",
        "opponent_id",
        "opponent_score",
        "home_team_id",
        "home_team_name",
        "home_team_score",
        "away_team_id",
        "away_team_name",
        "away_team_score",
        "team_is_home",
        "home_away",
        "display_tournament",
        "tournament",
        "tournament_id",
        "tournament_stage",
        "round",
        "result",
        "result_code",
        "not_started",
        "utc_time",
        "status_started",
        "status_finished",
        "status_cancelled",
        "status_awarded",
        "status_reason_short",
        "status_reason_long",
        "start_day",
        "live_time_short",
        "live_time_long",
        "stats_summary",
        "stats_league_names",
        "status",
    ],
    "squad": [
        "id",
        "player_image_url",
        "name",
        "first_name",
        "last_name",
        "position_group",
        "position",
        "role_key",
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
        "exclude_from_ranking",
    ],
    "player_stats": [
        "category",
        "category_display",
        "localized_title_id",
        "stat_name",
        "fetch_all_url",
        "player_id",
        "player_image_url",
        "player_name",
        "player_country",
        "team_id",
        "team_name",
        "rank",
        "value",
        "format",
        "fractions",
        "category_order",
        "category_type",
    ],
    "player_stat_rankings": [
        "category",
        "category_display",
        "stat_name",
        "title",
        "subtitle",
        "league_name",
        "player_id",
        "player_image_url",
        "player_name",
        "player_country",
        "team_id",
        "team_name",
        "rank",
        "value",
        "sub_value",
        "minutes_played",
        "matches_played",
        "stat_count",
        "positions",
        "team_color",
        "stat_format",
        "substat_format",
        "stat_decimals",
        "substat_decimals",
        "fetch_all_url",
    ],
    "team_stat_rankings": [
        "category",
        "category_display",
        "stat_name",
        "title",
        "league_name",
        "team_id",
        "team_name",
        "team_country",
        "rank",
        "value",
        "sub_value",
        "matches_played",
        "stat_count",
        "team_color",
        "stat_format",
        "substat_format",
        "stat_decimals",
        "substat_decimals",
        "fetch_all_url",
    ],
    "team_info": [
        "team_id",
        "team_name",
        "team_short_name",
        "team_type",
        "gender",
        "country_code",
        "season",
        "selected_season",
        "latest_season",
        "primary_league_id",
        "primary_league_name",
        "primary_league_url",
        "team_url",
        "team_logo_url",
        "seo_path",
        "can_sync_calendar",
        "stadium_name",
        "stadium_city",
        "stadium_country",
        "stadium_latitude",
        "stadium_longitude",
        "surface",
        "capacity",
        "opened",
        "color_primary",
        "color_alt",
        "color_away",
        "color_away_alt",
        "color_dark_mode",
        "color_light_mode",
        "font_dark_mode",
        "font_light_mode",
    ],
    "league_table": [
        "league",
        "league_id",
        "country_code",
        "page_url",
        "table_type",
        "position",
        "team_id",
        "team_name",
        "team_short_name",
        "played",
        "wins",
        "draws",
        "losses",
        "goals_for",
        "goals_against",
        "goal_difference",
        "points",
        "featured_in_match",
        "deduction",
        "ongoing",
        "qualification_color",
        "scores_str",
        "recent_form",
        "next_opponent_id",
        "next_opponent_name",
        "next_match_id",
        "next_match_utc_time",
    ],
    "table_legend": [
        "league",
        "league_id",
        "title",
        "key",
        "color",
        "indices",
    ],
    "transfers": [
        "type",
        "player_id",
        "player_name",
        "position",
        "position_key",
        "from_club",
        "from_club_id",
        "to_club",
        "to_club_id",
        "transfer_date",
        "from_date",
        "to_date",
        "fee",
        "fee_value",
        "fee_localized",
        "market_value",
        "on_loan",
        "contract_extension",
        "transfer_type_text",
        "transfer_type_key",
        "transfer_text",
    ],
    "match_highlights": [
        "match_type",
        "id",
        "page_url",
        "opponent",
        "opponent_id",
        "home_team_id",
        "home_team_name",
        "home_team_score",
        "away_team_id",
        "away_team_name",
        "away_team_score",
        "display_tournament",
        "tournament",
        "tournament_id",
        "not_started",
        "utc_time",
        "status_started",
        "status_finished",
        "status_cancelled",
        "status_awarded",
        "score_str",
        "reason_short",
        "reason_long",
        "start_day",
        "live_time_short",
        "live_time_long",
        "stats_summary",
    ],
    "team_form": [
        "sequence",
        "result",
        "result_string",
        "score",
        "utc_time",
        "tournament_name",
        "match_url",
        "opponent_id",
        "opponent_name",
        "is_home",
        "team_page_url",
        "opponent_logo_url",
        "tooltip_json",
    ],
    "top_players": [
        "group_name",
        "group_label",
        "see_all_link",
        "player_id",
        "player_image_url",
        "player_name",
        "player_country",
        "team_id",
        "team_name",
        "rank",
        "value",
        "stat_name",
        "format",
        "fractions",
        "team_color_dark",
        "team_color_light",
    ],
    "venue": [
        "stadium_name",
        "city",
        "latitude",
        "longitude",
        "surface",
        "capacity",
        "opened",
    ],
    "coach_history": [
        "coach_id",
        "coach_name",
        "season",
        "league_id",
        "league_name",
        "wins",
        "draws",
        "losses",
        "points_per_game",
        "win_percentage",
    ],
    "trophies": [
        "name",
        "tournament_template_id",
        "area",
        "country_code",
        "won",
        "runnerup",
        "season_won",
        "season_runnerup",
    ],
    "historical_seasons": [
        "season_name",
        "tournament_name",
        "tournament_id",
        "template_id",
        "stage_id",
        "position",
        "number_of_teams",
        "points",
        "wins",
        "draws",
        "losses",
        "is_consecutive",
        "table_link",
    ],
    "historical_table_rows": [
        "season_name",
        "tournament_name",
        "league_id",
        "table_name",
        "country_code",
        "position",
        "team_id",
        "team_name",
        "points",
        "wins",
        "draws",
        "losses",
        "goals_for",
        "goals_against",
        "home_points",
        "home_wins",
        "home_draws",
        "home_losses",
        "home_goals_for",
        "home_goals_against",
        "change",
        "table_link",
    ],
    "historical_table_rules": [
        "season_name",
        "tournament_name",
        "league_id",
        "table_name",
        "country_code",
        "description",
        "color",
        "key",
        "value",
        "table_link",
    ],
    "faq": [
        "source",
        "question",
        "answer",
    ],
    "tabs": ["tab"],
    "last_lineup": [
        "team_id",
        "team_name",
        "formation",
        "team_rating",
        "average_starter_age",
        "total_starter_market_value",
        "coach_id",
        "coach_name",
    ],
    "last_lineup_players": [
        "section",
        "player_id",
        "name",
        "first_name",
        "last_name",
        "age",
        "country_name",
        "country_code",
        "shirt_number",
        "position_id",
        "usual_playing_position_id",
        "is_captain",
        "market_value",
        "performance_rating",
        "season_goals",
        "season_assists",
        "season_rating",
        "events",
        "horizontal_x",
        "horizontal_y",
        "vertical_x",
        "vertical_y",
    ],
    "match_details": [
        "fixture_id",
        "match_id",
        "match_name",
        "league_id",
        "league_name",
        "parent_league_id",
        "country_code",
        "match_round",
        "league_round_name",
        "match_time_utc",
        "match_time_utc_date",
        "started",
        "finished",
        "coverage_level",
        "home_team_id",
        "home_team_name",
        "home_team_score",
        "away_team_id",
        "away_team_name",
        "away_team_score",
        "status_score_str",
        "status_reason_short",
        "status_reason_long",
        "player_of_match_id",
        "player_of_match_name",
        "attendance",
        "referee_name",
        "referee_country",
        "stadium_name",
        "stadium_city",
        "stadium_country",
        "stadium_lat",
        "stadium_long",
        "stadium_capacity",
        "stadium_surface",
        "qa_count",
        "home_top_player_count",
        "away_top_player_count",
    ],
    "match_events": [
        "fixture_id",
        "match_id",
        "event_id",
        "react_key",
        "time",
        "time_str",
        "overload_time",
        "overload_time_str",
        "type",
        "is_home",
        "team_side",
        "player_id",
        "player_name",
        "profile_url",
        "card",
        "card_description",
        "home_score",
        "away_score",
        "name_str",
        "full_name",
        "event_payload",
    ],
    "match_stats": [
        "fixture_id",
        "match_id",
        "period",
        "group_title",
        "group_key",
        "stat_title",
        "stat_key",
        "home_value",
        "away_value",
        "format",
        "stat_type",
        "highlighted",
    ],
    "match_shots": [
        "fixture_id",
        "match_id",
        "shot_id",
        "player_id",
        "player_name",
        "team_id",
        "team_color",
        "period",
        "minute",
        "minute_added",
        "event_type",
        "situation",
        "shot_type",
        "expected_goals",
        "expected_goals_on_target",
        "is_on_target",
        "is_blocked",
        "is_own_goal",
        "is_saved_off_line",
        "is_from_inside_box",
        "x",
        "y",
        "goal_crossed_y",
        "goal_crossed_z",
        "blocked_x",
        "blocked_y",
        "keeper_id",
    ],
    "match_lineup_players": [
        "fixture_id",
        "match_id",
        "team_side",
        "team_id",
        "team_name",
        "formation",
        "team_rating",
        "section",
        "player_id",
        "name",
        "first_name",
        "last_name",
        "age",
        "country_name",
        "country_code",
        "shirt_number",
        "position_id",
        "usual_playing_position_id",
        "market_value",
        "performance_rating",
        "horizontal_x",
        "horizontal_y",
        "vertical_x",
        "vertical_y",
    ],
    "match_player_stats": [
        "fixture_id",
        "match_id",
        "player_id",
        "player_name",
        "team_id",
        "team_name",
        "is_goalkeeper",
        "section_title",
        "section_key",
        "stat_title",
        "stat_key",
        "stat_value",
        "stat_total",
        "stat_type",
    ],
    "player_profiles": [
        "player_id",
        "player_image_url",
        "name",
        "birth_date",
        "gender",
        "status",
        "data_provider",
        "is_captain",
        "is_coach",
        "primary_team_id",
        "primary_team_name",
        "on_loan",
        "primary_position",
        "height_cm",
        "shirt_number",
        "age",
        "preferred_foot",
        "country",
        "country_code",
        "market_value",
        "contract_end_utc",
        "next_match_id",
        "next_match_date",
        "next_match_league",
        "main_league_id",
        "main_league_name",
        "main_league_season",
        "main_league_stats",
        "traits_key",
        "traits_title",
        "injury_information",
        "meta_json",
    ],
    "player_recent_matches": [
        "player_id",
        "match_id",
        "match_date",
        "match_page_url",
        "league_id",
        "league_name",
        "stage",
        "team_id",
        "team_name",
        "opponent_team_id",
        "opponent_team_name",
        "is_home_team",
        "home_score",
        "away_score",
        "minutes_played",
        "goals",
        "assists",
        "yellow_cards",
        "red_cards",
        "rating",
        "is_top_rating",
        "player_of_the_match",
        "on_bench",
    ],
    "player_career_entries": [
        "player_id",
        "career_stage",
        "entry_type",
        "team_id",
        "team_name",
        "team_gender",
        "show_team_gender",
        "transfer_type",
        "start_date",
        "end_date",
        "active",
        "role",
        "season_name",
        "appearances",
        "goals",
        "assists",
        "rating",
        "league_id",
        "league_name",
        "tournament_id",
        "is_friendly",
    ],
    "player_market_values": [
        "player_id",
        "date",
        "value",
        "currency",
        "lower_bound",
        "upper_bound",
        "source",
        "team_id",
        "team_name",
        "is_period_start",
    ],
    "player_trophies": [
        "player_id",
        "trophy_type",
        "team_id",
        "team_name",
        "country_code",
        "league_id",
        "league_name",
        "seasons_won",
        "seasons_runner_up",
    ],
    "player_traits": [
        "player_id",
        "traits_key",
        "traits_title",
        "item_key",
        "item_title",
        "item_value",
    ],
}

SYNC_TABLES = {
    "fixtures",
    "squad",
    "player_stats",
    "team_info",
    "league_table",
    "transfers",
}


def player_image_url(player_id):
    if not player_id:
        return None
    return f"https://images.fotmob.com/image_resources/playerimages/{player_id}.png"


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


def json_value(value):
    if value is None:
        return None
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=True, separators=(",", ":"))
    return value


def get_stat_pair(stat_pairs, label):
    for key, value in stat_pairs:
        if key == label:
            return value
    return None


def split_scores(scores_str):
    if not scores_str or "-" not in str(scores_str):
        return None, None
    parts = [part.strip() for part in str(scores_str).split("-", 1)]
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return None, None


def extract_round(fixture, tournament):
    tournament = tournament if isinstance(tournament, dict) else {}
    return (
        fixture.get("round")
        or fixture.get("roundName")
        or fixture.get("matchDay")
        or fixture.get("matchday")
        or tournament.get("round")
        or tournament.get("roundName")
        or tournament.get("matchDay")
        or tournament.get("matchday")
    )


def fetch_json_url(url):
    if not url:
        return None
    if url in _url_cache:
        return _url_cache[url]

    request = urllib.request.Request(url, headers={"Accept-Encoding": "gzip"})
    with urllib.request.urlopen(request) as response:
        raw = response.read()
        if response.headers.get("Content-Encoding") == "gzip" or raw[:2] == b"\x1f\x8b":
            raw = gzip.decompress(raw)
    data = json.loads(raw.decode("utf-8"))
    _url_cache[url] = data
    return data


def fetch_text_url(url):
    if not url:
        return None
    if url in _text_cache:
        return _text_cache[url]

    request = urllib.request.Request(
        url,
        headers={
            "Accept-Encoding": "gzip",
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.fotmob.com/",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read()
        if response.headers.get("Content-Encoding") == "gzip" or raw[:2] == b"\x1f\x8b":
            raw = gzip.decompress(raw)
    text = raw.decode("utf-8", errors="ignore")
    _text_cache[url] = text
    return text


def extract_next_data_from_html(html):
    if not html:
        return None
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        html,
        re.DOTALL,
    )
    if not match:
        return None
    return json.loads(match.group(1))


def fetch_match_page_data(fixture):
    page_url = fixture.get("pageUrl") or fixture.get("page_url")
    if not page_url:
        return None
    try:
        html = fetch_text_url(f"https://www.fotmob.com{page_url}")
    except Exception:
        return None
    payload = extract_next_data_from_html(html)
    if not payload:
        return None
    return payload.get("props", {}).get("pageProps", {})


def fetch_player_page_data(player_id):
    if not player_id:
        return None
    try:
        html = fetch_text_url(f"https://www.fotmob.com/players/{player_id}")
    except Exception:
        return None
    payload = extract_next_data_from_html(html)
    if not payload:
        return None
    page_props = payload.get("props", {}).get("pageProps", {})
    return page_props.get("data") or page_props.get("fallback", {}).get(
        f"player:{player_id}"
    )


def parse_fixtures(team_data):
    source_team_id = team_data.get("details", {}).get("id")
    all_fixtures = []
    fixtures_data = team_data.get("fixtures", {})
    fixtures_list = fixtures_data.get("allFixtures", {}).get("fixtures", [])
    total = len(fixtures_list)

    for idx, fixture in enumerate(fixtures_list, 1):
        opponent = fixture.get("opponent", {})
        home = fixture.get("home", {})
        away = fixture.get("away", {})
        tournament = fixture.get("tournament", {})
        status = fixture.get("status", {})
        live_time = fixture.get("liveTime", {})
        stats = fixture.get("stats", {})
        team_is_home = None
        if (
            isinstance(home, dict)
            and home.get("id") is not None
            and source_team_id is not None
        ):
            team_is_home = str(home.get("id")) == str(source_team_id)

        row = {
            "id": fixture.get("id"),
            "page_url": fixture.get("pageUrl"),
            "opponent": opponent.get("name"),
            "opponent_id": opponent.get("id"),
            "opponent_score": opponent.get("score"),
            "home_team_id": home.get("id"),
            "home_team_name": home.get("name"),
            "home_team_score": home.get("score"),
            "away_team_id": away.get("id"),
            "away_team_name": away.get("name"),
            "away_team_score": away.get("score"),
            "team_is_home": team_is_home,
            "home_away": json_value(home if team_is_home else away),
            "display_tournament": fixture.get("displayTournament"),
            "tournament": tournament.get("name"),
            "tournament_id": tournament.get("leagueId") or tournament.get("id"),
            "tournament_stage": tournament.get("stage"),
            "round": extract_round(fixture, tournament),
            "result": status.get("scoreStr") if isinstance(status, dict) else None,
            "result_code": fixture.get("result"),
            "not_started": fixture.get("notStarted"),
            "utc_time": status.get("utcTime") if isinstance(status, dict) else None,
            "status_started": status.get("started")
            if isinstance(status, dict)
            else None,
            "status_finished": status.get("finished")
            if isinstance(status, dict)
            else None,
            "status_cancelled": status.get("cancelled")
            if isinstance(status, dict)
            else None,
            "status_awarded": status.get("awarded")
            if isinstance(status, dict)
            else None,
            "status_reason_short": (status.get("reason") or {}).get("short")
            if isinstance(status, dict)
            else None,
            "status_reason_long": (status.get("reason") or {}).get("long")
            if isinstance(status, dict)
            else None,
            "start_day": fixture.get("startDay"),
            "live_time_short": live_time.get("short")
            if isinstance(live_time, dict)
            else None,
            "live_time_long": live_time.get("long")
            if isinstance(live_time, dict)
            else None,
            "stats_summary": json_value(
                stats.get("stats") if isinstance(stats, dict) else stats
            ),
            "stats_league_names": json_value(stats.get("leagueNames"))
            if isinstance(stats, dict)
            else None,
            "status": json_value(status),
        }
        all_fixtures.append(row)
        print_progress("Fixtures", idx, total)

    return pd.DataFrame(all_fixtures)


def parse_squad(team_data):
    all_players = []
    squad_groups = team_data.get("squad", {}).get("squad", [])
    total = sum(len(group.get("members", [])) for group in squad_groups)
    current = 0

    for group in squad_groups:
        position_group = group.get("title")
        for player in group.get("members", []):
            role = player.get("role", {})
            row = {
                "id": player.get("id"),
                "player_image_url": player_image_url(player.get("id")),
                "name": player.get("name"),
                "first_name": player.get("firstName"),
                "last_name": player.get("lastName"),
                "position_group": position_group,
                "position": role.get("fallback") if isinstance(role, dict) else role,
                "role_key": role.get("key") if isinstance(role, dict) else None,
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
                "exclude_from_ranking": player.get("excludeFromRanking"),
            }
            all_players.append(row)
            current += 1
            print_progress("Squad", current, total)

    return pd.DataFrame(all_players)


def parse_player_stats(team_data):
    all_stats = []
    categories = team_data.get("stats", {}).get("players", [])
    total = sum(len(category.get("topThree", [])) for category in categories)
    current = 0

    for category in categories:
        for player in category.get("topThree", []):
            stat = player.get("stat", {})
            row = {
                "category": category.get("name"),
                "category_display": category.get("header"),
                "localized_title_id": category.get("localizedTitleId"),
                "stat_name": stat.get("name"),
                "fetch_all_url": category.get("fetchAllUrl"),
                "player_id": player.get("id"),
                "player_image_url": player_image_url(player.get("id")),
                "player_name": player.get("name"),
                "player_country": player.get("ccode"),
                "team_id": player.get("teamId"),
                "team_name": player.get("teamName"),
                "rank": player.get("rank"),
                "value": stat.get("value"),
                "format": stat.get("format"),
                "fractions": stat.get("fractions"),
                "category_order": category.get("order"),
                "category_type": category.get("category"),
            }
            all_stats.append(row)
            current += 1
            print_progress("Player Stats", current, total)

    return pd.DataFrame(all_stats)


def parse_player_stat_rankings(team_data):
    source_team_id = str(team_data.get("details", {}).get("id"))
    rows = []
    categories = team_data.get("stats", {}).get("players", [])
    total = len(categories)

    for idx, category in enumerate(categories, 1):
        payload = fetch_json_url(category.get("fetchAllUrl"))
        for top_list in (payload or {}).get("TopLists", []):
            for entry in top_list.get("StatList", []):
                if str(entry.get("TeamId")) != source_team_id:
                    continue
                rows.append(
                    {
                        "category": category.get("name"),
                        "category_display": category.get("header"),
                        "stat_name": top_list.get("StatName"),
                        "title": top_list.get("Title"),
                        "subtitle": top_list.get("Subtitle"),
                        "league_name": (payload or {}).get("LeagueName"),
                        "player_id": entry.get("ParticiantId"),
                        "player_image_url": player_image_url(entry.get("ParticiantId")),
                        "player_name": entry.get("ParticipantName"),
                        "player_country": entry.get("ParticipantCountryCode"),
                        "team_id": entry.get("TeamId"),
                        "team_name": entry.get("TeamName"),
                        "rank": entry.get("Rank"),
                        "value": entry.get("StatValue"),
                        "sub_value": entry.get("SubStatValue"),
                        "minutes_played": entry.get("MinutesPlayed"),
                        "matches_played": entry.get("MatchesPlayed"),
                        "stat_count": entry.get("StatValueCount"),
                        "positions": json_value(entry.get("Positions")),
                        "team_color": entry.get("TeamColor"),
                        "stat_format": top_list.get("StatFormat"),
                        "substat_format": top_list.get("SubstatFormat"),
                        "stat_decimals": top_list.get("StatDecimals"),
                        "substat_decimals": top_list.get("SubstatDecimals"),
                        "fetch_all_url": category.get("fetchAllUrl"),
                    }
                )
        print_progress("Player Rankings", idx, total)

    return pd.DataFrame(rows)


def parse_team_stat_rankings(team_data):
    source_team_id = str(team_data.get("details", {}).get("id"))
    rows = []
    categories = team_data.get("stats", {}).get("teams", [])
    total = len(categories)

    for idx, category in enumerate(categories, 1):
        payload = fetch_json_url(category.get("fetchAllUrl"))
        for top_list in (payload or {}).get("TopLists", []):
            for entry in top_list.get("StatList", []):
                if str(entry.get("TeamId")) != source_team_id:
                    continue
                rows.append(
                    {
                        "category": category.get("stat") or category.get("header"),
                        "category_display": category.get("header"),
                        "stat_name": top_list.get("StatName"),
                        "title": top_list.get("Title"),
                        "league_name": (payload or {}).get("LeagueName"),
                        "team_id": entry.get("TeamId"),
                        "team_name": entry.get("ParticipantName"),
                        "team_country": entry.get("ParticipantCountryCode"),
                        "rank": entry.get("Rank"),
                        "value": entry.get("StatValue"),
                        "sub_value": entry.get("SubStatValue"),
                        "matches_played": entry.get("MatchesPlayed"),
                        "stat_count": entry.get("StatValueCount"),
                        "team_color": entry.get("TeamColor"),
                        "stat_format": top_list.get("StatFormat"),
                        "substat_format": top_list.get("SubstatFormat"),
                        "stat_decimals": top_list.get("StatDecimals"),
                        "substat_decimals": top_list.get("SubstatDecimals"),
                        "fetch_all_url": category.get("fetchAllUrl"),
                    }
                )
        print_progress("Team Rankings", idx, total)

    return pd.DataFrame(rows)


def parse_overview(team_data):
    details = team_data.get("details", {})
    overview = team_data.get("overview", {})
    venue = overview.get("venue", {})
    widget = venue.get("widget", {}) if isinstance(venue, dict) else {}
    stat_pairs = venue.get("statPairs", []) if isinstance(venue, dict) else []
    sports = details.get("sportsTeamJSONLD", {})
    location = sports.get("location", {}) if isinstance(sports, dict) else {}
    address = location.get("address", {}) if isinstance(location, dict) else {}
    geo = location.get("geo", {}) if isinstance(location, dict) else {}
    colors = overview.get("teamColors", {})
    color_map = team_data.get("history", {}).get("teamColorMap", {})
    member_of = sports.get("memberOf", {}) if isinstance(sports, dict) else {}

    team_info = {
        "team_id": details.get("id"),
        "team_name": details.get("name"),
        "team_short_name": details.get("shortName"),
        "team_type": details.get("type"),
        "gender": details.get("gender"),
        "country_code": details.get("country"),
        "season": overview.get("season"),
        "selected_season": overview.get("selectedSeason"),
        "latest_season": details.get("latestSeason"),
        "primary_league_id": details.get("primaryLeagueId"),
        "primary_league_name": details.get("primaryLeagueName"),
        "primary_league_url": member_of.get("url"),
        "team_url": sports.get("url"),
        "team_logo_url": sports.get("logo"),
        "seo_path": details.get("seopath"),
        "can_sync_calendar": details.get("canSyncCalendar"),
        "stadium_name": widget.get("name") or location.get("name"),
        "stadium_city": widget.get("city") or address.get("addressLocality"),
        "stadium_country": address.get("addressCountry"),
        "stadium_latitude": (widget.get("location") or [None, None])[0]
        if isinstance(widget.get("location"), list)
        else geo.get("latitude"),
        "stadium_longitude": (widget.get("location") or [None, None])[1]
        if isinstance(widget.get("location"), list)
        else geo.get("longitude"),
        "surface": get_stat_pair(stat_pairs, "Surface"),
        "capacity": get_stat_pair(stat_pairs, "Capacity"),
        "opened": get_stat_pair(stat_pairs, "Opened"),
        "color_primary": color_map.get("color"),
        "color_alt": color_map.get("colorAlternate"),
        "color_away": color_map.get("colorAway"),
        "color_away_alt": color_map.get("colorAwayAlternate"),
        "color_dark_mode": colors.get("darkMode"),
        "color_light_mode": colors.get("lightMode"),
        "font_dark_mode": colors.get("fontDarkMode"),
        "font_light_mode": colors.get("fontLightMode"),
    }

    return pd.DataFrame([team_info])


def parse_table(team_data):
    all_rows = []
    legend_rows = []
    tables = team_data.get("table", [])
    total = 0
    for table in tables:
        table_groups = (table.get("data") or {}).get("table") or {}
        total += sum(
            len(rows) for rows in table_groups.values() if isinstance(rows, list)
        )

    current = 0
    for table in tables:
        table_data = table.get("data", {})
        league_name = table_data.get("leagueName")
        league_id = table_data.get("leagueId")
        country_code = table_data.get("ccode")
        page_url = table_data.get("pageUrl")
        next_opponents = table.get("nextOpponent", {})
        team_form_map = table.get("teamForm", {})

        for legend in table_data.get("legend", []):
            legend_rows.append(
                {
                    "league": league_name,
                    "league_id": league_id,
                    "title": legend.get("title"),
                    "key": legend.get("tKey"),
                    "color": legend.get("color"),
                    "indices": json_value(legend.get("indices")),
                }
            )

        for table_type, rows in (table_data.get("table") or {}).items():
            if not isinstance(rows, list):
                continue
            for row in rows:
                current += 1
                team_id = row.get("id")
                next_opponent = next_opponents.get(str(team_id), [])
                recent_form = team_form_map.get(str(team_id), [])
                goals_for, goals_against = split_scores(row.get("scoresStr"))
                all_rows.append(
                    {
                        "league": league_name,
                        "league_id": league_id,
                        "country_code": country_code,
                        "page_url": page_url,
                        "table_type": table_type,
                        "position": row.get("idx"),
                        "team_id": team_id,
                        "team_name": row.get("name"),
                        "team_short_name": row.get("shortName"),
                        "played": row.get("played"),
                        "wins": row.get("wins"),
                        "draws": row.get("draws"),
                        "losses": row.get("losses"),
                        "goals_for": goals_for,
                        "goals_against": goals_against,
                        "goal_difference": row.get("goalConDiff"),
                        "points": row.get("pts"),
                        "featured_in_match": row.get("featuredInMatch"),
                        "deduction": row.get("deduction"),
                        "ongoing": row.get("ongoing"),
                        "qualification_color": row.get("qualColor"),
                        "scores_str": row.get("scoresStr"),
                        "recent_form": "".join(
                            item.get("resultString", "")
                            for item in recent_form
                            if isinstance(item, dict)
                        ),
                        "next_opponent_id": next_opponent[0]
                        if len(next_opponent) > 0
                        else None,
                        "next_opponent_name": next_opponent[1]
                        if len(next_opponent) > 1
                        else None,
                        "next_match_id": next_opponent[2]
                        if len(next_opponent) > 2
                        else None,
                        "next_match_utc_time": next_opponent[5]
                        if len(next_opponent) > 5
                        else None,
                    }
                )
                print_progress("League Table", current, total)

    return pd.DataFrame(all_rows), pd.DataFrame(legend_rows)


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
            transfer_type_info = transfer.get("transferType", {})
            row = {
                "type": transfer_type,
                "player_id": transfer.get("playerId"),
                "player_name": transfer.get("name"),
                "position": position.get("label")
                if isinstance(position, dict)
                else position,
                "position_key": position.get("key")
                if isinstance(position, dict)
                else None,
                "from_club": transfer.get("fromClub"),
                "from_club_id": transfer.get("fromClubId"),
                "to_club": transfer.get("toClub"),
                "to_club_id": transfer.get("toClubId"),
                "transfer_date": transfer.get("transferDate"),
                "from_date": transfer.get("fromDate"),
                "to_date": transfer.get("toDate"),
                "fee": fee.get("feeText") if isinstance(fee, dict) else None,
                "fee_value": fee.get("value") if isinstance(fee, dict) else None,
                "fee_localized": fee.get("localizedFeeText")
                if isinstance(fee, dict)
                else None,
                "market_value": transfer.get("marketValue"),
                "on_loan": transfer.get("onLoan"),
                "contract_extension": transfer.get("contractExtension"),
                "transfer_type_text": transfer_type_info.get("text")
                if isinstance(transfer_type_info, dict)
                else None,
                "transfer_type_key": transfer_type_info.get("localizationKey")
                if isinstance(transfer_type_info, dict)
                else None,
                "transfer_text": json_value(transfer.get("transferText")),
            }
            all_transfers.append(row)
            current += 1
            print_progress("Transfers", current, total)

    return pd.DataFrame(all_transfers)


def parse_match_highlights(team_data):
    rows = []
    overview = team_data.get("overview", {})
    for match_type in ("nextMatch", "lastMatch"):
        fixture = overview.get(match_type, {})
        if not isinstance(fixture, dict) or not fixture:
            continue
        opponent = fixture.get("opponent", {})
        home = fixture.get("home", {})
        away = fixture.get("away", {})
        tournament = fixture.get("tournament", {})
        status = fixture.get("status", {})
        live_time = fixture.get("liveTime", {})
        rows.append(
            {
                "match_type": "next" if match_type == "nextMatch" else "last",
                "id": fixture.get("id"),
                "page_url": fixture.get("pageUrl"),
                "opponent": opponent.get("name"),
                "opponent_id": opponent.get("id"),
                "home_team_id": home.get("id"),
                "home_team_name": home.get("name"),
                "home_team_score": home.get("score"),
                "away_team_id": away.get("id"),
                "away_team_name": away.get("name"),
                "away_team_score": away.get("score"),
                "display_tournament": fixture.get("displayTournament"),
                "tournament": tournament.get("name"),
                "tournament_id": tournament.get("leagueId") or tournament.get("id"),
                "not_started": fixture.get("notStarted"),
                "utc_time": status.get("utcTime") if isinstance(status, dict) else None,
                "status_started": status.get("started")
                if isinstance(status, dict)
                else None,
                "status_finished": status.get("finished")
                if isinstance(status, dict)
                else None,
                "status_cancelled": status.get("cancelled")
                if isinstance(status, dict)
                else None,
                "status_awarded": status.get("awarded")
                if isinstance(status, dict)
                else None,
                "score_str": status.get("scoreStr")
                if isinstance(status, dict)
                else None,
                "reason_short": (status.get("reason") or {}).get("short")
                if isinstance(status, dict)
                else None,
                "reason_long": (status.get("reason") or {}).get("long")
                if isinstance(status, dict)
                else None,
                "start_day": fixture.get("startDay"),
                "live_time_short": live_time.get("short")
                if isinstance(live_time, dict)
                else None,
                "live_time_long": live_time.get("long")
                if isinstance(live_time, dict)
                else None,
                "stats_summary": json_value((fixture.get("stats") or {}).get("stats")),
            }
        )
    return pd.DataFrame(rows)


def parse_team_form(team_data):
    source_team_id = str(team_data.get("details", {}).get("id"))
    rows = []
    team_form = team_data.get("overview", {}).get("teamForm", [])
    total = len(team_form)

    for idx, item in enumerate(team_form, 1):
        home = item.get("home", {})
        away = item.get("away", {})
        is_home = str(home.get("id")) == source_team_id if home else None
        opponent = away if is_home else home
        rows.append(
            {
                "sequence": idx,
                "result": item.get("result"),
                "result_string": item.get("resultString"),
                "score": item.get("score"),
                "utc_time": (item.get("date") or {}).get("utcTime"),
                "tournament_name": item.get("tournamentName"),
                "match_url": item.get("linkToMatch"),
                "opponent_id": opponent.get("id")
                if isinstance(opponent, dict)
                else None,
                "opponent_name": opponent.get("name")
                if isinstance(opponent, dict)
                else None,
                "is_home": is_home,
                "team_page_url": item.get("teamPageUrl"),
                "opponent_logo_url": item.get("imageUrl"),
                "tooltip_json": json_value(item.get("tooltipText")),
            }
        )
        print_progress("Team Form", idx, total)

    return pd.DataFrame(rows)


def parse_top_players(team_data):
    rows = []
    overview_top_players = team_data.get("overview", {}).get("topPlayers", {})
    groups = {
        "byRating": "Rating",
        "byGoals": "Goals",
        "byAssists": "Assists",
    }
    total = sum(
        len((overview_top_players.get(group_name) or {}).get("players", []))
        for group_name in groups
    )
    current = 0

    for group_name, group_label in groups.items():
        group = overview_top_players.get(group_name, {})
        for player in group.get("players", []):
            stat = player.get("stat", {})
            colors = player.get("teamColors", {})
            rows.append(
                {
                    "group_name": group_name,
                    "group_label": group_label,
                    "see_all_link": group.get("seeAllLink"),
                    "player_id": player.get("id"),
                    "player_image_url": player_image_url(player.get("id")),
                    "player_name": player.get("name"),
                    "player_country": player.get("ccode"),
                    "team_id": player.get("teamId"),
                    "team_name": player.get("teamName"),
                    "rank": player.get("rank"),
                    "value": player.get("value"),
                    "stat_name": stat.get("name"),
                    "format": stat.get("format"),
                    "fractions": stat.get("fractions"),
                    "team_color_dark": colors.get("darkMode"),
                    "team_color_light": colors.get("lightMode"),
                }
            )
            current += 1
            print_progress("Top Players", current, total)

    return pd.DataFrame(rows)


def parse_venue(team_data):
    venue = team_data.get("overview", {}).get("venue", {})
    widget = venue.get("widget", {}) if isinstance(venue, dict) else {}
    stat_pairs = venue.get("statPairs", []) if isinstance(venue, dict) else []
    row = {
        "stadium_name": widget.get("name"),
        "city": widget.get("city"),
        "latitude": (widget.get("location") or [None, None])[0]
        if isinstance(widget.get("location"), list)
        else None,
        "longitude": (widget.get("location") or [None, None])[1]
        if isinstance(widget.get("location"), list)
        else None,
        "surface": get_stat_pair(stat_pairs, "Surface"),
        "capacity": get_stat_pair(stat_pairs, "Capacity"),
        "opened": get_stat_pair(stat_pairs, "Opened"),
    }
    return pd.DataFrame([row])


def parse_coach_history(team_data):
    rows = []
    coach_history = team_data.get("history", {}).get("coachHistory", [])
    total = len(coach_history)
    for idx, coach in enumerate(coach_history, 1):
        rows.append(
            {
                "coach_id": coach.get("id"),
                "coach_name": coach.get("name"),
                "season": coach.get("season"),
                "league_id": coach.get("leagueId"),
                "league_name": coach.get("leagueName"),
                "wins": coach.get("win"),
                "draws": coach.get("draw"),
                "losses": coach.get("loss"),
                "points_per_game": coach.get("pointsPerGame"),
                "win_percentage": coach.get("winPercentage"),
            }
        )
        print_progress("Coach History", idx, total)
    return pd.DataFrame(rows)


def parse_trophies(team_data):
    rows = []
    trophy_list = team_data.get("history", {}).get("trophyList", [])
    total = len(trophy_list)
    for idx, trophy in enumerate(trophy_list, 1):
        keys = [
            "name",
            "tournamentTemplateId",
            "area",
            "ccode",
            "won",
            "runnerup",
            "season_won",
            "season_runnerup",
        ]
        lengths = [
            len(trophy.get(key, []))
            for key in keys
            if isinstance(trophy.get(key), list)
        ]
        row_count = max(lengths or [1])
        for row_idx in range(row_count):
            rows.append(
                {
                    "name": (trophy.get("name") or [None])[row_idx]
                    if isinstance(trophy.get("name"), list)
                    else trophy.get("name"),
                    "tournament_template_id": (
                        trophy.get("tournamentTemplateId") or [None]
                    )[row_idx]
                    if isinstance(trophy.get("tournamentTemplateId"), list)
                    else trophy.get("tournamentTemplateId"),
                    "area": (trophy.get("area") or [None])[row_idx]
                    if isinstance(trophy.get("area"), list)
                    else trophy.get("area"),
                    "country_code": (trophy.get("ccode") or [None])[row_idx]
                    if isinstance(trophy.get("ccode"), list)
                    else trophy.get("ccode"),
                    "won": (trophy.get("won") or [None])[row_idx]
                    if isinstance(trophy.get("won"), list)
                    else trophy.get("won"),
                    "runnerup": (trophy.get("runnerup") or [None])[row_idx]
                    if isinstance(trophy.get("runnerup"), list)
                    else trophy.get("runnerup"),
                    "season_won": (trophy.get("season_won") or [None])[row_idx]
                    if isinstance(trophy.get("season_won"), list)
                    else trophy.get("season_won"),
                    "season_runnerup": (trophy.get("season_runnerup") or [None])[
                        row_idx
                    ]
                    if isinstance(trophy.get("season_runnerup"), list)
                    else trophy.get("season_runnerup"),
                }
            )
        print_progress("Trophies", idx, total)
    return pd.DataFrame(rows)


def parse_historical_seasons(team_data):
    rows = []
    ranks = team_data.get("history", {}).get("historicalTableData", {}).get("ranks", [])
    total = len(ranks)
    for idx, season in enumerate(ranks, 1):
        stats = season.get("stats", {})
        rows.append(
            {
                "season_name": season.get("seasonName"),
                "tournament_name": season.get("tournamentName"),
                "tournament_id": season.get("tournamentId"),
                "template_id": season.get("templateId"),
                "stage_id": season.get("stageId"),
                "position": season.get("position"),
                "number_of_teams": season.get("numberOfTeams"),
                "points": stats.get("points"),
                "wins": stats.get("wins"),
                "draws": stats.get("draws"),
                "losses": stats.get("loss"),
                "is_consecutive": season.get("isConsecutive"),
                "table_link": season.get("tableLink"),
            }
        )
        print_progress("Historical Seasons", idx, total)
    return pd.DataFrame(rows)


def parse_historical_tables(team_data):
    row_records = []
    rule_records = []
    ranks = team_data.get("history", {}).get("historicalTableData", {}).get("ranks", [])
    total = len(ranks)

    for idx, season in enumerate(ranks, 1):
        table_link = season.get("tableLink")
        if not table_link:
            print_progress("Historical Tables", idx, total)
            continue

        try:
            xml_text = fetch_text_url(table_link)
        except Exception:
            print_progress("Historical Tables", idx, total)
            continue
        if not xml_text:
            print_progress("Historical Tables", idx, total)
            continue

        root = ET.fromstring(xml_text)
        table_name = root.attrib.get("name")
        country_code = root.attrib.get("ccode")
        league_id = root.attrib.get("lid")

        for position, team in enumerate(root.findall("t"), 1):
            row_records.append(
                {
                    "season_name": season.get("seasonName"),
                    "tournament_name": season.get("tournamentName"),
                    "league_id": league_id,
                    "table_name": table_name,
                    "country_code": country_code,
                    "position": position,
                    "team_id": team.attrib.get("id"),
                    "team_name": team.attrib.get("name"),
                    "points": team.attrib.get("p"),
                    "wins": team.attrib.get("w"),
                    "draws": team.attrib.get("d"),
                    "losses": team.attrib.get("l"),
                    "goals_for": team.attrib.get("g"),
                    "goals_against": team.attrib.get("c"),
                    "home_points": team.attrib.get("hp"),
                    "home_wins": team.attrib.get("hw"),
                    "home_draws": team.attrib.get("hd"),
                    "home_losses": team.attrib.get("hl"),
                    "home_goals_for": team.attrib.get("hg"),
                    "home_goals_against": team.attrib.get("hc"),
                    "change": team.attrib.get("change"),
                    "table_link": table_link,
                }
            )

        rules = root.find("rules")
        if rules is not None:
            for rule in rules.findall("ti"):
                rule_records.append(
                    {
                        "season_name": season.get("seasonName"),
                        "tournament_name": season.get("tournamentName"),
                        "league_id": league_id,
                        "table_name": table_name,
                        "country_code": country_code,
                        "description": rule.attrib.get("desc"),
                        "color": rule.attrib.get("color"),
                        "key": rule.attrib.get("tkey"),
                        "value": rule.attrib.get("value"),
                        "table_link": table_link,
                    }
                )

        print_progress("Historical Tables", idx, total)

    return pd.DataFrame(row_records), pd.DataFrame(rule_records)


def parse_match_pages(team_data):
    detail_rows = []
    event_rows = []
    stat_rows = []
    shot_rows = []
    lineup_rows = []
    player_stat_rows = []

    fixtures = team_data.get("fixtures", {}).get("allFixtures", {}).get("fixtures", [])
    total = len(fixtures)

    for idx, fixture in enumerate(fixtures, 1):
        page_data = fetch_match_page_data(fixture)
        if not page_data:
            print_progress("Match Pages", idx, total)
            continue

        general = page_data.get("general", {})
        header = page_data.get("header", {})
        content = page_data.get("content", {})
        status = header.get("status", {})
        teams = header.get("teams", [])
        home_team = teams[0] if len(teams) > 0 else {}
        away_team = teams[1] if len(teams) > 1 else {}
        match_facts = content.get("matchFacts", {})
        info_box = match_facts.get("infoBox", {})
        player_of_match = match_facts.get("playerOfTheMatch", {})
        top_players = match_facts.get("topPlayers", {})
        fixture_id = fixture.get("id")
        match_id = general.get("matchId") or fixture_id

        detail_rows.append(
            {
                "fixture_id": fixture_id,
                "match_id": match_id,
                "match_name": general.get("matchName"),
                "league_id": general.get("leagueId"),
                "league_name": general.get("leagueName"),
                "parent_league_id": general.get("parentLeagueId"),
                "country_code": general.get("countryCode"),
                "match_round": general.get("matchRound"),
                "league_round_name": general.get("leagueRoundName"),
                "match_time_utc": general.get("matchTimeUTC"),
                "match_time_utc_date": general.get("matchTimeUTCDate"),
                "started": general.get("started"),
                "finished": general.get("finished"),
                "coverage_level": general.get("coverageLevel"),
                "home_team_id": home_team.get("id")
                or (general.get("homeTeam") or {}).get("id"),
                "home_team_name": home_team.get("name")
                or (general.get("homeTeam") or {}).get("name"),
                "home_team_score": home_team.get("score"),
                "away_team_id": away_team.get("id")
                or (general.get("awayTeam") or {}).get("id"),
                "away_team_name": away_team.get("name")
                or (general.get("awayTeam") or {}).get("name"),
                "away_team_score": away_team.get("score"),
                "status_score_str": status.get("scoreStr"),
                "status_reason_short": (status.get("reason") or {}).get("short"),
                "status_reason_long": (status.get("reason") or {}).get("long"),
                "player_of_match_id": player_of_match.get("id")
                if isinstance(player_of_match, dict)
                else None,
                "player_of_match_name": player_of_match.get("name")
                if isinstance(player_of_match, dict)
                else None,
                "attendance": info_box.get("Attendance"),
                "referee_name": (info_box.get("Referee") or {}).get("text")
                if isinstance(info_box.get("Referee"), dict)
                else None,
                "referee_country": (info_box.get("Referee") or {}).get("country")
                if isinstance(info_box.get("Referee"), dict)
                else None,
                "stadium_name": (info_box.get("Stadium") or {}).get("name")
                if isinstance(info_box.get("Stadium"), dict)
                else None,
                "stadium_city": (info_box.get("Stadium") or {}).get("city")
                if isinstance(info_box.get("Stadium"), dict)
                else None,
                "stadium_country": (info_box.get("Stadium") or {}).get("country")
                if isinstance(info_box.get("Stadium"), dict)
                else None,
                "stadium_lat": (info_box.get("Stadium") or {}).get("lat")
                if isinstance(info_box.get("Stadium"), dict)
                else None,
                "stadium_long": (info_box.get("Stadium") or {}).get("long")
                if isinstance(info_box.get("Stadium"), dict)
                else None,
                "stadium_capacity": (info_box.get("Stadium") or {}).get("capacity")
                if isinstance(info_box.get("Stadium"), dict)
                else None,
                "stadium_surface": (info_box.get("Stadium") or {}).get("surface")
                if isinstance(info_box.get("Stadium"), dict)
                else None,
                "qa_count": len(match_facts.get("QAData", [])),
                "home_top_player_count": len(top_players.get("homeTopPlayers", []))
                if isinstance(top_players, dict)
                else 0,
                "away_top_player_count": len(top_players.get("awayTopPlayers", []))
                if isinstance(top_players, dict)
                else 0,
            }
        )

        events = (match_facts.get("events") or {}).get("events", [])
        for event in events:
            event_rows.append(
                {
                    "fixture_id": fixture_id,
                    "match_id": match_id,
                    "event_id": event.get("eventId"),
                    "react_key": event.get("reactKey"),
                    "time": event.get("time"),
                    "time_str": event.get("timeStr"),
                    "overload_time": event.get("overloadTime"),
                    "overload_time_str": event.get("overloadTimeStr"),
                    "type": event.get("type"),
                    "is_home": event.get("isHome"),
                    "team_side": "home" if event.get("isHome") else "away",
                    "player_id": event.get("playerId"),
                    "player_name": (event.get("player") or {}).get("name")
                    or event.get("fullName"),
                    "profile_url": event.get("profileUrl"),
                    "card": event.get("card"),
                    "card_description": event.get("cardDescription"),
                    "home_score": event.get("homeScore"),
                    "away_score": event.get("awayScore"),
                    "name_str": event.get("nameStr"),
                    "full_name": event.get("fullName"),
                    "event_payload": json_value(event),
                }
            )

        periods = (content.get("stats") or {}).get("Periods", {})
        for period_name, period_data in periods.items():
            for stat_group in period_data.get("stats", []):
                for item in stat_group.get("stats", []):
                    values = (
                        item.get("stats", [])
                        if isinstance(item.get("stats"), list)
                        else []
                    )
                    stat_rows.append(
                        {
                            "fixture_id": fixture_id,
                            "match_id": match_id,
                            "period": period_name,
                            "group_title": stat_group.get("title"),
                            "group_key": stat_group.get("key"),
                            "stat_title": item.get("title"),
                            "stat_key": item.get("key"),
                            "home_value": values[0] if len(values) > 0 else None,
                            "away_value": values[1] if len(values) > 1 else None,
                            "format": item.get("format"),
                            "stat_type": item.get("type"),
                            "highlighted": item.get("highlighted"),
                        }
                    )

        for shot in (content.get("shotmap") or {}).get("shots", []):
            shot_rows.append(
                {
                    "fixture_id": fixture_id,
                    "match_id": match_id,
                    "shot_id": shot.get("id"),
                    "player_id": shot.get("playerId"),
                    "player_name": shot.get("playerName") or shot.get("fullName"),
                    "team_id": shot.get("teamId"),
                    "team_color": shot.get("teamColor"),
                    "period": shot.get("period"),
                    "minute": shot.get("min"),
                    "minute_added": shot.get("minAdded"),
                    "event_type": shot.get("eventType"),
                    "situation": shot.get("situation"),
                    "shot_type": shot.get("shotType"),
                    "expected_goals": shot.get("expectedGoals"),
                    "expected_goals_on_target": shot.get("expectedGoalsOnTarget"),
                    "is_on_target": shot.get("isOnTarget"),
                    "is_blocked": shot.get("isBlocked"),
                    "is_own_goal": shot.get("isOwnGoal"),
                    "is_saved_off_line": shot.get("isSavedOffLine"),
                    "is_from_inside_box": shot.get("isFromInsideBox"),
                    "x": shot.get("x"),
                    "y": shot.get("y"),
                    "goal_crossed_y": shot.get("goalCrossedY"),
                    "goal_crossed_z": shot.get("goalCrossedZ"),
                    "blocked_x": shot.get("blockedX"),
                    "blocked_y": shot.get("blockedY"),
                    "keeper_id": shot.get("keeperId"),
                }
            )

        lineup = content.get("lineup", {})
        for side_key, team_key in (("home", "homeTeam"), ("away", "awayTeam")):
            lineup_team = lineup.get(team_key, {})
            for section_name, players in (
                ("starter", lineup_team.get("starters", [])),
                ("sub", lineup_team.get("subs", [])),
            ):
                for player in players:
                    horizontal = player.get("horizontalLayout", {})
                    vertical = player.get("verticalLayout", {})
                    performance = player.get("performance", {})
                    lineup_rows.append(
                        {
                            "fixture_id": fixture_id,
                            "match_id": match_id,
                            "team_side": side_key,
                            "team_id": lineup_team.get("id"),
                            "team_name": lineup_team.get("name"),
                            "formation": lineup_team.get("formation"),
                            "team_rating": lineup_team.get("rating"),
                            "section": section_name,
                            "player_id": player.get("id"),
                            "name": player.get("name"),
                            "first_name": player.get("firstName"),
                            "last_name": player.get("lastName"),
                            "age": player.get("age"),
                            "country_name": player.get("countryName"),
                            "country_code": player.get("countryCode"),
                            "shirt_number": player.get("shirtNumber"),
                            "position_id": player.get("positionId"),
                            "usual_playing_position_id": player.get(
                                "usualPlayingPositionId"
                            ),
                            "market_value": player.get("marketValue"),
                            "performance_rating": performance.get("rating")
                            if isinstance(performance, dict)
                            else None,
                            "horizontal_x": horizontal.get("x")
                            if isinstance(horizontal, dict)
                            else None,
                            "horizontal_y": horizontal.get("y")
                            if isinstance(horizontal, dict)
                            else None,
                            "vertical_x": vertical.get("x")
                            if isinstance(vertical, dict)
                            else None,
                            "vertical_y": vertical.get("y")
                            if isinstance(vertical, dict)
                            else None,
                        }
                    )

        for player_id, player_payload in (content.get("playerStats") or {}).items():
            for section in player_payload.get("stats", []):
                for stat_title, stat_entry in (section.get("stats") or {}).items():
                    stat = (
                        stat_entry.get("stat", {})
                        if isinstance(stat_entry, dict)
                        else {}
                    )
                    player_stat_rows.append(
                        {
                            "fixture_id": fixture_id,
                            "match_id": match_id,
                            "player_id": player_payload.get("id") or player_id,
                            "player_name": player_payload.get("name"),
                            "team_id": player_payload.get("teamId"),
                            "team_name": player_payload.get("teamName"),
                            "is_goalkeeper": player_payload.get("isGoalkeeper"),
                            "section_title": section.get("title"),
                            "section_key": section.get("key"),
                            "stat_title": stat_title,
                            "stat_key": stat_entry.get("key")
                            if isinstance(stat_entry, dict)
                            else None,
                            "stat_value": stat.get("value")
                            if isinstance(stat, dict)
                            else None,
                            "stat_total": stat.get("total")
                            if isinstance(stat, dict)
                            else None,
                            "stat_type": stat.get("type")
                            if isinstance(stat, dict)
                            else None,
                        }
                    )

        print_progress("Match Pages", idx, total)

    return (
        pd.DataFrame(detail_rows),
        pd.DataFrame(event_rows),
        pd.DataFrame(stat_rows),
        pd.DataFrame(shot_rows),
        pd.DataFrame(lineup_rows),
        pd.DataFrame(player_stat_rows),
    )


def get_info_value(player_information, title):
    for item in player_information or []:
        if item.get("title") == title:
            value = item.get("value", {})
            if isinstance(value, dict):
                fallback = value.get("fallback")
                if isinstance(fallback, dict):
                    return fallback.get("utcTime") or fallback
                return value.get("numberValue") or fallback or value.get("key")
            return value
    return None


def parse_player_pages(team_data):
    profile_rows = []
    recent_match_rows = []
    career_rows = []
    market_value_rows = []
    trophy_rows = []
    trait_rows = []

    seen_player_ids = []
    for group in team_data.get("squad", {}).get("squad", []):
        for member in group.get("members", []):
            player_id = member.get("id")
            if (
                player_id
                and player_id not in seen_player_ids
                and not member.get("excludeFromRanking")
            ):
                seen_player_ids.append(player_id)

    total = len(seen_player_ids)
    for idx, player_id in enumerate(seen_player_ids, 1):
        payload = fetch_player_page_data(player_id)
        if not payload:
            print_progress("Player Pages", idx, total)
            continue

        player_information = payload.get("playerInformation", [])
        primary_team = payload.get("primaryTeam", {})
        next_match = payload.get("nextMatch", {})
        main_league = payload.get("mainLeague", {})
        traits = payload.get("traits", {})

        profile_rows.append(
            {
                "player_id": payload.get("id") or player_id,
                "player_image_url": player_image_url(payload.get("id") or player_id),
                "name": payload.get("name"),
                "birth_date": payload.get("birthDate"),
                "gender": payload.get("gender"),
                "status": payload.get("status"),
                "data_provider": payload.get("dataProvider"),
                "is_captain": payload.get("isCaptain"),
                "is_coach": payload.get("isCoach"),
                "primary_team_id": primary_team.get("teamId"),
                "primary_team_name": primary_team.get("teamName"),
                "on_loan": primary_team.get("onLoan"),
                "primary_position": (payload.get("positionDescription") or {})
                .get("primaryPosition", {})
                .get("label"),
                "height_cm": get_info_value(player_information, "Height"),
                "shirt_number": get_info_value(player_information, "Shirt"),
                "age": get_info_value(player_information, "Age"),
                "preferred_foot": get_info_value(player_information, "Preferred foot"),
                "country": get_info_value(player_information, "Country"),
                "country_code": next(
                    (
                        item.get("countryCode")
                        for item in player_information
                        if item.get("title") == "Country"
                    ),
                    None,
                ),
                "market_value": get_info_value(player_information, "Market value"),
                "contract_end_utc": get_info_value(player_information, "Contract end"),
                "next_match_id": next_match.get("matchId"),
                "next_match_date": next_match.get("matchDate"),
                "next_match_league": next_match.get("leagueName"),
                "main_league_id": main_league.get("leagueId"),
                "main_league_name": main_league.get("leagueName"),
                "main_league_season": main_league.get("season"),
                "main_league_stats": json_value(main_league.get("stats")),
                "traits_key": traits.get("key"),
                "traits_title": traits.get("title"),
                "injury_information": json_value(payload.get("injuryInformation")),
                "meta_json": json_value(payload.get("meta")),
            }
        )

        for recent in payload.get("recentMatches", []):
            rating_props = recent.get("ratingProps", {})
            recent_match_rows.append(
                {
                    "player_id": player_id,
                    "match_id": recent.get("id"),
                    "match_date": (recent.get("matchDate") or {}).get("utcTime"),
                    "match_page_url": recent.get("matchPageUrl"),
                    "league_id": recent.get("leagueId"),
                    "league_name": recent.get("leagueName"),
                    "stage": recent.get("stage"),
                    "team_id": recent.get("teamId"),
                    "team_name": recent.get("teamName"),
                    "opponent_team_id": recent.get("opponentTeamId"),
                    "opponent_team_name": recent.get("opponentTeamName"),
                    "is_home_team": recent.get("isHomeTeam"),
                    "home_score": recent.get("homeScore"),
                    "away_score": recent.get("awayScore"),
                    "minutes_played": recent.get("minutesPlayed"),
                    "goals": recent.get("goals"),
                    "assists": recent.get("assists"),
                    "yellow_cards": recent.get("yellowCards"),
                    "red_cards": recent.get("redCards"),
                    "rating": rating_props.get("rating")
                    if isinstance(rating_props, dict)
                    else None,
                    "is_top_rating": rating_props.get("isTopRating")
                    if isinstance(rating_props, dict)
                    else None,
                    "player_of_the_match": recent.get("playerOfTheMatch"),
                    "on_bench": recent.get("onBench"),
                }
            )

        career_history = payload.get("careerHistory", {})
        for career_stage, stage_data in (
            career_history.get("careerItems") or {}
        ).items():
            if not isinstance(stage_data, dict):
                continue

            for entry in stage_data.get("teamEntries") or []:
                career_rows.append(
                    {
                        "player_id": player_id,
                        "career_stage": career_stage,
                        "entry_type": "team_entry",
                        "team_id": entry.get("teamId"),
                        "team_name": entry.get("team"),
                        "team_gender": entry.get("teamGender"),
                        "show_team_gender": entry.get("showTeamGender"),
                        "transfer_type": entry.get("transferType"),
                        "start_date": entry.get("startDate"),
                        "end_date": entry.get("endDate"),
                        "active": entry.get("active"),
                        "role": entry.get("role"),
                        "season_name": None,
                        "appearances": entry.get("appearances"),
                        "goals": entry.get("goals"),
                        "assists": entry.get("assists"),
                        "rating": None,
                        "league_id": None,
                        "league_name": None,
                        "tournament_id": None,
                        "is_friendly": None,
                    }
                )

            for season_entry in stage_data.get("seasonEntries") or []:
                rating = season_entry.get("rating", {})
                career_rows.append(
                    {
                        "player_id": player_id,
                        "career_stage": career_stage,
                        "entry_type": "season_entry",
                        "team_id": season_entry.get("teamId"),
                        "team_name": season_entry.get("team"),
                        "team_gender": season_entry.get("teamGender"),
                        "show_team_gender": season_entry.get("showTeamGender"),
                        "transfer_type": season_entry.get("transferType"),
                        "start_date": None,
                        "end_date": None,
                        "active": None,
                        "role": None,
                        "season_name": season_entry.get("seasonName"),
                        "appearances": season_entry.get("appearances"),
                        "goals": season_entry.get("goals"),
                        "assists": season_entry.get("assists"),
                        "rating": rating.get("rating")
                        if isinstance(rating, dict)
                        else None,
                        "league_id": None,
                        "league_name": None,
                        "tournament_id": None,
                        "is_friendly": None,
                    }
                )

                for tournament_stat in season_entry.get("tournamentStats") or []:
                    rating = tournament_stat.get("rating", {})
                    career_rows.append(
                        {
                            "player_id": player_id,
                            "career_stage": career_stage,
                            "entry_type": "tournament_stat",
                            "team_id": season_entry.get("teamId"),
                            "team_name": season_entry.get("team"),
                            "team_gender": season_entry.get("teamGender"),
                            "show_team_gender": season_entry.get("showTeamGender"),
                            "transfer_type": season_entry.get("transferType"),
                            "start_date": None,
                            "end_date": None,
                            "active": None,
                            "role": None,
                            "season_name": tournament_stat.get("seasonName"),
                            "appearances": tournament_stat.get("appearances"),
                            "goals": tournament_stat.get("goals"),
                            "assists": tournament_stat.get("assists"),
                            "rating": rating.get("rating")
                            if isinstance(rating, dict)
                            else None,
                            "league_id": tournament_stat.get("leagueId"),
                            "league_name": tournament_stat.get("leagueName"),
                            "tournament_id": tournament_stat.get("tournamentId"),
                            "is_friendly": tournament_stat.get("isFriendly"),
                        }
                    )

        for market_value in (payload.get("marketValues") or {}).get("values", []):
            market_value_rows.append(
                {
                    "player_id": player_id,
                    "date": market_value.get("date"),
                    "value": market_value.get("value"),
                    "currency": market_value.get("currency"),
                    "lower_bound": market_value.get("lowerBound"),
                    "upper_bound": market_value.get("upperBound"),
                    "source": market_value.get("source"),
                    "team_id": market_value.get("teamId"),
                    "team_name": market_value.get("teamName"),
                    "is_period_start": market_value.get("isPeriodStart"),
                }
            )

        trophies = payload.get("trophies") or {}
        for trophy_type, trophy_groups in trophies.items():
            for group in trophy_groups or []:
                for tournament in group.get("tournaments", []):
                    trophy_rows.append(
                        {
                            "player_id": player_id,
                            "trophy_type": trophy_type,
                            "team_id": group.get("teamId"),
                            "team_name": group.get("teamName"),
                            "country_code": group.get("ccode"),
                            "league_id": tournament.get("leagueId"),
                            "league_name": tournament.get("leagueName"),
                            "seasons_won": json_value(tournament.get("seasonsWon")),
                            "seasons_runner_up": json_value(
                                tournament.get("seasonsRunnerUp")
                            ),
                        }
                    )

        for item in traits.get("items", []):
            trait_rows.append(
                {
                    "player_id": player_id,
                    "traits_key": traits.get("key"),
                    "traits_title": traits.get("title"),
                    "item_key": item.get("key"),
                    "item_title": item.get("title"),
                    "item_value": item.get("value"),
                }
            )

        print_progress("Player Pages", idx, total)

    return (
        pd.DataFrame(profile_rows),
        pd.DataFrame(recent_match_rows),
        pd.DataFrame(career_rows),
        pd.DataFrame(market_value_rows),
        pd.DataFrame(trophy_rows),
        pd.DataFrame(trait_rows),
    )


def parse_faq(team_data):
    rows = []
    faq_entities = (
        team_data.get("details", {}).get("faqJSONLD", {}).get("mainEntity", [])
    )
    qa_data = team_data.get("QAData", [])

    for item in faq_entities:
        rows.append(
            {
                "source": "faq_jsonld",
                "question": item.get("name"),
                "answer": (item.get("acceptedAnswer") or {}).get("text"),
            }
        )

    for item in qa_data:
        rows.append(
            {
                "source": "qa_data",
                "question": item.get("question"),
                "answer": item.get("answer"),
            }
        )

    return pd.DataFrame(rows)


def parse_tabs(team_data):
    return pd.DataFrame([{"tab": tab} for tab in team_data.get("tabs", [])])


def parse_last_lineup(team_data):
    lineup = team_data.get("overview", {}).get("lastLineupStats", {})
    coach = lineup.get("coach", {}) if isinstance(lineup, dict) else {}
    summary = pd.DataFrame(
        [
            {
                "team_id": lineup.get("id"),
                "team_name": lineup.get("name"),
                "formation": lineup.get("formation"),
                "team_rating": lineup.get("rating"),
                "average_starter_age": lineup.get("averageStarterAge"),
                "total_starter_market_value": lineup.get("totalStarterMarketValue"),
                "coach_id": coach.get("id"),
                "coach_name": coach.get("name"),
            }
        ]
    )

    players = []
    sections = {
        "starter": lineup.get("starters", []),
        "sub": lineup.get("subs", []),
        "unavailable": lineup.get("unavailable", []),
    }
    total = sum(len(items) for items in sections.values())
    current = 0
    for section_name, items in sections.items():
        for item in items:
            performance = item.get("performance", {})
            horizontal = item.get("horizontalLayout", {})
            vertical = item.get("verticalLayout", {})
            players.append(
                {
                    "section": section_name,
                    "player_id": item.get("id"),
                    "name": item.get("name"),
                    "first_name": item.get("firstName"),
                    "last_name": item.get("lastName"),
                    "age": item.get("age"),
                    "country_name": item.get("countryName"),
                    "country_code": item.get("countryCode"),
                    "shirt_number": item.get("shirtNumber"),
                    "position_id": item.get("positionId"),
                    "usual_playing_position_id": item.get("usualPlayingPositionId"),
                    "is_captain": item.get("isCaptain"),
                    "market_value": item.get("marketValue"),
                    "performance_rating": performance.get("rating")
                    if isinstance(performance, dict)
                    else None,
                    "season_goals": performance.get("seasonGoals")
                    if isinstance(performance, dict)
                    else None,
                    "season_assists": performance.get("seasonAssists")
                    if isinstance(performance, dict)
                    else None,
                    "season_rating": performance.get("seasonRating")
                    if isinstance(performance, dict)
                    else None,
                    "events": json_value(performance.get("events"))
                    if isinstance(performance, dict)
                    else None,
                    "horizontal_x": horizontal.get("x")
                    if isinstance(horizontal, dict)
                    else None,
                    "horizontal_y": horizontal.get("y")
                    if isinstance(horizontal, dict)
                    else None,
                    "vertical_x": vertical.get("x")
                    if isinstance(vertical, dict)
                    else None,
                    "vertical_y": vertical.get("y")
                    if isinstance(vertical, dict)
                    else None,
                }
            )
            current += 1
            print_progress("Last Lineup", current, total)

    return summary, pd.DataFrame(players)


def save_csv(df, filename):
    label = format_label(filename)
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)

    filepath = os.path.join(output_dir, f"{filename}.csv")
    export_df = df.reindex(columns=OUTPUT_COLUMNS.get(filename, list(df.columns)))
    export_df.to_csv(filepath, index=False)

    if export_df.empty:
        print(f"  ! No data for {label}; wrote empty file: {filepath}")
        return False

    print(f"  + {label} saved: {filepath}")
    return True


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch FotMob team data and export CSV files."
    )
    parser.add_argument(
        "--sync-supabase",
        action="store_true",
        help="Also sync all exported tables to Supabase.",
    )
    parser.add_argument(
        "--overwrite-supabase",
        action="store_true",
        help="Delete all synced rows for this team before inserting fresh data.",
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
                "Error: --sync-supabase requires env vars: " + ", ".join(missing_vars)
            )
            return 1

    if args.overwrite_supabase and not args.sync_supabase:
        print("Error: --overwrite-supabase requires --sync-supabase")
        return 1

    print(f"Fetching data for team ID: {TEAM_ID}\n")
    team_data = get_team_data(TEAM_ID)

    print("\nProcessing data...")

    fixtures_df = parse_fixtures(team_data)
    save_csv(fixtures_df, "fixtures")

    squad_df = parse_squad(team_data)
    save_csv(squad_df, "squad")

    player_stats_df = parse_player_stats(team_data)
    save_csv(player_stats_df, "player_stats")

    player_rankings_df = parse_player_stat_rankings(team_data)
    save_csv(player_rankings_df, "player_stat_rankings")

    team_rankings_df = parse_team_stat_rankings(team_data)
    save_csv(team_rankings_df, "team_stat_rankings")

    team_info_df = parse_overview(team_data)
    save_csv(team_info_df, "team_info")

    league_table_df, table_legend_df = parse_table(team_data)
    save_csv(league_table_df, "league_table")
    save_csv(table_legend_df, "table_legend")

    transfers_df = parse_transfers(team_data)
    save_csv(transfers_df, "transfers")

    match_highlights_df = parse_match_highlights(team_data)
    save_csv(match_highlights_df, "match_highlights")

    team_form_df = parse_team_form(team_data)
    save_csv(team_form_df, "team_form")

    top_players_df = parse_top_players(team_data)
    save_csv(top_players_df, "top_players")

    venue_df = parse_venue(team_data)
    save_csv(venue_df, "venue")

    coach_history_df = parse_coach_history(team_data)
    save_csv(coach_history_df, "coach_history")

    trophies_df = parse_trophies(team_data)
    save_csv(trophies_df, "trophies")

    historical_seasons_df = parse_historical_seasons(team_data)
    save_csv(historical_seasons_df, "historical_seasons")

    historical_table_rows_df, historical_table_rules_df = parse_historical_tables(
        team_data
    )
    save_csv(historical_table_rows_df, "historical_table_rows")
    save_csv(historical_table_rules_df, "historical_table_rules")

    faq_df = parse_faq(team_data)
    save_csv(faq_df, "faq")

    tabs_df = parse_tabs(team_data)
    save_csv(tabs_df, "tabs")

    last_lineup_df, last_lineup_players_df = parse_last_lineup(team_data)
    save_csv(last_lineup_df, "last_lineup")
    save_csv(last_lineup_players_df, "last_lineup_players")

    (
        match_details_df,
        match_events_df,
        match_stats_df,
        match_shots_df,
        match_lineup_players_df,
        match_player_stats_df,
    ) = parse_match_pages(team_data)
    save_csv(match_details_df, "match_details")
    save_csv(match_events_df, "match_events")
    save_csv(match_stats_df, "match_stats")
    save_csv(match_shots_df, "match_shots")
    save_csv(match_lineup_players_df, "match_lineup_players")
    save_csv(match_player_stats_df, "match_player_stats")

    (
        player_profiles_df,
        player_recent_matches_df,
        player_career_entries_df,
        player_market_values_df,
        player_trophies_df,
        player_traits_df,
    ) = parse_player_pages(team_data)
    save_csv(player_profiles_df, "player_profiles")
    save_csv(player_recent_matches_df, "player_recent_matches")
    save_csv(player_career_entries_df, "player_career_entries")
    save_csv(player_market_values_df, "player_market_values")
    save_csv(player_trophies_df, "player_trophies")
    save_csv(player_traits_df, "player_traits")

    dataframes = {
        "fixtures": fixtures_df,
        "squad": squad_df,
        "player_stats": player_stats_df,
        "player_stat_rankings": player_rankings_df,
        "team_stat_rankings": team_rankings_df,
        "team_info": team_info_df,
        "league_table": league_table_df,
        "table_legend": table_legend_df,
        "transfers": transfers_df,
        "match_highlights": match_highlights_df,
        "team_form": team_form_df,
        "top_players": top_players_df,
        "venue": venue_df,
        "coach_history": coach_history_df,
        "trophies": trophies_df,
        "historical_seasons": historical_seasons_df,
        "historical_table_rows": historical_table_rows_df,
        "historical_table_rules": historical_table_rules_df,
        "faq": faq_df,
        "tabs": tabs_df,
        "last_lineup": last_lineup_df,
        "last_lineup_players": last_lineup_players_df,
        "match_details": match_details_df,
        "match_events": match_events_df,
        "match_stats": match_stats_df,
        "match_shots": match_shots_df,
        "match_lineup_players": match_lineup_players_df,
        "match_player_stats": match_player_stats_df,
        "player_profiles": player_profiles_df,
        "player_recent_matches": player_recent_matches_df,
        "player_career_entries": player_career_entries_df,
        "player_market_values": player_market_values_df,
        "player_trophies": player_trophies_df,
        "player_traits": player_traits_df,
    }

    if args.sync_supabase:
        try:
            source_team_id = int(TEAM_ID)
        except ValueError:
            print("Error: TEAM_ID must be an integer for Supabase sync")
            return 1

        print("\nSyncing all exported tables to Supabase...")
        try:
            from supabase_sync import sync_to_supabase

            sync_summary = sync_to_supabase(
                dataframes=dataframes,
                source_team_id=source_team_id,
                supabase_url=SUPABASE_URL,
                supabase_service_role_key=SUPABASE_SERVICE_ROLE_KEY,
                schema=SUPABASE_SCHEMA,
                overwrite_all=args.overwrite_supabase,
            )
        except Exception as exc:
            print(f"Error: Supabase sync failed: {exc}")
            return 1

        for table_name, result in sync_summary.items():
            label = format_label(table_name)
            print(f"  + {label} synced: {result['inserted_rows']} rows")

    print("\nDone! Data saved to: data/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
