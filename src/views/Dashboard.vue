<template>
  <div class="page">
    <div class="page-header">
      <h1>Dashboard</h1>
      <span class="subtitle">{{ currentMonthLabel }}</span>
    </div>

    <div class="cards">
      <div class="card balance">
        <div class="card-label">Kontostand</div>
        <div class="card-value" :class="store.balance >= 0 ? 'positive' : 'negative'">
          {{ fmt(store.balance) }}
        </div>
      </div>
      <div class="card income">
        <div class="card-label">Einnahmen</div>
        <div class="card-value positive">{{ fmt(store.totalIncome) }}</div>
      </div>
      <div class="card expense">
        <div class="card-label">Ausgaben</div>
        <div class="card-value negative">{{ fmt(store.totalExpenses) }}</div>
      </div>
    </div>

    <div class="section-grid">
      <div class="section-card">
        <h2>Letzte Transaktionen</h2>
        <div class="tx-list">
          <div v-for="tx in recent" :key="tx.id" class="tx-row">
            <div class="tx-left">
              <span class="tx-cat">{{ tx.category }}</span>
              <span class="tx-desc">{{ tx.description }}</span>
            </div>
            <div class="tx-right">
              <span :class="['tx-amount', tx.type === 'income' ? 'positive' : 'negative']">
                {{ tx.type === 'income' ? '+' : '-' }}{{ fmt(tx.amount) }}
              </span>
              <span class="tx-date">{{ tx.date }}</span>
            </div>
          </div>
          <div v-if="recent.length === 0" class="empty">Keine Transaktionen vorhanden.</div>
        </div>
        <RouterLink to="/transactions" class="see-all">Alle anzeigen →</RouterLink>
      </div>

      <div class="section-card">
        <h2>Budget-Übersicht</h2>
        <div class="budget-list">
          <div v-for="budget in budgetOverview" :key="budget.category" class="budget-row">
            <div class="budget-info">
              <span class="budget-cat">{{ budget.category }}</span>
              <span class="budget-nums">{{ fmt(budget.spent) }} / {{ fmt(budget.limit) }}</span>
            </div>
            <div class="progress-bar">
              <div
                class="progress-fill"
                :style="{ width: Math.min(budget.pct, 100) + '%' }"
                :class="budget.pct > 90 ? 'danger' : budget.pct > 70 ? 'warning' : 'ok'"
              />
            </div>
          </div>
        </div>
        <RouterLink to="/budget" class="see-all">Budgets verwalten →</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useTransactionStore } from '../stores/transactions'
import { useBudgetStore } from '../stores/budgets'

const store = useTransactionStore()
const budgetStore = useBudgetStore()

const now = new Date()
const currentMonthLabel = now.toLocaleDateString('de-DE', { month: 'long', year: 'numeric' })

const fmt = (n: number) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(n)

const recent = computed(() => store.transactions.slice(0, 6))

const budgetOverview = computed(() => {
  const expCat = store.expensesByCategory()
  return budgetStore.budgets.map(b => ({
    category: b.category,
    limit: b.limit,
    spent: expCat[b.category] || 0,
    pct: ((expCat[b.category] || 0) / b.limit) * 100,
  }))
})
</script>

<style scoped>
.page { padding: 2rem; max-width: 1200px; margin: 0 auto; }
.page-header { margin-bottom: 1.5rem; }
.page-header h1 { color: #e2e8f0; font-size: 1.8rem; margin: 0; }
.subtitle { color: #64748b; font-size: 0.9rem; }

.cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.card {
  background: #1e293b;
  border-radius: 12px;
  padding: 1.5rem;
  border-left: 4px solid transparent;
}

.balance { border-left-color: #60a5fa; }
.income { border-left-color: #10b981; }
.expense { border-left-color: #ef4444; }

.card-label { color: #64748b; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }
.card-value { font-size: 1.8rem; font-weight: 700; }
.positive { color: #10b981; }
.negative { color: #ef4444; }

.section-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }

.section-card {
  background: #1e293b;
  border-radius: 12px;
  padding: 1.5rem;
}

.section-card h2 { color: #e2e8f0; font-size: 1rem; margin: 0 0 1rem; }

.tx-list { display: flex; flex-direction: column; gap: 0.75rem; }

.tx-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 0;
  border-bottom: 1px solid #0f172a;
}

.tx-left { display: flex; flex-direction: column; }
.tx-cat { color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; }
.tx-desc { color: #e2e8f0; font-size: 0.9rem; }
.tx-right { display: flex; flex-direction: column; align-items: flex-end; }
.tx-amount { font-weight: 600; font-size: 0.95rem; }
.tx-date { color: #475569; font-size: 0.75rem; }

.empty { color: #475569; text-align: center; padding: 1rem; }

.see-all {
  display: inline-block;
  margin-top: 1rem;
  color: #60a5fa;
  text-decoration: none;
  font-size: 0.85rem;
}
.see-all:hover { text-decoration: underline; }

.budget-list { display: flex; flex-direction: column; gap: 0.75rem; }
.budget-row { }
.budget-info { display: flex; justify-content: space-between; margin-bottom: 0.3rem; }
.budget-cat { color: #e2e8f0; font-size: 0.9rem; }
.budget-nums { color: #94a3b8; font-size: 0.8rem; }

.progress-bar { height: 6px; background: #0f172a; border-radius: 3px; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 3px; transition: width 0.4s; }
.ok { background: #10b981; }
.warning { background: #f59e0b; }
.danger { background: #ef4444; }
</style>
