<script>
  export let data = []

  function normalizeType(type) {
    const value = String(type || '').toLowerCase()
    if (value.includes('in')) return 'in'
    if (value.includes('out')) return 'out'
    if (value.includes('contract')) return 'extension'
    return 'other'
  }

  function formatDate(value) {
    if (!value) return '-'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return value
    return date.toISOString().slice(0, 10)
  }

  function formatMarketValue(value) {
    if (value === undefined || value === null || value === '') return '-'
    const numeric = Number(value)
    if (Number.isNaN(numeric)) return value
    if (numeric >= 1000000) return `€${(numeric / 1000000).toFixed(1)}M`
    if (numeric >= 1000) return `€${Math.round(numeric / 1000)}K`
    return `€${numeric}`
  }

  function formatFee(transfer) {
    const rawFee = String(transfer.fee || '').trim().toLowerCase()
    if (rawFee.includes('loan') || String(transfer.on_loan).toLowerCase() === 'true') return 'Loan'
    if (rawFee.includes('free')) return 'Free'
    if (rawFee === 'fee') return formatMarketValue(transfer.market_value)
    if (rawFee) return transfer.fee
    return '-'
  }

  function sortByDateDesc(list) {
    return [...list].sort((a, b) => {
      const aTime = a.transfer_date ? new Date(a.transfer_date).getTime() : 0
      const bTime = b.transfer_date ? new Date(b.transfer_date).getTime() : 0
      return bTime - aTime
    })
  }

  $: transfersIn = sortByDateDesc(data.filter(t => normalizeType(t.type) === 'in'))
  $: transfersOut = sortByDateDesc(data.filter(t => normalizeType(t.type) === 'out'))
  $: extensions = sortByDateDesc(data.filter(t => normalizeType(t.type) === 'extension'))
  $: hasTransfers = transfersIn.length > 0 || transfersOut.length > 0 || extensions.length > 0
</script>

<div class="transfers">
  {#if !hasTransfers}
    <p class="empty">No transfer data available</p>
  {:else}
    {#if transfersIn.length > 0}
      <section>
        <h3>Incoming</h3>
        <table>
          <colgroup>
            <col class="col-date" />
            <col class="col-player" />
            <col class="col-club" />
            <col class="col-fee" />
          </colgroup>
          <thead>
            <tr>
              <th class="th-date">Date</th>
              <th>Player</th>
              <th class="th-club">From</th>
              <th class="th-fee">Fee</th>
            </tr>
          </thead>
          <tbody>
          {#each transfersIn as transfer}
            <tr>
              <td class="th-date">{formatDate(transfer.transfer_date)}</td>
              <td class="name">{transfer.player_name || '-'}</td>
              <td class="th-club">{transfer.from_club || '-'}</td>
              <td class="th-fee">{formatFee(transfer)}</td>
            </tr>
          {/each}
          </tbody>
        </table>
      </section>
    {/if}

    {#if transfersOut.length > 0}
      <section>
        <h3>Outgoing</h3>
        <table>
          <colgroup>
            <col class="col-date" />
            <col class="col-player" />
            <col class="col-club" />
            <col class="col-fee" />
          </colgroup>
          <thead>
            <tr>
              <th class="th-date">Date</th>
              <th>Player</th>
              <th class="th-club">To</th>
              <th class="th-fee">Fee</th>
            </tr>
          </thead>
          <tbody>
          {#each transfersOut as transfer}
            <tr>
              <td class="th-date">{formatDate(transfer.transfer_date)}</td>
              <td class="name">{transfer.player_name || '-'}</td>
              <td class="th-club">{transfer.to_club || '-'}</td>
              <td class="th-fee">{formatFee(transfer)}</td>
            </tr>
          {/each}
          </tbody>
        </table>
      </section>
    {/if}

    {#if extensions.length > 0}
      <section>
        <h3>Contract Extensions</h3>
        <table>
          <colgroup>
            <col class="col-date" />
            <col class="col-player-only" />
          </colgroup>
          <thead>
            <tr>
              <th class="th-date">Date</th>
              <th>Player</th>
            </tr>
          </thead>
          <tbody>
          {#each extensions as transfer}
            <tr>
              <td class="th-date">{formatDate(transfer.transfer_date)}</td>
              <td class="name">{transfer.player_name || '-'}</td>
            </tr>
          {/each}
          </tbody>
        </table>
      </section>
    {/if}
  {/if}
</div>

<style>
  .empty {
    color: #666;
    text-align: center;
    padding: 4rem;
  }

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

  table {
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
    font-size: 0.9rem;
  }

  .col-date {
    width: 11ch;
  }

  .col-player {
    width: 38%;
  }

  .col-club {
    width: auto;
  }

  .col-fee {
    width: 10ch;
  }

  .col-player-only {
    width: auto;
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
    white-space: nowrap;
    font-variant-numeric: tabular-nums;
  }

  .name {
    color: #fff;
    font-weight: 500;
  }

  .th-date {
    color: #888;
  }

  .th-club {
    color: #bbb;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .th-fee {
    text-align: right;
    color: #e0e0e0;
    font-weight: 600;
  }

  @media (max-width: 700px) {
    table {
      font-size: 0.85rem;
    }
  }
</style>
