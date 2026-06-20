<template>
  <div class="aff-wrap">
    <!-- Hero -->
    <div class="aff-hero">
      <RouterLink to="/" class="back-link">← Zurück zur Startseite</RouterLink>
      <div class="aff-badge">💰 Partnerprogramm</div>
      <h1>Verdiene <span class="green">30% Provision</span><br>für jede Empfehlung</h1>
      <p class="aff-sub">Empfiehl SecureHub auf deiner Website, deinem YouTube-Kanal oder Social Media – und verdiene dauerhaft 30% von jeder Zahlung deiner geworbenen Kunden.</p>
      <div class="aff-stats">
        <div class="aff-stat"><strong>30%</strong><span>Provision</span></div>
        <div class="aff-div"></div>
        <div class="aff-stat"><strong>90 Tage</strong><span>Cookie-Laufzeit</span></div>
        <div class="aff-div"></div>
        <div class="aff-stat"><strong>Monatlich</strong><span>Auszahlung</span></div>
        <div class="aff-div"></div>
        <div class="aff-stat"><strong>Live</strong><span>Statistiken</span></div>
      </div>
    </div>

    <!-- Wie es funktioniert -->
    <section class="how-section">
      <h2>So funktioniert es</h2>
      <div class="steps">
        <div class="step">
          <div class="step-num">1</div>
          <h3>Registrieren</h3>
          <p>Trage dich unten ein und erhalte sofort deinen persönlichen Affiliate-Link.</p>
        </div>
        <div class="step-arrow">→</div>
        <div class="step">
          <div class="step-num">2</div>
          <h3>Teilen</h3>
          <p>Teile deinen Link auf deiner Website, YouTube, Instagram oder per E-Mail.</p>
        </div>
        <div class="step-arrow">→</div>
        <div class="step">
          <div class="step-num">3</div>
          <h3>Verdienen</h3>
          <p>Für jedes bezahlte Abo über deinen Link erhältst du 30% dauerhaft.</p>
        </div>
      </div>
    </section>

    <!-- Provisionsrechner -->
    <section class="calc-section">
      <h2>💰 Verdienst-Rechner</h2>
      <p class="section-sub">Wie viel kannst du verdienen?</p>
      <div class="calc-box">
        <div class="calc-row">
          <label>Empfehlungen pro Monat</label>
          <input v-model.number="calcRefs" type="range" min="1" max="100" />
          <span class="calc-val">{{ calcRefs }}</span>
        </div>
        <div class="calc-row">
          <label>Ø Plan</label>
          <select v-model="calcPlan">
            <option value="19">Pro (19€/Monat)</option>
            <option value="49">Business (49€/Monat)</option>
          </select>
        </div>
        <div class="calc-result">
          <div class="calc-num">{{ calcMonthly }}€ <span>/ Monat</span></div>
          <div class="calc-year">= {{ calcYearly }}€ pro Jahr</div>
        </div>
      </div>
    </section>

    <!-- Registrierung -->
    <section class="reg-section">
      <h2>Jetzt Affiliate werden</h2>
      <p class="section-sub">Kostenlos · Sofortzugang · Keine Mindestbestellwerte</p>

      <div v-if="!registered" class="reg-form">
        <div class="field">
          <label>Dein Name</label>
          <input v-model="form.name" placeholder="Max Mustermann" />
        </div>
        <div class="field">
          <label>E-Mail-Adresse</label>
          <input v-model="form.email" type="email" placeholder="max@beispiel.de" />
        </div>
        <div class="field">
          <label>Website / Kanal (optional)</label>
          <input v-model="form.website" placeholder="https://deinkanal.de" />
        </div>
        <p v-if="regError" class="err-msg">⚠ {{ regError }}</p>
        <button class="btn-reg" :disabled="regLoading || !form.name || !form.email" @click="register">
          {{ regLoading ? 'Wird erstellt…' : 'Affiliate-Konto erstellen →' }}
        </button>
      </div>

      <!-- Erfolg -->
      <div v-else class="reg-success">
        <div class="success-icon">🎉</div>
        <h3>Willkommen im Partnerprogramm!</h3>
        <p>Dein persönlicher Affiliate-Link:</p>
        <div class="link-box">
          <span class="aff-link">{{ affiliateLink }}</span>
          <button class="btn-copy" @click="copyLink">{{ copied ? '✓ Kopiert!' : 'Kopieren' }}</button>
        </div>
        <p class="link-hint">Dein Code: <strong>{{ affiliateCode }}</strong> · Dashboard: <RouterLink to="/affiliate/portal">Statistiken ansehen →</RouterLink></p>
      </div>
    </section>

    <!-- Werbe-Materialien -->
    <section class="materials-section">
      <h2>📦 Werbe-Materialien</h2>
      <div class="materials-grid">
        <div class="material-card">
          <div class="mat-icon">📝</div>
          <h3>Text-Banner</h3>
          <div class="code-box">{{ textBanner }}</div>
          <button class="btn-sm" @click="copy(textBanner)">Kopieren</button>
        </div>
        <div class="material-card">
          <div class="mat-icon">🔗</div>
          <h3>HTML-Link</h3>
          <div class="code-box">{{ htmlLink }}</div>
          <button class="btn-sm" @click="copy(htmlLink)">Kopieren</button>
        </div>
        <div class="material-card">
          <div class="mat-icon">📱</div>
          <h3>Social Media Text</h3>
          <div class="code-box">{{ socialText }}</div>
          <button class="btn-sm" @click="copy(socialText)">Kopieren</button>
        </div>
      </div>
    </section>

    <!-- FAQ -->
    <section class="aff-faq">
      <h2>Häufige Fragen</h2>
      <div v-for="q in faqs" :key="q.q" class="faq-item">
        <strong>{{ q.q }}</strong>
        <p>{{ q.a }}</p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const calcRefs = ref(10)
