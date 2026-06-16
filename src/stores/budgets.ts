import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Budget {
  category: string
  limit: number
}

const STORAGE_KEY = 'finaz_budgets'

function loadBudgets(): Budget[] {
  try {
    const data = localStorage.getItem(STORAGE_KEY)
    return data ? JSON.parse(data) : defaultBudgets()
  } catch {
    return defaultBudgets()
  }
}

function defaultBudgets(): Budget[] {
  return [
    { category: 'Wohnen', limit: 1000 },
    { category: 'Lebensmittel', limit: 300 },
    { category: 'Transport', limit: 150 },
    { category: 'Freizeit', limit: 200 },
    { category: 'Restaurants', limit: 150 },
    { category: 'Kleidung', limit: 100 },
    { category: 'Gesundheit', limit: 100 },
  ]
}

export const useBudgetStore = defineStore('budgets', () => {
  const budgets = ref<Budget[]>(loadBudgets())

  function save() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(budgets.value))
  }

  function setBudget(category: string, limit: number) {
    const existing = budgets.value.find(b => b.category === category)
    if (existing) existing.limit = limit
    else budgets.value.push({ category, limit })
    save()
  }

  function removeBudget(category: string) {
    budgets.value = budgets.value.filter(b => b.category !== category)
    save()
  }

  // Ersetzt alle Budgets (für Wiederherstellen / Rückgängig).
  function setAll(list: Budget[]) {
    budgets.value = list
    save()
  }

  return { budgets, setBudget, removeBudget, setAll }
})
