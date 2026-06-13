<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1>Transaktionen</h1>
        <span class="subtitle">{{ filtered.length }} Einträge</span>
      </div>
      <button class="btn-add" @click="showForm = true">+ Neue Transaktion</button>
    </div>

    <div class="filters">
      <input v-model="search" type="text" placeholder="Suchen..." class="search-input" />
      <select v-model="filterType" class="filter-select">
        <option value="">Alle Typen</option>
        <option value="income">Einnahmen</option>
        <option value="expense">Ausgaben</option>
      </select>
      <select v-model="filterCategory" class="filter-select">
        <option value="">Alle Kategorien</option>
        <option v-for="cat in allCategories" :key="cat">{{ cat }}</option>
      </select>
    </div>

    <div class="tx-table">
      <div class="tx-head">
        <span>Datum</span>
        <span>Kategorie</span>
        <span>Beschreibung</span>
        <span>Typ</span>
        <span class="right">Betrag</span>
        <span></span>
      </div>
      <div v-for="tx in filtered" :key="tx.id" class="tx-row">
        <span class="date">{{ tx.date }}</span>
        <span class="cat">{{ tx.category }}</span>
        <span class="desc">{{ tx.description || '—' }}</span>
        <span :class="['badge', tx.type === 'income' ? 'badge-income' : 'badge-expense']">
          {{ tx.type === 'income' ? 'Einnahme' : 'Ausgabe' }}
        </span>
        <span :class="['amount', 'right', tx.type === 'income' ? 'positive' : 'negative']">
          {{ tx.type === 'income' ? '+' : '-' }}{{ fmt(tx.amount) }}
        </span>
        <span class="actions">
          <button class="icon-btn" title="Bearbeiten" @click="editing = tx">✏️</button>
          <button class="icon-btn" title="Löschen" @click="confirmDelete(tx.id)">🗑️</button>
        </span>
      </div>
      <div v-if="filtered.length === 0" class="empty">Keine Transaktionen gefunden.</div>
    </div>

    <TransactionForm v-if="showForm" @close="showForm = false" />
    <TransactionForm v-if="editing" :editing="editing" @close="editing = null" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useTransactionStore, INCOME_CATEGORIES, EXPENSE_CATEGORIES, type Transaction } from '../stores/transactions'
import TransactionForm from '../components/TransactionForm.vue'

const store = useTransactionStore()
const showForm = ref(false)
const editing = ref<Transaction | null>(null)
const search = ref('')
const filterType = ref('')
const filterCategory = ref('')

const fmt = (n: number) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(n)

const allCategories = [...INCOME_CATEGORIES, ...EXPENSE_CATEGORIES].filter((v, i, a) => a.indexOf(v) === i)

const filtered = computed(() =>
  store.transactions.filter(tx => {
    if (filterType.value && tx.type !== filterType.value) return false
    if (filterCategory.value && tx.category !== filterCategory.value) return false
    if (search.value) {
      const q = search.value.toLowerCase()
      if (!tx.description.toLowerCase().includes(q) && !tx.category.toLowerCase().includes(q)) return false
    }
    return true
  })
)

function confirmDelete(id: string) {
  if (confirm('Transaktion wirklich löschen?')) store.deleteTransaction(id)
}
</script>

<style scoped>
.page { padding: 2rem; max-width: 1200px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; }
.page-header h1 { color: #e2e8f0; font-size: 1.8rem; margin: 0; }
.subtitle { color: #64748b; font-size: 0.9rem; }

.btn-add {
  padding: 0.6rem 1.25rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
}
.btn-add:hover { background: #2563eb; }

.filters { display: flex; gap: 0.75rem; margin-bottom: 1.5rem; }

.search-input {
  flex: 1;
  padding: 0.6rem 0.8rem;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 0.9rem;
}

.filter-select {
  padding: 0.6rem 0.8rem;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 0.9rem;
}

.search-input:focus, .filter-select:focus { outline: none; border-color: #60a5fa; }

.tx-table {
  background: #1e293b;
  border-radius: 12px;
  overflow: hidden;
}

.tx-head {
  display: grid;
  grid-template-columns: 100px 130px 1fr 90px 130px 80px;
  padding: 0.8rem 1rem;
  background: #0f172a;
  color: #64748b;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.tx-row {
  display: grid;
  grid-template-columns: 100px 130px 1fr 90px 130px 80px;
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #0f172a;
  align-items: center;
  transition: background 0.15s;
}
.tx-row:hover { background: rgba(255,255,255,0.02); }
.tx-row:last-child { border-bottom: none; }

.date { color: #475569; font-size: 0.85rem; }
.cat { color: #94a3b8; font-size: 0.85rem; }
.desc { color: #e2e8f0; font-size: 0.9rem; }

.badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}
.badge-income { background: rgba(16,185,129,0.15); color: #10b981; }
.badge-expense { background: rgba(239,68,68,0.15); color: #ef4444; }

.amount { font-weight: 600; font-size: 0.95rem; }
.right { text-align: right; }
.positive { color: #10b981; }
.negative { color: #ef4444; }

.actions { display: flex; gap: 0.3rem; justify-content: flex-end; }
.icon-btn { background: none; border: none; cursor: pointer; font-size: 1rem; opacity: 0.6; transition: opacity 0.2s; }
.icon-btn:hover { opacity: 1; }

.empty { color: #475569; text-align: center; padding: 3rem; }
</style>
