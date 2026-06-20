import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import './style.css'
import App from './App.vue'

createApp(App).use(createPinia()).use(router).mount('#app')

// PWA: Service Worker registrieren (nur im Produktions-Build, nicht im Dev).
// Pfad respektiert das Vite-Base (z. B. /finaz-app/ auf GitHub Pages).
if (import.meta.env.PROD && 'serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register(`${import.meta.env.BASE_URL}sw.js`).catch(() => {
      /* Registrierung fehlgeschlagen – App läuft trotzdem (ohne Offline-Cache). */
    })
  })
}
