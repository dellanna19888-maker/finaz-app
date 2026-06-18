<template>
  <div class="page">
    <div class="page-header">
      <h1>🎓 KI Trainieren</h1>
      <p class="subtitle">Fine-Tuning mit deinen eigenen Daten</p>
    </div>

    <div class="layout">
      <div class="config-panel">
        <div class="card">
          <h3>1. Training konfigurieren</h3>

          <div class="form-group">
            <label>Job-Name</label>
            <input v-model="config.job_name" placeholder="z.B. Medizinische-Klassifikation-v1" />
          </div>

          <div class="form-group">
            <label>Aufgabe</label>
            <select v-model="config.task_type">
              <option value="text-classification">📝 Text-Klassifikation</option>
            </select>
          </div>

          <div class="form-group">
            <label>Basismodell</label>
            <select v-model="config.base_model">
              <option
                v-for="m in availableModels"
                :key="m.id"
                :value="m.id"
              >{{ m.name }} ({{ m.size }})</option>
            </select>
            <div class="form-hint">Empfohlen: DistilBERT ist schneller, BERT genauer</div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Epochen</label>
              <input v-model.number="config.num_epochs" type="number" min="1" max="20" />
            </div>
            <div class="form-group">
              <label>Batch-Größe</label>
              <input v-model.number="config.batch_size" type="number" min="2" max="64" />
            </div>
            <div class="form-group">
              <label>Lernrate</label>
              <input v-model="config.learning_rate" type="number" step="0.000001" />
            </div>
          </div>

          <div class="hf-section">
            <label style="display:flex;align-items:center;gap:0.5rem;text-transform:none;font-size:0.9rem;color:var(--text)">
              <input type="checkbox" v-model="config.push_to_hub" style="width:auto" />
              Modell auf Hugging Face Hub hochladen
            </label>
            <input
              v-if="config.push_to_hub"
              v-model="config.hub_model_id"
              placeholder="dein-username/modell-name"
              style="margin-top:0.5rem"
            />
          </div>
        </div>

        <div class="card" style="margin-top:1rem">
          <h3>2. Trainingsdaten hochladen</h3>

          <div
            class="drop-zone"
            :class="{ dragging }"
            @dragover.prevent="dragging = true"
            @dragleave="dragging = false"
            @drop.prevent="onDrop"
            @click="fileInput?.click()"
          >
            <div v-if="trainingFile">
              <div style="font-size:2rem">📊</div>
              <div class="file-name">{{ trainingFile.name }}</div>
              <div class="file-size">{{ (trainingFile.size / 1024).toFixed(1) }} KB</div>
            </div>
            <div v-else class="drop-placeholder">
              <div>📊</div>
              <p>JSON-Datei hierher ziehen</p>
              <p class="hint">Format: [{"text": "...", "label": "..."}]</p>
            </div>
          </div>

          <input ref="fileInput" type="file" accept=".json" style="display:none" @change="onFileChange" />

          <div class="data-example">
            <div class="example-title">Beispiel-Datenformat:</div>
            <pre class="code-block">{{ dataExample }}</pre>
            <button class="btn btn-secondary" @click="downloadExample" style="margin-top:0.5rem;font-size:0.82rem">
              ⬇ Beispiel herunterladen
            </button>
          </div>
        </div>

        <button
          class="btn btn-primary start-btn"
          @click="startTraining"
          :disabled="!canStart || starting"
        >
          {{ starting ? '⏳ Starte...' : '🚀 Training starten' }}
        </button>

        <div v-if="startError" class="error-msg">⚠️ {{ startError }}</div>
      </div>

      <div class="jobs-panel">
        <div class="jobs-header">
          <h3>Training-Jobs</h3>
          <button class="btn btn-secondary" @click="loadJobs" style="font-size:0.82rem">↻ Aktualisieren</button>
        </div>

        <div v-if="jobs.length === 0" class="empty-jobs">
          <div style="font-size:2rem;margin-bottom:0.5rem">📋</div>
          <p>Noch keine Training-Jobs</p>
        </div>

        <div v-for="job in jobs" :key="job.job_id" class="card job-card">
          <div class="job-header">
            <div>
              <div class="job-name">{{ job.job_name }}</div>
              <div class="job-meta">{{ job.task_type }} · {{ job.base_model }}</div>
            </div>
            <div class="job-status-col">
              <span class="badge" :class="statusBadge(job.status)">{{ statusLabel(job.status) }}</span>
              <button v-if="job.status !== 'running'" class="delete-btn" @click="deleteJob(job.job_id)">🗑</button>
            </div>
          </div>

          <div v-if="job.status === 'running' || job.status === 'queued'" class="job-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: job.progress + '%' }" />
            </div>
            <div class="progress-text">{{ job.progress.toFixed(0) }}% — {{ job.message }}</div>
          </div>

          <div v-if="job.status === 'completed'" class="job-done">
            ✅ {{ job.message }}
          </div>

          <div v-if="job.status === 'failed'" class="job-failed">
            ❌ {{ job.message }}
          </div>

          <div v-if="job.metrics" class="job-metrics">
            <span v-if="job.metrics.loss">Loss: {{ job.metrics.loss }}</span>
            <span v-if="job.metrics.epoch">Epoche: {{ job.metrics.epoch }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { api } from '../stores/api'

const config = ref({
  job_name: '',
  task_type: 'text-classification',
  base_model: 'distilbert-base-multilingual-cased',
  num_epochs: 3,
  batch_size: 8,
  learning_rate: 2e-5,
  push_to_hub: false,
  hub_model_id: '',
})

const availableModels = ref<any[]>([])
const trainingFile = ref<File | null>(null)
const jobs = ref<any[]>([])
const starting = ref(false)
const startError = ref('')
const dragging = ref(false)
const fileInput = ref<HTMLInputElement>()
let pollInterval: number | null = null

const canStart = computed(() =>
  config.value.job_name.trim() !== '' && trainingFile.value !== null
)

const dataExample = `[
  {"text": "Patient hat Fieber", "label": "Symptome"},
  {"text": "Nehmen Sie Ibuprofen", "label": "Medikamente"},
  {"text": "Blutdruck 140/90", "label": "Labor-Ergebnisse"}
]`

function statusBadge(status: string) {
  return {
    queued: 'badge-warning',
    running: 'badge-primary',
    completed: 'badge-success',
    failed: 'badge-danger',
  }[status] || 'badge-primary'
}

function statusLabel(status: string) {
  return {
    queued: '⏳ Wartend',
    running: '🔄 Läuft',
    completed: '✅ Fertig',
    failed: '❌ Fehler',
  }[status] || status
}

function onFileChange(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (f) trainingFile.value = f
}

function onDrop(e: DragEvent) {
  dragging.value = false
  const f = e.dataTransfer?.files[0]
  if (f) trainingFile.value = f
}

async function startTraining() {
  if (!canStart.value) return
  starting.value = true
  startError.value = ''
  try {
    const cfg: any = { ...config.value }
    if (!cfg.push_to_hub) delete cfg.hub_model_id
    await api.training.start(cfg, trainingFile.value!)
    await loadJobs()
    trainingFile.value = null
    config.value.job_name = ''
  } catch (e: any) {
    startError.value = e.message
  } finally {
    starting.value = false
  }
}

async function loadJobs() {
  try {
    const res = await api.training.jobs()
    jobs.value = res.jobs.sort((a: any, b: any) => b.created_at - a.created_at)
  } catch {}
}

async function deleteJob(jobId: string) {
  await api.training.deleteJob(jobId)
  await loadJobs()
}

function downloadExample() {
  const blob = new Blob([dataExample], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'training-beispiel.json'
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(async () => {
  try {
    const res = await api.training.models()
    availableModels.value = res.models['text-classification'] || []
  } catch {
    availableModels.value = [
      { id: 'distilbert-base-multilingual-cased', name: 'DistilBERT Multilingual (schneller)', size: '280MB' },
      { id: 'bert-base-multilingual-cased', name: 'BERT Multilingual', size: '680MB' },
    ]
  }
  await loadJobs()
  pollInterval = window.setInterval(loadJobs, 5000)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>

<style scoped>
.page { padding: 2rem; max-width: 1200px; }
.page-header { margin-bottom: 2rem; }
.page-header h1 { font-size: 1.75rem; font-weight: 800; }
.subtitle { color: var(--text-muted); margin-top: 0.3rem; }

.layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  align-items: flex-start;
}

@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; }
}

.config-panel h3, .jobs-header h3 { font-size: 1rem; margin-bottom: 1rem; }

.form-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.75rem; }

.form-hint { font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem; }

.hf-section { margin-top: 0.5rem; }

.drop-zone {
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.drop-zone:hover, .drop-zone.dragging {
  border-color: var(--primary);
  background: rgba(99,102,241,0.05);
}

.file-name { font-weight: 600; margin-top: 0.3rem; }
.file-size { font-size: 0.8rem; color: var(--text-muted); }
.drop-placeholder { font-size: 1.5rem; }
.drop-placeholder p { font-size: 0.9rem; color: var(--text-muted); margin-top: 0.3rem; }
.hint { font-size: 0.78rem; }

.data-example { margin-top: 0.5rem; }
.example-title { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.3rem; }

.code-block {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.75rem;
  font-size: 0.78rem;
  color: #34d399;
  overflow-x: auto;
  white-space: pre;
}

.start-btn { width: 100%; margin-top: 1rem; justify-content: center; }

.error-msg {
  margin-top: 0.75rem;
  padding: 0.5rem 0.75rem;
  background: rgba(239,68,68,0.1);
  border-radius: 8px;
  color: #f87171;
  font-size: 0.85rem;
}

.jobs-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }

.empty-jobs {
  text-align: center;
  color: var(--text-muted);
  padding: 3rem;
  background: var(--bg-card);
  border: 1px dashed var(--border);
  border-radius: var(--radius);
}

.job-card { margin-bottom: 0.75rem; }

.job-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem; }
.job-name { font-weight: 600; }
.job-meta { font-size: 0.78rem; color: var(--text-muted); margin-top: 0.2rem; }

.job-status-col { display: flex; align-items: center; gap: 0.5rem; }

.delete-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  opacity: 0.6;
  transition: opacity 0.2s;
}
.delete-btn:hover { opacity: 1; }

.job-progress { }
.progress-text { font-size: 0.8rem; color: var(--text-muted); margin-top: 0.4rem; }

.job-done { font-size: 0.85rem; color: #34d399; }
.job-failed { font-size: 0.85rem; color: #f87171; }

.job-metrics {
  display: flex;
  gap: 1rem;
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--border);
}
</style>
