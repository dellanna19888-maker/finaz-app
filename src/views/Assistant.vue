<template>
  <div class="ai-page">
    <div class="page-header">
      <h1>🤖 KI-Assistent</h1>
      <p class="sub">
        Erstellt aus deinen Finanzdaten Berichte &amp; Tipps – jede Anfrage läuft
        durch das Compliance-Gateway (Prüfung + Audit-Log).
      </p>
    </div>

    <div class="presets">
      <button
        v-for="p in presets"
        :key="p.id"
        class="card-btn"
        :disabled="busy"
        @click="run(p.instruction)"
      >
        <span class="card-btn-icon">{{ p.icon }}</span>
        <span class="card-btn-label">{{ p.label }}</span>
        <span class="card-btn-desc">{{ p.desc }}</span>
      </button>
    </div>

    <div class="custom">
      <input
        v-model="custom"
        class="instruction"
        placeholder="Eigene Frage zu deinen Finanzen ..."
        @keyup.enter="run(custom)"
      />
      <button class="btn" :disabled="busy || !custom.trim()" @click="run(custom)">Fragen</button>
    </div>

    <div v-if="panel" class="ai-panel">
      <div class="ai-head">
        <strong>Antwort</strong>
        <span class="status" :class="statusClass">{{ status }}</span>
        <span class="spacer"></span>
        <button class="btn-ghost" :disabled="!output" @click="copy">Kopieren</button>
        <button class="btn-ghost" @click="panel = false">Schließen</button>
      </div>
      <div v-if="pending" class="auth">
        <strong>⚠ {{ pending.message }}</strong>
        <p class="muted">Es werden aggregierte Finanzdaten an den KI-Dienst (Claude) gesendet.</p>
        <ul><li v-for="(r, i) in pending.reasons" :key="i">{{ r }}</li></ul>
        <button class="btn" @click="authorize">Autorisieren &amp; fortfahren</button>
      </div>
      <div class="preview" v-html="rendered"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { marked } from 'marked'
import { useTransactionStore } from '../stores/transactions'
import { useBudgetStore } from '../stores/budgets'
import { runAssist } from '../lib/assist'

const tx = useTransactionStore()
const bud = useBudgetStore()
const fmt = (n: number) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(n)

const presets = [
  { id: 'report', icon: '📄', label: 'Monatsbericht', desc: 'Einnahmen, Ausgaben, Bilanz im Überblick', instruction: 'Erstelle einen prägnanten Monatsbericht meiner Finanzen mit den wichtigsten Kennzahlen und 2–3 Beobachtungen.' },
  { id: 'insights', icon: '🔍', label: 'Budget-Insights', desc: 'Wo liege ich über/unter Budget?', instruction: 'Analysiere meine Ausgaben gegenüber den Budgets und nenne konkret, wo ich über oder unter Budget liege.' },
  { id: 'tips', icon: '💡', label: 'Spar-Tipps', desc: 'Konkrete Vorschläge zum Sparen', instruction: 'Gib mir 5 konkrete, umsetzbare Spar-Tipps basierend auf meinen Ausgabenmustern.' },
]

const custom = ref('')
const output = ref('')
const status = ref('')
const panel = ref(false)
const busy = ref(false)
const pending = ref<{ instruction: string; message: string; reasons: string[] } | null>(null)

const rendered = computed(() => marked.parse(output.value || '') as string)
const statusClass = computed(() => {
  if (status.value.includes('blockiert') || status.value.includes('Fehler')) return 'is-block'
  if (status.value.includes('Autorisierung')) return 'is-warn'
  return 'is-ok'
})

function buildSummary(): string {
  const byCat = tx.expensesByCategory()
  const rate = tx.totalIncome > 0 ? Math.round((tx.balance / tx.totalIncome) * 100) : 0
  const lines = [
    `Gesamteinnahmen: ${fmt(tx.totalIncome)}`,
    `Gesamtausgaben: ${fmt(tx.totalExpenses)}`,
    `Bilanz: ${fmt(tx.balance)}`,
    `Sparquote: ${rate}%`,
    '',
    'Ausgaben nach Kategorie:',
  ]
  for (const [cat, amount] of Object.entries(byCat).sort((a, b) => b[1] - a[1])) {
    const limit = bud.budgets.find((b) => b.category === cat)?.limit
    lines.push(`- ${cat}: ${fmt(amount)}${limit != null ? ` (Budget ${fmt(limit)})` : ''}`)
  }
  return lines.join('\n')
}

async function run(instruction: string, consent = false) {
  const task = instruction.trim()
  if (!task) return
  busy.value = true
  panel.value = true
  pending.value = null
  output.value = ''
  status.value = '… prüft / generiert'
  const outcome = await runAssist(
    { action: 'finance', text: buildSummary(), instruction: task, consent },
    (t) => { output.value += t },
  )
  if (outcome.kind === 'done') {
    status.value = `✓ fertig · ${outcome.status} · ${outcome.jurisdiction}`
  } else if (outcome.kind === 'needs-auth') {
    status.value = '⚠ Autorisierung erforderlich'
    pending.value = { instruction: task, message: outcome.info.error || 'Menschliche Autorisierung erforderlich.', reasons: outcome.info.reasons || [] }
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
  if (pending.value) run(pending.value.instruction, true)
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
