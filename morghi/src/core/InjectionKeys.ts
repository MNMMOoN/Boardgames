import type { IAuthService } from './IAuthService';
export const InjectionKeys = {
  authService: nameof<IAuthService>(),
  gameListService: 'gameListService',
  session: 'session',
} as const
