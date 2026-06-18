<template>
  <div class="page">
    <div class="page-header">
      <h1>🖼️ Bild-Erkennung</h1>
      <p class="subtitle">Bilder mit KI analysieren und klassifizieren</p>
    </div>

    <div class="layout">
      <div class="upload-panel card">
        <h3>Bild hochladen</h3>

        <div
          class="drop-zone"
          :class="{ dragging, 'has-image': previewUrl }"
          @dragover.prevent="dragging = true"
          @dragleave="dragging = false"
          @drop.prevent="onDrop"
          @click="fileInput?.click()"
        >
          <img v-if="previewUrl" :src="previewUrl" class="preview-img" />
          <div v-else class="drop-placeholder">
            <div class="drop-icon">🖼️</div>
            <p>Bild hierher ziehen oder klicken</p>
            <p class="hint">JPG, PNG, WEBP bis 10MB</p>
          </div>
        </div>

        <input ref="fileInput" type="file" accept="image/*" style="display:none" @change="onFileChange" />

        <div class="form-group" style="margin-top:1rem">
          <label>Bereich</label>
          <select v-model="domain">
            <option value="general">🤖 Allgemein (ImageNet)</option>
            <option value="health">🏥 Gesundheit / Medizin</option>
            <option value="ecommerce">🛍️ E-Commerce / Produkte</option>
            <option value="education">📚 Bildung / Diagramme</option>
          </select>
        </div>

        <div class="form-group">
          <label>Eigene Kategorien (optional, kommagetrennt)</label>
          <input v-model="customLabels" placeholder="z.B. Katze, Hund, Vogel" />
        </div>

        <button class="btn btn-primary" @click="classify" :disabled="!selectedFile || loading" style="width:100%">
          {{ loading ? '⏳ Analysiere...' : '🔍 Bild analysieren' }}
        </button>

        <div v-if="error" class="error-msg">⚠️ {{ error }}</div>
      </div>

      <div class="results-panel">
        <div v-if="!result" class="empty-result">
          <div style="font-size:3rem;margin-bottom:1rem">🔍</div>
          <p>Lade ein Bild hoch und analysiere es</p>
        </div>

        <div v-if="result" class="card">
          <div class="result-header">
            <h3>Ergebnis: <span class="top-label">{{ result.top_label }}</span></h3>
            <span class="badge badge-primary">{{ result.mode === 'zero-shot' ? 'Zero-Shot' : 'ImageNet' }}</span>
          </div>

          <div class="result-bars">
            <div v-for="r in result.results.slice(0, 8)" :key="r.label" class="result-bar-row">
              <div class="result-label" :title="r.label">{{ r.label }}</div>
              <div class="bar-track">
                <div class="bar-fill" :style="{ width: (r.score * 100) + '%' }" />
              </div>
              <div class="result-score">{{ (r.score * 100).toFixed(1) }}%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { api } from '../stores/api'

const selectedFile = ref<File | null>(null)
const previewUrl = ref('')
const domain = ref('general')
const customLabels = ref('')
const loading = ref(false)
const error = ref('')
const result = ref<any>(null)
const dragging = ref(false)
const fileInput = ref<HTMLInputElement>()

function setFile(file: File) {
  if (!file.type.startsWith('image/')) {
    error.value = 'Nur Bilder erlaubt'
    return
  }
  selectedFile.value = file
  previewUrl.value = URL.createObjectURL(file)
  result.value = null
  error.value = ''
}

function onFileChange(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (f) setFile(f)
}

function onDrop(e: DragEvent) {
  dragging.value = false
  const f = e.dataTransfer?.files[0]
  if (f) setFile(f)
}

async function classify() {
  if (!selectedFile.value) return
  loading.value = true
  error.value = ''
  result.value = null
  try {
    result.value = await api.image.classify(selectedFile.value, domain.value, customLabels.value || undefined)
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
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

.upload-panel h3 { margin-bottom: 1rem; }

.drop-zone {
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.drop-zone:hover, .drop-zone.dragging {
  border-color: var(--primary);
  background: rgba(99,102,241,0.05);
}

.drop-zone.has-image { padding: 0; }

.preview-img {
  width: 100%;
  height: 200px;
  object-fit: contain;
  border-radius: 10px;
}

.drop-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
.drop-placeholder p { color: var(--text-muted); }
.hint { font-size: 0.8rem; margin-top: 0.3rem; }

.error-msg {
  margin-top: 0.75rem;
  padding: 0.5rem 0.75rem;
  background: rgba(239,68,68,0.1);
  border-radius: 8px;
  color: #f87171;
  font-size: 0.85rem;
}

.empty-result {
  text-align: center;
  color: var(--text-muted);
  padding: 4rem 2rem;
  background: var(--bg-card);
  border: 1px dashed var(--border);
  border-radius: var(--radius);
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.top-label { color: var(--primary-light); }

.result-bars { display: flex; flex-direction: column; gap: 0.6rem; }

.result-bar-row {
  display: grid;
  grid-template-columns: 160px 1fr 50px;
  align-items: center;
  gap: 0.5rem;
}

.result-label {
  font-size: 0.85rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bar-track { background: var(--border); border-radius: 4px; height: 8px; overflow: hidden; }
.bar-fill { height: 100%; background: linear-gradient(90deg, var(--primary), var(--secondary)); border-radius: 4px; transition: width 0.5s; }
.result-score { font-size: 0.8rem; color: var(--text-muted); text-align: right; }
</style>
