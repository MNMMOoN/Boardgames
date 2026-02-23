import type { IEvent } from './utility/Event.js'
import type { GameInfo } from './models/GameInfo.js'
import type { IGamePlayService } from './IGamePlayService.js'

export interface IGameListService {
  onGamesListUpdated: IEvent<GameInfo[]>
  getGames(): GameInfo[]
  newGame(name: string): Promise<void>
  joinGame(id: string): Promise<IGamePlayService>
  getCurrentGame(): IGamePlayService | null
  refresh?(): Promise<void>
}
