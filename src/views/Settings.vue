<template>
  <div class="ai-page">
    <div class="page-header">
      <h1>⚙️ Einstellungen</h1>
      <p class="sub">
        Hinterlege deinen <strong>eigenen</strong> KI-Schlüssel (Bring Your Own Key):
        <strong>Anthropic</strong> (beste Qualität, kostenpflichtig) <strong>oder Google Gemini</strong>
        (kostenlos). Der Schlüssel bleibt nur in deinem Browser – niemals im Repository.
      </p>
    </div>

    <div class="card2">
      <h2>🔑 Anthropic API-Key</h2>
      <div class="key-row">
        <input
          :type="show ? 'text' : 'password'"
          v-model="draft"
          class="instruction"
          placeholder="sk-ant-..."
          autocomplete="off"
        />
        <button class="btn-ghost" @click="show = !show">{{ show ? 'Verbergen' : 'Zeigen' }}</button>
      </div>
      <div class="controls">
        <button class="btn" @click="save">Speichern</button>
        <button class="btn-ghost" :disabled="!stored" @click="clearKey">Löschen</button>
        <button class="btn-ghost" :disabled="busy" @click="test">Verbindung testen</button>
      </div>
      <p class="muted">{{ statusMsg }}</p>
      <p v-if="testOut" class="muted">Test-Antwort: {{ testOut }}</p>

      <p class="hint" style="margin-top: 1rem">
        Einen Key bekommst du unter
        <a href="https://platform.claude.com" target="_blank" rel="noreferrer">platform.claude.com</a>.
        Alternativ kann der Server einen Key aus <code>.env</code> (ANTHROPIC_API_KEY) nutzen –
        server-seitiger Key vorhanden:
        <strong>{{ envKey === null ? '…' : envKey ? 'ja' : 'nein' }}</strong>.
      </p>
      <p class="muted">
        ⚠ Ein im Browser gespeicherter Key ist für die lokale/private Nutzung gedacht.
        Lege Keys nicht im Browser ab, wenn du das Tool öffentlich hostest.
      </p>
    </div>

    <div class="card2">
      <h2>🆓 Google Gemini-Key (kostenlos)</h2>
      <p class="muted" style="margin-bottom: 0.6rem">
        Gratis-Alternative ohne Bezahlung: Schlüssel bei
        <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer">Google AI Studio</a>
        erstellen (kein Zahlungsmittel nötig). Ist ein Anthropic-Key gesetzt, wird dieser bevorzugt.
      </p>
      <div class="key-row">
        <input
          :type="gshow ? 'text' : 'password'"
          v-model="gdraft"
          class="instruction"
          placeholder="AIza..."
          autocomplete="off"
        />
        <button class="btn-ghost" @click="gshow = !gshow">{{ gshow ? 'Verbergen' : 'Zeigen' }}</button>
      </div>
      <div class="controls">
        <button class="btn" @click="gsave">Speichern</button>
        <button class="btn-ghost" :disabled="!gstored" @click="gclear">Löschen</button>
      </div>
      <p class="muted">{{ gstatusMsg }}</p>
    </div>

    <div class="card2">
      <h2>💾 Daten sichern &amp; übertragen</h2>
      <p class="muted" style="margin-bottom: 0.6rem">
        Alle Inhalte (Content-Plan, Finanzen, Wissen, Kanal) liegen nur in diesem Browser.
        Exportiere sie als Datei zur Sicherung oder um sie auf ein anderes Gerät zu übertragen.
        API-Schlüssel und der Chat-Verlauf werden aus Datenschutzgründen <strong>nicht</strong> mitexportiert.
      </p>
      <div class="controls">
        <button class="btn" @click="onExport">⬇ Exportieren</button>
        <button class="btn-ghost" @click="fileInput?.click()">⬆ Importieren …</button>
        <button class="btn-ghost danger" @click="onReset">🗑 Alle Daten zurücksetzen</button>
        <input ref="fileInput" type="file" accept="application/json,.json" class="hidden-file" @change="onImport" />
      </div>
      <p class="muted" :class="dataStatusClass">{{ dataStatus }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getApiKey, setApiKey, getGeminiKey, setGeminiKey } from '../lib/apiKey'
