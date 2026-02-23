<script setup lang="ts">
import { ref } from 'vue'
import { inject } from 'vue'
import { InjectionKeys, type IAuthService } from '../../core/index.js'

const authService = inject<IAuthService>(InjectionKeys.authService)!

const mode = ref<'signin' | 'signup'>('signin')
const email = ref('')
const password = ref('')
const error = ref<string | null>(null)
const loading = ref(false)
const signUpSuccess = ref(false)

async function submit() {
  error.value = null
  loading.value = true
  try {
    if (mode.value === 'signup') {
      await authService.signUp(email.value, password.value)
      signUpSuccess.value = true
    } else {
      await authService.signIn(email.value, password.value)
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
  }
}

function toggleMode() {
  mode.value = mode.value === 'signin' ? 'signup' : 'signin'
  error.value = null
  signUpSuccess.value = false
}
</script>
<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1>Morghi</h1>
      <p class="subtitle">First to 3 chickens wins</p>
      <div v-if="signUpSuccess" class="success">
        Check your email to verify your account, then sign in.
      </div>
      <form v-else @submit.prevent="submit" class="auth-form">
        <input
               v-model="email"
               type="email"
               placeholder="Email"
               required
               autocomplete="email" />
        <input
               v-model="password"
               type="password"
               placeholder="Password"
               required
               autocomplete="current-password" />
        <div v-if="error" class="error">{{ error }}</div>
        <button type="submit" :disabled="loading">
          {{ mode === 'signin' ? 'Sign In' : 'Sign Up' }}
        </button>
        <button type="button" class="link" @click="toggleMode">
          {{ mode === 'signin' ? 'Need an account? Sign up' : 'Have an account? Sign in' }}
        </button>
      </form>
    </div>
  </div>
</template>
<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 2rem;
}
.auth-card {
  background: var(--card-bg, #1a1a1a);
  padding: 2rem;
  border-radius: 12px;
  max-width: 320px;
  width: 100%;
}
h1 {
  margin: 0 0 0.25rem;
  font-size: 2rem;
}
.subtitle {
  color: #888;
  margin: 0 0 1.5rem;
}
.auth-form input {
  width: 100%;
  padding: 0.75rem;
  margin-bottom: 0.75rem;
  border: 1px solid #333;
  border-radius: 8px;
  font-size: 1rem;
  box-sizing: border-box;
}
.auth-form button {
  width: 100%;
  padding: 0.75rem;
  margin-top: 0.25rem;
}
.auth-form button.link {
  background: transparent;
  border: none;
  color: #646cff;
  margin-top: 0.5rem;
  cursor: pointer;
}
.auth-form button.link:hover {
  text-decoration: underline;
}
.error {
  color: #f87171;
  font-size: 0.875rem;
  margin: 0.5rem 0;
}
.success {
  color: #4ade80;
  font-size: 0.9rem;
  padding: 1rem;
}
</style>