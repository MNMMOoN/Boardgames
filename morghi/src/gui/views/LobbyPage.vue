<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { InjectionKeys, type IGameListService } from '../../core/index.js'
import { inject } from 'vue'

const gameListService = inject<IGameListService>(InjectionKeys.gameListService)!
const router = useRouter()
const games = ref(gameListService.getGames())
const newGameName = ref('')
const creating = ref(false)
const joining = ref<string | null>(null)
const error = ref<string | null>(null)

function onListUpdate(list: ReturnType<IGameListService['getGames']>) {
  games.value = list
}

onMounted(() => {
  gameListService.onGamesListUpdated.addListener(onListUpdate)
})
onUnmounted(() => {
  gameListService.onGamesListUpdated.delListener(onListUpdate)
})

async function createGame() {
  if (!newGameName.value.trim()) return
  creating.value = true
  error.value = null
  try {
    await gameListService.newGame(newGameName.value.trim())
    const current = gameListService.getCurrentGame()
    if (current) {
      router.push({ name: 'game', params: { id: current.getGame().id } })
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    creating.value = false
  }
}

async function joinGame(id: string) {
  joining.value = id
  error.value = null
  try {
    const playService = await gameListService.joinGame(id)
    router.push({ name: 'game', params: { id: playService.getGame().id } })
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    joining.value = null
  }
}
</script>
<template>
  <div class="lobby-page">
    <h1>Lobby</h1>
    <div class="create-section">
      <input v-model="newGameName" placeholder="Game name" />
      <button @click="createGame" :disabled="creating">Create Game</button>
    </div>
    <div v-if="error" class="error">{{ error }}</div>
    <div class="games-list">
      <h2>Games</h2>
      <div v-if="games.length === 0" class="empty">No games yet. Create one!</div>
      <div v-else class="game-rows">
        <div v-for="g in games" :key="g.id" class="game-row">
          <span class="game-name">{{ g.name }}</span>
          <span class="game-state">{{ g.state }}</span>
          <button
                  @click="joinGame(g.id)"
                  :disabled="joining === g.id">
            {{ joining === g.id ? 'Joining...' : 'Join' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
<style scoped>
.lobby-page {
  padding: 2rem;
  max-width: 600px;
  margin: 0 auto;
}
.create-section {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.create-section input {
  flex: 1;
  padding: 0.5rem;
}
.games-list h2 {
  font-size: 1rem;
  margin: 1.5rem 0 0.5rem;
}
.empty {
  color: #888;
  padding: 1rem;
}
.game-rows {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.game-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}
.game-name {
  flex: 1;
}
.game-state {
  color: #888;
  font-size: 0.875rem;
}
.error {
  color: #f87171;
  margin-bottom: 0.5rem;
}
</style>