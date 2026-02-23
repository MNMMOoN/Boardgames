import { type Session, InjectionKeys } from './core/index.js'
import { authService, gameListService } from './app/index.js'
import { createAppRouter } from './gui/router.js'
import { createApp, ref } from 'vue'
import App from './gui/App.vue'
import './global-style.css'

async function bootstrap() {
  const session = await authService.getSession()
  const sessionRef = ref<Session | null>(session)
  authService.onSessionChanged.addListener((s) => { sessionRef.value = s })

  await gameListService.refresh?.()

  const app = createApp(App)
  app.provide(InjectionKeys.authService, authService)
  app.provide(InjectionKeys.gameListService, gameListService)
  app.provide(InjectionKeys.session, sessionRef)

  const router = createAppRouter(authService, gameListService)
  app.use(router)

  app.mount('#app')
}

bootstrap().catch(console.error)
