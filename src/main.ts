import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import './style.css'
import App from './App.vue'
import { useAuthStore } from './stores/auth'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia).use(router)

const auth = useAuthStore()
auth.init()

// Affiliate-Referral-Code aus URL speichern + Klick tracken
const refParam = new URLSearchParams(window.location.search).get('ref')
if (refParam) {
  const code = refParam.toUpperCase()
  localStorage.setItem('finaz_ref', code)
  fetch('/api/affiliate/click', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ code }) }).catch(() => {})
}

app.mount('#app')
