<template>
  <NavBar />
  <main class="app-main">
    <RouterView />
  </main>
</template>

<script setup lang="ts">
import NavBar from './components/NavBar.vue'
</script>

<style scoped>
.app-main { min-height: 100vh; }

/* Leave room for the bottom tab bar on mobile */
@media (max-width: 700px) {
  .app-main { padding-bottom: calc(64px + env(safe-area-inset-bottom)); }
}
</style>
