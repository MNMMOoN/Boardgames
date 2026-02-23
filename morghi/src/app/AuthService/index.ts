import type { IAuthService } from '../../core/IAuthService.js'
import type { Session } from '../../core/models/Session.js'
import { Event } from '../../core/utility/Event.js'
import { supabase } from '../supabase/index.js'

export class AuthService implements IAuthService {
  onSessionChanged = new Event<Session | null>()
  private session: Session | null = null

  constructor() {
    supabase.auth.onAuthStateChange((_event, session) => {
      this.session = this.mapSession(session)
      this.onSessionChanged.invoke(this.session)
    })
  }

  private getSessionPromise: Promise<Session | null> | null = null
  async getSession(): Promise<Session | null> {
    if (this.getSessionPromise === null) {
      this.getSessionPromise = this.loadSession()
    }
    await this.getSessionPromise
    return this.session
  }

  private async loadSession(): Promise<Session | null> {
    const { data } = await supabase.auth.getSession()
    this.session = this.mapSession(data.session)
    if (this.session) this.onSessionChanged.invoke(this.session)
    return this.session
  }

  private mapSession(
    session: { user: { id: string; email?: string } } | null | undefined
  ): Session | null {
    if (!session?.user) return null
    return {
      userId: session.user.id,
      email: session.user.email ?? undefined,
    }
  }

  async signUp(email: string, password: string): Promise<void> {
    const { error } = await supabase.auth.signUp({ email, password })
    if (error) throw error
  }

  async signIn(email: string, password: string): Promise<void> {
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) throw error
  }

  async signOut(): Promise<void> {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
    this.onSessionChanged.invoke(null)
  }
}
