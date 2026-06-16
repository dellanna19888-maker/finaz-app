// Aktionen der "Zentrale": Die KI gibt Handlungswünsche als ```action-Block
// (JSON) aus. Hier werden sie aus dem Text geparst, beschriftet und – nach
// Bestätigung durch den Nutzer – real gegen die Stores / den Router ausgeführt.

import type { Router } from 'vue-router'
import type { useTransactionStore, TransactionType } from '../stores/transactions'
import type { useBudgetStore } from '../stores/budgets'
import { evaluate } from '../compliance/gateway'

type TxStore = ReturnType<typeof useTransactionStore>
type BudStore = ReturnType<typeof useBudgetStore>

export interface ChatAction {
  tool: string
  args: Record<string, unknown>
}

export interface ActionContext {
  tx: TxStore
  bud: BudStore
  router: Router
}

// Code-Fence mit Sprache "action": ```action\n{ ... }\n```
const FENCE = /```[ \t]*action[ \t]*\r?\n([\s\S]*?)```/gi

export function parseActions(text: string): ChatAction[] {
  const out: ChatAction[] = []
  for (const m of text.matchAll(FENCE)) {
    try {
      const obj = JSON.parse(m[1].trim()) as { tool?: unknown; args?: unknown }
      if (obj && typeof obj.tool === 'string') {
        out.push({ tool: obj.tool, args: obj.args && typeof obj.args === 'object' ? (obj.args as Record<string, unknown>) : {} })
      }
    } catch {
      /* ungültigen Block ignorieren */
    }
  }
  return out
}

/** Entfernt die Aktionsblöcke aus dem Text (für die Anzeige). */
export function stripActions(text: string): string {
  return text.replace(FENCE, '').replace(/\n{3,}/g, '\n\n').trim()
}

const fmtEur = (n: number) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(n)

export function actionLabel(a: ChatAction): string {
  const ar = a.args as Record<string, string | number | undefined>
  switch (a.tool) {
    case 'add_transaction':
      return `${ar.type === 'income' ? 'Einnahme' : 'Ausgabe'} erfassen: ${fmtEur(Number(ar.amount) || 0)} · ${ar.category ?? '?'}${ar.description ? ` (${ar.description})` : ''}`
    case 'set_budget':
      return `Budget setzen: ${ar.category ?? '?'} → ${fmtEur(Number(ar.limit) || 0)}`
    case 'append_note':
      return `Notiz ergänzen (${String(ar.content ?? '').length} Zeichen)`
    case 'navigate':
      return `Wechseln zu ${ar.to ?? '?'}`
    case 'compliance_check':
      return `Compliance-Prüfung ausführen${ar.jurisdiction ? ` (${ar.jurisdiction})` : ''}`
    case 'delete_transaction':
      return `Transaktion löschen (ID ${ar.id ?? '?'})`
    case 'remove_budget':
      return `Budget entfernen: ${ar.category ?? '?'}`
    default:
      return `Unbekannte Aktion: ${a.tool}`
  }
}

const ROUTES = new Set(['/', '/dashboard', '/transactions', '/budget', '/reports', '/notes', '/compliance', '/settings'])
const NOTES_KEY = 'finaz_notes'

export async function executeAction(a: ChatAction, ctx: ActionContext): Promise<string> {
  const ar = a.args as Record<string, string | number | undefined>
  switch (a.tool) {
    case 'add_transaction': {
      const type: TransactionType = ar.type === 'income' ? 'income' : 'expense'
      const amount = Number(ar.amount)
      if (!Number.isFinite(amount) || amount <= 0) throw new Error('Ungültiger Betrag.')
      const category = String(ar.category || 'Sonstiges')
      const date = /^\d{4}-\d{2}-\d{2}$/.test(String(ar.date || '')) ? String(ar.date) : new Date().toISOString().slice(0, 10)
      ctx.tx.addTransaction({ type, amount, category, description: String(ar.description || ''), date })
      return `${type === 'income' ? 'Einnahme' : 'Ausgabe'} ${fmtEur(amount)} (${category}) erfasst.`
    }
    case 'set_budget': {
      const limit = Number(ar.limit)
      if (!Number.isFinite(limit) || limit < 0) throw new Error('Ungültiges Budget.')
      const category = String(ar.category || '').trim()
      if (!category) throw new Error('Kategorie fehlt.')
      ctx.bud.setBudget(category, limit)
      return `Budget für ${category} auf ${fmtEur(limit)} gesetzt.`
    }
    case 'append_note': {
      const content = String(ar.content || '')
      if (!content.trim()) throw new Error('Kein Notizinhalt.')
      const cur = localStorage.getItem(NOTES_KEY) || ''
      localStorage.setItem(NOTES_KEY, cur ? `${cur}\n\n${content}` : content)
      return 'Notiz ergänzt (unter 📝 Notizen sichtbar).'
    }
    case 'navigate': {
      const to = String(ar.to || '')
      if (!ROUTES.has(to)) throw new Error(`Unbekanntes Ziel: ${to}`)
      await ctx.router.push(to)
      return `Gewechselt zu ${to}.`
    }
    case 'compliance_check': {
      const ev = evaluate({
        action: String(ar.action || 'chat'),
        text: String(ar.text || ''),
        jurisdiction: String(ar.jurisdiction || 'EU'),
      })
      const reasons = ev.reasons.length ? ev.reasons.join('; ') : 'keine Befunde'
      return `Compliance: ${ev.status} (${ev.rulesetLabel}) – ${reasons}.`
    }
    case 'delete_transaction': {
      const id = String(ar.id || '').trim()
      if (!id) throw new Error('Transaktions-ID fehlt.')
      const t = ctx.tx.transactions.find((x) => x.id === id)
      if (!t) throw new Error(`Keine Transaktion mit ID ${id} gefunden.`)
      ctx.tx.deleteTransaction(id)
      return `Transaktion gelöscht: ${t.type === 'income' ? 'Einnahme' : 'Ausgabe'} ${fmtEur(t.amount)} (${t.category}).`
    }
    case 'remove_budget': {
      const category = String(ar.category || '').trim()
      if (!category) throw new Error('Kategorie fehlt.')
      ctx.bud.removeBudget(category)
      return `Budget für ${category} entfernt.`
    }
    default:
      throw new Error(`Unbekannte Aktion: ${a.tool}`)
  }
}
