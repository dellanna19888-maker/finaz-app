#!/usr/bin/env node
/**
 * SecureHub Data Center Agent v1.0
 * Sammelt echte CPU/RAM/Uptime-Metriken und sendet sie an SecureHub.
 *
 * Voraussetzung: Node.js >= 18 (fetch ist eingebaut)
 *
 * Verwendung:
 *   node dc-agent.mjs --server https://deine-app.onrender.com --token DEIN_TOKEN --id web-server-01
 *
 * Optionale Parameter:
 *   --interval 30     Intervall in Sekunden (Standard: 30)
 *   --role Web        Server-Rolle (Web, Database, Cache, etc.)
 *   --location Frankfurt   Standort-Bezeichnung
 */

import os from 'os'

// ── Argumente parsen ──────────────────────────────────────────────────────────
const argv = process.argv.slice(2)
const arg = (name, fallback = null) => {
  const i = argv.indexOf('--' + name)
  return i !== -1 && argv[i + 1] ? argv[i + 1] : fallback
}

const SERVER  = arg('server', 'http://localhost:3001')
const TOKEN   = arg('token')
const ID      = arg('id', os.hostname())
const ROLE    = arg('role', 'Server')
const LOC     = arg('location', os.hostname())
const INTERVAL = parseInt(arg('interval', '30')) * 1000

if (!TOKEN) {
  console.error('Fehler: --token erforderlich.')
  console.error('Token in der App unter: Rechenzentrum → ⚙️ Agent einrichten → Token erstellen')
  process.exit(1)
}

// ── CPU-Messung (Delta über 500ms) ────────────────────────────────────────────
function cpuPercent() {
  return new Promise(resolve => {
    const snap = () => os.cpus().reduce((a, c) => {
      const t = Object.values(c.times)
      return { total: a.total + t.reduce((x, y) => x + y, 0), idle: a.idle + c.times.idle }
    }, { total: 0, idle: 0 })
    const s1 = snap()
    setTimeout(() => {
      const s2 = snap()
      const pct = 100 - ((s2.idle - s1.idle) / (s2.total - s1.total)) * 100
      resolve(Math.max(0, Math.min(100, +pct.toFixed(1))))
    }, 500)
  })
}

// ── Metriken senden ───────────────────────────────────────────────────────────
async function report() {
  const totalMem = os.totalmem()
  const freeMem  = os.freemem()
  const ram  = +(((totalMem - freeMem) / totalMem) * 100).toFixed(1)
  const cpu  = await cpuPercent()
  const uptime = Math.floor(os.uptime() / 3600)

  const payload = { id: ID, token: TOKEN, name: ID, role: ROLE, location: LOC, cpu, ram, net: 0, disk: 0, uptime, ts: new Date().toISOString() }

  try {
    const res = await fetch(`${SERVER}/api/dc/report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const ok = res.status === 200
    const time = new Date().toLocaleTimeString()
    if (ok) console.log(`[${time}] ✓  CPU: ${cpu}%  RAM: ${ram}%  Uptime: ${uptime}h`)
    else    console.error(`[${time}] ✗  HTTP ${res.status}`)
  } catch (e) {
    console.error(`[${new Date().toLocaleTimeString()}] Verbindungsfehler: ${e.message}`)
  }
}

// ── Start ─────────────────────────────────────────────────────────────────────
console.log('═══════════════════════════════════════')
console.log('  🛡️  SecureHub Data Center Agent v1.0')
console.log('═══════════════════════════════════════')
console.log(`  Server   : ${SERVER}`)
console.log(`  Agent-ID : ${ID}`)
console.log(`  Rolle    : ${ROLE}`)
console.log(`  Standort : ${LOC}`)
console.log(`  Intervall: ${INTERVAL / 1000}s`)
console.log('───────────────────────────────────────\n')

report()
setInterval(report, INTERVAL)
