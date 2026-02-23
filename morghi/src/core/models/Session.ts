/**
 * Auth session. Core defines this; App maps from Supabase Session.
 */
export interface Session {
  userId: string
  email?: string
}
