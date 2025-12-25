<script lang="ts">
  import { AuthState, GameInfo } from "./core/state";
  import GamePage from "./views/GamePage.svelte";
  import LoginPage from "./views/LoginPage.svelte";
  import PlayerPage from "./views/PlayerPage.svelte";
  let auth: AuthState | null = $state(AuthState.load());
  let game: GameInfo | null = $state(null);
</script>

{#if auth === null}
  <LoginPage bind:result={auth} />
{:else if game !== null}
  <GamePage {auth} {game} onLeftGame={() => (game = null)} />
{:else}
  <PlayerPage
    {auth}
    onClickedLogout={() => (auth = null)}
    onEnterGame={(g) => (game = g)}
  />
{/if}
