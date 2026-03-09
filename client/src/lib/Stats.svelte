<script>
  import { onPlayerImageError, playerImageUrl } from './playerImage.js'

  export let data = []
  export let playerRankings = []
  export let teamRankings = []
  export let topPlayers = []
  export let playerProfiles = []
  export let playerRecentMatches = []
  export let playerMarketValues = []
  export let playerTraits = []

  let activePanel = 'leaderboards'

  function groupBy(items, keyGetter) {
    return (items || []).reduce((groups, item) => {
      const key = keyGetter(item)
      if (!groups[key]) groups[key] = []
      groups[key].push(item)
      return groups
    }, {})
  }

  function formatNumber(value, digits = 0) {
    const n = Number(value)
    if (!Number.isFinite(n)) return value || '-'
    return n.toLocaleString('en-US', {
      minimumFractionDigits: digits,
      maximumFractionDigits: digits
    })
  }

  function formatPercent(value, digits = 1) {
    const n = Number(value)
    if (!Number.isFinite(n)) return value || '-'
    return `${n.toFixed(digits)}%`
  }

  function formatValue(value, format) {
    if (value === undefined || value === null || value === '') return '-'
    const n = Number(value)
    if (Number.isNaN(n)) return value
    if (format === 'fraction') return n.toFixed(n % 1 === 0 ? 0 : 2)
    if (format === 'percent') return formatPercent(n, 1)
    return formatNumber(n, n % 1 === 0 ? 0 : 1)
  }

  function sortByRank(list) {
    return [...list].sort((a, b) => Number(a.rank || 9999) - Number(b.rank || 9999))
  }

  function timestamp(value) {
    if (!value) return 0
    const t = new Date(value).getTime()
    return Number.isFinite(t) ? t : 0
  }

  $: groupedTopThree = Object.entries(groupBy(data || [], (item) => item.category || 'other')).map(([name, items]) => ({
    id: name,
    label: items[0]?.category_display || name,
    players: sortByRank(items)
  }))

  $: groupedFullRankings = Object.entries(groupBy(playerRankings || [], (item) => item.category || 'other')).map(([name, items]) => ({
    id: name,
    label: items[0]?.title || items[0]?.category_display || name,
    subtitle: items[0]?.subtitle || '',
    players: sortByRank(items).slice(0, 12)
  }))

  $: sortedTeamRankings = sortByRank(teamRankings || []).slice(0, 8)
  $: groupedTopPlayers = Object.entries(groupBy(topPlayers || [], (item) => item.group_label || 'Other'))
  $: trendingValues = Object.values(groupBy(playerMarketValues || [], (item) => item.player_id)).map((items) => {
    const ordered = [...items].sort((a, b) => timestamp(a.date) - timestamp(b.date))
    const first = ordered[0]
    const last = ordered[ordered.length - 1]
    const profile = (playerProfiles || []).find((player) => player.player_id === first?.player_id)
    return {
      player_id: first?.player_id,
      name: profile?.name || `Player ${first?.player_id}`,
      first: Number(first?.value || 0),
      last: Number(last?.value || 0),
      change: Number(last?.value || 0) - Number(first?.value || 0)
    }
  }).sort((a, b) => b.change - a.change).slice(0, 8)

  $: formPlayers = Object.values(groupBy(playerRecentMatches || [], (item) => item.player_id)).map((items) => {
    const ratings = items.map((item) => Number(item.rating || 0)).filter((value) => Number.isFinite(value) && value > 0)
    const avg = ratings.length ? ratings.reduce((sum, value) => sum + value, 0) / ratings.length : 0
    const profile = (playerProfiles || []).find((player) => player.player_id === items[0]?.player_id)
    return {
      player_id: items[0]?.player_id,
      name: profile?.name || `Player ${items[0]?.player_id}`,
      matches: ratings.length,
      average: avg
    }
  }).sort((a, b) => b.average - a.average).slice(0, 8)

  $: traitLeaders = (playerTraits || []).sort((a, b) => Number(b.item_value || 0) - Number(a.item_value || 0)).slice(0, 10)
</script>

