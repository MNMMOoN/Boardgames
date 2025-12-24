<script lang="ts">
    import { api } from "../core/api";
    import { AuthState } from "../core/state.svelte";
    let { auth = $bindable() }: { auth: AuthState | null } = $props();
    let name: string = $state("");
    let loggingIn: Promise<any> | null = $state(null);
    async function onBtnLoginClicked(): Promise<void> {
        loggingIn = api
            .fetchPost("/login", null, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: {
                    name: name,
                },
            })
            .then((r) => {
                console.log(r);
                try {
                    auth = AuthState.from_json(r);
                    auth.save();
                } catch (e) {
                    console.error(e);
                }
            })
            .catch((x) => {
                console.error(x);
            });
    }
</script>

<main>
    {#if loggingIn === null}
        <div>
            <label for="name">Name:</label>
            <input
                name="name"
                placeholder="Enter your Name"
                bind:value={name}
            />
        </div>
        <button style="margin: 8px;" onclick={onBtnLoginClicked}>Login</button>
    {:else}
        {#await loggingIn}
            <h4>Logging In ...</h4>
        {:then result}
            <h4>Logged In</h4>
            <p>{result}</p>
        {:catch error: Error}
            <h4>{error.name}</h4>
            <p>{error.message}</p>
            <button
                onclick={() => {
                    console.error(error);
                    loggingIn = null;
                }}>Retry</button
            >
        {/await}
    {/if}
</main>
