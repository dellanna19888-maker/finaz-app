// Baut einen kompakten Snapshot des App-Zustands, den die "Zentrale" als
// Kontext an die KI mitschickt (Content-Plan + Wissensbasis, nur das Nötige).

import type { useTaskStore } from '../stores/tasks'
import { STATUSES } from '../stores/tasks'
import type { useFinanceStore } from '../stores/finance'

type TaskStore = ReturnType<typeof useTaskStore>
type FinanceStore = ReturnType<typeof useFinanceStore>

// Kompakte Finanz-Aggregation: Kennzahlen + Kategorien + letzte Buchungen.
// Wird sowohl von der Finanzen-Seite (KI-Überblick) als auch von der Zentrale
// (Snapshot-Kontext) genutzt – bewusst ohne Einzelbeträge-Flut.
export function buildFinanceSummary(finance: FinanceStore): string {
  const cur = finance.currency
  const lines: string[] = [
    `Währung: ${cur}`,
    `Einnahmen gesamt: ${finance.totalIncome.toFixed(2)} ${cur}`,
    `Ausgaben gesamt: ${finance.totalExpense.toFixed(2)} ${cur}`,
    `Saldo: ${finance.balance.toFixed(2)} ${cur}`,
  ]
  const fmtCats = (rec: Record<string, number>) =>
    Object.entries(rec)
      .sort((a, b) => b[1] - a[1])
      .map(([k, v]) => `${k}: ${v.toFixed(2)}`)
      .join(', ')
  const inc = fmtCats(finance.byCategory.income)
  const exp = fmtCats(finance.byCategory.expense)
  if (inc) lines.push(`Einnahmen nach Kategorie: ${inc}`)
  if (exp) lines.push(`Ausgaben nach Kategorie: ${exp}`)

  const recent = finance.transactions.slice(0, 12)
  if (recent.length) {
    lines.push('', 'Letzte Buchungen (id · typ · betrag · kategorie · datum):')
    for (const t of recent) {
      lines.push(`- ${t.id} · ${t.type === 'income' ? 'Einnahme' : 'Ausgabe'} · ${t.amount.toFixed(2)} ${cur} · ${t.category || '-'} · ${t.date}`)
    }
  }
  return lines.join('\n')
}

const statusLabel = (k: string) => STATUSES.find((s) => s.key === k)?.label ?? k

export function buildContext(tasks: TaskStore, finance?: FinanceStore): string {
  const lines: string[] = [
    `Datum: ${new Date().toISOString().slice(0, 10)}`,
    `Content: ${tasks.openCount} in Arbeit · ${tasks.doneCount} veröffentlicht · ${tasks.overdue.length} überfällig`,
  ]
  if (finance) {
    const cur = finance.currency
    lines.push(
      `Finanzen: Einnahmen ${finance.totalIncome.toFixed(2)} · Ausgaben ${finance.totalExpense.toFixed(2)} · Saldo ${finance.balance.toFixed(2)} ${cur} (${finance.transactions.length} Buchungen)`,
    )
  }

  const projects = tasks.projects
  if (projects.length) lines.push(`Projekte/Reihen: ${projects.join(', ')}`)

  const open = tasks.tasks.filter((t) => !t.done).slice(0, 20)
  if (open.length) {
    lines.push('', 'Offene Inhalte (id · titel · status · plattform · prio · projekt · fällig):')
    for (const t of open) {
      lines.push(
        `- ${t.id} · ${t.title} · ${statusLabel(t.status)}${t.platform ? ` · ${t.platform}` : ''} · ${t.priority}${t.project ? ` · ${t.project}` : ''}${t.due ? ` · ${t.due}` : ''}`,
      )
    }
  }

  const live = tasks.tasks.filter((t) => t.done).slice(0, 5)
  if (live.length) {
    lines.push('', 'Zuletzt veröffentlicht (id · titel):')
    for (const t of live) lines.push(`- ${t.id} · ${t.title}`)
  }

  // Kanal-Check: eigenes Profil + Konkurrenz (für Performance-/Konkurrenz-Analyse).
  try {
    const pr = JSON.parse(localStorage.getItem('finaz_channel') || 'null') as
      | { platform?: string; handle?: string; followers?: number; niche?: string; recent?: string }
      | null
    if (pr && (pr.handle || pr.followers || pr.niche || (pr.recent && pr.recent.trim()))) {
      lines.push('', `Mein Kanal: ${pr.platform || '?'} ${pr.handle || ''} · ${pr.followers || 0} Follower · Nische: ${pr.niche || '-'}`)
      if (pr.recent && pr.recent.trim()) lines.push(`Meine letzten Inhalte:\n${pr.recent.slice(0, 500)}`)
    }
    const comps = JSON.parse(localStorage.getItem('finaz_competitors') || '[]') as Array<{ handle?: string; followers?: number; notes?: string }>
    if (Array.isArray(comps) && comps.length) {
      lines.push('', 'Konkurrenz:')
      for (const c of comps.slice(0, 5)) lines.push(`- ${c.handle || '?'} · ${c.followers || 0} Follower${c.notes ? ` · ${c.notes}` : ''}`)
    }
  } catch {
    /* ignore */
  }

  if (finance && finance.transactions.length) {
    const cur = finance.currency
    lines.push('', 'Letzte Buchungen (id · typ · betrag · kategorie · datum):')
    for (const t of finance.transactions.slice(0, 10)) {
      lines.push(`- ${t.id} · ${t.type === 'income' ? 'Einnahme' : 'Ausgabe'} · ${t.amount.toFixed(2)} ${cur} · ${t.category || '-'} · ${t.date}`)
    }
  }

  try {
    const note = localStorage.getItem('finaz_notes') || ''
    if (note.trim()) lines.push('', `Wissensbasis/Notizen (Auszug): ${note.slice(0, 400)}${note.length > 400 ? ' …' : ''}`)
  } catch {
    /* localStorage nicht verfügbar – ignorieren */
  }

  return lines.join('\n')
}
