<template>
  <!-- Top bar (desktop) -->
  <nav class="navbar">
    <div class="brand">
      <span class="brand-icon">🧠</span>
      <span class="brand-name">Hub</span>
    </div>
    <div class="nav-links">
      <RouterLink v-for="l in links" :key="l.to" :to="l.to" class="nav-link">{{ l.label }}</RouterLink>
    </div>
    <RouterLink to="/settings" class="nav-gear" title="Einstellungen">⚙️</RouterLink>
  </nav>

  <!-- Bottom tab bar (mobile) -->
  <nav class="tab-bar">
    <RouterLink v-for="l in links" :key="l.to" :to="l.to" class="tab-btn">
      <span class="tab-icon">{{ l.icon }}</span>
      <span class="tab-label">{{ l.short }}</span>
    </RouterLink>
  </nav>
</template>

<script setup lang="ts">
const links = [
  { to: '/', label: 'Zentrale', short: 'Zentrale', icon: '🧠' },
  { to: '/tasks', label: 'Content', short: 'Content', icon: '🎬' },
  { to: '/channel', label: 'Kanal', short: 'Kanal', icon: '📊' },
  { to: '/notes', label: 'Wissen', short: 'Wissen', icon: '📚' },
  { to: '/compliance', label: 'Compliance', short: 'Comp.', icon: '🛡️' },
]
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  height: 60px;
  background: #1a1a2e;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
  position: sticky;
  top: 0;
  z-index: 100;
}

.brand { display: flex; align-items: center; gap: 0.5rem; }
.brand-icon { font-size: 1.5rem; }
.brand-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: #e2e8f0;
  letter-spacing: 0.02em;
}

.nav-links { display: flex; gap: 0.5rem; }
.nav-link {
  padding: 0.4rem 1rem;
  border-radius: 6px;
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.9rem;
  transition: all 0.2s;
}
.nav-link:hover { color: #e2e8f0; background: rgba(255,255,255,0.05); }
.nav-link.router-link-active { color: #60a5fa; background: rgba(96,165,250,0.1); }

.nav-gear { font-size: 1.2rem; text-decoration: none; padding: 0.3rem 0.5rem; border-radius: 6px; line-height: 1; }
.nav-gear:hover { background: rgba(255,255,255,0.05); }
.nav-gear.router-link-active { background: rgba(96,165,250,0.1); }

/* Bottom tab bar — hidden on desktop */
.tab-bar {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: #1a1a2e;
  border-top: 1px solid #1e293b;
  padding-bottom: env(safe-area-inset-bottom);
}
.tab-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0.6rem 0.25rem;
  color: #475569;
  font-size: 0.68rem;
  gap: 3px;
  text-decoration: none;
  -webkit-tap-highlight-color: transparent;
}
.tab-btn.router-link-active { color: #60a5fa; }
.tab-icon { font-size: 1.3rem; line-height: 1; }

@media (max-width: 700px) {
  .navbar .nav-links { display: none; }
  .navbar { height: 52px; padding: 0 1rem; }
  .tab-bar { display: flex; }
}
</style>