const calcPlan = ref('19')
const calcMonthly = computed(() => Math.round(calcRefs.value * Number(calcPlan.value) * 0.3))
const calcYearly = computed(() => calcMonthly.value * 12)

const form = ref({ name: '', email: '', website: '' })
const regLoading = ref(false)
const regError = ref('')
const registered = ref(false)
const affiliateCode = ref('')
const copied = ref(false)

const affiliateLink = computed(() =>
  registered.value ? `${window.location.origin}/?ref=${affiliateCode.value}` : ''
)

const textBanner = computed(() =>
  `🛡️ Sichere deine Website mit SecureHub – Cyber Security Scanner + Server-Monitor. Jetzt kostenlos testen: ${affiliateLink.value || 'https://securehub.de/?ref=DEINCODE'}`
)
const htmlLink = computed(() =>
  `<a href="${affiliateLink.value || 'https://securehub.de/?ref=DEINCODE'}" target="_blank">🛡️ SecureHub – Website Security Scanner</a>`
)
const socialText = computed(() =>
  `Ich nutze SecureHub für meine Website-Sicherheit 🔒\n✅ Security Scanner\n✅ Server Monitor\n✅ KI-Assistent\n👉 Jetzt kostenlos testen: ${affiliateLink.value || 'https://securehub.de/?ref=DEINCODE'}`
)

