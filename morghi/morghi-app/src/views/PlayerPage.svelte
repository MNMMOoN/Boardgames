<script lang="ts">
    import { GameInfo } from "../core/state";
    import NewGame from "./player/NewGame.svelte";
    import ListOfGames from "./player/ListOfGames.svelte";
    import auth from "../services/auth.svelte";
    interface Props {
        onEnterGame: (game: GameInfo) => void;
    }

    let games: ListOfGames;
    let { onEnterGame }: Props = $props();
    function onNewGameCreated(): void {
        games.refresh();
    }
</script>

<header class="app-header">
    <h2 class="app-title">Morghi :3</h2>
    <button class="logout-button" onclick={() => auth.logout()}>Logout</button>
</header>

<main class="player-page">
    <h1 class="welcome-title">Hello {auth.playerName} :3</h1>
    <div class="content-section">
        <NewGame {onNewGameCreated} />
    </div>
    <div class="content-section">
        <ListOfGames bind:this={games} {onEnterGame} />
    </div>
</main>

<style>
    .app-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--spacing-md);
        background-color: var(--color-surface);
        border-bottom: 1px solid var(--color-border);
        position: sticky;
        top: 0;
        z-index: 10;
    }
    
    .app-title {
        margin: 0;
        font-size: var(--font-size-xl);
        font-weight: 600;
    }
    
    .logout-button {
        padding: var(--spacing-sm) var(--spacing-md);
        font-size: var(--font-size-sm);
        min-height: auto;
    }
    
    .player-page {
        padding: var(--spacing-md);
    }
    
    .welcome-title {
        text-align: center;
        margin-bottom: var(--spacing-xl);
        font-size: var(--font-size-2xl);
    }
    
    .content-section {
        margin-bottom: var(--spacing-xl);
    }
    
    .content-section:last-child {
        margin-bottom: 0;
    }
    
    @media (min-width: 640px) {
        .app-header {
            padding: var(--spacing-lg) var(--spacing-xl);
        }
        
        .app-title {
            font-size: var(--font-size-2xl);
        }
        
        .player-page {
            padding: var(--spacing-lg);
        }
        
        .welcome-title {
            font-size: var(--font-size-3xl);
        }
    }
    
    @media (min-width: 768px) {
        .player-page {
            padding: var(--spacing-xl);
        }
    }
</style>
