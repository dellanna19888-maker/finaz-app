<template>
  <div class="sec-page">
    <div class="page-header">
      <div>
        <h1>🛡️ Security &amp; Rechenzentrum</h1>
        <p class="sub">Cyber Security Scanner + Live Infrastruktur-Monitor + automatische E-Mail-Berichte</p>
      </div>
    </div>

    <div class="tabs">
      <button :class="['tab-btn', { active: tab === 'scanner' }]" @click="tab = 'scanner'">🔍 Scanner</button>
      <button :class="['tab-btn', { active: tab === 'dc' }]" @click="tab = 'dc'; loadMetrics()">🖥️ Rechenzentrum</button>
      <button :class="['tab-btn', { active: tab === 'monitor' }]" @click="tab = 'monitor'; loadSites()">📧 Monitoring</button>
    </div>

    <!-- ===== SECURITY SCANNER ===== -->
    <div v-if="tab === 'scanner'" class="panel">
      <div class="scan-box">
        <input v-model="scanUrl" class="url-input" placeholder="z. B. example.com oder https://mysite.de" @keydown.enter="runScan" />
        <button class="btn" :disabled="scanning || !scanUrl.trim()" @click="runScan">
          {{ scanning ? 'Scannt…' : 'Scan starten' }}
        </button>
      </div>
      <p v-if="scanError" class="error-msg">⚠ {{ scanError }}</p>

      <div v-if="scanResult" class="scan-result">
        <!-- Score-Zeile -->
        <div class="score-row">
          <div :class="['grade-badge', gradeClass(scanResult.grade)]">{{ scanResult.grade }}</div>
          <div class="score-info">
            <div class="score-num">{{ scanResult.score }}<span class="score-max">/100</span></div>
            <div class="score-sub">{{ scanResult.url }}</div>
          </div>
          <div :class="['https-badge', scanResult.https ? 'ok' : 'fail']">
            {{ scanResult.https ? '🔒 HTTPS aktiv' : '⚠ Kein HTTPS' }}
          </div>
          <button class="btn-icon" @click="exportPdf" title="Bericht exportieren">📄 Export</button>
        </div>

        <!-- SSL-Zertifikat Info -->
        <div v-if="scanResult.ssl" class="ssl-box">
          <div class="ssl-left">
            <span class="ssl-icon">🔐</span>
            <div>
              <div class="ssl-title">SSL-Zertifikat</div>
              <div class="ssl-issuer">{{ scanResult.ssl.issuer || 'Unbekannter Aussteller' }}</div>
            </div>
          </div>
          <div class="ssl-right">
            <span v-if="scanResult.ssl.daysRemaining !== null" :style="{ color: sslDaysColor(scanResult.ssl.daysRemaining) }" class="ssl-days">
              {{ scanResult.ssl.daysRemaining > 0 ? `${scanResult.ssl.daysRemaining} Tage` : 'ABGELAUFEN!' }}
            </span>
            <span class="ssl-expiry">{{ scanResult.ssl.expiry ? new Date(scanResult.ssl.expiry).toLocaleDateString('de-DE') : '–' }}</span>
            <span v-if="scanResult.ssl.daysRemaining !== null && scanResult.ssl.daysRemaining <= 30" class="ssl-warn">⚠ Bald ablaufend</span>
          </div>
        </div>

        <!-- Scan-Verlauf / Trend -->
        <div v-if="scanHistory.length >= 2" class="history-box">
          <div class="history-header">
            <span>📈 Score-Verlauf</span>
            <span :style="{ color: trendColor(scanHistory) }" class="trend-badge">{{ historyTrend(scanHistory) }} vs. letzter Scan</span>
          </div>
          <div class="history-dots">
            <div v-for="(h, i) in scanHistory.slice(0, 7)" :key="i" class="history-dot">
              <div :class="['dot-grade', gradeClass(h.grade)]" :title="`${new Date(h.date).toLocaleDateString('de-DE')}: ${h.score}/100`">{{ h.grade }}</div>
              <div class="dot-score">{{ h.score }}</div>
            </div>
          </div>
        </div>

        <!-- Checks mit Fix-Anleitungen -->
        <div class="checks-list">
          <div v-for="c in scanResult.checks" :key="c.label" :class="['check-row', c.present ? 'ok' : 'missing']">
            <div class="check-main">
              <span class="check-icon">{{ c.present ? '✅' : '❌' }}</span>
              <div class="check-info">
                <span class="check-label">{{ c.label }}</span>
                <span v-if="c.value" class="check-val">{{ truncate(c.value, 70) }}</span>
                <span v-else class="check-missing">Fehlt – {{ c.weight }} Punkte</span>
              </div>
              <button v-if="!c.present" class="btn-fix-toggle" @click="toggleFix(c.label)">
                {{ openFix === c.label ? '▲ Schließen' : '🔧 Wie beheben?' }}
              </button>
            </div>

            <!-- Fix-Anleitung aufklappbar -->
            <div v-if="!c.present && openFix === c.label" class="fix-guide">
              <div class="fix-tabs">
                <button v-for="t in fixTabs" :key="t" :class="['fix-tab', { active: fixLang === t }]" @click="fixLang = t">{{ t }}</button>
              </div>
              <div class="fix-code">
                <pre>{{ fixGuides[c.label]?.[fixLang] || '# Kein Beispiel verfügbar' }}</pre>
                <button class="btn-copy-code" @click="copyCode(fixGuides[c.label]?.[fixLang] || '')">📋 Kopieren</button>
              </div>
              <p class="fix-hint">{{ fixGuides[c.label]?.hint || '' }}</p>
            </div>
          </div>
        </div>

        <!-- Seite für E-Mail-Monitoring speichern -->
        <div class="monitor-save">
          <h3>📧 Automatische Berichte aktivieren</h3>
          <p>Erhalte jede Woche einen Security-Bericht für diese Website per E-Mail.</p>
          <div v-if="!monitorSaved" class="monitor-form">
            <input v-model="monitorEmail" type="email" placeholder="deine@email.de" class="mon-input" />
            <button class="btn btn-green" :disabled="savingMonitor || !monitorEmail" @click="saveMonitor">
              {{ savingMonitor ? '…' : '✅ Wöchentlichen Bericht aktivieren' }}
            </button>
          </div>
          <div v-else class="monitor-ok">
            ✅ Wöchentliche Berichte aktiviert für <strong>{{ monitorEmail }}</strong>
          </div>
          <p v-if="monitorError" class="error-msg">{{ monitorError }}</p>
        </div>
      </div>

      <!-- Info-Karten wenn noch kein Scan -->
      <div v-if="!scanResult" class="info-cards">
        <div class="info-card">
          <div class="info-icon">🔍</div>
          <h3>7 Security-Checks</h3>
          <ul><li>HTTPS / SSL</li><li>HSTS</li><li>Content-Security-Policy</li><li>X-Frame-Options</li><li>X-Content-Type-Options</li><li>Referrer-Policy</li><li>Permissions-Policy</li></ul>
        </div>
        <div class="info-card">
          <div class="info-icon">🔧</div>
          <h3>Fix-Anleitungen</h3>
          <ul><li>Apache (.htaccess)</li><li>Nginx Konfiguration</li><li>Node.js / Express</li><li>WordPress</li></ul>
        </div>
        <div class="info-card">
          <div class="info-icon">📧</div>
          <h3>Automatische Berichte</h3>
          <ul><li>Wöchentlicher Scan</li><li>E-Mail bei Problemen</li><li>Score-Verlauf</li><li>Sofort-Alarm bei Änderung</li></ul>
        </div>
      </div>
    </div>

    <!-- ===== RECHENZENTRUM MONITOR ===== -->
    <div v-if="tab === 'dc'" class="panel">
      <div class="dc-toolbar">
        <span class="dc-ts">Aktualisiert: {{ lastTs }}</span>
        <span v-if="hasRealAgents" class="badge-live">🟢 Live-Daten</span>
        <span v-else class="badge-sim">🔵 Simuliert</span>
        <button class="btn btn-sm" :disabled="loadingDc" @click="loadMetrics">{{ loadingDc ? '…' : '↻ Aktualisieren' }}</button>
        <label class="auto-label"><input v-model="autoRefresh" type="checkbox" @change="toggleAuto" /> Auto (5s)</label>
        <button class="btn btn-sm btn-outline-blue" @click="showAgentSetup = !showAgentSetup">⚙️ Agent einrichten</button>
      </div>

      <!-- Agent-Setup-Panel -->
      <div v-if="showAgentSetup" class="agent-setup">
        <h3>🔌 Echten Server verbinden</h3>
        <p class="sub">Installiere den SecureHub Agent auf deinem Server – er sendet echte CPU/RAM-Daten.</p>
        <div class="agent-steps">
          <div class="agent-step">
            <div class="step-num">1</div>
            <div>
              <strong>Agent registrieren</strong>
              <div class="agent-reg-form">
                <input v-model="agentName" class="url-input" placeholder="Server-Name z. B. Web-Server-01" />
                <button class="btn" :disabled="registeringAgent || !agentName" @click="registerAgent">
                  {{ registeringAgent ? '…' : 'Token erstellen' }}
                </button>
              </div>
              <div v-if="agentToken" class="token-box">
                <span class="token-label">Token:</span>
                <code>{{ agentToken }}</code>
                <button class="btn-copy-code" @click="copyCode(agentToken)">📋</button>
              </div>
            </div>
          </div>
          <div class="agent-step">
            <div class="step-num">2</div>
            <div>
              <strong>Agent auf Server starten</strong>
              <div class="fix-code" style="margin-top:0.5rem">
                <pre>{{ agentCommand }}</pre>
                <button class="btn-copy-code" @click="copyCode(agentCommand)">📋 Kopieren</button>
              </div>
            </div>
          </div>
          <div class="agent-step">
            <div class="step-num">3</div>
            <div>
              <strong>Fertig!</strong> Der Agent meldet sich alle 30s. Klicke auf ↻ Aktualisieren um Live-Daten zu sehen.
            </div>
          </div>
        </div>
      </div>
      <p v-if="dcError" class="error-msg">⚠ {{ dcError }}</p>
      <div v-if="dcAlerts.length" class="alert-bar">
        <div v-for="(a, i) in dcAlerts" :key="i" :class="['alert-item', a.level]">
          {{ a.level === 'critical' ? '🔴' : '🟡' }} <strong>{{ a.node }}</strong>: {{ a.msg }}
        </div>
      </div>
      <div v-else-if="dcNodes.length" class="alert-bar ok"><span>✅ Alle Systeme normal</span></div>
      <div class="nodes-grid">
        <div v-for="n in dcNodes" :key="n.id" :class="['node-card', n.status]">
          <div class="node-head">
            <span :class="['status-dot', n.status]"></span>
            <strong>{{ n.name }}</strong>
            <span class="node-role">{{ n.role }}</span>
          </div>
          <div class="node-loc">📍 {{ n.location }}</div>
          <div class="metrics">
            <div v-for="m in [['CPU', n.cpu], ['RAM', n.ram], ['Netz', n.net], ['Disk', n.disk]]" :key="m[0]" class="metric">
              <div class="metric-label">{{ m[0] }}</div>
              <div class="metric-bar"><div :class="['bar-fill', m[0] === 'Netz' ? 'net' : barClass(+m[1])]" :style="{ width: m[1] + '%' }"></div></div>
              <div class="metric-val">{{ m[1] }}%</div>
            </div>
          </div>
          <div class="node-uptime">⬆ Uptime: {{ n.uptime }}h</div>
        </div>
      </div>
    </div>

    <!-- ===== E-MAIL MONITORING ===== -->
    <div v-if="tab === 'monitor'" class="panel">
      <div class="mon-header">
        <div>
          <h2>📧 Überwachte Websites</h2>
          <p class="sub">Jede Woche automatisch gescannt und per E-Mail gemeldet.</p>
        </div>
        <button class="btn" @click="showAddForm = !showAddForm">+ Website hinzufügen</button>
      </div>

      <!-- Neue Website hinzufügen -->
      <div v-if="showAddForm" class="add-site-form">
        <input v-model="newSiteUrl" class="url-input" placeholder="https://meinewebsite.de" />
        <input v-model="newSiteEmail" type="email" class="url-input" placeholder="bericht@email.de" />
        <button class="btn btn-green" :disabled="addingsite || !newSiteUrl || !newSiteEmail" @click="addSite">
          {{ addingsite ? '…' : 'Speichern' }}
        </button>
      </div>

      <!-- Site-Liste -->
      <div v-if="monitoredSites.length" class="sites-list">
        <div v-for="s in monitoredSites" :key="s.url" class="site-row">
          <div class="site-info">
            <div class="site-url">{{ s.url }}</div>
            <div class="site-meta">📧 {{ s.email }} · Letzter Scan: {{ s.lastScan ? formatDate(s.lastScan) : 'Noch nicht' }}</div>
          </div>
          <div v-if="s.lastScore" :class="['site-grade', gradeClass(s.lastGrade || 'F')]">{{ s.lastGrade }}</div>
          <span :class="['uptime-dot', s.uptime === false ? 'down' : s.uptime === true ? 'up' : 'unknown']" :title="s.uptime === false ? 'Offline!' : s.uptime === true ? 'Online' : 'Unbekannt'">{{ s.uptime === false ? '🔴' : s.uptime === true ? '🟢' : '⚪' }}</span>
          <div class="site-actions">
            <button class="btn btn-sm" @click="scanNow(s.url)">▶ Jetzt scannen</button>
            <button class="btn-remove" @click="removeSite(s.url)">✕</button>
          </div>
        </div>
      </div>

      <div v-else-if="!loadingSites" class="empty-mon">
        <div class="empty-icon">📭</div>
        <p>Noch keine Websites überwacht.</p>
        <p class="sub">Füge deine erste Website hinzu und erhalte wöchentliche Security-Berichte per E-Mail.</p>
      </div>

      <!-- E-Mail-Konfiguration Hinweis -->
      <div class="email-config-hint">
        <strong>⚙️ E-Mail-Versand konfigurieren</strong>
        <p>Für automatische Berichte diese Variablen in Render setzen:</p>
        <div class="env-list">
          <code>SMTP_HOST</code> = z.B. smtp.gmail.com
          <code>SMTP_USER</code> = deine@gmail.com
          <code>SMTP_PASS</code> = App-Passwort
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue'

