<script lang="ts">
    import api from "../core/api";
    import auth from "../services/auth.svelte";
    let playerName: string = $state("");
    async function login(): Promise<void> {
        auth.login_from_json(
            await api.post("/login", null, { name: playerName }),
        );
    }
    let loggingIn: Promise<void> = $state(Promise.resolve());
</script>

<main>
    {#await loggingIn}
        <h4>Logging In ...</h4>
    {:then}
        <div>
            <label for="name">Name:</label>
            <input
                name="name"
                placeholder="Enter your Name"
                bind:value={playerName}
            />
        </div>
        <button style="margin: 8px;" onclick={() => (loggingIn = login())}>
            Login
        </button>
    {:catch error: Error}
        <h4>{error.name}</h4>
        <p>{error.message}</p>
        <button onclick={() => (loggingIn = Promise.resolve())}>Retry</button>
    {/await}
</main>
