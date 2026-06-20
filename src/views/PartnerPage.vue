<template>
  <div class="partner-wrap">

    <!-- Nav -->
    <header class="p-nav">
      <RouterLink to="/" class="p-brand">🛡️ <strong>SecureHub</strong></RouterLink>
      <div class="p-nav-links">
        <RouterLink to="/pricing">Preise</RouterLink>
        <RouterLink to="/affiliate">Affiliate</RouterLink>
        <a href="#register" class="btn-partner-nav">Partner werden →</a>
      </div>
    </header>

    <!-- Hero -->
    <section class="p-hero">
      <div class="p-badge">🤝 Vertriebspartner-Programm</div>
      <h1>Biete deinen Kunden<br><span class="highlight">Security als Service</span><br>– und verdiene dauerhaft</h1>
      <p class="p-sub">Du bist Web-Agentur, IT-Freelancer oder Berater? Empfiehl SecureHub an deine Kunden und kassiere <strong>30% Provision</strong> – jeden Monat, solange der Kunde zahlt. Kein Aufwand, keine Infrastruktur.</p>
      <div class="hero-ctas">
        <a href="#register" class="btn-hero-green">Jetzt Partner werden – kostenlos →</a>
        <a href="#how" class="btn-hero-ghost">Wie es funktioniert</a>
      </div>
      <div class="hero-stats">
        <div class="h-stat"><strong>30%</strong><span>Provision monatlich</span></div>
        <div class="h-div"></div>
        <div class="h-stat"><strong>90 Tage</strong><span>Cookie-Laufzeit</span></div>
        <div class="h-div"></div>
        <div class="h-stat"><strong>0€</strong><span>Kosten für dich</span></div>
        <div class="h-div"></div>
        <div class="h-stat"><strong>Live</strong><span>Dashboard & Stats</span></div>
      </div>
    </section>

    <!-- Für wen -->
    <section class="target-section">
      <h2>Für wen ist dieses Programm?</h2>
      <div class="target-grid">
        <div class="target-card active">
          <div class="t-icon">🏢</div>
          <h3>Web-Agenturen</h3>
          <p>Du baust Websites für Kunden – biete Security-Monitoring als monatlichen Service dazu.</p>
          <div class="t-example">5 Kunden × 19€ × 30% = <strong>28,50€/Monat passiv</strong></div>
        </div>
        <div class="target-card">
          <div class="t-icon">💻</div>
          <h3>IT-Freelancer</h3>
          <p>Du wartest Server und Infrastruktur – SecureHub ergänzt dein Portfolio perfekt.</p>
          <div class="t-example">10 Kunden × 19€ × 30% = <strong>57€/Monat passiv</strong></div>
        </div>
        <div class="target-card">
          <div class="t-icon">📊</div>
          <h3>SEO & Marketing Berater</h3>
          <p>Security-Score beeinflusst Google Rankings – ein perfektes Upsell-Argument.</p>
          <div class="t-example">20 Kunden × 19€ × 30% = <strong>114€/Monat passiv</strong></div>
        </div>
        <div class="target-card">
          <div class="t-icon">🎓</div>
          <h3>IT-Ausbilder & Coaches</h3>
          <p>Du bildest Webentwickler aus – zeige Security-Best-Practices mit echtem Tool.</p>
          <div class="t-example">50 Kunden × 19€ × 30% = <strong>285€/Monat passiv</strong></div>
        </div>
      </div>
    </section>

    <!-- Wie es funktioniert -->
    <section id="how" class="how-section">
      <h2>So funktioniert es in 3 Schritten</h2>
      <div class="how-steps">
        <div class="how-step">
          <div class="how-num">1</div>
          <h3>Registrieren & Link erhalten</h3>
          <p>Kostenlos anmelden. Du bekommst sofort deinen persönlichen Partner-Link und dein Dashboard.</p>
        </div>
        <div class="how-arrow">→</div>
        <div class="how-step">
          <div class="how-num">2</div>
          <h3>Kunden ansprechen</h3>
          <p>Nutze unsere fertigen E-Mail-Vorlagen und Pitch-Skripte weiter unten. Alles copy-paste fertig.</p>
        </div>
        <div class="how-arrow">→</div>
        <div class="how-step">
          <div class="how-num">3</div>
          <h3>Monatlich verdienen</h3>
          <p>Sobald ein Kunde über deinen Link kauft, fließt die Provision jeden Monat automatisch.</p>
        </div>
      </div>
    </section>

    <!-- Verdienst-Rechner -->
    <section class="calc-section">
      <h2>💰 Was kannst du verdienen?</h2>
      <p class="section-sub">Berechne dein monatliches Passiveinkommen</p>
      <div class="calc-card">
        <div class="calc-inputs">
          <div class="calc-field">
            <label>Anzahl deiner Kunden</label>
            <input v-model.number="clients" type="range" min="1" max="100" class="slider" />
            <span class="calc-num-label">{{ clients }} Kunden</span>
          </div>
          <div class="calc-field">
            <label>Anteil die kaufen</label>
            <input v-model.number="convRate" type="range" min="5" max="80" step="5" class="slider" />
            <span class="calc-num-label">{{ convRate }}%</span>
          </div>
          <div class="calc-field">
            <label>Durchschnittlicher Plan</label>
            <div class="plan-toggle">
              <button :class="['plan-btn', avgPrice === 19 ? 'active' : '']" @click="avgPrice = 19">Pro 19€</button>
              <button :class="['plan-btn', avgPrice === 49 ? 'active' : '']" @click="avgPrice = 49">Business 49€</button>
            </div>
          </div>
        </div>
        <div class="calc-result">
          <div class="result-row">
            <span class="result-label">Kunden die kaufen:</span>
            <span class="result-val">{{ buyingClients }}</span>
          </div>
          <div class="result-row">
            <span class="result-label">Deine Provision (30%):</span>
            <span class="result-val green">{{ monthlyEarnings }}€ / Monat</span>
          </div>
          <div class="result-row">
            <span class="result-label">Pro Jahr:</span>
            <span class="result-val green">{{ yearlyEarnings }}€</span>
          </div>
          <div class="result-note">⬆ Wächst automatisch mit jedem neuen Kunden</div>
        </div>
      </div>
    </section>

    <!-- Partner-Kit: Fertige Vorlagen -->
    <section class="kit-section">
      <h2>📦 Dein Partner-Kit</h2>
      <p class="section-sub">Copy-Paste fertig – sofort einsatzbereit</p>

      <div class="kit-tabs">
        <button v-for="t in kitTabs" :key="t.id" :class="['kit-tab', { active: activeKit === t.id }]" @click="activeKit = t.id">{{ t.label }}</button>
      </div>

      <!-- E-Mail Vorlage -->
      <div v-if="activeKit === 'email'" class="kit-box">
        <div class="kit-header">
          <span>📧 E-Mail an Kunden</span>
          <button class="btn-copy-kit" @click="copy(emailTemplate2)">📋 Kopieren</button>
        </div>
        <pre class="kit-text">{{ emailTemplate2 }}</pre>
      </div>

      <!-- LinkedIn Nachricht -->
      <div v-if="activeKit === 'linkedin'" class="kit-box">
        <div class="kit-header">
          <span>💼 LinkedIn Nachricht</span>
          <button class="btn-copy-kit" @click="copy(linkedinTemplate)">📋 Kopieren</button>
        </div>
        <pre class="kit-text">{{ linkedinTemplate }}</pre>
      </div>

      <!-- Pitch Skript (Telefonat) -->
      <div v-if="activeKit === 'pitch'" class="kit-box">
        <div class="kit-header">
          <span>📞 Telefon-Pitch Skript</span>
          <button class="btn-copy-kit" @click="copy(pitchTemplate)">📋 Kopieren</button>
        </div>
        <pre class="kit-text">{{ pitchTemplate }}</pre>
      </div>

      <!-- WhatsApp -->
      <div v-if="activeKit === 'whatsapp'" class="kit-box">
        <div class="kit-header">
          <span>💬 WhatsApp / SMS Nachricht</span>
          <button class="btn-copy-kit" @click="copy(whatsappTemplate)">📋 Kopieren</button>
        </div>
        <pre class="kit-text">{{ whatsappTemplate }}</pre>
      </div>

      <div v-if="copied" class="copy-toast">✓ Kopiert!</div>
    </section>

    <!-- Was SecureHub bietet -->
    <section class="product-section">
      <h2>Was deine Kunden bekommen</h2>
      <p class="section-sub">Du verkaufst – wir liefern. Kein Aufwand für dich.</p>
      <div class="product-grid">
        <div class="product-item">
          <span class="p-emoji">🔍</span>
          <div><strong>Security Scanner</strong><br><span>7 Header-Checks, Note A+ bis F, sofort verständlich</span></div>
        </div>
        <div class="product-item">
          <span class="p-emoji">🔐</span>
          <div><strong>SSL-Zertifikat-Check</strong><br><span>Ablaufdatum, Warnung vor Ablauf, Aussteller</span></div>
        </div>
        <div class="product-item">
          <span class="p-emoji">📈</span>
          <div><strong>Score-Verlauf</strong><br><span>Zeigt ob Sicherheit besser oder schlechter wird</span></div>
        </div>
        <div class="product-item">
          <span class="p-emoji">🟢</span>
          <div><strong>Uptime-Monitor</strong><br><span>Sofort-Alert wenn Website offline geht</span></div>
        </div>
        <div class="product-item">
          <span class="p-emoji">🔧</span>
          <div><strong>Fix-Anleitungen</strong><br><span>Copy-Paste Code für Apache, Nginx, WordPress</span></div>
        </div>
        <div class="product-item">
          <span class="p-emoji">📧</span>
          <div><strong>Wöchentliche E-Mail-Berichte</strong><br><span>Automatisch, mit Trend-Vergleich zur Vorwoche</span></div>
        </div>
        <div class="product-item">
          <span class="p-emoji">🖥️</span>
          <div><strong>Server-Monitor</strong><br><span>CPU, RAM, Disk – Echtzeit mit Alarm</span></div>
        </div>
        <div class="product-item">
          <span class="p-emoji">🤖</span>
          <div><strong>KI-Assistent</strong><br><span>Analyse & Empfehlungen powered by Claude AI</span></div>
        </div>
      </div>
    </section>

    <!-- Registrierung -->
    <section id="register" class="reg-section">
      <div class="reg-card">
        <div class="reg-left">
          <h2>Jetzt Partner werden</h2>
          <p>Kostenlos · Sofortzugang · Keine Vertragslaufzeit</p>
          <ul class="reg-perks">
            <li>✅ 30% Provision auf jeden Verkauf</li>
            <li>✅ Dauerhaft – solange Kunde zahlt</li>
            <li>✅ Live-Dashboard mit allen Stats</li>
            <li>✅ Fertige Vorlagen & Partner-Kit</li>
            <li>✅ 90-Tage Cookie-Laufzeit</li>
            <li>✅ Auszahlung ab 20€</li>
          </ul>
        </div>
        <div class="reg-right">
          <div v-if="!registered" class="reg-form">
            <div class="reg-field">
              <label>Dein Name *</label>
              <input v-model="form.name" placeholder="Max Mustermann" />
            </div>
            <div class="reg-field">
              <label>E-Mail-Adresse *</label>
              <input v-model="form.email" type="email" placeholder="max@agentur.de" />
            </div>
            <div class="reg-field">
              <label>Website / Firma (optional)</label>
              <input v-model="form.website" placeholder="https://meine-agentur.de" />
            </div>
            <p v-if="regError" class="err-msg">⚠ {{ regError }}</p>
            <button class="btn-reg" :disabled="regLoading || !form.name || !form.email" @click="register">
              {{ regLoading ? 'Wird erstellt…' : 'Partner-Konto erstellen →' }}
            </button>
          </div>

          <div v-else class="reg-success">
            <div class="success-icon">🎉</div>
            <h3>Willkommen als Partner!</h3>
            <p>Dein persönlicher Partner-Link:</p>
            <div class="link-box">
              <span class="aff-link">{{ partnerLink }}</span>
              <button class="btn-copy-small" @click="copyLink">{{ copiedLink ? '✓' : '📋' }}</button>
            </div>
            <p class="link-code">Code: <strong>{{ affiliateCode }}</strong></p>
            <RouterLink to="/affiliate/portal" class="btn-dashboard">Dashboard öffnen →</RouterLink>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="p-footer">
      <div>🛡️ SecureHub · <RouterLink to="/">Startseite</RouterLink> · <RouterLink to="/pricing">Preise</RouterLink> · <RouterLink to="/affiliate">Affiliate</RouterLink></div>
      <div class="p-footer-copy">© 2025 SecureHub · Alle Rechte vorbehalten</div>
    </footer>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// Rechner
