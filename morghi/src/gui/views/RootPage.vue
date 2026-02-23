<script setup lang="ts">
import { InjectionKeys, type IGameListService } from '../../core/index.js'
import { inject, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const session = inject<{ value: import('../../core/models/Session.js').Session | null }>(InjectionKeys.session)!
const gameListService = inject<IGameListService>(InjectionKeys.gameListService)!
const router = useRouter()

onMounted(() => {
  if (!session.value) {
    router.replace({ name: 'auth' })
    return
  }
  const currentGame = gameListService.getCurrentGame()
  if (currentGame) {
    router.replace({ name: 'game', params: { id: currentGame.getGame().id } })
  } else {
    router.replace({ name: 'lobby' })
  }
})
</script>
<template>
  <div class="root-loading">Loading...</div>
</template>
<style scoped>
.root-loading {
  padding: 2rem;
  text-align: center;
}
</style>