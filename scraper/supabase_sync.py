import math
from datetime import date, datetime

import pandas as pd


TABLE_RENAMES = {
    "fixtures": {"id": "fixture_id"},
    "squad": {"id": "player_id"},
    "player_stats": {"team_id": "stat_team_id"},
    "league_table": {"team_id": "table_team_id"},
    "transfers": {"type": "transfer_type"},
}

TABLE_INTEGER_COLUMNS = {
    "fixtures": {"source_team_id", "fixture_id", "opponent_id", "tournament_id"},
    "squad": {
        "source_team_id",
        "player_id",
        "shirt_number",
        "height",
        "age",
        "goals",
        "assists",
        "yellow_cards",
        "red_cards",
        "market_value",
    },
    "player_stats": {"source_team_id", "player_id", "stat_team_id", "rank"},
    "team_info": {"source_team_id", "team_id"},
    "league_table": {
        "source_team_id",
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
    },
    "transfers": {
        "source_team_id",
        "player_id",
        "from_club_id",
        "to_club_id",
        "market_value",
    },
}

TABLE_BOOLEAN_COLUMNS = {
    "fixtures": {"not_started"},
    "transfers": {"on_loan"},
}


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


def _coerce_integer(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else value
    if isinstance(value, str):
        try:
            parsed = float(value)
        except ValueError:
            return value
        return int(parsed) if parsed.is_integer() else value
    return value


def _coerce_boolean(value):
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
    return value


def _prepare_records(df, table_name, source_team_id):
    rename_map = TABLE_RENAMES.get(table_name, {})
    prepared = df.rename(columns=rename_map).copy()
    prepared["source_team_id"] = source_team_id
    records = prepared.to_dict(orient="records")

    integer_columns = TABLE_INTEGER_COLUMNS.get(table_name, set())
    boolean_columns = TABLE_BOOLEAN_COLUMNS.get(table_name, set())

    normalized_records = []
    for record in records:
        normalized = {}
        for key, value in record.items():
            normalized_value = _normalize_value(value)
            if key in integer_columns:
                normalized_value = _coerce_integer(normalized_value)
            elif key in boolean_columns:
                normalized_value = _coerce_boolean(normalized_value)
            normalized[key] = normalized_value
        normalized_records.append(normalized)

    return normalized_records


def _chunked(items, chunk_size):
    for idx in range(0, len(items), chunk_size):
        yield items[idx : idx + chunk_size]


def sync_to_supabase(
    dataframes,
    source_team_id,
    supabase_url,
    supabase_service_role_key,
    schema="public",
    chunk_size=500,
):
    client = _get_supabase_client(supabase_url, supabase_service_role_key)
    summary = {}

    for table_name, df in dataframes.items():
        records = _prepare_records(df, table_name, source_team_id)

        _table_query(client, schema, table_name).delete().eq(
            "source_team_id", source_team_id
        ).execute()

        inserted = 0
        for chunk in _chunked(records, chunk_size):
            if not chunk:
                continue
            _table_query(client, schema, table_name).insert(chunk).execute()
            inserted += len(chunk)

        summary[table_name] = {
            "deleted_for_team_id": source_team_id,
            "inserted_rows": inserted,
        }

    return summary
