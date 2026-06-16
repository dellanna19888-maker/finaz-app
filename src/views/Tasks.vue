<template>
  <div class="ai-page">
    <div class="page-header">
      <h1>📋 Aufgaben</h1>
      <p class="sub">
        To-dos &amp; Projekte – per Hand oder über die 🧠 Zentrale.
        {{ store.openCount }} offen · {{ store.doneCount }} erledigt<span v-if="store.overdue.length"> · <span class="ov">{{ store.overdue.length }} überfällig</span></span>.
      </p>
    </div>

    <div class="card2">
      <div class="add-row">
        <input v-model="title" class="instruction" placeholder="Neue Aufgabe … (Enter)" @keyup.enter="add" />
        <select v-model="priority" class="sel">
          <option value="low">niedrig</option>
          <option value="normal">normal</option>
          <option value="high">hoch</option>
        </select>
        <input v-model="project" class="sel proj" placeholder="Projekt (optional)" />
        <input v-model="due" type="date" class="sel" />
        <button class="btn" :disabled="!title.trim()" @click="add">Hinzufügen</button>
      </div>
    </div>

    <div class="filters">
      <button class="chip" :class="{ on: filter === 'open' }" @click="filter = 'open'">Offen</button>
      <button class="chip" :class="{ on: filter === 'done' }" @click="filter = 'done'">Erledigt</button>
      <button class="chip" :class="{ on: filter === 'all' }" @click="filter = 'all'">Alle</button>
      <select v-model="projFilter" class="sel">
        <option value="">Alle Projekte</option>
        <option v-for="p in store.projects" :key="p" :value="p">{{ p }}</option>
      </select>
    </div>

    <ul class="tasks">
      <li v-for="t in shown" :key="t.id" class="task" :class="{ done: t.done }">
        <input type="checkbox" :checked="t.done" @change="store.toggleTask(t.id)" />
        <div class="task-main">
          <span class="task-title">{{ t.title }}</span>
          <span class="meta">
            <span class="prio" :class="'p-' + t.priority">{{ prioLabel(t.priority) }}</span>
            <span v-if="t.project" class="tag">{{ t.project }}</span>
            <span v-if="t.due" class="tag" :class="{ over: isOverdue(t) }">📅 {{ t.due }}</span>
          </span>
        </div>
        <button class="btn-ghost xs" title="Löschen" @click="store.deleteTask(t.id)">✕</button>
      </li>
      <li v-if="!shown.length" class="muted empty-li">Keine Aufgaben hier.</li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useTaskStore, type Priority, type Task } from '../stores/tasks'

const store = useTaskStore()

const title = ref('')
const priority = ref<Priority>('normal')
const project = ref('')
const due = ref('')

const filter = ref<'open' | 'done' | 'all'>('open')
const projFilter = ref('')

const shown = computed(() =>
  store.tasks.filter((t) => {
    if (filter.value === 'open' && t.done) return false
    if (filter.value === 'done' && !t.done) return false
    if (projFilter.value && t.project !== projFilter.value) return false
    return true
  }),
)

function add() {
  if (!title.value.trim()) return
  store.addTask({ title: title.value.trim(), priority: priority.value, project: project.value.trim(), due: due.value })
  title.value = ''
  project.value = ''
  due.value = ''
  priority.value = 'normal'
}
function prioLabel(p: Priority) {
  return p === 'high' ? 'hoch' : p === 'low' ? 'niedrig' : 'normal'
}
function isOverdue(t: Task) {
  return !t.done && !!t.due && t.due < new Date().toISOString().slice(0, 10)
}
</script>

<style scoped>
.add-row { display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; }
.add-row .instruction { flex: 1; min-width: 200px; }
.proj { min-width: 140px; }
.filters { display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; margin: 1rem 0; }
.chip { padding: 0.4rem 0.8rem; border-radius: 999px; border: 1px solid #334155; background: #1e293b; color: #cbd5e1; cursor: pointer; font-size: 0.82rem; }
.chip.on { border-color: #60a5fa; color: #fff; background: rgba(96, 165, 250, 0.15); }
.ov { color: #f87171; }

.tasks { list-style: none; display: flex; flex-direction: column; gap: 0.5rem; padding: 0; }
.task { display: flex; align-items: center; gap: 0.75rem; padding: 0.7rem 0.9rem; background: #1e293b; border: 1px solid #334155; border-radius: 10px; }
.task.done { opacity: 0.6; }
.task.done .task-title { text-decoration: line-through; }
.task input[type='checkbox'] { width: 18px; height: 18px; flex-shrink: 0; cursor: pointer; }
.task-main { flex: 1; display: flex; flex-direction: column; gap: 0.25rem; min-width: 0; }
.task-title { color: #e2e8f0; word-break: break-word; }
.meta { display: flex; flex-wrap: wrap; gap: 0.4rem; align-items: center; }
.prio { font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 999px; }
.p-high { background: #7f1d1d; color: #fecaca; }
.p-normal { background: #334155; color: #cbd5e1; }
.p-low { background: #0f172a; color: #94a3b8; border: 1px solid #334155; }
.tag { font-size: 0.72rem; color: #94a3b8; background: #0f172a; padding: 0.1rem 0.45rem; border-radius: 6px; border: 1px solid #334155; }
.tag.over { color: #fecaca; border-color: #7f1d1d; }
.btn-ghost.xs { padding: 0.25rem 0.55rem; font-size: 0.9rem; line-height: 1; }
.empty-li { padding: 1rem; text-align: center; }
</style>
