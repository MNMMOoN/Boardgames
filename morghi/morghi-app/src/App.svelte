<script lang="ts">
  import { GameInfo } from "./core/state";
  import GamePage from "./views/GamePage.svelte";
  import LoginPage from "./views/LoginPage.svelte";
  import PlayerPage from "./views/PlayerPage.svelte";
  import auth from "./services/auth.svelte";
  let game: GameInfo | null = $state(null);
</script>

<svelte:boundary>
  {#if auth.isLoggedIn}
    {#if game === null}
      <PlayerPage onEnterGame={(g) => (game = g)} />
    {:else}
      <GamePage gameInfo={game} onLeftGame={() => (game = null)} />
    {/if}
  {:else}
    <LoginPage />
  {/if}
  {#snippet failed(error, retry)}
    <main class="error-boundary">
      <div class="error-card">
        <h1 class="error-title">Oops! Something went wrong</h1>
        {#if error === null}
          <p class="error-message">An unexpected error occurred.</p>
        {:else if error instanceof Error}
          <div class="error-details">
            <h2 class="error-name">{error.name}</h2>
            {#if error.cause}
              <p class="error-cause">Cause: {error.cause}</p>
            {/if}
            <p class="error-message">{error.message}</p>
            {#if error.stack}
              <details class="error-stack">
                <summary>Stack Trace</summary>
                <pre>{error.stack}</pre>
              </details>
            {/if}
          </div>
        {:else}
          <div class="error-details">
            <pre class="error-pre">{error}</pre>
          </div>
        {/if}
        <button class="retry-button" onclick={retry}>Try Again</button>
      </div>
    </main>
  {/snippet}
</svelte:boundary>

<style>
  .error-boundary {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: var(--spacing-md);
  }
  
  .error-card {
    width: 100%;
    max-width: 600px;
    background-color: var(--color-surface);
    border-radius: var(--radius-lg);
    padding: var(--spacing-xl);
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-md);
  }
  
  .error-title {
    color: var(--color-error);
    margin-bottom: var(--spacing-lg);
    text-align: center;
  }
  
  .error-details {
    margin-bottom: var(--spacing-lg);
  }
  
  .error-name {
    color: var(--color-error);
    font-size: var(--font-size-xl);
    margin-bottom: var(--spacing-sm);
  }
  
  .error-cause {
    color: var(--color-text-muted);
    font-size: var(--font-size-sm);
    margin-bottom: var(--spacing-sm);
  }
  
  .error-message {
    color: var(--color-text);
    margin-bottom: var(--spacing-md);
    font-size: var(--font-size-base);
  }
  
  .error-stack {
    margin-top: var(--spacing-md);
  }
  
  .error-stack summary {
    cursor: pointer;
    color: var(--color-text-muted);
    font-size: var(--font-size-sm);
    margin-bottom: var(--spacing-sm);
    user-select: none;
  }
  
  .error-stack pre {
    background-color: rgba(0, 0, 0, 0.2);
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
    overflow-x: auto;
    font-size: var(--font-size-xs);
    line-height: 1.5;
    margin: 0;
  }
  
  .error-pre {
    background-color: rgba(0, 0, 0, 0.2);
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
    overflow-x: auto;
    font-size: var(--font-size-sm);
    line-height: 1.5;
    margin: 0;
  }
  
  .retry-button {
    width: 100%;
  }
  
  @media (min-width: 640px) {
    .error-card {
      padding: var(--spacing-2xl);
    }
    
    .retry-button {
      width: auto;
      min-width: 140px;
    }
  }
  
  @media (prefers-color-scheme: light) {
    .error-stack pre,
    .error-pre {
      background-color: rgba(0, 0, 0, 0.05);
    }
  }
</style>
