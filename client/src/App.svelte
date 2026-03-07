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
    { id: 'overview', label: 'Dashboard' },
    { id: 'team_performance', label: 'Team Performance' },
    { id: 'stats', label: 'Player Stats' },
    { id: 'match_analysis', label: 'Match Analysis' },
    { id: 'squad_transfers', label: 'Squad & Transfers' },
    { id: 'raw', label: 'Raw Data' }
  ]

  async function loadData() {
    loading = true
    data = await loadTeamData()
    loading = false
  }

  function toNumber(value) {
    const number = Number(value)
    return Number.isFinite(number) ? number : 0
  }

  function formatCompactNumber(value) {
    const number = Number(value)
    if (!Number.isFinite(number)) return '-'
    return new Intl.NumberFormat('en', { notation: 'compact', maximumFractionDigits: 1 }).format(number)
  }

  function formatPercent(value) {
    const number = Number(value)
    if (!Number.isFinite(number)) return '-'
    return `${number.toFixed(1)}%`
  }

  function formatDateTime(value) {
    if (!value) return '-'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return value
    return date.toLocaleString('en-GB', {
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

  function barStyle(value, max) {
    const width = max > 0 ? Math.max(8, (value / max) * 100) : 0
    return `width: ${Math.min(width, 100)}%`
  }

  $: team = data.teamInfo?.[0] || null
  $: venue = data.venue?.[0] || null
  $: nextMatch = data.matchHighlights?.find(match => match.match_type === 'next') || null
  $: lastMatch = data.matchHighlights?.find(match => match.match_type === 'last') || null
  $: topPlayers = data.topPlayers || []
  $: teamForm = data.teamForm || []
  $: teamStats = [...(data.teamStatRankings || [])].sort((a, b) => Number(a.rank || 999) - Number(b.rank || 999))
  $: playerRankings = data.playerStatRankings || []
  $: historicalSeasons = data.historicalSeasons || []
  $: historicalTableRows = data.historicalTableRows || []
  $: historicalTableRules = data.historicalTableRules || []
  $: trophies = data.trophies || []
  $: coachHistory = data.coachHistory || []
  $: matchDetails = data.matchDetails || []
  $: playerProfiles = data.playerProfiles || []
  $: playerTrophies = data.playerTrophies || []
  $: lastLineup = data.lastLineup?.[0] || null
  $: lastLineupPlayers = data.lastLineupPlayers || []
  $: starters = lastLineupPlayers.filter(player => player.section === 'starter')
  $: squad = data.squad || []
  $: squadMarketValue = squad.reduce((total, player) => total + toNumber(player.market_value), 0)
  $: squadAverageAge = squad.length ? squad.reduce((total, player) => total + toNumber(player.age), 0) / squad.length : 0
  $: leaguePosition = (data.leagueTable || []).find(row => row.team_id === team?.team_id && row.table_type === 'all') || null
  $: trophiesWon = trophies.reduce((total, trophy) => total + toNumber(trophy.won), 0)
  $: bestTeamStats = teamStats.slice(0, 6)
  $: topScorers = [...playerRankings]
    .filter(row => row.category === 'goals')
    .sort((a, b) => Number(a.rank || 999) - Number(b.rank || 999))
    .slice(0, 5)
  $: topCreators = [...playerRankings]
    .filter(row => row.category === 'goal_assist')
    .sort((a, b) => Number(a.rank || 999) - Number(b.rank || 999))
    .slice(0, 5)
  $: recentHistory = [...historicalSeasons].slice(-8).reverse()
  $: lineupMaxValue = Math.max(...starters.map(player => toNumber(player.market_value)), 0)
  $: deepMatchCoverage = matchDetails.length
  $: scoutedProfiles = playerProfiles.length
  $: latestHistoricalSeasonName = historicalSeasons.length ? historicalSeasons[historicalSeasons.length - 1].season_name : null
  $: latestHistoricalStandings = historicalTableRows.filter(row => row.season_name === latestHistoricalSeasonName).slice(0, 8)
  $: latestHistoricalRules = historicalTableRules.filter(rule => rule.season_name === latestHistoricalSeasonName)
  $: decoratedPlayers = Object.values(playerTrophies.reduce((acc, trophy) => {
    const playerId = trophy.player_id
    const seasonsWon = countEntries(trophy.seasons_won)
    if (!acc[playerId]) {
      const profile = playerProfiles.find(item => item.player_id === playerId)
      acc[playerId] = {
        player_id: playerId,
        name: profile?.name || `Player ${playerId}`,
        honors: 0
      }
    }
    acc[playerId].honors += seasonsWon
    return acc
  }, {})).sort((a, b) => b.honors - a.honors).slice(0, 6)
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

  {#if !loading && team}
    <div class="page-meta">
      <span>{team.primary_league_name || '-'}</span>
      <span>League rank #{leaguePosition?.position || '-'}</span>
      <span>{squad.length} players</span>
      <span>{deepMatchCoverage} deep matches</span>
      <span>{scoutedProfiles} profiles</span>
    </div>
  {/if}

  {#if loading}
    <div class="loading">Loading...</div>
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
      <section class="panel-grid overview-grid">
        <article class="panel span-2">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Match Pulse</p>
              <h2>Next and Last Match</h2>
            </div>
          </div>
          <div class="match-grid">
            <div class="match-card">
              <span class="match-tag">Next</span>
              <h3>{nextMatch?.opponent || 'No upcoming match'}</h3>
              <p>{nextMatch?.tournament || '-'}</p>
              <strong>{formatDateTime(nextMatch?.utc_time)}</strong>
              <small>{nextMatch?.start_day || '-'}</small>
            </div>
            <div class="match-card">
              <span class="match-tag">Last</span>
              <h3>{lastMatch?.opponent || 'No recent match'}</h3>
              <p>{lastMatch?.tournament || '-'}</p>
              <strong>{lastMatch?.score_str || '-'}</strong>
              <small>{lastMatch?.reason_long || '-'}</small>
            </div>
          </div>
        </article>

        <article class="panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Venue</p>
              <h2>{venue?.stadium_name || team.stadium_name}</h2>
            </div>
          </div>
          <dl class="detail-list">
            <div><dt>City</dt><dd>{venue?.city || team.stadium_city || '-'}</dd></div>
            <div><dt>Surface</dt><dd>{venue?.surface || team.surface || '-'}</dd></div>
            <div><dt>Capacity</dt><dd>{venue?.capacity || team.capacity || '-'}</dd></div>
            <div><dt>Opened</dt><dd>{venue?.opened || team.opened || '-'}</dd></div>
          </dl>
        </article>

        <article class="panel span-2">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Team Shape</p>
              <h2>Recent Form</h2>
            </div>
          </div>
          <div class="form-strip">
            {#each teamForm as match}
              <div class="form-item result-{(match.result_string || '').toLowerCase()}">
                <strong>{match.result_string}</strong>
                <span>{match.opponent_name}</span>
                <small>{match.score}</small>
              </div>
            {/each}
          </div>
        </article>

        <article class="panel span-3">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Ranked Metrics</p>
              <h2>Best Team Stat Placings</h2>
            </div>
          </div>
          <div class="stat-bars">
            {#each bestTeamStats as stat}
              <div class="stat-bar-row">
                <div>
                  <strong>{stat.title}</strong>
                  <small>Rank #{stat.rank} · {stat.league_name}</small>
                </div>
                <div class="stat-bar">
                  <span style={barStyle(21 - Number(stat.rank || 20), 20)}></span>
                </div>
                <b>{stat.value}</b>
              </div>
            {/each}
          </div>
        </article>

        <article class="panel span-3">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Standouts</p>
              <h2>Top Players Snapshot</h2>
            </div>
          </div>
          <div class="player-chip-grid">
            {#each topPlayers as player}
              <div class="player-chip">
                <span>{player.group_label}</span>
                <strong>{player.player_name}</strong>
                <small>#{player.rank} · {player.value}</small>
              </div>
            {/each}
          </div>
        </article>

        <article class="panel span-3">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Deep Coverage</p>
              <h2>Recently Parsed Match Intelligence</h2>
            </div>
          </div>
          <div class="dataset-grid">
            {#each matchDetails.slice(-4).reverse() as match}
              <div class="dataset-card">
                <strong>{match.home_team_name} vs {match.away_team_name}</strong>
                <span>{match.status_score_str || '-'}</span>
                <small>{match.stadium_name || '-'} · {match.attendance || '-'} attendance</small>
              </div>
            {/each}
          </div>
        </article>
      </section>
    {:else if activeTab === 'team_performance'}
      <section class="panel-grid history-grid">
        <article class="panel span-2">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Timeline</p>
              <h2>Recent Historical Seasons</h2>
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

        <article class="panel span-2">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Archive Table</p>
              <h2>{latestHistoricalSeasonName || 'Latest parsed historical season'}</h2>
            </div>
          </div>
          <div class="history-table">
            <div class="history-row history-head standings-head">
              <span>Pos</span>
              <span>Club</span>
              <span>Pts</span>
              <span>Goal Diff</span>
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

        <article class="panel span-2">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Managers</p>
              <h2>Coach History</h2>
            </div>
          </div>
          <div class="coach-grid">
            {#each coachHistory.slice(0, 12) as coach}
              <div class="coach-card">
                <strong>{coach.coach_name}</strong>
                <span>{coach.season}</span>
                <small>{coach.league_name}</small>
                <b>{formatPercent(Number(coach.win_percentage || 0) * 100)}</b>
              </div>
            {/each}
          </div>
        </article>

        <article class="panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Qualification Keys</p>
              <h2>Historical Rules</h2>
            </div>
          </div>
          <div class="trophy-list">
            {#each latestHistoricalRules as rule}
              <div class="trophy-item">
                <strong>{rule.description}</strong>
                <small>{rule.key}</small>
                <span>{rule.value}</span>
              </div>
            {/each}
          </div>
        </article>

        <article class="panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Silverware</p>
              <h2>Trophy Cabinet</h2>
            </div>
          </div>
          <div class="trophy-list">
            {#each trophies.slice(0, 8) as trophy}
              <div class="trophy-item">
                <strong>{trophy.name}</strong>
                <small>{trophy.area}</small>
                <span>{trophy.won} won</span>
              </div>
            {/each}
          </div>
        </article>

        <article class="panel span-2">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Current Squad Honors</p>
              <h2>Most Decorated Profiles</h2>
            </div>
          </div>
          <div class="player-chip-grid">
            {#each decoratedPlayers as player}
              <div class="player-chip">
                <span>Career honors</span>
                <strong>{player.name}</strong>
                <small>{player.honors} recorded wins</small>
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
      <div style="display:flex; gap:1rem; flex-direction:column;">
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
        <Transfers data={data.transfers || []} />
      </div>
    {:else if activeTab === 'raw'}
      <section class="panel raw-panel">
        <div class="panel-header">
          <div>
            <p class="eyebrow">CSV Inventory</p>
            <h2>Exported Datasets</h2>
          </div>
        </div>
        <div class="dataset-grid">
          {#each rawDatasets as [name, rows]}
            <div class="dataset-card">
              <strong>{name}</strong>
              <span>{rows?.length || 0} rows</span>
              <small>CSV: /{name.replace(/[A-Z]/g, m => `_${m.toLowerCase()}`).replace(/^_/, '')}.csv</small>
            </div>
          {/each}
        </div>
      </section>
    {/if}
    </div>
  {/if}
</main>
