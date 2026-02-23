<script setup lang="ts">
import {
  ANIMAL_CARDS,
  Card as CardEnum,
  GameActionType,
  InjectionKeys,
  type Card,
  type Game,
  type GameAction,
  type IGameListService,
  type Session,
} from '../../core/index.js'
import { inject, ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GameHand from '../components/GameHand.vue'
import GameChat from '../components/GameChat.vue'

const gameListService = inject<IGameListService>(InjectionKeys.gameListService)!
const session = inject<{ value: Session | null }>(InjectionKeys.session)!
const route = useRoute()
const router = useRouter()
const gameId = route.params.id as string

const game = ref<Game | null>(null)
const hand = ref<Card[]>([])
const selectedCards = ref<Card[]>([])
const actionTarget = ref<string | null>(null)
const actionEggCount = ref(1)
const error = ref<string | null>(null)
const executing = ref(false)
let pendingInterval: ReturnType<typeof setInterval> | null = null

const gamePlayService = computed(() => gameListService.getCurrentGame())

const isMyTurn = computed(() => {
  const g = game.value
  const s = session.value
  if (!g || !s) return false
  return g.currentPlayer === s.userId
})

const isLobby = computed(() => game.value?.state === 'lobby')

const winner = computed(() => {
  const g = game.value
  if (!g || g.state !== 'finished') return null
  const withChickens = g.players.filter((p) => p.chickens >= 3)
  if (withChickens.length > 0) return withChickens[0]?.name ?? null
  return g.players.length === 1 ? g.players[0]?.name ?? null : null
})

const pendingTick = ref(0)
const pendingSecondsLeft = computed(() => {
  const p = pendingForMe.value?.action
  void pendingTick.value
  if (!p?.timeout) return null
  const end = new Date(p.timeout).getTime()
  return Math.max(0, Math.ceil((end - Date.now()) / 1000))
})

const canStart = computed(() => {
  const g = game.value
  if (!g || g.state !== 'lobby') return false
  const allReady = g.players.every((p) => p.ready)
  const enough = g.players.length >= 2
  return allReady && enough
})

const pendingForMe = computed(() => {
  const g = game.value
  const s = session.value
  if (!g?.pending || !s) return null
  const p = g.pending
  if (p.action.type === 'FoxSteal' && 'target' in (p.action.params ?? {})) {
    const targetId = (p.action.params as { target: { id: string } }).target.id
    if (targetId === s.userId) return { type: 'defend', action: p }
  }
  if (p.action.type === 'TrapKill' && p.action.actor.id === s.userId) {
    return { type: 'trap', action: p }
  }
  return null
})

const validAction = computed(() => {
  const g = game.value
  const s = session.value
  if (!g || !s || g.state !== 'playing') return null
  if (!isMyTurn.value && !pendingForMe.value) return null

  const sel = selectedCards.value
  const myId = s.userId

  if (pendingForMe.value?.type === 'defend') {
    const hasTwoRoosters =
      hand.value.filter((c) => c === CardEnum.Rooster).length >= 2
    return { type: 'DefendFoxSteal', defend: hasTwoRoosters && sel.length === 2 }
  }

  if (pendingForMe.value?.type === 'trap') {
    const lastResp = pendingForMe.value.action.lastResponse
    const targetHand = lastResp?.params?.targetHand ?? []
    const animals = targetHand.filter((c: Card) => ANIMAL_CARDS.includes(c))
    if (animals.length > 0) {
      const c = sel[0]
      if (sel.length === 1 && c && ANIMAL_CARDS.includes(c))
        return { type: 'TrapKill', finish: true, card: c }
    } else {
      return { type: 'TrapKill', finish: true, card: null }
    }
    return null
  }

  if (!isMyTurn.value) return null

  if (sel.length === 3) {
    const has =
      sel.includes(CardEnum.Hen) &&
      sel.includes(CardEnum.Rooster) &&
      sel.includes(CardEnum.Nest)
    if (has) return { type: 'LayEgg' }
  }
  if (sel.length === 2 && sel.every((c) => c === CardEnum.Hen)) {
    const me = g.players.find((p) => p.id === myId)
    if (me && me.eggs >= 1) return { type: 'HatchEgg' }
  }
  if (sel.length === 1 && sel[0] === CardEnum.Fox) {
    const withEggs = g.players.filter((p) => p.id !== myId && p.eggs >= 1)
    if (withEggs.length > 0 && actionTarget.value)
      return { type: 'FoxSteal', targetId: actionTarget.value }
  }
  if (sel.length === 1 && sel[0] === CardEnum.Snake) {
    const withEggs = g.players.filter((p) => p.id !== myId && p.eggs >= 1)
    if (withEggs.length > 0 && actionTarget.value)
      return {
        type: 'SnakeEat',
        targetId: actionTarget.value,
        eggCount: actionEggCount.value,
      }
  }
  if (sel.length === 1 && sel[0] === CardEnum.Trap && actionTarget.value) {
    return { type: 'TrapKill', targetId: actionTarget.value }
  }
  if (sel.length === 1 && isMyTurn.value) {
    return { type: 'SkipTurn' }
  }
  return null
})

function onGameUpdate(g: unknown) {
  game.value = g as Game
}
function onHandUpdate(h: unknown) {
  hand.value = h as Card[]
}

function toggleCard(card: Card) {
  const idx = selectedCards.value.indexOf(card)
  if (idx >= 0) {
    selectedCards.value = selectedCards.value.filter((_, i) => i !== idx)
  } else {
    selectedCards.value = [...selectedCards.value, card]
  }
}

async function execute() {
  const act = validAction.value
  if (!act || !gamePlayService.value || executing.value) return

  executing.value = true
  error.value = null
  try {
    const g = game.value!
    const s = session.value!

    if (act.type === 'DefendFoxSteal') {
      const cards = act.defend ? [CardEnum.Rooster, CardEnum.Rooster] : []
      await gamePlayService.value.executeAction({
        type: GameActionType.DefendFoxSteal,
        actor: g.players.find((p) => p.id === g.currentPlayer)!,
        cards,
        params: null,
      })
    } else if (act.type === 'TrapKill') {
      const targetId = (pendingForMe.value!.action.action.params as { target: { id: string } })?.target?.id
      await gamePlayService.value.executeAction({
        type: GameActionType.TrapKill,
        actor: g.players.find((p) => p.id === s.userId)!,
        cards: act.card ? [act.card] : [],
        params: {
          target: g.players.find((p) => p.id === targetId)!,
          finish: true,
          card: act.card ?? null,
        },
      })
    } else {
      const actor = g.players.find((p) => p.id === s.userId)!
      let params = null
      if (act.type === 'FoxSteal' && act.targetId) {
        params = { target: g.players.find((p) => p.id === act.targetId)! }
      }
      if (act.type === 'SnakeEat' && act.targetId) {
        params = {
          target: g.players.find((p) => p.id === act.targetId)!,
          eggCount: act.eggCount,
        }
      }
      if (act.type === 'TrapKill' && act.targetId) {
        params = {
          target: g.players.find((p) => p.id === act.targetId)!,
          finish: false,
          card: null,
        }
      }

      await gamePlayService.value.executeAction({
        type: act.type as GameAction['type'],
        actor,
        cards: selectedCards.value,
        params,
      })
    }
    selectedCards.value = []
    actionTarget.value = null
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    executing.value = false
  }
}

async function sendChat(text: string) {
  await gamePlayService.value?.sendMessage?.(text)
}

async function setReady() {
  await gamePlayService.value?.setReady?.()
}

async function startGame() {
  await gamePlayService.value?.startGame?.()
}

async function leave() {
  await gamePlayService.value?.leave?.()
  router.replace({ name: 'lobby' })
}

onMounted(() => {
  const svc = gameListService.getCurrentGame()
  if (!svc || svc.getGame().id !== gameId) {
    router.replace({ name: 'lobby' })
    return
  }
  game.value = svc.getGame()
  hand.value = svc.getHand()
  svc.onGameUpdated.addListener(onGameUpdate)
  svc.onHandChanged.addListener(onHandUpdate)

  pendingInterval = setInterval(() => {
    if (pendingForMe.value) pendingTick.value++
  }, 1000)
})

onUnmounted(() => {
  if (pendingInterval) clearInterval(pendingInterval)
  const svc = gameListService.getCurrentGame()
  if (svc) {
    svc.onGameUpdated.delListener(onGameUpdate)
    svc.onHandChanged.delListener(onHandUpdate)
  }
})
</script>
<template>
  <div class="game-page">
    <div class="header">
      <h1 v-if="game">{{ game.name }}</h1>
      <span v-if="game" class="state">{{ game.state }}</span>
      <button class="leave" @click="leave">Leave Game</button>
    </div>
    <div class="players" v-if="game">
      <div
           v-for="p in game.players"
           :key="p.id"
           class="player"
           :class="{
            current: game.currentPlayer === p.id,
            'has-eggs': p.eggs > 0 && game.state === 'playing',
          }">
        {{ p.name }}: {{ p.eggs }} eggs, {{ p.chickens }} chickens
        <span v-if="game.currentPlayer === p.id" class="turn-badge">TURN</span>
        <span v-if="isLobby" class="ready">{{ p.ready ? 'Ready' : '' }}</span>
      </div>
    </div>
    <div v-if="winner" class="win-banner">
      {{ winner }} wins!
    </div>
    <div v-if="pendingForMe?.type === 'defend'" class="pending-banner">
      {{ pendingForMe.action.action.actor.name }} is trying to steal your egg!
      Defend with 2 Roosters?
      <span v-if="pendingSecondsLeft !== null" class="timeout">({{ pendingSecondsLeft }}s)</span>
    </div>
    <div v-if="pendingForMe?.type === 'trap'" class="pending-banner">
      Select an animal to kill from their hand (or click Discard trap if none):
      <div class="target-hand-preview">
        <button
                v-for="(c, i) in (pendingForMe?.action?.lastResponse?.params?.targetHand ?? []).filter(x => ['Hen', 'Rooster', 'Snake', 'Fox'].includes(x))"
                :key="i"
                type="button"
                class="mini-card"
                :class="{ selected: selectedCards.includes(c) }"
                @click="toggleCard(c)">
          {{ c }}
        </button>
        <button
                v-if="!((pendingForMe?.action?.lastResponse?.params?.targetHand ?? []).some((x: string) => ['Hen', 'Rooster', 'Snake', 'Fox'].includes(x)))"
                type="button"
                class="discard-trap"
                @click="selectedCards = []; execute()">
          Discard trap
        </button>
      </div>
      <span v-if="pendingSecondsLeft !== null" class="timeout">({{ pendingSecondsLeft }}s)</span>
    </div>
    <div class="action-area" v-if="game && game.state === 'playing'">
      <div class="target-select" v-if="selectedCards.length === 1">
        <template v-if="selectedCards[0] === 'Fox'">
          <label>Target (must have eggs):</label>
          <select v-model="actionTarget">
            <option :value="null">Choose...</option>
            <option
                    v-for="p in game.players.filter(
                      (x) => x.id !== session.value?.userId && x.eggs >= 1
                    )"
                    :key="p.id"
                    :value="p.id">
              {{ p.name }} ({{ p.eggs }} eggs)
            </option>
          </select>
        </template>
        <template v-else-if="selectedCards[0] === 'Snake'">
          <label>Target:</label>
          <select v-model="actionTarget">
            <option :value="null">Choose...</option>
            <option
                    v-for="p in game.players.filter(
                      (x) => x.id !== session.value?.userId && x.eggs >= 1
                    )"
                    :key="p.id"
                    :value="p.id">
              {{ p.name }} ({{ p.eggs }} eggs)
            </option>
          </select>
          <template v-if="actionTarget">
            <label>Eggs to eat:</label>
            <select v-model="actionEggCount">
              <option
                      v-for="n in (game.players.find((x) => x.id === actionTarget)?.eggs ?? 1)"
                      :key="n"
                      :value="n">
                {{ n }}
              </option>
            </select>
          </template>
        </template>
        <template v-else-if="selectedCards[0] === 'Trap'">
          <label>Target:</label>
          <select v-model="actionTarget">
            <option :value="null">Choose...</option>
            <option
                    v-for="p in game.players.filter(
                      (x) => x.id !== session.value?.userId
                    )"
                    :key="p.id"
                    :value="p.id">
              {{ p.name }}
            </option>
          </select>
        </template>
      </div>
      <GameHand :cards="hand" :selected="selectedCards" :selectable="isMyTurn || !!pendingForMe" @toggle="toggleCard" />
      <button class="draw-btn" :disabled="!validAction || executing" @click="execute">
        {{ validAction?.type === 'DefendFoxSteal'
          ? (validAction.defend ? 'Defend!' : 'Let them steal')
          : validAction?.type === 'SkipTurn'
            ? 'Skip Turn'
            : validAction?.type === 'TrapKill' && validAction.card === null
              ? 'Discard trap'
              : validAction
                ? 'Draw'
                : 'Select cards' }}
      </button>
      <div v-if="error" class="error">{{ error }}</div>
    </div>
    <div class="lobby-actions" v-if="isLobby && game">
      <button @click="setReady">Ready</button>
      <button :disabled="!canStart" @click="startGame">Start Game</button>
    </div>
    <GameChat v-if="game" :messages="game.messages" :game="game" :can-send="!!gamePlayService" @send="sendChat" />
  </div>
