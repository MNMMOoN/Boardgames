<script lang="ts">
    import api from "../core/api";
    import type { SSE } from "sse.js";
    import { SvelteMap } from "svelte/reactivity";
    import { AuthState, GameInfo, GameState, Message } from "../core/state";
    import { writable, type Writable } from "svelte/store";

    interface Props {
        auth: AuthState;
        game: GameInfo;
        onLeftGame: () => void;
    }
    let { auth, game, onLeftGame }: Props = $props();
    let pLoadGame: Promise<void> = $state(undefined!);
    let pSetPlayerReady: Promise<void> | null = $state(null);
    let pLeaveGame: Promise<void> | null = $state(null);

    class Player {
        public id: number = $state(0);
        public name: string = $state("");
        public ready: boolean = $state(false);
        public eggs: number = $state(0);
        public chickens: number = $state(0);
    }
    let players = new SvelteMap<number, Player>();
    let messages: Writable<Message[]> = writable([]);
    let playerEggs: number = $state(0);
    let playerChickens: number = $state(0);
    let playerReady: boolean = $state(false);
    let playerHand: Writable<string[]> = writable([]);

    function onSseState(data: any): void {
        data = JSON.parse(data["data"]);
        console.log("onSseState: ", data);
        let state = GameState.from_json(data);
        players.clear();
        state.players.forEach((p) => {
            players.set(p.id, p);
            if (p.id == auth.playerId) {
                playerEggs = p.eggs;
                playerChickens = p.chickens;
                playerReady = p.ready;
                playerHand.set(p.hand ?? []);
            }
        });
        messages.set(state.messages);
    }
    function onSseMessage(data: any): void {
        data = JSON.parse(data["data"]);
        console.log("onSseMessage: ", data);
        let message = Message.from_json(data);
        messages.update((ms) => ms.concat(message));
    }
    function onSsePlayerReady(data: any): void {
        data = JSON.parse(data["data"]);
        console.log("onSsePlayerReady: ", data);
        let playerId = data["player_id"];
        let player = players.get(playerId);
        if (player) {
            player.ready = true;
            players.set(playerId, player);
        }
        if (playerId == auth.playerId) {
            playerReady = true;
            pSetPlayerReady = null;
        }
    }
    function onSseGameStart(data: any): void {
        data = JSON.parse(data["data"]);
        console.log("onSseGameStart: ", data);
    }
    function onSseTurn(data: any): void {
        data = JSON.parse(data["data"]);
        console.log("onSseTurn: ", data);
    }
    function onSseHandChanged(data: any): void {
        data = JSON.parse(data["data"]);
        console.log("onSseHandChanged: ", data);
    }
    function onSseScoresChanged(data: any): void {
        data = JSON.parse(data["data"]);
        console.log("onSseScoresChanged: ", data);
    }

    let eventStream: SSE | null = $state(null);
    async function loadGame(): Promise<void> {
        eventStream?.close();
        eventStream = api.stream(
            `/games/${game.id}`,
            {
                state: onSseState,
                message: onSseMessage,
                player_ready: onSsePlayerReady,
                game_start: onSseGameStart,
                turn: onSseTurn,
                hand_changed: onSseHandChanged,
                scores_changed: onSseScoresChanged,
            },
            auth.token,
        );
    }
    async function leaveGame(): Promise<void> {
        await api.post(`/games/${game.id}/leave`, auth.token);
        eventStream?.close();
        onLeftGame();
    }
    pLoadGame = loadGame();

    function onBtnReadyClicked(): void {
        pSetPlayerReady = api.post(`/games/${game.id}/ready`, auth.token);
    }
    function onClickedLeaveGame(): void {
        pLeaveGame = leaveGame();
    }
</script>

<main>
    <h1>Game: {game.name}</h1>
    {#if pLeaveGame == null}
        {#await pLoadGame}
            <p>Loading ...</p>
        {:then}
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <p>Players:</p>
                    {#each players as [id, player] (id)}
                        <p>
                            {player.name}
                            {#if player.ready}
                                (Ready)
                            {:else if player.id === auth.playerId}
                                <button onclick={onBtnReadyClicked}>
                                    Set Ready
                                </button>
                            {:else}
                                (Not Ready)
                            {/if}
                        </p>
                    {/each}
                </div>
                <div>
                    <p>Messages:</p>
                    {#each $messages as message}
                        <p>{message.text}</p>
                    {/each}
                </div>
            </div>
            <button onclick={onClickedLeaveGame}>Leave Game</button>
        {:catch error: Error}
            <p>{error.name}</p>
            <p>{error.message}</p>
            <button onclick={() => (pLoadGame = loadGame())}>Try Again</button>
        {/await}
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
</main>
