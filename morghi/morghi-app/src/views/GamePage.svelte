<script lang="ts" module>
    let game: Game | null = $state(null);
    let gameListener: GameEventsListener | null = $state(null);
    function initGame(info: GameInfo) {
        if (game == null || gameListener == null) {
            game = new Game(info);
            gameListener = new GameEventsListener(game);
            gameListener.openStream();
        }
    }
</script>

<script lang="ts">
    import api from "../core/api";
    import { GameInfo } from "../core/state";
    import GameLobby from "./game/GameLobby.svelte";
    import { Game } from "./game/Game.svelte";
    import { GameEventsListener } from "./game/GameEventsListener.svelte";
    import auth from "../services/auth.svelte";

    interface Props {
        gameInfo: GameInfo;
        onLeftGame: () => void;
    }
    let { gameInfo, onLeftGame }: Props = $props();
    let pLeaveGame: Promise<void> | null = $state(null);
    let lobby: GameLobby = $state(undefined!);

    async function leaveGame(): Promise<void> {
        await api.post(`/games/${gameInfo.id}/leave`, auth.token);
        gameListener?.closeStream();
        onLeftGame();
    }
    function onClickedLeaveGame(): void {
        pLeaveGame = leaveGame();
    }
    $effect(() => {
        initGame(gameInfo);
    });
</script>

<main class="game-page">
    {#if game == null || gameListener == null}
        <div class="loading-state">
            <h1>Initializing Game...</h1>
            <p class="loading-text">Please wait while we set up your game.</p>
        </div>
    {:else}
        <header class="game-header">
            <div class="game-header-content">
                <h1 class="game-title">{gameInfo.name}</h1>
                {#if pLeaveGame == null}
                    <button class="leave-button" onclick={onClickedLeaveGame}>
                        Leave Game
                    </button>
                {:else}
                    {#await pLeaveGame}
                        <button class="leave-button" disabled>
                            Leaving...
                        </button>
                    {:then}
                        <button class="leave-button" onclick={onClickedLeaveGame}>
                            Leave Game
                        </button>
                    {:catch error: Error}
                        <div class="error-state">
                            <p class="error-text">{error.name}: {error.message}</p>
                            <button class="back-button" onclick={() => (pLeaveGame = null)}>
                                Back
                            </button>
                        </div>
                    {/await}
                {/if}
            </div>
        </header>
        
        <div class="game-content">
            {#if pLeaveGame == null}
                <GameLobby bind:game bind:this={lobby} />
            {/if}
        </div>
    {/if}
</main>

<style>
    .game-page {
        padding: 0;
        max-width: 100%;
    }
    
    .loading-state {
        text-align: center;
        padding: var(--spacing-2xl) var(--spacing-md);
    }
    
    .loading-text {
        color: var(--color-text-muted);
        margin-top: var(--spacing-md);
    }
    
    .game-header {
        background-color: var(--color-surface);
        border-bottom: 1px solid var(--color-border);
        padding: var(--spacing-md);
        position: sticky;
        top: 0;
        z-index: 10;
    }
    
    .game-header-content {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-md);
        align-items: flex-start;
    }
    
    .game-title {
        margin: 0;
        font-size: var(--font-size-2xl);
        flex: 1;
    }
    
    .leave-button {
        width: 100%;
        background-color: rgba(239, 68, 68, 0.1);
        border-color: rgba(239, 68, 68, 0.3);
        color: var(--color-error);
    }
    
    .leave-button:hover:not(:disabled) {
        background-color: rgba(239, 68, 68, 0.2);
        border-color: var(--color-error);
    }
    
    .error-state {
        width: 100%;
        text-align: center;
    }
    
    .error-text {
        color: var(--color-error);
        font-size: var(--font-size-sm);
        margin-bottom: var(--spacing-sm);
    }
    
    .back-button {
        width: 100%;
    }
    
    .game-content {
        padding: var(--spacing-md);
    }
    
    @media (min-width: 640px) {
        .game-header {
            padding: var(--spacing-lg) var(--spacing-xl);
        }
        
        .game-header-content {
            flex-direction: row;
            align-items: center;
            justify-content: space-between;
        }
        
        .game-title {
            font-size: var(--font-size-3xl);
        }
        
        .leave-button {
            width: auto;
            min-width: 140px;
        }
        
        .game-content {
            padding: var(--spacing-lg);
        }
    }
    
    @media (min-width: 768px) {
        .game-content {
            padding: var(--spacing-xl);
        }
    }
</style>
