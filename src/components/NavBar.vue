<template>
  <!-- Top bar (desktop) -->
  <nav class="navbar">
    <RouterLink to="/" class="brand">
      <span class="brand-icon">🎯</span>
      <span class="brand-name">Creator Hub</span>
    </RouterLink>
    <div class="nav-links">
      <RouterLink v-for="l in links" :key="l.to" :to="l.to" class="nav-link">
        <span>{{ l.icon }}</span> {{ l.label }}
      </RouterLink>
    </div>
    <div class="nav-right">
      <span v-if="demoMode" class="demo-pill">🎮 Demo</span>
      <RouterLink to="/settings" class="nav-gear" title="Einstellungen">⚙️</RouterLink>
    </div>
  </nav>

  <!-- Bottom tab bar (mobile) -->
  <nav class="tab-bar">
    <RouterLink v-for="l in links" :key="l.to" :to="l.to" class="tab-btn">
      <span class="tab-icon">{{ l.icon }}</span>
      <span class="tab-label">{{ l.short }}</span>
    </RouterLink>
    <RouterLink to="/settings" class="tab-btn">
      <span class="tab-icon">⚙️</span>
      <span class="tab-label">Setup</span>
    </RouterLink>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const demoMode = computed(() => localStorage.getItem('finaz_demo') === '1')

const links = [
  { to: '/',           label: 'Zentrale',   short: 'Zentrale', icon: '🧠' },
  { to: '/tasks',      label: 'Content',    short: 'Content',  icon: '🎬' },
  { to: '/channel',    label: 'Kanal',      short: 'Kanal',    icon: '📊' },
  { to: '/notes',      label: 'Wissen',     short: 'Wissen',   icon: '📚' },
  { to: '/compliance', label: 'Compliance', short: 'Comp.',    icon: '🛡️' },
]
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  padding: 0 1.5rem;
  height: 60px;
  background: rgba(13, 20, 38, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
  gap: 1rem;
}

.brand { display: flex; align-items: center; gap: 0.5rem; text-decoration: none; flex-shrink: 0; }
.brand-icon { font-size: 1.4rem; }
.brand-name { font-size: 1.1rem; font-weight: 700; color: var(--text); letter-spacing: 0.01em; }

.nav-links { display: flex; gap: 0.25rem; flex: 1; justify-content: center; }
.nav-link {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.85rem;
  border-radius: 8px;
  color: var(--text2);
  text-decoration: none;
  font-size: 0.88rem;
  transition: all 0.18s;
  white-space: nowrap;
}
.nav-link:hover { color: var(--text); background: rgba(255,255,255,0.05); }
.nav-link.router-link-active { color: var(--accent2); background: rgba(99,102,241,0.12); }

.nav-right { display: flex; align-items: center; gap: 0.5rem; flex-shrink: 0; }
.demo-pill {
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  background: rgba(99,102,241,0.2);
  color: var(--accent2);
  border: 1px solid rgba(99,102,241,0.3);
}
.nav-gear { font-size: 1.15rem; text-decoration: none; padding: 0.3rem 0.45rem; border-radius: 8px; line-height: 1; }
.nav-gear:hover { background: rgba(255,255,255,0.05); }
.nav-gear.router-link-active { background: rgba(99,102,241,0.12); }

.tab-bar {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(13, 20, 38, 0.97);
  backdrop-filter: blur(12px);
  border-top: 1px solid var(--border);
  padding-bottom: env(safe-area-inset-bottom);
}
.tab-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 0.2rem 0.4rem;
  color: var(--text3);
  font-size: 0.64rem;
  gap: 2px;
  text-decoration: none;
  -webkit-tap-highlight-color: transparent;
  transition: color 0.18s;
}
.tab-btn.router-link-active { color: var(--accent2); }
.tab-icon { font-size: 1.25rem; line-height: 1; }

@media (max-width: 700px) {
  .navbar .nav-links { display: none; }
  .navbar { height: 52px; padding: 0 1rem; }
  .tab-bar { display: flex; }
}
</style>
