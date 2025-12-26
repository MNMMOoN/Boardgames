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
    <div>
      {#if error === null}
        <p>Something went wrong ...</p>
      {:else if error instanceof Error}
        <h1>{error.name}</h1>
        <h4>{error.cause}</h4>
        <p>{error.message}</p>
        <pre>{error.stack}</pre>
      {:else}
        <pre>{error}</pre>
      {/if}
      <button onclick={retry}>Retry</button>
    </div>
  {/snippet}
</svelte:boundary>
