import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Vite ist das Werkzeug, das unseren Code im Browser ausführbar macht
// und beim Entwickeln die Seite automatisch neu lädt.
// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
})
