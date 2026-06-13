<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1>Budget-Planung</h1>
        <span class="subtitle">Monatliche Limits verwalten</span>
      </div>
    </div>

    <div class="budget-grid">
      <div v-for="item in overview" :key="item.category" class="budget-card">
        <div class="budget-top">
          <span class="budget-cat">{{ item.category }}</span>
          <span :class="['pct-badge', item.pct > 100 ? 'over' : item.pct > 80 ? 'warn' : 'ok']">
            {{ Math.round(item.pct) }}%
          </span>
        </div>

        <div class="amounts">
          <span class="spent" :class="item.pct > 100 ? 'over-text' : ''">{{ fmt(item.spent) }}</span>
          <span class="sep"> / </span>
          <span class="limit">{{ fmt(item.limit) }}</span>
        </div>

        <div class="progress-bar">
          <div
            class="progress-fill"
            :style="{ width: Math.min(item.pct, 100) + '%' }"
            :class="item.pct > 100 ? 'over' : item.pct > 80 ? 'warn' : 'ok'"
          />
        </div>

        <div class="remaining">
          <template v-if="item.pct <= 100">
            Noch verfügbar: <strong>{{ fmt(item.limit - item.spent) }}</strong>
          </template>
          <template v-else>
            <span class="over-text">Überschritten um {{ fmt(item.spent - item.limit) }}</span>
          </template>
        </div>

        <div class="budget-edit">
          <label>Limit anpassen (€)</label>
          <div class="edit-row">
            <input
              type="number"
              :value="item.limit"
              min="1"
              @change="e => budgetStore.setBudget(item.category, Number((e.target as HTMLInputElement).value))"
            />
          </div>
        </div>
      </div>
    </div>

    <div class="add-budget">
      <h2>Neue Kategorie hinzufügen</h2>
      <div class="add-row">
        <select v-model="newCat" class="filter-select">
          <option value="">Kategorie wählen...</option>
          <option v-for="cat in availableCats" :key="cat">{{ cat }}</option>
        </select>
        <input v-model.number="newLimit" type="number" placeholder="Budget in €" class="budget-input" />
        <button class="btn-add" @click="handleAdd">Hinzufügen</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useBudgetStore } from '../stores/budgets'
import { useTransactionStore, EXPENSE_CATEGORIES } from '../stores/transactions'

const budgetStore = useBudgetStore()
const txStore = useTransactionStore()

const newCat = ref('')
const newLimit = ref(0)

const fmt = (n: number) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(n)

const expByCategory = computed(() => txStore.expensesByCategory())

const overview = computed(() =>
  budgetStore.budgets.map(b => ({
    ...b,
    spent: expByCategory.value[b.category] || 0,
    pct: ((expByCategory.value[b.category] || 0) / b.limit) * 100,
  }))
)

const availableCats = computed(() =>
  EXPENSE_CATEGORIES.filter(c => !budgetStore.budgets.find(b => b.category === c))
)

function handleAdd() {
  if (!newCat.value || !newLimit.value) return
  budgetStore.setBudget(newCat.value, newLimit.value)
  newCat.value = ''
  newLimit.value = 0
}
</script>

<style scoped>
.page { padding: 2rem; max-width: 1200px; margin: 0 auto; }
.page-header { margin-bottom: 2rem; }
.page-header h1 { color: #e2e8f0; font-size: 1.8rem; margin: 0; }
.subtitle { color: #64748b; font-size: 0.9rem; }

.budget-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.25rem;
  margin-bottom: 2rem;
}

.budget-card {
  background: #1e293b;
  border-radius: 12px;
  padding: 1.25rem;
}

.budget-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.budget-cat { color: #e2e8f0; font-weight: 600; }

.pct-badge {
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}
.pct-badge.ok { background: rgba(16,185,129,0.15); color: #10b981; }
.pct-badge.warn { background: rgba(245,158,11,0.15); color: #f59e0b; }
.pct-badge.over { background: rgba(239,68,68,0.15); color: #ef4444; }

.amounts { color: #94a3b8; font-size: 0.9rem; margin-bottom: 0.75rem; }
.spent { color: #e2e8f0; font-weight: 600; }
.over-text { color: #ef4444; }
.sep { color: #475569; }
.limit { color: #64748b; }

.progress-bar { height: 8px; background: #0f172a; border-radius: 4px; overflow: hidden; margin-bottom: 0.75rem; }
.progress-fill { height: 100%; border-radius: 4px; transition: width 0.4s; }
.progress-fill.ok { background: #10b981; }
.progress-fill.warn { background: #f59e0b; }
.progress-fill.over { background: #ef4444; }

.remaining { font-size: 0.8rem; color: #64748b; margin-bottom: 1rem; }
.remaining strong { color: #10b981; }

.budget-edit label { display: block; color: #475569; font-size: 0.75rem; margin-bottom: 0.3rem; }
.edit-row input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 6px;
  color: #e2e8f0;
  font-size: 0.9rem;
  box-sizing: border-box;
}
.edit-row input:focus { outline: none; border-color: #60a5fa; }

.add-budget { background: #1e293b; border-radius: 12px; padding: 1.5rem; }
.add-budget h2 { color: #e2e8f0; font-size: 1rem; margin: 0 0 1rem; }

.add-row { display: flex; gap: 0.75rem; }

.filter-select, .budget-input {
  padding: 0.6rem 0.8rem;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 0.9rem;
}

.filter-select { flex: 1; }
.budget-input { width: 150px; }
.filter-select:focus, .budget-input:focus { outline: none; border-color: #60a5fa; }

.btn-add {
  padding: 0.6rem 1.25rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  white-space: nowrap;
}
.btn-add:hover { background: #2563eb; }
</style>
