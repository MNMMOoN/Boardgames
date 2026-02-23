import type { IGameListService } from '../../core/IGameListService.js'
import type { IAuthService } from '../../core/IAuthService.js'
import type { GameInfo } from '../../core/models/GameInfo.js'
import type { IGamePlayService } from '../../core/IGamePlayService.js'
import { Event } from '../../core/utility/Event.js'
import { supabase } from '../supabase/index.js'
import { GamePlayService } from '../GamePlayService/index.js'

export class GameListService implements IGameListService {
  onGamesListUpdated = new Event<GameInfo[]>()

  private playingGame: IGamePlayService | null = null
  private readonly authService: IAuthService

  constructor(authService: IAuthService) {
    this.authService = authService
    this.authService.onSessionChanged.addListener(() => this.refresh())
  }

  getGames(): GameInfo[] {
    return this.cachedGames
  }

  private cachedGames: GameInfo[] = []

  async refresh(): Promise<void> {
    const session = await this.authService.getSession()
    if (!session) {
      this.cachedGames = []
      this.playingGame = null
      this.onGamesListUpdated.invoke([])
      return
    }

    const { data: gamesData, error } = await supabase
      .from('games')
      .select('id, name, state')
      .in('state', ['lobby'])
      .order('created_at', { ascending: false })

    if (error) {
      this.cachedGames = []
      this.onGamesListUpdated.invoke([])
      return
    }

    const games: GameInfo[] = (gamesData ?? []).map((g) => ({
      id: g.id,
      name: g.name,
      state: g.state,
    }))
    this.cachedGames = games
    this.onGamesListUpdated.invoke(games)

    const { data: myPlayer } = await supabase
      .from('players')
      .select('game_id')
      .eq('id', session.userId)
      .is('left_at', null)
      .single()

    if (myPlayer?.game_id && !this.playingGame) {
      this.playingGame = new GamePlayService(myPlayer.game_id, this.authService)
      await this.playingGame.subscribe?.()
    }
  }

  async newGame(name: string): Promise<void> {
    const session = await this.authService.getSession()
    if (!session) throw new Error('Not authenticated')

    const { data: game, error: gameError } = await supabase
      .from('games')
      .insert({ name, state: 'lobby' })
      .select('id')
      .single()

    if (gameError || !game) throw gameError ?? new Error('Failed to create game')

    const userName = session.email ?? session.userId.slice(0, 8)
    const { error: playerError } = await supabase.from('players').insert({
      id: session.userId,
      game_id: game.id,
      name: userName,
    })

    if (playerError) throw playerError

    this.playingGame = new GamePlayService(game.id, this.authService)
    await this.playingGame.subscribe?.()
    await this.refresh()
  }

  async joinGame(id: string): Promise<IGamePlayService> {
    const session = await this.authService.getSession()
    if (!session) throw new Error('Not authenticated')

    const { data: game } = await supabase
      .from('games')
      .select('state')
      .eq('id', id)
      .single()

    if (!game) throw new Error('Game not found')
    if (game.state !== 'lobby') throw new Error('Game already started')

    const userName = session.email ?? session.userId.slice(0, 8)
    const { error } = await supabase.from('players').insert({
      id: session.userId,
      game_id: id,
      name: userName,
    })

    if (error) throw error

    this.playingGame = new GamePlayService(id, this.authService)
    await this.playingGame.subscribe?.()
    await this.refresh()
    return this.playingGame
  }

  getCurrentGame(): IGamePlayService | null {
    return this.playingGame
  }
}