const clients = ref(20)
const convRate = ref(30)
const avgPrice = ref(19)
const buyingClients = computed(() => Math.round(clients.value * convRate.value / 100))
const monthlyEarnings = computed(() => +(buyingClients.value * avgPrice.value * 0.3).toFixed(2))
const yearlyEarnings = computed(() => +(monthlyEarnings.value * 12).toFixed(2))

// Kit Tabs
const kitTabs = [
  { id: 'email', label: '📧 E-Mail' },
  { id: 'linkedin', label: '💼 LinkedIn' },
  { id: 'pitch', label: '📞 Telefon-Pitch' },
  { id: 'whatsapp', label: '💬 WhatsApp' },
]
const activeKit = ref('email')
const copied = ref(false)

const emailTemplate = `Betreff: Kostenloser Security-Check für Ihre Website

Sehr geehrte/r [Name],

im Rahmen meiner Arbeit als [Web-Agentur / IT-Berater] führe ich
regelmäßig Sicherheitsüberprüfungen für meine Kunden durch.

Ich habe Ihre Website kurz geprüft und möchte Ihnen ein Tool
vorstellen, das ich für meine Kunden einsetze:

🛡️ SecureHub – Automatischer Security-Monitor

Das Tool prüft wöchentlich:
✅ 7 HTTP-Sicherheitsheader (Note A+ bis F)
✅ SSL-Zertifikat (Ablaufdatum, Warnung vor Ablauf)
✅ Uptime (sofortige Benachrichtigung wenn Website offline)
✅ Score-Verlauf (wird Ihre Seite sicherer oder unsicherer?)

Kosten: ab 19€/Monat – günstiger als eine einzige Sicherheitslücke.

👉 Kostenlos testen: [IHR PARTNER-LINK]

Ich stehe gerne für Rückfragen zur Verfügung.

Mit freundlichen Grüßen,
[Ihr Name]`

