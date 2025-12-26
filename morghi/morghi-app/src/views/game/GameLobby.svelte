<script lang="ts">
    import api from "../../core/api";
    import auth from "../../services/auth.svelte";
    import type { Game } from "./Game.svelte";
    interface Props {
        game: Game;
    }
    let { game = $bindable() }: Props = $props();
    let pSetPlayerReady: Promise<void> = $state(Promise.resolve());
    function onBtnReadyClicked(): void {
        pSetPlayerReady = api.post(`/games/${game.id}/ready`, auth.token);
    }
    
    function formatTime(date: Date): string {
        const hours = date.getHours().toString().padStart(2, "0");
        const minutes = date.getMinutes().toString().padStart(2, "0");
        const seconds = date.getSeconds().toString().padStart(2, "0");
        return `${hours}:${minutes}:${seconds}`;
    }
</script>

<div class="lobby-container">
    <div class="section-card">
        <h3 class="section-title">Players</h3>
        <div class="table-wrapper">
            <table class="players-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th class="status-column">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {#each game.players as [id, player] (id)}
                        <tr class:current-player={player.id === auth.playerId}>
                            <td class="player-name">
                                {player.name}
                                {#if player.id === auth.playerId}
                                    <span class="you-badge">(You)</span>
                                {/if}
                            </td>
                            <td class="status-column">
                                {#if player.ready}
                                    <span class="ready-badge">Ready</span>
                                {:else if player.id === auth.playerId}
                                    {#await pSetPlayerReady}
                                        <span class="loading-badge">Setting Ready...</span>
                                    {:then}
                                        <button class="ready-button" onclick={onBtnReadyClicked}>
                                            Set Ready
                                        </button>
                                    {:catch error: Error}
                                        <div class="error-state">
                                            <span class="error-badge">{error.name}</span>
                                            <button class="ready-button" onclick={onBtnReadyClicked}>
                                                Retry
                                            </button>
                                        </div>
                                    {/await}
                                {:else}
                                    <span class="not-ready-badge">Not Ready</span>
                                {/if}
                            </td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="section-card">
        <h3 class="section-title">Messages</h3>
        <div class="messages-wrapper">
            {#if game.messages.length === 0}
                <div class="empty-messages">
                    <p>No messages yet</p>
                </div>
            {:else}
                <div class="messages-list">
                    {#each game.messages as message (message.id)}
                        <div class="message-item">
                            <div class="message-header">
                                <span class="message-sender">{message.sender}</span>
                                <span class="message-time">{formatTime(message.time)}</span>
                            </div>
                            <div class="message-text">{message.text}</div>
                        </div>
                    {/each}
                </div>
            {/if}
        </div>
    </div>
</div>

<style>
    .lobby-container {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-lg);
    }
    
    .section-card {
        background-color: var(--color-surface);
        border-radius: var(--radius-lg);
        padding: var(--spacing-lg);
        border: 1px solid var(--color-border);
    }
    
    .section-title {
        margin: 0 0 var(--spacing-md) 0;
        font-size: var(--font-size-xl);
        font-weight: 600;
    }
    
    .table-wrapper {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    
    .players-table {
        width: 100%;
    }
    
    .players-table th {
        padding: var(--spacing-sm) var(--spacing-md);
        font-size: var(--font-size-sm);
        font-weight: 600;
        text-align: left;
    }
    
    .players-table td {
        padding: var(--spacing-md);
        vertical-align: middle;
    }
    
    .current-player {
        background-color: rgba(100, 108, 255, 0.1);
    }
    
    .player-name {
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: var(--spacing-xs);
    }
    
    .you-badge {
        font-size: var(--font-size-xs);
        color: var(--color-text-muted);
        font-weight: normal;
    }
    
    .status-column {
        text-align: right;
        white-space: nowrap;
    }
    
    .ready-badge,
    .not-ready-badge,
    .loading-badge,
    .error-badge {
        display: inline-block;
        padding: var(--spacing-xs) var(--spacing-sm);
        border-radius: var(--radius-sm);
        font-size: var(--font-size-xs);
        font-weight: 500;
    }
    
    .ready-badge {
        background-color: rgba(34, 197, 94, 0.2);
        color: #4ade80;
    }
    
    .not-ready-badge {
        background-color: rgba(107, 114, 128, 0.2);
        color: #9ca3af;
    }
    
    .loading-badge {
        background-color: rgba(59, 130, 246, 0.2);
        color: #60a5fa;
    }
    
    .error-badge {
        background-color: rgba(239, 68, 68, 0.2);
        color: var(--color-error);
        display: block;
        margin-bottom: var(--spacing-xs);
    }
    
    .ready-button {
        padding: var(--spacing-xs) var(--spacing-md);
        font-size: var(--font-size-sm);
        min-height: auto;
    }
    
    .error-state {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-xs);
    }
    
    .messages-wrapper {
        max-height: 400px;
        overflow-y: auto;
        -webkit-overflow-scrolling: touch;
    }
    
    .empty-messages {
        text-align: center;
        padding: var(--spacing-xl) 0;
        color: var(--color-text-muted);
    }
    
    .messages-list {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-md);
    }
    
    .message-item {
        padding: var(--spacing-md);
        background-color: rgba(255, 255, 255, 0.02);
        border-radius: var(--radius-md);
        border: 1px solid var(--color-border);
    }
    
    .message-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--spacing-xs);
        gap: var(--spacing-sm);
    }
    
    .message-sender {
        font-weight: 600;
        font-size: var(--font-size-sm);
        color: var(--color-primary);
    }
    
    .message-time {
        font-size: var(--font-size-xs);
        color: var(--color-text-muted);
        white-space: nowrap;
    }
    
    .message-text {
        font-size: var(--font-size-sm);
        line-height: 1.5;
        word-wrap: break-word;
    }
    
    @media (min-width: 768px) {
        .lobby-container {
            flex-direction: row;
            align-items: flex-start;
        }
        
        .section-card {
            flex: 1;
        }
        
        .messages-wrapper {
            max-height: 500px;
        }
    }
    
    @media (prefers-color-scheme: light) {
        .current-player {
            background-color: rgba(100, 108, 255, 0.05);
        }
        
        .ready-badge {
            background-color: rgba(34, 197, 94, 0.1);
            color: #16a34a;
        }
        
        .not-ready-badge {
            background-color: rgba(107, 114, 128, 0.1);
            color: #6b7280;
        }
        
        .loading-badge {
            background-color: rgba(59, 130, 246, 0.1);
            color: #2563eb;
        }
        
        .message-item {
            background-color: rgba(0, 0, 0, 0.01);
        }
    }
</style>
