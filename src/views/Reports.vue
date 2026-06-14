<template>
  <div class="page">
    <div class="page-header">
      <h1>Berichte & Auswertungen</h1>
    </div>

    <div class="charts-grid">
      <div class="chart-card wide">
        <h2>Einnahmen vs. Ausgaben (Monatlich)</h2>
        <Bar v-if="barData" :data="barData" :options="barOptions" />
      </div>

      <div class="chart-card">
        <h2>Ausgaben nach Kategorie</h2>
        <Doughnut v-if="pieData && hasPieData" :data="pieData" :options="pieOptions" />
        <div v-else class="empty">Keine Ausgaben vorhanden.</div>
      </div>

      <div class="chart-card">
        <h2>Top Ausgaben-Kategorien</h2>
        <div class="top-list">
          <div v-for="(item, i) in topExpenses" :key="item.category" class="top-row">
            <span class="rank">{{ i + 1 }}</span>
            <span class="top-cat">{{ item.category }}</span>
            <div class="top-bar-wrap">
              <div class="top-bar" :style="{ width: (item.amount / topExpenses[0].amount * 100) + '%' }" />
            </div>
            <span class="top-amount">{{ fmt(item.amount) }}</span>
          </div>
          <div v-if="topExpenses.length === 0" class="empty">Keine Daten.</div>
        </div>
      </div>
    </div>

    <div class="summary-card">
      <h2>Zusammenfassung</h2>
      <div class="summary-grid">
        <div class="stat">
          <div class="stat-label">Gesamteinnahmen</div>
          <div class="stat-value positive">{{ fmt(store.totalIncome) }}</div>
        </div>
        <div class="stat">
          <div class="stat-label">Gesamtausgaben</div>
          <div class="stat-value negative">{{ fmt(store.totalExpenses) }}</div>
        </div>
        <div class="stat">
          <div class="stat-label">Netto-Bilanz</div>
          <div class="stat-value" :class="store.balance >= 0 ? 'positive' : 'negative'">{{ fmt(store.balance) }}</div>
        </div>
        <div class="stat">
          <div class="stat-label">Sparquote</div>
          <div class="stat-value positive">
            {{ store.totalIncome > 0 ? Math.round((store.balance / store.totalIncome) * 100) : 0 }}%
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend,
  ArcElement,
} from 'chart.js'
import { Bar, Doughnut } from 'vue-chartjs'
import { useTransactionStore } from '../stores/transactions'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement)

const store = useTransactionStore()
const fmt = (n: number) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(n)

const monthlyTotals = computed(() => {
  const data = store.monthlyTotals()
  const keys = Object.keys(data).sort()
  return {
    labels: keys.map(k => {
      const [y, m] = k.split('-')
      return new Date(Number(y), Number(m) - 1).toLocaleDateString('de-DE', { month: 'short', year: '2-digit' })
    }),
    income: keys.map(k => data[k].income),
    expense: keys.map(k => data[k].expense),
  }
})

const barData = computed(() => ({
  labels: monthlyTotals.value.labels,
  datasets: [
    {
      label: 'Einnahmen',
      data: monthlyTotals.value.income,
      backgroundColor: 'rgba(16, 185, 129, 0.7)',
      borderRadius: 4,
    },
    {
      label: 'Ausgaben',
      data: monthlyTotals.value.expense,
      backgroundColor: 'rgba(239, 68, 68, 0.7)',
      borderRadius: 4,
    },
  ],
}))

const barOptions = {
  responsive: true,
  plugins: {
    legend: { labels: { color: '#94a3b8' } },
    tooltip: { callbacks: { label: (ctx: any) => fmt(ctx.raw) } },
  },
  scales: {
    x: { ticks: { color: '#64748b' }, grid: { color: '#1e293b' } },
    y: { ticks: { color: '#64748b', callback: (v: any) => fmt(v) }, grid: { color: '#334155' } },
  },
}

const CHART_COLORS = ['#60a5fa','#f472b6','#34d399','#fbbf24','#a78bfa','#f87171','#38bdf8','#4ade80','#fb923c']

const expByCat = computed(() => store.expensesByCategory())

const hasPieData = computed(() => Object.keys(expByCat.value).length > 0)

const pieData = computed(() => {
  const cats = Object.keys(expByCat.value)
  return {
    labels: cats,
    datasets: [{
      data: cats.map(c => expByCat.value[c]),
      backgroundColor: CHART_COLORS.slice(0, cats.length),
      borderWidth: 2,
      borderColor: '#0f172a',
    }],
  }
})

const pieOptions = {
  responsive: true,
  plugins: {
    legend: { labels: { color: '#94a3b8', padding: 12 }, position: 'bottom' as const },
    tooltip: { callbacks: { label: (ctx: any) => `${ctx.label}: ${fmt(ctx.raw)}` } },
  },
}

const topExpenses = computed(() =>
  Object.entries(expByCat.value)
    .map(([category, amount]) => ({ category, amount }))
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 5)
)
</script>

<style scoped>
.page { padding: 2rem; max-width: 1200px; margin: 0 auto; }
.page-header { margin-bottom: 2rem; }
.page-header h1 { color: #e2e8f0; font-size: 1.8rem; margin: 0; }

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.chart-card {
  background: #1e293b;
  border-radius: 12px;
  padding: 1.5rem;
}

.chart-card.wide { grid-column: 1 / -1; }
.chart-card h2 { color: #e2e8f0; font-size: 1rem; margin: 0 0 1.25rem; }

.empty { color: #475569; text-align: center; padding: 2rem; }

.top-list { display: flex; flex-direction: column; gap: 0.75rem; }
.top-row { display: grid; grid-template-columns: 24px 120px 1fr 100px; align-items: center; gap: 0.75rem; }

.rank { color: #475569; font-size: 0.85rem; font-weight: 600; }
.top-cat { color: #e2e8f0; font-size: 0.9rem; }
.top-bar-wrap { height: 8px; background: #0f172a; border-radius: 4px; overflow: hidden; }
.top-bar { height: 100%; background: linear-gradient(90deg, #3b82f6, #60a5fa); border-radius: 4px; transition: width 0.4s; }
.top-amount { color: #94a3b8; font-size: 0.85rem; text-align: right; }

.summary-card {
  background: #1e293b;
  border-radius: 12px;
  padding: 1.5rem;
}
.summary-card h2 { color: #e2e8f0; font-size: 1rem; margin: 0 0 1.25rem; }

.summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
.stat { }
.stat-label { color: #64748b; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.4rem; }
.stat-value { font-size: 1.5rem; font-weight: 700; }
.positive { color: #10b981; }
.negative { color: #ef4444; }

@media (max-width: 700px) {
  .page { padding: 1.25rem; }
  .page-header h1 { font-size: 1.5rem; }
  .charts-grid { grid-template-columns: 1fr; gap: 1rem; }
  .chart-card.wide { grid-column: auto; }
  .chart-box { height: 220px; }
  .top-row { grid-template-columns: 20px 80px 1fr 70px; gap: 0.5rem; }
  .summary-grid { grid-template-columns: 1fr 1fr; gap: 0.75rem; }
  .stat-value { font-size: 1.3rem; }
}
</style>