type Tab = 'scanner' | 'dc' | 'monitor'
const tab = ref<Tab>('scanner')

// ── Security Scanner ──────────────────────────────────────────────────────────
interface CheckResult { label: string; present: boolean; value: string | null; weight: number }
interface SslInfo { valid: boolean; daysRemaining: number | null; expiry: string | null; issuer: string | null; subject: string | null }
interface ScanResult { url: string; https: boolean; score: number; grade: string; checks: CheckResult[]; ssl?: SslInfo }
interface HistoryEntry { date: string; score: number; grade: string; https: boolean }

const scanUrl = ref('')
const scanning = ref(false)
const scanError = ref('')
const scanResult = ref<ScanResult | null>(null)
const scanHistory = ref<HistoryEntry[]>([])
const openFix = ref('')
const fixLang = ref('Apache')
const fixTabs = ['Apache', 'Nginx', 'Node.js', 'WordPress']

const monitorEmail = ref('')
const monitorSaved = ref(false)
const savingMonitor = ref(false)
const monitorError = ref('')

async function runScan() {
  if (!scanUrl.value.trim() || scanning.value) return
  scanning.value = true; scanError.value = ''; scanResult.value = null; monitorSaved.value = false; scanHistory.value = []
  try {
    const res = await fetch('/api/security/scan', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ url: scanUrl.value.trim() }) })
    const data = await res.json()
    if (!res.ok) throw new Error(data.error || 'Scan fehlgeschlagen')
    scanResult.value = data
    // Verlauf laden
    const hRes = await fetch(`/api/security/history?url=${encodeURIComponent(data.url)}`)
    const hData = await hRes.json()
    scanHistory.value = hData.history || []
  } catch (err) { scanError.value = (err as Error).message }
  finally { scanning.value = false }
}

