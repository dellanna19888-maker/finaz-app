import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export type TransactionType = 'income' | 'expense'

export interface Transaction {
  id: string
  type: TransactionType
  amount: number
  category: string
  description: string
  date: string
}

export const INCOME_CATEGORIES = ['Gehalt', 'Freelance', 'Investitionen', 'Geschenke', 'Sonstiges']
export const EXPENSE_CATEGORIES = ['Wohnen', 'Lebensmittel', 'Transport', 'Gesundheit', 'Freizeit', 'Kleidung', 'Bildung', 'Restaurants', 'Sonstiges']

const STORAGE_KEY = 'finaz_transactions'

function loadFromStorage(): Transaction[] {
  try {
    const data = localStorage.getItem(STORAGE_KEY)
    return data ? JSON.parse(data) : sampleData()
  } catch {
    return sampleData()
  }
}

function sampleData(): Transaction[] {
  const now = new Date()
  const month = now.getMonth()
  const year = now.getFullYear()
  const d = (day: number, m = month) => new Date(year, m, day).toISOString().split('T')[0]

  return [
    { id: '1', type: 'income', amount: 3200, category: 'Gehalt', description: 'Monatsgehalt', date: d(1) },
    { id: '2', type: 'income', amount: 450, category: 'Freelance', description: 'Webprojekt', date: d(5) },
    { id: '3', type: 'expense', amount: 850, category: 'Wohnen', description: 'Miete', date: d(1) },
    { id: '4', type: 'expense', amount: 120, category: 'Lebensmittel', description: 'Supermarkt', date: d(3) },
    { id: '5', type: 'expense', amount: 89, category: 'Transport', description: 'Monatsticket', date: d(2) },
    { id: '6', type: 'expense', amount: 45, category: 'Restaurants', description: 'Essen gehen', date: d(7) },
    { id: '7', type: 'expense', amount: 199, category: 'Kleidung', description: 'Winterjacke', date: d(10) },
    { id: '8', type: 'expense', amount: 30, category: 'Freizeit', description: 'Kino', date: d(12) },
    { id: '9', type: 'income', amount: 200, category: 'Geschenke', description: 'Geburtstag', date: d(15) },
    { id: '10', type: 'expense', amount: 65, category: 'Gesundheit', description: 'Apotheke', date: d(8) },
  ]
}

export const useTransactionStore = defineStore('transactions', () => {
  const transactions = ref<Transaction[]>(loadFromStorage())

  function save() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(transactions.value))
  }

  function addTransaction(tx: Omit<Transaction, 'id'>) {
    transactions.value.unshift({ ...tx, id: Date.now().toString() })
    save()
  }

  function deleteTransaction(id: string) {
    transactions.value = transactions.value.filter(t => t.id !== id)
    save()
  }

  function updateTransaction(updated: Transaction) {
    const i = transactions.value.findIndex(t => t.id === updated.id)
    if (i !== -1) transactions.value[i] = updated
    save()
  }

  const totalIncome = computed(() =>
    transactions.value.filter(t => t.type === 'income').reduce((s, t) => s + t.amount, 0)
  )

  const totalExpenses = computed(() =>
    transactions.value.filter(t => t.type === 'expense').reduce((s, t) => s + t.amount, 0)
  )

  const balance = computed(() => totalIncome.value - totalExpenses.value)

  function byMonth(year: number, month: number) {
    return transactions.value.filter(t => {
      const d = new Date(t.date)
      return d.getFullYear() === year && d.getMonth() === month
    })
  }

  function expensesByCategory() {
    const map: Record<string, number> = {}
    transactions.value.filter(t => t.type === 'expense').forEach(t => {
      map[t.category] = (map[t.category] || 0) + t.amount
    })
    return map
  }

  function monthlyTotals() {
    const map: Record<string, { income: number; expense: number }> = {}
    transactions.value.forEach(t => {
      const key = t.date.slice(0, 7)
      if (!map[key]) map[key] = { income: 0, expense: 0 }
      if (t.type === 'income') map[key].income += t.amount
      else map[key].expense += t.amount
    })
    return map
  }

  return {
    transactions,
    totalIncome,
    totalExpenses,
    balance,
    addTransaction,
    deleteTransaction,
    updateTransaction,
    byMonth,
    expensesByCategory,
    monthlyTotals,
  }
})
