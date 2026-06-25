<template>
  <div class="jaris-page">
    <!-- HUD-Ecken -->
    <div class="hud-corner top-left"></div>
    <div class="hud-corner top-right"></div>
    <div class="hud-corner bottom-left"></div>
    <div class="hud-corner bottom-right"></div>

    <!-- Header -->
    <div class="jaris-header">
      <div class="arc-reactor" :class="{ active: busy }">
        <div class="arc-ring ring-1"></div>
        <div class="arc-ring ring-2"></div>
        <div class="arc-ring ring-3"></div>
        <div class="arc-core">
          <span class="arc-icon">⚡</span>
        </div>
      </div>
      <div class="jaris-title">
        <h1>J.A.R.I.S.</h1>
        <p class="jaris-sub">Just A Rather Intelligent System <span class="ver">v3.1</span></p>
        <div class="status-bar">
          <span class="dot" :class="busy ? 'blink' : 'on'"></span>
          <span class="status-text">{{ busy ? 'VERARBEITE…' : 'BEREIT' }}</span>
          <span class="sep">|</span>
          <span class="sys-text">SYSTEM ONLINE</span>
        </div>
      </div>
      <button class="reset-btn" :disabled="busy" @click="reset" title="Neues Gespräch">⟳ RESET</button>
    </div>

    <RouterLink v-if="!hasKey" to="/settings" class="key-warning">
      ⚠ KEIN API-SCHLÜSSEL — Einstellungen öffnen
    </RouterLink>

    <!-- Chat-Fenster -->
    <div ref="scroller" class="chat-window">
      <div v-if="!messages.length" class="boot-screen">
        <p class="boot-line">JARIS-SYSTEM INITIALISIERT…</p>
        <p class="boot-line">VERBINDUNG ZU KI-KERN HERGESTELLT…</p>
        <p class="boot-line highlight">GUTEN TAG, SIR. WIE KANN ICH IHNEN BEHILFLICH SEIN?</p>
        <div class="suggestions">
          <button
            v-for="s in suggestions"
            :key="s.cmd"
            class="cmd-chip"
            :disabled="busy"
            @click="send(s.cmd)"
          >
            <span class="cmd-icon">{{ s.icon }}</span>
            <span>{{ s.label }}</span>
          </button>
        </div>
      </div>

      <div v-for="(m, i) in messages" :key="i" class="msg-row" :class="m.role">
        <div class="msg-prefix">{{ m.role === 'user' ? '› SIR' : '‹ JARIS' }}</div>
        <div class="msg-bubble" :class="m.role">
          <div v-if="m.role === 'assistant'" class="md" v-html="renderMd(m.content)"></div>
          <template v-else>{{ m.content }}</template>
        </div>
      </div>

      <div v-if="busy" class="thinking-row">
        <div class="msg-prefix">‹ JARIS</div>
        <div class="thinking">
          <span class="dot-anim"></span>
          <span class="dot-anim d2"></span>
          <span class="dot-anim d3"></span>
          <span class="think-text">ANALYSIERE…</span>
        </div>
      </div>
    </div>

    <!-- Autorisierungs-Banner -->
    <div v-if="pendingAuth" class="auth-banner">
      <span class="auth-icon">⚠</span>
      <div class="auth-body">
        <strong>{{ pendingAuth.message }}</strong>
        <p>Bestätigung erforderlich, um die Anfrage an den KI-Kern weiterzuleiten.</p>
        <ul><li v-for="(r, i) in pendingAuth.reasons" :key="i">{{ r }}</li></ul>
      </div>
      <button class="auth-btn" :disabled="busy" @click="authorize">AUTORISIEREN</button>
    </div>

    <!-- Eingabebereich -->
    <div class="composer">
      <div class="composer-inner">
        <span class="input-prefix">&gt;_</span>
        <textarea
          ref="inputEl"
          v-model="input"
          class="jaris-input"
          rows="1"
          placeholder="Befehl eingeben, Sir …"
          :disabled="busy"
          @keydown.enter.exact.prevent="onEnter"
          @input="autoGrow"
        ></textarea>
        <button class="send-btn" :disabled="busy || !input.trim()" @click="send(input)">
          {{ busy ? '…' : '▶' }}
        </button>
      </div>
      <p class="bottom-status" :class="statusClass">{{ status }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { marked } from 'marked'
import { hasAnyKey } from '../lib/apiKey'
import { runJaris, type JarisMessage } from '../lib/jaris'

interface Msg {
  role: 'user' | 'assistant'
  content: string
}

const SAVE_KEY = 'finaz_jaris'

const hasKey = hasAnyKey()
const messages = ref<Msg[]>(load())
const input = ref('')
const busy = ref(false)
const status = ref('')
const pendingAuth = ref<{ message: string; reasons: string[]; text: string } | null>(null)
const scroller = ref<HTMLElement | null>(null)
const inputEl = ref<HTMLTextAreaElement | null>(null)

const suggestions = [
  { icon: '🎯', label: 'Strategie-Briefing', cmd: 'Erstelle ein vollständiges Strategie-Briefing für meinen Content-Kanal mit konkreten Maßnahmen.' },
  { icon: '📊', label: 'Daten analysieren', cmd: 'Analysiere meine aktuelle Situation und gib mir die 3 wichtigsten Handlungsempfehlungen.' },
  { icon: '⚡', label: 'Schnell-Plan', cmd: 'Generiere einen Schnell-Aktionsplan für diese Woche – priorisiert und umsetzbar.' },
  { icon: '🛡️', label: 'Risiko-Check', cmd: 'Führe einen Risiko-Check durch: Was könnte schiefgehen und wie verhindere ich es?' },
]

const statusClass = computed(() => {
  if (status.value.includes('FEHLER') || status.value.includes('BLOCKIERT')) return 'err'
  if (status.value.includes('AUTH')) return 'warn'
  if (status.value.includes('✓') || status.value.includes('BEREIT')) return 'ok'
  return ''
})

function load(): Msg[] {
  try {
    const raw = JSON.parse(localStorage.getItem(SAVE_KEY) || '[]')
    return Array.isArray(raw) ? raw : []
  } catch { return [] }
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

function renderMd(content: string): string {
  return marked.parse(content || '…') as string
}

function autoGrow() {
  const el = inputEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 160) + 'px'
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
    nextTick(() => {
      if (inputEl.value) inputEl.value.style.height = 'auto'
    })
  }
  pendingAuth.value = null
  persist()
  scrollDown()

  const payload: JarisMessage[] = messages.value
    .filter((m) => m.content.trim())
    .map((m) => ({ role: m.role, content: m.content }))

  messages.value.push({ role: 'assistant', content: '' })
  const aiIdx = messages.value.length - 1
  busy.value = true
  status.value = 'JARIS VERARBEITET…'

  const outcome = await runJaris({ messages: payload, consent }, (delta) => {
    const m = messages.value[aiIdx]
    if (m) {
      m.content += delta
      scrollDown()
    }
  })

  if (outcome.kind === 'done') {
    status.value = `✓ BEREIT · ${outcome.status}`
  } else if (outcome.kind === 'needs-auth') {
    messages.value.splice(aiIdx, 1)
    pendingAuth.value = {
      message: outcome.info.error || 'Menschliche Autorisierung erforderlich.',
      reasons: outcome.info.reasons || [],
      text: msg,
    }
    status.value = '⚠ AUTH ERFORDERLICH'
  } else if (outcome.kind === 'blocked') {
    messages.value[aiIdx].content = `⛔ ${outcome.info.error || 'Anfrage blockiert.'}\n\n${(outcome.info.reasons || []).join('\n')}`
    status.value = '⛔ BLOCKIERT'
  } else {
    messages.value[aiIdx].content = `⚠ Systemfehler: ${outcome.error}`
    status.value = '⚠ FEHLER'
  }

  busy.value = false
  persist()
  scrollDown()
}

