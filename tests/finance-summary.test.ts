import { describe, it, expect } from 'vitest'
import { buildFinanceSummary, buildContext } from '../src/lib/appState'

// Schlanke Fakes der Pinia-Stores: buildFinanceSummary/buildContext lesen nur
// die hier abgebildeten Felder (keine Pinia-Reaktivität nötig).
const fakeFinance = {
  currency: 'EUR',
  totalIncome: 1220.5,
  totalExpense: 223.9,
  balance: 996.6,
  byCategory: {
    income: { AdSense: 420.5, Sponsoring: 800 },
    expense: { Equipment: 199, 'Software/Abo': 24.9 },
  },
  transactions: [
    { id: 'f1', type: 'income', amount: 800, category: 'Sponsoring', note: '', date: '2026-06-10' },
    { id: 'f2', type: 'expense', amount: 199, category: 'Equipment', note: '', date: '2026-06-09' },
  ],
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
} as any

const fakeTasks = {
  openCount: 3,
  doneCount: 1,
  overdue: [],
  projects: ['YouTube'],
  tasks: [],
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
} as any

describe('buildFinanceSummary', () => {
  it('enthält Kennzahlen, Kategorien und Buchungs-IDs', () => {
    const s = buildFinanceSummary(fakeFinance)
    expect(s).toContain('Saldo: 996.60 EUR')
    expect(s).toContain('Einnahmen nach Kategorie')
    expect(s).toContain('Sponsoring: 800.00')
    expect(s).toContain('f1')
    expect(s).toContain('Einnahme')
  })
})

describe('buildContext', () => {
  it('nimmt eine Finanz-Zeile auf, wenn der Finance-Store übergeben wird', () => {
    const ctx = buildContext(fakeTasks, fakeFinance)
    expect(ctx).toContain('Finanzen: Einnahmen 1220.50')
    expect(ctx).toContain('Saldo 996.60 EUR')
    expect(ctx).toContain('Letzte Buchungen')
  })

  it('lässt Finanzen weg, wenn kein Store übergeben wird', () => {
    const ctx = buildContext(fakeTasks)
    expect(ctx).not.toContain('Finanzen:')
  })
})
