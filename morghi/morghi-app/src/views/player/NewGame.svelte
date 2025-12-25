<script lang="ts">
    import api from "../../core/api";
    import { AuthState } from "../../core/state";
    interface Props {
        auth: AuthState;
        onNewGameCreated: () => void;
    }
    let { auth, onNewGameCreated }: Props = $props();
    let gameName: string = $state("");
    let pCreatingGame: Promise<void> = $state(Promise.resolve());
    async function CreateGame(): Promise<void> {
        await api.post("/games", auth.token, { name: gameName });
        onNewGameCreated();
    }
    function onBtnCreateGameClicked(): void {
        pCreatingGame = CreateGame();
    }
</script>

{#snippet content()}
    <div>
        <label for="name">Create Game:</label>
        <input
            name="name"
            placeholder="Enter a name for the new game"
            bind:value={gameName}
        />
    </div>
    <button style="margin: 8px;" onclick={onBtnCreateGameClicked}>
        Create Game
    </button>
{/snippet}
<div>
    {#await pCreatingGame}
        <p>Creating Game</p>
    {:then}
        {@render content()}
    {:catch}
        <p style="color: red;">Failed to create game</p>
        {@render content()}
    {/await}
</div>
