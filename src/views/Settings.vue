<template>
  <div class="page">
    <div class="page-header">
      <h1>⚙️ Einstellungen</h1>
      <p class="sub">API-Keys, Demo-Modus und App-Konfiguration.</p>
    </div>

    <!-- Demo mode toggle -->
    <div class="card">
      <h2>🎮 Demo-Modus</h2>
      <p class="muted" style="margin-bottom:0.9rem">Im Demo-Modus läuft die App komplett kostenlos ohne API-Key — mit realistischen Beispiel-Antworten. Ideal zum Testen.</p>
      <label style="display:flex;align-items:center;gap:0.75rem;cursor:pointer">
        <input type="checkbox" :checked="demoOn" @change="toggleDemo" style="width:18px;height:18px;cursor:pointer;accent-color:var(--accent)" />
        <span>Demo-Modus aktivieren (kostenlos, kein Key nötig)</span>
      </label>
      <div v-if="demoOn" class="demo-banner" style="margin-top:0.75rem;margin-bottom:0">
        <span class="demo-dot"></span>
        Demo-Modus ist <strong>aktiv</strong> — geh zur Zentrale und probiere es aus!
      </div>
    </div>

    <!-- Anthropic API Key -->
    <div class="card">
      <h2>🔑 Anthropic API-Key (Claude)</h2>
      <p class="muted" style="margin-bottom:0.75rem">Hol dir einen Key auf <strong>console.anthropic.com</strong> — startet ab ca. $5 Guthaben. Der Key wird nur lokal in deinem Browser gespeichert.</p>
      <div class="key-row">
        <input v-model="anthropicKey" class="inp" type="password" placeholder="sk-ant-api03-…" autocomplete="off" />
        <button class="btn btn-primary" @click="saveAnthropic">Speichern</button>
        <button v-if="anthropicKey" class="btn btn-ghost" @click="clearAnthropic">✕</button>
      </div>
      <div class="key-indicator" :class="anthropicKey ? 'set' : 'unset'">
        {{ anthropicKey ? '✓ Claude-Key gesetzt' : '○ Kein Key' }}
      </div>
    </div>

    <!-- Gemini API Key -->
    <div class="card">
      <h2>🔑 Google Gemini API-Key (kostenlos)</h2>
      <p class="muted" style="margin-bottom:0.75rem">Hole dir einen kostenlosen Key auf <strong>aistudio.google.com</strong>. Kein Guthaben nötig — Gemini Flash ist gratis.</p>
      <div class="key-row">
        <input v-model="geminiKey" class="inp" type="password" placeholder="AIzaSy…" autocomplete="off" />
        <button class="btn btn-green" @click="saveGemini">Speichern</button>
        <button v-if="geminiKey" class="btn btn-ghost" @click="clearGemini">✕</button>
      </div>
      <div class="key-indicator" :class="geminiKey ? 'set' : 'unset'">
        {{ geminiKey ? '✓ Gemini-Key gesetzt' : '○ Kein Key' }}
      </div>
    </div>

    <!-- Data -->
    <div class="card">
      <h2>🗑️ Daten</h2>
      <p class="muted" style="margin-bottom:0.9rem">Alle Daten werden nur lokal in deinem Browser gespeichert (localStorage). Nichts wird an Server übertragen.</p>
      <div style="display:flex;gap:0.5rem;flex-wrap:wrap">
        <button class="btn btn-ghost btn-sm" @click="clearChat">Chat löschen</button>
        <button class="btn btn-ghost btn-sm" style="color:var(--red);border-color:var(--red)" @click="clearAll">Alle Daten löschen</button>
      </div>
    </div>

    <!-- About -->
    <div class="card">
      <h2>ℹ️ Creator Hub</h2>
      <div class="muted" style="font-size:0.85rem;line-height:1.8">
        <div>Version 2.0 · Multi-Agent KI-System</div>
        <div>4 spezialisierte Agenten: Analyst · Creative · Strategie · Compliance</div>
        <div>Mobile-optimiert (Android + iOS) · Funktioniert offline</div>
        <div style="margin-top:0.5rem">Demo-Modus: gratis · Gemini: gratis · Claude: ab ~$5</div>
      </div>
    </div>

    <div v-if="savedMsg" class="demo-banner" style="position:fixed;bottom:5rem;left:50%;transform:translateX(-50%);z-index:200;white-space:nowrap">
      ✓ {{ savedMsg }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getApiKey, setApiKey, getGeminiKey, setGeminiKey } from '../lib/apiKey'
import { setDemoMode, isDemoMode } from '../lib/demo'

const anthropicKey = ref('')
const geminiKey = ref('')
const demoOn = ref(false)
const savedMsg = ref('')

function showSaved(msg: string) { savedMsg.value = msg; setTimeout(() => savedMsg.value = '', 2200) }

function saveAnthropic() { setApiKey(anthropicKey.value.trim()); showSaved('Claude-Key gespeichert') }
function clearAnthropic() { anthropicKey.value = ''; setApiKey(''); showSaved('Claude-Key gelöscht') }

function saveGemini() { setGeminiKey(geminiKey.value.trim()); showSaved('Gemini-Key gespeichert') }
function clearGemini() { geminiKey.value = ''; setGeminiKey(''); showSaved('Gemini-Key gelöscht') }

function toggleDemo(e: Event) {
  const on = (e.target as HTMLInputElement).checked
  setDemoMode(on); demoOn.value = on
  showSaved(on ? 'Demo-Modus aktiviert' : 'Demo-Modus deaktiviert')
}

function clearChat() { localStorage.removeItem('finaz_chat'); showSaved('Chat gelöscht') }
function clearAll() {
  if (!confirm('Wirklich ALLE Daten löschen? (Keys, Chat, Notizen, Tasks)')) return
  localStorage.clear(); anthropicKey.value = ''; geminiKey.value = ''; demoOn.value = false
  showSaved('Alle Daten gelöscht')
}

onMounted(() => {
  anthropicKey.value = getApiKey()
  geminiKey.value = getGeminiKey()
  demoOn.value = isDemoMode()
})
</script>
