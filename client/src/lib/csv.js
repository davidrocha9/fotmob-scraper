export async function parseCSV(text) {
  const lines = text.trim().split('\n')
  const headers = parseCSVLine(lines[0])
  
  return lines.slice(1).map(line => {
    const values = parseCSVLine(line)
    const obj = {}
    headers.forEach((header, i) => {
      obj[header] = values[i] || ''
    })
    return obj
  })
}

function parseCSVLine(line) {
  const result = []
  let current = ''
  let inQuotes = false
  
  for (let i = 0; i < line.length; i++) {
    const char = line[i]
    
    if (char === '"') {
      if (inQuotes && line[i + 1] === '"') {
        current += '"'
        i++
      } else {
        inQuotes = !inQuotes
      }
    } else if (char === ',' && !inQuotes) {
      result.push(current.trim())
      current = ''
    } else {
      current += char
    }
  }
  
  result.push(current.trim())
  return result
}

export async function loadTeamData() {
  const files = {
    teamInfo: 'team_info.csv',
    squad: 'squad.csv',
    fixtures: 'fixtures.csv',
    playerStats: 'player_stats.csv',
    transfers: 'transfers.csv'
  }
  
  const data = {}
  
  for (const [key, filename] of Object.entries(files)) {
    try {
      const response = await fetch(`/${filename}`)
      if (response.ok) {
        const text = await response.text()
        data[key] = await parseCSV(text)
      }
    } catch (e) {
      data[key] = []
    }
  }
  
  return data
}

export function formatValue(value) {
  if (!value || value === '') return '-'
  return value
}

export function formatMarketValue(value) {
  if (!value || value === '') return '-'
  const num = parseFloat(value)
  if (isNaN(num)) return value
  if (num >= 1000000) return `€${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `€${(num / 1000).toFixed(0)}K`
  return `€${num}`
}
