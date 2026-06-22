<template>
  <div class="page">
    <div class="page-header">
      <h1>📊 Kanal-Check</h1>
      <p class="sub">Trag deine Zahlen &amp; Konkurrenz ein — die KI-Zentrale analysiert deinen Kanal und gibt dir konkrete Verbesserungen.</p>
    </div>

    <!-- My channel -->
    <div class="card">
      <h2>📺 Mein Kanal</h2>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:0.75rem;margin-bottom:0.75rem">
        <label class="lbl">Plattform
          <input v-model="p.platform" class="inp" list="pf-list" placeholder="YouTube, TikTok …" />
          <datalist id="pf-list">
            <option>YouTube</option><option>TikTok</option><option>Instagram</option>
            <option>Podcast</option><option>Twitch</option><option>LinkedIn</option>
          </datalist>
        </label>
        <label class="lbl">Handle / Kanal-Name
          <input v-model="p.handle" class="inp" placeholder="@meinkanal" />
        </label>
        <label class="lbl">Abonnenten / Follower
          <input v-model.number="p.followers" type="number" min="0" class="inp" placeholder="0" />
        </label>
        <label class="lbl">Nische / Thema
          <input v-model="p.niche" class="inp" placeholder="z. B. Produktivität & KI" />
        </label>
      </div>
      <label class="lbl">Letzte Videos / Posts (Titel, gern mit Aufrufen)
        <textarea v-model="p.recent" class="ta" style="min-height:100px"
          placeholder="- Mein Setup 2026 — 1.200 Aufrufe&#10;- 5 KI-Tools die ich liebe — 800 Aufrufe&#10;- Produktivitäts-Trick — 2.100 Aufrufe"></textarea>
      </label>
    </div>

    <!-- Competitors -->
    <div class="card">
      <div style="display:flex;align-items:center;margin-bottom:0.9rem">
        <h2 style="margin-bottom:0">🏆 Konkurrenz</h2>
        <span class="spacer"></span>
        <button class="btn btn-ghost btn-sm" @click="store.addCompetitor()">+ Konkurrent</button>
      </div>
      <p v-if="!store.competitors.length" class="muted">Noch keine Konkurrenten — füg 1–3 hinzu, die du beobachtest.</p>
      <div v-for="c in store.competitors" :key="c.id" class="comp-row" style="margin-bottom:0.5rem">
        <input v-model="c.handle" class="inp" style="width:140px;flex-shrink:0" placeholder="@kanal" />
        <input v-model.number="c.followers" type="number" min="0" class="inp" style="width:120px;flex-shrink:0" placeholder="Follower" />
        <input v-model="c.notes" class="inp" style="flex:1;min-width:150px" placeholder="Was posten sie? Stärken?" />
        <button class="btn btn-ghost btn-sm" style="color:var(--red);flex-shrink:0" @click="store.deleteCompetitor(c.id)">✕</button>
      </div>
    </div>

    <!-- Analyze button -->
    <div class="card" style="text-align:center">
      <p class="muted" style="margin-bottom:0.75rem">Fertig? Lass die KI-Zentrale eine vollständige Analyse erstellen:</p>
      <button class="btn btn-primary btn-full" style="max-width:360px;margin:0 auto" @click="analyze">
        🧠 Kanal jetzt analysieren
      </button>
      <p class="muted" style="margin-top:0.75rem;font-size:0.8rem">→ Öffnet die Zentrale mit einer vorgefertigten Analyse-Anfrage</p>
    </div>

    <!-- Quick stats -->
    <div v-if="p.followers" class="card">
      <h2>📈 Schnell-Übersicht</h2>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:0.75rem">
        <div style="text-align:center;padding:0.75rem;background:var(--bg2);border-radius:var(--radius-sm)">
          <div style="font-size:1.4rem;font-weight:700;color:var(--accent2)">{{ formatNum(p.followers) }}</div>
          <div class="muted">Follower</div>
        </div>
        <div v-if="store.competitors.length" style="text-align:center;padding:0.75rem;background:var(--bg2);border-radius:var(--radius-sm)">
          <div style="font-size:1.4rem;font-weight:700;color:var(--amber)">{{ store.competitors.length }}</div>
          <div class="muted">Konkurrenten</div>
        </div>
        <div v-if="store.competitors.length" style="text-align:center;padding:0.75rem;background:var(--bg2);border-radius:var(--radius-sm)">
          <div style="font-size:1.4rem;font-weight:700;" :class="position === 'leader' ? 'text-green' : 'text-amber'">
            {{ position === 'leader' ? '🏆 Führend' : '📈 Aufsteiger' }}
          </div>
          <div class="muted">vs. Konkurrenz</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useChannelStore } from '../stores/channel'

const store = useChannelStore()
const p = store.profile
const router = useRouter()

const position = computed(() => {
  if (!store.competitors.length) return 'leader'
  const avg = store.competitors.reduce((s, c) => s + (c.followers || 0), 0) / store.competitors.length
  return p.followers >= avg ? 'leader' : 'growing'
})

function formatNum(n: number) {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M'
  if (n >= 1_000) return (n / 1_000).toFixed(1) + 'K'
  return String(n)
}

function analyze() {
  const parts: string[] = []
  parts.push(`Analysiere meinen ${p.platform || 'Social-Media'}-Kanal "${p.handle || 'meinKanal'}" (${p.followers || 0} Follower, Nische: ${p.niche || 'unbekannt'}).`)
  if (p.recent) parts.push(`Meine letzten Inhalte:\n${p.recent}`)
  if (store.competitors.length) {
    const comp = store.competitors.map(c => `${c.handle} (${c.followers || 0} Follower)${c.notes ? ' – ' + c.notes : ''}`).join(', ')
    parts.push(`Meine Konkurrenz: ${comp}`)
  }
  parts.push('Gib mir: 1) 3 konkrete Verbesserungen, 2) was meine Konkurrenz besser macht, 3) meinen nächsten konkreten Schritt.')
  localStorage.setItem('finaz_pending_prompt', parts.join('\n\n'))
  router.push('/')
}
</script>

<style scoped>
.text-green { color: var(--green); }
.text-amber { color: var(--amber); }
</style>
