// Baut einen kompakten Snapshot des App-Zustands, den die "Zentrale" als
// Kontext an die KI mitschickt (Aufgaben + Wissensbasis, nur das Nötige).

import type { useTaskStore } from '../stores/tasks'

type TaskStore = ReturnType<typeof useTaskStore>

export function buildContext(tasks: TaskStore): string {
  const lines: string[] = [
    `Datum: ${new Date().toISOString().slice(0, 10)}`,
    `Aufgaben offen: ${tasks.openCount} · erledigt: ${tasks.doneCount} · überfällig: ${tasks.overdue.length}`,
  ]

  const projects = tasks.projects
  if (projects.length) lines.push(`Projekte: ${projects.join(', ')}`)

  const open = tasks.tasks.filter((t) => !t.done).slice(0, 20)
  if (open.length) {
    lines.push('', 'Offene Aufgaben (id · titel · prio · projekt · fällig):')
    for (const t of open) {
      lines.push(`- ${t.id} · ${t.title} · ${t.priority}${t.project ? ` · ${t.project}` : ''}${t.due ? ` · ${t.due}` : ''}`)
    }
  }

  const doneRecent = tasks.tasks.filter((t) => t.done).slice(0, 5)
  if (doneRecent.length) {
    lines.push('', 'Zuletzt erledigt (id · titel):')
    for (const t of doneRecent) lines.push(`- ${t.id} · ${t.title}`)
  }

  try {
    const note = localStorage.getItem('finaz_notes') || ''
    if (note.trim()) lines.push('', `Wissensbasis/Notizen (Auszug): ${note.slice(0, 400)}${note.length > 400 ? ' …' : ''}`)
  } catch {
    /* localStorage nicht verfügbar – ignorieren */
  }

  return lines.join('\n')
}
