<script>
  import { formatMarketValue } from './csv.js'

  export let data = []

  function formatDate(value) {
    if (!value) return '-'
    const d = new Date(value)
    if (Number.isNaN(d.getTime())) return value
    return d.toISOString().slice(0, 10)
  }

  function timestamp(value) {
    if (!value) return 0
    const t = new Date(value).getTime()
    return Number.isFinite(t) ? t : 0
  }

  function normalizeType(type) {
    const v = String(type || '').toLowerCase()
    if (v.includes('in'))       return 'in'
    if (v.includes('out'))      return 'out'
    if (v.includes('contract')) return 'extension'
    return 'other'
  }

  function formatFee(transfer) {
    if (transfer.fee_value) return formatMarketValue(transfer.fee_value)
    const fee = String(transfer.fee || '').trim()
    return fee || '-'
  }

  function sortByDateDesc(list) {
    return [...list].sort((a,b) => timestamp(b.transfer_date) - timestamp(a.transfer_date))
  }

  $: transfersIn  = sortByDateDesc((data || []).filter(t => normalizeType(t.type) === 'in'))
  $: transfersOut = sortByDateDesc((data || []).filter(t => normalizeType(t.type) === 'out'))
  $: extensions   = sortByDateDesc((data || []).filter(t => normalizeType(t.type) === 'extension'))
</script>

<div class="transfer-layout">

  <!-- Incoming -->
  <section class="transfer-column">
    <div class="column-head">
      <div>
        <span class="eyebrow">Arrivals</span>
        <h3>{transfersIn.length} incoming</h3>
      </div>
    </div>
    {#if transfersIn.length === 0}
      <p class="empty">No incoming transfers</p>
    {:else}
      {#each transfersIn as transfer}
        <article class="transfer-card in">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:0.5rem;">
            <div>
              <strong>{transfer.player_name || '-'}</strong>
              <small style="display:block;color:var(--text-2);">{transfer.position || '-'} · from {transfer.from_club || '-'}</small>
            </div>
            <b style="white-space:nowrap;font-size:0.82rem;">{formatFee(transfer)}</b>
          </div>
          <div style="margin-top:0.35rem;font-size:0.73rem;color:var(--text-3);">
            {formatDate(transfer.transfer_date)} · {transfer.transfer_type_text || transfer.fee || '-'}
          </div>
        </article>
      {/each}
    {/if}
  </section>

  <!-- Outgoing -->
  <section class="transfer-column">
    <div class="column-head">
      <div>
        <span class="eyebrow">Departures</span>
        <h3>{transfersOut.length} outgoing</h3>
      </div>
    </div>
    {#if transfersOut.length === 0}
      <p class="empty">No outgoing transfers</p>
    {:else}
      {#each transfersOut as transfer}
        <article class="transfer-card out">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:0.5rem;">
            <div>
              <strong>{transfer.player_name || '-'}</strong>
              <small style="display:block;color:var(--text-2);">{transfer.position || '-'} · to {transfer.to_club || '-'}</small>
            </div>
            <b style="white-space:nowrap;font-size:0.82rem;">{formatFee(transfer)}</b>
          </div>
          <div style="margin-top:0.35rem;font-size:0.73rem;color:var(--text-3);">
            {formatDate(transfer.transfer_date)} · {transfer.transfer_type_text || transfer.fee || '-'}
          </div>
        </article>
      {/each}
    {/if}
  </section>

  <!-- Extensions -->
  <section class="transfer-column">
    <div class="column-head">
      <div>
        <span class="eyebrow">Renewals</span>
        <h3>{extensions.length} extensions</h3>
      </div>
    </div>
    {#if extensions.length === 0}
      <p class="empty">No contract extensions</p>
    {:else}
      {#each extensions as transfer}
        <article class="transfer-card extension">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:0.5rem;">
            <div>
              <strong>{transfer.player_name || '-'}</strong>
              <small style="display:block;color:var(--text-2);">{transfer.position || '-'}</small>
            </div>
            <b style="white-space:nowrap;font-size:0.82rem;">{transfer.to_date ? `Until ${formatDate(transfer.to_date)}` : '-'}</b>
          </div>
          <div style="margin-top:0.35rem;font-size:0.73rem;color:var(--text-3);">
            {formatDate(transfer.transfer_date)}
          </div>
        </article>
      {/each}
    {/if}
  </section>

</div>
