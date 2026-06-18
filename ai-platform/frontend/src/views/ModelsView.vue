<template>
  <div class="page">
    <div class="page-header">
      <h1>🗄️ Meine Modelle</h1>
      <p class="subtitle">Vortrainierte und eigene trainierte Modelle</p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="loading-dots">Lade Modelle</div>
    </div>

    <div v-else>
      <section v-if="models.custom.length > 0">
        <h2 class="section-title">🎓 Eigene Modelle ({{ models.custom.length }})</h2>
        <div class="models-grid">
          <div v-for="m in models.custom" :key="m.model_id" class="card model-card custom-model">
            <div class="model-icon">🎓</div>
            <div class="model-info">
              <div class="model-name">{{ m.name }}</div>
              <div class="model-task">{{ m.task }}</div>
              <div class="model-source">
                <span class="badge badge-success">Lokal trainiert</span>
              </div>
              <div v-if="m.labels" class="model-labels">
                <span class="badge badge-primary" v-for="l in m.labels.slice(0, 4)" :key="l">{{ l }}</span>
                <span v-if="m.labels.length > 4" class="badge badge-primary">+{{ m.labels.length - 4 }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section>
        <h2 class="section-title">🤗 Vortrainierte Modelle ({{ models.pretrained.length }})</h2>
        <div class="models-grid">
          <div v-for="m in models.pretrained" :key="m.model_id" class="card model-card">
            <div class="model-icon">{{ taskIcon(m.task) }}</div>
            <div class="model-info">
              <div class="model-name">{{ m.name }}</div>
              <div class="model-id">{{ m.model_id }}</div>
              <div class="model-task-label">
                <span class="badge badge-primary">{{ taskLabel(m.task) }}</span>
              </div>
              <a
                :href="`https://huggingface.co/${m.model_id}`"
                target="_blank"
                class="hf-link"
              >Auf Hugging Face ansehen ↗</a>
            </div>
          </div>
        </div>
      </section>

      <div class="info-card card">
        <h3>💡 Eigenes Modell trainieren</h3>
        <p>Gehe zu <RouterLink to="/training">KI Trainieren</RouterLink>, um ein Modell mit deinen eigenen Daten zu trainieren. Das Modell erscheint dann hier unter "Eigene Modelle".</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '../stores/api'

const loading = ref(true)
const models = ref<{ pretrained: any[]; custom: any[]; total: number }>({
  pretrained: [],
  custom: [],
  total: 0,
})

function taskIcon(task: string) {
  const icons: Record<string, string> = {
    'text-classification': '📝',
    'image-classification': '🖼️',
    'summarization': '📋',
    'question-answering': '❓',
    'text-generation': '💬',
  }
  return icons[task] || '🤖'
}

function taskLabel(task: string) {
  const labels: Record<string, string> = {
    'text-classification': 'Text-Klassifikation',
    'image-classification': 'Bild-Erkennung',
    'summarization': 'Zusammenfassung',
    'question-answering': 'Frage & Antwort',
    'text-generation': 'Text-Generierung',
  }
  return labels[task] || task
}

onMounted(async () => {
  try {
    models.value = await api.models.list()
  } catch {}
  loading.value = false
})
</script>

<style scoped>
.page { padding: 2rem; max-width: 1100px; }
.page-header { margin-bottom: 2rem; }
.page-header h1 { font-size: 1.75rem; font-weight: 800; }
.subtitle { color: var(--text-muted); margin-top: 0.3rem; }

.loading-state { text-align: center; padding: 4rem; color: var(--text-muted); font-size: 1.1rem; }

.section-title {
  font-size: 0.9rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 1rem;
  margin-top: 2rem;
}

.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.model-card {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.custom-model {
  border-color: rgba(16,185,129,0.3);
  background: rgba(16,185,129,0.03);
}

.model-icon { font-size: 2rem; flex-shrink: 0; }

.model-name { font-weight: 600; margin-bottom: 0.2rem; }
.model-id { font-size: 0.75rem; color: var(--text-muted); font-family: monospace; margin-bottom: 0.5rem; word-break: break-all; }
.model-task { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.5rem; }
.model-task-label { margin-bottom: 0.5rem; }

.model-source, .model-labels {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  margin-bottom: 0.3rem;
}

.hf-link {
  font-size: 0.78rem;
  color: var(--primary-light);
  margin-top: 0.3rem;
  display: inline-block;
}

.info-card {
  margin-top: 2rem;
}

.info-card h3 { margin-bottom: 0.5rem; }
.info-card p { color: var(--text-muted); font-size: 0.9rem; }
.info-card a { color: var(--primary-light); }
</style>
