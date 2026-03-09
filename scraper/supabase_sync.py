import json
import math
from datetime import date, datetime

import pandas as pd


TABLE_CONFIG = {
    "fixtures": {
        "renames": {"id": "fixture_id"},
        "ints": {
            "source_team_id",
            "fixture_id",
            "opponent_id",
            "opponent_score",
            "home_team_id",
            "home_team_score",
            "away_team_id",
            "away_team_score",
            "tournament_id",
        },
        "floats": {"result_code"},
        "bools": {
            "display_tournament",
            "team_is_home",
            "not_started",
            "status_started",
            "status_finished",
            "status_cancelled",
            "status_awarded",
        },
        "json": {"home_away", "status"},
        "timestamps": {"utc_time"},
    },
    "squad": {
        "renames": {"id": "player_id"},
        "ints": {"source_team_id", "player_id", "age"},
        "floats": {
            "shirt_number",
            "height",
            "rating",
            "goals",
            "assists",
            "yellow_cards",
            "red_cards",
            "market_value",
        },
        "bools": {"exclude_from_ranking"},
        "dates": {"date_of_birth"},
    },
    "player_stats": {
        "renames": {"team_id": "stat_team_id"},
        "ints": {
            "source_team_id",
            "player_id",
            "stat_team_id",
            "rank",
            "fractions",
            "category_order",
        },
        "floats": {"value"},
    },
    "player_stat_rankings": {
        "renames": {"team_id": "stat_team_id"},
        "ints": {
            "source_team_id",
            "player_id",
            "stat_team_id",
            "rank",
            "minutes_played",
            "matches_played",
            "stat_count",
            "stat_decimals",
            "substat_decimals",
        },
        "floats": {"value", "sub_value"},
        "json": {"positions"},
    },
    "team_stat_rankings": {
        "renames": {"team_id": "stat_team_id"},
        "ints": {
            "source_team_id",
            "stat_team_id",
            "rank",
            "matches_played",
            "stat_count",
            "stat_decimals",
            "substat_decimals",
        },
        "floats": {"value", "sub_value"},
    },
    "team_info": {
        "ints": {
            "source_team_id",
            "team_id",
            "primary_league_id",
            "capacity",
            "opened",
        },
        "floats": {"stadium_latitude", "stadium_longitude"},
        "bools": {"can_sync_calendar"},
    },
    "league_table": {
        "renames": {"team_id": "table_team_id"},
        "ints": {
            "source_team_id",
            "league_id",
            "position",
            "table_team_id",
            "played",
            "wins",
            "draws",
            "losses",
            "goals_for",
            "goals_against",
            "goal_difference",
            "points",
            "next_opponent_id",
            "next_match_id",
        },
        "floats": {"deduction"},
        "bools": {"featured_in_match"},
        "timestamps": {"next_match_utc_time"},
    },
    "table_legend": {
        "ints": {"source_team_id", "league_id"},
        "json": {"indices"},
    },
    "transfers": {
        "renames": {"type": "transfer_type"},
        "ints": {
            "source_team_id",
            "player_id",
            "from_club_id",
            "to_club_id",
            "market_value",
        },
        "floats": {"fee_value"},
        "bools": {"on_loan", "contract_extension"},
        "json": {"transfer_text"},
        "timestamps": {"transfer_date", "from_date", "to_date"},
    },
    "match_highlights": {
        "renames": {"id": "fixture_id"},
        "ints": {
            "source_team_id",
            "fixture_id",
            "opponent_id",
            "home_team_id",
            "home_team_score",
            "away_team_id",
            "away_team_score",
            "tournament_id",
        },
        "bools": {
            "display_tournament",
            "not_started",
            "status_started",
            "status_finished",
            "status_cancelled",
            "status_awarded",
        },
        "json": {"stats_summary"},
        "timestamps": {"utc_time"},
    },
    "team_form": {
        "renames": {"is_home": "team_is_home"},
        "ints": {"source_team_id", "sequence", "result", "opponent_id"},
        "bools": {"team_is_home"},
        "json": {"tooltip_json"},
        "timestamps": {"utc_time"},
    },
    "top_players": {
        "ints": {
            "source_team_id",
            "player_id",
            "team_id",
            "rank",
            "fractions",
        },
        "floats": {"value"},
    },
    "venue": {
        "ints": {"source_team_id", "capacity", "opened"},
        "floats": {"latitude", "longitude"},
    },
    "coach_history": {
        "ints": {"source_team_id", "coach_id", "league_id", "wins", "draws", "losses"},
        "floats": {"points_per_game", "win_percentage"},
    },
    "trophies": {
        "ints": {"source_team_id", "tournament_template_id", "won", "runnerup"},
    },
    "historical_seasons": {
        "ints": {
            "source_team_id",
            "tournament_id",
            "template_id",
            "stage_id",
            "position",
            "number_of_teams",
            "points",
            "wins",
            "draws",
            "losses",
        },
        "bools": {"is_consecutive"},
    },
    "historical_table_rows": {
        "ints": {
            "source_team_id",
            "league_id",
            "position",
            "team_id",
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
        },
    },
    "historical_table_rules": {
        "ints": {"source_team_id", "league_id"},
    },
    "faq": {"ints": {"source_team_id"}},
    "tabs": {"ints": {"source_team_id"}},
    "last_lineup": {
        "renames": {"team_id": "lineup_team_id"},
        "ints": {
            "source_team_id",
            "lineup_team_id",
            "average_starter_age",
            "total_starter_market_value",
            "coach_id",
        },
        "floats": {"team_rating"},
    },
    "last_lineup_players": {
        "ints": {"source_team_id", "player_id", "age", "shirt_number"},
        "floats": {
            "position_id",
            "usual_playing_position_id",
            "market_value",
            "performance_rating",
            "season_goals",
            "season_assists",
            "season_rating",
            "horizontal_x",
            "horizontal_y",
            "vertical_x",
            "vertical_y",
        },
        "bools": {"is_captain"},
        "json": {"events"},
    },
    "match_details": {
        "renames": {
            "fixture_id": "source_fixture_id",
            "match_id": "fotmob_match_id",
        },
        "ints": {
            "source_team_id",
            "source_fixture_id",
            "fotmob_match_id",
            "league_id",
            "parent_league_id",
            "home_team_id",
            "home_team_score",
            "away_team_id",
            "away_team_score",
            "qa_count",
            "home_top_player_count",
            "away_top_player_count",
        },
        "floats": {
            "player_of_match_id",
            "attendance",
            "stadium_lat",
            "stadium_long",
            "stadium_capacity",
        },
        "bools": {"started", "finished"},
        "timestamps": {"match_time_utc_date"},
    },
    "match_events": {
        "renames": {
            "fixture_id": "source_fixture_id",
            "match_id": "fotmob_match_id",
        },
        "ints": {
            "source_team_id",
            "source_fixture_id",
            "fotmob_match_id",
            "time",
            "home_score",
            "away_score",
        },
        "floats": {"event_id", "overload_time", "player_id"},
        "bools": {"is_home"},
        "json": {"event_payload"},
    },
    "match_stats": {
        "renames": {
            "fixture_id": "source_fixture_id",
            "match_id": "fotmob_match_id",
        },
        "ints": {"source_team_id", "source_fixture_id", "fotmob_match_id"},
    },
    "match_shots": {
        "renames": {
            "fixture_id": "source_fixture_id",
            "match_id": "fotmob_match_id",
        },
        "ints": {
            "source_team_id",
            "source_fixture_id",
            "fotmob_match_id",
            "shot_id",
            "player_id",
            "team_id",
            "minute",
        },
        "floats": {
            "minute_added",
            "expected_goals",
            "expected_goals_on_target",
            "x",
            "y",
            "goal_crossed_y",
            "goal_crossed_z",
            "blocked_x",
            "blocked_y",
            "keeper_id",
        },
        "bools": {
            "is_on_target",
            "is_blocked",
            "is_own_goal",
            "is_saved_off_line",
            "is_from_inside_box",
        },
    },
    "match_lineup_players": {
        "renames": {
            "fixture_id": "source_fixture_id",
            "match_id": "fotmob_match_id",
            "team_id": "lineup_team_id",
        },
        "ints": {
            "source_team_id",
            "source_fixture_id",
            "fotmob_match_id",
            "lineup_team_id",
            "player_id",
            "shirt_number",
        },
        "floats": {
            "team_rating",
            "age",
            "position_id",
            "usual_playing_position_id",
            "market_value",
            "performance_rating",
            "horizontal_x",
            "horizontal_y",
            "vertical_x",
            "vertical_y",
        },
    },
    "match_player_stats": {
        "renames": {
            "fixture_id": "source_fixture_id",
            "match_id": "fotmob_match_id",
            "team_id": "stat_team_id",
        },
        "ints": {
            "source_team_id",
            "source_fixture_id",
            "fotmob_match_id",
            "player_id",
            "stat_team_id",
        },
        "floats": {"stat_value", "stat_total"},
        "bools": {"is_goalkeeper"},
    },
    "player_profiles": {
        "ints": {
            "source_team_id",
            "player_id",
            "primary_team_id",
            "shirt_number",
            "age",
            "market_value",
            "next_match_id",
            "main_league_id",
        },
        "floats": {"height_cm"},
        "bools": {"is_captain", "is_coach", "on_loan"},
        "json": {"main_league_stats", "injury_information", "meta_json"},
        "timestamps": {"contract_end_utc", "next_match_date"},
    },
    "player_recent_matches": {
        "ints": {
            "source_team_id",
            "player_id",
            "match_id",
            "league_id",
            "team_id",
            "opponent_team_id",
            "home_score",
            "away_score",
            "minutes_played",
            "goals",
            "assists",
            "yellow_cards",
            "red_cards",
        },
        "floats": {"rating"},
        "bools": {"is_home_team", "is_top_rating", "player_of_the_match", "on_bench"},
        "timestamps": {"match_date"},
    },
    "player_career_entries": {
        "ints": {"source_team_id", "player_id", "team_id", "appearances", "goals"},
        "floats": {"assists", "rating", "league_id", "tournament_id"},
        "bools": {"show_team_gender", "active", "is_friendly"},
        "timestamps": {"start_date", "end_date"},
    },
    "player_market_values": {
        "ints": {"source_team_id", "player_id", "value", "lower_bound", "upper_bound"},
        "floats": {"team_id"},
        "bools": {"is_period_start"},
        "timestamps": {"date"},
    },
    "player_trophies": {
        "ints": {"source_team_id", "player_id", "team_id", "league_id"},
        "json": {"seasons_won", "seasons_runner_up"},
    },
    "player_traits": {
        "ints": {"source_team_id", "player_id"},
        "floats": {"item_value"},
    },
}

