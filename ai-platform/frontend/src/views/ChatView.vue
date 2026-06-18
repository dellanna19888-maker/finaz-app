<template>
  <div class="chat-page">
    <div class="chat-header">
      <div>
        <h1>💬 Chat / Assistent</h1>
        <p class="subtitle">Sprich mit deiner KI</p>
      </div>
      <div class="domain-selector">
        <label>Bereich:</label>
        <select v-model="selectedDomain">
          <option v-for="d in domains" :key="d.id" :value="d.id">
            {{ d.icon }} {{ d.name }}
          </option>
        </select>
        <button class="btn btn-secondary" @click="clearChat">🗑 Löschen</button>
      </div>
    </div>

    <div class="messages" ref="messagesEl">
      <div v-if="messages.length === 0" class="empty-state">
        <div class="empty-icon">🤖</div>
        <p>Starte ein Gespräch! Wähle einen Bereich oben und schreibe eine Nachricht.</p>
        <div class="suggestions">
          <button
            v-for="s in suggestions[selectedDomain] || suggestions.general"
            :key="s"
            class="suggestion-chip"
            @click="sendSuggestion(s)"
          >{{ s }}</button>
        </div>
      </div>

      <div
        v-for="(msg, i) in messages"
        :key="i"
        class="message"
        :class="msg.role"
      >
        <div class="message-avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
        <div class="message-bubble">
          <div class="message-content">{{ msg.content }}</div>
          <div class="message-time">{{ msg.time }}</div>
        </div>
      </div>

      <div v-if="loading" class="message assistant">
        <div class="message-avatar">🤖</div>
        <div class="message-bubble">
          <div class="typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-input-area">
      <div v-if="error" class="error-bar">⚠️ {{ error }}</div>
      <div class="input-row">
        <textarea
          v-model="input"
          placeholder="Schreib eine Nachricht..."
          rows="1"
          @keydown.enter.exact.prevent="send"
          @input="autoResize"
          ref="textareaEl"
        />
        <button class="btn btn-primary send-btn" @click="send" :disabled="loading || !input.trim()">
          {{ loading ? '⏳' : '➤' }}
        </button>
      </div>
      <div class="input-hint">Enter = Senden · Shift+Enter = neue Zeile</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import { api } from '../stores/api'

interface Message { role: 'user' | 'assistant'; content: string; time: string }

const messages = ref<Message[]>([])
const input = ref('')
const loading = ref(false)
const error = ref('')
const selectedDomain = ref('general')
const domains = ref<Array<{id:string;name:string;icon:string}>>([])
const messagesEl = ref<HTMLElement>()
const textareaEl = ref<HTMLTextAreaElement>()

const suggestions: Record<string, string[]> = {
  general: ['Was kannst du?', 'Erkläre mir KI', 'Wie trainiere ich ein Modell?'],
  health: ['Erkläre Blutdruckwerte', 'Was bedeutet ein erhöhter CRP-Wert?', 'Wann zum Arzt gehen?'],
  ecommerce: ['Schreib eine Produktbeschreibung', 'Analysiere diese Bewertung', 'SEO-Tipps für Produkte'],
  education: ['Erkläre Photosynthese einfach', 'Was ist der Satz des Pythagoras?', 'Lernplan erstellen'],
}

function autoResize() {
  if (!textareaEl.value) return
  textareaEl.value.style.height = 'auto'
  textareaEl.value.style.height = Math.min(textareaEl.value.scrollHeight, 120) + 'px'
}

function scrollBottom() {
  nextTick(() => {
    if (messagesEl.value) {
      messagesEl.value.scrollTop = messagesEl.value.scrollHeight
    }
  })
}

function now() {
  return new Date().toLocaleTimeString('de', { hour: '2-digit', minute: '2-digit' })
}

async function send() {
  const text = input.value.trim()
  if (!text || loading.value) return

  messages.value.push({ role: 'user', content: text, time: now() })
  input.value = ''
  error.value = ''
  loading.value = true
  scrollBottom()

  try {
    const payload = messages.value.map(m => ({ role: m.role, content: m.content }))
    const res: any = await api.chat.send(payload, selectedDomain.value)
    messages.value.push({ role: 'assistant', content: res.reply, time: now() })
  } catch (e: any) {
    error.value = e.message || 'Fehler beim Senden'
  } finally {
    loading.value = false
    scrollBottom()
  }
}

function sendSuggestion(text: string) {
  input.value = text
  send()
}

function clearChat() {
  messages.value = []
  error.value = ''
}

onMounted(async () => {
  try {
    const res = await api.chat.domains()
    domains.value = res.domains
  } catch {
    domains.value = [
      { id: 'general', name: 'Allgemein', icon: '🤖' },
      { id: 'health', name: 'Gesundheit', icon: '🏥' },
      { id: 'ecommerce', name: 'E-Commerce', icon: '🛍️' },
      { id: 'education', name: 'Bildung', icon: '📚' },
    ]
  }
})
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 0;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border);
  background: var(--bg-card);
  flex-wrap: wrap;
  gap: 1rem;
}

.chat-header h1 { font-size: 1.3rem; }
.subtitle { color: var(--text-muted); font-size: 0.85rem; }

.domain-selector {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.domain-selector label { font-size: 0.85rem; color: var(--text-muted); white-space: nowrap; }
.domain-selector select { width: auto; min-width: 160px; }

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.empty-state {
  text-align: center;
  margin: auto;
  color: var(--text-muted);
}

.empty-icon { font-size: 3rem; margin-bottom: 0.75rem; }

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  margin-top: 1rem;
}

.suggestion-chip {
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--primary-light);
  border-radius: 999px;
  padding: 0.4rem 1rem;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-chip:hover {
  border-color: var(--primary);
  background: rgba(99,102,241,0.1);
}

.message {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
  max-width: 75%;
}

.message.user {
  flex-direction: row-reverse;
  align-self: flex-end;
}

.message.assistant { align-self: flex-start; }

.message-avatar { font-size: 1.4rem; flex-shrink: 0; }

.message-bubble {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 0.75rem 1rem;
  max-width: 100%;
}

.message.user .message-bubble {
  background: rgba(99,102,241,0.2);
  border-color: var(--primary);
}

.message-content { font-size: 0.95rem; white-space: pre-wrap; word-break: break-word; }

.message-time { font-size: 0.7rem; color: var(--text-muted); margin-top: 0.3rem; text-align: right; }

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 0.25rem 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: var(--primary-light);
  border-radius: 50%;
  animation: bounce 1.2s infinite;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-6px); }
}

.chat-input-area {
  border-top: 1px solid var(--border);
  background: var(--bg-card);
  padding: 1rem 1.5rem;
}

.error-bar {
  background: rgba(239,68,68,0.1);
  border: 1px solid rgba(239,68,68,0.3);
  border-radius: 8px;
  padding: 0.5rem 0.75rem;
  font-size: 0.85rem;
  color: #f87171;
  margin-bottom: 0.75rem;
}

.input-row {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
}

.input-row textarea {
  resize: none;
  overflow: hidden;
  min-height: 42px;
  line-height: 1.5;
}

.send-btn {
  flex-shrink: 0;
  height: 42px;
  width: 48px;
  font-size: 1.1rem;
  padding: 0;
  justify-content: center;
}

.input-hint {
  font-size: 0.72rem;
  color: var(--text-muted);
  margin-top: 0.4rem;
  text-align: right;
}
</style>
