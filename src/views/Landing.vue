<template>
  <div class="landing">
    <!-- Nav -->
    <header class="l-nav">
      <div class="l-brand">🛡️ <strong>SecureHub</strong></div>
      <div class="l-nav-links">
        <a href="#features">Features</a>
        <a href="#pricing">Preise</a>
        <RouterLink to="/partner" class="partner-link">🤝 Partner werden</RouterLink>
        <RouterLink to="/login" class="btn-outline">Anmelden</RouterLink>
        <RouterLink to="/app" class="btn-primary">Kostenlos starten</RouterLink>
      </div>
    </header>

    <!-- Hero -->
    <section class="hero">
      <div class="hero-badge">🚀 Neu: Rechenzentrum Monitor</div>
      <h1>Deine komplette<br><span class="gradient-text">Cyber Security Zentrale</span></h1>
      <p class="hero-sub">Website-Sicherheit scannen, Server überwachen und Infrastruktur schützen – alles in einem Dashboard. Für Entwickler, Agenturen und IT-Teams.</p>
      <div class="hero-actions">
        <RouterLink to="/app" class="btn-hero">Kostenlos testen →</RouterLink>
        <RouterLink to="/pricing" class="btn-hero-ghost">Preise ansehen</RouterLink>
      </div>
      <div class="hero-stats">
        <div class="stat"><strong>7</strong><span>Security-Checks</span></div>
        <div class="stat-div"></div>
        <div class="stat"><strong>A+</strong><span>bis F Bewertung</span></div>
        <div class="stat-div"></div>
        <div class="stat"><strong>Live</strong><span>Server-Metriken</span></div>
        <div class="stat-div"></div>
        <div class="stat"><strong>100%</strong><span>Datenschutz</span></div>
      </div>
    </section>

    <!-- Features -->
    <section id="features" class="features">
      <h2>Alles was du brauchst</h2>
      <p class="section-sub">Zwei leistungsstarke Tools in einer App</p>
      <div class="feat-grid">
        <div class="feat-card accent-blue">
          <div class="feat-icon">🔍</div>
          <h3>Security Scanner</h3>
          <p>Prüfe jede Website auf Sicherheitslücken in Sekunden. Erhalte eine Schul-Note (A+ bis F) und konkrete Handlungsempfehlungen.</p>
          <ul>
            <li>✅ HTTPS / SSL-Prüfung</li>
            <li>✅ 7 HTTP-Sicherheitsheader</li>
            <li>✅ Sicherheitsscore 0–100</li>
            <li>✅ PDF-Bericht exportieren</li>
          </ul>
        </div>
        <div class="feat-card accent-green">
          <div class="feat-icon">🖥️</div>
          <h3>Rechenzentrum Monitor</h3>
          <p>Behalte deine Server-Infrastruktur im Blick. Echtzeit-Metriken für CPU, RAM, Netzwerk und Festplatte.</p>
          <ul>
            <li>✅ Live CPU & RAM Metriken</li>
            <li>✅ Status-Ampel (OK / Warnung / Kritisch)</li>
            <li>✅ Auto-Refresh alle 5 Sekunden</li>
            <li>✅ Mehrere Rechenzentren</li>
          </ul>
        </div>
        <div class="feat-card accent-purple">
          <div class="feat-icon">🤖</div>
          <h3>KI-Assistent</h3>
          <p>Deine persönliche KI-Zentrale für Analyse, Empfehlungen und Planung. Powered by Claude & Gemini.</p>
          <ul>
            <li>✅ Security-Analyse per Chat</li>
            <li>✅ Optimierungsvorschläge</li>
            <li>✅ Compliance-Gateway</li>
            <li>✅ DSGVO-konform</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- Pricing Preview -->
    <section id="pricing" class="pricing-section">
      <h2>Einfache, transparente Preise</h2>
      <p class="section-sub">Starte kostenlos, upgrade wenn du wächst</p>
      <div class="price-grid">
        <div class="price-card">
          <div class="plan-name">Free</div>
          <div class="plan-price">0€<span>/Monat</span></div>
          <ul>
            <li>✅ 3 Scans pro Tag</li>
            <li>✅ 1 Server im Monitor</li>
            <li>✅ Basis-Berichte</li>
            <li>❌ PDF-Export</li>
            <li>❌ Unbegrenzte Scans</li>
          </ul>
          <RouterLink to="/app" class="btn-plan">Kostenlos starten</RouterLink>
        </div>
        <div class="price-card popular">
          <div class="popular-badge">⭐ Beliebt</div>
          <div class="plan-name">Pro</div>
          <div class="plan-price">19€<span>/Monat</span></div>
          <ul>
            <li>✅ Unbegrenzte Scans</li>
            <li>✅ 10 Server im Monitor</li>
            <li>✅ PDF-Export</li>
            <li>✅ Scan-Historie</li>
            <li>✅ Priorität-Support</li>
          </ul>
          <RouterLink to="/pricing" class="btn-plan primary">Jetzt upgraden</RouterLink>
        </div>
        <div class="price-card">
          <div class="plan-name">Business</div>
          <div class="plan-price">49€<span>/Monat</span></div>
          <ul>
            <li>✅ Alles aus Pro</li>
            <li>✅ 50 Server</li>
            <li>✅ API-Zugang</li>
            <li>✅ White-Label</li>
            <li>✅ Team-Verwaltung</li>
          </ul>
          <RouterLink to="/pricing" class="btn-plan">Zum Business Plan</RouterLink>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta-section">
      <h2>Bereit deine Infrastruktur zu schützen?</h2>
      <p>Keine Kreditkarte nötig. Sofort loslegen.</p>
      <RouterLink to="/app" class="btn-hero">Kostenlos starten →</RouterLink>
    </section>

    <!-- Source Code kaufen -->
    <section class="code-sale-section">
      <div class="code-sale-inner">
        <div class="code-sale-badge">👨‍💻 Für Entwickler & Agenturen</div>
        <h2>Starte dein eigenes SaaS</h2>
        <p class="section-sub">Kaufe den kompletten Quellcode – deploy, rebrande und verkaufe als dein eigenes Produkt.</p>
        <div class="code-sale-grid">
          <div class="code-tier">
            <div class="ct-icon">📦</div>
            <div class="ct-name">Starter</div>
            <div class="ct-price">49€</div>
            <ul>
              <li>✅ Kompletter Quellcode</li>
              <li>✅ Setup-Anleitung (README)</li>
              <li>✅ Render.com Deploy-Config</li>
              <li>❌ Video-Tutorial</li>
              <li>❌ Support</li>
            </ul>
          </div>
          <div class="code-tier popular-tier">
            <div class="popular-badge-code">⭐ Empfohlen</div>
            <div class="ct-icon">🚀</div>
            <div class="ct-name">Pro Bundle</div>
            <div class="ct-price">99€</div>
            <ul>
              <li>✅ Kompletter Quellcode</li>
              <li>✅ Setup + Deploy-Anleitung</li>
              <li>✅ Video-Tutorial (Setup → Live)</li>
              <li>✅ 30 Tage E-Mail-Support</li>
              <li>✅ Gratis-Updates (6 Monate)</li>
            </ul>
          </div>
          <div class="code-tier">
            <div class="ct-icon">🏢</div>
            <div class="ct-name">White-Label</div>
            <div class="ct-price">249€</div>
            <ul>
              <li>✅ Alles aus Pro Bundle</li>
              <li>✅ Vollständige White-Label-Lizenz</li>
              <li>✅ Darf unbegrenzt verkauft werden</li>
              <li>✅ Unbegrenzte Instanzen</li>
              <li>✅ Priorität-Support</li>
            </ul>
          </div>
        </div>
        <a :href="gumroadLink || '#'" class="btn-gumroad" target="_blank">
          Jetzt kaufen auf Gumroad →
        </a>
        <p class="code-sub">Einmalzahlung · sofortiger Download · keine Abonnements</p>
      </div>
    </section>

    <!-- Footer -->
    <footer class="l-footer">
      <div class="footer-brand">🛡️ SecureHub</div>
      <div class="footer-links">
        <RouterLink to="/app">App</RouterLink>
        <RouterLink to="/pricing">Preise</RouterLink>
        <RouterLink to="/affiliate">Affiliate</RouterLink>
        <RouterLink to="/partner">Vertriebspartner</RouterLink>
        <RouterLink to="/login">Anmelden</RouterLink>
      </div>
      <div class="footer-copy">© 2025 SecureHub · Alle Rechte vorbehalten</div>
    </footer>
  </div>
