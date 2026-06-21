<template>
  <div class="ai-page hub">
    <div class="page-header hub-header">
      <div>
        <h1>🧠 Zentrale</h1>
        <p class="sub">Deine KI-Zentrale für Online-Creator – Ideen, Skripte &amp; Content-Plan, Wissen und Support per Chat. Jede Anfrage läuft durch das Compliance-Gateway.</p>
      </div>
      <div class="head-actions">
        <button v-if="lastAction" class="btn-ghost" :disabled="busy" :title="lastAction.label" @click="undo">↩ Rückgängig</button>
        <button class="btn-ghost" :disabled="busy" @click="reset">Neuer Chat</button>
      </div>
    </div>

    <div class="dash">
      <RouterLink to="/tasks" class="dash-pill" title="Content-Plan öffnen">
        🎬 <strong>{{ tasks.openCount }}</strong> in Arbeit
      </RouterLink>
      <RouterLink v-if="tasks.overdue.length" to="/tasks" class="dash-pill warn" title="Überfällige Inhalte">
        ⏰ <strong>{{ tasks.overdue.length }}</strong> überfällig
      </RouterLink>
      <RouterLink to="/finance" class="dash-pill" title="Finanzen öffnen">
        💰 Saldo <strong :class="{ neg: finance.balance < 0 }">{{ finance.format(finance.balance) }}</strong>
      </RouterLink>
    </div>

    <RouterLink v-if="!hasKey" to="/settings" class="keyhint">🔑 Kein API-Key gesetzt – hier eintragen (⚙️ Einstellungen)</RouterLink>

    <div ref="scroller" class="msgs">
      <div v-if="!messages.length" class="empty">
        <p>👋 Ich bin deine Zentrale. Frag mich z. B.:</p>
        <div class="suggestions">
          <button v-for="s in suggestions" :key="s" class="chip" :disabled="busy" @click="send(s)">{{ s }}</button>
        </div>
      </div>

      <div v-for="(m, i) in messages" :key="i" class="row" :class="m.role">
        <div class="bubble" :class="m.role">
          <div v-if="m.role === 'assistant'" class="md" v-html="renderAssistant(m.content)"></div>
          <template v-else>{{ m.content }}</template>

          <div v-if="m.role === 'assistant' && parse(m.content).length" class="actions">
            <div v-for="(act, j) in parse(m.content)" :key="j" class="action-card">
              <span class="action-label">⚡ {{ label(act) }}</span>
              <span class="spacer"></span>
              <button v-if="!isDone(i, j)" class="btn xs" :disabled="busy" @click="doAction(i, j, act)">Ausführen</button>
              <span v-else class="done-tag">✓ erledigt</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="pendingAuth" class="auth">
      <strong>⚠ {{ pendingAuth.message }}</strong>
      <p class="muted">Bestätige, dass die Anfrage an den KI-Dienst (Claude) gesendet werden darf.</p>
      <ul><li v-for="(r, i) in pendingAuth.reasons" :key="i">{{ r }}</li></ul>
      <button class="btn" :disabled="busy" @click="authorize">Autorisieren &amp; senden</button>
    </div>

    <div class="composer">
      <textarea
        v-model="input"
        class="chat-input"
        rows="1"
        placeholder="Nachricht an die Zentrale … (Enter sendet · Shift+Enter = neue Zeile)"
        @keydown.enter.exact.prevent="onEnter"
      ></textarea>
      <button class="btn" :disabled="busy || !input.trim()" @click="send(input)">Senden</button>
    </div>
    <p class="status" :class="statusClass">{{ status }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { marked } from 'marked'
import { useTaskStore } from '../stores/tasks'
import type { Task } from '../stores/tasks'
import { useFinanceStore } from '../stores/finance'
import type { Transaction } from '../stores/finance'
import { hasAnyKey } from '../lib/apiKey'
import { runChat, type ChatMessage } from '../lib/chat'
import { buildContext } from '../lib/appState'
import { parseActions, stripActions, actionLabel, executeAction, type ChatAction } from '../lib/actions'

interface Msg {
  role: 'user' | 'assistant'
  content: string
}

interface Snapshot {
  tasks: Task[]
  notes: string
  transactions: Transaction[]
}

const tasks = useTaskStore()
const finance = useFinanceStore()
const router = useRouter()
const hasKey = hasAnyKey()

const SAVE_KEY = 'finaz_chat'
const messages = ref<Msg[]>(load())
const input = ref('')
const busy = ref(false)
const status = ref('')
const pendingAuth = ref<{ message: string; reasons: string[]; text: string } | null>(null)
const done = ref<Set<string>>(new Set())
const lastAction = ref<{ key: string; msgIndex: number; label: string; snapshot: Snapshot } | null>(null)
const scroller = ref<HTMLElement | null>(null)

// Aktionen, die den App-Zustand verändern (Snapshot für Rückgängig).
const MUTATING = new Set(['add_task', 'set_status', 'complete_task', 'reopen_task', 'update_task', 'delete_task', 'append_note', 'add_income', 'add_expense', 'delete_transaction'])

const suggestions = [
  'Analysiere meinen Kanal: 3 Verbesserungen + was die Konkurrenz macht',
  'Gib mir 10 YouTube-Video-Ideen zum Thema Produktivität',
  'Schreibe einen 30-Sekunden-Hook + Skript für ein TikTok',
  'Buche 800€ Sponsoring-Einnahme und zeig mir meinen Saldo',
]

const statusClass = computed(() => {
  if (status.value.includes('blockiert') || status.value.includes('Fehler')) return 'is-block'
  if (status.value.includes('Autorisierung')) return 'is-warn'
  if (status.value.includes('✓')) return 'is-ok'
  return ''
})

function load(): Msg[] {
  try {
    const raw = JSON.parse(localStorage.getItem(SAVE_KEY) || '[]')
    return Array.isArray(raw) ? raw : []
  } catch {
    return []
  }
}
function persist() {
  localStorage.setItem(SAVE_KEY, JSON.stringify(messages.value.slice(-60)))
}
function scrollDown() {
  nextTick(() => {
    const el = scroller.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

function renderAssistant(content: string): string {
  return marked.parse(stripActions(content) || '…') as string
}
function parse(content: string): ChatAction[] {
  return parseActions(content)
}
function label(a: ChatAction): string {
  return actionLabel(a)
}
function isDone(i: number, j: number): boolean {
  return done.value.has(`${i}:${j}`)
}

function onEnter() {
  if (!busy.value && input.value.trim()) send(input.value)
}

async function send(text: string, consent = false) {
  const msg = text.trim()
  if (!msg || busy.value) return

  if (!consent) {
    messages.value.push({ role: 'user', content: msg })
    input.value = ''
  }
  pendingAuth.value = null
  persist()
  scrollDown()

  // Dialog für die KI: alle bisherigen Nachrichten (inkl. angehängter
  // Aktionsergebnisse), ohne die gleich folgende leere Assistenten-Bubble.
  const payload: ChatMessage[] = messages.value
    .filter((m) => m.content.trim())
    .map((m) => ({ role: m.role, content: m.content }))

  messages.value.push({ role: 'assistant', content: '' })
  const aiIndex = messages.value.length - 1
  busy.value = true
  status.value = '… prüft / antwortet'

  const outcome = await runChat({ messages: payload, context: buildContext(tasks, finance), consent }, (delta) => {
    const m = messages.value[aiIndex]
    if (m) {
      m.content += delta
      scrollDown()
    }
  })

  if (outcome.kind === 'done') {
    status.value = `✓ ${outcome.status} · ${outcome.jurisdiction}`
  } else if (outcome.kind === 'needs-auth') {
    messages.value.splice(aiIndex, 1)
    pendingAuth.value = {
      message: outcome.info.error || 'Menschliche Autorisierung erforderlich.',
      reasons: outcome.info.reasons || [],
      text: msg,
    }
    status.value = '⚠ Autorisierung erforderlich'
  } else if (outcome.kind === 'blocked') {
    messages.value[aiIndex].content = `⛔ ${outcome.info.error || 'Blockiert.'}\n\n${(outcome.info.reasons || []).join('\n')}`
    status.value = '⛔ blockiert'
  } else {
    messages.value[aiIndex].content = `⚠ ${outcome.error}`
    status.value = '⚠ Fehler'
  }
  busy.value = false
  persist()
  scrollDown()
}

function authorize() {
  if (pendingAuth.value) send(pendingAuth.value.text, true)
}

async function doAction(i: number, j: number, act: ChatAction) {
  const key = `${i}:${j}`
  if (done.value.has(key) || busy.value) return
  const m = messages.value[i]
  if (!m) return
  const snap = MUTATING.has(act.tool) ? captureState() : null
  try {
    const result = await executeAction(act, { tasks, finance, router })
    done.value.add(key)
    // Ergebnis an die Assistenten-Nachricht anhängen → es bleibt Teil des
    // Dialogs, die KI kennt in der nächsten Runde den neuen Stand.
    m.content += `\n\n_✅ Ausgeführt: ${result}_`
    if (snap) lastAction.value = { key, msgIndex: i, label: actionLabel(act), snapshot: snap }
    status.value = '✓ Aktion ausgeführt'
  } catch (err) {
    m.content += `\n\n_⚠ Aktion fehlgeschlagen: ${(err as Error).message}_`
    status.value = '⚠ Fehler'
  }
  persist()
  scrollDown()
}

function captureState(): Snapshot {
  return {
    tasks: JSON.parse(JSON.stringify(tasks.tasks)) as Task[],
    notes: localStorage.getItem('finaz_notes') || '',
    transactions: JSON.parse(JSON.stringify(finance.transactions)) as Transaction[],
  }
}

function undo() {
  const la = lastAction.value
  if (!la || busy.value) return
  tasks.setAll(la.snapshot.tasks)
  finance.setAll(la.snapshot.transactions)
  localStorage.setItem('finaz_notes', la.snapshot.notes)
  done.value.delete(la.key)
  const m = messages.value[la.msgIndex]
  if (m) m.content += `\n\n_↩ Rückgängig gemacht: ${la.label}_`
  status.value = '↩ Rückgängig gemacht'
  lastAction.value = null
  persist()
  scrollDown()
}

function reset() {
  messages.value = []
  done.value = new Set()
  lastAction.value = null
  pendingAuth.value = null
  status.value = ''
  input.value = ''
  persist()
}

// Vom Kanal-Check übergebene Analyse-Aufforderung automatisch starten.
onMounted(() => {
  const pending = localStorage.getItem('finaz_pending_prompt')
  if (!pending) return
  localStorage.removeItem('finaz_pending_prompt')
  if (hasKey) send(pending)
  else input.value = pending
})
</script>

<style scoped>
.hub-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; }
.head-actions { display: flex; gap: 0.5rem; flex-shrink: 0; }

.dash { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem; }
.dash-pill {
  display: inline-flex; align-items: center; gap: 0.35rem;
  padding: 0.4rem 0.8rem; border-radius: 999px;
  border: 1px solid #334155; background: #1e293b; color: #cbd5e1;
  text-decoration: none; font-size: 0.85rem;
}
.dash-pill:hover { border-color: #60a5fa; color: #e2e8f0; }
.dash-pill strong { color: #e2e8f0; }
.dash-pill.warn { border-color: #6b2c2c; color: #fca5a5; }
.dash-pill strong.neg { color: #f87171; }

.msgs {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 1rem;
  min-height: 320px;
  max-height: 60vh;
  overflow: auto;
}
.empty { margin: auto; text-align: center; color: #94a3b8; }
.suggestions { display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; margin-top: 0.75rem; }
.chip {
  padding: 0.45rem 0.8rem;
  border-radius: 999px;
  border: 1px solid #334155;
  background: #1e293b;
  color: #cbd5e1;
  cursor: pointer;
  font-size: 0.82rem;
}
.chip:hover { border-color: #60a5fa; }
.chip:disabled { opacity: 0.5; cursor: not-allowed; }

.row { display: flex; }
.row.user { justify-content: flex-end; }
.bubble {
  max-width: 85%;
  padding: 0.7rem 0.9rem;
  border-radius: 12px;
  line-height: 1.5;
  word-break: break-word;
}
.bubble.user { background: #3b82f6; color: #fff; border-bottom-right-radius: 4px; white-space: pre-wrap; }
.bubble.assistant { background: #1e293b; color: #e2e8f0; border: 1px solid #334155; border-bottom-left-radius: 4px; }

.bubble .md :first-child { margin-top: 0; }
.bubble .md :last-child { margin-bottom: 0; }
.bubble .md :is(h1, h2, h3) { font-size: 1.05rem; margin: 0.6rem 0 0.3rem; }
.bubble .md p { margin: 0.4rem 0; }
.bubble .md ul, .bubble .md ol { margin: 0.3rem 0 0.3rem 1.1rem; }
.bubble .md code { background: #0f172a; padding: 0.1rem 0.3rem; border-radius: 4px; font-size: 0.85em; }
.bubble .md table { border-collapse: collapse; }
.bubble .md th, .bubble .md td { border: 1px solid #334155; padding: 0.25rem 0.5rem; }

.actions { margin-top: 0.6rem; display: flex; flex-direction: column; gap: 0.4rem; }
.action-card {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.7rem;
  border: 1px dashed #f59e0b;
  background: rgba(245, 158, 11, 0.08);
  border-radius: 8px;
}
.action-label { font-size: 0.85rem; color: #fcd34d; }
.action-card .spacer { flex: 1; }
.btn.xs { padding: 0.3rem 0.6rem; font-size: 0.8rem; }
.done-tag { color: #34d399; font-size: 0.82rem; white-space: nowrap; }

.composer { display: flex; gap: 0.5rem; margin-top: 0.75rem; align-items: flex-end; }
.chat-input {
  flex: 1;
  resize: vertical;
  min-height: 46px;
  max-height: 160px;
  padding: 0.6rem 0.8rem;
  border-radius: 10px;
  border: 1px solid #334155;
  background: #0f172a;
  color: #e2e8f0;
  font-family: inherit;
  font-size: 0.95rem;
  line-height: 1.5;
}
.composer .btn { height: 46px; }
.status { min-height: 1.2em; margin-top: 0.4rem; }
</style>
