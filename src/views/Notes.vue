<template>
  <div class="page">
    <div class="page-header" style="display:flex;align-items:flex-start;justify-content:space-between;gap:1rem">
      <div>
        <h1>📚 Wissensbasis</h1>
        <p class="sub">Deine persönliche Notizsammlung — Ideen, Learnings, Strategien.</p>
      </div>
      <div style="display:flex;gap:0.5rem;align-items:center;padding-top:0.25rem">
        <span class="muted" style="font-size:0.8rem">{{ saved ? '✓ gespeichert' : '' }}</span>
        <button class="btn btn-ghost btn-sm" @click="exportNotes">⬇ Export</button>
      </div>
    </div>

    <!-- Quick notes -->
    <div class="card">
      <h2>📝 Notizen</h2>
      <textarea
        v-model="notes"
        class="ta"
        style="min-height:260px;font-family:inherit;line-height:1.7"
        placeholder="Schreib hier deine Ideen, Learnings, Hook-Formeln, Strategien …&#10;&#10;Tipp: Die KI-Zentrale kann hier automatisch Notizen speichern (Aktion: Notiz anhängen)."
        @input="scheduleAutosave"
      ></textarea>
    </div>

    <!-- Quick templates -->
    <div class="card">
      <h2>⚡ Vorlagen (einfügen)</h2>
      <div style="display:flex;flex-wrap:wrap;gap:0.5rem">
        <button v-for="t in templates" :key="t.label" class="chip" @click="insertTemplate(t.text)">{{ t.label }}</button>
      </div>
    </div>

    <!-- Word count -->
    <div class="muted" style="margin-top:0.5rem;font-size:0.8rem">
      {{ wordCount }} Wörter · {{ notes.length }} Zeichen
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const SAVE_KEY = 'finaz_notes'
const notes = ref('')
const saved = ref(false)
let saveTimer: ReturnType<typeof setTimeout> | null = null

const wordCount = computed(() => notes.value.trim() ? notes.value.trim().split(/\s+/).length : 0)

const templates = [
  { label: '📌 Hook-Formel', text: '\n\n## Hook-Formel\n[Zahl] + [Versprechen] + [Neugier]\nBeispiel: "3 Fehler die 90% der Creator machen — und wie du sie vermeidest"\n' },
  { label: '📅 Wochenplan', text: '\n\n## Content-Woche\n| Tag | Format | Thema |\n|-----|--------|-------|\n| Mo  | Reel   |       |\n| Di  | Post   |       |\n| Mi  | Short  |       |\n| Do  | Story  |       |\n| Fr  | Reel   |       |\n' },
  { label: '🎯 Content-Idee', text: '\n\n## Idee: [Titel]\n- Zielgruppe: \n- Problem: \n- Lösung: \n- Hook: \n- CTA: \n' },
  { label: '📊 Kanal-Review', text: '\n\n## Kanal-Review [Datum]\n- Top-Video: \n- Schwächstes Video: \n- Was ich ändere: \n- Nächster Fokus: \n' },
  { label: '✍️ Skript-Struktur', text: '\n\n## Skript: [Titel]\n**[0-3s] HOOK:**\n\n**[3-15s] PROBLEM:**\n\n**[15-40s] LÖSUNG:**\n\n**[40-55s] BEWEIS:**\n\n**[55-60s] CTA:**\n' },
]

function scheduleAutosave() {
  if (saveTimer) clearTimeout(saveTimer)
  saveTimer = setTimeout(() => { localStorage.setItem(SAVE_KEY, notes.value); saved.value = true; setTimeout(() => saved.value = false, 2000) }, 600)
}

function insertTemplate(text: string) { notes.value += text; scheduleAutosave() }

function exportNotes() {
  const blob = new Blob([notes.value], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a'); a.href = url; a.download = 'wissensbasis.txt'; a.click()
  URL.revokeObjectURL(url)
}

onMounted(() => { notes.value = localStorage.getItem(SAVE_KEY) || '' })
</script>
