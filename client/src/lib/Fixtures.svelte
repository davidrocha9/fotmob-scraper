<script>
  export let data = []

  let hideUpcoming = false
  let selectedFixture = null

  function parseJson(str) {
    if (!str) return null
    try {
      const normalized = str
        .replace(/'/g, '"')
        .replace(/\bTrue\b/g, 'true')
        .replace(/\bFalse\b/g, 'false')
        .replace(/\bNone\b/g, 'null')
      return JSON.parse(normalized)
    } catch {
      return null
    }
  }

  function pad(value) {
    return String(value).padStart(2, '0')
  }

  function formatDate(date) {
    if (!date) return '-'
    return `${date.getUTCFullYear()}-${pad(date.getUTCMonth() + 1)}-${pad(date.getUTCDate())}`
  }

  function formatTime(date) {
    if (!date) return '--:--'
    return `${pad(date.getUTCHours())}:${pad(date.getUTCMinutes())}`
  }

  function parseScore(scoreStr) {
    if (!scoreStr) return null
    const match = scoreStr.match(/(\d+)\s*-\s*(\d+)/)
    if (!match) return null
    return { home: Number(match[1]), away: Number(match[2]) }
  }

  function getSeasonLabel(date) {
    if (!date) return ''
    const year = date.getUTCFullYear()
    const month = date.getUTCMonth() + 1
    const seasonStart = month >= 7 ? year : year - 1
    return `${String(seasonStart).slice(-2)}/${pad((seasonStart + 1) % 100)}`
  }

  function getCompetitionLabel(fixture, kickoffDate) {
    const displayTournament = fixture.display_tournament
    const tournament = fixture.tournament
    const displayAsText = (
      displayTournament !== undefined &&
      displayTournament !== null &&
      displayTournament !== '' &&
      String(displayTournament).toLowerCase() !== 'true' &&
      String(displayTournament).toLowerCase() !== 'false'
    )
      ? String(displayTournament)
      : ''

    const baseCompetition = tournament || displayAsText || 'Other'
    const seasonLabel = getSeasonLabel(kickoffDate)
    return seasonLabel ? `${baseCompetition} ${seasonLabel}` : baseCompetition
  }

  function formatRound(roundValue) {
    if (roundValue === undefined || roundValue === null || roundValue === '') return '-'
    const raw = String(roundValue).trim()
    if (!raw) return '-'
    if (/^j\d+$/i.test(raw)) return `J${raw.slice(1)}`
    if (/^\d+$/.test(raw)) return `J${raw}`
    return raw
  }

  function isUpcomingFixture(fixture, status, kickoffDate) {
    if (fixture.not_started === 'True') return true
    if (status?.started === false) return true
    if (!status?.finished && kickoffDate && kickoffDate.getTime() > Date.now()) return true
    return false
  }

  function openFixtureDetails(fixture) {
    selectedFixture = fixture
  }

  function closeFixtureDetails() {
    selectedFixture = null
  }

  function onFixtureKeydown(event, fixture) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      openFixtureDetails(fixture)
    }
  }

  function onGlobalKeydown(event) {
    if (event.key === 'Escape' && selectedFixture) {
      closeFixtureDetails()
    }
  }

  $: fixtures = (data || [])
    .map(fixture => {
      const status = parseJson(fixture.status)
      const homeAway = parseJson(fixture.home_away)
      const kickoffDate = status?.utcTime ? new Date(status.utcTime) : null
      const isTeamHome = homeAway?.name ? homeAway.name !== fixture.opponent : false
      const isUpcoming = isUpcomingFixture(fixture, status, kickoffDate)
      const score = parseScore(status?.scoreStr)

      let formResult = '-'
      if (!isUpcoming && score) {
        const teamGoals = isTeamHome ? score.home : score.away
        const opponentGoals = isTeamHome ? score.away : score.home
        if (teamGoals > opponentGoals) formResult = 'W'
        if (teamGoals === opponentGoals) formResult = 'D'
        if (teamGoals < opponentGoals) formResult = 'L'
      }

      const roundRaw = fixture.round || fixture.round_name || fixture.matchday || fixture.tournament_round
      const homeTeamName = homeAway?.name || ''
      const homeGoals = score ? score.home : null
      const awayGoals = score ? score.away : null
      const teamGoals = score ? (isTeamHome ? score.home : score.away) : null
      const opponentGoals = score ? (isTeamHome ? score.away : score.home) : null

      return {
        ...fixture,
        status,
        kickoffDate,
        kickoffTimestamp: kickoffDate ? kickoffDate.getTime() : Number.NEGATIVE_INFINITY,
        isHome: isTeamHome,
        isUpcoming,
        formResult: isUpcoming ? 'h2h' : formResult,
        dateLabel: formatDate(kickoffDate),
        timeLabel: formatTime(kickoffDate),
        venueLabel: isTeamHome ? 'C' : 'F',
        scoreLabel: isUpcoming ? '-' : (status?.scoreStr?.replace(/\s+/g, '') || '-'),
        tournamentLabel: getCompetitionLabel(fixture, kickoffDate),
        roundLabel: formatRound(roundRaw),
        statusShort: status?.reason?.short || (isUpcoming ? 'NS' : '-'),
        statusLong: status?.reason?.long || (isUpcoming ? 'Not started' : '-'),
        homeTeamName,
        homeGoals,
        awayGoals,
        teamGoals,
        opponentGoals,
        matchUrl: fixture.page_url ? `https://www.fotmob.com${fixture.page_url}` : ''
      }
    })
    .sort((a, b) => b.kickoffTimestamp - a.kickoffTimestamp)

  $: visibleFixtures = hideUpcoming ? fixtures.filter(fixture => !fixture.isUpcoming) : fixtures
  $: teamName = fixtures.find(f => f.homeTeamName && f.homeTeamName !== f.opponent)?.homeTeamName || 'Team'
  $: detailHomeName = selectedFixture ? (selectedFixture.isHome ? teamName : selectedFixture.opponent) : ''
  $: detailAwayName = selectedFixture ? (selectedFixture.isHome ? selectedFixture.opponent : teamName) : ''
  $: detailHomeScore = selectedFixture
    ? (selectedFixture.isUpcoming ? '-' : (selectedFixture.isHome ? selectedFixture.teamGoals : selectedFixture.opponentGoals))
    : '-'
  $: detailAwayScore = selectedFixture
    ? (selectedFixture.isUpcoming ? '-' : (selectedFixture.isHome ? selectedFixture.opponentGoals : selectedFixture.teamGoals))
    : '-'