import { runAssist } from '../lib/assist'
import { downloadBackup, importJson, resetData } from '../lib/backup'

const draft = ref(getApiKey())
const saved = ref(getApiKey())
const show = ref(false)
const busy = ref(false)
const testOut = ref('')
const envKey = ref<boolean | null>(null)

const gdraft = ref(getGeminiKey())
const gsaved = ref(getGeminiKey())
const gshow = ref(false)
const gstored = computed(() => gsaved.value.length > 0)
const gstatusMsg = computed(() => (gsaved.value ? '✓ Gemini-Key im Browser gespeichert.' : 'Kein Gemini-Key gespeichert.'))

function gsave() {
  setGeminiKey(gdraft.value.trim())
  gsaved.value = getGeminiKey()
}
function gclear() {
  setGeminiKey('')
  gdraft.value = ''
  gsaved.value = ''
}

const stored = computed(() => saved.value.length > 0)
const statusMsg = computed(() => (saved.value ? '✓ Key im Browser gespeichert.' : 'Kein Key gespeichert.'))

function save() {
  setApiKey(draft.value.trim())
  saved.value = getApiKey()
}
function clearKey() {
  setApiKey('')
  draft.value = ''
  saved.value = ''
}
async function test() {
  save()
  busy.value = true
  testOut.value = ''
  const outcome = await runAssist(
    { action: 'generate', instruction: 'Antworte nur mit dem Wort OK.' },
    (t) => { testOut.value += t },
  )
  busy.value = false
  if (outcome.kind === 'error') testOut.value = 'Fehler: ' + outcome.error
  else if (outcome.kind === 'blocked') testOut.value = 'Blockiert: ' + (outcome.info.error || '')
  else if (outcome.kind === 'needs-auth') testOut.value = 'Compliance: Autorisierung erforderlich.'
  else if (!testOut.value) testOut.value = '(leer)'
}

// --- Daten sichern / übertragen ---
const fileInput = ref<HTMLInputElement | null>(null)
const dataStatus = ref('')
const dataStatusClass = computed(() => {
  if (dataStatus.value.includes('Fehler') || dataStatus.value.includes('⚠')) return 'is-block'
  if (dataStatus.value.includes('✓')) return 'is-ok'
  return ''
})

function onExport() {
  try {
    downloadBackup()
    dataStatus.value = '✓ Backup-Datei heruntergeladen.'
  } catch (err) {
    dataStatus.value = '⚠ Fehler beim Export: ' + (err as Error).message
  }
}

function onImport(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    try {
      const res = importJson(String(reader.result))
      dataStatus.value = `✓ ${res.imported.length} Datensätze importiert. App wird neu geladen …`
      setTimeout(() => location.reload(), 800)
    } catch (err) {
      dataStatus.value = '⚠ Import-Fehler: ' + (err as Error).message
    }
  }
  reader.onerror = () => (dataStatus.value = '⚠ Datei konnte nicht gelesen werden.')
  reader.readAsText(file)
  if (fileInput.value) fileInput.value.value = ''
}

function onReset() {
  if (!confirm('Wirklich ALLE Inhalte (Content, Finanzen, Wissen, Kanal) löschen? Das kann nicht rückgängig gemacht werden.')) return
  resetData()
  dataStatus.value = '✓ Daten zurückgesetzt. App wird neu geladen …'
  setTimeout(() => location.reload(), 800)
}

onMounted(async () => {
  try {
    const r = await fetch('/api/health')
    envKey.value = r.ok ? !!((await r.json()) as { envKey?: boolean }).envKey : false
  } catch {
    envKey.value = false
  }
})
</script>

<style scoped>
.hidden-file { display: none; }
.btn-ghost.danger { border-color: #6b2c2c; color: #f08a8a; }
.btn-ghost.danger:hover { background: rgba(240, 138, 138, 0.08); }
</style>
