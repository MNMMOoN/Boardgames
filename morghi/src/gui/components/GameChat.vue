<script setup lang="ts">
import { ref } from 'vue'
import type { Message } from '../../core/models/Message.js'
import type { Game } from '../../core/models/Game.js'

const props = defineProps<{
  messages: Message[]
  game: Game | null
  canSend: boolean
}>()

const emit = defineEmits<{
  send: [text: string]
}>()

const input = ref('')

function send() {
  const t = input.value.trim()
  if (!t) return
  emit('send', t)
  input.value = ''
}
</script>

<template>
  <div class="chat">
    <div class="messages" ref="messagesEl">
      <div v-for="m in messages" :key="m.id" class="message">
        <span v-if="m.sender" class="sender">
          {{ game?.players.find(p => p.id === m.sender)?.name ?? '?' }}:
        </span>
        <span v-else class="system">[System]</span>
        {{ m.message }}
      </div>
    </div>
    <form v-if="canSend" @submit.prevent="send" class="chat-input">
      <input v-model="input" placeholder="Type a message..." />
      <button type="submit">Send</button>
    </form>
  </div>
</template>

<style scoped>
.chat {
  display: flex;
  flex-direction: column;
  border: 1px solid #333;
  border-radius: 8px;
  overflow: hidden;
}
.messages {
  height: 150px;
  overflow-y: auto;
  padding: 0.5rem;
  background: #1a1a1a;
}
.message {
  padding: 0.25rem 0;
  font-size: 0.9rem;
}
.sender { color: #646cff; }
.system { color: #888; }
.chat-input {
  display: flex;
  padding: 0.5rem;
  gap: 0.5rem;
}
.chat-input input {
  flex: 1;
  padding: 0.5rem;
}
</style>
