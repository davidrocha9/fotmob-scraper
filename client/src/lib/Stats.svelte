<script>
  export let data = []

  $: grouped = (() => {
    const groups = {}
    ;(data || []).forEach(player => {
      const cat = player.category || 'other'
      if (!groups[cat]) groups[cat] = []
      groups[cat].push(player)
    })
    return Object.entries(groups).map(([name, players]) => ({
      id: name,
      label: players[0]?.category_display || name,
      players: [...players].sort((a, b) => Number(a.rank || 9999) - Number(b.rank || 9999))
    }))
  })()

  function formatValue(value, format) {
    if (value === undefined || value === null || value === '') return '-'
    const numeric = Number(value)
    if (Number.isNaN(numeric)) return value
    if (format === 'fraction') {
      return Number.isInteger(numeric) ? String(numeric) : numeric.toFixed(2)
    }
    if (format === 'number') {
      return Number.isInteger(numeric) ? String(numeric) : numeric.toFixed(1)
    }
    return String(value)
  }
</script>

<div class="stats">
  {#if data.length === 0}
    <p class="empty">No stats data available</p>
  {:else}
    <div class="categories">
      {#each grouped as group}
        <section>
          <h3>{group.label}</h3>
          <table>
            <thead>
              <tr>
                <th class="th-rank">Rank</th>
                <th>Player</th>
                <th class="th-country">Country</th>
                <th class="th-value">Value</th>
              </tr>
            </thead>
            <tbody>
              {#each group.players as player, i}
                <tr>
                  <td class="th-rank">{i + 1}</td>
                  <td class="name">{player.player_name || '-'}</td>
                  <td class="th-country">{player.player_country || '-'}</td>
                  <td class="th-value">{formatValue(player.value, player.format)}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </section>
      {/each}
    </div>
  {/if}
</div>

<style>
  .empty {
    color: #666;
    text-align: center;
    padding: 4rem;
  }

  .categories {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1rem;
    width: 100%;
  }

  section {
    background: #111;
    border: 1px solid #1f1f1f;
    border-radius: 0.5rem;
    padding: 0.85rem;
  }

  h3 {
    text-transform: uppercase;
    font-size: 0.75rem;
    color: #666;
    margin-bottom: 0.75rem;
    letter-spacing: 0.1em;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
    table-layout: auto;
  }

  th {
    text-align: left;
    padding: 0.5rem;
    color: #666;
    font-weight: 500;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid #222;
    white-space: nowrap;
  }

  td {
    padding: 0.5rem;
    border-bottom: 1px solid #222;
    font-size: 0.9rem;
    white-space: nowrap;
  }

  .th-rank {
    width: 4.5rem;
  }

  .th-country {
    width: 5rem;
    text-align: center;
  }

  .th-value {
    width: 6rem;
    text-align: right;
  }

  td.th-rank {
    color: #666;
    font-weight: 600;
  }

  .name {
    color: #fff;
    font-weight: 500;
  }

  .th-value {
    color: #e0e0e0;
    font-weight: 600;
  }

  @media (max-width: 640px) {
    .categories {
      grid-template-columns: 1fr;
    }

    table {
      font-size: 0.85rem;
    }

    .th-country {
      display: none;
    }
  }

  @media (min-width: 641px) and (max-width: 1050px) {
    .categories {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }
</style>
