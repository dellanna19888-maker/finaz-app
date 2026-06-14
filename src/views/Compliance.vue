<template>
  <div class="ai-page">
    <div class="page-header">
      <h1>🛡️ Compliance</h1>
      <p class="sub">Operationen lokal prüfen (ohne Server) und das Audit-Log einsehen.</p>
    </div>

    <div class="card2">
      <h2>Prüfung (lokal, Simulation)</h2>
      <textarea v-model="text" class="editor sm" placeholder="Inhalt / Daten ..."></textarea>
      <div class="controls">
        <label>
          Aktion
          <select v-model="action" class="sel">
            <option value="finance">Finanz-Analyse</option>
            <option value="generate">Generieren</option>
            <option value="improve">Verbessern</option>
            <option value="summarize">Zusammenfassen</option>
            <option value="translate">Übersetzen</option>
          </select>
        </label>
        <label>
          Gerichtsbarkeit
          <select v-model="jur" class="sel">
            <option value="DEFAULT">DEFAULT (restriktiv)</option>
            <option value="EU">EU (DSGVO / AI Act)</option>
            <option value="UK">UK (UK GDPR)</option>
            <option value="US">US (NIST / CCPA)</option>
          </select>
        </label>
        <label class="check"><input type="checkbox" v-model="consent" /> Menschliche Autorisierung</label>
        <button class="btn" @click="check">Prüfen</button>
      </div>

      <div v-if="result" class="result">
        <div class="result-head">
          <span class="badge" :class="'badge-' + result.status">{{ result.status }}</span>
          <span v-if="result.status !== result.originalStatus" class="muted">
            (Befund: {{ result.originalStatus }})
          </span>
        </div>
        <dl>
          <dt>Gerichtsbarkeit</dt><dd>{{ result.rulesetLabel }}</dd>
          <dt>Entscheidung</dt><dd>{{ result.decisionText }}</dd>
          <dt>Referenz</dt><dd>{{ result.reference }}</dd>
          <dt>Befunde</dt>
          <dd>
            <ul>
              <li v-for="(r, i) in (result.reasons.length ? result.reasons : ['Keine Befunde'])" :key="i">{{ r }}</li>
            </ul>
          </dd>
        </dl>
      </div>
    </div>

    <div class="card2">
      <div class="row">
        <h2>Audit-Log</h2>
        <span class="spacer"></span>
        <button class="btn-ghost" @click="loadLog">Aktualisieren</button>
        <button class="btn-ghost" :disabled="!log.length" @click="exportCsv">CSV</button>
      </div>
      <p v-if="logError" class="muted">{{ logError }}</p>
      <div v-if="log.length" class="table-wrap">
        <table>
          <thead>
            <tr><th>Zeit</th><th>Gerichtsbarkeit</th><th>Aktion</th><th>Status</th><th>Referenz</th><th>Entscheidung</th></tr>
          </thead>
          <tbody>
            <tr v-for="(d, i) in log" :key="i">
              <td>{{ d.timestamp }}</td>
              <td>{{ d.angewandte_gerichtsbarkeit }}</td>
              <td>{{ d.angeforderte_aktion }}</td>
              <td class="st" :class="'st-' + d.konformitätsstatus">{{ d.konformitätsstatus }}</td>
              <td>{{ d.gesetzliche_referenz }}</td>
              <td>{{ d.endgültige_entscheidung }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else-if="!logError" class="muted">Noch keine Einträge (oder API-Server nicht aktiv).</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { evaluate, type EvalResult, type LogEntry } from '../compliance/gateway'

const text = ref('Kontakt: max@example.com – bitte zusammenfassen.')
const action = ref('summarize')
const jur = ref('EU')
const consent = ref(false)
const result = ref<EvalResult | null>(null)

const log = ref<LogEntry[]>([])
const logError = ref('')

function check() {
  result.value = evaluate({ action: action.value, text: text.value, jurisdiction: jur.value, consent: consent.value })
}

async function loadLog() {
  logError.value = ''
  try {
    const resp = await fetch('/api/compliance/logs?limit=200')
    if (!resp.ok) throw new Error('HTTP ' + resp.status)
    const data = (await resp.json()) as { decisions: LogEntry[] }
    log.value = data.decisions.slice().reverse()
  } catch (err) {
    log.value = []
    logError.value = `Audit-Log nicht verfügbar (${(err as Error).message}). Starte das Backend mit "npm run api".`
  }
}

function exportCsv() {
  const cols: (keyof LogEntry)[] = ['timestamp', 'angewandte_gerichtsbarkeit', 'angeforderte_aktion', 'konformitätsstatus', 'gesetzliche_referenz', 'endgültige_entscheidung']
  const cell = (v: unknown) => `"${String(v ?? '').replace(/"/g, '""')}"`
  const lines = [cols.join(',')].concat(log.value.map((d) => cols.map((c) => cell(d[c])).join(',')))
  const blob = new Blob(['﻿' + lines.join('\n')], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'compliance-audit.csv'
  a.click()
  URL.revokeObjectURL(url)
}

check()
onMounted(loadLog)
</script>
