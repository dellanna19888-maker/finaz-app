<template>
  <div class="pricing-wrap">
    <div class="pricing-header">
      <RouterLink to="/" class="back-link">← Zurück</RouterLink>
      <h1>Preise & Pläne</h1>
      <p class="sub">Starte kostenlos · upgrade jederzeit · keine versteckten Kosten</p>

      <!-- Success/Cancel Banner -->
      <div v-if="routeSuccess" class="banner success">🎉 Zahlung erfolgreich! Dein Plan wurde aktiviert.</div>
      <div v-if="routeCancel" class="banner warn">Zahlung abgebrochen. Du kannst jederzeit upgraden.</div>
    </div>

    <div class="plans-grid">
      <div v-for="p in plans" :key="p.id" :class="['plan-card', { popular: p.popular, current: currentPlan === p.id }]">
        <div v-if="p.popular" class="popular-tag">⭐ Empfohlen</div>
        <div v-if="currentPlan === p.id" class="current-tag">✓ Aktuell</div>
        <div class="plan-icon">{{ p.icon }}</div>
        <h2 class="plan-name">{{ p.name }}</h2>
        <div class="plan-price">
          {{ p.price }}<span v-if="p.priceNote">{{ p.priceNote }}</span>
        </div>
        <p class="plan-desc">{{ p.desc }}</p>
        <ul class="plan-features">
          <li v-for="f in p.features" :key="f" :class="f.startsWith('❌') ? 'miss' : ''">{{ f }}</li>
        </ul>
        <button
          v-if="currentPlan !== p.id && p.id !== 'enterprise'"
          :class="['btn-plan', { primary: p.popular }]"
          :disabled="loading === p.id"
          @click="checkout(p)"
        >
          {{ loading === p.id ? '…' : p.id === 'free' ? 'Kostenlos starten' : `${p.name} wählen →` }}
        </button>
        <a v-if="p.id === 'enterprise'" href="mailto:sales@securehub.de" class="btn-plan">Kontakt aufnehmen</a>
        <span v-if="currentPlan === p.id" class="current-label">Dein aktueller Plan</span>
      </div>
    </div>

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
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const route = useRoute()
const loading = ref('')

const routeSuccess = computed(() => route.query.success === 'true')
const routeCancel = computed(() => route.query.cancel === 'true')
const currentPlan = computed(() => auth.plan)

const plans = [
  {
    id: 'free', icon: '🆓', name: 'Free', price: '0€', priceNote: '/Monat',
    desc: 'Perfekt zum Ausprobieren',
    popular: false,
    stripePriceId: null,
    features: [
      '✅ 3 Scans pro Tag',
      '✅ 1 Server im Monitor',
      '✅ Basis-Sicherheitsbericht',
      '✅ KI-Assistent (limitiert)',
      '❌ PDF-Export',
      '❌ Scan-Historie',
      '❌ API-Zugang',
    ],
  },
  {
    id: 'pro', icon: '⚡', name: 'Pro', price: '19€', priceNote: '/Monat',
    desc: 'Für professionelle Entwickler & Freelancer',
    popular: true,
    stripePriceId: import.meta.env.VITE_STRIPE_PRO_PRICE_ID || '',
    features: [
      '✅ Unbegrenzte Scans',
      '✅ 10 Server im Monitor',
      '✅ PDF-Export',
      '✅ 30 Tage Scan-Historie',
      '✅ Vollständiger KI-Assistent',
      '✅ Prioritäts-Support',
      '❌ API-Zugang',
    ],
  },
  {
    id: 'business', icon: '🏢', name: 'Business', price: '49€', priceNote: '/Monat',
    desc: 'Für Teams und Agenturen',
    popular: false,
    stripePriceId: import.meta.env.VITE_STRIPE_BUSINESS_PRICE_ID || '',
    features: [
      '✅ Alles aus Pro',
      '✅ 50 Server im Monitor',
      '✅ REST API-Zugang',
      '✅ White-Label-Option',
      '✅ 5 Teammitglieder',
      '✅ 90 Tage Historie',
      '✅ Dedizierter Support',
    ],
  },
  {
    id: 'enterprise', icon: '🔐', name: 'Enterprise', price: 'Auf Anfrage', priceNote: '',
    desc: 'Für große Unternehmen',
    popular: false,
    stripePriceId: null,
    features: [
      '✅ Alles aus Business',
      '✅ Unbegrenzte Server',
      '✅ SSO / SAML',
      '✅ SLA-Garantie',
      '✅ On-Premise-Option',
      '✅ Eigene Integrationen',
      '✅ 24/7 Support',
    ],
  },
]