const linkedinTemplate = `Hallo [Name],

ich bin [Titel] und helfe [Zielgruppe] dabei, ihre Online-Präsenz
zu schützen.

Ich nutze für meine Kunden SecureHub – ein Security-Monitoring-Tool
das automatisch prüft ob eine Website Sicherheitslücken hat, das
SSL-Zertifikat bald abläuft oder die Seite offline ist.

Für eine KMU-Website ist das Gold wert – kostet 19€/Monat und
erspart teure Notfall-Einsätze.

Hätten Sie Interesse an einer kurzen Demo? Ich zeige Ihnen gerne
in 10 Minuten wie es funktioniert.

Viele Grüße,
[Ihr Name]

🔗 Mehr Infos: [IHR PARTNER-LINK]`

const pitchTemplate = `📞 TELEFON-PITCH SKRIPT (ca. 3 Minuten)

EINSTIEG:
"Guten Tag, [Name]. Ich bin [Ihr Name] von [Firma].
Ich betreue ja Ihre Website – darf ich Ihnen kurz etwas zeigen
das ich bei meinen Kunden einführe?"

PROBLEM:
"Wussten Sie, dass über 80% aller Websites kritische
Sicherheitsheader vermissen? Das klingt technisch, aber im
Klartext bedeutet es: Hacker haben leichteres Spiel, und Google
bewertet Ihre Seite schlechter."

LÖSUNG:
"Ich nutze jetzt SecureHub für meine Kunden. Das Tool scannt
Ihre Website jede Woche automatisch, bewertet sie wie in der
Schule – A+ bis F – und schickt Ihnen einen Bericht per E-Mail.
Wenn Ihre Website offline geht, bekommen Sie sofort eine Meldung."

PREIS:
"Das kostet 19€ im Monat – weniger als ein Mittagessen. Dafür
haben Sie jede Woche die Gewissheit dass alles in Ordnung ist."

ABSCHLUSS:
"Soll ich das für Sie einrichten? Sie können es 14 Tage kostenlos
testen – kein Risiko, keine Kreditkarte nötig."

[IHR PARTNER-LINK]`

