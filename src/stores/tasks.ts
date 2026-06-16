import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export type Priority = 'low' | 'normal' | 'high'

export interface Task {
  id: string
  title: string
  done: boolean
  priority: Priority
  project: string
  due: string // '' oder 'YYYY-MM-DD'
  notes: string
  createdAt: string
}

export interface NewTask {
  title: string
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

function loadFromStorage(): Task[] {
  try {
    const data = localStorage.getItem(STORAGE_KEY)
    return data ? (JSON.parse(data) as Task[]) : sampleData()
  } catch {
    return sampleData()
  }
}

function sampleData(): Task[] {
  const t = today()
  return [
    { id: '1', title: 'Angebot für Kunde Müller erstellen', done: false, priority: 'high', project: 'Vertrieb', due: t, notes: '', createdAt: t },
    { id: '2', title: 'Wissensartikel „Onboarding" schreiben', done: false, priority: 'normal', project: 'Wissen', due: '', notes: '', createdAt: t },
    { id: '3', title: 'Support-Anfragen vom Vormittag beantworten', done: true, priority: 'normal', project: 'Support', due: '', notes: '', createdAt: t },
  ]
}

export const useTaskStore = defineStore('tasks', () => {
  const tasks = ref<Task[]>(loadFromStorage())

  function save() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks.value))
  }

  function addTask(input: NewTask) {
    tasks.value.unshift({
      id: Date.now().toString(),
      title: input.title,
      done: input.done ?? false,
      priority: input.priority ?? 'normal',
      project: input.project ?? '',
      due: input.due ?? '',
      notes: input.notes ?? '',
      createdAt: today(),
    })
    save()
  }

  function setDone(id: string, done: boolean) {
    const t = tasks.value.find((x) => x.id === id)
    if (t) {
      t.done = done
      save()
    }
  }

  function toggleTask(id: string) {
    const t = tasks.value.find((x) => x.id === id)
    if (t) {
      t.done = !t.done
      save()
    }
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

  // Ersetzt alle Aufgaben (für Wiederherstellen / Rückgängig).
  function setAll(list: Task[]) {
    tasks.value = list
    save()
  }

  const openCount = computed(() => tasks.value.filter((t) => !t.done).length)
  const doneCount = computed(() => tasks.value.filter((t) => t.done).length)
  const projects = computed(() => Array.from(new Set(tasks.value.map((t) => t.project).filter(Boolean))))
  const overdue = computed(() => {
    const t = today()
    return tasks.value.filter((x) => !x.done && x.due && x.due < t)
  })

  return { tasks, addTask, setDone, toggleTask, updateTask, deleteTask, setAll, openCount, doneCount, projects, overdue }
})
