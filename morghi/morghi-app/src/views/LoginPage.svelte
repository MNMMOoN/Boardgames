<script lang="ts">
    import api from "../core/api";
    import { AuthState } from "../core/state";
    let { result = $bindable() }: { result: AuthState | null } = $props();
    let name: string = $state("");
    let loggingIn: Promise<any> | null = $state(null);

    async function onBtnLoginClicked(): Promise<void> {
        loggingIn = api.post("/login", null, { name: name });
        try {
            let r = await loggingIn;
            let auth = AuthState.from_json(r);
            auth.save();
            result = auth;
        } catch (e) {
            console.error(e);
        }
    }
</script>

<main>
    {#if result !== null}
        <h4>Welcome {result.playerName}</h4>
    {/if}
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
