import type { GameActionType } from './GameActionType.js'
import type { Player } from './Player.js'
import type { Card } from './Card.js'
import type {
  FoxStealParams,
  SnakeEatParams,
  TrapKillParams,
} from './GameActionParams.js'

/**
 * Action requested by a player. cards refers to cards in actor's hand (1-3 depending on type).
 */
export interface GameAction {
  type: GameActionType
  actor: Player
  cards: Card[]
  params: FoxStealParams | SnakeEatParams | TrapKillParams | null
}
