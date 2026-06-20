<template>
  <div class="auth-wrap">
    <div class="auth-card">
      <RouterLink to="/" class="back-link">← Zurück</RouterLink>
      <div class="auth-logo">🛡️ SecureHub</div>

      <div class="auth-tabs">
        <button :class="['auth-tab', { active: mode === 'login' }]" @click="mode = 'login'; err = ''">Anmelden</button>
        <button :class="['auth-tab', { active: mode === 'register' }]" @click="mode = 'register'; err = ''">Registrieren</button>
      </div>

      <form @submit.prevent="submit">
        <div class="field">
          <label>E-Mail</label>
          <input v-model="email" type="email" placeholder="du@beispiel.de" required autocomplete="email" />
        </div>
        <div class="field">
          <label>Passwort</label>
          <input v-model="password" type="password" placeholder="Mindestens 8 Zeichen" required autocomplete="current-password" />
        </div>
        <div v-if="mode === 'register'" class="field">
          <label>Passwort bestätigen</label>
          <input v-model="password2" type="password" placeholder="Passwort wiederholen" required />
        </div>

        <p v-if="err" class="auth-error">⚠ {{ err }}</p>
        <p v-if="success" class="auth-success">✅ {{ success }}</p>

        <button type="submit" class="btn-auth" :disabled="auth.loading">
          {{ auth.loading ? '…' : mode === 'login' ? 'Anmelden' : 'Konto erstellen' }}
        </button>
      </form>

      <div class="auth-divider"><span>oder</span></div>

      <button class="btn-demo" @click="demoLogin">
        🎯 Demo-Konto verwenden (kein Account nötig)
      </button>

      <p v-if="!supabaseEnabled" class="demo-hint">
        ℹ Supabase nicht konfiguriert – Demo-Modus aktiv. Daten werden lokal gespeichert.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { supabaseEnabled } from '../lib/supabase'

const auth = useAuthStore()
const router = useRouter()

const mode = ref<'login' | 'register'>('login')
const email = ref('')
const password = ref('')
const password2 = ref('')
const err = ref('')
const success = ref('')

async function submit() {
  err.value = ''
  success.value = ''
  if (mode.value === 'register') {
    if (password.value !== password2.value) { err.value = 'Passwörter stimmen nicht überein.'; return }
    if (password.value.length < 8) { err.value = 'Passwort muss mindestens 8 Zeichen haben.'; return }
    await auth.signUp(email.value, password.value)
    if (auth.error) { err.value = auth.error; return }
    success.value = 'Konto erstellt! Bitte E-Mail bestätigen (falls Supabase aktiv).'
  } else {
    await auth.signIn(email.value, password.value)
    if (auth.error) { err.value = auth.error; return }
    router.push('/app')
  }
}

async function demoLogin() {
  await auth.signIn('demo@securehub.de', 'demo1234')
  router.push('/app')
}
</script>

<style scoped>
.auth-wrap {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: #020817; padding: 2rem;
}
.auth-card {
  width: 100%; max-width: 420px; background: #0f172a;
  border: 1px solid #1e293b; border-radius: 16px; padding: 2rem;
}
.back-link { font-size: 0.85rem; color: #64748b; text-decoration: none; }
.back-link:hover { color: #94a3b8; }
.auth-logo { text-align: center; font-size: 1.5rem; font-weight: 700; color: #e2e8f0; margin: 1rem 0 1.5rem; }

.auth-tabs { display: flex; gap: 0; margin-bottom: 1.5rem; background: #1e293b; border-radius: 10px; padding: 3px; }
.auth-tab {
  flex: 1; padding: 0.55rem; border-radius: 8px; border: none;
  background: transparent; color: #64748b; cursor: pointer; font-size: 0.9rem; font-weight: 500; transition: all 0.2s;
}
.auth-tab.active { background: #334155; color: #e2e8f0; }

.field { margin-bottom: 1rem; }
.field label { display: block; font-size: 0.85rem; color: #94a3b8; margin-bottom: 0.35rem; }
.field input {
  width: 100%; padding: 0.65rem 0.9rem; border-radius: 8px; border: 1px solid #334155;
  background: #0f172a; color: #e2e8f0; font-size: 0.95rem; box-sizing: border-box;
}
.field input:focus { outline: none; border-color: #3b82f6; }

.auth-error { color: #f87171; font-size: 0.85rem; margin: 0 0 1rem; background: rgba(248,113,113,0.1); padding: 0.5rem 0.75rem; border-radius: 8px; }
.auth-success { color: #4ade80; font-size: 0.85rem; margin: 0 0 1rem; background: rgba(74,222,128,0.1); padding: 0.5rem 0.75rem; border-radius: 8px; }

.btn-auth {
  width: 100%; padding: 0.75rem; border-radius: 10px; border: none;
  background: #3b82f6; color: #fff; font-size: 1rem; font-weight: 600; cursor: pointer; transition: background 0.2s;
}
.btn-auth:hover:not(:disabled) { background: #2563eb; }
.btn-auth:disabled { opacity: 0.6; cursor: not-allowed; }

.auth-divider { text-align: center; margin: 1.25rem 0; position: relative; }
.auth-divider::before { content: ''; position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #1e293b; }
.auth-divider span { position: relative; background: #0f172a; padding: 0 0.75rem; font-size: 0.82rem; color: #475569; }

.btn-demo {
  width: 100%; padding: 0.7rem; border-radius: 10px; border: 1px solid #334155;
  background: transparent; color: #94a3b8; font-size: 0.9rem; cursor: pointer; transition: all 0.2s;
}
.btn-demo:hover { border-color: #60a5fa; color: #e2e8f0; }

.demo-hint { font-size: 0.78rem; color: #475569; text-align: center; margin: 1rem 0 0; line-height: 1.4; }
</style>
