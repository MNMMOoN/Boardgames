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

<main class="login-container">
    <div class="login-card">
        <h1>Welcome to Morghi</h1>
        {#await loggingIn}
            <div class="loading-state">
                <p class="loading-text">Logging in...</p>
            </div>
        {:then}
            <form class="login-form" onsubmit={(e) => { e.preventDefault(); loggingIn = login(); }}>
                <div class="form-group">
                    <label for="name">Player Name</label>
                    <input
                        id="name"
                        name="name"
                        type="text"
                        placeholder="Enter your name"
                        bind:value={playerName}
                        required
                        autocomplete="name"
                        autofocus
                    />
                </div>
                <button type="submit" class="login-button">
                    Login
                </button>
            </form>
        {:catch error: Error}
            <div class="error-state">
                <h4 class="error-title">{error.name}</h4>
                <p class="error-message">{error.message}</p>
                <button onclick={() => (loggingIn = Promise.resolve())} class="retry-button">
                    Try Again
                </button>
            </div>
        {/await}
    </div>
</main>

<style>
    .login-container {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        padding: var(--spacing-md);
    }
    
    .login-card {
        width: 100%;
        max-width: 400px;
        background-color: var(--color-surface);
        border-radius: var(--radius-lg);
        padding: var(--spacing-xl);
        box-shadow: var(--shadow-md);
        border: 1px solid var(--color-border);
    }
    
    .login-card h1 {
        text-align: center;
        margin-bottom: var(--spacing-xl);
        font-size: var(--font-size-3xl);
    }
    
    .login-form {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-lg);
    }
    
    .form-group {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-xs);
    }
    
    .login-button {
        width: 100%;
        margin-top: var(--spacing-sm);
    }
    
    .loading-state {
        text-align: center;
        padding: var(--spacing-xl) 0;
    }
    
    .loading-text {
        color: var(--color-text-muted);
        font-size: var(--font-size-lg);
    }
    
    .error-state {
        text-align: center;
    }
    
    .error-title {
        color: var(--color-error);
        margin-bottom: var(--spacing-sm);
    }
    
    .error-message {
        color: var(--color-text-muted);
        margin-bottom: var(--spacing-lg);
    }
    
    .retry-button {
        width: 100%;
    }
    
    @media (min-width: 640px) {
        .login-card {
            padding: var(--spacing-2xl);
        }
    }
</style>
