<script>
  import { formatMarketValue } from './csv.js'
  import { onPlayerImageError, playerImageUrl } from './playerImage.js'

  export let data = []
  export let lineup = []
  export let lineupPlayers = []
  export let playerProfiles = []
  export let playerCareerEntries = []
  export let playerMarketValues = []
  export let playerTrophies = []
  export let playerTraits = []
  export let playerRecentMatches = []

  let viewMode = 'list'
  let selectedPlayerId = null
  let comparePlayerId = null

  const positionOrder = ['keepers', 'defenders', 'midfielders', 'attackers', 'coaches']

  function toNumber(value) {
    const n = Number(value)
    return Number.isFinite(n) ? n : 0
  }

  function formatNumber(value, digits = 0) {
    const n = Number(value)
    if (!Number.isFinite(n)) return value || '-'
    return n.toLocaleString('en-US', {
      minimumFractionDigits: digits,
      maximumFractionDigits: digits
    })
  }

  function getRatingClass(rating) {
    const r = Number(rating)
    if (!Number.isFinite(r)) return ''
    if (r >= 7.5) return 'rating-great'
    if (r >= 7) return 'rating-good'
    if (r >= 6.5) return 'rating-ok'
    return 'rating-bad'
  }

  function formatHeight(height) {
    if (!height) return '-'
    return `${Math.round(Number(height))} cm`
  }

  function average(values) {
    const nums = values.map((value) => Number(value)).filter((value) => Number.isFinite(value) && value > 0)
    return nums.length ? nums.reduce((sum, value) => sum + value, 0) / nums.length : 0
  }

  function formatDate(value) {
    if (!value) return '-'
    const d = new Date(value)
    if (Number.isNaN(d.getTime())) return value
    return d.toISOString().slice(0, 10)
  }

  function parseJSON(value, fallback = null) {
    if (!value) return fallback
    try {
      return JSON.parse(value)
    } catch {
      return fallback
    }
  }

  function sortByDate(items, key) {
    return [...items].sort((a, b) => new Date(a[key] || 0).getTime() - new Date(b[key] || 0).getTime())
  }

  function compactNumber(value) {
    const n = Number(value)
    if (!Number.isFinite(n)) return value || '-'
    return new Intl.NumberFormat('en', { notation: 'compact', maximumFractionDigits: 1 }).format(n)
  }

  function chartPoint(index, total, value, max) {
    const left = total <= 1 ? 0 : (index / (total - 1)) * 100
    const top = max > 0 ? 100 - (toNumber(value) / max) * 100 : 100
    return `${left},${top}`
  }

  function getStatValue(stats, title) {
    const item = (stats || []).find((entry) => entry.title === title)
    return item?.value ?? null
  }

  function roleSummary(profile) {
    const stats = parseJSON(profile.main_league_stats, [])
    const position = String(profile.primary_position || '').toLowerCase()
    if (position.includes('keeper')) {
      return {
        label: 'Goalkeeping',
        primary: `${getStatValue(stats, 'Clean sheets') || 0} clean sheets`,
        secondary: `${getStatValue(stats, 'Goals conceded') || 0} conceded`
      }
    }
    if (position.includes('back') || position.includes('defender')) {
      return {
        label: 'Defending',
        primary: `${getStatValue(stats, 'Started') || 0} starts`,
        secondary: `${getStatValue(stats, 'Minutes played') || 0} minutes`
      }
    }
    if (position.includes('midfielder')) {
      return {
        label: 'Midfield',
        primary: `${getStatValue(stats, 'Assists') || 0} assists`,
        secondary: `${getStatValue(stats, 'Rating') || '-'} rating`
      }
    }
    return {
      label: 'Attack',
      primary: `${getStatValue(stats, 'Goals') || 0} goals`,
      secondary: `${getStatValue(stats, 'Assists') || 0} assists`
    }
  }

  $: grouped = (() => {
    const groups = {}
    ;(data || []).forEach((player) => {
      const group = player.position_group || 'other'
      if (!groups[group]) groups[group] = []
      groups[group].push(player)
    })
    return [...positionOrder.filter((group) => groups[group]), ...Object.keys(groups).filter((group) => !positionOrder.includes(group))]
      .map((group) => ({ name: group, players: groups[group] }))
  })()

  $: lineupInfo = lineup?.[0] || null
  $: starters = (lineupPlayers || []).filter((player) => player.section === 'starter')
  $: subs = (lineupPlayers || []).filter((player) => player.section === 'sub')
  $: unavailable = (lineupPlayers || []).filter((player) => player.section === 'unavailable')
  $: lineupMaxValue = Math.max(...starters.map((player) => toNumber(player.market_value)), 0)
  $: playerProfileCards = (playerProfiles || []).map((profile) => {
    const recent = (playerRecentMatches || []).filter((match) => match.player_id === profile.player_id).slice(0, 5)
    const marketPoints = (playerMarketValues || []).filter((point) => point.player_id === profile.player_id)
    const careers = (playerCareerEntries || []).filter((entry) => entry.player_id === profile.player_id && entry.entry_type === 'season_entry')
    const traits = (playerTraits || []).filter((item) => item.player_id === profile.player_id).sort((a, b) => Number(b.item_value || 0) - Number(a.item_value || 0))
    return {
      ...profile,
      avgRecentRating: average(recent.map((match) => match.rating)),
      latestMarketValue: marketPoints.length ? marketPoints[marketPoints.length - 1].value : profile.market_value,
      careerStops: new Set(careers.map((entry) => entry.team_name)).size,
      topTrait: traits[0]?.item_title || '-',
      roleSummary: roleSummary(profile)
    }
  })
  $: selectedPlayerId = selectedPlayerId || playerProfileCards[0]?.player_id || null
  $: comparePlayerId = comparePlayerId || playerProfileCards.find((player) => player.player_id !== selectedPlayerId)?.player_id || null
  $: selectedPlayer = playerProfileCards.find((player) => player.player_id === selectedPlayerId) || null
  $: comparePlayer = playerProfileCards.find((player) => player.player_id === comparePlayerId) || null
  $: selectedPlayerMatches = (playerRecentMatches || []).filter((match) => match.player_id === selectedPlayerId).slice(0, 8)
  $: selectedPlayerTraits = (playerTraits || []).filter((item) => item.player_id === selectedPlayerId).sort((a, b) => Number(b.item_value || 0) - Number(a.item_value || 0)).slice(0, 6)
  $: selectedPlayerTrophies = (playerCareerEntries || []).filter((entry) => entry.player_id === selectedPlayerId && entry.entry_type === 'tournament_stat').slice(0, 8)
  $: selectedMarketValues = sortByDate((playerMarketValues || []).filter((point) => point.player_id === selectedPlayerId), 'date')
  $: selectedMarketMax = Math.max(...selectedMarketValues.map((point) => toNumber(point.value)), 0)
  $: selectedHonorRows = (playerTrophies || []).filter((item) => item.player_id === selectedPlayerId)
  $: totalHonors = selectedHonorRows.reduce((sum, item) => sum + (parseJSON(item.seasons_won, [])?.length || 0), 0)
  $: recentRatingSeries = selectedPlayerMatches.slice().reverse()
  $: ratingMax = Math.max(...recentRatingSeries.map((match) => toNumber(match.rating)), 10)
  $: ratingPolyline = recentRatingSeries.map((match, index) => chartPoint(index, recentRatingSeries.length, match.rating, ratingMax)).join(' ')
  $: marketPolyline = selectedMarketValues.slice(-8).map((point, index, arr) => chartPoint(index, arr.length, point.value, selectedMarketMax)).join(' ')
  $: compareHonorRows = (playerTrophies || []).filter((item) => item.player_id === comparePlayerId)
  $: compareHonors = compareHonorRows.reduce((sum, item) => sum + (parseJSON(item.seasons_won, [])?.length || 0), 0)
