import type { GameActionType } from './GameActionType.js'
import type { TrapKillResponseParams } from './GameActionResponseParams.js'

/**
 * Response to a game action - used for multi-step flows like TrapKill, FoxSteal.
 */
export interface GameActionResponse {
  type: GameActionType
  isComplete: boolean
  isAwaitingActor: boolean
  isAwaitingTarget: boolean
  params: TrapKillResponseParams | null
}
