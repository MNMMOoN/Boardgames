<script lang="ts">
    import api from "../core/api";
    import { AuthState, GameInfo } from "../core/state";
    import NewGame from "./player/NewGame.svelte";
    import ListOfGames from "./player/ListOfGames.svelte";
    interface Props {
        auth: AuthState;
        onEnterGame: (game: GameInfo) => void;
        onClickedLogout: () => void;
    }
    let games: ListOfGames;
    let { auth, onEnterGame, onClickedLogout }: Props = $props();
    function onNewGameCreated(): void {
        games.refresh();
    }
</script>

<header style="display: flex; justify-content: space-between;">
    <p>Morghi :3</p>
    <button onclick={onClickedLogout}>Logout</button>
</header>

<main>
    <h1>Hallo {auth.playerName} :3</h1>
    <NewGame {auth} {onNewGameCreated} />
    <ListOfGames bind:this={games} {auth} {onEnterGame} />
</main>