</template>
<style scoped>
.game-page {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}
.header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}
.leave {
  margin-left: auto;
}
.state {
  color: #888;
  font-size: 0.9rem;
}
.players {
  margin: 1rem 0;
}
.player {
  padding: 0.5rem;
  border-radius: 8px;
}
.player.current {
  background: rgba(100, 108, 255, 0.2);
}
.player.has-eggs {
  border-left: 3px solid #fbbf24;
}
.turn-badge {
  margin-left: 0.5rem;
  font-size: 0.75rem;
  background: #646cff;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
}
.ready {
  color: #4ade80;
  margin-left: 0.5rem;
}
.win-banner {
  background: #16a34a;
  color: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin: 1rem 0;
  font-size: 1.25rem;
}
.pending-banner {
  background: #7c3aed;
  color: white;
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
}
.pending-banner .timeout {
  opacity: 0.9;
  font-size: 0.9rem;
}
.target-hand-preview {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
  flex-wrap: wrap;
}
.mini-card {
  padding: 0.35rem 0.6rem;
  font-size: 0.85rem;
  border: 2px solid transparent;
  border-radius: 6px;
  cursor: pointer;
}
.mini-card.selected {
  border-color: #fff;
}
.discard-trap {
  padding: 0.35rem 0.6rem;
  font-size: 0.85rem;
  border-radius: 6px;
  cursor: pointer;
}
.action-area {
  margin: 1.5rem 0;
}
.target-select {
  margin-bottom: 0.5rem;
}
.target-select label {
  margin-right: 0.5rem;
}
.target-select select {
  padding: 0.25rem;
  margin-right: 0.5rem;
}
.draw-btn {
  margin-top: 0.75rem;
  padding: 0.5rem 1.5rem;
}
.error {
  color: #f87171;
  margin-top: 0.5rem;
}
.lobby-actions {
  display: flex;
  gap: 0.5rem;
  margin: 1rem 0;
}
</style>