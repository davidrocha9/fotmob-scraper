<script>
  export let data = []
  export let teamForm = []
  export let matchHighlights = []
  export let matchDetails = []
  export let matchEvents = []
  export let matchStats = []
  export let matchShots = []
  export let matchLineupPlayers = []
  export let matchPlayerStats = []

  let filter = 'all'
  let selectedFixture = null
  let eventTypeFilter = 'all'
  let shotTeamFilter = 'all'
  let activeSubtab = 'summary'

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

  function toBool(value) {
    return String(value).toLowerCase() === 'true'
  }

  function toNumber(value) {
    const n = Number(value)
    return Number.isFinite(n) ? n : 0
  }

  function timestamp(value) {
    if (!value) return 0
    const t = new Date(value).getTime()
    return Number.isFinite(t) ? t : 0
  }

  function fixtureState(fixture) {
    if (toBool(fixture.not_started) || (!toBool(fixture.status_finished) && !toBool(fixture.status_started))) return 'upcoming'
    if (toBool(fixture.status_finished)) return 'played'
    return 'live'
  }

  function summaryText(fixture) {
    const summary = parseJSON(fixture.stats_summary, [])
    if (!Array.isArray(summary) || summary.length === 0) return null
    return summary.slice(0, 2).map((item) => `${item.title}: ${Array.isArray(item.stats) ? item.stats.join(' - ') : ''}`).join(' | ')
  }

  function eventMinute(event) {
    return `${event.time_str || event.time || 0}${event.overload_time ? `+${event.overload_time}` : ''}`
  }

  $: fixtures = (data || [])
    .map((fixture) => ({
      ...fixture,
      state: fixtureState(fixture),
      kickoffLabel: formatDateTime(fixture.utc_time),
      isHome: String(fixture.team_is_home).toLowerCase() === 'true',
      detailSummary: summaryText(fixture)
    }))
    .sort((a, b) => timestamp(b.utc_time) - timestamp(a.utc_time))

  $: visibleFixtures = filter === 'all' ? fixtures : fixtures.filter((fixture) => fixture.state === filter)
  $: nextMatch = matchHighlights?.find((match) => match.match_type === 'next') || null
  $: lastMatch = matchHighlights?.find((match) => match.match_type === 'last') || null
  $: selectedFixture = selectedFixture || visibleFixtures[0] || null
  $: selectedDetail = selectedFixture ? matchDetails.find((detail) => String(detail.fixture_id) === String(selectedFixture.id)) : null
  $: selectedEvents = selectedFixture ? matchEvents.filter((event) => String(event.fixture_id) === String(selectedFixture.id)).slice(0, 16) : []
  $: selectedStats = selectedFixture ? matchStats.filter((stat) => String(stat.fixture_id) === String(selectedFixture.id) && stat.period === 'All').slice(0, 10) : []
  $: selectedShots = selectedFixture ? matchShots.filter((shot) => String(shot.fixture_id) === String(selectedFixture.id)) : []
  $: selectedLineup = selectedFixture ? matchLineupPlayers.filter((player) => String(player.fixture_id) === String(selectedFixture.id)) : []
  $: selectedPlayerStats = selectedFixture ? matchPlayerStats.filter((stat) => String(stat.fixture_id) === String(selectedFixture.id)) : []
  $: homeLineupCount = selectedLineup.filter((player) => player.section === 'starter').length
  $: benchLineupCount = selectedLineup.filter((player) => player.section === 'sub').length
  $: availableEventTypes = ['all', ...new Set(selectedEvents.map((event) => event.type).filter(Boolean))]
  $: filteredEvents = eventTypeFilter === 'all' ? selectedEvents : selectedEvents.filter((event) => event.type === eventTypeFilter)
  $: filteredShots = shotTeamFilter === 'all'
    ? selectedShots
    : selectedShots.filter((shot) => shotTeamFilter === 'home'
      ? String(shot.team_id) === String(selectedFixture?.home_team_id)
      : String(shot.team_id) === String(selectedFixture?.away_team_id))
  $: homeShots = selectedShots.filter((shot) => String(shot.team_id) === String(selectedFixture?.home_team_id))
  $: awayShots = selectedShots.filter((shot) => String(shot.team_id) === String(selectedFixture?.away_team_id))
  $: homeXg = homeShots.reduce((sum, shot) => sum + toNumber(shot.expected_goals), 0)
  $: awayXg = awayShots.reduce((sum, shot) => sum + toNumber(shot.expected_goals), 0)
  $: selectedRatings = Object.values(selectedPlayerStats.reduce((acc, stat) => {
    if (stat.stat_title !== 'FotMob rating') return acc
    const key = stat.player_id || stat.player_name
    if (!acc[key]) {
      acc[key] = { player_name: stat.player_name, rating: stat.stat_value, team_name: stat.team_name }
    }
    return acc
  }, {})).sort((a, b) => Number(b.rating || 0) - Number(a.rating || 0)).slice(0, 6)
  $: selectedTopShotTakers = Object.values(selectedShots.reduce((acc, shot) => {
    const key = shot.player_id || shot.player_name
    if (!key) return acc
    if (!acc[key]) acc[key] = { player_name: shot.player_name, shots: 0, xg: 0 }
    acc[key].shots += 1
    acc[key].xg += toNumber(shot.expected_goals)
    return acc
  }, {})).sort((a, b) => b.shots - a.shots).slice(0, 5)

  $: shotMapBounds = {
    minX: Math.min(...selectedShots.map((shot) => toNumber(shot.x)), 0),
    maxX: Math.max(...selectedShots.map((shot) => toNumber(shot.x)), 105),
    minY: Math.min(...selectedShots.map((shot) => toNumber(shot.y)), 0),
    maxY: Math.max(...selectedShots.map((shot) => toNumber(shot.y)), 68)
  }

  function shotLeft(shot) {
    const span = shotMapBounds.maxX - shotMapBounds.minX || 105
    return `${((toNumber(shot.x) - shotMapBounds.minX) / span) * 100}%`
  }

  function shotTop(shot) {
    const span = shotMapBounds.maxY - shotMapBounds.minY || 68
    return `${((toNumber(shot.y) - shotMapBounds.minY) / span) * 100}%`
  }

  function shotSize(shot) {
    return `${12 + Math.min(24, toNumber(shot.expected_goals) * 40)}px`
  }
