import type { GameAction } from './GameAction.js'
import type { GameActionResponse } from './GameActionResponse.js'

/**
 * Pending action awaiting response (e.g., FoxSteal awaiting target's defend decision,
 * TrapKill awaiting actor's card selection).
 */
export interface GamePending {
  action: GameAction
  timeout: string
  lastResponse: GameActionResponse | null
}
