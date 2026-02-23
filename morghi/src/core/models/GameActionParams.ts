import type { Player } from './Player.js'
import type { Card } from './Card.js'

export interface FoxStealParams {
  target: Player
}

export interface SnakeEatParams {
  target: Player
  eggCount: number
}

export interface TrapKillParams {
  target: Player
  finish: boolean
  card: Card | null
}