</script>

<section class="squad-shell">
  <aside class="squad-sidebar panel">
    <div class="section-head">
      <div>
        <span class="eyebrow">Last lineup</span>
        <h2>{lineupInfo?.formation || 'No lineup data'}</h2>
      </div>
      <div class="lineup-meta">
        <span>{lineupInfo?.coach_name || '-'}</span>
        <span>XI {lineupInfo?.team_rating || '-'}</span>
      </div>
    </div>

    <div class="lineup-pitch sofascore-pitch">
      {#if starters.length === 0}
        <div class="empty">No lineup data available</div>
      {:else}
        {#each starters as player}
          <div
            class="starter-dot"
            style={`left:${Number(player.horizontal_y || 0) * 100}%; top:${Number(player.horizontal_x || 0) * 100}%;`}
          >
            <span>{player.shirt_number || '-'}</span>
            <strong>{player.last_name || player.name}</strong>
          </div>
        {/each}
      {/if}
    </div>

    <div class="bench-grid">
      <div>
        <h4>Bench</h4>
        {#if subs.length === 0}
          <p class="empty-small">No subs exported</p>
        {:else}
          {#each subs.slice(0, 10) as player}
            <div class="bench-row">
              <span>{player.shirt_number || '-'}</span>
              <strong>{player.name}</strong>
            </div>
          {/each}
        {/if}
      </div>
      <div>
        <h4>Unavailable</h4>
        {#if unavailable.length === 0}
          <p class="empty-small">No unavailable list</p>
        {:else}
          {#each unavailable.slice(0, 10) as player}
            <div class="bench-row muted-row">
              <span>{player.shirt_number || '-'}</span>
              <strong>{player.name}</strong>
            </div>
          {/each}
        {/if}
      </div>
    </div>

    {#if starters.length > 0}
      <div class="sidebar-section-block">
        <span class="eyebrow">Starter values</span>
        <div class="starter-values">
          {#each starters as player}
            <div class="starter-value-row">
              <span>{player.name}</span>
              <div class="value-bar">
                <i style={`width:${lineupMaxValue ? Math.max(8, (toNumber(player.market_value) / lineupMaxValue) * 100) : 0}%`}></i>
              </div>
              <strong>{formatMarketValue(player.market_value)}</strong>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  </aside>

  <section class="squad-content">
    <div class="panel squad-toolbar-panel">
      <div class="toolbar">
        <div>
          <span class="eyebrow">Roster</span>
          <h2>Players</h2>
        </div>
        <div class="view-toggle">
          <button class:active={viewMode === 'list'} on:click={() => (viewMode = 'list')}>List</button>
          <button class:active={viewMode === 'grid'} on:click={() => (viewMode = 'grid')}>Cards</button>
        </div>
      </div>

      {#if viewMode === 'list'}
        {#each grouped as group}
          <section class="group-section">
            <h4>{group.name}</h4>
            <div class="table-wrap sofascore-table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Player</th>
                    <th>Pos</th>
                    <th>Nat</th>
                    <th>Age</th>
                    <th>Ht</th>
                    <th>Rating</th>
                    <th>G</th>
                    <th>A</th>
                    <th>Value</th>
                  </tr>
                </thead>
                <tbody>
                  {#each group.players as player}
                    <tr>
                      <td>{player.shirt_number || '-'}</td>
                      <td class="name-cell">
                        <strong>{player.name}</strong>
                        <small>{player.first_name || ''} {player.last_name || ''}</small>
                      </td>
                      <td>{player.position || '-'}</td>
                      <td>{player.country_code || '-'}</td>
                      <td>{player.age || '-'}</td>
                      <td>{formatHeight(player.height)}</td>
                      <td class={getRatingClass(player.rating)}>{player.rating || '-'}</td>
                      <td>{formatNumber(player.goals || 0)}</td>
                      <td>{formatNumber(player.assists || 0)}</td>
                      <td>{formatMarketValue(player.market_value)}</td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
          </section>
        {/each}
      {:else}
        <div class="squad-card-grid">
          {#each data as player}
            <article class="player-card squad-player-card">
              <div class="player-card-head">
                <span class="shirt">{player.shirt_number || '-'}</span>
                <span>{formatMarketValue(player.market_value)}</span>
              </div>
              <h4>{player.name}</h4>
              <p>{player.position_group} · {player.position || '-'}</p>
              <div class="mini-grid">
                <span><b>{player.age || '-'}</b> age</span>
                <span><b>{player.country_code || '-'}</b></span>
                <span><b class={getRatingClass(player.rating)}>{player.rating || '-'}</b> rating</span>
                <span><b>{player.goals || 0}</b>g {player.assists || 0}a</span>
              </div>
            </article>
          {/each}
        </div>
      {/if}
    </div>

    <div class="panel squad-profile-selector-panel">
      <div class="section-head">
        <div>
          <span class="eyebrow">Profiles</span>
          <h2>Deep player cards</h2>
        </div>
      </div>
      <div class="profile-selection-grid">
        {#each playerProfileCards.slice(0, 12) as player}
          <button
            type="button"
            class="player-card selectable-card deep-profile-tile"
            class:selected-card={selectedPlayerId === player.player_id}
            on:click={() => (selectedPlayerId = player.player_id)}
          >
            <div class="player-card-head">
              <div class="player-headshot-wrap">
                <img class="player-headshot" src={playerImageUrl(player)} alt={player.name} on:error={onPlayerImageError} />
                <span class="overlay-shirt">{player.shirt_number || '-'}</span>
              </div>
              <span>{formatMarketValue(player.latestMarketValue)}</span>
            </div>
            <h4>{player.name}</h4>
            <p>{player.primary_position || player.position || '-'} · {player.country_code || '-'}</p>
            <div class="mini-grid">
              <span><b>{player.avgRecentRating ? player.avgRecentRating.toFixed(2) : '-'}</b> rating</span>
              <span><b>{player.careerStops}</b> clubs</span>
            </div>
          </button>
        {/each}
      </div>
    </div>

    {#if selectedPlayer}
      <div class="panel player-drilldown-shell">
        <div class="panel-header">
          <div>
            <span class="eyebrow">Player drilldown</span>
            <h2>{selectedPlayer.name}</h2>
          </div>
          <div class="lineup-meta">
            <span>{selectedPlayer.primary_position || '-'}</span>
            <span>{selectedPlayer.country_code || '-'}</span>
          </div>
        </div>

        <div class="compare-toolbar">
          <span class="metric-label">Compare with</span>
          <select bind:value={comparePlayerId}>
            {#each playerProfileCards.filter((player) => player.player_id !== selectedPlayerId) as player}
              <option value={player.player_id}>{player.name}</option>
            {/each}
          </select>
        </div>

        <div class="summary-grid drill-summary-grid">
          <article class="metric-card compact-metric">
            <span class="metric-label">Market value</span>
            <strong>{formatMarketValue(selectedPlayer.latestMarketValue)}</strong>
            <small>{selectedPlayer.contract_end_utc ? selectedPlayer.contract_end_utc.slice(0, 10) : 'Contract unknown'}</small>
          </article>
          <article class="metric-card compact-metric">
            <span class="metric-label">Avg rating</span>
            <strong>{selectedPlayer.avgRecentRating ? selectedPlayer.avgRecentRating.toFixed(2) : '-'}</strong>
            <small>recent matches</small>
          </article>
          <article class="metric-card compact-metric">
            <span class="metric-label">Honors</span>
            <strong>{totalHonors}</strong>
            <small>{selectedHonorRows.length} competition rows</small>
          </article>
          <article class="metric-card compact-metric">
            <span class="metric-label">Top trait</span>
            <strong>{selectedPlayer.topTrait}</strong>
            <small>{selectedPlayer.roleSummary.label}</small>
          </article>
        </div>

        {#if comparePlayer}
          <div class="comparison-box compact-box compare-box">
            <span>Comparison</span>
            <div class="compare-grid">
              <div class="compare-card">
                <strong>{selectedPlayer.name}</strong>
                <small>{selectedPlayer.primary_position || '-'}</small>
                <div class="mini-stat-row"><strong>Value</strong><small>{formatMarketValue(selectedPlayer.latestMarketValue)}</small></div>
                <div class="mini-stat-row"><strong>Avg rating</strong><small>{selectedPlayer.avgRecentRating ? selectedPlayer.avgRecentRating.toFixed(2) : '-'}</small></div>
                <div class="mini-stat-row"><strong>Honors</strong><small>{totalHonors}</small></div>
                <div class="mini-stat-row"><strong>Role focus</strong><small>{selectedPlayer.roleSummary.primary}</small></div>
              </div>
              <div class="compare-card">
                <strong>{comparePlayer.name}</strong>
                <small>{comparePlayer.primary_position || '-'}</small>
                <div class="mini-stat-row"><strong>Value</strong><small>{formatMarketValue(comparePlayer.latestMarketValue)}</small></div>
                <div class="mini-stat-row"><strong>Avg rating</strong><small>{comparePlayer.avgRecentRating ? comparePlayer.avgRecentRating.toFixed(2) : '-'}</small></div>
                <div class="mini-stat-row"><strong>Honors</strong><small>{compareHonors}</small></div>
                <div class="mini-stat-row"><strong>Role focus</strong><small>{comparePlayer.roleSummary.primary}</small></div>
              </div>
            </div>
          </div>
        {/if}

        <div class="detail-section-grid">
          <div class="comparison-box compact-box">
            <span>Recent matches</span>
            {#if selectedPlayerMatches.length === 0}
              <p class="empty-small">No recent matches exported</p>
            {:else}
              {#each selectedPlayerMatches as match}
                <div class="mini-stat-row">
                  <strong>{match.opponent_team_name}</strong>
                  <small>{formatDate(match.match_date)} · {match.rating || '-'} rating</small>
                </div>
              {/each}
            {/if}
            {#if recentRatingSeries.length > 1}
              <div class="mini-chart-wrap">
                <svg viewBox="0 0 100 100" class="mini-line-chart" preserveAspectRatio="none">
                  <polyline points={ratingPolyline} />
                </svg>
              </div>
            {/if}
          </div>

          <div class="comparison-box compact-box">
            <span>Market value timeline</span>
            {#if selectedMarketValues.length === 0}
              <p class="empty-small">No market value history</p>
            {:else}
              {#each selectedMarketValues.slice(-6) as point}
                <div class="starter-value-row">
                  <span>{formatDate(point.date)}</span>
                  <div class="value-bar">
                    <i style={`width:${selectedMarketMax ? Math.max(8, (toNumber(point.value) / selectedMarketMax) * 100) : 0}%`}></i>
                  </div>
                  <strong>{formatMarketValue(point.value)}</strong>
                </div>
              {/each}
            {/if}
            {#if selectedMarketValues.length > 1}
              <div class="mini-chart-wrap">
                <svg viewBox="0 0 100 100" class="mini-line-chart" preserveAspectRatio="none">
                  <polyline points={marketPolyline} />
                </svg>
              </div>
            {/if}
          </div>

          <div class="comparison-box compact-box">
            <span>Top traits</span>
            {#if selectedPlayerTraits.length === 0}
              <p class="empty-small">No traits exported</p>
            {:else}
              {#each selectedPlayerTraits as trait}
                <div class="mini-stat-row">
                  <strong>{trait.item_title}</strong>
                  <small>{Number(trait.item_value || 0).toFixed(2)}</small>
                </div>
              {/each}
            {/if}
          </div>

          <div class="comparison-box compact-box">
            <span>Honors & competitions</span>
            {#if selectedHonorRows.length === 0 && selectedPlayerTrophies.length === 0}
              <p class="empty-small">No honors or competition history rows</p>
            {:else}
              {#each selectedHonorRows.slice(0, 4) as honor}
                <div class="mini-stat-row">
                  <strong>{honor.league_name || '-'}</strong>
                  <small>{compactNumber(parseJSON(honor.seasons_won, [])?.length || 0)} wins</small>
                </div>
              {/each}
              {#each selectedPlayerTrophies as entry}
                <div class="mini-stat-row">
                  <strong>{entry.league_name || '-'}</strong>
                  <small>{entry.season_name || '-'} · {entry.appearances || 0} apps</small>
                </div>
              {/each}
            {/if}
          </div>
        </div>
      </div>
    {/if}
  </section>
</section>
