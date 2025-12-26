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
        gameName = "";
        onNewGameCreated();
    }
    function onBtnCreateGameClicked(): void {
        pCreatingGame = CreateGame();
    }
</script>

<div class="new-game-card">
    <h3 class="section-title">Create New Game</h3>
    {#await pCreatingGame}
        <div class="loading-state">
            <p class="loading-text">Creating game...</p>
        </div>
    {:then}
        <form class="new-game-form" onsubmit={(e) => { e.preventDefault(); onBtnCreateGameClicked(); }}>
            <div class="form-group">
                <label for="game-name">Game Name</label>
                <input
                    id="game-name"
                    name="name"
                    type="text"
                    placeholder="Enter game name"
                    required
                    bind:value={gameName}
                />
            </div>
            <button type="submit" class="create-button">
                Create Game
            </button>
        </form>
    {:catch x: Error}
        <div class="error-message">
            <p class="error-text">{x.name}: {x.message}</p>
        </div>
        <form class="new-game-form" onsubmit={(e) => { e.preventDefault(); onBtnCreateGameClicked(); }}>
            <div class="form-group">
                <label for="game-name">Game Name</label>
                <input
                    id="game-name"
                    name="name"
                    type="text"
                    placeholder="Enter game name"
                    required
                    bind:value={gameName}
                />
            </div>
            <button type="submit" class="create-button">
                Create Game
            </button>
        </form>
    {/await}
</div>

<style>
    .new-game-card {
        background-color: var(--color-surface);
        border-radius: var(--radius-lg);
        padding: var(--spacing-lg);
        border: 1px solid var(--color-border);
        margin-bottom: var(--spacing-lg);
    }
    
    .section-title {
        margin-bottom: var(--spacing-md);
        font-size: var(--font-size-xl);
    }
    
    .new-game-form {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-md);
    }
    
    .form-group {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-xs);
    }
    
    .create-button {
        width: 100%;
    }
    
    .loading-state {
        text-align: center;
        padding: var(--spacing-md) 0;
    }
    
    .loading-text {
        color: var(--color-text-muted);
    }
    
    .error-message {
        margin-bottom: var(--spacing-md);
    }
    
    .error-text {
        color: var(--color-error);
        font-size: var(--font-size-sm);
        margin: 0;
    }
    
    @media (min-width: 640px) {
        .new-game-card {
            padding: var(--spacing-xl);
        }
        
        .new-game-form {
            flex-direction: row;
            align-items: flex-end;
            gap: var(--spacing-md);
        }
        
        .form-group {
            flex: 1;
        }
        
        .create-button {
            width: auto;
            min-width: 140px;
        }
    }
</style>