DEFAULT_SYNC_TABLES = tuple(TABLE_CONFIG.keys())


def _get_supabase_client(supabase_url, supabase_service_role_key):
    try:
        from supabase import create_client
    except ImportError as exc:
        raise RuntimeError(
            "Supabase client not installed. Run `pip install -r requirements.txt`."
        ) from exc

    return create_client(supabase_url, supabase_service_role_key)


def _table_query(client, schema, table_name):
    if schema and schema != "public":
        if not hasattr(client, "schema"):
            raise RuntimeError(
                "Current supabase client does not support custom schemas."
            )
        return client.schema(schema).table(table_name)
    return client.table(table_name)


def _is_missing(value):
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if isinstance(value, (dict, list, tuple, set)):
        return False
    try:
        return bool(pd.isna(value))
    except Exception:
        return False


def _normalize_value(value):
    if _is_missing(value):
        return None

    if hasattr(value, "item") and not isinstance(value, (str, bytes, bytearray)):
        try:
            value = value.item()
        except Exception:
            pass

    if isinstance(value, str):
        trimmed = value.strip()
        return trimmed if trimmed else None

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    return value


def _coerce_int(value):
    value = _normalize_value(value)
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else None
    if isinstance(value, str):
        try:
            parsed = float(value)
        except ValueError:
            return None
        return int(parsed) if parsed.is_integer() else None
    return None


