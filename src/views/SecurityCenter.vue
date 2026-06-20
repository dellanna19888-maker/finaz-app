<template>
  <div class="sec-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1>🛡️ Security &amp; Rechenzentrum</h1>
        <p class="sub">Cyber Security Scanner + Live Infrastruktur-Monitor — dein Dashboard für sichere Systeme.</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button :class="['tab-btn', { active: tab === 'scanner' }]" @click="tab = 'scanner'">🔍 Security Scanner</button>
      <button :class="['tab-btn', { active: tab === 'dc' }]" @click="tab = 'dc'; loadMetrics()">🖥️ Rechenzentrum</button>
    </div>

    <!-- ===== SECURITY SCANNER ===== -->
    <div v-if="tab === 'scanner'" class="panel">
      <div class="scan-box">
        <input
          v-model="scanUrl"
          class="url-input"
          placeholder="z. B. example.com oder https://mysite.de"
          @keydown.enter="runScan"
        />
        <button class="btn" :disabled="scanning || !scanUrl.trim()" @click="runScan">
          {{ scanning ? 'Scannt…' : 'Scan starten' }}
        </button>
      </div>
      <p v-if="scanError" class="error-msg">⚠ {{ scanError }}</p>

      <!-- Ergebnis -->
      <div v-if="scanResult" class="scan-result">
        <div class="score-row">
          <div :class="['grade-badge', gradeClass(scanResult.grade)]">{{ scanResult.grade }}</div>
          <div class="score-info">
            <div class="score-num">{{ scanResult.score }}<span class="score-max">/100</span></div>
            <div class="score-sub">{{ scanResult.url }}</div>
          </div>
          <div :class="['https-badge', scanResult.https ? 'ok' : 'fail']">
            {{ scanResult.https ? '🔒 HTTPS aktiv' : '⚠ Kein HTTPS' }}
          </div>
        </div>

        <div class="checks-grid">
          <div v-for="c in scanResult.checks" :key="c.label" :class="['check-card', c.present ? 'ok' : 'missing']">
            <div class="check-icon">{{ c.present ? '✅' : '❌' }}</div>
            <div class="check-info">
              <div class="check-label">{{ c.label }}</div>
              <div v-if="c.value" class="check-val">{{ truncate(c.value, 60) }}</div>
              <div v-else class="check-missing">Nicht gesetzt – {{ weight(c.weight) }} Punkte fehlen</div>
            </div>
          </div>
        </div>

        <div class="recs">
          <h3>Empfehlungen</h3>
          <ul>
            <li v-if="!scanResult.https">🔴 <strong>HTTPS aktivieren</strong> – alle Daten werden unverschlüsselt übertragen</li>
            <li v-for="c in scanResult.checks.filter(x => !x.present)" :key="c.label">
              🟡 <strong>{{ c.label }}</strong> Header hinzufügen (+{{ weight(c.weight) }} Punkte)
            </li>
            <li v-if="scanResult.score >= 80">🟢 Gute Sicherheitskonfiguration! Weiter so.</li>
          </ul>
        </div>
      </div>

      <!-- Erklärungs-Box -->
      <div v-if="!scanResult" class="info-cards">
        <div class="info-card">
          <div class="info-icon">🔒</div>
          <h3>Was wird geprüft?</h3>
          <ul>
            <li>HTTPS / SSL-Verschlüsselung</li>
            <li>HTTP Sicherheitsheader (7 Checks)</li>
            <li>Sicherheitsscore 0–100</li>
            <li>Note A+ bis F</li>
          </ul>
        </div>
        <div class="info-card">
          <div class="info-icon">💼</div>
          <h3>Für wen?</h3>
          <ul>
            <li>Website-Betreiber</li>
            <li>IT-Abteilungen</li>
            <li>Agenturen & Freelancer</li>
            <li>E-Commerce Shops</li>
          </ul>
        </div>
        <div class="info-card">
          <div class="info-icon">💰</div>
          <h3>Als Abo verkaufen</h3>
          <ul>
            <li>Free: 1 Scan/Tag</li>
            <li>Pro 29€/Monat: unbegrenzt</li>
            <li>Team 99€/Monat: API-Zugang</li>
            <li>Enterprise: individuell</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- ===== RECHENZENTRUM MONITOR ===== -->
    <div v-if="tab === 'dc'" class="panel">
      <div class="dc-toolbar">
        <span class="dc-ts">Letzte Aktualisierung: {{ lastTs }}</span>
        <button class="btn btn-sm" :disabled="loadingDc" @click="loadMetrics">
          {{ loadingDc ? '…' : '↻ Aktualisieren' }}
        </button>
        <label class="auto-label">
          <input v-model="autoRefresh" type="checkbox" @change="toggleAuto" /> Auto (5s)
        </label>
      </div>

      <p v-if="dcError" class="error-msg">⚠ {{ dcError }}</p>

      <!-- Alerts -->
      <div v-if="dcAlerts.length" class="alert-bar">
        <div v-for="(a, i) in dcAlerts" :key="i" :class="['alert-item', a.level]">
          {{ a.level === 'critical' ? '🔴' : '🟡' }} <strong>{{ a.node }}</strong>: {{ a.msg }}
        </div>
      </div>
      <div v-else-if="dcNodes.length" class="alert-bar ok">
        <span>✅ Alle Systeme laufen normal</span>
      </div>

      <!-- Server Grid -->
      <div class="nodes-grid">
        <div v-for="n in dcNodes" :key="n.id" :class="['node-card', n.status]">
          <div class="node-head">
            <span :class="['status-dot', n.status]"></span>
            <strong>{{ n.name }}</strong>
            <span class="node-role">{{ n.role }}</span>
          </div>
          <div class="node-loc">📍 {{ n.location }}</div>
          <div class="metrics">
            <div class="metric">
              <div class="metric-label">CPU</div>
              <div class="metric-bar">
                <div :class="['bar-fill', barClass(n.cpu)]" :style="{ width: n.cpu + '%' }"></div>
              </div>
              <div class="metric-val">{{ n.cpu }}%</div>
            </div>
            <div class="metric">
              <div class="metric-label">RAM</div>
              <div class="metric-bar">
                <div :class="['bar-fill', barClass(n.ram)]" :style="{ width: n.ram + '%' }"></div>
              </div>
              <div class="metric-val">{{ n.ram }}%</div>
            </div>
            <div class="metric">
              <div class="metric-label">Netz</div>
              <div class="metric-bar">
                <div class="bar-fill net" :style="{ width: n.net + '%' }"></div>
              </div>
              <div class="metric-val">{{ n.net }}%</div>
            </div>
            <div class="metric">
              <div class="metric-label">Disk</div>
              <div class="metric-bar">
                <div :class="['bar-fill', barClass(n.disk)]" :style="{ width: n.disk + '%' }"></div>
              </div>
              <div class="metric-val">{{ n.disk }}%</div>
            </div>
          </div>
          <div class="node-uptime">⬆ Uptime: {{ n.uptime }}h</div>
        </div>
      </div>

      <!-- Leere Zustandsanzeige -->
      <div v-if="!dcNodes.length && !loadingDc" class="info-cards">
        <div class="info-card">
          <div class="info-icon">🖥️</div>
          <h3>Rechenzentrum Monitor</h3>
          <p>Klicke auf "Aktualisieren" um Metriken zu laden.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue'

