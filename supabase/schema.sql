drop table if exists public.transfers;
drop table if exists public.league_table;
drop table if exists public.team_info;
drop table if exists public.player_stats;
drop table if exists public.squad;
drop table if exists public.fixtures;

create table if not exists public.fixtures (
  source_team_id bigint not null,
  fixture_id bigint not null,
  page_url text,
  opponent text,
  opponent_id bigint,
  home_away jsonb,
  display_tournament text,
  tournament text,
  tournament_id bigint,
  round text,
  result text,
  not_started boolean,
  status jsonb,
  synced_at timestamptz not null default now(),
  primary key (source_team_id, fixture_id)
);

create table if not exists public.squad (
  source_team_id bigint not null,
  player_id bigint not null,
  name text,
  position_group text,
  position text,
  shirt_number integer,
  country_code text,
  country text,
  height integer,
  age integer,
  date_of_birth date,
  rating numeric,
  goals integer,
  assists integer,
  yellow_cards integer,
  red_cards integer,
  market_value bigint,
  synced_at timestamptz not null default now(),
  primary key (source_team_id, player_id)
);

create table if not exists public.player_stats (
  source_team_id bigint not null,
  category text not null,
  category_display text,
  player_id bigint not null,
  player_name text,
  player_country text,
  stat_team_id bigint,
  team_name text,
  rank integer,
  value numeric,
  format text,
  synced_at timestamptz not null default now(),
  primary key (source_team_id, category, player_id)
);

create table if not exists public.team_info (
  source_team_id bigint primary key,
  team_id bigint,
  team_name text,
  team_short_name text,
  season text,
  selected_season text,
  synced_at timestamptz not null default now()
);

create table if not exists public.league_table (
  source_team_id bigint not null,
  league text not null,
  position integer not null,
  table_team_id bigint,
  team_name text,
  played integer,
  wins integer,
  draws integer,
  losses integer,
  goals_for integer,
  goals_against integer,
  goal_difference integer,
  points integer,
  synced_at timestamptz not null default now(),
  primary key (source_team_id, league, position)
);

create table if not exists public.transfers (
  id bigserial primary key,
  source_team_id bigint not null,
  transfer_type text not null,
  player_id bigint,
  player_name text,
  position text,
  from_club text,
  from_club_id bigint,
  to_club text,
  to_club_id bigint,
  transfer_date timestamptz,
  fee text,
  market_value bigint,
  on_loan boolean,
  synced_at timestamptz not null default now()
);

alter table public.fixtures enable row level security;
alter table public.squad enable row level security;
alter table public.player_stats enable row level security;
alter table public.team_info enable row level security;
alter table public.league_table enable row level security;
alter table public.transfers enable row level security;

create index if not exists transfers_source_team_id_idx
  on public.transfers (source_team_id);

create index if not exists league_table_source_team_id_idx
  on public.league_table (source_team_id);