function sslDaysColor(days: number | null) {
  if (days === null) return '#64748b'
  return days <= 7 ? '#f87171' : days <= 30 ? '#fbbf24' : '#4ade80'
}
function historyTrend(entries: HistoryEntry[]) {
  if (entries.length < 2) return ''
  const diff = entries[0].score - entries[1].score
  return diff > 0 ? `▲ +${diff}` : diff < 0 ? `▼ ${diff}` : '→'
}
function trendColor(entries: HistoryEntry[]) {
  if (entries.length < 2) return '#94a3b8'
  const diff = entries[0].score - entries[1].score
  return diff > 0 ? '#4ade80' : diff < 0 ? '#f87171' : '#94a3b8'
}

function toggleFix(label: string) { openFix.value = openFix.value === label ? '' : label }
function truncate(s: string, n: number) { return s.length > n ? s.slice(0, n) + '…' : s }
function gradeClass(g: string) { return g === 'A+' || g === 'A' ? 'grade-a' : g === 'B' ? 'grade-b' : g === 'C' ? 'grade-c' : 'grade-f' }

async function copyCode(text: string) { await navigator.clipboard.writeText(text) }

async function saveMonitor() {
  if (!scanResult.value || !monitorEmail.value) return
  savingMonitor.value = true; monitorError.value = ''
  try {
    const res = await fetch('/api/monitor/add', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ url: scanResult.value.url, email: monitorEmail.value }) })
    const data = await res.json()
    if (!res.ok) throw new Error(data.error)
    monitorSaved.value = true
  } catch (e: unknown) { monitorError.value = (e as Error).message }
  finally { savingMonitor.value = false }
}