</script>

<svelte:window on:keydown={onGlobalKeydown} />

<div class="fixtures">
  <div class="toolbar">
    <div class="filter-toggle">
      <button
        class:active={!hideUpcoming}
        on:click={() => hideUpcoming = false}
        aria-label="Show all fixtures"
        title="Show all fixtures"
      >
        All
      </button>
      <button
        class:active={hideUpcoming}
        on:click={() => hideUpcoming = true}
        aria-label="Hide upcoming fixtures"
        title="Hide upcoming fixtures"
      >
        Played
      </button>
    </div>
    <span>{visibleFixtures.length} matches</span>
  </div>

  <div class="list">
    {#if visibleFixtures.length === 0}
      <div class="empty">No fixtures found.</div>
    {:else}
      {#each visibleFixtures as fixture (fixture.id || fixture.page_url)}
        <div
          class="fixture"
          class:upcoming={fixture.isUpcoming}
          role="button"
          tabindex="0"
          aria-label={`Open details for ${fixture.opponent} on ${fixture.dateLabel}`}
          on:click={() => openFixtureDetails(fixture)}
          on:keydown={(event) => onFixtureKeydown(event, fixture)}
        >
          <span class="result {fixture.formResult === 'h2h' ? 'h2h' : fixture.formResult.toLowerCase()}">{fixture.formResult}</span>
          <span class="date">{fixture.dateLabel}</span>
          <span class="time">{fixture.timeLabel}</span>
          <span class="venue">({fixture.venueLabel})</span>
          <span class="opponent-badge">
            {#if fixture.opponent_id}
              <img
                src={`https://images.fotmob.com/image_resources/logo/teamlogo/${fixture.opponent_id}.png`}
                alt=""
                loading="lazy"
                on:error={event => event.currentTarget.style.display = 'none'}
              />
            {/if}
          </span>
          <span class="opponent">{fixture.opponent}</span>
          <span class="score">{fixture.scoreLabel}</span>
          <span class="tournament">{fixture.tournamentLabel}</span>
        </div>
      {/each}
    {/if}
  </div>
</div>

{#if selectedFixture}
  <button class="dialog-backdrop" aria-label="Close dialog" on:click={closeFixtureDetails}></button>
  <div class="match-dialog" role="dialog" aria-modal="true" aria-label="Match details" tabindex="-1">
    <div class="dialog-header">
      <h4>Match Details</h4>
      <button class="close-btn" aria-label="Close dialog" on:click={closeFixtureDetails}>×</button>
    </div>

    <div class="dialog-scoreline">
      <div class="team-name">{detailHomeName}</div>
      <div class="team-score">{detailHomeScore}</div>
      <div class="team-separator">-</div>
      <div class="team-score">{detailAwayScore}</div>
      <div class="team-name away">{detailAwayName}</div>
    </div>

    <div class="dialog-grid">
      <div>
        <span>Competition</span>
        <strong>{selectedFixture.tournamentLabel}</strong>
      </div>
      <div>
        <span>Round</span>
        <strong>{selectedFixture.roundLabel}</strong>
      </div>
      <div>
        <span>Date</span>
        <strong>{selectedFixture.dateLabel}</strong>
      </div>
      <div>
        <span>Time (UTC)</span>
        <strong>{selectedFixture.timeLabel}</strong>
      </div>
      <div>
        <span>Venue</span>
        <strong>{selectedFixture.venueLabel === 'C' ? 'Home' : 'Away'}</strong>
      </div>
      <div>
        <span>Status</span>
        <strong>{selectedFixture.statusLong}</strong>
      </div>
      <div>
        <span>Match ID</span>
        <strong>{selectedFixture.id || '-'}</strong>
      </div>
      <div>
        <span>Result</span>
        <strong>{selectedFixture.scoreLabel}</strong>
      </div>
    </div>

    {#if selectedFixture.matchUrl}
      <a class="match-link" href={selectedFixture.matchUrl} target="_blank" rel="noreferrer">Open match page</a>
    {/if}
  </div>
{/if}

<style>
  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.75rem;
    gap: 0.75rem;
  }

  .filter-toggle {
    display: flex;
    gap: 0.25rem;
  }

  .filter-toggle button {
    background: #1a1a1a;
    border: 1px solid #333;
    padding: 0.5rem 0.75rem;
    cursor: pointer;
    color: #666;
    border-radius: 0.25rem;
    transition: all 0.2s;
    font-size: 0.8rem;
    line-height: 1;
  }

  .filter-toggle button:hover {
    color: #fff;
  }

  .filter-toggle button.active {
    background: #333;
    color: #fff;
    border-color: #444;
  }

  .toolbar span {
    color: #888;
    font-size: 0.8rem;
  }

  .list {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .fixture {
    display: grid;
    grid-template-columns: 2.6rem 6.6rem 4rem 2.8rem 2.3rem minmax(10rem, 1fr) 4.5ch minmax(12rem, 1fr);
    align-items: center;
    gap: 0.45rem;
    padding: 0.6rem 0.5rem;
    border-bottom: 1px solid #1a1a1a;
    font-size: 0.9rem;
    cursor: pointer;
    background: transparent;
    border: none;
    width: 100%;
    text-align: left;
  }

  .fixture:hover {
    background: #111;
  }

  .fixture:focus-visible {
    outline: 1px solid #3b82f6;
    outline-offset: 1px;
  }

  .result {
    width: 2rem;
    height: 2rem;
    border-radius: 0.45rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    color: #fff;
    line-height: 1;
  }

  .result.w {
    background: #739a3c;
  }

  .result.d {
    background: #949494;
  }

  .result.l {
    background: #c84940;
  }

  .result.h2h {
    width: auto;
    height: auto;
    border-radius: 0;
    background: transparent;
    color: #c7ced6;
    font-weight: 500;
  }

  .date {
    color: #888;
    font-size: 0.8rem;
  }

  .time {
    color: #666;
    font-size: 0.75rem;
  }

  .venue {
    color: #888;
    font-size: 0.8rem;
    font-weight: 500;
  }

  .opponent-badge {
    width: 2rem;
    height: 2rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .opponent-badge img {
    width: 1.9rem;
    height: 1.9rem;
    object-fit: contain;
  }

  .opponent {
    color: #e0e0e0;
    min-width: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .score {
    width: 4.5ch;
    justify-self: center;
    text-align: center;
    color: #e0e0e0;
    font-weight: 500;
    font-variant-numeric: tabular-nums;
  }

  .tournament {
    color: #999;
    font-size: 0.8rem;
    text-align: right;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .upcoming {
    opacity: 0.6;
  }

  .empty {
    color: #888;
    font-size: 0.9rem;
    padding: 1rem 0.5rem;
  }

  .dialog-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.62);
    border: none;
    margin: 0;
    padding: 0;
    z-index: 30;
    cursor: pointer;
  }

  .match-dialog {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: min(680px, calc(100vw - 2rem));
    background: #0f1115;
    border: 1px solid #262b35;
    border-radius: 0.6rem;
    z-index: 31;
    padding: 1rem;
    box-shadow: 0 25px 70px rgba(0, 0, 0, 0.45);
  }

  .dialog-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.8rem;
  }

  .dialog-header h4 {
    margin: 0;
    color: #e5e7eb;
    font-size: 0.95rem;
    letter-spacing: 0.02em;
  }

  .close-btn {
    border: 1px solid #323946;
    background: #151924;
    color: #d1d5db;
    width: 2rem;
    height: 2rem;
    border-radius: 0.35rem;
    cursor: pointer;
    line-height: 1;
    font-size: 1.1rem;
  }

  .close-btn:hover {
    color: #fff;
    border-color: #475569;
  }

  .dialog-scoreline {
    display: grid;
    grid-template-columns: 1fr auto auto auto 1fr;
    gap: 0.5rem;
    align-items: center;
    padding: 0.75rem;
    background: #151923;
    border: 1px solid #242938;
    border-radius: 0.45rem;
    margin-bottom: 0.85rem;
  }

  .team-name {
    color: #f3f4f6;
    font-weight: 600;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .team-name.away {
    text-align: right;
  }

  .team-score {
    color: #fff;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
    min-width: 1.2rem;
    text-align: center;
  }

  .team-separator {
    color: #9ca3af;
  }

  .dialog-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.65rem;
    margin-bottom: 0.75rem;
  }

  .dialog-grid div {
    background: #121620;
    border: 1px solid #232838;
    border-radius: 0.4rem;
    padding: 0.5rem 0.6rem;
    min-width: 0;
  }

  .dialog-grid span {
    display: block;
    color: #8490a3;
    font-size: 0.72rem;
    margin-bottom: 0.22rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  .dialog-grid strong {
    display: block;
    color: #e5e7eb;
    font-size: 0.88rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .match-link {
    display: inline-block;
    color: #7dd3fc;
    text-decoration: none;
    font-size: 0.85rem;
  }

  .match-link:hover {
    color: #bae6fd;
    text-decoration: underline;
  }

  @media (max-width: 900px) {
    .fixture {
      grid-template-columns: 2.6rem 6.4rem 4rem 2.8rem 2.3rem minmax(7rem, 1fr) 4.5ch minmax(10rem, 1fr);
    }

    .tournament {
      grid-column: auto;
      padding-left: 0;
    }

  }

  @media (max-width: 640px) {
    .toolbar {
      flex-direction: column;
      align-items: flex-start;
    }

    .fixture {
      grid-template-columns: 2.6rem 5.6rem 3.5rem 1.8rem 1fr 3.6rem;
      grid-template-areas:
        'result date time venue opponent score'
        'result badge badge tournament tournament tournament';
      font-size: 0.85rem;
    }

    .result {
      grid-area: result;
      align-self: start;
      margin-top: 0.2rem;
    }

    .date {
      grid-area: date;
    }

    .time {
      grid-area: time;
    }

    .venue {
      grid-area: venue;
    }

    .opponent {
      grid-area: opponent;
    }

    .opponent-badge {
      grid-area: badge;
      justify-content: flex-start;
    }

    .score {
      grid-area: score;
    }

    .tournament {
      grid-area: tournament;
      max-width: 100%;
    }

    .match-dialog {
      padding: 0.85rem;
    }

    .dialog-scoreline {
      grid-template-columns: 1fr auto 1fr;
      grid-template-areas:
        'home score away';
      gap: 0.45rem;
    }

    .team-name {
      font-size: 0.85rem;
    }

    .team-name.away {
      text-align: right;
    }

    .dialog-grid {
      grid-template-columns: 1fr;
    }

  }
</style>
