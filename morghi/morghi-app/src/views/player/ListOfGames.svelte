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

<div>
    {#await pListingGames}
        <p>Loading Games ...</p>
    {:then result}
        <table>
            <thead>
                <tr>
                    <th style="min-width: 64px;">Id</th>
                    <th style="min-width: 64px;">Name</th>
                    <th style="min-width: 64px;">Players</th>
                    <th style="min-width: 64px;">Status</th>
                    <th style="min-width: 64px;"></th>
                </tr>
            </thead>
            <tbody>
                {#each result as game}
                    <tr>
                        <td>{game.id}</td>
                        <td>{game.name}</td>
                        <td>{game.players.length} / {game.capacity}</td>
                        <td>{game.status}</td>
                        <td>
                            {#if !game.isStarted}
                                <button onclick={() => joinGame(game)}>
                                    Join
                                </button>
                            {/if}
                        </td>
                    </tr>
                {/each}
            </tbody>
        </table>
    {:catch error: Error}
        <p>{error.name}</p>
        <p>{error.message}</p>
        <button onclick={refresh}>Retry</button>
    {/await}
</div>
