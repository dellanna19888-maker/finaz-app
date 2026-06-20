<template>
  <div class="ai-page">
    <div class="page-header">
      <h1>💰 Finanzen</h1>
      <p class="sub">
        Einnahmen &amp; Ausgaben deines Creator-Business im Blick – per Hand oder über die 🧠 Zentrale.
        Lass dir per KI einen Überblick erstellen.
      </p>
    </div>

    <!-- Kennzahlen -->
    <div class="stats">
      <div class="stat in">
        <span class="stat-label">Einnahmen</span>
        <span class="stat-val">{{ store.format(store.totalIncome) }}</span>
      </div>
      <div class="stat out">
        <span class="stat-label">Ausgaben</span>
        <span class="stat-val">{{ store.format(store.totalExpense) }}</span>
      </div>
      <div class="stat bal" :class="{ neg: store.balance < 0 }">
        <span class="stat-label">Saldo</span>
        <span class="stat-val">{{ store.format(store.balance) }}</span>
      </div>
      <select v-model="store.currency" class="sel cur" title="Währung">
        <option v-for="c in CURRENCIES" :key="c" :value="c">{{ c }}</option>
      </select>
    </div>

    <!-- Neue Buchung -->
    <div class="card2">
      <div class="add-row">
        <select v-model="type" class="sel">
          <option value="income">＋ Einnahme</option>
          <option value="expense">－ Ausgabe</option>
        </select>
        <input v-model.number="amount" type="number" min="0" step="0.01" class="sel amount" placeholder="Betrag" @keyup.enter="add" />
        <input v-model="category" class="sel cat" placeholder="Kategorie" :list="type === 'income' ? 'inc-cats' : 'exp-cats'" />
        <datalist id="inc-cats"><option v-for="c in INCOME_CATEGORIES" :key="c">{{ c }}</option></datalist>
        <datalist id="exp-cats"><option v-for="c in EXPENSE_CATEGORIES" :key="c">{{ c }}</option></datalist>
        <input v-model="note" class="instruction" placeholder="Notiz … (Enter)" @keyup.enter="add" />
        <input v-model="date" type="date" class="sel" />
        <button class="btn" :disabled="!amount || amount <= 0" @click="add">Buchen</button>
      </div>
    </div>

    <!-- Filter + KI -->
    <div class="filters">
      <button class="chip" :class="{ on: filter === 'all' }" @click="filter = 'all'">Alle</button>
      <button class="chip" :class="{ on: filter === 'income' }" @click="filter = 'income'">Einnahmen</button>
      <button class="chip" :class="{ on: filter === 'expense' }" @click="filter = 'expense'">Ausgaben</button>
      <span class="spacer"></span>
      <button class="btn" :disabled="busy || !store.transactions.length" @click="aiOverview()">🧠 KI-Finanzüberblick</button>
    </div>

    <RouterLink v-if="!hasKey" to="/settings" class="keyhint">🔑 Kein API-Key gesetzt – für den KI-Überblick hier eintragen (⚙️ Einstellungen)</RouterLink>

    <!-- Buchungsliste -->
    <ul class="tx-list">
      <li v-for="t in shown" :key="t.id" class="tx" :class="t.type">
        <span class="tx-sign">{{ t.type === 'income' ? '＋' : '－' }}</span>
        <div class="tx-main">
          <span class="tx-amount">{{ store.format(t.amount) }}</span>
          <span class="tx-meta">
            <span v-if="t.category" class="tag">{{ t.category }}</span>
            <span v-if="t.note" class="tx-note">{{ t.note }}</span>
            <span class="tag date">📅 {{ t.date }}</span>
          </span>
        </div>
        <button class="btn-ghost xs" title="Löschen" @click="store.deleteTransaction(t.id)">✕</button>
      </li>
      <li v-if="!shown.length" class="muted empty-li">Keine Buchungen.</li>
    </ul>

    <!-- KI-Ausgabe -->
    <div v-if="panel" class="ai-panel">
      <div class="ai-head">
        <strong>Finanzüberblick (KI)</strong>
        <span class="status" :class="statusClass">{{ status }}</span>
        <span class="spacer"></span>
        <button class="btn-ghost" :disabled="!output" @click="copy">Kopieren</button>
        <button class="btn-ghost" @click="panel = false">Schließen</button>
      </div>
      <div v-if="pending" class="auth">
        <strong>⚠ {{ pending.message }}</strong>
        <ul><li v-for="(r, i) in pending.reasons" :key="i">{{ r }}</li></ul>
        <button class="btn" @click="authorize">Autorisieren &amp; fortfahren</button>
      </div>
      <div class="ai-output md" v-html="rendered"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { marked } from 'marked'
import { useFinanceStore, INCOME_CATEGORIES, EXPENSE_CATEGORIES, CURRENCIES, type TxType } from '../stores/finance'
import { runAssist } from '../lib/assist'
import { hasAnyKey } from '../lib/apiKey'
import { buildFinanceSummary } from '../lib/appState'

const store = useFinanceStore()
const hasKey = hasAnyKey()

const type = ref<TxType>('income')
const amount = ref<number | null>(null)
const category = ref('')
const note = ref('')
const date = ref(new Date().toISOString().slice(0, 10))

const filter = ref<'all' | TxType>('all')

const shown = computed(() => store.transactions.filter((t) => filter.value === 'all' || t.type === filter.value))

