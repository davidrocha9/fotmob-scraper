drop table if exists public.player_traits;
drop table if exists public.player_trophies;
drop table if exists public.player_market_values;
drop table if exists public.player_career_entries;
drop table if exists public.player_recent_matches;
drop table if exists public.player_profiles;
drop table if exists public.match_player_stats;
drop table if exists public.match_lineup_players;
drop table if exists public.match_shots;
drop table if exists public.match_stats;
drop table if exists public.match_events;
drop table if exists public.match_details;
drop table if exists public.last_lineup_players;
drop table if exists public.last_lineup;
drop table if exists public.tabs;
drop table if exists public.faq;
drop table if exists public.historical_table_rules;
drop table if exists public.historical_table_rows;
drop table if exists public.historical_seasons;
drop table if exists public.trophies;
drop table if exists public.coach_history;
drop table if exists public.venue;
drop table if exists public.top_players;
drop table if exists public.team_form;
drop table if exists public.match_highlights;
drop table if exists public.transfers;
drop table if exists public.table_legend;
drop table if exists public.league_table;
drop table if exists public.team_info;
drop table if exists public.team_stat_rankings;
drop table if exists public.player_stat_rankings;
drop table if exists public.player_stats;
drop table if exists public.squad;
drop table if exists public.fixtures;

create table if not exists public.fixtures (
  source_team_id bigint not null,
  fixture_id bigint,
  page_url text,
  opponent text,
  opponent_id bigint,
  opponent_score integer,
  home_team_id bigint,
  home_team_name text,
  home_team_score integer,
  away_team_id bigint,
  away_team_name text,
  away_team_score integer,
  team_is_home boolean,
  home_away jsonb,
  display_tournament boolean,
  tournament text,
  tournament_id bigint,
  tournament_stage text,
  round text,
  result text,
  result_code double precision,
  not_started boolean,
  utc_time timestamptz,
  status_started boolean,
  status_finished boolean,
  status_cancelled boolean,
  status_awarded boolean,
  status_reason_short text,
  status_reason_long text,
  start_day text,
  live_time_short text,
  live_time_long text,
  stats_summary text,
  stats_league_names text,
  status jsonb,
  synced_at timestamptz not null default now(),
  primary key (source_team_id, fixture_id)
);

create table if not exists public.squad (
  source_team_id bigint not null,
  player_id bigint,
  player_image_url text,
  name text,
  first_name text,
  last_name text,
  position_group text,
  position text,
  role_key text,
  shirt_number double precision,
  country_code text,
  country text,
  height double precision,
  age integer,
  date_of_birth date,
  rating double precision,
  goals double precision,
  assists double precision,
  yellow_cards double precision,
  red_cards double precision,
  market_value double precision,
  exclude_from_ranking boolean,
  synced_at timestamptz not null default now(),
  primary key (source_team_id, player_id)
);

create table if not exists public.player_stats (
  source_team_id bigint not null,
  category text,
  category_display text,
  localized_title_id text,
  stat_name text,
  fetch_all_url text,
  player_id bigint,
  player_image_url text,
  player_name text,
  player_country text,
  stat_team_id bigint,
  team_name text,
  rank integer,
  value double precision,
  format text,
  fractions integer,
  category_order integer,
  category_type text,
  synced_at timestamptz not null default now(),
  primary key (source_team_id, category, player_id)
);

create table if not exists public.player_stat_rankings (
  source_team_id bigint not null,
  category text,
  category_display text,
  stat_name text,
  title text,
  subtitle text,
  league_name text,
  player_id bigint,
  player_image_url text,
  player_name text,
  player_country text,
  stat_team_id bigint,
  team_name text,
  rank integer,
  value double precision,
  sub_value double precision,
  minutes_played integer,
  matches_played integer,
  stat_count integer,
  positions jsonb,
  team_color text,
  stat_format text,
  substat_format text,
  stat_decimals integer,
  substat_decimals integer,
  fetch_all_url text,
  synced_at timestamptz not null default now()
);

create table if not exists public.team_stat_rankings (
  source_team_id bigint not null,
  category text,
  category_display text,
  stat_name text,
  title text,
  league_name text,
  stat_team_id bigint,
  team_name text,
  team_country text,
  rank integer,
  value double precision,
  sub_value double precision,
  matches_played integer,
  stat_count integer,
  team_color text,
  stat_format text,
  substat_format text,
  stat_decimals integer,
  substat_decimals integer,
  fetch_all_url text,
  synced_at timestamptz not null default now()
);