function authorize() {
  if (pendingAuth.value) send(pendingAuth.value.text, true)
}

function reset() {
  messages.value = []
  pendingAuth.value = null
  status.value = ''
  input.value = ''
  persist()
}
</script>

<style scoped>
/* ---- Grundlayout ---- */
.jaris-page {
  min-height: 100vh;
  background: #080c14;
  color: #a8d8ea;
  font-family: 'Courier New', Courier, monospace;
  display: flex;
  flex-direction: column;
  padding: 1.5rem 2rem;
  max-width: 1000px;
  margin: 0 auto;
  position: relative;
  gap: 1rem;
}

/* ---- HUD-Ecken ---- */
.hud-corner {
  position: fixed;
  width: 40px;
  height: 40px;
  pointer-events: none;
  z-index: 0;
}
.hud-corner.top-left    { top: 68px; left: 12px; border-top: 2px solid #c0392b; border-left: 2px solid #c0392b; }
.hud-corner.top-right   { top: 68px; right: 12px; border-top: 2px solid #c0392b; border-right: 2px solid #c0392b; }
.hud-corner.bottom-left { bottom: 8px; left: 12px; border-bottom: 2px solid #c0392b; border-left: 2px solid #c0392b; }
.hud-corner.bottom-right{ bottom: 8px; right: 12px; border-bottom: 2px solid #c0392b; border-right: 2px solid #c0392b; }

/* ---- Header ---- */
.jaris-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  border-bottom: 1px solid #1e3a5a;
  padding-bottom: 1rem;
}

/* Arc Reactor */
.arc-reactor {
  position: relative;
  width: 64px;
  height: 64px;
  flex-shrink: 0;
}
.arc-ring {
  position: absolute;
  border-radius: 50%;
  border: 2px solid rgba(192,57,43,0.4);
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  animation: spin 8s linear infinite;
}
.ring-1 { width: 64px; height: 64px; border-color: rgba(192,57,43,0.5); animation-duration: 6s; }
.ring-2 { width: 48px; height: 48px; border-color: rgba(231,76,60,0.6); animation-duration: 4s; animation-direction: reverse; }
.ring-3 { width: 32px; height: 32px; border-color: rgba(255,100,80,0.7); animation-duration: 3s; }
.arc-reactor.active .ring-1 { border-color: rgba(52,152,219,0.7); animation-duration: 1s; }
.arc-reactor.active .ring-2 { border-color: rgba(41,128,185,0.8); animation-duration: 0.8s; }
.arc-reactor.active .ring-3 { border-color: rgba(100,200,255,0.9); animation-duration: 0.6s; }
.arc-core {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 22px; height: 22px;
  background: radial-gradient(circle, #c0392b 0%, #7b1a0c 80%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 12px #e74c3c, 0 0 24px rgba(231,76,60,0.3);
  transition: all 0.3s;
}
.arc-reactor.active .arc-core {
  background: radial-gradient(circle, #5dade2 0%, #1a5276 80%);
  box-shadow: 0 0 16px #3498db, 0 0 32px rgba(52,152,219,0.5);
}
.arc-icon { font-size: 0.75rem; line-height: 1; }

@keyframes spin { to { transform: translate(-50%, -50%) rotate(360deg); } }

.jaris-title { flex: 1; }
.jaris-title h1 {
  font-size: 2rem;
  font-weight: 900;
  letter-spacing: 0.15em;
  color: #e74c3c;
  text-shadow: 0 0 20px rgba(231,76,60,0.6), 0 0 40px rgba(231,76,60,0.2);
  margin: 0;
  line-height: 1;
}
.jaris-sub {
  font-size: 0.72rem;
  color: #6c8ea4;
  letter-spacing: 0.05em;
  margin: 0.2rem 0 0.4rem;
}
.ver { color: #c0392b; font-size: 0.65rem; }
.status-bar { display: flex; align-items: center; gap: 0.5rem; font-size: 0.68rem; letter-spacing: 0.08em; }
.dot { width: 7px; height: 7px; border-radius: 50%; background: #c0392b; }
.dot.on { background: #27ae60; box-shadow: 0 0 6px #27ae60; }
.dot.blink { background: #f39c12; box-shadow: 0 0 6px #f39c12; animation: blink 0.8s infinite; }
@keyframes blink { 50% { opacity: 0.3; } }
.status-text { color: #e8e8e8; }
.sep { color: #1e3a5a; }
.sys-text { color: #4a6a7a; }

.reset-btn {
  background: transparent;
  border: 1px solid #c0392b;
  color: #e74c3c;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  transition: all 0.2s;
}
.reset-btn:hover { background: rgba(192,57,43,0.15); box-shadow: 0 0 8px rgba(231,76,60,0.3); }
.reset-btn:disabled { opacity: 0.3; cursor: not-allowed; }

/* ---- Key Warning ---- */
.key-warning {
  display: block;
  padding: 0.5rem 1rem;
  border: 1px solid #7b1a0c;
  background: rgba(192,57,43,0.1);
  color: #e74c3c;
  border-radius: 4px;
  text-decoration: none;
  font-size: 0.78rem;
  letter-spacing: 0.06em;
  text-align: center;
  animation: blink 2s infinite;
}

/* ---- Chat-Fenster ---- */
.chat-window {
  flex: 1;
  min-height: 300px;
  max-height: 55vh;
  overflow-y: auto;
  border: 1px solid #1e3a5a;
  border-top: 2px solid #c0392b;
  background: rgba(8,12,20,0.9);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  scrollbar-width: thin;
  scrollbar-color: #c0392b #080c14;
}
.chat-window::-webkit-scrollbar { width: 5px; }
.chat-window::-webkit-scrollbar-thumb { background: #c0392b; border-radius: 2px; }

/* Boot Screen */
.boot-screen { margin: auto; text-align: center; padding: 1rem; }
.boot-line {
  font-size: 0.75rem;
  color: #4a6a7a;
  letter-spacing: 0.1em;
  margin: 0.3rem 0;
  text-transform: uppercase;
}
.boot-line.highlight {
  color: #e74c3c;
  font-size: 0.85rem;
  text-shadow: 0 0 10px rgba(231,76,60,0.5);
  margin: 0.8rem 0;
}
.suggestions { display: flex; flex-wrap: wrap; gap: 0.6rem; justify-content: center; margin-top: 1.2rem; }
.cmd-chip {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 0.9rem;
  border: 1px solid #1e3a5a;
  background: rgba(30,58,90,0.3);
  color: #a8d8ea;
  border-radius: 3px;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.75rem;
  letter-spacing: 0.04em;
  transition: all 0.2s;
}
.cmd-chip:hover { border-color: #c0392b; color: #e74c3c; background: rgba(192,57,43,0.1); }
.cmd-chip:disabled { opacity: 0.4; cursor: not-allowed; }
.cmd-icon { font-size: 1rem; }

/* Messages */
.msg-row { display: flex; flex-direction: column; gap: 0.2rem; }
.msg-row.user { align-items: flex-end; }
.msg-row.assistant { align-items: flex-start; }
.msg-prefix {
  font-size: 0.62rem;
  letter-spacing: 0.12em;
  color: #4a6a7a;
  padding: 0 0.4rem;
}
.msg-row.user .msg-prefix { color: #8b3a3a; }

.msg-bubble {
  max-width: 82%;
  padding: 0.65rem 0.9rem;
  border-radius: 2px;
  line-height: 1.55;
  font-size: 0.88rem;
  word-break: break-word;
}
.msg-bubble.user {
  background: rgba(192,57,43,0.15);
  border: 1px solid rgba(192,57,43,0.4);
  color: #f5b7b1;
  border-top-right-radius: 0;
}
.msg-bubble.assistant {
  background: rgba(30,58,90,0.4);
  border: 1px solid #1e3a5a;
  color: #d6eaf8;
  border-top-left-radius: 0;
}

/* Markdown in assistant bubble */
.md :first-child { margin-top: 0; }
.md :last-child { margin-bottom: 0; }
.md p { margin: 0.4rem 0; }
.md h1, .md h2, .md h3 { color: #e74c3c; font-size: 0.95rem; margin: 0.6rem 0 0.3rem; letter-spacing: 0.04em; }
.md ul, .md ol { margin: 0.3rem 0 0.3rem 1.1rem; }
.md li { margin: 0.15rem 0; }
.md strong { color: #f5cba7; }
.md code { background: rgba(8,12,20,0.8); border: 1px solid #1e3a5a; padding: 0.1rem 0.3rem; border-radius: 2px; font-size: 0.82em; color: #a9cce3; }
.md pre { background: rgba(8,12,20,0.9); border: 1px solid #1e3a5a; padding: 0.7rem; border-radius: 2px; overflow: auto; margin: 0.4rem 0; }
.md pre code { background: none; border: none; padding: 0; }
.md blockquote { border-left: 3px solid #c0392b; margin: 0.4rem 0; padding-left: 0.7rem; color: #7f8c8d; }
.md table { border-collapse: collapse; width: 100%; font-size: 0.82em; }
.md th, .md td { border: 1px solid #1e3a5a; padding: 0.3rem 0.5rem; }
.md th { color: #e74c3c; }

/* Thinking animation */
.thinking-row { display: flex; flex-direction: column; gap: 0.2rem; align-items: flex-start; }
.thinking {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 0.8rem;
  border: 1px solid #1e3a5a;
  background: rgba(30,58,90,0.3);
  border-radius: 2px;
}
.dot-anim {
  width: 6px; height: 6px;
  background: #3498db;
  border-radius: 50%;
  animation: pulse-dot 1.2s ease-in-out infinite;
}
.dot-anim.d2 { animation-delay: 0.2s; }
.dot-anim.d3 { animation-delay: 0.4s; }
@keyframes pulse-dot { 0%, 80%, 100% { opacity: 0.2; transform: scale(0.8); } 40% { opacity: 1; transform: scale(1.2); } }
.think-text { font-size: 0.7rem; letter-spacing: 0.1em; color: #5dade2; }

/* ---- Auth Banner ---- */
.auth-banner {
  display: flex;
  align-items: flex-start;
  gap: 0.8rem;
  padding: 0.8rem 1rem;
  border: 1px solid #7b1a0c;
  background: rgba(192,57,43,0.12);
  border-radius: 2px;
}
.auth-icon { font-size: 1.2rem; flex-shrink: 0; }
.auth-body { flex: 1; font-size: 0.82rem; }
.auth-body strong { color: #e74c3c; }
.auth-body p { color: #a8d8ea; margin: 0.3rem 0; }
.auth-body ul { margin: 0.2rem 0; padding-left: 1rem; color: #a8d8ea; }
.auth-btn {
  background: #c0392b;
  border: none;
  color: #fff;
  padding: 0.45rem 0.8rem;
  border-radius: 3px;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.72rem;
  letter-spacing: 0.1em;
  font-weight: 700;
  white-space: nowrap;
  flex-shrink: 0;
  transition: background 0.2s;
}
.auth-btn:hover { background: #e74c3c; }
.auth-btn:disabled { opacity: 0.4; cursor: not-allowed; }

/* ---- Composer ---- */
.composer { display: flex; flex-direction: column; gap: 0.3rem; }
.composer-inner {
  display: flex;
  align-items: flex-end;
  gap: 0;
  border: 1px solid #1e3a5a;
  border-top: 2px solid #c0392b;
  background: rgba(8,12,20,0.95);
  border-radius: 2px;
  padding: 0.5rem 0.7rem;
  gap: 0.5rem;
}
.composer-inner:focus-within { border-color: #c0392b; box-shadow: 0 0 10px rgba(231,76,60,0.2); }
.input-prefix { color: #c0392b; font-size: 0.9rem; line-height: 1; padding-bottom: 2px; flex-shrink: 0; }
.jaris-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #d6eaf8;
  font-family: inherit;
  font-size: 0.88rem;
  line-height: 1.5;
  resize: none;
  min-height: 26px;
  max-height: 160px;
}
.jaris-input::placeholder { color: #2e5370; }
.jaris-input:disabled { opacity: 0.5; }
.send-btn {
  background: #c0392b;
  border: none;
  color: #fff;
  width: 32px;
  height: 32px;
  border-radius: 2px;
  cursor: pointer;
  font-size: 0.9rem;
  line-height: 1;
  flex-shrink: 0;
  transition: background 0.2s;
  align-self: flex-end;
}
.send-btn:hover:not(:disabled) { background: #e74c3c; box-shadow: 0 0 8px rgba(231,76,60,0.4); }
.send-btn:disabled { opacity: 0.3; cursor: not-allowed; }

.bottom-status {
  font-size: 0.68rem;
  letter-spacing: 0.08em;
  color: #4a6a7a;
  text-transform: uppercase;
  min-height: 1em;
}
.bottom-status.ok { color: #27ae60; }
.bottom-status.warn { color: #f39c12; }
.bottom-status.err { color: #e74c3c; }

/* ---- Mobile ---- */
@media (max-width: 700px) {
  .jaris-page { padding: 1rem; }
  .jaris-title h1 { font-size: 1.4rem; }
  .hud-corner { display: none; }
  .chat-window { max-height: 48vh; }
}
</style>
