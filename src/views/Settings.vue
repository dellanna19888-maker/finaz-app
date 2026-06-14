<template>
  <div class="ai-page">
    <div class="page-header">
      <h1>⚙️ Einstellungen</h1>
      <p class="sub">
        Hinterlege deinen <strong>eigenen</strong> Anthropic-API-Key (Bring Your Own Key).
        Er wird nur in deinem Browser gespeichert und bei Anfragen an dein lokales
        Backend gesendet – niemals ins Repository übernommen.
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getApiKey, setApiKey } from '../lib/apiKey'
import { runAssist } from '../lib/assist'

const draft = ref(getApiKey())
const saved = ref(getApiKey())
const show = ref(false)
const busy = ref(false)
const testOut = ref('')
const envKey = ref<boolean | null>(null)

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

onMounted(async () => {
  try {
    const r = await fetch('/api/health')
    envKey.value = r.ok ? !!((await r.json()) as { envKey?: boolean }).envKey : false
  } catch {
    envKey.value = false
  }
})
</script>
