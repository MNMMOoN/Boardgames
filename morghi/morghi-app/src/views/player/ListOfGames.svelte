<script lang="ts">
    import api from "../../core/api";
    import { GameInfo, GameState } from "../../core/state";
    import auth from "../../services/auth.svelte";
    interface Props {
        onEnterGame: (game: GameInfo) => void;
    }
    let { onEnterGame }: Props = $props();
    async function getListOfGames(): Promise<GameInfo[]> {
        let games: GameInfo[] = [];
        try {
            let response: { games: GameInfo[] } = await api.get(
                "/games",
                auth.token,
            );
            games = response.games;
        } catch (x) {
            console.error(x);
            throw x;
        }
        for (let game of games) {
            for (let pId of game.players) {
                if (pId === auth.playerId) {
                    onEnterGame(game);
                    throw new Error(`Already in game '${game.name}'`);
                }
            }
        }
        return games;
    }
    let pListingGames: Promise<GameInfo[]> = $state(getListOfGames());
    export function refresh() {
        pListingGames = getListOfGames();
    }
    async function joinGame(game: GameInfo): Promise<void> {
        await api.post("/games/" + game.id + "/join", auth.token);
        onEnterGame(game);
    }
</script>

<div class="games-list-container">
    <h3 class="section-title">Available Games</h3>
    {#await pListingGames}
        <div class="loading-state">
            <p class="loading-text">Loading games...</p>
        </div>
    {:then result}
        {#if result.length === 0}
            <div class="empty-state">
                <p class="empty-text">No games available. Create one to get started!</p>
            </div>
        {:else}
            <div class="table-wrapper">
                <table class="games-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Players</th>
                            <th>Status</th>
                            <th class="action-column"></th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each result as game}
                            <tr>
                                <td class="game-name" data-label="Name">{game.name}</td>
                                <td data-label="Players">{game.players.length} / {game.capacity}</td>
                                <td data-label="Status">
                                    <span class="status-badge status-{game.status.toLowerCase()}">
                                        {game.status}
                                    </span>
                                </td>
                                <td class="action-column" data-label="">
                                    {#if !game.isStarted}
                                        <button class="join-button" onclick={() => joinGame(game)}>
                                            Join
                                        </button>
                                    {:else}
                                        <span class="started-badge">Started</span>
                                    {/if}
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        {/if}
    {:catch error: Error}
        <div class="error-state">
            <h4 class="error-title">{error.name}</h4>
            <p class="error-message">{error.message}</p>
            <button class="retry-button" onclick={refresh}>Retry</button>
        </div>
    {/await}
</div>

<style>
    .games-list-container {
        background-color: var(--color-surface);
        border-radius: var(--radius-lg);
        padding: var(--spacing-lg);
        border: 1px solid var(--color-border);
    }
    
    .section-title {
        margin-bottom: var(--spacing-md);
        font-size: var(--font-size-xl);
    }
    
    .loading-state {
        text-align: center;
        padding: var(--spacing-xl) 0;
    }
    
    .loading-text {
        color: var(--color-text-muted);
    }
    
    .empty-state {
        text-align: center;
        padding: var(--spacing-xl) 0;
    }
    
    .empty-text {
        color: var(--color-text-muted);
    }
    
    .table-wrapper {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    
    .games-table {
        width: 100%;
        min-width: 100%;
    }
    
    .game-name {
        font-weight: 500;
    }
    
    .status-badge {
        display: inline-block;
        padding: var(--spacing-xs) var(--spacing-sm);
        border-radius: var(--radius-sm);
        font-size: var(--font-size-xs);
        font-weight: 500;
        text-transform: capitalize;
    }
    
    .status-waiting {
        background-color: rgba(59, 130, 246, 0.2);
        color: #60a5fa;
    }
    
    .status-playing {
        background-color: rgba(34, 197, 94, 0.2);
        color: #4ade80;
    }
    
    .status-finished {
        background-color: rgba(107, 114, 128, 0.2);
        color: #9ca3af;
    }
    
    .started-badge {
        color: var(--color-text-muted);
        font-size: var(--font-size-xs);
    }
    
    .join-button {
        padding: var(--spacing-xs) var(--spacing-md);
        font-size: var(--font-size-sm);
        min-height: auto;
    }
    
    .action-column {
        text-align: right;
        white-space: nowrap;
    }
    
    .error-state {
        text-align: center;
        padding: var(--spacing-lg) 0;
    }
    
    .error-title {
        color: var(--color-error);
        margin-bottom: var(--spacing-sm);
    }
    
    .error-message {
        color: var(--color-text-muted);
        margin-bottom: var(--spacing-md);
    }
    
    .retry-button {
        width: 100%;
        max-width: 200px;
    }
    
    /* Mobile-first: Stack table rows as cards */
    @media (max-width: 639px) {
        .games-table,
        .games-table thead,
        .games-table tbody,
        .games-table th,
        .games-table td,
        .games-table tr {
            display: block;
        }
        
        .games-table thead tr {
            position: absolute;
            top: -9999px;
            left: -9999px;
        }
        
        .games-table tr {
            border: 1px solid var(--color-border);
            border-radius: var(--radius-md);
            margin-bottom: var(--spacing-md);
            padding: var(--spacing-md);
            background-color: rgba(255, 255, 255, 0.02);
        }
        
        .games-table td {
            border: none;
            position: relative;
            padding: var(--spacing-sm) var(--spacing-sm) var(--spacing-sm) 40%;
            text-align: right;
        }
        
        .games-table td:before {
            content: attr(data-label);
            position: absolute;
            left: var(--spacing-sm);
            width: 35%;
            text-align: left;
            font-weight: 600;
            color: var(--color-text-muted);
        }
        
        .games-table td.action-column {
            padding-left: var(--spacing-sm);
            text-align: left;
        }
        
        .games-table td.action-column:before {
            display: none;
        }
    }
    
    @media (min-width: 640px) {
        .games-list-container {
            padding: var(--spacing-xl);
        }
        
        .retry-button {
            width: auto;
        }
    }
    
    @media (prefers-color-scheme: light) {
        .status-waiting {
            background-color: rgba(59, 130, 246, 0.1);
            color: #2563eb;
        }
        
        .status-playing {
            background-color: rgba(34, 197, 94, 0.1);
            color: #16a34a;
        }
        
        .status-finished {
            background-color: rgba(107, 114, 128, 0.1);
            color: #6b7280;
        }
        
        .games-table tr {
            background-color: rgba(0, 0, 0, 0.01);
        }
    }
</style>