create table if not exists public.team_info (
  source_team_id bigint not null,
  team_id bigint,
  team_name text,
  team_short_name text,
  team_type text,
  gender text,
  country_code text,
  season text,
  selected_season text,
  latest_season text,
  primary_league_id bigint,
  primary_league_name text,
  primary_league_url text,
  team_url text,
  team_logo_url text,
  seo_path text,
  can_sync_calendar boolean,
  stadium_name text,
  stadium_city text,
  stadium_country text,
  stadium_latitude double precision,
  stadium_longitude double precision,
  surface text,
  capacity integer,
  opened integer,
  color_primary text,
  color_alt text,
  color_away text,
  color_away_alt text,
  color_dark_mode text,
  color_light_mode text,
  font_dark_mode text,
  font_light_mode text,
  synced_at timestamptz not null default now(),
  primary key (source_team_id)
);

create table if not exists public.league_table (
  source_team_id bigint not null,
  league text,
  league_id bigint,
  country_code text,
  page_url text,
  table_type text,
  position integer,
  table_team_id bigint,
  team_name text,
  team_short_name text,
  played integer,
  wins integer,
  draws integer,
  losses integer,
  goals_for integer,
  goals_against integer,
  goal_difference integer,
  points integer,
  featured_in_match boolean,
  deduction double precision,
  ongoing text,
  qualification_color text,
  scores_str text,
  recent_form text,
  next_opponent_id bigint,
  next_opponent_name text,
  next_match_id bigint,
  next_match_utc_time timestamptz,
  synced_at timestamptz not null default now()
);

create table if not exists public.table_legend (
  source_team_id bigint not null,
  league text,
  league_id bigint,
  title text,
  key text,
  color text,
  indices jsonb,
  synced_at timestamptz not null default now()
);

create table if not exists public.transfers (
  source_team_id bigint not null,
  transfer_type text,
  player_id bigint,
  player_name text,
  position text,
  position_key text,
  from_club text,
  from_club_id bigint,
  to_club text,
  to_club_id bigint,
  transfer_date timestamptz,
  from_date timestamptz,
  to_date timestamptz,
  fee text,
  fee_value double precision,
  fee_localized text,
  market_value bigint,
  on_loan boolean,
  contract_extension boolean,
  transfer_type_text text,
  transfer_type_key text,
  transfer_text jsonb,
  synced_at timestamptz not null default now()
);

create table if not exists public.match_highlights (
  source_team_id bigint not null,
  match_type text,
  fixture_id bigint,
  page_url text,
  opponent text,
  opponent_id bigint,
  home_team_id bigint,
  home_team_name text,
  home_team_score integer,
  away_team_id bigint,
  away_team_name text,
  away_team_score integer,
  display_tournament boolean,
  tournament text,
  tournament_id bigint,
  not_started boolean,
  utc_time timestamptz,
  status_started boolean,
  status_finished boolean,
  status_cancelled boolean,
  status_awarded boolean,
  score_str text,
  reason_short text,
  reason_long text,
  start_day text,
  live_time_short text,
  live_time_long text,
  stats_summary jsonb,
  synced_at timestamptz not null default now()
);

create table if not exists public.team_form (
  source_team_id bigint not null,
  sequence integer,
  result integer,
  result_string text,
  score text,
  utc_time timestamptz,
  tournament_name text,
  match_url text,
  opponent_id bigint,
  opponent_name text,
  team_is_home boolean,
  team_page_url text,
  opponent_logo_url text,
  tooltip_json jsonb,
  synced_at timestamptz not null default now()
);

create table if not exists public.top_players (
  source_team_id bigint not null,
  group_name text,
  group_label text,
  see_all_link text,
  player_id bigint,
  player_image_url text,
  player_name text,
  player_country text,
  team_id bigint,
  team_name text,
  rank integer,
  value double precision,
  stat_name text,
  format text,
  fractions integer,
  team_color_dark text,
  team_color_light text,
  synced_at timestamptz not null default now()
);

create table if not exists public.venue (
  source_team_id bigint not null,
  stadium_name text,
  city text,
  latitude double precision,
  longitude double precision,
  surface text,
  capacity integer,
  opened integer,
  synced_at timestamptz not null default now()
);

create table if not exists public.coach_history (
  source_team_id bigint not null,
  coach_id bigint,
  coach_name text,
  season text,
  league_id bigint,
  league_name text,
  wins integer,
  draws integer,
  losses integer,
  points_per_game double precision,
  win_percentage double precision,
  synced_at timestamptz not null default now()
);

create table if not exists public.trophies (
  source_team_id bigint not null,
  name text,
  tournament_template_id bigint,
  area text,
  country_code text,
  won integer,
  runnerup integer,
  season_won text,
  season_runnerup text,
  synced_at timestamptz not null default now()
);

create table if not exists public.historical_seasons (
  source_team_id bigint not null,
  season_name text,
  tournament_name text,
  tournament_id bigint,
  template_id bigint,
  stage_id bigint,
  position integer,
  number_of_teams integer,
  points integer,
  wins integer,
  draws integer,
  losses integer,
  is_consecutive boolean,
  table_link text,
  synced_at timestamptz not null default now()
);

