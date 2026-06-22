<template>
  <div class="page">
    <div class="page-header">
      <h1>🎬 Content-Planer</h1>
      <p class="sub">Deine Content-Pipeline — von der Idee bis zur Veröffentlichung.</p>
    </div>

    <!-- Add task -->
    <div class="card">
      <h2>➕ Neue Idee / Aufgabe</h2>
      <div style="display:flex;gap:0.5rem;flex-wrap:wrap">
        <input v-model="newTitle" class="inp" style="flex:1;min-width:180px" placeholder="Titel / Idee …" @keydown.enter="addTask" />
        <select v-model="newPlatform" class="sel" style="width:130px">
          <option value="">Plattform …</option>
          <option>YouTube</option><option>TikTok</option><option>Instagram</option>
          <option>LinkedIn</option><option>Newsletter</option><option>Podcast</option>
        </select>
        <button class="btn btn-primary" :disabled="!newTitle.trim()" @click="addTask">Hinzufügen</button>
      </div>
    </div>

    <!-- Pipeline view -->
    <div class="card">
      <h2>🔄 Pipeline-Übersicht</h2>
      <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.75rem">
        <button v-for="s in STATUSES" :key="s.key"
          class="btn btn-sm" :class="activeFilter === s.key ? 'btn-primary' : 'btn-ghost'"
          @click="activeFilter = activeFilter === s.key ? '' : s.key">
          {{ s.label }}
          <span style="background:rgba(255,255,255,0.15);border-radius:999px;padding:0.1rem 0.4rem;font-size:0.7rem;margin-left:0.2rem">
            {{ countByStatus(s.key) }}
          </span>
        </button>
        <button class="btn btn-sm" :class="activeFilter === '' ? 'btn-primary' : 'btn-ghost'" @click="activeFilter = ''">Alle ({{ tasks.tasks.length }})</button>
      </div>
    </div>

    <!-- Empty -->
    <div v-if="!visibleTasks.length" class="card" style="text-align:center;padding:2rem">
      <p class="muted">Keine Aufgaben — füge oben deine erste Content-Idee hinzu!</p>
    </div>

    <!-- Task list -->
    <div class="task-list">
      <div v-for="t in visibleTasks" :key="t.id" class="task-item" :class="{ done: t.done }">
        <input type="checkbox" class="task-check" :checked="t.done" @change="tasks.toggleTask(t.id)" />
        <div class="task-body">
          <div class="task-title">{{ t.title }}</div>
          <div class="task-meta">
            <span class="tag" :class="statusTagClass(t.status)">{{ statusLabel(t.status) }}</span>
            <span v-if="t.platform" class="tag">{{ t.platform }}</span>
            <span v-if="t.priority === 'high'" class="tag urgent">🔴 Prio</span>
            <span v-if="t.due" class="muted">📅 {{ t.due }}</span>
          </div>
          <div v-if="t.notes" class="muted" style="margin-top:0.25rem;font-size:0.8rem">{{ t.notes }}</div>
        </div>
        <div style="display:flex;gap:0.35rem;flex-shrink:0;align-items:center">
          <!-- Pipeline advance -->
          <button v-if="nextStatus(t.status)" class="btn btn-ghost btn-sm" style="font-size:0.75rem" @click="tasks.setStatus(t.id, nextStatus(t.status)!)">
            → {{ nextStatusLabel(t.status) }}
          </button>
          <button class="btn btn-ghost btn-sm" style="color:var(--red);border-color:transparent" @click="tasks.deleteTask(t.id)">✕</button>
        </div>
      </div>
    </div>

    <!-- Stats row -->
    <div class="card" style="margin-top:1rem">
      <div style="display:flex;gap:1.5rem;flex-wrap:wrap">
        <div style="text-align:center">
          <div style="font-size:1.5rem;font-weight:700;color:var(--accent2)">{{ tasks.tasks.length }}</div>
          <div class="muted">Gesamt</div>
        </div>
        <div style="text-align:center">
          <div style="font-size:1.5rem;font-weight:700;color:var(--amber)">{{ tasks.openCount }}</div>
          <div class="muted">In Arbeit</div>
        </div>
        <div style="text-align:center">
          <div style="font-size:1.5rem;font-weight:700;color:var(--green)">{{ tasks.doneCount }}</div>
          <div class="muted">Veröffentlicht</div>
        </div>
        <div v-if="tasks.overdue.length" style="text-align:center">
          <div style="font-size:1.5rem;font-weight:700;color:var(--red)">{{ tasks.overdue.length }}</div>
          <div class="muted">Überfällig</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useTaskStore, STATUSES, type ContentStatus } from '../stores/tasks'

const tasks = useTaskStore()
const newTitle = ref('')
const newPlatform = ref('')
const activeFilter = ref<ContentStatus | ''>('')

const visibleTasks = computed(() => {
  if (!activeFilter.value) return tasks.tasks
  return tasks.tasks.filter(t => t.status === activeFilter.value)
})

function countByStatus(s: ContentStatus) { return tasks.tasks.filter(t => t.status === s).length }
function statusLabel(k: string) { return STATUSES.find(s => s.key === k)?.label ?? k }
function statusTagClass(s: string) {
  const m: Record<string, string> = { live: 'post', idee: '', skript: 'reel', aufnahme: 'reel', schnitt: 'urgent' }
  return m[s] || ''
}

const ORDER = STATUSES.map(s => s.key)
function nextStatus(current: ContentStatus): ContentStatus | null {
  const i = ORDER.indexOf(current); return i < ORDER.length - 1 ? ORDER[i + 1] : null
}
function nextStatusLabel(current: ContentStatus): string {
  const n = nextStatus(current); return n ? statusLabel(n) : ''
}

function addTask() {
  const title = newTitle.value.trim(); if (!title) return
  tasks.addTask({ title, platform: newPlatform.value, status: 'idee', priority: 'normal' })
  newTitle.value = ''; newPlatform.value = ''
}
</script>
