import { AuthService } from './AuthService/index.js'
import { GameListService } from './GameListService/index.js'
import type { IAuthService } from '../core/IAuthService.js'
import type { IGameListService } from '../core/IGameListService.js'

export const authService: IAuthService = new AuthService()
export const gameListService: IGameListService = new GameListService(authService)
