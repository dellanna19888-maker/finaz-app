<template>
  <div class="page">
    <div class="page-header">
      <h1>📝 Text-Klassifikation</h1>
      <p class="subtitle">Texte automatisch kategorisieren und Stimmung erkennen</p>
    </div>

    <div class="layout">
      <div class="input-panel card">
        <h3>Text eingeben</h3>

        <div class="form-group">
          <label>Bereich</label>
          <select v-model="domain" @change="loadLabels">
            <option value="general">🤖 Allgemein</option>
            <option value="health">🏥 Gesundheit</option>
            <option value="ecommerce">🛍️ E-Commerce</option>
            <option value="education">📚 Bildung</option>
          </select>
        </div>

        <div class="form-group">
          <label>Text</label>
          <textarea v-model="text" rows="5" placeholder="Gib deinen Text hier ein..." />
        </div>

        <div class="form-group">
          <label>Eigene Kategorien (optional, kommagetrennt)</label>
          <input v-model="customLabelsInput" placeholder="z.B. Positiv, Negativ, Neutral" />
        </div>

        <div class="form-group">
          <label style="display:flex;align-items:center;gap:0.5rem;text-transform:none;font-size:0.9rem;">
            <input type="checkbox" v-model="multiLabel" style="width:auto" />
            Mehrere Kategorien gleichzeitig möglich
          </label>
        </div>

        <div class="action-row">
          <button class="btn btn-primary" @click="classify" :disabled="loading || !text.trim()">
            {{ loading ? '⏳ Analysiere...' : '🔍 Klassifizieren' }}
          </button>
          <button class="btn btn-secondary" @click="analyzeSentiment" :disabled="loading || !text.trim()">
            😊 Stimmung
          </button>
        </div>

        <div v-if="error" class="error-msg">⚠️ {{ error }}</div>

        <div class="current-labels" v-if="currentLabels.length">
          <div class="label-title">Verfügbare Kategorien:</div>
          <div class="label-chips">
            <span class="badge badge-primary" v-for="l in currentLabels" :key="l">{{ l }}</span>
          </div>
        </div>
      </div>

      <div class="results-panel">
        <div v-if="!result && !sentiment" class="empty-result">
          <div style="font-size:3rem;margin-bottom:1rem">📊</div>
          <p>Gib Text ein und klicke auf "Klassifizieren"</p>
        </div>

        <div v-if="result" class="card result-card">
          <h3>Klassifikations-Ergebnis</h3>
          <div class="top-result">
            <span class="top-label">{{ result.top_label }}</span>
            <span class="top-score">{{ (result.results[0]?.score * 100).toFixed(1) }}%</span>
          </div>
          <div class="result-bars">
            <div v-for="r in result.results.slice(0, 6)" :key="r.label" class="result-bar-row">
              <div class="result-label">{{ r.label }}</div>
              <div class="bar-track">
                <div class="bar-fill" :style="{ width: (r.score * 100) + '%' }" />
              </div>
              <div class="result-score">{{ (r.score * 100).toFixed(1) }}%</div>
            </div>
          </div>
        </div>

        <div v-if="sentiment" class="card sentiment-card">
          <h3>Stimmungsanalyse</h3>
          <div class="sentiment-display">
            <span class="sentiment-emoji">{{ sentimentEmoji }}</span>
            <div>
              <div class="sentiment-label">{{ sentiment.sentiment }}</div>
              <div class="sentiment-score">Konfidenz: {{ (sentiment.score * 100).toFixed(1) }}%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { api } from '../stores/api'

const text = ref('')
const domain = ref('general')
const customLabelsInput = ref('')
const multiLabel = ref(false)
const loading = ref(false)
const error = ref('')
const result = ref<any>(null)
const sentiment = ref<any>(null)
const currentLabels = ref<string[]>([])

const sentimentEmoji = computed(() => {
  if (!sentiment.value) return ''
  const s = sentiment.value.sentiment.toLowerCase()
  if (s.includes('positive') || s.includes('positiv')) return '😊'
  if (s.includes('negative') || s.includes('negativ')) return '😟'
  return '😐'
})

async function loadLabels() {
  try {
    const res = await api.text.labels(domain.value)
    currentLabels.value = res.labels
  } catch {}
}

async function classify() {
  if (!text.value.trim()) return
  loading.value = true
  error.value = ''
  result.value = null
  sentiment.value = null
  try {
    const labels = customLabelsInput.value
      ? customLabelsInput.value.split(',').map(l => l.trim()).filter(Boolean)
      : undefined
    result.value = await api.text.classify(text.value, labels, domain.value, multiLabel.value)
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function analyzeSentiment() {
  if (!text.value.trim()) return
  loading.value = true
  error.value = ''
  sentiment.value = null
  result.value = null
  try {
    sentiment.value = await api.text.sentiment(text.value)
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(loadLabels)
</script>

<style scoped>
.page { padding: 2rem; max-width: 1100px; }
.page-header { margin-bottom: 2rem; }
.page-header h1 { font-size: 1.75rem; font-weight: 800; }
.subtitle { color: var(--text-muted); margin-top: 0.3rem; }

.layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 800px) {
  .layout { grid-template-columns: 1fr; }
}

.input-panel h3, .result-card h3, .sentiment-card h3 {
  margin-bottom: 1rem;
  font-size: 1rem;
}

.action-row { display: flex; gap: 0.75rem; flex-wrap: wrap; }

.error-msg {
  margin-top: 0.75rem;
  padding: 0.5rem 0.75rem;
  background: rgba(239,68,68,0.1);
  border-radius: 8px;
  color: #f87171;
  font-size: 0.85rem;
}

.current-labels { margin-top: 1rem; }
.label-title { font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.4rem; text-transform: uppercase; letter-spacing: 0.05em; }
.label-chips { display: flex; flex-wrap: wrap; gap: 0.3rem; }

.empty-result {
  text-align: center;
  color: var(--text-muted);
  padding: 4rem 2rem;
  background: var(--bg-card);
  border: 1px dashed var(--border);
  border-radius: var(--radius);
}

.top-result {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(99,102,241,0.1);
  border: 1px solid var(--primary);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
}

.top-label { font-weight: 700; font-size: 1.1rem; color: var(--primary-light); }
.top-score { font-size: 1.3rem; font-weight: 800; color: var(--secondary); }

.result-bars { display: flex; flex-direction: column; gap: 0.6rem; }

.result-bar-row {
  display: grid;
  grid-template-columns: 150px 1fr 50px;
  align-items: center;
  gap: 0.5rem;
}

.result-label { font-size: 0.85rem; truncate: ellipsis; white-space: nowrap; overflow: hidden; }
.bar-track { background: var(--border); border-radius: 4px; height: 8px; overflow: hidden; }
.bar-fill { height: 100%; background: linear-gradient(90deg, var(--primary), var(--secondary)); border-radius: 4px; transition: width 0.5s; }
.result-score { font-size: 0.8rem; color: var(--text-muted); text-align: right; }

.sentiment-display {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--bg);
  border-radius: 8px;
}

.sentiment-emoji { font-size: 3rem; }
.sentiment-label { font-size: 1.25rem; font-weight: 700; }
.sentiment-score { font-size: 0.85rem; color: var(--text-muted); }
</style>
