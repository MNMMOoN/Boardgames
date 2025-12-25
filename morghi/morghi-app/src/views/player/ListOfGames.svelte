<script lang="ts">
    import api from "../../core/api";
    import { AuthState, GameInfo } from "../../core/state";
    interface Props {
        auth: AuthState;
        onEnterGame: (game: GameInfo) => void;
    }
    let { auth, onEnterGame }: Props = $props();
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
        let response: {} = await api.post(
            "/games/" + game.id + "/join",
            auth.token,
        );
        onEnterGame(game);
    }
</script>

<div>
    {#await pListingGames}
        <p>Loading Games ...</p>
    {:then result}
        {#each result as game}
            <div
                style="display: flex; justify-content: center; align-items: center;"
            >
                <p style="padding: 8px 16px;">{game.name}</p>
                <button onclick={() => joinGame(game)}>Join</button>
            </div>
        {/each}
    {:catch error: Error}
        <p>{error.name}</p>
        <p>{error.message}</p>
        <button onclick={refresh}>Retry</button>
    {/await}
</div>