async function register() {
  regLoading.value = true
  regError.value = ''
  try {
    const res = await fetch('/api/affiliate/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.error || 'Registrierung fehlgeschlagen')
    affiliateCode.value = data.code
    registered.value = true
    localStorage.setItem('finaz_aff_code', data.code)
    localStorage.setItem('finaz_aff_email', form.value.email)
  } catch (e: unknown) {
    regError.value = (e as Error).message
  } finally {
    regLoading.value = false
  }
}

async function copyLink() {
  await navigator.clipboard.writeText(affiliateLink.value)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

async function copy(text: string) {
  await navigator.clipboard.writeText(text)
}

const faqs = [
  { q: 'Wie hoch ist die Provision?', a: '30% von jeder Zahlung – dauerhaft, solange der geworbene Kunde zahlt. Bei einem Pro-Plan (19€/Monat) verdienst du 5,70€ pro Monat pro Kunde.' },
  { q: 'Wie lange läuft der Affiliate-Cookie?', a: '90 Tage. Wenn jemand deinen Link klickt und innerhalb von 90 Tagen kauft, erhältst du die Provision.' },
  { q: 'Wie wird ausgezahlt?', a: 'Monatlich per PayPal oder Banküberweisung ab einem Mindestbetrag von 20€.' },
  { q: 'Gibt es Einschränkungen?', a: 'Kein Spam, keine irreführende Werbung. Ansonsten kannst du auf jeder Plattform werben: Website, YouTube, Instagram, TikTok, Newsletter.' },
]
</script>

<style scoped>
.aff-wrap { max-width: 900px; margin: 0 auto; padding: 2rem 1.5rem; }
.back-link { font-size: 0.85rem; color: #64748b; text-decoration: none; display: inline-block; margin-bottom: 1rem; }
.back-link:hover { color: #94a3b8; }

/* Hero */
.aff-hero { text-align: center; padding: 2rem 0 3rem; }
.aff-badge { display: inline-block; padding: 0.3rem 1rem; border-radius: 999px; background: rgba(34,197,94,0.15); border: 1px solid rgba(34,197,94,0.3); color: #4ade80; font-size: 0.85rem; margin-bottom: 1rem; }
.aff-hero h1 { font-size: 2.75rem; font-weight: 800; line-height: 1.15; margin: 0 0 1rem; color: #e2e8f0; }
.green { color: #4ade80; }
.aff-sub { color: #94a3b8; font-size: 1rem; max-width: 600px; margin: 0 auto 2rem; line-height: 1.6; }
.aff-stats { display: flex; align-items: center; justify-content: center; gap: 2rem; flex-wrap: wrap; }
.aff-stat { text-align: center; }
.aff-stat strong { display: block; font-size: 1.5rem; font-weight: 700; color: #4ade80; }
.aff-stat span { font-size: 0.8rem; color: #64748b; }
.aff-div { width: 1px; height: 30px; background: #1e293b; }

/* Steps */
.how-section { text-align: center; padding: 3rem 0; }
.how-section h2 { font-size: 1.75rem; font-weight: 700; margin: 0 0 2rem; }
.steps { display: flex; align-items: center; justify-content: center; gap: 1rem; flex-wrap: wrap; }
.step { background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 1.5rem; max-width: 200px; }
.step-num { width: 36px; height: 36px; border-radius: 50%; background: rgba(59,130,246,0.2); color: #60a5fa; font-weight: 700; font-size: 1.1rem; display: flex; align-items: center; justify-content: center; margin: 0 auto 0.75rem; }
.step h3 { margin: 0 0 0.4rem; color: #e2e8f0; font-size: 1rem; }
.step p { font-size: 0.82rem; color: #94a3b8; margin: 0; line-height: 1.5; }
.step-arrow { font-size: 1.5rem; color: #334155; }

/* Rechner */
.calc-section { text-align: center; padding: 3rem 0; }
.calc-section h2 { font-size: 1.75rem; font-weight: 700; margin: 0 0 0.5rem; }
.section-sub { color: #94a3b8; margin: 0 0 2rem; }
.calc-box { background: #0f172a; border: 1px solid #1e293b; border-radius: 16px; padding: 2rem; max-width: 480px; margin: 0 auto; }
.calc-row { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap; }
.calc-row label { font-size: 0.88rem; color: #94a3b8; flex: 1; min-width: 160px; text-align: left; }
.calc-row input[type=range] { flex: 2; accent-color: #3b82f6; }
.calc-row select { flex: 2; padding: 0.4rem; background: #1e293b; border: 1px solid #334155; border-radius: 6px; color: #e2e8f0; font-size: 0.88rem; }
.calc-val { width: 30px; text-align: right; font-weight: 600; color: #e2e8f0; }
.calc-result { border-top: 1px solid #1e293b; padding-top: 1.25rem; margin-top: 0.5rem; }
.calc-num { font-size: 2.5rem; font-weight: 800; color: #4ade80; }
.calc-num span { font-size: 1rem; color: #64748b; font-weight: 400; }
.calc-year { color: #64748b; font-size: 0.9rem; }

/* Registrierung */
.reg-section { padding: 3rem 0; text-align: center; }
.reg-section h2 { font-size: 1.75rem; font-weight: 700; margin: 0 0 0.5rem; }
.reg-form { max-width: 440px; margin: 0 auto; background: #0f172a; border: 1px solid #1e293b; border-radius: 16px; padding: 2rem; text-align: left; }
.field { margin-bottom: 1rem; }
.field label { display: block; font-size: 0.85rem; color: #94a3b8; margin-bottom: 0.35rem; }
.field input { width: 100%; padding: 0.65rem 0.9rem; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: #e2e8f0; font-size: 0.95rem; box-sizing: border-box; }
.field input:focus { outline: none; border-color: #3b82f6; }
.err-msg { color: #f87171; font-size: 0.85rem; background: rgba(248,113,113,0.1); padding: 0.5rem 0.75rem; border-radius: 8px; margin-bottom: 1rem; }
.btn-reg { width: 100%; padding: 0.8rem; border-radius: 10px; border: none; background: #22c55e; color: #000; font-size: 1rem; font-weight: 700; cursor: pointer; transition: background 0.2s; }
.btn-reg:hover:not(:disabled) { background: #16a34a; }
.btn-reg:disabled { opacity: 0.6; cursor: not-allowed; }

.reg-success { max-width: 500px; margin: 0 auto; background: #0f172a; border: 1px solid rgba(34,197,94,0.3); border-radius: 16px; padding: 2rem; text-align: center; }
.success-icon { font-size: 3rem; margin-bottom: 0.75rem; }
.reg-success h3 { color: #4ade80; margin: 0 0 0.5rem; }
.reg-success p { color: #94a3b8; font-size: 0.9rem; }
.link-box { display: flex; gap: 0.5rem; align-items: center; background: #1e293b; border-radius: 8px; padding: 0.6rem 0.9rem; margin: 0.75rem 0; }
.aff-link { flex: 1; font-size: 0.82rem; color: #60a5fa; word-break: break-all; }
.btn-copy { padding: 0.35rem 0.8rem; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: #94a3b8; cursor: pointer; font-size: 0.8rem; white-space: nowrap; }
.btn-copy:hover { border-color: #60a5fa; color: #60a5fa; }
.link-hint { font-size: 0.82rem; color: #64748b; }
.link-hint a { color: #60a5fa; }

/* Materialien */
.materials-section { padding: 3rem 0; }
.materials-section h2 { font-size: 1.75rem; font-weight: 700; margin: 0 0 1.5rem; text-align: center; }
.materials-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; }
.material-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 1.25rem; }
.mat-icon { font-size: 1.75rem; margin-bottom: 0.5rem; }
.material-card h3 { margin: 0 0 0.75rem; color: #e2e8f0; font-size: 0.95rem; }
.code-box { background: #020817; border: 1px solid #1e293b; border-radius: 8px; padding: 0.6rem 0.75rem; font-size: 0.75rem; color: #94a3b8; margin-bottom: 0.75rem; word-break: break-all; line-height: 1.5; min-height: 60px; white-space: pre-wrap; }
.btn-sm { padding: 0.35rem 0.8rem; border-radius: 6px; border: 1px solid #334155; background: transparent; color: #94a3b8; cursor: pointer; font-size: 0.82rem; }
.btn-sm:hover { border-color: #60a5fa; color: #e2e8f0; }

/* FAQ */
.aff-faq { padding: 2rem 0; max-width: 680px; margin: 0 auto; }
.aff-faq h2 { font-size: 1.5rem; font-weight: 700; margin: 0 0 1.5rem; }
.faq-item { border-bottom: 1px solid #1e293b; padding: 1rem 0; }
.faq-item strong { color: #e2e8f0; font-size: 0.95rem; }
.faq-item p { color: #94a3b8; font-size: 0.875rem; margin: 0.4rem 0 0; line-height: 1.6; }

@media (max-width: 600px) {
  .aff-hero h1 { font-size: 1.9rem; }
  .steps { flex-direction: column; }
  .step-arrow { transform: rotate(90deg); }
}
</style>