function exportPdf() {
  if (!scanResult.value) return
  const r = scanResult.value
  const date = new Date().toLocaleDateString('de-DE', { day: '2-digit', month: 'long', year: 'numeric' })
  const gc = r.grade.startsWith('A') ? '#16a34a' : r.grade === 'B' ? '#65a30d' : r.grade === 'C' ? '#d97706' : '#dc2626'
  const rows = r.checks.map(c => `
    <tr>
      <td style="padding:9px 14px;border-bottom:1px solid #e5e7eb;font-size:1.1em">${c.present ? '✅' : '❌'}</td>
      <td style="padding:9px 14px;border-bottom:1px solid #e5e7eb;font-weight:600;color:${c.present ? '#111' : '#dc2626'}">${c.label}</td>
      <td style="padding:9px 14px;border-bottom:1px solid #e5e7eb;color:#6b7280;font-size:0.85em;word-break:break-all">${c.present ? (c.value || '✓ Vorhanden') : `Fehlt – ${c.weight} Punkte`}</td>
    </tr>`).join('')
  const passed = r.checks.filter(c => c.present).length
  const html = `<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8">
    <title>Security Bericht – ${r.url}</title>
    <style>
      *{box-sizing:border-box;margin:0;padding:0}
      body{font-family:-apple-system,Arial,sans-serif;padding:40px;color:#111;background:#fff;line-height:1.5}
      .header{display:flex;justify-content:space-between;align-items:center;padding-bottom:16px;border-bottom:2px solid #e5e7eb;margin-bottom:28px}
      .brand{font-size:1.2rem;font-weight:700;color:#1d4ed8}
      .date{color:#6b7280;font-size:0.85rem}
      .score-box{display:flex;align-items:center;gap:24px;background:#f9fafb;border:1px solid #e5e7eb;border-radius:12px;padding:20px 28px;margin-bottom:28px}
      .grade{width:76px;height:76px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.8rem;font-weight:800;color:${gc};border:3px solid ${gc};flex-shrink:0}
      .score-big{font-size:2.25rem;font-weight:800;color:#111}
      .score-lbl{color:#6b7280;font-size:0.85rem}
      .score-url{font-size:0.9rem;color:#374151;margin-bottom:6px;word-break:break-all}
      .badge{display:inline-block;padding:3px 12px;border-radius:999px;font-size:0.8rem;font-weight:600}
      .badge-ok{background:#dcfce7;color:#16a34a}
      .badge-fail{background:#fee2e2;color:#dc2626}
      h2{font-size:1rem;font-weight:600;color:#374151;margin-bottom:12px}
      table{width:100%;border-collapse:collapse}
      th{text-align:left;padding:9px 14px;background:#f3f4f6;color:#6b7280;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em}
      .footer{margin-top:40px;padding-top:14px;border-top:1px solid #e5e7eb;color:#9ca3af;font-size:0.8rem;display:flex;justify-content:space-between}
      @media print{body{padding:20px}@page{margin:1.5cm}}
    </style></head><body>
    <div class="header">
      <div class="brand">🛡️ SecureHub – Security Bericht</div>
      <div class="date">${date}</div>
    </div>
    <div class="score-box">
      <div class="grade">${r.grade}</div>
      <div>
        <div class="score-url">${r.url}</div>
        <div><span class="score-big">${r.score}</span> <span class="score-lbl">/ 100 Punkte</span></div>
        <span class="badge ${r.https ? 'badge-ok' : 'badge-fail'}">${r.https ? '🔒 HTTPS aktiv' : '⚠ Kein HTTPS'}</span>
      </div>
    </div>
    <h2>Security-Checks – ${passed} von ${r.checks.length} bestanden</h2>
    <table><thead><tr><th></th><th>Header</th><th>Details</th></tr></thead>
    <tbody>${rows}</tbody></table>
    <div class="footer">
      <span>🛡️ SecureHub Security Scanner · securehub.de</span>
      <span>${r.url} · ${date}</span>
    </div>
    <script>window.onload=()=>{ window.print() }<\/script>
  </body></html>`
  const win = window.open('', '_blank', 'width=860,height=700')
  if (!win) { alert('Bitte Pop-ups für diese Seite erlauben.'); return }
  win.document.write(html)
  win.document.close()
}