create table if not exists public.historical_table_rows (
  source_team_id bigint not null,
  season_name text,
  tournament_name text,
  league_id bigint,
  table_name text,
  country_code text,
  position integer,
  team_id bigint,
  team_name text,
  points integer,
  wins integer,
  draws integer,
  losses integer,
  goals_for integer,
  goals_against integer,
  home_points integer,
  home_wins integer,
  home_draws integer,
  home_losses integer,
  home_goals_for integer,
  home_goals_against integer,
  change text,
  table_link text,
  synced_at timestamptz not null default now()
);

create table if not exists public.historical_table_rules (
  source_team_id bigint not null,
  season_name text,
  tournament_name text,
  league_id bigint,
  table_name text,
  country_code text,
  description text,
  color text,
  key text,
  value text,
  table_link text,
  synced_at timestamptz not null default now()
);

create table if not exists public.faq (
  source_team_id bigint not null,
  source text,
  question text,
  answer text,
  synced_at timestamptz not null default now()
);

create table if not exists public.tabs (
  source_team_id bigint not null,
  tab text,
  synced_at timestamptz not null default now()
);

create table if not exists public.last_lineup (
  source_team_id bigint not null,
  lineup_team_id bigint,
  team_name text,
  formation text,
  team_rating double precision,
  average_starter_age integer,
  total_starter_market_value bigint,
  coach_id bigint,
  coach_name text,
  synced_at timestamptz not null default now()
);

create table if not exists public.last_lineup_players (
  source_team_id bigint not null,
  section text,
  player_id bigint,
  name text,
  first_name text,
  last_name text,
  age integer,
  country_name text,
  country_code text,
  shirt_number integer,
  position_id double precision,
  usual_playing_position_id double precision,
  is_captain boolean,
  market_value double precision,
  performance_rating double precision,
  season_goals double precision,
  season_assists double precision,
  season_rating double precision,
  events jsonb,
  horizontal_x double precision,
  horizontal_y double precision,
  vertical_x double precision,
  vertical_y double precision,
  synced_at timestamptz not null default now()
);

create table if not exists public.match_details (
  source_team_id bigint not null,
  source_fixture_id bigint,
  fotmob_match_id bigint,
  match_name text,
  league_id bigint,
  league_name text,
  parent_league_id bigint,
  country_code text,
  match_round text,
  league_round_name text,
  match_time_utc text,
  match_time_utc_date timestamptz,
  started boolean,
  finished boolean,
  coverage_level text,
  home_team_id bigint,
  home_team_name text,
  home_team_score integer,
  away_team_id bigint,
  away_team_name text,
  away_team_score integer,
  status_score_str text,
  status_reason_short text,
  status_reason_long text,
  player_of_match_id double precision,
  player_of_match_name text,
  attendance double precision,
  referee_name text,
  referee_country text,
  stadium_name text,
  stadium_city text,
  stadium_country text,
  stadium_lat double precision,
  stadium_long double precision,
  stadium_capacity double precision,
  stadium_surface text,
  qa_count integer,
  home_top_player_count integer,
  away_top_player_count integer,
  synced_at timestamptz not null default now()
);

create table if not exists public.match_events (
  source_team_id bigint not null,
  source_fixture_id bigint,
  fotmob_match_id bigint,
  event_id double precision,
  react_key text,
  time integer,
  time_str text,
  overload_time double precision,
  overload_time_str text,
  type text,
  is_home boolean,
  team_side text,
  player_id double precision,
  player_name text,
  profile_url text,
  card text,
  card_description text,
  home_score integer,
  away_score integer,
  name_str text,
  full_name text,
  event_payload jsonb,
  synced_at timestamptz not null default now()
);

create table if not exists public.match_stats (
  source_team_id bigint not null,
  source_fixture_id bigint,
  fotmob_match_id bigint,
  period text,
  group_title text,
  group_key text,
  stat_title text,
  stat_key text,
  home_value text,
  away_value text,
  format text,
  stat_type text,
  highlighted text,
  synced_at timestamptz not null default now()
);

create table if not exists public.match_shots (
  source_team_id bigint not null,
  source_fixture_id bigint,
  fotmob_match_id bigint,
  shot_id bigint,
  player_id bigint,
  player_name text,
  team_id bigint,
  team_color text,
  period text,
  minute integer,
  minute_added double precision,
  event_type text,
  situation text,
  shot_type text,
  expected_goals double precision,
  expected_goals_on_target double precision,
  is_on_target boolean,
  is_blocked boolean,
  is_own_goal boolean,
  is_saved_off_line boolean,
  is_from_inside_box boolean,
  x double precision,
  y double precision,
  goal_crossed_y double precision,
  goal_crossed_z double precision,
  blocked_x double precision,
  blocked_y double precision,
  keeper_id double precision,
  synced_at timestamptz not null default now()
);