type Tab = 'scanner' | 'dc'
const tab = ref<Tab>('scanner')

// ── Security Scanner ──────────────────────────────────────────────────────────
interface CheckResult {
  label: string
  present: boolean
  value: string | null
  weight: number
}
interface ScanResult {
  url: string
  https: boolean
  score: number
  grade: string
  checks: CheckResult[]
  status: number
}

const scanUrl = ref('')
const scanning = ref(false)
const scanError = ref('')
const scanResult = ref<ScanResult | null>(null)

async function runScan() {
  if (!scanUrl.value.trim() || scanning.value) return
  scanning.value = true
  scanError.value = ''
  scanResult.value = null
  try {
    const res = await fetch('/api/security/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: scanUrl.value.trim() }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.error || 'Scan fehlgeschlagen')
    scanResult.value = data
  } catch (err) {
    scanError.value = (err as Error).message
  } finally {
    scanning.value = false
  }
}

function gradeClass(grade: string) {
  if (grade === 'A+' || grade === 'A') return 'grade-a'
  if (grade === 'B') return 'grade-b'
  if (grade === 'C') return 'grade-c'
  return 'grade-f'
}

function truncate(s: string, n: number) {
  return s.length > n ? s.slice(0, n) + '…' : s
}

function weight(w: number) {
  return w + ' Punkte'
}

// ── Rechenzentrum Monitor ─────────────────────────────────────────────────────
interface DcNode {
  id: string
  name: string
  role: string
  location: string
  cpu: number
  ram: number
  net: number
  disk: number
  status: 'ok' | 'warning' | 'critical'
  uptime: number
}
interface DcAlert {
  node: string
  level: string
  msg: string
}

const dcNodes = ref<DcNode[]>([])
const dcAlerts = ref<DcAlert[]>([])
const loadingDc = ref(false)
const dcError = ref('')
const lastTs = ref('–')
const autoRefresh = ref(false)
let autoTimer: ReturnType<typeof setInterval> | null = null

async function loadMetrics() {
  loadingDc.value = true
  dcError.value = ''
  try {
    const res = await fetch('/api/dc/metrics')
    const data = await res.json()
    if (!res.ok) throw new Error(data.error || 'Fehler beim Laden')
    dcNodes.value = data.nodes
    dcAlerts.value = data.alerts
    lastTs.value = new Date(data.ts).toLocaleTimeString('de-DE')
  } catch (err) {
    dcError.value = (err as Error).message
  } finally {
    loadingDc.value = false
  }
}

function toggleAuto() {
  if (autoTimer) { clearInterval(autoTimer); autoTimer = null }
  if (autoRefresh.value) autoTimer = setInterval(loadMetrics, 5000)
}

function barClass(val: number) {
  return val > 90 ? 'critical' : val > 75 ? 'warning' : 'ok'
}

onUnmounted(() => {
  if (autoTimer) clearInterval(autoTimer)
})
</script>

<style scoped>
.sec-page { max-width: 1100px; margin: 0 auto; padding: 1.5rem 1rem; }
.page-header { margin-bottom: 1.5rem; }
.page-header h1 { font-size: 1.6rem; font-weight: 700; color: #e2e8f0; margin: 0 0 0.3rem; }
.sub { color: #94a3b8; font-size: 0.9rem; margin: 0; }

/* Tabs */
.tabs { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; }
.tab-btn {
  padding: 0.6rem 1.4rem; border-radius: 8px; border: 1px solid #334155;
  background: #1e293b; color: #94a3b8; cursor: pointer; font-size: 0.95rem; transition: all 0.2s;
}
.tab-btn.active { background: #3b82f6; border-color: #3b82f6; color: #fff; }
.tab-btn:hover:not(.active) { border-color: #60a5fa; color: #e2e8f0; }

.panel { animation: fadeIn 0.2s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: none; } }

/* Scanner */
.scan-box { display: flex; gap: 0.75rem; margin-bottom: 1rem; }
.url-input {
  flex: 1; padding: 0.7rem 1rem; border-radius: 10px; border: 1px solid #334155;
  background: #0f172a; color: #e2e8f0; font-size: 1rem;
}
.url-input:focus { outline: none; border-color: #3b82f6; }
.error-msg { color: #f87171; background: rgba(248,113,113,0.1); border: 1px solid rgba(248,113,113,0.3); padding: 0.6rem 1rem; border-radius: 8px; margin-bottom: 1rem; }

/* Score */
.scan-result { margin-top: 1rem; }
.score-row {
  display: flex; align-items: center; gap: 1.5rem;
  background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 1.2rem 1.5rem; margin-bottom: 1.5rem;
}
.grade-badge {
  width: 64px; height: 64px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 1.5rem; font-weight: 700; flex-shrink: 0;
}
.grade-a { background: #052e16; color: #4ade80; border: 2px solid #4ade80; }
.grade-b { background: #0c4a6e; color: #38bdf8; border: 2px solid #38bdf8; }
.grade-c { background: #451a03; color: #fb923c; border: 2px solid #fb923c; }
.grade-f { background: #3f0000; color: #f87171; border: 2px solid #f87171; }

.score-num { font-size: 2rem; font-weight: 700; color: #e2e8f0; }
.score-max { font-size: 1rem; color: #64748b; }
.score-sub { font-size: 0.8rem; color: #64748b; word-break: break-all; }
.https-badge { padding: 0.4rem 0.9rem; border-radius: 999px; font-size: 0.85rem; font-weight: 600; margin-left: auto; }
.https-badge.ok { background: rgba(74,222,128,0.15); color: #4ade80; border: 1px solid rgba(74,222,128,0.3); }
.https-badge.fail { background: rgba(248,113,113,0.15); color: #f87171; border: 1px solid rgba(248,113,113,0.3); }

/* Checks */
.checks-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 0.75rem; margin-bottom: 1.5rem; }
.check-card {
  display: flex; gap: 0.75rem; align-items: flex-start;
  background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 0.8rem 1rem;
}
.check-card.ok { border-color: rgba(74,222,128,0.2); }
.check-card.missing { border-color: rgba(248,113,113,0.2); }
.check-icon { font-size: 1.2rem; flex-shrink: 0; line-height: 1.4; }
.check-label { font-weight: 600; color: #e2e8f0; font-size: 0.9rem; }
.check-val { font-size: 0.75rem; color: #64748b; margin-top: 0.15rem; word-break: break-all; }
.check-missing { font-size: 0.75rem; color: #f87171; margin-top: 0.15rem; }

/* Recommendations */
.recs { background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 1rem 1.25rem; }
.recs h3 { margin: 0 0 0.75rem; color: #e2e8f0; font-size: 1rem; }
.recs ul { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.4rem; }
.recs li { font-size: 0.88rem; color: #cbd5e1; }

/* Info Cards */
.info-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 1rem; margin-top: 1rem; }
.info-card {
  background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 1.25rem;
}
.info-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.info-card h3 { margin: 0 0 0.5rem; color: #e2e8f0; font-size: 1rem; }
.info-card ul { list-style: none; padding: 0; margin: 0; }
.info-card li { font-size: 0.85rem; color: #94a3b8; padding: 0.2rem 0; }
.info-card li::before { content: '• '; color: #3b82f6; }
.info-card p { font-size: 0.88rem; color: #94a3b8; margin: 0; }

/* DC Toolbar */
.dc-toolbar { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap; }
.dc-ts { font-size: 0.82rem; color: #64748b; }
.btn-sm { padding: 0.35rem 0.8rem; font-size: 0.85rem; }
.auto-label { display: flex; align-items: center; gap: 0.4rem; font-size: 0.85rem; color: #94a3b8; cursor: pointer; }

/* Alert Bar */
.alert-bar {
  border-radius: 10px; padding: 0.7rem 1rem; margin-bottom: 1rem;
  display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center;
  background: rgba(15,23,42,0.8); border: 1px solid #334155;
}
.alert-bar.ok { border-color: rgba(74,222,128,0.3); color: #4ade80; font-size: 0.9rem; }
.alert-item { font-size: 0.85rem; color: #e2e8f0; }
.alert-item.critical { color: #f87171; }
.alert-item.warning { color: #fbbf24; }

/* Node Cards */
.nodes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
.node-card {
  background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 1rem 1.2rem;
  transition: border-color 0.2s;
}
.node-card.warning { border-color: rgba(251,191,36,0.4); }
.node-card.critical { border-color: rgba(248,113,113,0.4); }
.node-head { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem; }
.status-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.status-dot.ok { background: #4ade80; box-shadow: 0 0 6px #4ade80; }
.status-dot.warning { background: #fbbf24; box-shadow: 0 0 6px #fbbf24; }
.status-dot.critical { background: #f87171; box-shadow: 0 0 6px #f87171; }
.node-role { margin-left: auto; font-size: 0.75rem; color: #64748b; background: #0f172a; padding: 0.1rem 0.5rem; border-radius: 999px; }
.node-loc { font-size: 0.78rem; color: #64748b; margin-bottom: 0.75rem; }

/* Metrics */
.metrics { display: flex; flex-direction: column; gap: 0.4rem; }
.metric { display: flex; align-items: center; gap: 0.5rem; }
.metric-label { width: 32px; font-size: 0.72rem; color: #64748b; flex-shrink: 0; }
.metric-bar { flex: 1; height: 6px; background: #0f172a; border-radius: 3px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 3px; transition: width 0.5s ease; }
.bar-fill.ok { background: #4ade80; }
.bar-fill.warning { background: #fbbf24; }
.bar-fill.critical { background: #f87171; }
.bar-fill.net { background: #60a5fa; }
.metric-val { width: 40px; font-size: 0.75rem; color: #94a3b8; text-align: right; flex-shrink: 0; }
.node-uptime { font-size: 0.75rem; color: #475569; margin-top: 0.75rem; }

@media (max-width: 600px) {
  .scan-box { flex-direction: column; }
  .score-row { flex-wrap: wrap; gap: 1rem; }
  .https-badge { margin-left: 0; }
}
</style>
