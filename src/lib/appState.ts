// Baut einen kompakten Snapshot des App-Zustands, den die "Zentrale" als
// Kontext an die KI mitschickt (aggregiert, nur die wirklich nötigen Daten).

import type { useTransactionStore } from '../stores/transactions'
import type { useBudgetStore } from '../stores/budgets'
import { INCOME_CATEGORIES, EXPENSE_CATEGORIES } from '../stores/transactions'

type TxStore = ReturnType<typeof useTransactionStore>
type BudStore = ReturnType<typeof useBudgetStore>

const fmt = (n: number) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(n)

export function buildContext(tx: TxStore, bud: BudStore): string {
  const byCat = tx.expensesByCategory()
  const rate = tx.totalIncome > 0 ? Math.round((tx.balance / tx.totalIncome) * 100) : 0

  const lines: string[] = [
    `Datum: ${new Date().toISOString().slice(0, 10)}`,
    `Einnahmen gesamt: ${fmt(tx.totalIncome)}`,
    `Ausgaben gesamt: ${fmt(tx.totalExpenses)}`,
    `Bilanz: ${fmt(tx.balance)}`,
    `Sparquote: ${rate}%`,
    '',
    'Ausgaben nach Kategorie (mit Budget):',
  ]
  for (const [cat, amount] of Object.entries(byCat).sort((a, b) => b[1] - a[1])) {
    const limit = bud.budgets.find((b) => b.category === cat)?.limit
    lines.push(`- ${cat}: ${fmt(amount)}${limit != null ? ` / Budget ${fmt(limit)}` : ''}`)
  }

  lines.push('', 'Budgets:')
  for (const b of bud.budgets) lines.push(`- ${b.category}: ${fmt(b.limit)}`)

  lines.push('', `Einnahmen-Kategorien: ${INCOME_CATEGORIES.join(', ')}`)
  lines.push(`Ausgaben-Kategorien: ${EXPENSE_CATEGORIES.join(', ')}`)

  const recent = tx.transactions.slice(0, 15)
  if (recent.length) {
    lines.push('', 'Letzte Transaktionen (id · datum · typ · betrag · kategorie · beschreibung):')
    for (const t of recent) {
      lines.push(
        `- ${t.id} · ${t.date} · ${t.type === 'income' ? 'Einnahme' : 'Ausgabe'} · ${fmt(t.amount)} · ${t.category}${t.description ? ` · ${t.description}` : ''}`,
      )
    }
  }

  try {
    const note = localStorage.getItem('finaz_notes') || ''
    if (note.trim()) lines.push('', `Notiz (Auszug): ${note.slice(0, 200)}${note.length > 200 ? ' …' : ''}`)
  } catch {
    /* localStorage nicht verfügbar – ignorieren */
  }

  return lines.join('\n')
}