const whatsappTemplate = `Hallo [Name] 👋

kurze Frage: Weißt du ob deine Website ein aktuelles SSL-Zertifikat
hat und die wichtigsten Sicherheitsheader gesetzt sind?

Ich nutze für meine Kunden gerade SecureHub – das scannt die
Website automatisch jede Woche und schickt einen Bericht.
Sehr praktisch, besonders der Uptime-Alert wenn die Seite mal
offline ist.

Kostet 19€/Monat, du kannst kostenlos starten:
👉 [DEIN PARTNER-LINK]

Sag mir Bescheid wenn du Fragen hast 🙂`

async function copy(text: string) {
  await navigator.clipboard.writeText(text)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

// Registrierung
const form = ref({ name: '', email: '', website: '' })
const regLoading = ref(false)
const regError = ref('')
const registered = ref(false)
const affiliateCode = ref('')
const copiedLink = ref(false)

const partnerLink = computed(() =>
  affiliateCode.value ? `${window.location.origin}/?ref=${affiliateCode.value}` : ''
)

// Templates aktualisieren wenn Link vorhanden
const emailTemplate2 = computed(() => emailTemplate.replace('[IHR PARTNER-LINK]', partnerLink.value || '[IHR PARTNER-LINK]'))

async function register() {
  regLoading.value = true; regError.value = ''
  try {
    const res = await fetch('/api/affiliate/register', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.error || 'Registrierung fehlgeschlagen')
    affiliateCode.value = data.code
    registered.value = true
    localStorage.setItem('finaz_aff_code', data.code)
    localStorage.setItem('finaz_aff_email', form.value.email)
  } catch (e: unknown) { regError.value = (e as Error).message }
  finally { regLoading.value = false }
}

async function copyLink() {
  await navigator.clipboard.writeText(partnerLink.value)
  copiedLink.value = true
  setTimeout(() => { copiedLink.value = false }, 2000)
}
</script>

<style scoped>
.partner-wrap { min-height: 100vh; background: #020817; color: #e2e8f0; }

/* Nav */
.p-nav { display: flex; align-items: center; justify-content: space-between; padding: 1rem 2rem; position: sticky; top: 0; z-index: 100; background: rgba(2,8,23,0.95); backdrop-filter: blur(12px); border-bottom: 1px solid rgba(255,255,255,0.06); }
.p-brand { font-size: 1.2rem; color: #e2e8f0; text-decoration: none; }
.p-nav-links { display: flex; align-items: center; gap: 1.5rem; }
.p-nav-links a { color: #94a3b8; text-decoration: none; font-size: 0.9rem; }
.p-nav-links a:hover { color: #e2e8f0; }
.btn-partner-nav { padding: 0.4rem 1rem; border-radius: 8px; background: #22c55e; color: #000 !important; font-weight: 600; font-size: 0.88rem; }
.btn-partner-nav:hover { background: #16a34a; }

/* Hero */
.p-hero { text-align: center; padding: 5rem 2rem 4rem; background: radial-gradient(ellipse 80% 50% at 50% -10%, rgba(34,197,94,0.1), transparent); }
.p-badge { display: inline-block; padding: 0.35rem 1rem; border-radius: 999px; background: rgba(34,197,94,0.15); border: 1px solid rgba(34,197,94,0.3); color: #4ade80; font-size: 0.85rem; margin-bottom: 1.5rem; }
.p-hero h1 { font-size: 3.2rem; font-weight: 800; line-height: 1.15; margin: 0 0 1.25rem; }
.highlight { background: linear-gradient(135deg, #22c55e, #4ade80); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.p-sub { font-size: 1.1rem; color: #94a3b8; max-width: 620px; margin: 0 auto 2.5rem; line-height: 1.7; }
.hero-ctas { display: flex; gap: 1rem; justify-content: center; margin-bottom: 3rem; flex-wrap: wrap; }
.btn-hero-green { padding: 0.9rem 2.2rem; border-radius: 10px; background: #22c55e; color: #000; text-decoration: none; font-weight: 700; font-size: 1rem; transition: all 0.2s; }
.btn-hero-green:hover { background: #16a34a; transform: translateY(-1px); }
.btn-hero-ghost { padding: 0.9rem 2.2rem; border-radius: 10px; border: 1px solid #334155; color: #94a3b8; text-decoration: none; font-size: 1rem; transition: all 0.2s; }
.btn-hero-ghost:hover { border-color: #4ade80; color: #e2e8f0; }
.hero-stats { display: flex; align-items: center; justify-content: center; gap: 2rem; flex-wrap: wrap; }
.h-stat { text-align: center; }
.h-stat strong { display: block; font-size: 1.6rem; font-weight: 800; color: #4ade80; }
.h-stat span { font-size: 0.78rem; color: #64748b; }
.h-div { width: 1px; height: 32px; background: #1e293b; }

/* Target */
.target-section { padding: 5rem 2rem; text-align: center; }
.target-section h2 { font-size: 2rem; font-weight: 700; margin: 0 0 2.5rem; }
.target-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.25rem; max-width: 1000px; margin: 0 auto; }
.target-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 14px; padding: 1.75rem; text-align: left; transition: border-color 0.2s; }
.target-card.active { border-color: rgba(34,197,94,0.4); }
.target-card:hover { border-color: #334155; }
.t-icon { font-size: 2rem; margin-bottom: 0.75rem; }
.target-card h3 { font-size: 1.05rem; font-weight: 700; color: #e2e8f0; margin: 0 0 0.5rem; }
.target-card p { color: #94a3b8; font-size: 0.85rem; margin: 0 0 1rem; line-height: 1.5; }
.t-example { background: rgba(34,197,94,0.08); border: 1px solid rgba(34,197,94,0.2); border-radius: 8px; padding: 0.5rem 0.75rem; font-size: 0.82rem; color: #86efac; }
.t-example strong { color: #4ade80; }

/* How */
.how-section { padding: 5rem 2rem; text-align: center; background: #0a1628; }
.how-section h2 { font-size: 2rem; font-weight: 700; margin: 0 0 3rem; }
.how-steps { display: flex; align-items: center; justify-content: center; gap: 1.5rem; flex-wrap: wrap; max-width: 900px; margin: 0 auto; }
.how-step { background: #0f172a; border: 1px solid #1e293b; border-radius: 14px; padding: 2rem; max-width: 220px; text-align: left; }
.how-num { width: 40px; height: 40px; border-radius: 50%; background: rgba(34,197,94,0.2); color: #4ade80; font-weight: 700; font-size: 1.2rem; display: flex; align-items: center; justify-content: center; margin-bottom: 1rem; }
.how-step h3 { font-size: 1rem; color: #e2e8f0; margin: 0 0 0.5rem; }
.how-step p { font-size: 0.82rem; color: #94a3b8; margin: 0; line-height: 1.5; }
.how-arrow { font-size: 1.75rem; color: #334155; }

/* Rechner */
.calc-section { padding: 5rem 2rem; text-align: center; }
.calc-section h2 { font-size: 2rem; font-weight: 700; margin: 0 0 0.5rem; }
.section-sub { color: #94a3b8; margin: 0 0 2.5rem; }
.calc-card { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; max-width: 800px; margin: 0 auto; background: #0f172a; border: 1px solid #1e293b; border-radius: 16px; padding: 2rem; }
.calc-inputs { display: flex; flex-direction: column; gap: 1.5rem; }
.calc-field label { display: block; font-size: 0.85rem; color: #94a3b8; margin-bottom: 0.5rem; }
.slider { width: 100%; accent-color: #22c55e; }
.calc-num-label { font-size: 0.9rem; color: #4ade80; font-weight: 600; }
.plan-toggle { display: flex; gap: 0.5rem; margin-top: 0.5rem; }
.plan-btn { padding: 0.4rem 1rem; border-radius: 8px; border: 1px solid #334155; background: transparent; color: #64748b; cursor: pointer; font-size: 0.85rem; transition: all 0.2s; }
.plan-btn.active { background: rgba(34,197,94,0.15); border-color: #22c55e; color: #4ade80; }
.calc-result { border-left: 1px solid #1e293b; padding-left: 2rem; display: flex; flex-direction: column; gap: 1rem; justify-content: center; }
.result-row { display: flex; justify-content: space-between; align-items: center; padding: 0.6rem 0; border-bottom: 1px solid #0f172a; }
.result-label { font-size: 0.85rem; color: #64748b; }
.result-val { font-weight: 700; color: #e2e8f0; font-size: 0.95rem; }
.result-val.green { color: #4ade80; font-size: 1.2rem; }
.result-note { font-size: 0.78rem; color: #22c55e; background: rgba(34,197,94,0.08); padding: 0.5rem 0.75rem; border-radius: 8px; text-align: center; }

/* Partner Kit */
.kit-section { padding: 5rem 2rem; max-width: 860px; margin: 0 auto; }
.kit-section h2 { font-size: 2rem; font-weight: 700; margin: 0 0 0.5rem; text-align: center; }
.kit-tabs { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1.25rem; }
.kit-tab { padding: 0.5rem 1.1rem; border-radius: 8px; border: 1px solid #334155; background: transparent; color: #64748b; cursor: pointer; font-size: 0.88rem; transition: all 0.2s; }
.kit-tab.active { background: #1e293b; border-color: #475569; color: #e2e8f0; }
.kit-box { background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; overflow: hidden; position: relative; }
.kit-header { display: flex; align-items: center; justify-content: space-between; padding: 0.75rem 1.1rem; background: #1e293b; font-size: 0.88rem; color: #94a3b8; }
.btn-copy-kit { padding: 0.3rem 0.8rem; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: #94a3b8; cursor: pointer; font-size: 0.8rem; }
.btn-copy-kit:hover { color: #e2e8f0; border-color: #4ade80; }
.kit-text { margin: 0; padding: 1.25rem; font-size: 0.83rem; color: #94a3b8; white-space: pre-wrap; word-break: break-word; line-height: 1.7; font-family: -apple-system, Arial, sans-serif; }
.copy-toast { position: fixed; bottom: 2rem; right: 2rem; background: #22c55e; color: #000; padding: 0.6rem 1.25rem; border-radius: 8px; font-weight: 600; font-size: 0.9rem; z-index: 999; }

/* Produkt-Features */
.product-section { padding: 5rem 2rem; text-align: center; background: #0a1628; }
.product-section h2 { font-size: 2rem; font-weight: 700; margin: 0 0 0.5rem; }
.product-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 0.85rem; max-width: 860px; margin: 2rem auto 0; }
.product-item { display: flex; align-items: flex-start; gap: 1rem; background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 1rem 1.1rem; text-align: left; }
.p-emoji { font-size: 1.5rem; flex-shrink: 0; }
.product-item strong { display: block; color: #e2e8f0; font-size: 0.88rem; margin-bottom: 0.2rem; }
.product-item span { color: #64748b; font-size: 0.8rem; line-height: 1.4; }

/* Registrierung */
.reg-section { padding: 5rem 2rem; }
.reg-card { display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; max-width: 860px; margin: 0 auto; background: #0f172a; border: 1px solid rgba(34,197,94,0.2); border-radius: 20px; padding: 2.5rem; }
.reg-left h2 { font-size: 1.75rem; font-weight: 700; margin: 0 0 0.4rem; }
.reg-left p { color: #64748b; font-size: 0.88rem; margin: 0 0 1.5rem; }
.reg-perks { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.6rem; }
.reg-perks li { font-size: 0.88rem; color: #cbd5e1; }
.reg-field { margin-bottom: 1rem; }
.reg-field label { display: block; font-size: 0.83rem; color: #94a3b8; margin-bottom: 0.35rem; }
.reg-field input { width: 100%; padding: 0.65rem 0.9rem; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: #e2e8f0; font-size: 0.95rem; box-sizing: border-box; }
.reg-field input:focus { outline: none; border-color: #22c55e; }
.err-msg { color: #f87171; font-size: 0.83rem; background: rgba(248,113,113,0.1); padding: 0.5rem 0.75rem; border-radius: 6px; margin-bottom: 0.75rem; }
.btn-reg { width: 100%; padding: 0.85rem; border-radius: 10px; border: none; background: #22c55e; color: #000; font-size: 1rem; font-weight: 700; cursor: pointer; transition: background 0.2s; }
.btn-reg:hover:not(:disabled) { background: #16a34a; }
.btn-reg:disabled { opacity: 0.5; cursor: not-allowed; }
.reg-success { text-align: center; }
.success-icon { font-size: 3rem; margin-bottom: 0.5rem; }
.reg-success h3 { color: #4ade80; margin: 0 0 0.5rem; }
.reg-success p { color: #94a3b8; font-size: 0.88rem; margin: 0 0 0.5rem; }
.link-box { display: flex; align-items: center; gap: 0.5rem; background: #1e293b; border-radius: 8px; padding: 0.6rem 0.9rem; margin: 0.5rem 0; }
.aff-link { flex: 1; font-size: 0.8rem; color: #60a5fa; word-break: break-all; }
.btn-copy-small { padding: 0.3rem 0.6rem; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: #94a3b8; cursor: pointer; }
.link-code { font-size: 0.8rem; color: #64748b; margin: 0.25rem 0 1rem; }
.btn-dashboard { display: block; padding: 0.75rem 1rem; border-radius: 10px; background: #22c55e; color: #000; text-decoration: none; font-weight: 700; font-size: 0.95rem; text-align: center; }

/* Footer */
.p-footer { padding: 2rem; border-top: 1px solid #0f172a; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; color: #64748b; font-size: 0.82rem; }
.p-footer a { color: #64748b; text-decoration: none; }
.p-footer a:hover { color: #94a3b8; }

@media (max-width: 700px) {
  .p-hero h1 { font-size: 2rem; }
  .calc-card { grid-template-columns: 1fr; }
  .calc-result { border-left: none; border-top: 1px solid #1e293b; padding-left: 0; padding-top: 1.5rem; }
  .reg-card { grid-template-columns: 1fr; }
  .how-steps { flex-direction: column; }
  .how-arrow { transform: rotate(90deg); }
  .p-nav-links { display: none; }
}
</style>
