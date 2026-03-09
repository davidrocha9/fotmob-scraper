export async function parseCSV(text) {
  const normalized = text.trim()
  if (!normalized) return []

  const rows = []
  let current = ''
  let row = []
  let inQuotes = false

  for (let i = 0; i < text.length; i += 1) {
    const char = text[i]
    const next = text[i + 1]

    if (char === '"') {
      if (inQuotes && next === '"') {
        current += '"'
        i += 1
      } else {
        inQuotes = !inQuotes
      }
    } else if (char === ',' && !inQuotes) {
      row.push(current)
      current = ''
    } else if ((char === '\n' || char === '\r') && !inQuotes) {
      if (char === '\r' && next === '\n') i += 1
      row.push(current)
      if (row.some(cell => cell !== '')) rows.push(row)
      row = []
      current = ''
    } else {
      current += char
    }
  }

  if (current !== '' || row.length > 0) {
    row.push(current)
    if (row.some(cell => cell !== '')) rows.push(row)
  }

  if (rows.length === 0) return []

  const headers = rows[0]
  return rows.slice(1).map(values => {
    const obj = {}
    headers.forEach((header, index) => {
      obj[header] = values[index] ?? ''
    })
    return obj
  })
}

export async function loadTeamData() {
  const files = {
    teamInfo: 'team_info.csv',
    squad: 'squad.csv',
    fixtures: 'fixtures.csv',
    playerStats: 'player_stats.csv',
    playerStatRankings: 'player_stat_rankings.csv',
    teamStatRankings: 'team_stat_rankings.csv',
    transfers: 'transfers.csv',
    matchHighlights: 'match_highlights.csv',
    teamForm: 'team_form.csv',
    topPlayers: 'top_players.csv',
    venue: 'venue.csv',
    leagueTable: 'league_table.csv',
    tableLegend: 'table_legend.csv',
    coachHistory: 'coach_history.csv',
    trophies: 'trophies.csv',
    historicalSeasons: 'historical_seasons.csv',
    historicalTableRows: 'historical_table_rows.csv',
    historicalTableRules: 'historical_table_rules.csv',
    faq: 'faq.csv',
    tabs: 'tabs.csv',
    lastLineup: 'last_lineup.csv',
    lastLineupPlayers: 'last_lineup_players.csv',
    matchDetails: 'match_details.csv',
    matchEvents: 'match_events.csv',
    matchStats: 'match_stats.csv',
    matchShots: 'match_shots.csv',
    matchLineupPlayers: 'match_lineup_players.csv',
    matchPlayerStats: 'match_player_stats.csv',
    playerProfiles: 'player_profiles.csv',
    playerRecentMatches: 'player_recent_matches.csv',
    playerCareerEntries: 'player_career_entries.csv',
    playerMarketValues: 'player_market_values.csv',
    playerTrophies: 'player_trophies.csv',
    playerTraits: 'player_traits.csv'
  }

  const data = {}

  await Promise.all(Object.entries(files).map(async ([key, filename]) => {
    try {
      const response = await fetch(`/${filename}`)
      if (!response.ok) {
        data[key] = []
        return
      }
      const text = await response.text()
      data[key] = await parseCSV(text)
    } catch {
      data[key] = []
    }
  }))

  return data
}

export function formatValue(value) {
  if (value === undefined || value === null || value === '') return '-'
  return value
}

export function formatNumber(value, digits = 0) {
  if (value === undefined || value === null || value === '') return '-'
  const number = Number(value)
  if (Number.isNaN(number)) return value
  return number.toLocaleString('en-US', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits
  })
}

export function formatPercent(value, digits = 1) {
  if (value === undefined || value === null || value === '') return '-'
  const number = Number(value)
  if (Number.isNaN(number)) return value
  return `${number.toFixed(digits)}%`
}

export function formatMarketValue(value) {
  if (!value || value === '') return '-'
  const num = Number(value)
  if (Number.isNaN(num)) return value
  if (num >= 1000000000) return `EUR ${(num / 1000000000).toFixed(2)}B`
  if (num >= 1000000) return `EUR ${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `EUR ${(num / 1000).toFixed(0)}K`
  return `EUR ${num}`
}

export function formatDate(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toISOString().slice(0, 10)
}

export function formatDateTime(value) {
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

export function parseJSON(value, fallback = null) {
  if (!value) return fallback
  try {
    return JSON.parse(value)
  } catch {
    return fallback
  }
}

export function groupBy(items, keyGetter) {
  return items.reduce((groups, item) => {
    const key = keyGetter(item)
    if (!groups[key]) groups[key] = []
    groups[key].push(item)
    return groups
  }, {})
}

export function playerImageUrl(player) {
  return player?.player_image_url || player?.image_url || '/player-fallback.svg'
}

export function onPlayerImageError(event) {
  event.currentTarget.src = '/player-fallback.svg'
}
