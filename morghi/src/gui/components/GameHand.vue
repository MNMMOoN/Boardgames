<script setup lang="ts">
import type { Card } from '../../core/models/Card.js'

const props = defineProps<{
  cards: Card[]
  selected: Card[]
  selectable: boolean
}>()

const emit = defineEmits<{
  toggle: [card: Card]
}>()

function isSelected(card: Card) {
  return props.selected.includes(card)
}

function click(card: Card) {
  if (!props.selectable) return
  emit('toggle', card)
}
</script>

<template>
  <div class="hand">
    <button
      v-for="(c, i) in cards"
      :key="i"
      type="button"
      class="card"
      :class="{ selected: isSelected(c) }"
      :disabled="!selectable"
      @click="click(c)"
    >
      {{ c }}
    </button>
  </div>
</template>

<style scoped>
.hand {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
}
.card {
  padding: 0.75rem 1.25rem;
  background: #333;
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
}
.card:hover:not(:disabled) {
  border-color: #646cff;
}
.card.selected {
  border-color: #646cff;
  background: #404060;
}
</style>
