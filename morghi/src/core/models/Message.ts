/**
 * Chat or system message. sender is Player.id for player messages, null for system.
 */
export interface Message {
  id: string
  sender: string | null
  message: string
}