<section class="stats-shell">
  <aside class="stats-sidebar panel">
    <div class="section-head">
      <div>
        <span class="eyebrow">Player stats</span>
        <h2>Explorer</h2>
      </div>
    </div>

    <div class="stats-sidebar-tabs">
      <button class:active={activePanel === 'leaderboards'} on:click={() => (activePanel = 'leaderboards')}>Leaderboards</button>
      <button class:active={activePanel === 'overview'} on:click={() => (activePanel = 'overview')}>Overview</button>
      <button class:active={activePanel === 'traits'} on:click={() => (activePanel = 'traits')}>Traits</button>
    </div>

    <article class="sidebar-section-block">
      <span class="eyebrow">Team level</span>
      <div class="mini-stat-list">
        {#each sortedTeamRankings as stat}
          <div class="team-stat-row compact-team-row">
            <div>
              <strong>{stat.title}</strong>
              <small>Rank #{stat.rank}</small>
            </div>
            <b>{formatValue(stat.value, stat.stat_format)}</b>
          </div>
        {/each}
      </div>
    </article>

    <article class="sidebar-section-block">
      <span class="eyebrow">Fast view</span>
      {#each groupedTopPlayers as [label, items]}
        <div class="top-player-group">
          <h4>{label}</h4>
          {#each items as player}
            <div class="team-stat-row compact-team-row">
              <div>
                <strong>{player.player_name}</strong>
                <small>#{player.rank}</small>
              </div>
              <b>{player.value}</b>
            </div>
          {/each}
        </div>
      {/each}
    </article>
  </aside>

  <section class="stats-content">
    {#if activePanel === 'leaderboards'}
      <div class="stats-board-grid">
        {#each groupedFullRankings as group}
          <article class="panel stats-board-card">
            <div class="card-head">
              <div>
                <h3>{group.label}</h3>
                <small>{group.subtitle || 'Top squad rows'}</small>
              </div>
            </div>
            <div class="ranking-list">
              {#each group.players as player}
                <div class="sofascore-player-row">
                  <span class="rank">#{player.rank}</span>
                  <img class="inline-player-photo" src={playerImageUrl(player)} alt={player.player_name} on:error={onPlayerImageError} />
                  <div class="player-block">
                    <strong>{player.player_name}</strong>
                    <small>{player.player_country} · {player.minutes_played} mins</small>
                  </div>
                  <b>{formatValue(player.value, player.stat_format)}</b>
                </div>
              {/each}
            </div>
          </article>
        {/each}
      </div>
    {:else if activePanel === 'overview'}
      <div class="stats-overview-grid">
        <article class="panel">
          <div class="section-head">
            <div>
              <span class="eyebrow">Top 3 export</span>
              <h3>Category snapshots</h3>
            </div>
          </div>
          <div class="stats-board-grid compact-grid">
            {#each groupedTopThree as group}
              <div class="ranking-card compact-stat-card">
                <h4>{group.label}</h4>
                <div class="ranking-list">
                  {#each group.players as player}
                    <div class="sofascore-player-row">
                      <span class="rank">#{player.rank}</span>
                      <div class="player-block">
                        <strong>{player.player_name}</strong>
                        <small>{player.player_country}</small>
                      </div>
                      <b>{formatValue(player.value, player.format)}</b>
                    </div>
                  {/each}
                </div>
              </div>
            {/each}
          </div>
        </article>

        <article class="panel">
          <div class="section-head">
            <div>
              <span class="eyebrow">Form</span>
              <h3>Best recent average ratings</h3>
            </div>
          </div>
          <div class="ranking-list">
            {#each formPlayers as player}
              <div class="sofascore-player-row">
                <span class="rank">{player.matches}</span>
                <div class="player-block">
                  <strong>{player.name}</strong>
                  <small>{player.matches} rated matches</small>
                </div>
                <b>{player.average.toFixed(2)}</b>
              </div>
            {/each}
          </div>
        </article>

        <article class="panel">
          <div class="section-head">
            <div>
              <span class="eyebrow">Value trend</span>
              <h3>Market value growth</h3>
            </div>
          </div>
          <div class="ranking-list">
            {#each trendingValues as player}
              <div class="sofascore-player-row">
                <span class="rank">+</span>
                <div class="player-block">
                  <strong>{player.name}</strong>
                  <small>{formatNumber(player.first)} -> {formatNumber(player.last)}</small>
                </div>
                <b class="positive-metric">{formatNumber(player.change)}</b>
              </div>
            {/each}
          </div>
        </article>
      </div>
    {:else if activePanel === 'traits'}
      <div class="stats-overview-grid">
        <article class="panel span-2">
          <div class="section-head">
            <div>
              <span class="eyebrow">Traits</span>
              <h3>Top trait scores</h3>
            </div>
          </div>
          <div class="ranking-list">
            {#each traitLeaders as trait}
              <div class="sofascore-player-row">
                <span class="rank">{Number(trait.item_value).toFixed(2)}</span>
                <div class="player-block">
                  <strong>{trait.item_title}</strong>
                  <small>{trait.traits_title}</small>
                </div>
                <b>{trait.player_id}</b>
              </div>
            {/each}
          </div>
        </article>
      </div>
    {/if}
  </section>
</section>