</script>

<section class="matches-shell">
  <aside class="matches-sidebar panel">
    <div class="matches-sidebar-head">
      <div>
        <span class="eyebrow">Fixtures</span>
        <h2>Match center</h2>
      </div>
      <div class="filter-row">
        <button class:active={filter === 'all'} on:click={() => (filter = 'all')}>All</button>
        <button class:active={filter === 'played'} on:click={() => (filter = 'played')}>Played</button>
        <button class:active={filter === 'upcoming'} on:click={() => (filter = 'upcoming')}>Upcoming</button>
        <button class:active={filter === 'live'} on:click={() => (filter = 'live')}>Live</button>
      </div>
    </div>

    <div class="compact-match-promo">
      <div class="compact-match-promo-card">
        <span>Next</span>
        <strong>{nextMatch?.opponent || '-'}</strong>
        <small>{nextMatch?.tournament || '-'}</small>
      </div>
      <div class="compact-match-promo-card">
        <span>Last</span>
        <strong>{lastMatch?.score_str || '-'}</strong>
        <small>{lastMatch?.opponent || '-'}</small>
      </div>
    </div>

    <div class="fixture-list sofascore-list">
      {#each visibleFixtures as fixture}
        <button
          class="sofascore-match-row"
          class:selected-card={selectedFixture?.id === fixture.id}
          on:click={() => {
            selectedFixture = fixture
            activeSubtab = 'summary'
          }}
        >
          <div class="sofascore-match-row-top">
            <span class={`state ${fixture.state}`}>{fixture.state}</span>
            <small>{fixture.kickoffLabel}</small>
          </div>
          <div class="sofascore-match-row-main">
            <div class="sofascore-match-teams">
              <strong>{fixture.home_team_name || teamForm?.[0]?.team_name || 'Home'}</strong>
              <strong>{fixture.away_team_name || fixture.opponent || 'Away'}</strong>
            </div>
            <div class="sofascore-match-score">
              <b>{fixture.home_team_score ?? '-'}</b>
              <b>{fixture.away_team_score ?? '-'}</b>
            </div>
          </div>
          <div class="sofascore-match-row-bottom">
            <span>{fixture.tournament || '-'}</span>
            <span>{fixture.round || fixture.tournament_stage || '-'}</span>
          </div>
        </button>
      {/each}
    </div>
  </aside>

  <section class="matches-main">
    {#if selectedFixture}
      <article class="panel match-scoreboard-card">
        <div class="match-scoreboard-meta">
          <span>{selectedFixture.tournament || '-'}</span>
          <span>{selectedFixture.round || selectedFixture.tournament_stage || '-'}</span>
          <span>{selectedFixture.kickoffLabel}</span>
        </div>
        <div class="match-scoreboard-main">
          <div class="scoreboard-team-block">
            <strong>{selectedFixture.home_team_name || 'Home'}</strong>
            <small>Home</small>
          </div>
          <div class="scoreboard-score-block">
            <span class={`state ${selectedFixture.state}`}>{selectedFixture.status_reason_long || selectedFixture.state}</span>
            <div class="scoreboard-scoreline">
              <b>{selectedFixture.home_team_score ?? '-'}</b>
              <span>:</span>
              <b>{selectedFixture.away_team_score ?? '-'}</b>
            </div>
            <small>{selectedFixture.result || selectedFixture.score_str || '-'}</small>
          </div>
          <div class="scoreboard-team-block is-away">
            <strong>{selectedFixture.away_team_name || selectedFixture.opponent || 'Away'}</strong>
            <small>Away</small>
          </div>
        </div>
      </article>

      <div class="match-subtabs panel">
        <button class:active={activeSubtab === 'summary'} on:click={() => (activeSubtab = 'summary')}>Summary</button>
        <button class:active={activeSubtab === 'stats'} on:click={() => (activeSubtab = 'stats')}>Stats</button>
        <button class:active={activeSubtab === 'timeline'} on:click={() => (activeSubtab = 'timeline')}>Timeline</button>
        <button class:active={activeSubtab === 'lineups'} on:click={() => (activeSubtab = 'lineups')}>Lineups</button>
      </div>

      {#if activeSubtab === 'summary'}
        <div class="match-tab-grid">
          <article class="panel">
            <div class="section-head">
              <div>
                <span class="eyebrow">Overview</span>
                <h3>Match facts</h3>
              </div>
            </div>
            <div class="info-card-grid">
              <div class="info-card">
                <span>Competition</span>
                <strong>{selectedFixture.tournament || '-'}</strong>
              </div>
              <div class="info-card">
                <span>Kickoff</span>
                <strong>{selectedFixture.kickoffLabel}</strong>
              </div>
              <div class="info-card">
                <span>Attendance</span>
                <strong>{selectedDetail?.attendance || '-'}</strong>
              </div>
              <div class="info-card">
                <span>Referee</span>
                <strong>{selectedDetail?.referee_name || '-'}</strong>
              </div>
            </div>
            {#if selectedFixture.detailSummary}
              <div class="analyst-note-box">
                <span>Prematch note</span>
                <p>{selectedFixture.detailSummary}</p>
              </div>
            {/if}
          </article>

          <article class="panel">
            <div class="section-head">
              <div>
                <span class="eyebrow">Shot profile</span>
                <h3>xG & volume</h3>
              </div>
            </div>
            <div class="summary-compare-grid">
              <div class="summary-compare-card">
                <span>{selectedFixture.home_team_name || 'Home'}</span>
                <strong>{homeShots.length}</strong>
                <small>{homeXg.toFixed(2)} xG</small>
              </div>
              <div class="summary-compare-card">
                <span>{selectedFixture.away_team_name || 'Away'}</span>
                <strong>{awayShots.length}</strong>
                <small>{awayXg.toFixed(2)} xG</small>
              </div>
            </div>
            <div class="mini-stat-list">
              {#each selectedTopShotTakers as player}
                <div class="mini-stat-row">
                  <strong>{player.player_name}</strong>
                  <small>{player.shots} shots · xG {player.xg.toFixed(2)}</small>
                </div>
              {/each}
            </div>
          </article>

          <article class="panel span-2">
            <div class="section-head">
              <div>
                <span class="eyebrow">Ratings</span>
                <h3>Top players</h3>
              </div>
            </div>
            <div class="rank-metric-grid ratings-grid">
              {#each selectedRatings as player}
                <div class="rank-metric-card player-rating-card">
                  <span>{player.team_name}</span>
                  <strong>{player.rating}</strong>
                  <b>{player.player_name}</b>
                </div>
              {/each}
            </div>
          </article>
        </div>
      {:else if activeSubtab === 'stats'}
        <div class="match-tab-grid">
          <article class="panel span-2">
            <div class="section-head">
              <div>
                <span class="eyebrow">Stats</span>
                <h3>Team comparison</h3>
              </div>
            </div>
            <div class="stats-comparison-list">
              {#each selectedStats as stat}
                <div class="stats-comparison-row">
                  <b>{stat.home_value}</b>
                  <span>{stat.stat_title}</span>
                  <b>{stat.away_value}</b>
                </div>
              {/each}
            </div>
          </article>

          <article class="panel shot-box">
            <div class="section-head">
              <div>
                <span class="eyebrow">Shot map</span>
                <h3>Location view</h3>
              </div>
              <div class="filter-row">
                <button class:active={shotTeamFilter === 'all'} on:click={() => (shotTeamFilter = 'all')}>Both</button>
                <button class:active={shotTeamFilter === 'home'} on:click={() => (shotTeamFilter = 'home')}>Home</button>
                <button class:active={shotTeamFilter === 'away'} on:click={() => (shotTeamFilter = 'away')}>Away</button>
              </div>
            </div>
            <div class="shot-pitch">
              {#each filteredShots.slice(0, 36) as shot}
                <span
                  class={`shot-dot ${String(shot.team_id) === String(selectedFixture.home_team_id) ? 'home-shot' : 'away-shot'}`}
                  style={`left:${shotLeft(shot)}; top:${shotTop(shot)}; width:${shotSize(shot)}; height:${shotSize(shot)};`}
                  title={`${shot.player_name} · xG ${toNumber(shot.expected_goals).toFixed(2)}`}
                ></span>
              {/each}
            </div>
          </article>
        </div>
      {:else if activeSubtab === 'timeline'}
        <div class="match-tab-grid">
          <article class="panel span-2">
            <div class="section-head">
              <div>
                <span class="eyebrow">Timeline</span>
                <h3>Key events</h3>
              </div>
              <div class="filter-row">
                {#each availableEventTypes.slice(0, 6) as eventType}
                  <button class:active={eventTypeFilter === eventType} on:click={() => (eventTypeFilter = eventType)}>{eventType}</button>
                {/each}
              </div>
            </div>
            <div class="event-feed-list">
              {#each filteredEvents as event}
                <div class="event-feed-row">
                  <span>{eventMinute(event)}'</span>
                  <div>
                    <strong>{event.type}</strong>
                    <small>{event.player_name || event.team_side || '-'}</small>
                  </div>
                </div>
              {/each}
            </div>
          </article>
        </div>
      {:else if activeSubtab === 'lineups'}
        <div class="match-tab-grid">
          <article class="panel">
            <div class="section-head">
              <div>
                <span class="eyebrow">Lineups</span>
                <h3>Coverage</h3>
              </div>
            </div>
            <div class="info-card-grid">
              <div class="info-card">
                <span>Starters</span>
                <strong>{homeLineupCount}</strong>
              </div>
              <div class="info-card">
                <span>Bench</span>
                <strong>{benchLineupCount}</strong>
              </div>
              <div class="info-card">
                <span>Total rows</span>
                <strong>{selectedLineup.length}</strong>
              </div>
            </div>
          </article>
        </div>
      {/if}
    {/if}
  </section>
</section>
