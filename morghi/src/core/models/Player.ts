/**
 * Player in a game. id maps to Auth.uid.
 */
export interface Player {
  id: string
  name: string
  eggs: number
  chickens: number
  /** Whether player has set ready in lobby. */
  ready?: boolean
  /** Turn order (0-based), determined at game start. */
  order?: number
  /** Whether player has left the game. */
  left?: boolean
}