def _coerce_float(value):
    value = _normalize_value(value)
    if value is None:
        return None
    if isinstance(value, bool):
        return float(int(value))
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _coerce_bool(value):
    value = _normalize_value(value)
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(int(value))
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "t", "1", "yes", "y"}:
            return True
        if lowered in {"false", "f", "0", "no", "n"}:
            return False
    return None


def _coerce_json(value):
    value = _normalize_value(value)
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return None
    return None


def _coerce_timestamp(value):
    value = _normalize_value(value)
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, str):
        return value
    return None


def _coerce_date(value):
    value = _normalize_value(value)
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, str):
        return value
    return None


def _prepare_records(df, table_name, source_team_id):
    config = TABLE_CONFIG.get(table_name, {})
    rename_map = config.get("renames", {})
    prepared = df.rename(columns=rename_map).copy()
    prepared["source_team_id"] = source_team_id
    records = prepared.to_dict(orient="records")

    ints = config.get("ints", set())
    floats = config.get("floats", set())
    bools = config.get("bools", set())
    json_fields = config.get("json", set())
    timestamps = config.get("timestamps", set())
    dates = config.get("dates", set())

    normalized_records = []
    for record in records:
        normalized = {}
        for key, value in record.items():
            if key in ints:
                normalized_value = _coerce_int(value)
            elif key in floats:
                normalized_value = _coerce_float(value)
            elif key in bools:
                normalized_value = _coerce_bool(value)
            elif key in json_fields:
                normalized_value = _coerce_json(value)
            elif key in timestamps:
                normalized_value = _coerce_timestamp(value)
            elif key in dates:
                normalized_value = _coerce_date(value)
            else:
                normalized_value = _normalize_value(value)
            normalized[key] = normalized_value
        normalized_records.append(normalized)

    return normalized_records


def _chunked(items, chunk_size):
    for idx in range(0, len(items), chunk_size):
        yield items[idx : idx + chunk_size]


def _clear_table(query, source_team_id, overwrite_all):
    if overwrite_all:
        query.delete().neq("source_team_id", -1).execute()
    else:
        query.delete().eq("source_team_id", source_team_id).execute()


def sync_to_supabase(
    dataframes,
    source_team_id,
    supabase_url,
    supabase_service_role_key,
    schema="public",
    chunk_size=500,
    overwrite_all=False,
):
    client = _get_supabase_client(supabase_url, supabase_service_role_key)
    summary = {}

    for table_name in DEFAULT_SYNC_TABLES:
        if table_name not in dataframes:
            continue

        df = dataframes[table_name]
        records = _prepare_records(df, table_name, source_team_id)
        table = _table_query(client, schema, table_name)

        _clear_table(table, source_team_id, overwrite_all)

        inserted = 0
        for chunk in _chunked(records, chunk_size):
            if not chunk:
                continue
            table.insert(chunk).execute()
            inserted += len(chunk)

        summary[table_name] = {
            "mode": "overwrite_all" if overwrite_all else "team_only",
            "inserted_rows": inserted,
        }

    return summary
