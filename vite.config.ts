import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  // Base path for GitHub Pages project site (served from /finaz-app/)
  base: process.env.GITHUB_PAGES ? '/finaz-app/' : '/',
  plugins: [vue()],
})
