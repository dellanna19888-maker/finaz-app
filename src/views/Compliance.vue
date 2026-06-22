<template>
  <div class="page">
    <div class="page-header">
      <h1>🛡️ Compliance</h1>
      <p class="sub">Inhalte lokal auf Datenschutz &amp; KI-Recht prüfen (DSGVO, EU AI Act, UK GDPR, CCPA) — ohne Server, komplett offline.</p>
    </div>

    <!-- Checker -->
    <div class="card">
      <h2>🔍 Inhalts-Prüfung (lokal)</h2>
      <label class="lbl" style="margin-bottom:0.75rem">Text / Inhalt zu prüfen
        <textarea v-model="text" class="ta" style="min-height:110px" placeholder="Füge hier den Text ein, den du prüfen möchtest …&#10;z. B.: &quot;Kontakt: max@example.com – bitte analysiere seine Finanzdaten.&quot;"></textarea>
      </label>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:0.75rem;margin-bottom:0.75rem">
        <label class="lbl">KI-Aktion
          <select v-model="action" class="sel">
            <option value="finance">Finanz-Analyse</option>
            <option value="generate">Generieren</option>
            <option value="improve">Verbessern</option>
            <option value="summarize">Zusammenfassen</option>
            <option value="translate">Übersetzen</option>
          </select>
        </label>
        <label class="lbl">Rechtssystem
          <select v-model="jur" class="sel">
            <option value="DEFAULT">DEFAULT (restriktiv)</option>
            <option value="EU">EU (DSGVO + AI Act)</option>
            <option value="UK">UK (UK GDPR)</option>
            <option value="US">US (NIST / CCPA)</option>
          </select>
        </label>
      </div>
      <div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap">
        <label style="display:flex;align-items:center;gap:0.5rem;cursor:pointer;font-size:0.88rem">
          <input type="checkbox" v-model="consent" style="accent-color:var(--accent)" /> Menschliche Autorisierung erteilt
        </label>
        <button class="btn btn-primary" @click="check">Jetzt prüfen</button>
      </div>

      <!-- Result -->
      <div v-if="result" style="margin-top:1rem;padding-top:1rem;border-top:1px solid var(--border)">
        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.75rem;flex-wrap:wrap">
          <span class="badge" :class="'badge-' + result.status">{{ result.status }}</span>
          <span v-if="result.status !== result.originalStatus" class="muted">(Befund: {{ result.originalStatus }})</span>
          <span class="muted">{{ result.rulesetLabel }}</span>
        </div>
        <div style="display:grid;gap:0.5rem;font-size:0.87rem">
          <div><span style="color:var(--text3)">Entscheidung:</span> <span>{{ result.decisionText }}</span></div>
          <div><span style="color:var(--text3)">Referenz:</span> <span style="color:var(--accent2)">{{ result.reference }}</span></div>
          <div>
            <span style="color:var(--text3)">Befunde:</span>
            <ul style="margin:0.3rem 0 0 1.1rem">
              <li v-for="(r, i) in (result.reasons.length ? result.reasons : ['Keine Befunde'])" :key="i">{{ r }}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Audit log -->
    <div class="card">
      <div style="display:flex;align-items:center;margin-bottom:0.75rem;gap:0.5rem">
        <h2 style="margin-bottom:0">📋 Audit-Log</h2>
        <span class="spacer"></span>
        <button class="btn btn-ghost btn-sm" @click="loadLog">Aktualisieren</button>
        <button class="btn btn-ghost btn-sm" :disabled="!log.length" @click="exportCsv">⬇ CSV</button>
      </div>
      <p v-if="logError" class="muted">{{ logError }}</p>
      <div v-if="log.length" class="table-wrap">
        <table>
          <thead>
            <tr><th>Zeit</th><th>System</th><th>Aktion</th><th>Status</th><th>Referenz</th><th>Entscheidung</th></tr>
          </thead>
          <tbody>
            <tr v-for="(d, i) in log" :key="i">
              <td>{{ d.timestamp }}</td>
              <td>{{ d.angewandte_gerichtsbarkeit }}</td>
              <td>{{ d.angeforderte_aktion }}</td>
              <td :class="'st-' + d.konformitätsstatus" style="font-weight:600">{{ d.konformitätsstatus }}</td>
              <td style="font-size:0.78rem;color:var(--text3)">{{ d.gesetzliche_referenz }}</td>
              <td>{{ d.endgültige_entscheidung }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else-if="!logError" class="muted" style="text-align:center;padding:1rem">Keine Log-Einträge (oder Backend nicht aktiv — starte mit <code>npm run api</code>).</p>
    </div>

    <!-- Info -->
    <div class="card" style="font-size:0.83rem;color:var(--text3)">
      ⚠️ Dieses System ist ein Governance-Gerüst zur Orientierung — keine zertifizierte Rechtsberatung. Für verbindliche Aussagen wende dich an einen Datenschutz- oder Rechtsexperten.
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
    logError.value = `Audit-Log nicht verfügbar (${(err as Error).message}).`
  }
}

function exportCsv() {
  const cols: (keyof LogEntry)[] = ['timestamp','angewandte_gerichtsbarkeit','angeforderte_aktion','konformitätsstatus','gesetzliche_referenz','endgültige_entscheidung']
  const cell = (v: unknown) => `"${String(v ?? '').replace(/"/g, '""')}"`
  const lines = [cols.join(','), ...log.value.map(d => cols.map(c => cell(d[c])).join(','))]
  const blob = new Blob(['﻿' + lines.join('\n')], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a'); a.href = url; a.download = 'compliance-audit.csv'; a.click()
  URL.revokeObjectURL(url)
}

check()
onMounted(loadLog)
</script>