const faqs = [
  { q: 'Kann ich jederzeit kündigen?', a: 'Ja, du kannst deinen Plan jederzeit im Kundenportal kündigen. Die Kündigung gilt zum Ende der aktuellen Abrechnungsperiode.' },
  { q: 'Welche Zahlungsmethoden werden akzeptiert?', a: 'Kreditkarte (Visa, Mastercard, Amex), SEPA-Lastschrift und PayPal über Stripe.' },
  { q: 'Gibt es eine kostenlose Testphase?', a: 'Der Free-Plan ist dauerhaft kostenlos. Pro und Business können 14 Tage kostenlos getestet werden.' },
  { q: 'Was passiert mit meinen Daten bei Kündigung?', a: 'Deine Daten bleiben 30 Tage nach Kündigung verfügbar. Danach werden sie unwiderruflich gelöscht.' },
]

async function checkout(plan: typeof plans[0]) {
  if (plan.id === 'free') {
    window.location.href = '/#/app'
    return
  }
  if (!plan.stripePriceId) {
    alert('Stripe noch nicht konfiguriert. Bitte VITE_STRIPE_PRO_PRICE_ID in .env eintragen.')
    return
  }
  loading.value = plan.id
  try {
    const res = await fetch('/api/stripe/create-checkout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        priceId: plan.stripePriceId,
        planId: plan.id,
        userEmail: auth.email,
        refCode: localStorage.getItem('finaz_ref') || '',
        successUrl: window.location.origin + '/#/pricing?success=true',
        cancelUrl: window.location.origin + '/#/pricing?cancel=true',
      }),
    })
    const data = await res.json()
    if (data.url) window.location.href = data.url
    else alert(data.error || 'Fehler beim Erstellen der Checkout-Session.')
  } catch {
    alert('Verbindungsfehler. Bitte erneut versuchen.')
  } finally {
    loading.value = ''
  }
}
</script>

<style scoped>
.pricing-wrap { max-width: 1100px; margin: 0 auto; padding: 2rem 1.5rem; }
.pricing-header { text-align: center; margin-bottom: 3rem; }
.back-link { font-size: 0.85rem; color: #64748b; text-decoration: none; display: inline-block; margin-bottom: 1rem; }
.back-link:hover { color: #94a3b8; }
.pricing-header h1 { font-size: 2.25rem; font-weight: 700; margin: 0 0 0.5rem; }
.sub { color: #94a3b8; margin: 0; }

.banner { padding: 0.75rem 1.25rem; border-radius: 10px; margin-top: 1rem; font-size: 0.9rem; }
.banner.success { background: rgba(74,222,128,0.15); border: 1px solid rgba(74,222,128,0.3); color: #4ade80; }
.banner.warn { background: rgba(251,191,36,0.15); border: 1px solid rgba(251,191,36,0.3); color: #fbbf24; }

.plans-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 1.25rem; margin-bottom: 4rem; }
.plan-card {
  background: #0f172a; border: 1px solid #1e293b; border-radius: 16px;
  padding: 1.75rem; position: relative; transition: border-color 0.2s;
}
.plan-card.popular { border-color: #3b82f6; }
.plan-card.current { border-color: #22c55e; }
.popular-tag, .current-tag {
  position: absolute; top: -13px; left: 50%; transform: translateX(-50%);
  padding: 0.2rem 0.9rem; border-radius: 999px; font-size: 0.78rem; white-space: nowrap;
}
.popular-tag { background: #3b82f6; color: #fff; }
.current-tag { background: #22c55e; color: #000; }
.plan-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.plan-name { font-size: 1.25rem; font-weight: 700; color: #e2e8f0; margin: 0 0 0.25rem; }
.plan-price { font-size: 2.25rem; font-weight: 800; color: #e2e8f0; margin-bottom: 0.25rem; }
.plan-price span { font-size: 1rem; color: #64748b; font-weight: 400; }
.plan-desc { color: #64748b; font-size: 0.82rem; margin: 0 0 1.25rem; }
.plan-features { list-style: none; padding: 0; margin: 0 0 1.5rem; display: flex; flex-direction: column; gap: 0.45rem; }
.plan-features li { font-size: 0.85rem; color: #cbd5e1; }
.plan-features li.miss { color: #475569; }
.btn-plan {
  display: block; text-align: center; padding: 0.7rem; border-radius: 10px;
  border: 1px solid #334155; color: #e2e8f0; font-weight: 600; font-size: 0.9rem;
  cursor: pointer; background: transparent; width: 100%; transition: all 0.2s; text-decoration: none;
}
.btn-plan:hover:not(:disabled) { border-color: #60a5fa; }
.btn-plan.primary { background: #3b82f6; border-color: #3b82f6; color: #fff; }
.btn-plan.primary:hover { background: #2563eb; }
.btn-plan:disabled { opacity: 0.6; cursor: not-allowed; }
.current-label { display: block; text-align: center; font-size: 0.85rem; color: #22c55e; margin-top: 0.5rem; }

.faq { max-width: 680px; margin: 0 auto; }
.faq h2 { font-size: 1.5rem; font-weight: 700; margin: 0 0 1.5rem; }
.faq-item { border-bottom: 1px solid #1e293b; padding: 1rem 0; }
.faq-item strong { color: #e2e8f0; font-size: 0.95rem; }
.faq-item p { color: #94a3b8; font-size: 0.875rem; margin: 0.4rem 0 0; line-height: 1.6; }
</style>
