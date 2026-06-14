<template>
  <div class="ai-page">
    <div class="page-header">
      <h1>📝 Notizen</h1>
      <p class="sub">Markdown-Editor mit KI – jede KI-Aktion läuft durch das Compliance-Gateway.</p>
    </div>

    <div class="toolbar">
      <input
        v-model="instruction"
        class="instruction"
        type="text"
        placeholder="Auftrag für die KI (z. B. 'Schreibe eine Sparplan-Notiz')"
      />
      <select v-model="language" class="sel" title="Zielsprache für Übersetzung">
        <option>Englisch</option><option>Deutsch</option><option>Französisch</option>
        <option>Spanisch</option><option>Italienisch</option>
      </select>
      <button v-for="a in actions" :key="a.id" class="btn" :disabled="busy" @click="run(a.id)">
        {{ a.label }}
      </button>
    </div>

    <div class="editor-grid">
      <div class="col">
        <div class="col-head">Editor</div>
        <textarea v-model="doc" class="editor" spellcheck="false" placeholder="# Hier schreiben ..."></textarea>
      </div>
      <div class="col">
        <div class="col-head">Vorschau</div>
        <div class="preview" v-html="rendered"></div>
      </div>
    </div>

    <div v-if="panel" class="ai-panel">
      <div class="ai-head">
        <strong>{{ panelTitle }}</strong>
        <span class="status" :class="statusClass">{{ status }}</span>
        <span class="spacer"></span>
        <button class="btn-ghost" :disabled="!output" @click="applyOut">Übernehmen</button>
        <button class="btn-ghost" :disabled="!output" @click="appendOut">Anhängen</button>
        <button class="btn-ghost" :disabled="!output" @click="copy">Kopieren</button>
        <button class="btn-ghost" @click="panel = false">Schließen</button>
      </div>
      <div v-if="pending" class="auth">
        <strong>⚠ {{ pending.message }}</strong>
        <ul><li v-for="(r, i) in pending.reasons" :key="i">{{ r }}</li></ul>
        <button class="btn" @click="authorize">Autorisieren &amp; fortfahren</button>
      </div>
      <pre class="ai-output">{{ output }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { marked } from 'marked'
import { runAssist } from '../lib/assist'

const actions = [
  { id: 'generate', label: 'Generieren' },
  { id: 'improve', label: 'Verbessern' },
  { id: 'continue', label: 'Fortsetzen' },
  { id: 'summarize', label: 'Zusammenfassen' },
  { id: 'translate', label: 'Übersetzen' },
]
const TITLES: Record<string, string> = {
  generate: 'Generiertes Dokument',
  improve: 'Verbesserte Version',
  continue: 'Fortsetzung',
  summarize: 'Zusammenfassung',
  translate: 'Übersetzung',
}

const SAVE_KEY = 'finaz_notes'
const doc = ref(localStorage.getItem(SAVE_KEY) || '# Notiz\n\nSchreibe hier – oder lass die **KI** etwas erstellen.\n')
const instruction = ref('')
const language = ref('Englisch')

const output = ref('')
const status = ref('')
const panel = ref(false)
const panelTitle = ref('KI-Ausgabe')
const busy = ref(false)
const pending = ref<{ action: string; message: string; reasons: string[] } | null>(null)

const rendered = computed(() => marked.parse(doc.value || '') as string)
const statusClass = computed(() => {
  if (status.value.includes('blockiert') || status.value.includes('Fehler')) return 'is-block'
  if (status.value.includes('Autorisierung')) return 'is-warn'
  return 'is-ok'
})

watch(doc, (v) => localStorage.setItem(SAVE_KEY, v))

async function run(action: string, consent = false) {
  busy.value = true
  panel.value = true
  pending.value = null
  panelTitle.value = TITLES[action] || 'KI-Ausgabe'
  output.value = ''
  status.value = '… prüft / generiert'
  const outcome = await runAssist(
    { action, text: doc.value, instruction: instruction.value, language: language.value, consent },
    (t) => { output.value += t },
  )
  if (outcome.kind === 'done') {
    status.value = `✓ fertig · ${outcome.status} · ${outcome.jurisdiction}`
  } else if (outcome.kind === 'needs-auth') {
    status.value = '⚠ Autorisierung erforderlich'
    pending.value = { action, message: outcome.info.error || 'Menschliche Autorisierung erforderlich.', reasons: outcome.info.reasons || [] }
  } else if (outcome.kind === 'blocked') {
    status.value = '⛔ blockiert'
    output.value = `${outcome.info.error || ''}\n\n${(outcome.info.reasons || []).join('\n')}`
  } else {
    status.value = '⚠ Fehler'
    output.value = outcome.error
  }
  busy.value = false
}

function authorize() {
  if (pending.value) run(pending.value.action, true)
}
function applyOut() {
  doc.value = output.value
}
function appendOut() {
  doc.value = doc.value ? doc.value + '\n\n' + output.value : output.value
}
async function copy() {
  try {
    await navigator.clipboard.writeText(output.value)
    status.value = '✓ kopiert'
  } catch {
    status.value = '⚠ Kopieren fehlgeschlagen'
  }
}
</script>
