import { createRouter, createWebHistory } from 'vue-router'
import type { IAuthService } from '../core/IAuthService.js'
import type { IGameListService } from '../core/IGameListService.js'

export function createAppRouter(
  authService: IAuthService,
  gameListService: IGameListService
) {
  const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
      {
        path: '/',
        name: 'root',
        component: () => import('./views/RootPage.vue'),
      },
      {
        path: '/auth',
        name: 'auth',
        component: () => import('./views/AuthPage.vue'),
      },
      {
        path: '/lobby',
        name: 'lobby',
        component: () => import('./views/LobbyPage.vue'),
      },
      {
        path: '/game/:id',
        name: 'game',
        component: () => import('./views/GamePage.vue'),
      },
    ],
  })

  router.beforeEach(async (to, _from, next) => {
    const session = await authService.getSession()
    if (!session && to.name !== 'auth') {
      next({ name: 'auth' })
      return
    }
    if (session && to.name === 'auth') {
      const current = gameListService.getCurrentGame()
      if (current) {
        next({ name: 'game', params: { id: current.getGame().id } })
      } else {
        next({ name: 'lobby' })
      }
      return
    }
    next()
  })

  return router
}
