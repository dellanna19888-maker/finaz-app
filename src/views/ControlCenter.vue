<template>
  <div class="page">
    <div class="page-header" style="display:flex;align-items:flex-start;justify-content:space-between;gap:1rem">
      <div>
        <h1>🧠 KI-Zentrale</h1>
        <p class="sub">4 spezialisierte Agenten — Analyse, Content, Skript &amp; Strategie.</p>
      </div>
      <div style="display:flex;gap:0.5rem;flex-shrink:0;padding-top:0.25rem">
        <button v-if="lastAction" class="btn btn-ghost btn-sm" :disabled="busy" @click="undo">↩ Rückgängig</button>
        <button class="btn btn-ghost btn-sm" :disabled="busy" @click="reset">Neuer Chat</button>
      </div>
    </div>

    <div v-if="demo" class="demo-banner">
      <span class="demo-dot"></span>
      <strong>Demo-Modus</strong> — kostenlos &amp; ohne API-Key. Echte KI → ⚙️ Einstellungen.
    </div>

    <RouterLink v-if="!hasKey && !demo && serverKey === false" to="/settings" class="keyhint">
      🔑 Kein API-Key — hier eintragen oder Demo-Modus aktivieren (kostenlos).
    </RouterLink>

    <!-- 4 Agent cards -->
    <div class="agent-grid">
      <div v-for="ag in agents" :key="ag.id" class="agent-card"
           :class="{ active: ag.state === 'running', done: ag.state === 'done' }">
        <div class="agent-head">
          <span class="agent-icon">{{ ag.icon }}</span>
          <div>
            <div class="agent-name">{{ ag.name }}</div>
            <div class="agent-role">{{ ag.role }}</div>
          </div>
        </div>
        <div class="agent-status">
          <span v-if="ag.state === 'running'" class="spin"></span>
          <span v-else-if="ag.state === 'done'" style="color:var(--green)">✓</span>
          {{ ag.statusText }}
        </div>
        <div v-if="ag.preview" class="agent-output">{{ ag.preview }}</div>
      </div>
    </div>

    <!-- Messages -->
    <div ref="scroller" class="msgs">
      <div v-if="!messages.length" class="empty-chat">
        <p>Frag die Zentrale — alle 4 Agenten antworten sofort:</p>
        <div class="suggestions">
          <button v-for="s in suggestions" :key="s" class="chip" :disabled="busy" @click="send(s)">{{ s }}</button>
        </div>
      </div>

      <div v-for="(m, i) in messages" :key="i" class="msg-row" :class="m.role">
        <div class="bubble" :class="m.role">
          <div v-if="m.role !== 'user'" class="md" v-html="renderMd(m.content)"></div>
          <template v-else>{{ m.content }}</template>

          <div v-if="m.role === 'assistant' && parseActs(m.content).length" class="action-cards">
            <div v-for="(act, j) in parseActs(m.content)" :key="j" class="action-card">
              <span class="action-label">⚡ {{ actLabel(act) }}</span>
              <button v-if="!isDone(i, j)" class="btn btn-ghost btn-sm" :disabled="busy" @click="doAction(i, j, act)">Ausführen</button>
              <span v-else class="done-tag">✓ erledigt</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Auth -->
    <div v-if="pendingAuth" class="auth-overlay">
      <strong>⚠ {{ pendingAuth.message }}</strong>
      <p class="muted" style="margin:0.35rem 0">Die Anfrage benötigt deine Zustimmung.</p>
      <ul><li v-for="(r, k) in pendingAuth.reasons" :key="k">{{ r }}</li></ul>
      <button class="btn btn-primary" :disabled="busy" @click="authorize" style="margin-top:0.6rem">Autorisieren &amp; senden</button>
    </div>

    <!-- Composer -->
    <div class="composer" style="margin-top:0.75rem">
      <textarea v-model="input" class="chat-input" rows="1"
        placeholder="Frag die Zentrale … (Enter sendet · Shift+Enter = neue Zeile)"
        @keydown.enter.exact.prevent="onEnter"></textarea>
      <button class="btn btn-primary" :disabled="busy || !input.trim()" @click="send(input)">
        <span v-if="busy" class="spin"></span>
        <template v-else>Senden</template>
      </button>
    </div>
    <div class="status-bar" :class="statusCls">{{ status }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { marked } from 'marked'
import { useTaskStore } from '../stores/tasks'
import type { Task } from '../stores/tasks'
import { hasAnyKey, hasServerKey } from '../lib/apiKey'
import { runChat, type ChatMessage } from '../lib/chat'
import { buildContext } from '../lib/appState'
import { parseActions, stripActions, actionLabel, executeAction, type ChatAction } from '../lib/actions'
import { isDemoMode, demoChat } from '../lib/demo'

interface Msg { role: 'user' | 'assistant' | 'system'; content: string }
interface AgentState { id: string; icon: string; name: string; role: string; state: 'idle'|'running'|'done'; statusText: string; preview: string }
interface Snapshot { tasks: Task[]; notes: string }

const tasks = useTaskStore()
const router = useRouter()
const hasKey = hasAnyKey()
const demo = ref(isDemoMode())
const serverKey = ref<boolean | null>(null)

const agents = ref<AgentState[]>([
  { id: 'analyst',    icon: '🔍', name: 'Analyst',    role: 'Kanal-Analyse & Daten', state: 'idle', statusText: 'Bereit', preview: '' },
  { id: 'creative',   icon: '✍️',  name: 'Creative',   role: 'Hooks & Skripte',       state: 'idle', statusText: 'Bereit', preview: '' },
  { id: 'strategy',   icon: '📈', name: 'Strategie',  role: 'Plan & Trends',          state: 'idle', statusText: 'Bereit', preview: '' },
  { id: 'compliance', icon: '🛡️', name: 'Compliance', role: 'Rechtliche Prüfung',    state: 'idle', statusText: 'Bereit', preview: '' },
])

const SAVE_KEY = 'finaz_chat'
const messages = ref<Msg[]>(loadMsgs())
const input = ref('')
const busy = ref(false)
const status = ref('')
const pendingAuth = ref<{ message: string; reasons: string[]; text: string } | null>(null)
const done = ref<Set<string>>(new Set())
const lastAction = ref<{ key: string; msgIndex: number; label: string; snapshot: Snapshot } | null>(null)
const scroller = ref<HTMLElement | null>(null)

const suggestions = [
  'Analysiere meinen Kanal: 3 Verbesserungen + Konkurrenz',
  '10 Video-Ideen für Produktivität & KI',
  'Schreib einen 30-Sek-Hook für TikTok',
  'Erstelle meinen Content-Plan für diese Woche',
]

const statusCls = computed(() => {
  if (status.value.includes('blockiert') || status.value.includes('Fehler')) return 'err'
  if (status.value.includes('Autorisierung')) return 'warn'
  if (status.value.includes('✓')) return 'ok'
  return ''
})

function loadMsgs(): Msg[] { try { return JSON.parse(localStorage.getItem(SAVE_KEY) || '[]') || [] } catch { return [] } }
function persist() { localStorage.setItem(SAVE_KEY, JSON.stringify(messages.value.slice(-60))) }
function scrollDown() { nextTick(() => { if (scroller.value) scroller.value.scrollTop = scroller.value.scrollHeight }) }
function renderMd(c: string) { return marked.parse(stripActions(c) || '…') as string }
function parseActs(c: string) { return parseActions(c) }
function actLabel(a: ChatAction) { return actionLabel(a) }
function isDone(i: number, j: number) { return done.value.has(`${i}:${j}`) }
function onEnter() { if (!busy.value && input.value.trim()) send(input.value) }
function setAg(id: string, state: AgentState['state'], statusText: string, preview = '') {
  const ag = agents.value.find(a => a.id === id); if (ag) { ag.state = state; ag.statusText = statusText; ag.preview = preview }
}
function resetAgents() { agents.value.forEach(ag => { ag.state = 'idle'; ag.statusText = 'Bereit'; ag.preview = '' }) }

async function send(text: string, consent = false) {
  const msg = text.trim(); if (!msg || busy.value) return
  demo.value = isDemoMode()
  if (!consent) { messages.value.push({ role: 'user', content: msg }); input.value = '' }
  pendingAuth.value = null; persist(); scrollDown()
  messages.value.push({ role: 'assistant', content: '' })
  const aiIdx = messages.value.length - 1
  busy.value = true; status.value = '… denkt nach'; resetAgents()

  if (demo.value) {
    setAg('analyst', 'running', 'analysiert…'); await sleep(700)
    setAg('analyst', 'done', 'fertig ✓', 'Kanal-Daten ausgewertet')
    setAg('creative', 'running', 'schreibt…'); await sleep(400)
    setAg('creative', 'done', 'fertig ✓', 'Hook-Varianten bereit')
    setAg('strategy', 'running', 'plant…')
    await demoChat(msg, (d) => { const m = messages.value[aiIdx]; if (m) { m.content += d; scrollDown() } })
    setAg('strategy', 'done', 'fertig ✓', 'Plan erstellt')
    setAg('compliance', 'done', 'geprüft ✓', 'Keine Verstöße')
    status.value = '✓ Demo-Antwort (4 Agenten)'
  } else {
    const payload: ChatMessage[] = messages.value
      .filter(m => m.content.trim() && m.role !== 'system').slice(0, -1)
      .map(m => ({ role: m.role as 'user'|'assistant', content: m.content }))
    setAg('analyst', 'running', 'analysiert…'); setAg('compliance', 'running', 'prüft…')
    const outcome = await runChat(
      { messages: payload, context: buildContext(tasks), consent },
      (d) => { const m = messages.value[aiIdx]; if (m) { m.content += d; scrollDown() }; setAg('creative','running','generiert…'); setAg('strategy','running','plant…') }
    )
    if (outcome.kind === 'done') {
      agents.value.forEach(ag => setAg(ag.id, 'done', 'fertig ✓'))
      status.value = `✓ ${outcome.status} · ${outcome.jurisdiction}`
    } else if (outcome.kind === 'needs-auth') {
      messages.value.splice(aiIdx, 1)
      pendingAuth.value = { message: outcome.info.error || 'Autorisierung nötig.', reasons: outcome.info.reasons || [], text: msg }
      status.value = '⚠ Autorisierung erforderlich'; resetAgents()
    } else if (outcome.kind === 'blocked') {
      messages.value[aiIdx].content = `⛔ ${outcome.info.error}\n\n${(outcome.info.reasons||[]).join('\n')}`
      status.value = '⛔ blockiert'; resetAgents()
    } else {
      messages.value[aiIdx].content = `⚠ ${outcome.error}`
      status.value = '⚠ Fehler'; resetAgents()
    }
  }
  busy.value = false; persist(); scrollDown()
}

function authorize() { if (pendingAuth.value) send(pendingAuth.value.text, true) }

const MUTATING = new Set(['add_task','set_status','complete_task','reopen_task','update_task','delete_task','append_note'])
async function doAction(i: number, j: number, act: ChatAction) {
  const key = `${i}:${j}`; if (done.value.has(key) || busy.value) return
  const m = messages.value[i]; if (!m) return
  const snap = MUTATING.has(act.tool) ? captureState() : null
  try {
    const result = await executeAction(act, { tasks, router })
    done.value.add(key); m.content += `\n\n_✅ Ausgeführt: ${result}_`
    if (snap) lastAction.value = { key, msgIndex: i, label: actionLabel(act), snapshot: snap }
    status.value = '✓ Aktion ausgeführt'
  } catch (err) {
    m.content += `\n\n_⚠ Fehler: ${(err as Error).message}_`; status.value = '⚠ Fehler'
  }
  persist(); scrollDown()
}

function captureState(): Snapshot {
  return { tasks: JSON.parse(JSON.stringify(tasks.tasks)) as Task[], notes: localStorage.getItem('finaz_notes') || '' }
}
function undo() {
  const la = lastAction.value; if (!la || busy.value) return
  tasks.setAll(la.snapshot.tasks); localStorage.setItem('finaz_notes', la.snapshot.notes)
  done.value.delete(la.key)
  const m = messages.value[la.msgIndex]; if (m) m.content += `\n\n_↩ Rückgängig: ${la.label}_`
  status.value = '↩ Rückgängig'; lastAction.value = null; persist(); scrollDown()
}
function reset() {
  messages.value = []; done.value = new Set(); lastAction.value = null
  pendingAuth.value = null; status.value = ''; input.value = ''; resetAgents(); persist()
}
function sleep(ms: number) { return new Promise(r => setTimeout(r, ms)) }

onMounted(async () => {
  // Prüfen, ob der Server einen KI-Key hat (vermarktete Besucher brauchen dann keinen eigenen).
  serverKey.value = await hasServerKey()
  const p = localStorage.getItem('finaz_pending_prompt'); if (!p) return
  localStorage.removeItem('finaz_pending_prompt')
  if (hasKey || isDemoMode() || serverKey.value) send(p); else input.value = p
})
</script>
