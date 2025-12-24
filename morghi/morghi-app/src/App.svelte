<script lang="ts">
  import { AuthState } from "./core/state.svelte";
  import LoginPage from "./pages/LoginPage.svelte";
  let auth: AuthState | null = $state(AuthState.load());
  const isLoggedIn: boolean = $derived(auth != null);
</script>

{#if isLoggedIn}
  <h1>Page</h1>
{:else}
  <LoginPage bind:auth />
{/if}