create table if not exists public.match_lineup_players (
  source_team_id bigint not null,
  source_fixture_id bigint,
  fotmob_match_id bigint,
  team_side text,
  lineup_team_id bigint,
  team_name text,
  formation text,
  team_rating double precision,
  section text,
  player_id bigint,
  name text,
  first_name text,
  last_name text,
  age double precision,
  country_name text,
  country_code text,
  shirt_number integer,
  position_id double precision,
  usual_playing_position_id double precision,
  market_value double precision,
  performance_rating double precision,
  horizontal_x double precision,
  horizontal_y double precision,
  vertical_x double precision,
  vertical_y double precision,
  synced_at timestamptz not null default now()
);

create table if not exists public.match_player_stats (
  source_team_id bigint not null,
  source_fixture_id bigint,
  fotmob_match_id bigint,
  player_id bigint,
  player_name text,
  stat_team_id bigint,
  team_name text,
  is_goalkeeper boolean,
  section_title text,
  section_key text,
  stat_title text,
  stat_key text,
  stat_value double precision,
  stat_total double precision,
  stat_type text,
  synced_at timestamptz not null default now()
);

create table if not exists public.player_profiles (
  source_team_id bigint not null,
  player_id bigint,
  player_image_url text,
  name text,
  birth_date text,
  gender text,
  status text,
  data_provider text,
  is_captain boolean,
  is_coach boolean,
  primary_team_id bigint,
  primary_team_name text,
  on_loan boolean,
  primary_position text,
  height_cm double precision,
  shirt_number integer,
  age integer,
  preferred_foot text,
  country text,
  country_code text,
  market_value bigint,
  contract_end_utc timestamptz,
  next_match_id bigint,
  next_match_date timestamptz,
  next_match_league text,
  main_league_id bigint,
  main_league_name text,
  main_league_season text,
  main_league_stats jsonb,
  traits_key text,
  traits_title text,
  injury_information jsonb,
  meta_json jsonb,
  synced_at timestamptz not null default now()
);

create table if not exists public.player_recent_matches (
  source_team_id bigint not null,
  player_id bigint,
  match_id bigint,
  match_date timestamptz,
  match_page_url text,
  league_id bigint,
  league_name text,
  stage text,
  team_id bigint,
  team_name text,
  opponent_team_id bigint,
  opponent_team_name text,
  is_home_team boolean,
  home_score integer,
  away_score integer,
  minutes_played integer,
  goals integer,
  assists integer,
  yellow_cards integer,
  red_cards integer,
  rating double precision,
  is_top_rating boolean,
  player_of_the_match boolean,
  on_bench boolean,
  synced_at timestamptz not null default now()
);

create table if not exists public.player_career_entries (
  source_team_id bigint not null,
  player_id bigint,
  career_stage text,
  entry_type text,
  team_id bigint,
  team_name text,
  team_gender text,
  show_team_gender boolean,
  transfer_type text,
  start_date timestamptz,
  end_date timestamptz,
  active boolean,
  role text,
  season_name text,
  appearances integer,
  goals integer,
  assists double precision,
  rating double precision,
  league_id double precision,
  league_name text,
  tournament_id double precision,
  is_friendly boolean,
  synced_at timestamptz not null default now()
);

create table if not exists public.player_market_values (
  source_team_id bigint not null,
  player_id bigint,
  date timestamptz,
  value bigint,
  currency text,
  lower_bound bigint,
  upper_bound bigint,
  source text,
  team_id double precision,
  team_name text,
  is_period_start boolean,
  synced_at timestamptz not null default now()
);

create table if not exists public.player_trophies (
  source_team_id bigint not null,
  player_id bigint,
  trophy_type text,
  team_id bigint,
  team_name text,
  country_code text,
  league_id bigint,
  league_name text,
  seasons_won jsonb,
  seasons_runner_up jsonb,
  synced_at timestamptz not null default now()
);

create table if not exists public.player_traits (
  source_team_id bigint not null,
  player_id bigint,
  traits_key text,
  traits_title text,
  item_key text,
  item_title text,
  item_value double precision,
  synced_at timestamptz not null default now()
);

