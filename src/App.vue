<template>
  <NavBar v-if="showNav" />
  <main :class="showNav ? 'app-main' : ''">
    <RouterView />
  </main>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from './components/NavBar.vue'

const route = useRoute()
const noNavRoutes = ['/', '/login', '/pricing', '/affiliate', '/affiliate/portal']
const showNav = computed(() => !noNavRoutes.includes(route.path))
</script>

<style scoped>
.app-main { min-height: 100vh; }

@media (max-width: 700px) {
  .app-main { padding-bottom: calc(64px + env(safe-area-inset-bottom)); }
}
</style>
