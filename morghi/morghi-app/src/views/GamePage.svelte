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

<main>
    {#if game == null || gameListener == null}
        <h1>Initializing</h1>
    {:else}
        <h1>Game: {gameInfo.name}</h1>
        {#if pLeaveGame == null}
            <div>
                <span>Game: {gameInfo.name}</span>
                <button onclick={onClickedLeaveGame}>Leave Game</button>
            </div>
            {#if game.isPlaying}
                <GameLobby bind:game />
            {:else}
                <GameLobby bind:game bind:this={lobby} />
            {/if}
        {:else}
            {#await pLeaveGame}
                <p>Leaving Game ...</p>
            {:then}
                <button onclick={onClickedLeaveGame}>Leave Game</button>
            {:catch error: Error}
                <p>{error.name}</p>
                <p>{error.message}</p>
                <button onclick={() => (pLeaveGame = null)}> Back </button>
            {/await}
        {/if}
    {/if}
</main>
