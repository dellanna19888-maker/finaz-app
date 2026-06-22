import { defineConfig } from 'vitest/config'

// Unit-Tests laufen in einer reinen Node-Umgebung gegen die isomorphen Kerne
// (Compliance-Gateway, Aktions-Parsing, Kontext-/Finanz-Aggregation) – ohne DOM.
export default defineConfig({
  test: {
    environment: 'node',
    include: ['tests/**/*.test.ts'],
  },
})