</template>

<script setup lang="ts">
const gumroadLink = import.meta.env.VITE_GUMROAD_LINK || ''
</script>

<style scoped>
.landing { min-height: 100vh; background: #020817; color: #e2e8f0; }

/* Nav */
.l-nav {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1rem 2rem; position: sticky; top: 0; z-index: 100;
  background: rgba(2,8,23,0.9); backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.l-brand { font-size: 1.25rem; color: #e2e8f0; }
.l-nav-links { display: flex; align-items: center; gap: 1.5rem; }
.l-nav-links a { color: #94a3b8; text-decoration: none; font-size: 0.9rem; transition: color 0.2s; }
.l-nav-links a:hover { color: #e2e8f0; }
.partner-link {
  padding: 0.4rem 1rem; border-radius: 8px; border: 1px solid rgba(34,197,94,0.4);
  color: #4ade80 !important; font-size: 0.9rem; font-weight: 500; transition: all 0.2s;
}
.partner-link:hover { border-color: #4ade80; background: rgba(34,197,94,0.1); }
.btn-outline {
  padding: 0.4rem 1rem; border-radius: 8px; border: 1px solid #334155;
  color: #94a3b8 !important; font-size: 0.9rem;
}
.btn-outline:hover { border-color: #60a5fa; color: #60a5fa !important; }
.btn-primary {
  padding: 0.4rem 1rem; border-radius: 8px; background: #3b82f6;
  color: #fff !important; font-size: 0.9rem; font-weight: 600;
}
.btn-primary:hover { background: #2563eb; }

/* Hero */
.hero {
  text-align: center; padding: 6rem 2rem 4rem;
  background: radial-gradient(ellipse 80% 50% at 50% -20%, rgba(59,130,246,0.15), transparent);
}
.hero-badge {
  display: inline-block; padding: 0.35rem 1rem; border-radius: 999px;
  background: rgba(59,130,246,0.15); border: 1px solid rgba(59,130,246,0.3);
  color: #60a5fa; font-size: 0.85rem; margin-bottom: 1.5rem;
}
.hero h1 { font-size: 3.5rem; font-weight: 800; line-height: 1.1; margin: 0 0 1.25rem; }
.gradient-text {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero-sub { font-size: 1.15rem; color: #94a3b8; max-width: 580px; margin: 0 auto 2rem; line-height: 1.6; }
.hero-actions { display: flex; gap: 1rem; justify-content: center; margin-bottom: 3rem; }
.btn-hero {
  padding: 0.85rem 2rem; border-radius: 10px; background: #3b82f6;
  color: #fff; text-decoration: none; font-size: 1rem; font-weight: 600; transition: all 0.2s;
}
.btn-hero:hover { background: #2563eb; transform: translateY(-1px); }
.btn-hero-ghost {
  padding: 0.85rem 2rem; border-radius: 10px; border: 1px solid #334155;
  color: #94a3b8; text-decoration: none; font-size: 1rem; transition: all 0.2s;
}
.btn-hero-ghost:hover { border-color: #60a5fa; color: #e2e8f0; }

.hero-stats {
  display: flex; align-items: center; justify-content: center; gap: 2rem;
  flex-wrap: wrap;
}
.stat { display: flex; flex-direction: column; align-items: center; }
.stat strong { font-size: 1.75rem; font-weight: 700; color: #60a5fa; }
.stat span { font-size: 0.8rem; color: #64748b; }
.stat-div { width: 1px; height: 36px; background: #1e293b; }

/* Features */
.features { padding: 5rem 2rem; text-align: center; }
.features h2, .pricing-section h2 { font-size: 2.25rem; font-weight: 700; margin: 0 0 0.5rem; }
.section-sub { color: #94a3b8; margin: 0 0 3rem; font-size: 1rem; }

.feat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; max-width: 1000px; margin: 0 auto; }
.feat-card {
  background: #0f172a; border: 1px solid #1e293b; border-radius: 16px;
  padding: 2rem; text-align: left; transition: transform 0.2s, border-color 0.2s;
}
.feat-card:hover { transform: translateY(-3px); }
.feat-card.accent-blue { border-top: 3px solid #3b82f6; }
.feat-card.accent-green { border-top: 3px solid #22c55e; }
.feat-card.accent-purple { border-top: 3px solid #8b5cf6; }
.feat-icon { font-size: 2.5rem; margin-bottom: 1rem; }
.feat-card h3 { font-size: 1.2rem; margin: 0 0 0.75rem; color: #e2e8f0; }
.feat-card p { color: #94a3b8; font-size: 0.9rem; line-height: 1.6; margin: 0 0 1rem; }
.feat-card ul { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.35rem; }
.feat-card li { font-size: 0.85rem; color: #cbd5e1; }

/* Pricing */
.pricing-section { padding: 5rem 2rem; text-align: center; background: #020817; }
.price-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.5rem; max-width: 900px; margin: 0 auto; }
.price-card {
  background: #0f172a; border: 1px solid #1e293b; border-radius: 16px;
  padding: 2rem; text-align: left; position: relative;
}
.price-card.popular { border-color: #3b82f6; background: linear-gradient(180deg, rgba(59,130,246,0.05), #0f172a); }
.popular-badge {
  position: absolute; top: -12px; left: 50%; transform: translateX(-50%);
  background: #3b82f6; color: #fff; padding: 0.2rem 1rem; border-radius: 999px; font-size: 0.8rem; white-space: nowrap;
}
.plan-name { font-size: 1rem; font-weight: 600; color: #94a3b8; margin-bottom: 0.5rem; }
.plan-price { font-size: 2.5rem; font-weight: 800; color: #e2e8f0; margin-bottom: 1.5rem; }
.plan-price span { font-size: 1rem; color: #64748b; font-weight: 400; }
.price-card ul { list-style: none; padding: 0; margin: 0 0 1.5rem; display: flex; flex-direction: column; gap: 0.5rem; }
.price-card li { font-size: 0.88rem; color: #cbd5e1; }
.btn-plan {
  display: block; text-align: center; padding: 0.7rem 1rem; border-radius: 10px;
  border: 1px solid #334155; color: #e2e8f0; text-decoration: none; font-weight: 600;
  font-size: 0.9rem; transition: all 0.2s;
}
.btn-plan:hover { border-color: #60a5fa; }
.btn-plan.primary { background: #3b82f6; border-color: #3b82f6; color: #fff; }
.btn-plan.primary:hover { background: #2563eb; }

/* CTA */
.cta-section {
  text-align: center; padding: 5rem 2rem;
  background: radial-gradient(ellipse 60% 60% at 50% 50%, rgba(59,130,246,0.1), transparent);
}
.cta-section h2 { font-size: 2rem; margin: 0 0 0.75rem; }
.cta-section p { color: #94a3b8; margin: 0 0 2rem; }

/* Footer */
.l-footer {
  border-top: 1px solid #0f172a; padding: 2rem; display: flex; align-items: center;
  justify-content: space-between; flex-wrap: wrap; gap: 1rem;
}
.footer-brand { font-size: 1.1rem; color: #e2e8f0; }
.footer-links { display: flex; gap: 1.5rem; }
.footer-links a { color: #64748b; text-decoration: none; font-size: 0.85rem; }
.footer-links a:hover { color: #94a3b8; }
.footer-copy { font-size: 0.8rem; color: #475569; }

/* Code Sale Section */
.code-sale-section {
  padding: 5rem 2rem;
  background: linear-gradient(180deg, #020817 0%, #0a1628 50%, #020817 100%);
  text-align: center;
}
.code-sale-inner { max-width: 900px; margin: 0 auto; }
.code-sale-badge {
  display: inline-block; padding: 0.35rem 1rem; border-radius: 999px;
  background: rgba(139,92,246,0.15); border: 1px solid rgba(139,92,246,0.3);
  color: #a78bfa; font-size: 0.85rem; margin-bottom: 1.5rem;
}
.code-sale-section h2 { font-size: 2.25rem; font-weight: 700; margin: 0 0 0.5rem; }
.code-sale-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.25rem; margin: 2.5rem 0;
}
.code-tier {
  background: #0f172a; border: 1px solid #1e293b; border-radius: 16px;
  padding: 1.75rem; text-align: left; position: relative;
  transition: border-color 0.2s;
}
.code-tier:hover { border-color: #334155; }
.code-tier.popular-tier { border-color: #8b5cf6; background: linear-gradient(180deg, rgba(139,92,246,0.05), #0f172a); }
.popular-badge-code {
  position: absolute; top: -13px; left: 50%; transform: translateX(-50%);
  background: #8b5cf6; color: #fff; padding: 0.2rem 0.9rem;
  border-radius: 999px; font-size: 0.78rem; white-space: nowrap;
}
.ct-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.ct-name { font-size: 1rem; font-weight: 600; color: #94a3b8; margin-bottom: 0.25rem; }
.ct-price { font-size: 2.25rem; font-weight: 800; color: #e2e8f0; margin-bottom: 1.25rem; }
.code-tier ul { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.45rem; }
.code-tier li { font-size: 0.85rem; color: #cbd5e1; }
.btn-gumroad {
  display: inline-block; padding: 0.9rem 2.5rem; border-radius: 12px;
  background: linear-gradient(135deg, #8b5cf6, #6d28d9); color: #fff;
  text-decoration: none; font-size: 1rem; font-weight: 700;
  transition: all 0.2s; margin-bottom: 0.75rem;
}
.btn-gumroad:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(139,92,246,0.3); }
.code-sub { color: #475569; font-size: 0.82rem; margin: 0; }

@media (max-width: 700px) {
  .hero h1 { font-size: 2.2rem; }
  .l-nav-links .btn-outline { display: none; }
  .l-footer { flex-direction: column; align-items: flex-start; }
}
</style>