alter table public.fixtures enable row level security;
alter table public.squad enable row level security;
alter table public.player_stats enable row level security;
alter table public.player_stat_rankings enable row level security;
alter table public.team_stat_rankings enable row level security;
alter table public.team_info enable row level security;
alter table public.league_table enable row level security;
alter table public.table_legend enable row level security;
alter table public.transfers enable row level security;
alter table public.match_highlights enable row level security;
alter table public.team_form enable row level security;
alter table public.top_players enable row level security;
alter table public.venue enable row level security;
alter table public.coach_history enable row level security;
alter table public.trophies enable row level security;
alter table public.historical_seasons enable row level security;
alter table public.historical_table_rows enable row level security;
alter table public.historical_table_rules enable row level security;
alter table public.faq enable row level security;
alter table public.tabs enable row level security;
alter table public.last_lineup enable row level security;
alter table public.last_lineup_players enable row level security;
alter table public.match_details enable row level security;
alter table public.match_events enable row level security;
alter table public.match_stats enable row level security;
alter table public.match_shots enable row level security;
alter table public.match_lineup_players enable row level security;
alter table public.match_player_stats enable row level security;
alter table public.player_profiles enable row level security;
alter table public.player_recent_matches enable row level security;
alter table public.player_career_entries enable row level security;
alter table public.player_market_values enable row level security;
alter table public.player_trophies enable row level security;
alter table public.player_traits enable row level security;

create index if not exists fixtures_source_team_id_idx
  on public.fixtures (source_team_id);
create index if not exists fixtures_utc_time_idx
  on public.fixtures (utc_time);
create index if not exists fixtures_tournament_id_idx
  on public.fixtures (tournament_id);

create index if not exists squad_source_team_id_idx
  on public.squad (source_team_id);
create index if not exists squad_position_group_idx
  on public.squad (position_group);
create index if not exists squad_country_code_idx
  on public.squad (country_code);

create index if not exists player_stats_source_team_id_idx
  on public.player_stats (source_team_id);
create index if not exists player_stats_stat_team_id_idx
  on public.player_stats (stat_team_id);
create index if not exists player_stats_category_idx
  on public.player_stats (category);

create index if not exists player_stat_rankings_source_team_id_idx
  on public.player_stat_rankings (source_team_id);
create index if not exists player_stat_rankings_player_id_idx
  on public.player_stat_rankings (player_id);
create index if not exists player_stat_rankings_category_idx
  on public.player_stat_rankings (category);
create index if not exists player_stat_rankings_stat_team_id_idx
  on public.player_stat_rankings (stat_team_id);

create index if not exists team_stat_rankings_source_team_id_idx
  on public.team_stat_rankings (source_team_id);
create index if not exists team_stat_rankings_stat_team_id_idx
  on public.team_stat_rankings (stat_team_id);
create index if not exists team_stat_rankings_category_idx
  on public.team_stat_rankings (category);

create index if not exists team_info_source_team_id_idx
  on public.team_info (source_team_id);
create index if not exists team_info_team_id_idx
  on public.team_info (team_id);
create index if not exists team_info_primary_league_id_idx
  on public.team_info (primary_league_id);

create index if not exists league_table_source_team_id_idx
  on public.league_table (source_team_id);
create index if not exists league_table_league_id_idx
  on public.league_table (league_id);
create index if not exists league_table_table_team_id_idx
  on public.league_table (table_team_id);
create index if not exists league_table_position_idx
  on public.league_table (position);

create index if not exists table_legend_source_team_id_idx
  on public.table_legend (source_team_id);
create index if not exists table_legend_league_id_idx
  on public.table_legend (league_id);

create index if not exists transfers_source_team_id_idx
  on public.transfers (source_team_id);
create index if not exists transfers_player_id_idx
  on public.transfers (player_id);
create index if not exists transfers_from_club_id_idx
  on public.transfers (from_club_id);
create index if not exists transfers_to_club_id_idx
  on public.transfers (to_club_id);
create index if not exists transfers_transfer_date_idx
  on public.transfers (transfer_date);

create index if not exists match_highlights_source_team_id_idx
  on public.match_highlights (source_team_id);
create index if not exists match_highlights_fixture_id_idx
  on public.match_highlights (fixture_id);
create index if not exists match_highlights_tournament_id_idx
  on public.match_highlights (tournament_id);
create index if not exists match_highlights_utc_time_idx
  on public.match_highlights (utc_time);

create index if not exists team_form_source_team_id_idx
  on public.team_form (source_team_id);
create index if not exists team_form_sequence_idx
  on public.team_form (sequence);
create index if not exists team_form_utc_time_idx
  on public.team_form (utc_time);
create index if not exists team_form_opponent_id_idx
  on public.team_form (opponent_id);

create index if not exists top_players_source_team_id_idx
  on public.top_players (source_team_id);
create index if not exists top_players_player_id_idx
  on public.top_players (player_id);
create index if not exists top_players_team_id_idx
  on public.top_players (team_id);
create index if not exists top_players_group_name_idx
  on public.top_players (group_name);

create index if not exists venue_source_team_id_idx
  on public.venue (source_team_id);

