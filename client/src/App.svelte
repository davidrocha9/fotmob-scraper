<script>
  import { onMount } from 'svelte'
  import { loadTeamData } from './lib/csv.js'
  import Squad from './lib/Squad.svelte'
  import Fixtures from './lib/Fixtures.svelte'
  import Stats from './lib/Stats.svelte'
  import Transfers from './lib/Transfers.svelte'

  let data = {}
  let loading = true
  let activeTab = 'overview'

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'team_performance', label: 'History' },
    { id: 'match_analysis', label: 'Matches' },
    { id: 'stats', label: 'Player Stats' },
    { id: 'squad_transfers', label: 'Squad' },
    { id: 'raw', label: 'Data' }
  ]

  async function loadData() {
    loading = true
    data = await loadTeamData()
    loading = false
  }

  function toNumber(value) {
    const n = Number(value)
    return Number.isFinite(n) ? n : 0
  }

  function formatPercent(value) {
    const n = Number(value)
    if (!Number.isFinite(n)) return '-'
    return `${n.toFixed(1)}%`
  }

  function formatDateTime(value) {
    if (!value) return '-'
    const d = new Date(value)
    if (Number.isNaN(d.getTime())) return value
    return d.toLocaleString('en-GB', {
      year: 'numeric',
      month: 'short',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'UTC'
    })
  }

  function parseJSON(value, fallback = null) {
    if (!value) return fallback
    try {
      return JSON.parse(value)
    } catch {
      return fallback
    }
  }

  function countEntries(value) {
    const parsed = Array.isArray(value) ? value : parseJSON(value, [])
    return Array.isArray(parsed) ? parsed.length : 0
  }

  $: team = data.teamInfo?.[0] || null
  $: venue = data.venue?.[0] || null
  $: nextMatch = data.matchHighlights?.find((m) => m.match_type === 'next') || null
  $: lastMatch = data.matchHighlights?.find((m) => m.match_type === 'last') || null
  $: topPlayers = data.topPlayers || []
  $: teamForm = data.teamForm || []
  $: teamStats = [...(data.teamStatRankings || [])].sort((a, b) => Number(a.rank || 999) - Number(b.rank || 999))
  $: playerRankings = data.playerStatRankings || []
  $: historicalSeasons = data.historicalSeasons || []
  $: historicalTableRows = data.historicalTableRows || []
  $: trophies = data.trophies || []
  $: coachHistory = data.coachHistory || []
  $: lastLineup = data.lastLineup?.[0] || null
  $: lastLineupPlayers = data.lastLineupPlayers || []
  $: starters = lastLineupPlayers.filter((p) => p.section === 'starter')
  $: squad = data.squad || []
  $: leaguePosition = (data.leagueTable || []).find((r) => r.team_id === team?.team_id && r.table_type === 'all') || null
  $: bestTeamStats = teamStats.slice(0, 6)
  $: topScorers = [...playerRankings]
    .filter((r) => r.category === 'goals')
    .sort((a, b) => Number(a.rank || 999) - Number(b.rank || 999))
    .slice(0, 4)
  $: topCreators = [...playerRankings]
    .filter((r) => r.category === 'goal_assist')
    .sort((a, b) => Number(a.rank || 999) - Number(b.rank || 999))
    .slice(0, 4)
  $: recentHistory = [...historicalSeasons].slice(-8).reverse()
  $: latestHistoricalSeasonName = historicalSeasons.length ? historicalSeasons[historicalSeasons.length - 1].season_name : null
  $: latestHistoricalStandings = historicalTableRows.filter((r) => r.season_name === latestHistoricalSeasonName).slice(0, 8)
  $: wonTrophies = trophies.filter((trophy) => toNumber(trophy.won) > 0)
  $: decoratedPlayers = Object.values(playerRankings.reduce((acc, row) => {
    if (!row.player_id) return acc
    if (!acc[row.player_id]) {
      acc[row.player_id] = { player_id: row.player_id, points: 0 }
    }
    acc[row.player_id].points += Math.max(0, 12 - Number(row.rank || 99))
    return acc
  }, {}))
    .map((entry) => {
      const profile = (data.playerProfiles || []).find((player) => player.player_id === entry.player_id)
      return {
        player_id: entry.player_id,
        name: profile?.name || `Player ${entry.player_id}`,
        points: entry.points,
        role: profile?.primary_position || profile?.position || '-',
        country: profile?.country_code || '-'
      }
    })
    .sort((a, b) => b.points - a.points)
    .slice(0, 4)

  $: rawDatasets = [
    ['teamInfo', data.teamInfo],
    ['squad', data.squad],
    ['fixtures', data.fixtures],
    ['playerStats', data.playerStats],
    ['playerStatRankings', data.playerStatRankings],
    ['teamStatRankings', data.teamStatRankings],
    ['leagueTable', data.leagueTable],
    ['tableLegend', data.tableLegend],
    ['transfers', data.transfers],
    ['matchHighlights', data.matchHighlights],
    ['teamForm', data.teamForm],
    ['topPlayers', data.topPlayers],
    ['venue', data.venue],
    ['coachHistory', data.coachHistory],
    ['trophies', data.trophies],
    ['historicalSeasons', data.historicalSeasons],
    ['historicalTableRows', data.historicalTableRows],
    ['historicalTableRules', data.historicalTableRules],
    ['faq', data.faq],
    ['tabs', data.tabs],
    ['lastLineup', data.lastLineup],
    ['lastLineupPlayers', data.lastLineupPlayers],
    ['matchDetails', data.matchDetails],
    ['matchEvents', data.matchEvents],
    ['matchStats', data.matchStats],
    ['matchShots', data.matchShots],
    ['matchLineupPlayers', data.matchLineupPlayers],
    ['matchPlayerStats', data.matchPlayerStats],
    ['playerProfiles', data.playerProfiles],
    ['playerRecentMatches', data.playerRecentMatches],
    ['playerCareerEntries', data.playerCareerEntries],
    ['playerMarketValues', data.playerMarketValues],
    ['playerTrophies', data.playerTrophies],
    ['playerTraits', data.playerTraits]
  ]

  onMount(loadData)
