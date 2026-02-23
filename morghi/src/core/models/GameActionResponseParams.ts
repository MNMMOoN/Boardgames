import type { Card } from './Card.js'

/**
 * Only used when action is TrapKill - target's hand for actor to select card to kill.
 */
export interface TrapKillResponseParams {
  targetHand: Card[] | null
}
