<script>
  import { formatMarketValue } from './csv.js'

  export let data

  let viewMode = 'list'

  const positionOrder = ['keepers', 'defenders', 'midfielders', 'attackers']
  
  $: grouped = (() => {
    const groups = {}
    data.forEach(player => {
      const group = player.position_group || 'other'
      if (!groups[group]) groups[group] = []
      groups[group].push(player)
    })
    return positionOrder
      .filter(g => groups[g])
      .map(g => ({ name: g, players: groups[g] }))
  })()

  function getRatingClass(rating) {
    if (!rating) return ''
    const r = parseFloat(rating)
    if (r >= 7) return 'rating-great'
    if (r >= 6) return 'rating-good'
    if (r >= 5) return 'rating-ok'
    return 'rating-bad'
  }

  function formatHeight(height) {
    if (!height) return '-'
    return Math.round(height)  + ' cm'
  }

  function getInitials(name) {
    if (!name) return '?'
    return name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
  }
</script>

<div class="squad">
  <div class="view-toggle">
    <button class:active={viewMode === 'list'} on:click={() => viewMode = 'list'}>
      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>
    </button>
    <button class:active={viewMode === 'grid'} on:click={() => viewMode = 'grid'}>
      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
    </button>
  </div>

  {#if viewMode === 'list'}
    {#each grouped as group}
      <section>
        <h3>{group.name}</h3>
        <table>
          <thead>
            <tr>
              <th class="th-num">#</th>
              <th class="th-player">Player</th>
              <th class="th-country">Country</th>
              <th class="th-age">Age</th>
              <th class="th-height">Height</th>
              <th class="th-rating">Rating</th>
              <th class="th-stat">G</th>
              <th class="th-stat">A</th>
              <th class="th-cards"><span class="card-header yellow"></span></th>
              <th class="th-cards"><span class="card-header red"></span></th>
              <th class="th-value">Value</th>
            </tr>
          </thead>
          <tbody>
            {#each group.players as player}
              <tr>
                <td class="th-num">{player.shirt_number ? Math.round(player.shirt_number) : '-'}</td>
                <td class="name th-player">{player.name}</td>
                <td class="th-country">{player.country_code || '-'}</td>
                <td class="th-age">{player.age || '-'}</td>
                <td class="th-height">{formatHeight(player.height)}</td>
                <td class="th-rating {getRatingClass(player.rating)}">{player.rating || '-'}</td>
                <td class="th-stat">{player.goals ? Math.round(player.goals) : '0'}</td>
                <td class="th-stat">{player.assists ? Math.round(player.assists) : '0'}</td>
                <td class="th-cards">{Math.round(player.yellow_cards) || 0}</td>
                <td class="th-cards">{Math.round(player.red_cards) || 0}</td>
                <td class="th-value">{formatMarketValue(player.market_value)}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </section>
    {/each}
  {:else}
    {#each grouped as group}
      <section>
        <h3>{group.name}</h3>
        <div class="grid">
          {#each group.players as player}
            <div class="card">
              <div class="card-header-area">
                <div class="card-number">{player.shirt_number ? Math.round(player.shirt_number) : '-'}</div>
                <div class="card-value">{formatMarketValue(player.market_value)}</div>
              </div>
              <div class="card-name">{player.name}</div>
              <div class="card-info">
                <span>{player.country_code || '-'}</span>
              </div>
              <div class="card-stats">
                <div class="stat">
                  <span class="label">Age</span>
                  <span class="value">{player.age || '-'}</span>
                </div>
                <div class="stat">
                  <span class="label">Rating</span>
                  <span class="value {getRatingClass(player.rating)}">{player.rating || '-'}</span>
                </div>
                <div class="stat">
                  <span class="label">G</span>
                  <span class="value">{player.goals ? Math.round(player.goals) : '0'}</span>
                </div>
                <div class="stat">
                  <span class="label">A</span>
                  <span class="value">{player.assists ? Math.round(player.assists) : '0'}</span>
                </div>
                <div class="stat">
                  <span class="card-small card-header yellow"></span>
                  <span class="value">{player.yellow_cards ? Math.round(player.yellow_cards) : '0'}</span>
                </div>
                <div class="stat">
                  <span class="card-small card-header red"></span>
                  <span class="value">{player.red_cards ? Math.round(player.red_cards) : '0'}</span>
                </div>
              </div>
            </div>
          {/each}
        </div>
      </section>
    {/each}
  {/if}
</div>

<style>
  h3 {
    text-transform: uppercase;
    font-size: 0.75rem;
    color: #666;
    margin-bottom: 0.75rem;
    letter-spacing: 0.1em;
  }

  section {
    margin-bottom: 2rem;
  }

  .view-toggle {
    display: flex;
    gap: 0.25rem;
    margin-bottom: 1.5rem;
  }

  .view-toggle button {
    background: #1a1a1a;
    border: 1px solid #333;
    padding: 0.5rem;
    cursor: pointer;
    color: #666;
    border-radius: 0.25rem;
    transition: all 0.2s;
  }

  .view-toggle button:hover {
    color: #e0e0e0;
  }

  .view-toggle button.active {
    background: #333;
    color: #fff;
    border-color: #444;
  }

  /* List View */
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
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
    border-bottom: 1px solid #1a1a1a;
    vertical-align: middle;
    white-space: nowrap;
  }

  .th-num { width: 3rem; text-align: center; }
  .th-player { min-width: 150px; }
  .th-country { width: 5rem; }
  .th-age { width: 3rem; text-align: center; }
  .th-height { width: 4.5rem; text-align: center; }
  .th-rating { width: 4rem; text-align: center; }
  .th-stat { width: 3rem; text-align: center; }
  .th-cards { width: 2.5rem; text-align: center; }
  .th-value { width: 6rem; text-align: right; padding-right: 1rem; }

  .name { font-weight: 500; color: #fff; }
  .th-rating { font-weight: 500; }
  .rating-great { color: #22c55e; }
  .rating-good { color: #facc15; }
  .rating-ok { color: #fa8f15; }
  .rating-bad { color: #ef4444; }
  .th-stat { font-weight: 600; color: #e0e0e0; }
  .th-value { color: #888; }

  .card-header {
    display: inline-block;
    width: 1rem;
    height: 1.25rem;
    border-radius: 0.2rem;
  }
  .card-header.yellow { background: #facc15; }
  .card-header.red { background: #ef4444; }
  .card-small {
    width: 0.5rem;
    height: 0.65rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 0.65rem;
    border-radius: 0.15rem;
  }

  /* Grid View */
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 1rem;
  }

  .card {
    background: #1a1a1a;
    border-radius: 0.5rem;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .card-header-area {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .card-number {
    font-size: 1.5rem;
    font-weight: 700;
    color: #444;
  }

  .card-avatar {
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 50%;
    background: #2a2a2a;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 600;
    color: #888;
  }

  .card-value {
    margin-left: auto;
    font-size: 0.8rem;
    color: #888;
    font-weight: 500;
  }

  .card-name {
    font-weight: 600;
    color: #fff;
    font-size: 0.95rem;
  }

  .card-info {
    display: flex;
    gap: 0.5rem;
    font-size: 0.75rem;
    color: #666;
  }

  .card-info span:first-child {
    color: #888;
  }

  .card-stats {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 0.25rem;
    margin-top: 0.5rem;
  }

  .card-stats .stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.1rem;
  }

  .card-stats .label {
    font-size: 0.65rem;
    line-height: 1;
    color: #555;
    text-transform: uppercase;
  }

  .card-stats .value {
    font-size: 0.9rem;
    font-weight: 600;
    color: #e0e0e0;
  }

  .card-stats .value.rating-great { color: #22c55e; }
  .card-stats .value.rating-good { color: #facc15; }
  .card-stats .value.rating-ok { color: #fa8f15; }
  .card-stats .value.rating-bad { color: #ef4444; }
</style>
