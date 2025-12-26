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
</script>

<div class="container">
    <div class="table-wrapper">
        <table>
            <thead>
                <tr>
                    <td colspan="3">Players</td>
                </tr>
                <tr>
                    <td>Id</td>
                    <td>Name</td>
                    <td>Ready</td>
                </tr>
            </thead>
            <tbody>
                {#each game.players as [id, player] (id)}
                    <tr>
                        <td>{player.id}</td>
                        <td>{player.name}</td>
                        <td>
                            {#if player.ready}
                                (Ready)
                            {:else if player.id === auth.playerId}
                                {#await pSetPlayerReady}
                                    (Setting Ready ...)
                                {:then}
                                    <button onclick={onBtnReadyClicked}>
                                        Set Ready
                                    </button>
                                {:catch error: Error}
                                    ({error.name}: {error.message})
                                {/await}time
                            {:else}
                                (Not Ready)
                            {/if}
                        </td>
                    </tr>
                {/each}
            </tbody>
        </table>
    </div>
    <div class="table-wrapper">
        <table>
            <thead>
                <tr>
                    <td colspan="4">Messages</td>
                </tr>
                <tr>
                    <td>Time</td>
                    <td>Sender</td>
                    <td>Text</td>
                </tr>
            </thead>
            <tbody>
                {#each game.messages as message (message.id)}
                    <tr>
                        <td>
                            {message.time
                                .getHours()
                                .toString()
                                .padStart(
                                    2,
                                    "0",
                                )}:{message.time.getMinutes()}:{message.time.getSeconds()}
                        </td>
                        <td style="text-align: center;"
                            >{message.sender}</td
                        >
                        <td>{message.text}</td>
                    </tr>
                {/each}
            </tbody>
        </table>
    </div>
</div>

<style>
    .container {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        padding: 1rem;
    }
    .table-wrapper {
        overflow-x: auto;
        width: 100%;
    }
    table {
        width: 100%;
        border-collapse: collapse;
    }
    td {
        padding: 0.5rem;
        text-align: left;
    }
    button {
        padding: 0.5rem 1rem;
        font-size: 1rem;
    }
    @media (min-width: 768px) {
        .container {
            flex-direction: row;
            justify-content: space-between;
        }
        .table-wrapper {
            width: auto;
            flex: 1;
        }
    }
</style>
