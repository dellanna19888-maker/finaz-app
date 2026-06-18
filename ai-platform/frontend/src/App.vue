<template>
  <div id="app-wrapper">
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <div class="logo">
          <span class="logo-icon">🧠</span>
          <span v-if="!sidebarCollapsed" class="logo-text">KI-Plattform</span>
        </div>
        <button class="collapse-btn" @click="sidebarCollapsed = !sidebarCollapsed">
          {{ sidebarCollapsed ? '›' : '‹' }}
        </button>
      </div>

      <nav class="sidebar-nav">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-item"
          :title="item.label"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span v-if="!sidebarCollapsed" class="nav-label">{{ item.label }}</span>
        </RouterLink>
      </nav>

      <div v-if="!sidebarCollapsed" class="sidebar-footer">
        <div class="version-badge">v1.0.0</div>
      </div>
    </aside>

    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, RouterView } from 'vue-router'

const sidebarCollapsed = ref(false)

const navItems = [
  { to: '/',               icon: '📊', label: 'Dashboard' },
  { to: '/chat',           icon: '💬', label: 'Chat / Assistent' },
  { to: '/text',           icon: '📝', label: 'Text-Klassifikation' },
  { to: '/image',          icon: '🖼️', label: 'Bild-Erkennung' },
  { to: '/documents',      icon: '📄', label: 'Dokument-Analyse' },
  { to: '/training',       icon: '🎓', label: 'KI Trainieren' },
  { to: '/models',         icon: '🗄️', label: 'Meine Modelle' },
]
</script>

<style scoped>
#app-wrapper {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 220px;
  background: var(--bg-card);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  flex-shrink: 0;
}

.sidebar.collapsed { width: 60px; }

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.2rem 1rem;
  border-bottom: 1px solid var(--border);
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.logo-icon { font-size: 1.6rem; }

.logo-text {
  font-size: 1rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary-light), var(--secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  white-space: nowrap;
}

.collapse-btn {
  background: none;
  border: 1px solid var(--border);
  color: var(--text-muted);
  border-radius: 6px;
  width: 28px;
  height: 28px;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.collapse-btn:hover { border-color: var(--primary); color: var(--primary-light); }

.sidebar-nav {
  flex: 1;
  padding: 0.75rem 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem 1rem;
  color: var(--text-muted);
  border-radius: 8px;
  margin: 0 0.5rem;
  transition: all 0.2s;
  text-decoration: none;
  white-space: nowrap;
  overflow: hidden;
}

.nav-item:hover {
  background: rgba(99,102,241,0.1);
  color: var(--text);
  text-decoration: none;
}

.nav-item.router-link-active {
  background: rgba(99,102,241,0.15);
  color: var(--primary-light);
  border-left: 3px solid var(--primary);
}

.nav-icon { font-size: 1.2rem; flex-shrink: 0; }

.nav-label { font-size: 0.9rem; font-weight: 500; }

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid var(--border);
}

.version-badge {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-align: center;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  min-width: 0;
}
</style>
