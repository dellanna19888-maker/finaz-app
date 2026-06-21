<template>
  <div class="ai-page">
    <div class="page-header">
      <h1>🎬 Content-Plan</h1>
      <p class="sub">
        Idee → Skript → Aufnahme → Schnitt → Veröffentlicht. Plane Inhalte per Hand oder über die 🧠 Zentrale.
        {{ store.openCount }} in Arbeit · {{ store.doneCount }} veröffentlicht<span v-if="store.overdue.length"> · <span class="ov">{{ store.overdue.length }} überfällig</span></span>.
      </p>
    </div>

    <div class="card2">
      <div class="add-row">
        <input v-model="title" class="instruction" placeholder="Neue Idee / Inhalt … (Enter)" @keyup.enter="add" />
        <input v-model="platform" class="sel plat" placeholder="Plattform" list="platforms" />
        <datalist id="platforms">
          <option>YouTube</option><option>TikTok</option><option>Instagram</option><option>Reels</option>
          <option>Shorts</option><option>Podcast</option><option>Newsletter</option><option>Blog</option>
          <option>X</option><option>LinkedIn</option>
        </datalist>
        <select v-model="status" class="sel">
          <option v-for="s in STATUSES" :key="s.key" :value="s.key">{{ s.label }}</option>
        </select>
        <select v-model="priority" class="sel">
          <option value="low">niedrig</option><option value="normal">normal</option><option value="high">hoch</option>
        </select>
        <input v-model="due" type="date" class="sel" />
        <button class="btn" :disabled="!title.trim()" @click="add">Hinzufügen</button>
      </div>
    </div>

    <div class="filters">
      <button class="chip" :class="{ on: statusFilter === 'all' }" @click="statusFilter = 'all'">Alle</button>
      <button v-for="s in STATUSES" :key="s.key" class="chip" :class="{ on: statusFilter === s.key }" @click="statusFilter = s.key">{{ s.label }}</button>
      <select v-model="projFilter" class="sel">
        <option value="">Alle Projekte</option>
        <option v-for="p in store.projects" :key="p" :value="p">{{ p }}</option>
      </select>
    </div>

    <ul class="tasks">
      <li v-for="t in shown" :key="t.id" class="task" :class="'st-' + t.status">
        <select class="status-sel" :value="t.status" @change="onStatus(t.id, $event)" title="Status">
          <option v-for="s in STATUSES" :key="s.key" :value="s.key">{{ s.label }}</option>
        </select>
        <div class="task-main">
          <span class="task-title" :class="{ live: t.status === 'live' }">{{ t.title }}</span>
          <span class="meta">
            <span v-if="t.platform" class="tag plat-tag">{{ t.platform }}</span>
            <span class="prio" :class="'p-' + t.priority">{{ prioLabel(t.priority) }}</span>
            <span v-if="t.project" class="tag">{{ t.project }}</span>
            <span v-if="t.due" class="tag" :class="{ over: isOverdue(t) }">📅 {{ t.due }}</span>
          </span>
        </div>
        <button class="btn-ghost xs" title="Löschen" :aria-label="`Inhalt „${t.title}“ löschen`" @click="store.deleteTask(t.id)">✕</button>
      </li>
      <li v-if="!shown.length" class="muted empty-li">Nichts in diesem Status.</li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useTaskStore, STATUSES, type Priority, type ContentStatus, type Task } from '../stores/tasks'

const store = useTaskStore()

const title = ref('')
const platform = ref('')
const status = ref<ContentStatus>('idee')
const priority = ref<Priority>('normal')
const due = ref('')

const statusFilter = ref<ContentStatus | 'all'>('all')
const projFilter = ref('')

const shown = computed(() =>
  store.tasks.filter((t) => {
    if (statusFilter.value !== 'all' && t.status !== statusFilter.value) return false
    if (projFilter.value && t.project !== projFilter.value) return false
    return true
  }),
)

function add() {
  if (!title.value.trim()) return
  store.addTask({ title: title.value.trim(), platform: platform.value.trim(), status: status.value, priority: priority.value, due: due.value })
  title.value = ''
  platform.value = ''
  due.value = ''
  status.value = 'idee'
  priority.value = 'normal'
}
function onStatus(id: string, e: Event) {
  store.setStatus(id, (e.target as HTMLSelectElement).value as ContentStatus)
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
.add-row .instruction { flex: 1; min-width: 180px; }
.plat { min-width: 120px; }
.filters { display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; margin: 1rem 0; }
.chip { padding: 0.4rem 0.8rem; border-radius: 999px; border: 1px solid #334155; background: #1e293b; color: #cbd5e1; cursor: pointer; font-size: 0.82rem; }
.chip.on { border-color: #60a5fa; color: #fff; background: rgba(96, 165, 250, 0.15); }
.ov { color: #f87171; }

.tasks { list-style: none; display: flex; flex-direction: column; gap: 0.5rem; padding: 0; }
.task { display: flex; align-items: center; gap: 0.75rem; padding: 0.6rem 0.8rem; background: #1e293b; border: 1px solid #334155; border-left: 3px solid #475569; border-radius: 10px; }
.task.st-idee { border-left-color: #64748b; }
.task.st-skript { border-left-color: #f59e0b; }
.task.st-aufnahme { border-left-color: #a78bfa; }
.task.st-schnitt { border-left-color: #38bdf8; }
.task.st-live { border-left-color: #34d399; }
.status-sel { background: #0f172a; color: #e2e8f0; border: 1px solid #334155; border-radius: 8px; padding: 0.35rem 0.4rem; font-size: 0.8rem; flex-shrink: 0; cursor: pointer; }
.task-main { flex: 1; display: flex; flex-direction: column; gap: 0.25rem; min-width: 0; }
.task-title { color: #e2e8f0; word-break: break-word; }
.task-title.live { color: #94a3b8; text-decoration: line-through; }
.meta { display: flex; flex-wrap: wrap; gap: 0.4rem; align-items: center; }
.prio { font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 999px; }
.p-high { background: #7f1d1d; color: #fecaca; }
.p-normal { background: #334155; color: #cbd5e1; }
.p-low { background: #0f172a; color: #94a3b8; border: 1px solid #334155; }
.tag { font-size: 0.72rem; color: #94a3b8; background: #0f172a; padding: 0.1rem 0.45rem; border-radius: 6px; border: 1px solid #334155; }
.plat-tag { color: #93c5fd; border-color: #1e40af; }
.tag.over { color: #fecaca; border-color: #7f1d1d; }
.btn-ghost.xs { padding: 0.25rem 0.55rem; font-size: 0.9rem; line-height: 1; }
.empty-li { padding: 1rem; text-align: center; }
</style>
