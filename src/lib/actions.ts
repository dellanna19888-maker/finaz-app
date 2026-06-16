// Aktionen der "Zentrale": Die KI gibt Handlungswünsche als ```action-Block
// (JSON) aus. Hier werden sie aus dem Text geparst, beschriftet und – nach
// Bestätigung durch den Nutzer – real gegen den Aufgaben-Store / die
// Wissensbasis (Notizen) / den Router ausgeführt.

import type { Router } from 'vue-router'
import type { useTaskStore, Priority } from '../stores/tasks'
import { evaluate } from '../compliance/gateway'

type TaskStore = ReturnType<typeof useTaskStore>

export interface ChatAction {
  tool: string
  args: Record<string, unknown>
}

export interface ActionContext {
  tasks: TaskStore
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

const PRIOS = new Set(['low', 'normal', 'high'])
function normPriority(v: unknown): Priority {
  const s = String(v ?? '').toLowerCase()
  return (PRIOS.has(s) ? s : 'normal') as Priority
}

const isDate = (v: unknown) => /^\d{4}-\d{2}-\d{2}$/.test(String(v ?? ''))

export function actionLabel(a: ChatAction): string {
  const ar = a.args as Record<string, string | number | boolean | undefined>
  switch (a.tool) {
    case 'add_task':
      return `Aufgabe anlegen: „${ar.title ?? '?'}"${ar.project ? ` · ${ar.project}` : ''}${ar.due ? ` · fällig ${ar.due}` : ''}`
    case 'complete_task':
      return `Aufgabe abhaken (ID ${ar.id ?? '?'})`
    case 'reopen_task':
      return `Aufgabe wieder öffnen (ID ${ar.id ?? '?'})`
    case 'update_task':
      return `Aufgabe bearbeiten (ID ${ar.id ?? '?'})`
    case 'delete_task':
      return `Aufgabe löschen (ID ${ar.id ?? '?'})`
    case 'append_note':
      return `Wissen/Notiz ergänzen (${String(ar.content ?? '').length} Zeichen)`
    case 'navigate':
      return `Wechseln zu ${ar.to ?? '?'}`
    case 'compliance_check':
      return `Compliance-Prüfung ausführen${ar.jurisdiction ? ` (${ar.jurisdiction})` : ''}`
    default:
      return `Unbekannte Aktion: ${a.tool}`
  }
}

const ROUTES = new Set(['/', '/tasks', '/notes', '/compliance', '/settings'])
const NOTES_KEY = 'finaz_notes'

export async function executeAction(a: ChatAction, ctx: ActionContext): Promise<string> {
  const ar = a.args as Record<string, string | number | boolean | undefined>
  switch (a.tool) {
    case 'add_task': {
      const title = String(ar.title || '').trim()
      if (!title) throw new Error('Titel fehlt.')
      ctx.tasks.addTask({
        title,
        priority: normPriority(ar.priority),
        project: String(ar.project || ''),
        due: isDate(ar.due) ? String(ar.due) : '',
        notes: String(ar.notes || ''),
      })
      return `Aufgabe „${title}" angelegt.`
    }
    case 'complete_task': {
      const id = String(ar.id || '').trim()
      const t = ctx.tasks.tasks.find((x) => x.id === id)
      if (!t) throw new Error(`Keine Aufgabe mit ID ${id} gefunden.`)
      ctx.tasks.setDone(id, true)
      return `Aufgabe „${t.title}" abgehakt.`
    }
    case 'reopen_task': {
      const id = String(ar.id || '').trim()
      const t = ctx.tasks.tasks.find((x) => x.id === id)
      if (!t) throw new Error(`Keine Aufgabe mit ID ${id} gefunden.`)
      ctx.tasks.setDone(id, false)
      return `Aufgabe „${t.title}" wieder geöffnet.`
    }
    case 'update_task': {
      const id = String(ar.id || '').trim()
      const cur = ctx.tasks.tasks.find((x) => x.id === id)
      if (!cur) throw new Error(`Keine Aufgabe mit ID ${id} gefunden.`)
      const updated = { ...cur }
      if (ar.title !== undefined && String(ar.title).trim()) updated.title = String(ar.title)
      if (ar.priority !== undefined) updated.priority = normPriority(ar.priority)
      if (ar.project !== undefined) updated.project = String(ar.project)
      if (ar.due !== undefined && (String(ar.due) === '' || isDate(ar.due))) updated.due = String(ar.due)
      if (ar.notes !== undefined) updated.notes = String(ar.notes)
      if (ar.done !== undefined) updated.done = ar.done === true || ar.done === 'true'
      ctx.tasks.updateTask(updated)
      return `Aufgabe „${updated.title}" aktualisiert.`
    }
    case 'delete_task': {
      const id = String(ar.id || '').trim()
      const t = ctx.tasks.tasks.find((x) => x.id === id)
      if (!t) throw new Error(`Keine Aufgabe mit ID ${id} gefunden.`)
      ctx.tasks.deleteTask(id)
      return `Aufgabe „${t.title}" gelöscht.`
    }
    case 'append_note': {
      const content = String(ar.content || '')
      if (!content.trim()) throw new Error('Kein Inhalt.')
      const cur = localStorage.getItem(NOTES_KEY) || ''
      localStorage.setItem(NOTES_KEY, cur ? `${cur}\n\n${content}` : content)
      return 'Wissen/Notiz ergänzt (unter 📚 Wissen sichtbar).'
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
    default:
      throw new Error(`Unbekannte Aktion: ${a.tool}`)
  }
}
