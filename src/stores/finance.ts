import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

export type TxType = 'income' | 'expense'

export interface Transaction {
  id: string
  type: TxType
  amount: number // immer positiv; das Vorzeichen ergibt sich aus type
  category: string
  note: string
  date: string // 'YYYY-MM-DD'
}

export interface NewTransaction {
  type: TxType
  amount: number
  category?: string
  note?: string
  date?: string
}

const TX_KEY = 'finaz_finance'
const CUR_KEY = 'finaz_currency'

// Kategorien passend zum Creator-Business (Vorschläge, frei erweiterbar).
export const INCOME_CATEGORIES = ['AdSense', 'Sponsoring', 'Affiliate', 'Produkt/Shop', 'Mitglieder', 'Sonstiges']
export const EXPENSE_CATEGORIES = ['Equipment', 'Software/Abo', 'Werbung', 'Freelancer', 'Gebühren', 'Sonstiges']

export const CURRENCIES = ['EUR', 'CHF', 'USD', 'GBP'] as const
export type Currency = (typeof CURRENCIES)[number]

function today(): string {
  return new Date().toISOString().slice(0, 10)
}

// Robust gegen alte/teildefinierte Einträge.
function normalize(raw: unknown): Transaction {
  const t = (raw ?? {}) as Partial<Transaction>
  const type: TxType = t.type === 'expense' ? 'expense' : 'income'
  const amount = Math.abs(Number(t.amount) || 0)
  return {
    id: String(t.id ?? Date.now().toString()),
    type,
    amount,
    category: String(t.category ?? ''),
    note: String(t.note ?? ''),
    date: /^\d{4}-\d{2}-\d{2}$/.test(String(t.date ?? '')) ? String(t.date) : today(),
  }
}

function loadFromStorage(): Transaction[] {
  try {
    const data = localStorage.getItem(TX_KEY)
    if (!data) return sampleData()
    const arr = JSON.parse(data) as unknown[]
    return Array.isArray(arr) ? arr.map(normalize) : sampleData()
  } catch {
    return sampleData()
  }
}

function loadCurrency(): Currency {
  const c = localStorage.getItem(CUR_KEY)
  return (CURRENCIES as readonly string[]).includes(c || '') ? (c as Currency) : 'EUR'
}

function sampleData(): Transaction[] {
  const d = today()
  return [
    normalize({ id: 'f1', type: 'income', amount: 420.5, category: 'AdSense', note: 'YouTube-Auszahlung', date: d }),
    normalize({ id: 'f2', type: 'income', amount: 800, category: 'Sponsoring', note: 'Integration im Video', date: d }),
    normalize({ id: 'f3', type: 'expense', amount: 24.9, category: 'Software/Abo', note: 'Schnitt-Software', date: d }),
    normalize({ id: 'f4', type: 'expense', amount: 199, category: 'Equipment', note: 'Mikrofon', date: d }),
  ]
}

export const useFinanceStore = defineStore('finance', () => {
  const transactions = ref<Transaction[]>(loadFromStorage())
  const currency = ref<Currency>(loadCurrency())

  watch(transactions, () => localStorage.setItem(TX_KEY, JSON.stringify(transactions.value)), { deep: true })
  watch(currency, (c) => localStorage.setItem(CUR_KEY, c))

  function addTransaction(input: NewTransaction): Transaction {
    const tx: Transaction = {
      id: Date.now().toString(),
      type: input.type === 'expense' ? 'expense' : 'income',
      amount: Math.abs(Number(input.amount) || 0),
      category: input.category ?? '',
      note: input.note ?? '',
      date: input.date && /^\d{4}-\d{2}-\d{2}$/.test(input.date) ? input.date : today(),
    }
    transactions.value.unshift(tx)
    return tx
  }

  function updateTransaction(updated: Transaction) {
    const i = transactions.value.findIndex((x) => x.id === updated.id)
    if (i !== -1) transactions.value[i] = normalize(updated)
  }

  function deleteTransaction(id: string) {
    transactions.value = transactions.value.filter((x) => x.id !== id)
  }

  // Ersetzt alle Buchungen (für Rückgängig / Wiederherstellen aus der Zentrale).
  function setAll(list: Transaction[]) {
    transactions.value = list.map(normalize)
  }

  const totalIncome = computed(() => transactions.value.filter((t) => t.type === 'income').reduce((s, t) => s + t.amount, 0))
  const totalExpense = computed(() => transactions.value.filter((t) => t.type === 'expense').reduce((s, t) => s + t.amount, 0))
  const balance = computed(() => totalIncome.value - totalExpense.value)

  // Summe je Kategorie (für Übersicht/KI-Kontext), getrennt nach Typ.
  const byCategory = computed(() => {
    const out: Record<TxType, Record<string, number>> = { income: {}, expense: {} }
    for (const t of transactions.value) {
      const cat = t.category || 'Sonstiges'
      out[t.type][cat] = (out[t.type][cat] || 0) + t.amount
    }
    return out
  })

  function format(value: number): string {
    try {
      return new Intl.NumberFormat('de-DE', { style: 'currency', currency: currency.value }).format(value)
    } catch {
      return `${value.toFixed(2)} ${currency.value}`
    }
  }

  return {
    transactions,
    currency,
    addTransaction,
    updateTransaction,
    deleteTransaction,
    setAll,
    totalIncome,
    totalExpense,
    balance,
    byCategory,
    format,
  }
})