// Fix-Anleitungen mit echtem Code
const fixGuides: Record<string, Record<string, string> & { hint: string }> = {
  'HSTS': {
    hint: 'HSTS erzwingt HTTPS und schützt vor Downgrade-Angriffen. Nur aktivieren wenn HTTPS vollständig eingerichtet ist.',
    Apache: `# In .htaccess oder Apache-Config:\nHeader always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"`,
    Nginx: `# In nginx.conf server-Block:\nadd_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;`,
    'Node.js': `// Express Middleware:\napp.use((req, res, next) => {\n  res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');\n  next();\n});`,
    WordPress: `// In functions.php:\nadd_action('send_headers', function() {\n  header('Strict-Transport-Security: max-age=31536000; includeSubDomains');\n});`,
  },
  'Content-Security-Policy': {
    hint: 'CSP verhindert XSS-Angriffe. Starte mit einer lockeren Policy und verschärfe sie schrittweise.',
    Apache: `Header always set Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"`,
    Nginx: `add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'" always;`,
    'Node.js': `res.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self'");`,
    WordPress: `header("Content-Security-Policy: default-src 'self'");`,
  },
  'X-Frame-Options': {
    hint: 'Verhindert Clickjacking-Angriffe indem deine Seite nicht in iFrames eingebettet werden kann.',
    Apache: `Header always set X-Frame-Options "DENY"\n# Oder: "SAMEORIGIN" wenn eigene iFrames nötig`,
    Nginx: `add_header X-Frame-Options "DENY" always;`,
    'Node.js': `res.setHeader('X-Frame-Options', 'DENY');`,
    WordPress: `header('X-Frame-Options: DENY');`,
  },
  'X-Content-Type-Options': {
    hint: 'Verhindert MIME-Type Sniffing. Einfach zu setzen, hohe Wirkung.',
    Apache: `Header always set X-Content-Type-Options "nosniff"`,
    Nginx: `add_header X-Content-Type-Options "nosniff" always;`,
    'Node.js': `res.setHeader('X-Content-Type-Options', 'nosniff');`,
    WordPress: `header('X-Content-Type-Options: nosniff');`,
  },
  'Referrer-Policy': {
    hint: 'Kontrolliert welche Referrer-Informationen bei Links weitergegeben werden.',
    Apache: `Header always set Referrer-Policy "strict-origin-when-cross-origin"`,
    Nginx: `add_header Referrer-Policy "strict-origin-when-cross-origin" always;`,
    'Node.js': `res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');`,
    WordPress: `header('Referrer-Policy: strict-origin-when-cross-origin');`,
  },
  'Permissions-Policy': {
    hint: 'Deaktiviert Browser-Features die deine Seite nicht benötigt (Kamera, Mikrofon, etc.).',
    Apache: `Header always set Permissions-Policy "geolocation=(), microphone=(), camera=(), payment=()"`,
    Nginx: `add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;`,
    'Node.js': `res.setHeader('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');`,
    WordPress: `header('Permissions-Policy: geolocation=(), microphone=(), camera=()');`,
  },
  'X-XSS-Protection': {
    hint: 'Aktiviert den XSS-Filter älterer Browser. Moderne Browser nutzen stattdessen CSP.',
    Apache: `Header always set X-XSS-Protection "1; mode=block"`,
    Nginx: `add_header X-XSS-Protection "1; mode=block" always;`,
    'Node.js': `res.setHeader('X-XSS-Protection', '1; mode=block');`,
    WordPress: `header('X-XSS-Protection: 1; mode=block');`,
  },
}

// ── Rechenzentrum Monitor ─────────────────────────────────────────────────────
interface DcNode { id: string; name: string; role: string; location: string; cpu: number; ram: number; net: number; disk: number; status: 'ok'|'warning'|'critical'; uptime: number }
interface DcAlert { node: string; level: string; msg: string }

const dcNodes = ref<DcNode[]>([])
const dcAlerts = ref<DcAlert[]>([])
const loadingDc = ref(false)
const dcError = ref('')
const lastTs = ref('–')
const autoRefresh = ref(false)
const hasRealAgents = ref(false)
let autoTimer: ReturnType<typeof setInterval> | null = null

// Agent Setup
const showAgentSetup = ref(false)
const agentName = ref('')
const agentToken = ref('')
const registeringAgent = ref(false)
const agentCommand = ref('node dc-agent.mjs --server https://deine-app.onrender.com --token TOKEN --id SERVER-NAME')

async function registerAgent() {
  if (!agentName.value.trim()) return
  registeringAgent.value = true
  try {
    const res = await fetch('/api/dc/register', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: agentName.value }) })
    const data = await res.json()
    if (!res.ok) throw new Error(data.error)
    agentToken.value = data.token
    agentCommand.value = `node dc-agent.mjs --server ${window.location.origin} --token ${data.token} --id "${agentName.value.replace(/\s+/g, '-').toLowerCase()}"`
  } catch (e: unknown) { console.error(e) }
  finally { registeringAgent.value = false }
}

async function loadMetrics() {
  loadingDc.value = true; dcError.value = ''
  try {
    const res = await fetch('/api/dc/metrics')
    const data = await res.json()
    if (!res.ok) throw new Error(data.error)
    dcNodes.value = data.nodes; dcAlerts.value = data.alerts
    hasRealAgents.value = !!data.hasRealAgents
    lastTs.value = new Date(data.ts).toLocaleTimeString('de-DE')
  } catch (err) { dcError.value = (err as Error).message }
  finally { loadingDc.value = false }
}

