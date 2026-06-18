<template>
  <div class="page">
    <div class="page-header">
      <h1>🧠 KI-Plattform</h1>
      <p class="subtitle">Deine eigene KI — trainieren, analysieren, verstehen</p>
    </div>

    <div class="stats-grid">
      <div class="stat-card" v-for="s in stats" :key="s.label">
        <div class="stat-icon">{{ s.icon }}</div>
        <div class="stat-value">{{ s.value }}</div>
        <div class="stat-label">{{ s.label }}</div>
      </div>
    </div>

    <h2 class="section-title">Funktionen</h2>
    <div class="features-grid">
      <RouterLink
        v-for="f in features"
        :key="f.to"
        :to="f.to"
        class="feature-card card card-hover"
      >
        <div class="feature-icon">{{ f.icon }}</div>
        <div class="feature-body">
          <h3>{{ f.title }}</h3>
          <p>{{ f.desc }}</p>
          <div class="feature-tags">
            <span class="badge badge-primary" v-for="tag in f.tags" :key="tag">{{ tag }}</span>
          </div>
        </div>
      </RouterLink>
    </div>

    <div class="info-cards">
      <div class="card info-card">
        <h3>🚀 Schnellstart</h3>
        <ol class="steps">
          <li>Gehe zu <RouterLink to="/training">KI Trainieren</RouterLink> und lade deine Daten hoch</li>
          <li>Wähle ein Basismodell von Hugging Face</li>
          <li>Starte das Training und beobachte den Fortschritt</li>
          <li>Nutze dein trainiertes Modell in Chat, Text- oder Bildanalyse</li>
        </ol>
      </div>

      <div class="card info-card">
        <h3>📋 Datenformat für Training</h3>
        <pre class="code-block">{{ dataFormatExample }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { ref, onMounted } from 'vue'
import { api } from '../stores/api'

const stats = ref([
  { icon: '🤖', value: '5', label: 'Vortrainierte Modelle' },
  { icon: '🎓', value: '0', label: 'Eigene Modelle' },
  { icon: '📄', value: '3', label: 'Unterstützte Aufgaben' },
  { icon: '🌐', value: '100+', label: 'Sprachen (multilingual)' },
])

const features = [
  {
    to: '/chat',
    icon: '💬',
    title: 'Chat / Assistent',
    desc: 'Sprich mit deiner KI — für Gesundheit, E-Commerce oder Bildung',
    tags: ['Gesundheit', 'E-Commerce', 'Bildung'],
  },
  {
    to: '/text',
    icon: '📝',
    title: 'Text-Klassifikation',
    desc: 'Texte automatisch in Kategorien einteilen und Stimmung erkennen',
    tags: ['Zero-Shot', 'Multilingual'],
  },
  {
    to: '/image',
    icon: '🖼️',
    title: 'Bild-Erkennung',
    desc: 'Bilder analysieren und klassifizieren mit Vision AI',
    tags: ['CLIP', 'ViT', 'Zero-Shot'],
  },
  {
    to: '/documents',
    icon: '📄',
    title: 'Dokument-Analyse',
    desc: 'PDFs zusammenfassen und Fragen zu Dokumenten stellen',
    tags: ['PDF', 'Zusammenfassung', 'Q&A'],
  },
  {
    to: '/training',
    icon: '🎓',
    title: 'KI Trainieren',
    desc: 'Fine-Tuning mit eigenen Daten — speziell für dein Thema',
    tags: ['Fine-Tuning', 'Hugging Face'],
  },
  {
    to: '/models',
    icon: '🗄️',
    title: 'Meine Modelle',
    desc: 'Alle vortrainierten und eigenen Modelle verwalten',
    tags: ['Übersicht', 'Verwalten'],
  },
]

const dataFormatExample = `[
  {
    "text": "Patient hat Fieber 38.5°C",
    "label": "Symptome"
  },
  {
    "text": "2x täglich 500mg Ibuprofen",
    "label": "Medikamente"
  }
]`

onMounted(async () => {
  try {
    const result = await api.models.list()
    stats.value[1].value = String(result.custom.length)
  } catch {}
})
</script>

<style scoped>
.page {
  padding: 2rem;
  max-width: 1100px;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(135deg, #a5b4fc, #34d399);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  color: var(--text-muted);
  margin-top: 0.3rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 1rem;
  margin-bottom: 2.5rem;
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.25rem;
  text-align: center;
}

.stat-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.stat-value { font-size: 1.75rem; font-weight: 700; color: var(--primary-light); }
.stat-label { font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem; }

.section-title {
  font-size: 1.1rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 1rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.feature-card {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  text-decoration: none;
  color: inherit;
}

.feature-icon { font-size: 2rem; flex-shrink: 0; }

.feature-body h3 { font-size: 1rem; margin-bottom: 0.3rem; }
.feature-body p { font-size: 0.875rem; color: var(--text-muted); margin-bottom: 0.5rem; }
.feature-tags { display: flex; flex-wrap: wrap; gap: 0.3rem; }

.info-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

@media (max-width: 700px) {
  .info-cards { grid-template-columns: 1fr; }
}

.info-card h3 { margin-bottom: 0.75rem; }

.steps {
  padding-left: 1.25rem;
  color: var(--text-muted);
  font-size: 0.9rem;
  line-height: 2;
}

.steps a { color: var(--primary-light); }

.code-block {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.75rem;
  font-size: 0.8rem;
  color: #34d399;
  overflow-x: auto;
  white-space: pre;
}
</style>
