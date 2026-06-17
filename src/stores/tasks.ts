import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export type Priority = 'low' | 'normal' | 'high'
export type ContentStatus = 'idee' | 'skript' | 'aufnahme' | 'schnitt' | 'live'

// Content-Pipeline: Reihenfolge + Anzeigelabels.
export const STATUSES: { key: ContentStatus; label: string }[] = [
  { key: 'idee', label: 'Idee' },
  { key: 'skript', label: 'Skript' },
  { key: 'aufnahme', label: 'Aufnahme' },
  { key: 'schnitt', label: 'Schnitt' },
  { key: 'live', label: 'Veröffentlicht' },
]

export interface Task {
  id: string
  title: string
  done: boolean
  status: ContentStatus
  platform: string
  priority: Priority
  project: string
  due: string // '' oder 'YYYY-MM-DD'
  notes: string
  createdAt: string
}

export interface NewTask {
  title: string
  status?: ContentStatus
  platform?: string
  priority?: Priority
  project?: string
  due?: string
  notes?: string
  done?: boolean
}

const STORAGE_KEY = 'finaz_tasks'

function today(): string {
  return new Date().toISOString().slice(0, 10)
}

// Robust gegen alte/teildefinierte Einträge (z. B. ohne status/platform).
function normalize(raw: unknown): Task {
  const t = (raw ?? {}) as Partial<Task>
  const status: ContentStatus = STATUSES.some((s) => s.key === t.status) ? (t.status as ContentStatus) : 'idee'
  return {
    id: String(t.id ?? Date.now().toString()),
    title: String(t.title ?? ''),
    done: t.done ?? status === 'live',
    status,
    platform: String(t.platform ?? ''),
    priority: t.priority === 'low' || t.priority === 'high' ? t.priority : 'normal',
    project: String(t.project ?? ''),
    due: String(t.due ?? ''),
    notes: String(t.notes ?? ''),
    createdAt: String(t.createdAt ?? today()),
  }
}

function loadFromStorage(): Task[] {
  try {
    const data = localStorage.getItem(STORAGE_KEY)
    if (!data) return sampleData()
    const arr = JSON.parse(data) as unknown[]
    return Array.isArray(arr) ? arr.map(normalize) : sampleData()
  } catch {
    return sampleData()
  }
}

function sampleData(): Task[] {
  const t = today()
  return [
    normalize({ id: '1', title: 'YouTube: „Mein Setup 2026" – Skript schreiben', status: 'skript', platform: 'YouTube', priority: 'high', project: 'YouTube', due: t }),
    normalize({ id: '2', title: '10 TikTok-Hook-Ideen sammeln', status: 'idee', platform: 'TikTok', priority: 'normal', project: 'Shorts' }),
    normalize({ id: '3', title: 'Newsletter #12 fertig schneiden', status: 'schnitt', platform: 'Newsletter', priority: 'normal' }),
    normalize({ id: '4', title: 'Reel „3 Tools, die ich liebe"', status: 'live', platform: 'Instagram', priority: 'low' }),
  ]
}

export const useTaskStore = defineStore('tasks', () => {
  const tasks = ref<Task[]>(loadFromStorage())

  function save() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks.value))
  }

  function addTask(input: NewTask) {
    const status: ContentStatus = input.status ?? 'idee'
    tasks.value.unshift({
      id: Date.now().toString(),
      title: input.title,
      done: input.done ?? status === 'live',
      status,
      platform: input.platform ?? '',
      priority: input.priority ?? 'normal',
      project: input.project ?? '',
      due: input.due ?? '',
      notes: input.notes ?? '',
      createdAt: today(),
    })
    save()
  }

  // Status entlang der Pipeline setzen; "live" = veröffentlicht (= done).
  function setStatus(id: string, status: ContentStatus) {
    const t = tasks.value.find((x) => x.id === id)
    if (t) {
      t.status = status
      t.done = status === 'live'
      save()
    }
  }

  function setDone(id: string, done: boolean) {
    const t = tasks.value.find((x) => x.id === id)
    if (t) {
      t.done = done
      if (done) t.status = 'live'
      else if (t.status === 'live') t.status = 'schnitt'
      save()
    }
  }

  function toggleTask(id: string) {
    const t = tasks.value.find((x) => x.id === id)
    if (t) setDone(id, !t.done)
  }

  function updateTask(updated: Task) {
    const i = tasks.value.findIndex((x) => x.id === updated.id)
    if (i !== -1) tasks.value[i] = updated
    save()
  }

  function deleteTask(id: string) {
    tasks.value = tasks.value.filter((x) => x.id !== id)
    save()
  }

  // Ersetzt alle Inhalte (für Wiederherstellen / Rückgängig).
  function setAll(list: Task[]) {
    tasks.value = list
    save()
  }

  const openCount = computed(() => tasks.value.filter((t) => !t.done).length)
  const doneCount = computed(() => tasks.value.filter((t) => t.done).length)
  const projects = computed(() => Array.from(new Set(tasks.value.map((t) => t.project).filter(Boolean))))
  const overdue = computed(() => {
    const d = today()
    return tasks.value.filter((x) => !x.done && x.due && x.due < d)
  })

  return { tasks, addTask, setStatus, setDone, toggleTask, updateTask, deleteTask, setAll, openCount, doneCount, projects, overdue }
})
