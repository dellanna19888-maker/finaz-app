<template>
  <div class="ai-page">
    <div class="page-header">
      <h1>📊 Kanal-Check</h1>
      <p class="sub">
        Trag kurz deine Zahlen &amp; Konkurrenz ein – die 🧠 Zentrale analysiert, wie dein Kanal läuft,
        was du verbessern kannst und was die Konkurrenz macht. Kein API-Schlüssel nötig.
      </p>
    </div>

    <div class="card2">
      <h2>Mein Kanal</h2>
      <div class="form">
        <label>Plattform
          <input v-model="p.platform" class="inp" list="pf" />
          <datalist id="pf"><option>YouTube</option><option>TikTok</option><option>Instagram</option><option>Podcast</option><option>Twitch</option></datalist>
        </label>
        <label>Handle / Name <input v-model="p.handle" class="inp" placeholder="@meinkanal" /></label>
        <label>Abos / Follower <input v-model.number="p.followers" type="number" min="0" class="inp" /></label>
        <label>Nische / Thema <input v-model="p.niche" class="inp" placeholder="z. B. Tech-Tutorials" /></label>
      </div>
      <label class="full">Meine letzten Videos / Posts (Titel, gern mit Aufrufen)
        <textarea v-model="p.recent" class="ta" placeholder="- Mein Setup 2026 — 1.200 Aufrufe&#10;- 5 Apps, die ich liebe — 800 Aufrufe"></textarea>
      </label>
    </div>

    <div class="card2">
      <div class="row">
        <h2>Konkurrenz</h2>
        <span class="spacer"></span>
        <button class="btn-ghost" @click="store.addCompetitor()">+ Konkurrent</button>
      </div>
      <p v-if="!store.competitors.length" class="muted">Noch keine Konkurrenten – füg 1–3 hinzu, die du beobachten willst.</p>
      <div v-for="c in store.competitors" :key="c.id" class="comp">
        <input v-model="c.handle" class="inp" placeholder="@konkurrent" />
        <input v-model.number="c.followers" type="number" min="0" class="inp sm" placeholder="Follower" />
        <input v-model="c.notes" class="inp grow" placeholder="Was posten sie? Auffälligkeiten?" />
        <button class="btn-ghost xs" title="Entfernen" aria-label="Konkurrent entfernen" @click="store.deleteCompetitor(c.id)">✕</button>
      </div>
    </div>

    <div class="card2 analyze">
      <p>Fertig? Lass die Zentrale daraus eine Analyse machen:</p>
      <button class="btn" @click="analyze">🧠 Kanal analysieren</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useChannelStore } from '../stores/channel'

const store = useChannelStore()
const p = store.profile
const router = useRouter()

function analyze() {
  localStorage.setItem(
    'finaz_pending_prompt',
    'Analysiere meinen Kanal anhand der eingetragenen Zahlen und Konkurrenz: Wie läuft mein Kanal? Nenne 3 konkrete Verbesserungen und was die Konkurrenz anders/besser macht.',
  )
  router.push('/')
}
</script>

<style scoped>
.form { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.75rem; margin-bottom: 0.75rem; }
.form label, .full { display: flex; flex-direction: column; gap: 0.3rem; font-size: 0.85rem; color: #94a3b8; }
.full { margin-top: 0.5rem; }
.inp { padding: 0.5rem 0.6rem; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: #e2e8f0; }
.inp.sm { max-width: 140px; }
.ta { min-height: 90px; padding: 0.6rem; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: #e2e8f0; font: inherit; resize: vertical; }
.row { display: flex; align-items: center; }
.row .spacer { flex: 1; }
.comp { display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; margin-bottom: 0.5rem; }
.comp .inp.grow { flex: 1; min-width: 160px; }
.btn-ghost.xs { padding: 0.25rem 0.55rem; line-height: 1; }
.analyze { text-align: center; }
.analyze p { color: #94a3b8; margin-bottom: 0.6rem; }
</style>
