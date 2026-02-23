import type { IEvent } from './utility/Event.js'
import type { Game } from './models/Game.js'
import type { GameAction } from './models/GameAction.js'
import type { Card } from './models/Card.js'

export interface IGamePlayService {
  onGameUpdated: IEvent<Game>
  onGameAction: IEvent<GameAction>
  onHandChanged: IEvent<Card[]>
  getGame(): Game
  getHand(): Card[]
  leave(): Promise<void>
  setReady(): Promise<void>
  executeAction(action: GameAction): Promise<void>
  subscribe?(): Promise<void>
  sendMessage?(text: string): Promise<void>
  startGame?(): Promise<void>
}
