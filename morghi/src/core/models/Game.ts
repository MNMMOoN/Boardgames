import type { Player } from './Player.js'
import type { Message } from './Message.js'
import type { GamePending } from './GamePending.js'

/**
 * Full game state. currentPlayer is Player.id when state=playing, else null.
 */
export interface Game {
  id: string
  name: string
  state: string
  players: Player[]
  messages: Message[]
  currentPlayer: string | null
  pending: GamePending | null
}

/**
 * Returns the Player whose turn it is, or null.
 */
export function getCurrentPlayer(game: Game): Player | null {
  if (!game.currentPlayer) return null
  return game.players.find((p) => p.id === game.currentPlayer) ?? null
}
