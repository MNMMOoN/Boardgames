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

<header style="display: flex; justify-content: space-between;">
    <p>Morghi :3</p>
    <button onclick={() => auth.logout()}>Logout</button>
</header>

<main>
    <h1>Hallo {auth.playerName} :3</h1>
    <NewGame {onNewGameCreated} />
    <ListOfGames bind:this={games} {onEnterGame} />
</main>