create index if not exists coach_history_source_team_id_idx
  on public.coach_history (source_team_id);
create index if not exists coach_history_coach_id_idx
  on public.coach_history (coach_id);
create index if not exists coach_history_league_id_idx
  on public.coach_history (league_id);

create index if not exists trophies_source_team_id_idx
  on public.trophies (source_team_id);
create index if not exists trophies_tournament_template_id_idx
  on public.trophies (tournament_template_id);

create index if not exists historical_seasons_source_team_id_idx
  on public.historical_seasons (source_team_id);
create index if not exists historical_seasons_tournament_id_idx
  on public.historical_seasons (tournament_id);
create index if not exists historical_seasons_season_name_idx
  on public.historical_seasons (season_name);

create index if not exists historical_table_rows_source_team_id_idx
  on public.historical_table_rows (source_team_id);
create index if not exists historical_table_rows_league_id_idx
  on public.historical_table_rows (league_id);
create index if not exists historical_table_rows_team_id_idx
  on public.historical_table_rows (team_id);
create index if not exists historical_table_rows_season_name_idx
  on public.historical_table_rows (season_name);

create index if not exists historical_table_rules_source_team_id_idx
  on public.historical_table_rules (source_team_id);
create index if not exists historical_table_rules_league_id_idx
  on public.historical_table_rules (league_id);
create index if not exists historical_table_rules_season_name_idx
  on public.historical_table_rules (season_name);

create index if not exists faq_source_team_id_idx
  on public.faq (source_team_id);

create index if not exists tabs_source_team_id_idx
  on public.tabs (source_team_id);

create index if not exists last_lineup_source_team_id_idx
  on public.last_lineup (source_team_id);
create index if not exists last_lineup_lineup_team_id_idx
  on public.last_lineup (lineup_team_id);
create index if not exists last_lineup_coach_id_idx
  on public.last_lineup (coach_id);

create index if not exists last_lineup_players_source_team_id_idx
  on public.last_lineup_players (source_team_id);
create index if not exists last_lineup_players_player_id_idx
  on public.last_lineup_players (player_id);
create index if not exists last_lineup_players_section_idx
  on public.last_lineup_players (section);

create index if not exists match_details_source_team_id_idx
  on public.match_details (source_team_id);
create index if not exists match_details_source_fixture_id_idx
  on public.match_details (source_fixture_id);
create index if not exists match_details_fotmob_match_id_idx
  on public.match_details (fotmob_match_id);
create index if not exists match_details_league_id_idx
  on public.match_details (league_id);
create index if not exists match_details_match_time_utc_date_idx
  on public.match_details (match_time_utc_date);

create index if not exists match_events_source_team_id_idx
  on public.match_events (source_team_id);
create index if not exists match_events_source_fixture_id_idx
  on public.match_events (source_fixture_id);
create index if not exists match_events_fotmob_match_id_idx
  on public.match_events (fotmob_match_id);
create index if not exists match_events_player_id_idx
  on public.match_events (player_id);
create index if not exists match_events_type_idx
  on public.match_events (type);

create index if not exists match_stats_source_team_id_idx
  on public.match_stats (source_team_id);
create index if not exists match_stats_source_fixture_id_idx
  on public.match_stats (source_fixture_id);
create index if not exists match_stats_fotmob_match_id_idx
  on public.match_stats (fotmob_match_id);
create index if not exists match_stats_group_key_idx
  on public.match_stats (group_key);
create index if not exists match_stats_stat_key_idx
  on public.match_stats (stat_key);

create index if not exists match_shots_source_team_id_idx
  on public.match_shots (source_team_id);
create index if not exists match_shots_source_fixture_id_idx
  on public.match_shots (source_fixture_id);
create index if not exists match_shots_fotmob_match_id_idx
  on public.match_shots (fotmob_match_id);
create index if not exists match_shots_shot_id_idx
  on public.match_shots (shot_id);
create index if not exists match_shots_player_id_idx
  on public.match_shots (player_id);
create index if not exists match_shots_team_id_idx
  on public.match_shots (team_id);

create index if not exists match_lineup_players_source_team_id_idx
  on public.match_lineup_players (source_team_id);
create index if not exists match_lineup_players_source_fixture_id_idx
  on public.match_lineup_players (source_fixture_id);
create index if not exists match_lineup_players_fotmob_match_id_idx
  on public.match_lineup_players (fotmob_match_id);
create index if not exists match_lineup_players_lineup_team_id_idx
  on public.match_lineup_players (lineup_team_id);
create index if not exists match_lineup_players_player_id_idx
  on public.match_lineup_players (player_id);

create index if not exists match_player_stats_source_team_id_idx
  on public.match_player_stats (source_team_id);
