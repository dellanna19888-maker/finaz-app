// Baut einen kompakten Snapshot des App-Zustands, den die "Zentrale" als
// Kontext an die KI mitschickt (Content-Plan + Wissensbasis, nur das Nötige).

import type { useTaskStore } from '../stores/tasks'
import { STATUSES } from '../stores/tasks'

type TaskStore = ReturnType<typeof useTaskStore>

const statusLabel = (k: string) => STATUSES.find((s) => s.key === k)?.label ?? k

export function buildContext(tasks: TaskStore): string {
  const lines: string[] = [
    `Datum: ${new Date().toISOString().slice(0, 10)}`,
    `Content: ${tasks.openCount} in Arbeit · ${tasks.doneCount} veröffentlicht · ${tasks.overdue.length} überfällig`,
  ]

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

  try {
    const note = localStorage.getItem('finaz_notes') || ''
    if (note.trim()) lines.push('', `Wissensbasis/Notizen (Auszug): ${note.slice(0, 400)}${note.length > 400 ? ' …' : ''}`)
  } catch {
    /* localStorage nicht verfügbar – ignorieren */
  }

  return lines.join('\n')
}
