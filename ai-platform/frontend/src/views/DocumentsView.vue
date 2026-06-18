<template>
  <div class="page">
    <div class="page-header">
      <h1>📄 Dokument-Analyse</h1>
      <p class="subtitle">PDFs und Texte zusammenfassen und befragen</p>
    </div>

    <div class="layout">
      <div class="upload-panel card">
        <h3>Dokument hochladen</h3>

        <div
          class="drop-zone"
          :class="{ dragging }"
          @dragover.prevent="dragging = true"
          @dragleave="dragging = false"
          @drop.prevent="onDrop"
          @click="fileInput?.click()"
        >
          <div v-if="uploadedDoc">
            <div class="doc-icon">📄</div>
            <div class="doc-name">{{ uploadedDoc.filename }}</div>
            <div class="doc-stats">
              {{ uploadedDoc.word_count.toLocaleString() }} Wörter
              · {{ (uploadedDoc.size_bytes / 1024).toFixed(1) }} KB
            </div>
          </div>
          <div v-else class="drop-placeholder">
            <div class="drop-icon">📄</div>
            <p>PDF oder TXT hierher ziehen</p>
            <p class="hint">Bis 50MB</p>
          </div>
        </div>

        <input ref="fileInput" type="file" accept=".pdf,.txt" style="display:none" @change="onFileChange" />

        <div v-if="uploadError" class="error-msg">⚠️ {{ uploadError }}</div>

        <div v-if="uploadedDoc" class="doc-actions">
          <button class="btn btn-primary" @click="summarize" :disabled="loading">
            {{ loading && activeAction === 'summarize' ? '⏳ Zusammenfasse...' : '📋 Zusammenfassen' }}
          </button>
          <button class="btn btn-secondary" @click="uploadedDoc = null; result = null">
            🗑 Neues Dokument
          </button>
        </div>
      </div>

      <div class="right-panel">
        <div v-if="uploadedDoc" class="card qa-card">
          <h3>❓ Frage zum Dokument stellen</h3>
          <div class="qa-input">
            <input v-model="question" placeholder="Was ist das Thema? Wer ist der Autor? ..." @keydown.enter="askQuestion" />
            <button class="btn btn-primary" @click="askQuestion" :disabled="loading || !question.trim()">
              {{ loading && activeAction === 'qa' ? '⏳' : '➤' }}
            </button>
          </div>
          <div v-if="qaResult" class="qa-result">
            <div class="qa-question">❓ {{ qaResult.question }}</div>
            <div class="qa-answer">💡 {{ qaResult.answer }}</div>
            <div class="qa-confidence">Konfidenz: {{ (qaResult.confidence * 100).toFixed(1) }}%</div>
          </div>
        </div>

        <div v-if="result" class="card summary-card">
          <h3>📋 Zusammenfassung</h3>
          <p class="summary-text">{{ result.summary }}</p>
          <div class="summary-stats">
            <span>{{ result.word_count.toLocaleString() }} Wörter</span>
            <span>{{ result.char_count.toLocaleString() }} Zeichen</span>
          </div>
        </div>

        <div v-if="!uploadedDoc && !result" class="empty-result">
          <div style="font-size:3rem;margin-bottom:1rem">📄</div>
          <p>Lade ein Dokument hoch, um es zu analysieren</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { api } from '../stores/api'

const uploadedDoc = ref<any>(null)
const result = ref<any>(null)
const qaResult = ref<any>(null)
const question = ref('')
const loading = ref(false)
const uploadError = ref('')
const activeAction = ref('')
const dragging = ref(false)
const fileInput = ref<HTMLInputElement>()

async function uploadFile(file: File) {
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (!['pdf', 'txt'].includes(ext || '')) {
    uploadError.value = 'Nur PDF und TXT erlaubt'
    return
  }
  uploadError.value = ''
  loading.value = true
  activeAction.value = 'upload'
  try {
    uploadedDoc.value = await api.documents.upload(file)
    result.value = null
    qaResult.value = null
  } catch (e: any) {
    uploadError.value = e.message
  } finally {
    loading.value = false
  }
}

function onFileChange(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (f) uploadFile(f)
}

function onDrop(e: DragEvent) {
  dragging.value = false
  const f = e.dataTransfer?.files[0]
  if (f) uploadFile(f)
}

async function summarize() {
  if (!uploadedDoc.value) return
  loading.value = true
  activeAction.value = 'summarize'
  try {
    result.value = await api.documents.summarize(uploadedDoc.value.document_id)
  } catch (e: any) {
    uploadError.value = e.message
  } finally {
    loading.value = false
  }
}

async function askQuestion() {
  if (!question.value.trim() || !uploadedDoc.value) return
  loading.value = true
  activeAction.value = 'qa'
  try {
    qaResult.value = await api.documents.qa(uploadedDoc.value.document_id, question.value)
  } catch (e: any) {
    uploadError.value = e.message
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
  grid-template-columns: 1fr 1.5fr;
  gap: 1.5rem;
}

@media (max-width: 800px) {
  .layout { grid-template-columns: 1fr; }
}

.upload-panel h3 { margin-bottom: 1rem; }

.drop-zone {
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  padding: 2rem 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  min-height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drop-zone:hover, .drop-zone.dragging {
  border-color: var(--primary);
  background: rgba(99,102,241,0.05);
}

.doc-icon { font-size: 3rem; margin-bottom: 0.5rem; }
.doc-name { font-weight: 600; word-break: break-all; }
.doc-stats { font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem; }
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

.doc-actions { display: flex; gap: 0.75rem; margin-top: 1rem; flex-wrap: wrap; }

.right-panel { display: flex; flex-direction: column; gap: 1rem; }

.qa-card h3 { margin-bottom: 0.75rem; }

.qa-input { display: flex; gap: 0.5rem; }
.qa-input input { flex: 1; }
.qa-input button { flex-shrink: 0; }

.qa-result {
  margin-top: 1rem;
  padding: 0.75rem;
  background: var(--bg);
  border-radius: 8px;
  border: 1px solid var(--border);
}

.qa-question { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.3rem; }
.qa-answer { font-size: 1rem; font-weight: 600; color: var(--secondary); }
.qa-confidence { font-size: 0.75rem; color: var(--text-muted); margin-top: 0.3rem; }

.summary-card h3 { margin-bottom: 0.75rem; }
.summary-text { line-height: 1.7; color: var(--text); }
.summary-stats { display: flex; gap: 1rem; font-size: 0.8rem; color: var(--text-muted); margin-top: 0.75rem; }

.empty-result {
  text-align: center;
  color: var(--text-muted);
  padding: 4rem 2rem;
  background: var(--bg-card);
  border: 1px dashed var(--border);
  border-radius: var(--radius);
}
</style>
