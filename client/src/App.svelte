<script>
  import { onMount } from 'svelte'
  import { loadTeamData } from './lib/csv.js'
  import Squad from './lib/Squad.svelte'
  import Fixtures from './lib/Fixtures.svelte'
  import Stats from './lib/Stats.svelte'
  import Transfers from './lib/Transfers.svelte'

  let data = {}
  let loading = true
  let activeTab = 'squad'

  const tabs = [
    { id: 'squad', label: 'Squad' },
    { id: 'fixtures', label: 'Fixtures' },
    { id: 'stats', label: 'Stats' },
    { id: 'transfers', label: 'Transfers' }
  ]

  async function loadData() {
    loading = true
    data = await loadTeamData()
    loading = false
  }

  onMount(loadData)
</script>

<main>
  <header>
    <h1>{data.teamInfo?.[0]?.team_name || 'Team Data'}</h1>
    {#if data.teamInfo?.[0]}
      <span class="season">{data.teamInfo[0].season}</span>
    {/if}
  </header>

  {#if loading}
    <div class="loading">Loading...</div>
  {:else if !data.teamInfo || data.teamInfo.length === 0}
    <div class="loading">No team data found. Run scraper/scraper.py first.</div>
  {:else}
    <nav>
      {#each tabs as tab}
        <button 
          class:active={activeTab === tab.id}
          on:click={() => activeTab = tab.id}
        >
          {tab.label}
        </button>
      {/each}
    </nav>

    <div class="content">
        {#if activeTab === 'squad'}
          <Squad data={data.squad || []} />
        {:else if activeTab === 'fixtures'}
          <Fixtures data={data.fixtures || []} />
        {:else if activeTab === 'stats'}
          <Stats data={data.playerStats || []} />
        {:else if activeTab === 'transfers'}
          <Transfers data={data.transfers || []} />
        {/if}
      </div>
  {/if}
</main>

<style>
  :global(*) {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  :global(body) {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0f0f0f;
    color: #e0e0e0;
    min-height: 100vh;
  }

  main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
  }

  header {
    margin-bottom: 2rem;
    display: flex;
    align-items: baseline;
    gap: 1rem;
  }

  h1 {
    font-size: 2rem;
    font-weight: 600;
  }

  .season {
    color: #666;
    font-size: 0.9rem;
  }

  nav {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 2rem;
    border-bottom: 1px solid #222;
    padding-bottom: 1rem;
  }

  button {
    background: transparent;
    border: none;
    color: #666;
    padding: 0.5rem 1rem;
    cursor: pointer;
    font-size: 0.95rem;
    transition: color 0.2s;
  }

  button:hover {
    color: #e0e0e0;
  }

  button.active {
    color: #fff;
    border-bottom: 2px solid #c00;
    margin-bottom: -1px;
  }

  .loading {
    text-align: center;
    padding: 4rem;
    color: #666;
  }

  .content {
    animation: fadeIn 0.3s ease;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
</style>
