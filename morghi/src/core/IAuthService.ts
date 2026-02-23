import type { IEvent } from './utility/Event.js'
import type { Session } from './models/Session.js'

export interface IAuthService {
  getSession(): Promise<Session | null>
  onSessionChanged: IEvent<Session | null>
  signUp(email: string, password: string): Promise<void>
  signIn(email: string, password: string): Promise<void>
  signOut(): Promise<void>
}