create index if not exists match_player_stats_source_fixture_id_idx
  on public.match_player_stats (source_fixture_id);
create index if not exists match_player_stats_fotmob_match_id_idx
  on public.match_player_stats (fotmob_match_id);
create index if not exists match_player_stats_player_id_idx
  on public.match_player_stats (player_id);
create index if not exists match_player_stats_stat_team_id_idx
  on public.match_player_stats (stat_team_id);

create index if not exists player_profiles_source_team_id_idx
  on public.player_profiles (source_team_id);
create index if not exists player_profiles_player_id_idx
  on public.player_profiles (player_id);
create index if not exists player_profiles_primary_team_id_idx
  on public.player_profiles (primary_team_id);
create index if not exists player_profiles_main_league_id_idx
  on public.player_profiles (main_league_id);
create index if not exists player_profiles_next_match_id_idx
  on public.player_profiles (next_match_id);

create index if not exists player_recent_matches_source_team_id_idx
  on public.player_recent_matches (source_team_id);
create index if not exists player_recent_matches_player_id_idx
  on public.player_recent_matches (player_id);
create index if not exists player_recent_matches_match_id_idx
  on public.player_recent_matches (match_id);
create index if not exists player_recent_matches_team_id_idx
  on public.player_recent_matches (team_id);
create index if not exists player_recent_matches_match_date_idx
  on public.player_recent_matches (match_date);

create index if not exists player_career_entries_source_team_id_idx
  on public.player_career_entries (source_team_id);
create index if not exists player_career_entries_player_id_idx
  on public.player_career_entries (player_id);
create index if not exists player_career_entries_team_id_idx
  on public.player_career_entries (team_id);
create index if not exists player_career_entries_league_id_idx
  on public.player_career_entries (league_id);
create index if not exists player_career_entries_start_date_idx
  on public.player_career_entries (start_date);

create index if not exists player_market_values_source_team_id_idx
  on public.player_market_values (source_team_id);
create index if not exists player_market_values_player_id_idx
  on public.player_market_values (player_id);
create index if not exists player_market_values_date_idx
  on public.player_market_values (date);
create index if not exists player_market_values_team_id_idx
  on public.player_market_values (team_id);

create index if not exists player_trophies_source_team_id_idx
  on public.player_trophies (source_team_id);
create index if not exists player_trophies_player_id_idx
  on public.player_trophies (player_id);
create index if not exists player_trophies_team_id_idx
  on public.player_trophies (team_id);
create index if not exists player_trophies_league_id_idx
  on public.player_trophies (league_id);

create index if not exists player_traits_source_team_id_idx
  on public.player_traits (source_team_id);
create index if not exists player_traits_player_id_idx
  on public.player_traits (player_id);
create index if not exists player_traits_traits_key_idx
  on public.player_traits (traits_key);
create index if not exists player_traits_item_key_idx
  on public.player_traits (item_key);

grant usage on schema public to anon, authenticated;

grant select on table
  public.fixtures,
  public.squad,
  public.player_stats,
  public.player_stat_rankings,
  public.team_stat_rankings,
  public.team_info,
  public.league_table,
  public.table_legend,
  public.transfers,
  public.match_highlights,
  public.team_form,
  public.top_players,
  public.venue,
  public.coach_history,
  public.trophies,
  public.historical_seasons,
  public.historical_table_rows,
  public.historical_table_rules,
  public.faq,
  public.tabs,
  public.last_lineup,
  public.last_lineup_players,
  public.match_details,
  public.match_events,
  public.match_stats,
  public.match_shots,
  public.match_lineup_players,
  public.match_player_stats,
  public.player_profiles,
  public.player_recent_matches,
  public.player_career_entries,
  public.player_market_values,
  public.player_trophies,
  public.player_traits
to anon, authenticated;

drop policy if exists "Allow public read fixtures" on public.fixtures;
create policy "Allow public read fixtures"
  on public.fixtures for select to anon, authenticated using (true);

drop policy if exists "Allow public read squad" on public.squad;
create policy "Allow public read squad"
  on public.squad for select to anon, authenticated using (true);

drop policy if exists "Allow public read player_stats" on public.player_stats;
create policy "Allow public read player_stats"
  on public.player_stats for select to anon, authenticated using (true);

drop policy if exists "Allow public read player_stat_rankings" on public.player_stat_rankings;
create policy "Allow public read player_stat_rankings"
  on public.player_stat_rankings for select to anon, authenticated using (true);

drop policy if exists "Allow public read team_stat_rankings" on public.team_stat_rankings;
create policy "Allow public read team_stat_rankings"
  on public.team_stat_rankings for select to anon, authenticated using (true);

drop policy if exists "Allow public read team_info" on public.team_info;
create policy "Allow public read team_info"
  on public.team_info for select to anon, authenticated using (true);