function toggleAuto() {
  if (autoTimer) { clearInterval(autoTimer); autoTimer = null }
  if (autoRefresh.value) autoTimer = setInterval(loadMetrics, 5000)
}
function barClass(v: number) { return v > 90 ? 'critical' : v > 75 ? 'warning' : 'ok' }
onUnmounted(() => { if (autoTimer) clearInterval(autoTimer) })

// ── Monitoring ─────────────────────────────────────────────────────────────────
interface MonSite { url: string; email: string; lastScore?: number; lastGrade?: string; lastScan?: string; uptime?: boolean | null }

const monitoredSites = ref<MonSite[]>([])
const loadingSites = ref(false)
const showAddForm = ref(false)
const newSiteUrl = ref('')
const newSiteEmail = ref('')
const addingsite = ref(false)

async function loadSites() {
  loadingSites.value = true
  try {
    const res = await fetch('/api/monitor/list')
    const data = await res.json()
    monitoredSites.value = data.sites || []
  } catch { /* ignore */ }
  finally { loadingSites.value = false }
}

async function addSite() {
  addingsite.value = true
  try {
    const res = await fetch('/api/monitor/add', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ url: newSiteUrl.value, email: newSiteEmail.value }) })
    if (res.ok) { newSiteUrl.value = ''; newSiteEmail.value = ''; showAddForm.value = false; await loadSites() }
  } catch { /* ignore */ }
  finally { addingsite.value = false }
}

async function removeSite(url: string) {
  await fetch('/api/monitor/remove', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ url }) })
  await loadSites()
}

async function scanNow(url: string) {
  await fetch('/api/monitor/scan-now', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ url }) })
  setTimeout(loadSites, 3000)
}

function formatDate(d: string) { return new Date(d).toLocaleDateString('de-DE') }
</script>

