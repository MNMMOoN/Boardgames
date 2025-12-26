<script lang="ts">
    import api from "../../core/api";
    import auth from "../../services/auth.svelte";
    interface Props {
        onNewGameCreated: () => void;
    }

    let { onNewGameCreated }: Props = $props();
    let gameName: string = $state("");
    let pCreatingGame: Promise<void> = $state(Promise.resolve());
    async function CreateGame(): Promise<void> {
        await Promise.resolve();
        if (gameName === "") {
            throw new Error("Game name cannot be empty");
        }
        await api.post("/games", auth.token, { name: gameName });
        onNewGameCreated();
    }
    function onBtnCreateGameClicked(): void {
        pCreatingGame = CreateGame();
    }
</script>

{#snippet content()}
    <div
        style:display="flex"
        style:justify-content="space-between"
        style:align-items="center"
    >
        <label for="name">Create Game:</label>
        <input
            name="name"
            type="text"
            placeholder="Name the new game"
            style:padding="4px"
            style:margin="2px 16px"
            required
            bind:value={gameName}
        />
        <button style="margin: 8px;" onclick={onBtnCreateGameClicked}>
            Create Game
        </button>
    </div>
{/snippet}
<div>
    {#await pCreatingGame}
        <p>Creating Game</p>
    {:then}
        {@render content()}
    {:catch x: Error}
        <p style="color: red;">{x.name}: {x.message}</p>
        {@render content()}
    {/await}
</div>