drop policy if exists "Allow public read league_table" on public.league_table;
create policy "Allow public read league_table"
  on public.league_table for select to anon, authenticated using (true);

drop policy if exists "Allow public read table_legend" on public.table_legend;
create policy "Allow public read table_legend"
  on public.table_legend for select to anon, authenticated using (true);

drop policy if exists "Allow public read transfers" on public.transfers;
create policy "Allow public read transfers"
  on public.transfers for select to anon, authenticated using (true);

drop policy if exists "Allow public read match_highlights" on public.match_highlights;
create policy "Allow public read match_highlights"
  on public.match_highlights for select to anon, authenticated using (true);

drop policy if exists "Allow public read team_form" on public.team_form;
create policy "Allow public read team_form"
  on public.team_form for select to anon, authenticated using (true);

drop policy if exists "Allow public read top_players" on public.top_players;
create policy "Allow public read top_players"
  on public.top_players for select to anon, authenticated using (true);

drop policy if exists "Allow public read venue" on public.venue;
create policy "Allow public read venue"
  on public.venue for select to anon, authenticated using (true);

drop policy if exists "Allow public read coach_history" on public.coach_history;
create policy "Allow public read coach_history"
  on public.coach_history for select to anon, authenticated using (true);

drop policy if exists "Allow public read trophies" on public.trophies;
create policy "Allow public read trophies"
  on public.trophies for select to anon, authenticated using (true);

drop policy if exists "Allow public read historical_seasons" on public.historical_seasons;
create policy "Allow public read historical_seasons"
  on public.historical_seasons for select to anon, authenticated using (true);

drop policy if exists "Allow public read historical_table_rows" on public.historical_table_rows;
create policy "Allow public read historical_table_rows"
  on public.historical_table_rows for select to anon, authenticated using (true);

drop policy if exists "Allow public read historical_table_rules" on public.historical_table_rules;
create policy "Allow public read historical_table_rules"
  on public.historical_table_rules for select to anon, authenticated using (true);

drop policy if exists "Allow public read faq" on public.faq;
create policy "Allow public read faq"
  on public.faq for select to anon, authenticated using (true);

drop policy if exists "Allow public read tabs" on public.tabs;
create policy "Allow public read tabs"
  on public.tabs for select to anon, authenticated using (true);

drop policy if exists "Allow public read last_lineup" on public.last_lineup;
create policy "Allow public read last_lineup"
  on public.last_lineup for select to anon, authenticated using (true);

drop policy if exists "Allow public read last_lineup_players" on public.last_lineup_players;
create policy "Allow public read last_lineup_players"
  on public.last_lineup_players for select to anon, authenticated using (true);

drop policy if exists "Allow public read match_details" on public.match_details;
create policy "Allow public read match_details"
  on public.match_details for select to anon, authenticated using (true);

drop policy if exists "Allow public read match_events" on public.match_events;
create policy "Allow public read match_events"
  on public.match_events for select to anon, authenticated using (true);

drop policy if exists "Allow public read match_stats" on public.match_stats;
create policy "Allow public read match_stats"
  on public.match_stats for select to anon, authenticated using (true);

drop policy if exists "Allow public read match_shots" on public.match_shots;
create policy "Allow public read match_shots"
  on public.match_shots for select to anon, authenticated using (true);

drop policy if exists "Allow public read match_lineup_players" on public.match_lineup_players;
create policy "Allow public read match_lineup_players"
  on public.match_lineup_players for select to anon, authenticated using (true);

drop policy if exists "Allow public read match_player_stats" on public.match_player_stats;
create policy "Allow public read match_player_stats"
  on public.match_player_stats for select to anon, authenticated using (true);

drop policy if exists "Allow public read player_profiles" on public.player_profiles;
create policy "Allow public read player_profiles"
  on public.player_profiles for select to anon, authenticated using (true);

drop policy if exists "Allow public read player_recent_matches" on public.player_recent_matches;
create policy "Allow public read player_recent_matches"
  on public.player_recent_matches for select to anon, authenticated using (true);

drop policy if exists "Allow public read player_career_entries" on public.player_career_entries;
create policy "Allow public read player_career_entries"
  on public.player_career_entries for select to anon, authenticated using (true);

drop policy if exists "Allow public read player_market_values" on public.player_market_values;
create policy "Allow public read player_market_values"
  on public.player_market_values for select to anon, authenticated using (true);

drop policy if exists "Allow public read player_trophies" on public.player_trophies;
create policy "Allow public read player_trophies"
  on public.player_trophies for select to anon, authenticated using (true);

drop policy if exists "Allow public read player_traits" on public.player_traits;
create policy "Allow public read player_traits"
  on public.player_traits for select to anon, authenticated using (true);
