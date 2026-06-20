<template>
  <div class="portal-wrap">
    <div class="portal-header">
      <RouterLink to="/affiliate" class="back-link">← Partnerprogramm</RouterLink>
      <h1>📊 Affiliate Dashboard</h1>
    </div>

    <!-- Login für Portal -->
    <div v-if="!loggedIn" class="portal-login">
      <h2>Mit deinem Affiliate-Code einloggen</h2>
      <div class="login-row">
        <input v-model="codeInput" placeholder="Dein Affiliate-Code (z.B. JANE20)" @keydown.enter="loadStats" />
        <button class="btn-load" :disabled="loading" @click="loadStats">
          {{ loading ? '…' : 'Statistiken laden' }}
        </button>
      </div>
      <p v-if="loadError" class="err-msg">⚠ {{ loadError }}</p>
      <p class="hint">Du findest deinen Code in der Bestätigungs-E-Mail oder auf der Registrierungsseite.</p>
    </div>

    <!-- Dashboard -->
    <div v-else class="dashboard">
      <div class="welcome-bar">
        <div>Hallo, <strong>{{ stats.name }}</strong> 👋</div>
        <div class="aff-code-display">Dein Code: <code>{{ stats.code }}</code></div>
        <button class="btn-ghost-sm" @click="loggedIn = false">Abmelden</button>
      </div>

      <!-- KPI-Karten -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-icon">👆</div>
          <div class="kpi-num">{{ stats.clicks }}</div>
          <div class="kpi-label">Klicks gesamt</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon">✅</div>
          <div class="kpi-num">{{ stats.conversions }}</div>
          <div class="kpi-label">Conversions</div>
        </div>
        <div class="kpi-card highlight">
          <div class="kpi-icon">💰</div>
          <div class="kpi-num">{{ stats.earnings.toFixed(2) }}€</div>
          <div class="kpi-label">Verdient (gesamt)</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon">📈</div>
          <div class="kpi-num">{{ convRate }}%</div>
          <div class="kpi-label">Conversion-Rate</div>
        </div>
      </div>

      <!-- Dein Link -->
      <div class="link-section">
        <h2>Dein Affiliate-Link</h2>
        <div class="link-display">
          <span>{{ myLink }}</span>
          <button class="btn-copy" @click="copyMyLink">{{ copiedLink ? '✓' : '📋 Kopieren' }}</button>
        </div>
        <div class="share-row">
          <a :href="`https://twitter.com/intent/tweet?text=${encodeURIComponent(tweetText)}`" target="_blank" class="share-btn twitter">🐦 Twitter</a>
          <a :href="`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(myLink)}`" target="_blank" class="share-btn linkedin">💼 LinkedIn</a>
          <button class="share-btn email" @click="shareEmail">📧 E-Mail</button>
        </div>
      </div>

      <!-- Letzte Conversions -->
      <div class="conv-section">
        <h2>Letzte Conversions</h2>
        <div v-if="stats.recentConversions?.length" class="conv-list">
          <div v-for="c in stats.recentConversions" :key="c.date" class="conv-row">
            <span class="conv-date">{{ formatDate(c.date) }}</span>
            <span class="conv-plan">{{ c.plan }}</span>
            <span class="conv-earn">+{{ c.commission.toFixed(2) }}€</span>
          </div>
        </div>
        <div v-else class="conv-empty">
          Noch keine Conversions. Teile deinen Link um die ersten Provisionen zu verdienen!
        </div>
      </div>

      <!-- Auszahlung -->
      <div class="payout-section">
        <h2>💳 Auszahlung beantragen</h2>
        <p>Verfügbares Guthaben: <strong class="green">{{ stats.earnings.toFixed(2) }}€</strong></p>
        <p class="hint">Auszahlung ab 20€ · Bearbeitung innerhalb von 5 Werktagen</p>
        <button class="btn-payout" :disabled="stats.earnings < 20" @click="requestPayout">
          {{ stats.earnings >= 20 ? 'Auszahlung beantragen' : `Noch ${(20 - stats.earnings).toFixed(2)}€ bis zur Auszahlung` }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const codeInput = ref(localStorage.getItem('finaz_aff_code') || '')
const loading = ref(false)
const loadError = ref('')
const loggedIn = ref(false)
const copiedLink = ref(false)

interface Conversion { date: string; plan: string; commission: number }
interface AffStats {
  name: string; code: string; email: string
  clicks: number; conversions: number; earnings: number
  recentConversions: Conversion[]
}

const stats = ref<AffStats>({ name: '', code: '', email: '', clicks: 0, conversions: 0, earnings: 0, recentConversions: [] })

const convRate = computed(() => stats.value.clicks > 0 ? ((stats.value.conversions / stats.value.clicks) * 100).toFixed(1) : '0.0')
const myLink = computed(() => `${window.location.origin}/?ref=${stats.value.code}`)
const tweetText = computed(() => `🛡️ Schütze deine Website mit SecureHub – Cyber Security Scanner + Server Monitor. Kostenlos testen: ${myLink.value}`)

async function loadStats() {
  if (!codeInput.value.trim()) return
  loading.value = true
  loadError.value = ''
  try {
    const res = await fetch(`/api/affiliate/stats/${codeInput.value.trim().toUpperCase()}`)
    const data = await res.json()
    if (!res.ok) throw new Error(data.error || 'Code nicht gefunden')
    stats.value = data
    loggedIn.value = true
    localStorage.setItem('finaz_aff_code', codeInput.value.trim().toUpperCase())
  } catch (e: unknown) {
    loadError.value = (e as Error).message
  } finally {
    loading.value = false
  }
}

async function copyMyLink() {
  await navigator.clipboard.writeText(myLink.value)
  copiedLink.value = true
  setTimeout(() => { copiedLink.value = false }, 2000)
}

function shareEmail() {
  window.location.href = `mailto:?subject=SecureHub%20empfehlen&body=${encodeURIComponent(`Ich nutze SecureHub für Website-Security und kann es nur empfehlen!\n\nJetzt kostenlos testen: ${myLink.value}`)}`
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('de-DE')
}

function requestPayout() {
  alert(`Auszahlungsanfrage für ${stats.value.earnings.toFixed(2)}€ wurde gesendet. Du erhältst eine E-Mail an ${stats.value.email}.`)
}

// Auto-laden wenn Code gespeichert
if (codeInput.value) loadStats()
</script>

<style scoped>
.portal-wrap { max-width: 900px; margin: 0 auto; padding: 2rem 1.5rem; }
.portal-header { margin-bottom: 2rem; }
.back-link { font-size: 0.85rem; color: #64748b; text-decoration: none; }
.back-link:hover { color: #94a3b8; }
.portal-header h1 { font-size: 1.75rem; font-weight: 700; margin: 0.5rem 0 0; }

.portal-login { max-width: 480px; background: #0f172a; border: 1px solid #1e293b; border-radius: 16px; padding: 2rem; }
.portal-login h2 { margin: 0 0 1.25rem; font-size: 1.2rem; }
.login-row { display: flex; gap: 0.75rem; }
.login-row input { flex: 1; padding: 0.65rem 0.9rem; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: #e2e8f0; font-size: 0.95rem; }
.login-row input:focus { outline: none; border-color: #3b82f6; }
.btn-load { padding: 0.65rem 1.25rem; border-radius: 8px; border: none; background: #3b82f6; color: #fff; font-weight: 600; cursor: pointer; white-space: nowrap; }
.btn-load:disabled { opacity: 0.6; }
.err-msg { color: #f87171; font-size: 0.85rem; background: rgba(248,113,113,0.1); padding: 0.5rem 0.75rem; border-radius: 8px; margin-top: 0.75rem; }
.hint { font-size: 0.8rem; color: #475569; margin-top: 0.75rem; }

.welcome-bar { display: flex; align-items: center; gap: 1rem; background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 0.9rem 1.25rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.aff-code-display { font-size: 0.85rem; color: #64748b; }
.aff-code-display code { background: #1e293b; padding: 0.15rem 0.5rem; border-radius: 4px; color: #60a5fa; }
.btn-ghost-sm { margin-left: auto; padding: 0.3rem 0.75rem; border-radius: 6px; border: 1px solid #334155; background: transparent; color: #64748b; cursor: pointer; font-size: 0.82rem; }

.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
.kpi-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 1.25rem; text-align: center; }
.kpi-card.highlight { border-color: rgba(34,197,94,0.3); background: rgba(34,197,94,0.05); }
.kpi-icon { font-size: 1.75rem; margin-bottom: 0.5rem; }
.kpi-num { font-size: 2rem; font-weight: 700; color: #e2e8f0; }
.kpi-card.highlight .kpi-num { color: #4ade80; }
.kpi-label { font-size: 0.8rem; color: #64748b; margin-top: 0.25rem; }

.link-section, .conv-section, .payout-section { background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.25rem; }
.link-section h2, .conv-section h2, .payout-section h2 { margin: 0 0 1rem; font-size: 1.1rem; color: #e2e8f0; }
.link-display { display: flex; align-items: center; gap: 0.75rem; background: #020817; border: 1px solid #1e293b; border-radius: 8px; padding: 0.7rem 1rem; margin-bottom: 1rem; }
.link-display span { flex: 1; font-size: 0.85rem; color: #60a5fa; word-break: break-all; }
.btn-copy { padding: 0.35rem 0.8rem; border-radius: 6px; border: 1px solid #334155; background: #1e293b; color: #94a3b8; cursor: pointer; font-size: 0.82rem; white-space: nowrap; }
.btn-copy:hover { border-color: #60a5fa; color: #60a5fa; }

.share-row { display: flex; gap: 0.75rem; flex-wrap: wrap; }
.share-btn { padding: 0.5rem 1.1rem; border-radius: 8px; border: 1px solid #334155; font-size: 0.85rem; cursor: pointer; text-decoration: none; color: #e2e8f0; background: #1e293b; transition: all 0.2s; }
.share-btn:hover { border-color: #60a5fa; }
.share-btn.twitter:hover { border-color: #1da1f2; color: #1da1f2; }
.share-btn.linkedin:hover { border-color: #0a66c2; color: #0a66c2; }

.conv-list { display: flex; flex-direction: column; gap: 0.5rem; }
.conv-row { display: flex; align-items: center; gap: 1rem; padding: 0.6rem 0; border-bottom: 1px solid #1e293b; }
.conv-date { font-size: 0.82rem; color: #64748b; flex: 1; }
.conv-plan { font-size: 0.85rem; color: #cbd5e1; }
.conv-earn { font-weight: 600; color: #4ade80; margin-left: auto; }
.conv-empty { font-size: 0.88rem; color: #64748b; font-style: italic; }

.payout-section p { color: #94a3b8; font-size: 0.9rem; margin: 0 0 0.35rem; }
.green { color: #4ade80; }
.btn-payout { margin-top: 1rem; padding: 0.7rem 1.5rem; border-radius: 10px; border: none; background: #22c55e; color: #000; font-weight: 700; cursor: pointer; transition: background 0.2s; }
.btn-payout:hover:not(:disabled) { background: #16a34a; }
.btn-payout:disabled { opacity: 0.5; cursor: not-allowed; background: #334155; color: #64748b; }
</style>
