import type { IGamePlayService } from '../../core/IGamePlayService.js'
import type { IAuthService } from '../../core/IAuthService.js'
import type { Game } from '../../core/models/Game.js'
import type { Player } from '../../core/models/Player.js'
import type { Message } from '../../core/models/Message.js'
import type { GamePending } from '../../core/models/GamePending.js'
import type { GameAction } from '../../core/models/GameAction.js'
import type { Card } from '../../core/models/Card.js'
import { Event } from '../../core/utility/Event.js'
import { supabase } from '../supabase/index.js'

export class GamePlayService implements IGamePlayService {
  onGameUpdated = new Event<Game>()
  onGameAction = new Event<GameAction>()
  onHandChanged = new Event<Card[]>()

  private game: Game | null = null
  private hand: Card[] = []

  private readonly gameId: string
  private readonly authService: IAuthService

  constructor(gameId: string, authService: IAuthService) {
    this.gameId = gameId
    this.authService = authService
  }

  async subscribe(): Promise<void> {
    await this.fetchGame()
    supabase
      .channel(`game:${this.gameId}`)
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'games', filter: `id=eq.${this.gameId}` },
        () => this.fetchGame()
      )
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'players', filter: `game_id=eq.${this.gameId}` },
        () => this.fetchGame()
      )
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'messages', filter: `game_id=eq.${this.gameId}` },
        () => this.fetchGame()
      )
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'game_pending', filter: `game_id=eq.${this.gameId}` },
        () => this.fetchGame()
      )
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'hands', filter: `game_id=eq.${this.gameId}` },
        () => this.fetchHand()
      )
      .subscribe()
  }

  private async fetchGame(): Promise<void> {
    const { data: g, error } = await supabase
      .from('games')
      .select('*')
      .eq('id', this.gameId)
      .single()

    if (error || !g) return

    const { data: playersData } = await supabase
      .from('players')
      .select('*')
      .eq('game_id', this.gameId)
      .order('player_order', { ascending: true })

    const players: Player[] = (playersData ?? [])
      .filter((p) => !p.left_at)
      .map((p) => ({
        id: p.id,
        name: p.name,
        eggs: p.eggs,
        chickens: p.chickens,
        ready: p.ready,
        order: p.player_order,
      }))

    const order = g.current_player_order as number | undefined
    const currentPlayer =
      g.state === 'playing' && order != null && order >= 0 && order < players.length
        ? players[order]
        : null
    const currentPlayerId = currentPlayer?.id ?? null

    const { data: messagesData } = await supabase
      .from('messages')
      .select('id, sender_id, message')
      .eq('game_id', this.gameId)
      .order('created_at', { ascending: true })

    const messages: Message[] = (messagesData ?? []).map((m) => ({
      id: m.id,
      sender: m.sender_id,
      message: m.message,
    }))

    let pending: GamePending | null = null
    const { data: pd } = await supabase
      .from('game_pending')
      .select('*')
      .eq('game_id', this.gameId)
      .maybeSingle()

    if (pd) {
      const actor = players.find((p) => p.id === pd.action?.actor?.id)
      if (actor) {
        pending = {
          action: {
            type: pd.action.type,
            actor,
            cards: pd.action.cards ?? [],
            params: pd.action.params ?? null,
          },
          timeout: pd.timeout,
          lastResponse: pd.last_response ?? null,
        }
      }
    }

    this.game = {
      id: g.id,
      name: g.name,
      state: g.state,
      players,
      messages,
      currentPlayer: currentPlayerId,
      pending,
    }
    this.onGameUpdated.invoke(this.game)
    await this.fetchHand()
  }

  private async fetchHand(): Promise<void> {
    const session = await this.authService.getSession()
    if (!session) return

    const { data, error } = await supabase
      .from('hands')
      .select('cards')
      .eq('game_id', this.gameId)
      .eq('player_id', session.userId)
      .maybeSingle()

    if (!error && data?.cards) {
      this.hand = data.cards as Card[]
      this.onHandChanged.invoke(this.hand)
    }
  }

  getGame(): Game {
    if (!this.game) throw new Error('Game not loaded')
    return this.game
  }

  getHand(): Card[] {
    return [...this.hand]
  }

  async leave(): Promise<void> {
    await supabase.rpc('leave_game', { p_game_id: this.gameId })
  }

  async setReady(): Promise<void> {
    const session = await this.authService.getSession()
    if (!session) throw new Error('Not authenticated')

    await supabase
      .from('players')
      .update({ ready: true })
      .eq('game_id', this.gameId)
      .eq('id', session.userId)
  }

  async executeAction(action: GameAction): Promise<void> {
    const session = await this.authService.getSession()
    if (!session) throw new Error('Not authenticated')

    if (
      action.type === 'LayEgg' ||
      action.type === 'HatchEgg' ||
      action.type === 'SkipTurn'
    ) {
      await supabase.rpc('execute_simple_action', {
        p_game_id: this.gameId,
        p_action_type: action.type,
        p_cards: action.cards,
        p_params: action.params,
      })
      return
    }

    if (action.type === 'FoxSteal' && action.params && 'target' in action.params) {
      await supabase.rpc('fox_steal', {
        p_game_id: this.gameId,
        p_cards: action.cards,
        p_target_id: action.params.target.id,
      })
      return
    }

    if (action.type === 'SnakeEat' && action.params && 'target' in action.params && 'eggCount' in action.params) {
      await supabase.rpc('snake_eat', {
        p_game_id: this.gameId,
        p_cards: action.cards,
        p_target_id: action.params.target.id,
        p_egg_count: action.params.eggCount,
      })
      return
    }

    if (action.type === 'TrapKill' && action.params && 'target' in action.params) {
      const params = action.params as { target: { id: string }; finish?: boolean; card?: string | null }
      if (params.finish) {
        await supabase.rpc('trap_kill_finish', {
          p_game_id: this.gameId,
          p_card_to_kill: params.card ?? null,
        })
      } else {
        await supabase.rpc('trap_kill_init', {
          p_game_id: this.gameId,
          p_cards: action.cards,
          p_target_id: params.target.id,
        })
      }
      return
    }

    if (action.type === 'DefendFoxSteal') {
      const defend = action.cards.length === 2
      await supabase.rpc('defend_fox', {
        p_game_id: this.gameId,
        p_defend: defend,
      })
      return
    }

    throw new Error(`Unknown action type: ${action.type}`)
  }

  async startGame(): Promise<void> {
    await supabase.rpc('start_game', { p_game_id: this.gameId })
  }

  async sendMessage(text: string): Promise<void> {
    const session = await this.authService.getSession()
    if (!session) throw new Error('Not authenticated')

    await supabase.from('messages').insert({
      game_id: this.gameId,
      sender_id: session.userId,
      message: text,
    })
  }
}
