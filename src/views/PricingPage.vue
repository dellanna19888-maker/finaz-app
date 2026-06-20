<template>
  <div class="pricing-wrap">
    <div class="pricing-header">
      <RouterLink to="/" class="back-link">← Zurück</RouterLink>
      <h1>Preise & Pläne</h1>
      <p class="sub">Starte kostenlos · sicher bezahlen über Digistore24 · keine versteckten Kosten</p>
      <div v-if="routeSuccess" class="banner success">🎉 Zahlung erfolgreich! Du erhältst eine Bestätigungs-E-Mail von Digistore24.</div>
      <div v-if="routeCancel" class="banner warn">Zahlung abgebrochen. Du kannst jederzeit upgraden.</div>
    </div>

    <!-- Vertrauens-Badges -->
    <div class="trust-row">
      <div class="trust-badge">🔒 SSL-verschlüsselt</div>
      <div class="trust-badge">🇩🇪 Zahlung via Digistore24</div>
      <div class="trust-badge">💳 Kreditkarte, PayPal, Sofort</div>
      <div class="trust-badge">↩ 14 Tage Rückgabe</div>
    </div>

    <div class="plans-grid">
      <div v-for="p in plans" :key="p.id" :class="['plan-card', { popular: p.popular }]">
        <div v-if="p.popular" class="popular-tag">⭐ Empfohlen</div>
        <div class="plan-icon">{{ p.icon }}</div>
        <h2 class="plan-name">{{ p.name }}</h2>
        <div class="plan-price">{{ p.price }}<span>{{ p.priceNote }}</span></div>
        <p class="plan-desc">{{ p.desc }}</p>
        <ul class="plan-features">
          <li v-for="f in p.features" :key="f" :class="{ miss: f.startsWith('❌') }">{{ f }}</li>
        </ul>
        <a
          v-if="p.dsLink"
          :href="p.dsLink"
          target="_blank"
          :class="['btn-buy', { primary: p.popular }]"
        >
          {{ p.id === 'free' ? 'Kostenlos starten →' : 'Jetzt kaufen bei Digistore24 →' }}
        </a>
        <RouterLink v-else-if="p.id === 'free'" to="/app" class="btn-buy">Kostenlos starten →</RouterLink>
        <a v-else href="mailto:kontakt@securehub.de" class="btn-buy">Kontakt aufnehmen</a>
      </div>
    </div>

    <!-- Digistore24 Erklärung -->
    <div class="ds-info">
      <div class="ds-logo">🛒</div>
      <div>
        <strong>Sichere Zahlung über Digistore24</strong>
        <p>Digistore24 ist Deutschlands führende Zahlungsplattform für digitale Produkte. Du bezahlst sicher per Kreditkarte, PayPal, Sofortüberweisung oder Klarna. Nach der Zahlung erhältst du sofort Zugang per E-Mail.</p>
      </div>
    </div>

    <!-- FAQ -->
    <div class="faq">
      <h2>Häufige Fragen</h2>
      <div v-for="q in faqs" :key="q.q" class="faq-item">
        <strong>{{ q.q }}</strong>
        <p>{{ q.a }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
const route = useRoute()
const routeSuccess = computed(() => route.query.success === 'true')
const routeCancel = computed(() => route.query.cancel === 'true')

// Digistore24 Produkt-IDs in .env hinterlegen:
// VITE_DS24_PRO_LINK=https://www.digistore24.com/product/DEINE_ID
// VITE_DS24_BUSINESS_LINK=https://www.digistore24.com/product/DEINE_ID
const proLink = import.meta.env.VITE_DS24_PRO_LINK || ''
const businessLink = import.meta.env.VITE_DS24_BUSINESS_LINK || ''

const plans = [
  {
    id: 'free', icon: '🆓', name: 'Free', price: '0€', priceNote: '/Monat',
    desc: 'Perfekt zum Ausprobieren',
    popular: false, dsLink: '',
    features: ['✅ 3 Scans pro Tag', '✅ 1 Server im Monitor', '✅ Basis-Bericht', '✅ KI-Assistent (limitiert)', '❌ PDF-Export', '❌ Unbegrenzte Scans', '❌ E-Mail-Berichte'],
  },
  {
    id: 'pro', icon: '⚡', name: 'Pro', price: '19€', priceNote: '/Monat',
    desc: 'Für Entwickler & Freelancer',
    popular: true, dsLink: proLink,
    features: ['✅ Unbegrenzte Scans', '✅ 10 Server im Monitor', '✅ PDF-Export', '✅ Wöchentliche E-Mail-Berichte', '✅ 30 Tage Scan-Historie', '✅ Vollständiger KI-Assistent', '✅ Prioritäts-Support'],
  },
  {
    id: 'business', icon: '🏢', name: 'Business', price: '49€', priceNote: '/Monat',
    desc: 'Für Teams und Agenturen',
    popular: false, dsLink: businessLink,
    features: ['✅ Alles aus Pro', '✅ 50 Server im Monitor', '✅ API-Zugang', '✅ White-Label-Option', '✅ 5 Teammitglieder', '✅ 90 Tage Historie', '✅ Dedizierter Support'],
  },
  {
    id: 'enterprise', icon: '🔐', name: 'Enterprise', price: 'Auf Anfrage', priceNote: '',
    desc: 'Für große Unternehmen',
    popular: false, dsLink: '',
    features: ['✅ Alles aus Business', '✅ Unbegrenzte Server', '✅ SSO / SAML', '✅ SLA-Garantie', '✅ On-Premise-Option', '✅ 24/7 Support'],
  },
]

const faqs = [
  { q: 'Wie funktioniert die Zahlung?', a: 'Du wirst zu Digistore24 weitergeleitet – Deutschlands führende Plattform für digitale Produkte. Dort kannst du per Kreditkarte, PayPal, Sofortüberweisung oder Klarna zahlen.' },
  { q: 'Wann bekomme ich Zugang?', a: 'Sofort nach der Zahlung. Du erhältst eine Bestätigungs-E-Mail von Digistore24 mit deinen Zugangsdaten.' },
  { q: 'Kann ich kündigen?', a: 'Ja, jederzeit direkt über Digistore24. Kein Anruf nötig, alles online.' },
  { q: 'Gibt es eine Geld-zurück-Garantie?', a: 'Ja! 14 Tage Geld-zurück-Garantie ohne Angabe von Gründen – über Digistore24 Standard.' },
  { q: 'Welche Zahlungsmethoden?', a: 'Kreditkarte (Visa, Mastercard), PayPal, Sofortüberweisung, Klarna, Lastschrift.' },
]
</script>

<style scoped>
.pricing-wrap { max-width: 1100px; margin: 0 auto; padding: 2rem 1.5rem; }
.pricing-header { text-align: center; margin-bottom: 1.5rem; }
.back-link { font-size: 0.85rem; color: #64748b; text-decoration: none; display: inline-block; margin-bottom: 1rem; }
.back-link:hover { color: #94a3b8; }
.pricing-header h1 { font-size: 2.25rem; font-weight: 700; margin: 0 0 0.5rem; }
.sub { color: #94a3b8; margin: 0; }
.banner { padding: 0.75rem 1.25rem; border-radius: 10px; margin-top: 1rem; font-size: 0.9rem; }
.banner.success { background: rgba(74,222,128,0.15); border: 1px solid rgba(74,222,128,0.3); color: #4ade80; }
.banner.warn { background: rgba(251,191,36,0.15); border: 1px solid rgba(251,191,36,0.3); color: #fbbf24; }

/* Trust Badges */
.trust-row { display: flex; justify-content: center; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 2.5rem; }
.trust-badge { padding: 0.35rem 0.9rem; background: #0f172a; border: 1px solid #1e293b; border-radius: 999px; font-size: 0.82rem; color: #94a3b8; }

/* Plans */
.plans-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 1.25rem; margin-bottom: 2.5rem; }
.plan-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 16px; padding: 1.75rem; position: relative; transition: border-color 0.2s; }
.plan-card.popular { border-color: #3b82f6; background: linear-gradient(180deg, rgba(59,130,246,0.05), #0f172a); }
.popular-tag { position: absolute; top: -13px; left: 50%; transform: translateX(-50%); background: #3b82f6; color: #fff; padding: 0.2rem 0.9rem; border-radius: 999px; font-size: 0.78rem; white-space: nowrap; }
.plan-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.plan-name { font-size: 1.25rem; font-weight: 700; color: #e2e8f0; margin: 0 0 0.25rem; }
.plan-price { font-size: 2.25rem; font-weight: 800; color: #e2e8f0; margin-bottom: 0.25rem; }
.plan-price span { font-size: 1rem; color: #64748b; font-weight: 400; }
.plan-desc { color: #64748b; font-size: 0.82rem; margin: 0 0 1.25rem; }
.plan-features { list-style: none; padding: 0; margin: 0 0 1.5rem; display: flex; flex-direction: column; gap: 0.45rem; }
.plan-features li { font-size: 0.85rem; color: #cbd5e1; }
.plan-features li.miss { color: #475569; }
.btn-buy { display: block; text-align: center; padding: 0.75rem 1rem; border-radius: 10px; border: 1px solid #334155; color: #e2e8f0; font-weight: 600; font-size: 0.9rem; text-decoration: none; cursor: pointer; background: transparent; transition: all 0.2s; }
.btn-buy:hover { border-color: #60a5fa; }
.btn-buy.primary { background: #3b82f6; border-color: #3b82f6; color: #fff; }
.btn-buy.primary:hover { background: #2563eb; }

/* Digistore24 Info */
.ds-info { display: flex; gap: 1.25rem; align-items: flex-start; background: #0f172a; border: 1px solid rgba(59,130,246,0.2); border-radius: 12px; padding: 1.5rem; margin-bottom: 2.5rem; }
.ds-logo { font-size: 2.5rem; flex-shrink: 0; }
.ds-info strong { color: #e2e8f0; display: block; margin-bottom: 0.4rem; }
.ds-info p { color: #94a3b8; font-size: 0.88rem; margin: 0; line-height: 1.6; }

/* FAQ */
.faq { max-width: 680px; margin: 0 auto; }
.faq h2 { font-size: 1.5rem; font-weight: 700; margin: 0 0 1.5rem; }
.faq-item { border-bottom: 1px solid #1e293b; padding: 1rem 0; }
.faq-item strong { color: #e2e8f0; font-size: 0.95rem; }
.faq-item p { color: #94a3b8; font-size: 0.875rem; margin: 0.4rem 0 0; line-height: 1.6; }
</style>