<style scoped>
.sec-page { max-width: 1100px; margin: 0 auto; padding: 1.5rem 1rem; }
.page-header { margin-bottom: 1.5rem; }
.page-header h1 { font-size: 1.6rem; font-weight: 700; color: #e2e8f0; margin: 0 0 0.3rem; }
.sub { color: #94a3b8; font-size: 0.9rem; margin: 0; }

.tabs { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.tab-btn { padding: 0.6rem 1.4rem; border-radius: 8px; border: 1px solid #334155; background: #1e293b; color: #94a3b8; cursor: pointer; font-size: 0.9rem; transition: all 0.2s; }
.tab-btn.active { background: #3b82f6; border-color: #3b82f6; color: #fff; }
.tab-btn:hover:not(.active) { border-color: #60a5fa; color: #e2e8f0; }

.panel { animation: fadeIn 0.2s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: none; } }

.scan-box { display: flex; gap: 0.75rem; margin-bottom: 1rem; }
.url-input { flex: 1; padding: 0.7rem 1rem; border-radius: 10px; border: 1px solid #334155; background: #0f172a; color: #e2e8f0; font-size: 0.95rem; }
.url-input:focus { outline: none; border-color: #3b82f6; }
.error-msg { color: #f87171; background: rgba(248,113,113,0.1); border: 1px solid rgba(248,113,113,0.3); padding: 0.6rem 1rem; border-radius: 8px; margin-bottom: 1rem; font-size: 0.88rem; }

/* Score */
.scan-result { margin-top: 1rem; }
.score-row { display: flex; align-items: center; gap: 1.25rem; background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 1.2rem 1.5rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.grade-badge { width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; font-weight: 700; flex-shrink: 0; }
.grade-a { background: #052e16; color: #4ade80; border: 2px solid #4ade80; }
.grade-b { background: #0c4a6e; color: #38bdf8; border: 2px solid #38bdf8; }
.grade-c { background: #451a03; color: #fb923c; border: 2px solid #fb923c; }
.grade-f { background: #3f0000; color: #f87171; border: 2px solid #f87171; }
.score-num { font-size: 1.9rem; font-weight: 700; color: #e2e8f0; }
.score-max { font-size: 0.95rem; color: #64748b; }
.score-sub { font-size: 0.78rem; color: #64748b; word-break: break-all; }
.https-badge { padding: 0.35rem 0.85rem; border-radius: 999px; font-size: 0.82rem; font-weight: 600; }
.https-badge.ok { background: rgba(74,222,128,0.15); color: #4ade80; border: 1px solid rgba(74,222,128,0.3); }
.https-badge.fail { background: rgba(248,113,113,0.15); color: #f87171; border: 1px solid rgba(248,113,113,0.3); }
.btn-icon { padding: 0.4rem 0.9rem; border-radius: 8px; border: 1px solid #334155; background: #1e293b; color: #94a3b8; cursor: pointer; font-size: 0.82rem; margin-left: auto; }
.btn-icon:hover { border-color: #60a5fa; color: #e2e8f0; }

/* Checks mit Fix-Guides */
.checks-list { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 1.5rem; }
.check-row { background: #1e293b; border: 1px solid #334155; border-radius: 10px; overflow: hidden; }
.check-row.ok { border-color: rgba(74,222,128,0.2); }
.check-row.missing { border-color: rgba(248,113,113,0.2); }
.check-main { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; }
.check-icon { font-size: 1.1rem; flex-shrink: 0; }
.check-info { flex: 1; min-width: 0; }
.check-label { font-weight: 600; color: #e2e8f0; font-size: 0.88rem; display: block; }
.check-val { font-size: 0.72rem; color: #64748b; word-break: break-all; }
.check-missing { font-size: 0.75rem; color: #f87171; }
.btn-fix-toggle { padding: 0.3rem 0.75rem; border-radius: 6px; border: 1px solid rgba(251,191,36,0.4); background: rgba(251,191,36,0.08); color: #fbbf24; cursor: pointer; font-size: 0.78rem; white-space: nowrap; flex-shrink: 0; }
.btn-fix-toggle:hover { background: rgba(251,191,36,0.15); }

/* Fix-Anleitung */
.fix-guide { border-top: 1px solid #334155; padding: 1rem; background: #0f172a; }
.fix-tabs { display: flex; gap: 0.4rem; margin-bottom: 0.75rem; }
.fix-tab { padding: 0.25rem 0.75rem; border-radius: 6px; border: 1px solid #334155; background: transparent; color: #64748b; cursor: pointer; font-size: 0.8rem; }
.fix-tab.active { background: #1e293b; color: #e2e8f0; border-color: #475569; }
.fix-code { position: relative; background: #020817; border: 1px solid #1e293b; border-radius: 8px; }
.fix-code pre { margin: 0; padding: 0.85rem 2.5rem 0.85rem 1rem; font-size: 0.8rem; color: #94a3b8; white-space: pre-wrap; word-break: break-all; line-height: 1.6; font-family: monospace; }
.btn-copy-code { position: absolute; top: 0.5rem; right: 0.5rem; padding: 0.2rem 0.5rem; border-radius: 5px; border: 1px solid #334155; background: #1e293b; color: #64748b; cursor: pointer; font-size: 0.72rem; }
.btn-copy-code:hover { color: #e2e8f0; }
.fix-hint { font-size: 0.78rem; color: #64748b; margin: 0.6rem 0 0; line-height: 1.5; }

/* SSL-Zertifikat Box */
.ssl-box { display: flex; align-items: center; justify-content: space-between; background: #0f172a; border: 1px solid rgba(96,165,250,0.2); border-radius: 10px; padding: 0.85rem 1.1rem; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.75rem; }
.ssl-left { display: flex; align-items: center; gap: 0.75rem; }
.ssl-icon { font-size: 1.5rem; }
.ssl-title { font-weight: 600; color: #e2e8f0; font-size: 0.88rem; }
.ssl-issuer { font-size: 0.75rem; color: #64748b; }
.ssl-right { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }
.ssl-days { font-weight: 700; font-size: 0.9rem; }
.ssl-expiry { font-size: 0.75rem; color: #64748b; }
.ssl-warn { font-size: 0.75rem; background: rgba(251,191,36,0.15); color: #fbbf24; padding: 0.15rem 0.6rem; border-radius: 999px; border: 1px solid rgba(251,191,36,0.3); }

/* Scan-Verlauf / History */
.history-box { background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 0.85rem 1.1rem; margin-bottom: 1rem; }
.history-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem; font-size: 0.85rem; color: #94a3b8; }
.trend-badge { font-weight: 700; font-size: 0.88rem; }
.history-dots { display: flex; gap: 0.6rem; flex-wrap: wrap; }
.history-dot { display: flex; flex-direction: column; align-items: center; gap: 0.25rem; }
.dot-grade { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.72rem; font-weight: 700; cursor: default; }
.dot-score { font-size: 0.68rem; color: #64748b; }

/* Monitoring speichern */
.monitor-save { background: #0f172a; border: 1px solid rgba(59,130,246,0.2); border-radius: 12px; padding: 1.25rem; }
.monitor-save h3 { margin: 0 0 0.35rem; color: #e2e8f0; font-size: 1rem; }
.monitor-save p { color: #94a3b8; font-size: 0.85rem; margin: 0 0 0.85rem; }
.monitor-form { display: flex; gap: 0.75rem; flex-wrap: wrap; }
.mon-input { flex: 1; min-width: 200px; padding: 0.6rem 0.9rem; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: #e2e8f0; font-size: 0.9rem; }
.btn-green { background: #16a34a !important; border-color: #16a34a !important; }
.monitor-ok { color: #4ade80; font-size: 0.9rem; }

/* Info-Cards */
.info-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 1rem; margin-top: 1rem; }
.info-card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 1.25rem; }
.info-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.info-card h3 { margin: 0 0 0.5rem; color: #e2e8f0; font-size: 1rem; }
.info-card ul { list-style: none; padding: 0; margin: 0; }
.info-card li { font-size: 0.82rem; color: #94a3b8; padding: 0.2rem 0; }
.info-card li::before { content: '• '; color: #3b82f6; }

/* DC Monitor */
.dc-toolbar { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap; }
.dc-ts { font-size: 0.82rem; color: #64748b; }
.badge-live { padding: 0.2rem 0.7rem; border-radius: 999px; font-size: 0.75rem; background: rgba(74,222,128,0.15); color: #4ade80; border: 1px solid rgba(74,222,128,0.3); }
.badge-sim { padding: 0.2rem 0.7rem; border-radius: 999px; font-size: 0.75rem; background: rgba(96,165,250,0.15); color: #60a5fa; border: 1px solid rgba(96,165,250,0.3); }
.btn-outline-blue { border-color: rgba(59,130,246,0.4) !important; color: #60a5fa !important; }
.btn-outline-blue:hover { border-color: #3b82f6 !important; }
.agent-setup { background: #0f172a; border: 1px solid rgba(59,130,246,0.25); border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 1.5rem; }
.agent-setup h3 { color: #e2e8f0; margin: 0 0 0.35rem; font-size: 1rem; }
.agent-steps { display: flex; flex-direction: column; gap: 1.25rem; margin-top: 1rem; }
.agent-step { display: flex; gap: 1rem; align-items: flex-start; }
.step-num { width: 28px; height: 28px; border-radius: 50%; background: #3b82f6; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; font-weight: 700; flex-shrink: 0; }
.agent-step strong { color: #e2e8f0; font-size: 0.9rem; display: block; margin-bottom: 0.5rem; }
.agent-reg-form { display: flex; gap: 0.6rem; flex-wrap: wrap; margin-bottom: 0.6rem; }
.token-box { display: flex; align-items: center; gap: 0.5rem; background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 0.5rem 0.75rem; margin-top: 0.4rem; }
.token-label { font-size: 0.75rem; color: #64748b; flex-shrink: 0; }
.token-box code { color: #60a5fa; font-size: 0.82rem; flex: 1; word-break: break-all; }
.btn-sm { padding: 0.35rem 0.8rem; font-size: 0.82rem; }
.auto-label { display: flex; align-items: center; gap: 0.4rem; font-size: 0.82rem; color: #94a3b8; cursor: pointer; }
.alert-bar { border-radius: 10px; padding: 0.7rem 1rem; margin-bottom: 1rem; display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; background: rgba(15,23,42,0.8); border: 1px solid #334155; }
.alert-bar.ok { border-color: rgba(74,222,128,0.3); color: #4ade80; font-size: 0.88rem; }
.alert-item { font-size: 0.85rem; color: #e2e8f0; }
.alert-item.critical { color: #f87171; }
.alert-item.warning { color: #fbbf24; }
.nodes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
.node-card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 1rem 1.2rem; }
.node-card.warning { border-color: rgba(251,191,36,0.4); }
.node-card.critical { border-color: rgba(248,113,113,0.4); }
.node-head { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem; }
.status-dot { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }
.status-dot.ok { background: #4ade80; box-shadow: 0 0 6px #4ade80; }
.status-dot.warning { background: #fbbf24; box-shadow: 0 0 6px #fbbf24; }
.status-dot.critical { background: #f87171; box-shadow: 0 0 6px #f87171; }
.node-role { margin-left: auto; font-size: 0.72rem; color: #64748b; background: #0f172a; padding: 0.1rem 0.5rem; border-radius: 999px; }
.node-loc { font-size: 0.75rem; color: #64748b; margin-bottom: 0.75rem; }
.metrics { display: flex; flex-direction: column; gap: 0.4rem; }
.metric { display: flex; align-items: center; gap: 0.5rem; }
.metric-label { width: 30px; font-size: 0.7rem; color: #64748b; flex-shrink: 0; }
.metric-bar { flex: 1; height: 5px; background: #0f172a; border-radius: 3px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 3px; transition: width 0.5s ease; }
.bar-fill.ok { background: #4ade80; }
.bar-fill.warning { background: #fbbf24; }
.bar-fill.critical { background: #f87171; }
.bar-fill.net { background: #60a5fa; }
.metric-val { width: 38px; font-size: 0.72rem; color: #94a3b8; text-align: right; flex-shrink: 0; }
.node-uptime { font-size: 0.72rem; color: #475569; margin-top: 0.75rem; }

/* Monitoring Tab */
.mon-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; margin-bottom: 1.25rem; flex-wrap: wrap; }
.mon-header h2 { margin: 0 0 0.25rem; font-size: 1.2rem; color: #e2e8f0; }
.add-site-form { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1.25rem; background: #0f172a; padding: 1rem; border-radius: 10px; border: 1px solid #334155; }
.sites-list { display: flex; flex-direction: column; gap: 0.75rem; margin-bottom: 1.5rem; }
.site-row { display: flex; align-items: center; gap: 1rem; background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 0.9rem 1.1rem; flex-wrap: wrap; }
.site-info { flex: 1; min-width: 0; }
.site-url { font-weight: 600; color: #e2e8f0; font-size: 0.9rem; }
.site-meta { font-size: 0.78rem; color: #64748b; margin-top: 0.2rem; }
.site-grade { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.9rem; flex-shrink: 0; }
.uptime-dot { font-size: 1rem; flex-shrink: 0; cursor: default; }
.site-actions { display: flex; gap: 0.5rem; align-items: center; }
.btn-remove { padding: 0.3rem 0.6rem; border-radius: 6px; border: 1px solid rgba(248,113,113,0.3); background: transparent; color: #f87171; cursor: pointer; font-size: 0.82rem; }
.btn-remove:hover { background: rgba(248,113,113,0.1); }
.empty-mon { text-align: center; padding: 3rem 1rem; color: #64748b; }
.empty-icon { font-size: 3rem; margin-bottom: 0.75rem; }
.empty-mon p { margin: 0 0 0.4rem; }
.email-config-hint { background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 1rem 1.25rem; margin-top: 1.5rem; }
.email-config-hint strong { color: #e2e8f0; display: block; margin-bottom: 0.4rem; font-size: 0.9rem; }
.email-config-hint p { color: #64748b; font-size: 0.82rem; margin: 0 0 0.5rem; }
.env-list { display: flex; flex-direction: column; gap: 0.3rem; }
.env-list code { background: #1e293b; padding: 0.2rem 0.5rem; border-radius: 5px; font-size: 0.8rem; color: #60a5fa; }

@media (max-width: 600px) {
  .scan-box, .monitor-form, .add-site-form { flex-direction: column; }
  .score-row { gap: 0.75rem; }
}
</style>