</script>

<main class="shell">
  <header class="page-header">
    <h1>{team?.team_name || 'Team Data'}</h1>
    {#if team}
      <span class="season">{team.season || team.latest_season}</span>
    {/if}
  </header>

  {#if loading}
    <div class="loading">Loading data...</div>
  {:else if !team}
    <div class="loading">No team data found. Run `python3 scraper/scraper.py` first.</div>
  {:else}
    <nav class="tabs">
      {#each tabs as tab}
        <button class:active={activeTab === tab.id} on:click={() => (activeTab = tab.id)}>
          {tab.label}
        </button>
      {/each}
    </nav>

    <div class="content">
      {#if activeTab === 'overview'}
        <section class="overview-stack">
          <article class="panel overview-hero">
            <div class="panel-header">
              <div>
                <span class="eyebrow">Next fixture</span>
                <h2>Match focus</h2>
              </div>
            </div>
            <div class="match-focus-card">
              <div class="match-focus-team">
                <strong>{team.team_name}</strong>
                <small>{team.primary_league_name || '-'}</small>
              </div>
              <div class="match-focus-center">
                <span class="match-focus-time">{formatDateTime(nextMatch?.utc_time)}</span>
                <strong class="match-focus-vs">vs</strong>
                <small>{nextMatch?.tournament || '-'}</small>
              </div>
              <div class="match-focus-team is-opponent">
                <strong>{nextMatch?.opponent || 'No upcoming match'}</strong>
                <small>{nextMatch?.start_day || '-'}</small>
              </div>
            </div>
          </article>

          <div class="panel-grid overview-main-grid">
            <article class="panel">
              <div class="panel-header">
                <div>
                  <span class="eyebrow">Venue</span>
                  <h2>{venue?.stadium_name || team.stadium_name || '-'}</h2>
                </div>
              </div>
              <div class="info-card-grid">
                <div class="info-card">
                  <span>City</span>
                  <strong>{venue?.city || team.stadium_city || '-'}</strong>
                </div>
                <div class="info-card">
                  <span>Surface</span>
                  <strong>{venue?.surface || team.surface || '-'}</strong>
                </div>
                <div class="info-card">
                  <span>Capacity</span>
                  <strong>{venue?.capacity || team.capacity || '-'}</strong>
                </div>
                <div class="info-card">
                  <span>Opened</span>
                  <strong>{venue?.opened || team.opened || '-'}</strong>
                </div>
              </div>
            </article>

            <article class="panel">
              <div class="panel-header">
                <div>
                  <span class="eyebrow">Form</span>
                  <h2>Recent sequence</h2>
                </div>
              </div>
              <div class="form-sequence-card">
                <div class="form-sequence-strip">
                  {#each teamForm as match}
                    <div class="form-badge result-{(match.result_string || '').toLowerCase()}">
                      {match.result_string}
                    </div>
                  {/each}
                </div>
                <div class="form-sequence-list">
                  {#each teamForm.slice(0, 5) as match}
                    <div class="form-line-row">
                      <strong>{match.opponent_name}</strong>
                      <span>{match.score || '-'}</span>
                    </div>
                  {/each}
                </div>
              </div>
            </article>

            <article class="panel span-2">
              <div class="panel-header">
                <div>
                  <span class="eyebrow">League rankings</span>
                  <h2>Best team metrics</h2>
                </div>
              </div>
              <div class="rank-metric-grid">
                {#each bestTeamStats as stat}
                  <div class="rank-metric-card">
                    <span>Rank #{stat.rank}</span>
                    <strong>{stat.value}</strong>
                    <b>{stat.title}</b>
                    <small>{stat.league_name}</small>
                  </div>
                {/each}
              </div>
            </article>

            <article class="panel span-2">
              <div class="panel-header">
                <div>
                  <span class="eyebrow">Standouts</span>
                  <h2>Analyst shortlist</h2>
                </div>
              </div>
              <div class="standout-grid">
                <div class="standout-column">
                  <h3>Top scorers</h3>
                  {#each topScorers as player}
                    <div class="standout-row">
                      <div>
                        <strong>{player.player_name}</strong>
                        <small>{player.player_country || '-'}</small>
                      </div>
                      <b>{player.value}</b>
                    </div>
                  {/each}
                </div>
                <div class="standout-column">
                  <h3>Top creators</h3>
                  {#each topCreators as player}
                    <div class="standout-row">
                      <div>
                        <strong>{player.player_name}</strong>
                        <small>{player.player_country || '-'}</small>
                      </div>
                      <b>{player.value}</b>
                    </div>
                  {/each}
                </div>
                <div class="standout-column">
                  <h3>Overall impact</h3>
                  {#each decoratedPlayers as player}
                    <div class="standout-row">
                      <div>
                        <strong>{player.name}</strong>
                        <small>{player.role} · {player.country}</small>
                      </div>
                      <b>{player.points}</b>
                    </div>
                  {/each}
                </div>
              </div>
            </article>
          </div>
        </section>
      {:else if activeTab === 'team_performance'}
        <section class="panel-grid history-grid">
          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">Timeline</span>
                <h2>Season-by-season</h2>
              </div>
            </div>
            <div class="history-table">
              <div class="history-row history-head">
                <span>Season</span>
                <span>Competition</span>
                <span>Pos</span>
                <span>Pts</span>
              </div>
              {#each recentHistory as season}
                <div class="history-row">
                  <span>{season.season_name}</span>
                  <span>{season.tournament_name}</span>
                  <span>#{season.position}</span>
                  <span>{season.points}</span>
                </div>
              {/each}
            </div>
          </article>

          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">Historical table</span>
                <h2>{latestHistoricalSeasonName || 'Latest season'}</h2>
              </div>
            </div>
            <div class="history-table">
              <div class="history-row history-head standings-head">
                <span>Pos</span>
                <span>Club</span>
                <span>Pts</span>
                <span>GD</span>
              </div>
              {#each latestHistoricalStandings as row}
                <div class="history-row standings-row">
                  <span>#{row.position}</span>
                  <span>{row.team_name}</span>
                  <span>{row.points}</span>
                  <span>{toNumber(row.goals_for) - toNumber(row.goals_against)}</span>
                </div>
              {/each}
            </div>
          </article>

          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">Silverware</span>
                <h2>Won trophies</h2>
              </div>
            </div>
            <div class="trophy-list">
              {#each wonTrophies.slice(0, 10) as trophy}
                <div class="trophy-item">
                  <strong>{trophy.name}</strong>
                  <small>{trophy.area}</small>
                  <span>{trophy.won} won</span>
                </div>
              {/each}
            </div>
          </article>

          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">Managers</span>
                <h2>Coach history</h2>
              </div>
            </div>
            <div class="coach-grid">
              {#each coachHistory.slice(0, 12) as coach}
                <div class="coach-card">
                  <strong>{coach.coach_name}</strong>
                  <span>{coach.season}</span>
                  <small>{coach.league_name}</small>
                  <b>{formatPercent(Number(coach.win_percentage || 0) * 100)} win rate</b>
                </div>
              {/each}
            </div>
          </article>
        </section>
      {:else if activeTab === 'match_analysis'}
        <Fixtures
          data={data.fixtures || []}
          teamForm={data.teamForm || []}
          matchHighlights={data.matchHighlights || []}
          matchDetails={data.matchDetails || []}
          matchEvents={data.matchEvents || []}
          matchStats={data.matchStats || []}
          matchShots={data.matchShots || []}
          matchLineupPlayers={data.matchLineupPlayers || []}
          matchPlayerStats={data.matchPlayerStats || []}
        />
      {:else if activeTab === 'stats'}
        <Stats
          data={data.playerStats || []}
          playerRankings={data.playerStatRankings || []}
          teamRankings={data.teamStatRankings || []}
          topPlayers={data.topPlayers || []}
          playerProfiles={data.playerProfiles || []}
          playerRecentMatches={data.playerRecentMatches || []}
          playerMarketValues={data.playerMarketValues || []}
          playerTraits={data.playerTraits || []}
        />
      {:else if activeTab === 'squad_transfers'}
        <div class="squad-page-stack">
          <Squad
            data={data.squad || []}
            lineup={data.lastLineup || []}
            lineupPlayers={data.lastLineupPlayers || []}
            playerProfiles={data.playerProfiles || []}
            playerCareerEntries={data.playerCareerEntries || []}
            playerMarketValues={data.playerMarketValues || []}
            playerTrophies={data.playerTrophies || []}
            playerTraits={data.playerTraits || []}
            playerRecentMatches={data.playerRecentMatches || []}
          />
          <section>
            <div class="section-block-head">
              <span class="eyebrow">Transfer window</span>
              <h2>Transfers & contract extensions</h2>
            </div>
            <Transfers data={data.transfers || []} />
          </section>
        </div>
      {:else if activeTab === 'raw'}
        <section class="panel raw-panel">
          <div class="panel-header">
            <div>
              <span class="eyebrow">CSV inventory</span>
              <h2>Exported datasets</h2>
            </div>
          </div>
          <div class="dataset-grid">
            {#each rawDatasets as [name, rows]}
              <div class="dataset-card">
                <strong>{name}</strong>
                <span>{rows?.length || 0} rows</span>
                <small>{name.replace(/[A-Z]/g, (m) => `_${m.toLowerCase()}`).replace(/^_/, '')}.csv</small>
              </div>
            {/each}
          </div>
        </section>
      {/if}
    </div>
  {/if}
</main>