// KI-Panel
const panel = ref(false)
const busy = ref(false)
const output = ref('')
const status = ref('')
const pending = ref<{ message: string; reasons: string[] } | null>(null)

const rendered = computed(() => marked.parse(output.value || '…') as string)
const statusClass = computed(() => {
  if (status.value.includes('blockiert') || status.value.includes('Fehler')) return 'is-block'
  if (status.value.includes('Autorisierung')) return 'is-warn'
  return 'is-ok'
})

function add() {
  if (!amount.value || amount.value <= 0) return
  store.addTransaction({ type: type.value, amount: amount.value, category: category.value.trim(), note: note.value.trim(), date: date.value })
  amount.value = null
  category.value = ''
  note.value = ''
  date.value = new Date().toISOString().slice(0, 10)
}

async function aiOverview(consent = false) {
  busy.value = true
  panel.value = true
  pending.value = null
  output.value = ''
  status.value = '… prüft / erstellt'
  const outcome = await runAssist(
    {
      action: 'finance',
      text: buildFinanceSummary(store),
      instruction:
        'Erstelle einen kompakten Finanzüberblick für einen Online-Creator: Saldo einordnen, größte Einnahme-/Ausgabenposten, ' +
        'Auffälligkeiten und 2–3 konkrete, umsetzbare Tipps. Keine verbindliche Steuer-/Rechtsberatung.',
      consent,
    },
    (t) => { output.value += t },
  )
  if (outcome.kind === 'done') {
    status.value = `✓ fertig · ${outcome.status} · ${outcome.jurisdiction}`
  } else if (outcome.kind === 'needs-auth') {
    status.value = '⚠ Autorisierung erforderlich'
    pending.value = { message: outcome.info.error || 'Menschliche Autorisierung erforderlich.', reasons: outcome.info.reasons || [] }
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
  aiOverview(true)
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

<style scoped>
.stats { display: grid; grid-template-columns: repeat(3, 1fr) auto; gap: 0.75rem; align-items: stretch; margin-bottom: 1.25rem; }
.stat { display: flex; flex-direction: column; gap: 0.2rem; padding: 0.9rem 1rem; border-radius: 12px; border: 1px solid #334155; background: #1e293b; border-left: 3px solid #475569; }
.stat.in { border-left-color: #34d399; }
.stat.out { border-left-color: #f87171; }
.stat.bal { border-left-color: #60a5fa; }
.stat.bal.neg { border-left-color: #f87171; }
.stat-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; color: #94a3b8; }
.stat-val { font-size: 1.3rem; font-weight: 700; color: #e2e8f0; }
.stat.in .stat-val { color: #34d399; }
.stat.out .stat-val { color: #f87171; }
.stat.bal.neg .stat-val { color: #f87171; }
.cur { align-self: center; }

.add-row { display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; }
.add-row .instruction { flex: 1; min-width: 160px; }
.amount { width: 110px; }
.cat { min-width: 130px; }

.filters { display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; margin: 1rem 0; }
.filters .spacer { flex: 1; }
.chip { padding: 0.4rem 0.8rem; border-radius: 999px; border: 1px solid #334155; background: #1e293b; color: #cbd5e1; cursor: pointer; font-size: 0.82rem; }
.chip.on { border-color: #60a5fa; color: #fff; background: rgba(96, 165, 250, 0.15); }

.tx-list { list-style: none; display: flex; flex-direction: column; gap: 0.5rem; padding: 0; }
.tx { display: flex; align-items: center; gap: 0.75rem; padding: 0.6rem 0.8rem; background: #1e293b; border: 1px solid #334155; border-left: 3px solid #475569; border-radius: 10px; }
.tx.income { border-left-color: #34d399; }
.tx.expense { border-left-color: #f87171; }
.tx-sign { font-size: 1.1rem; width: 1.2rem; text-align: center; flex-shrink: 0; }
.tx.income .tx-sign { color: #34d399; }
.tx.expense .tx-sign { color: #f87171; }
.tx-main { flex: 1; display: flex; flex-direction: column; gap: 0.25rem; min-width: 0; }
.tx-amount { font-weight: 700; color: #e2e8f0; }
.tx-meta { display: flex; flex-wrap: wrap; gap: 0.4rem; align-items: center; }
.tx-note { color: #cbd5e1; font-size: 0.85rem; word-break: break-word; }
.tag { font-size: 0.72rem; color: #94a3b8; background: #0f172a; padding: 0.1rem 0.45rem; border-radius: 6px; border: 1px solid #334155; }
.tag.date { color: #93c5fd; border-color: #1e40af; }
.btn-ghost.xs { padding: 0.25rem 0.55rem; font-size: 0.9rem; line-height: 1; }
.empty-li { padding: 1rem; text-align: center; }

.ai-panel { margin-top: 1.25rem; }
.ai-output.md { white-space: normal; font: inherit; line-height: 1.6; }
.ai-output.md :first-child { margin-top: 0; }
.ai-output.md :is(h1, h2, h3) { font-size: 1.1rem; margin: 0.8rem 0 0.4rem; }
.ai-output.md table { border-collapse: collapse; }
.ai-output.md th, .ai-output.md td { border: 1px solid #334155; padding: 0.3rem 0.5rem; }

@media (max-width: 700px) {
  .stats { grid-template-columns: 1fr 1fr; }
  .cur { grid-column: span 2; justify-self: start; }
}
</style>
