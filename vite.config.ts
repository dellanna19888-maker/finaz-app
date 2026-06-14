import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const API_PORT = process.env.API_PORT || '3001'

// https://vite.dev/config/
export default defineConfig({
  // Base path for GitHub Pages project site (served from /finaz-app/)
  base: process.env.GITHUB_PAGES ? '/finaz-app/' : '/',
  plugins: [vue()],
  server: {
    // Leitet /api im Dev an das Backend (npm run api) weiter.
    proxy: {
      '/api': { target: `http://localhost:${API_PORT}`, changeOrigin: true },
    },
  },
})
