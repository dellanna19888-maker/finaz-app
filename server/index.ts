// API-Backend für finaz-app: KI-Assistent (Claude) + Compliance-Gateway.
// Mit tsx ausführen:  npm run api   (Dev: npm run api:dev, Demo: npm run demo)
import express from 'express'
import type { Request, Response } from 'express'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import Anthropic from '@anthropic-ai/sdk'
import nodemailer from 'nodemailer'
import 'dotenv/config'
import { evaluate, mapCountryToJurisdiction } from '../src/compliance/gateway'
import { writeDecisionLog, readRecentDecisions } from './logger'

// ── Affiliate-Datenspeicher (JSON-Datei, DB-unabhängig) ──────────────────────
const AFF_FILE = join(dirname(fileURLToPath(import.meta.url)), 'affiliates.json')

interface AffConversion { date: string; plan: string; commission: number }
interface Affiliate {
  code: string; name: string; email: string; website: string
  clicks: number; conversions: number; earnings: number
  recentConversions: AffConversion[]; createdAt: string
}

function loadAffiliates(): Record<string, Affiliate> {
  try { return JSON.parse(readFileSync(AFF_FILE, 'utf-8')) } catch { return {} }
}
function saveAffiliates(data: Record<string, Affiliate>) {
  writeFileSync(AFF_FILE, JSON.stringify(data, null, 2))
}
function generateCode(name: string): string {
  const base = name.toUpperCase().replace(/[^A-Z]/g, '').slice(0, 4) || 'AFF'
  return base + Math.floor(1000 + Math.random() * 9000)
}

const __dirname = dirname(fileURLToPath(import.meta.url))
const PORT = Number(process.env.API_PORT || process.env.PORT || 3001)
const MODEL = process.env.CLAUDE_MODEL || 'claude-opus-4-8'
const MAX_CHARS = Number(process.env.COMPLIANCE_MAX_CHARS) || 50000

const app = express()
app.set('trust proxy', true)
app.use(express.json({ limit: '2mb' }))

const envClient = process.env.ANTHROPIC_API_KEY ? new Anthropic() : null
const GEMINI_MODEL = process.env.GEMINI_MODEL || 'gemini-2.0-flash'

interface ModelMessage {
  role: 'user' | 'assistant'
  content: string
}

// Streamt eine Modell-Antwort als Server-Sent Events (Events: delta/done/error).
// Provider-Wahl: Anthropic (Claude) wenn ein Anthropic-Key vorhanden ist, sonst
// Google Gemini (kostenloser Tier). "Bring your own key": pro Anfrage darf der
// Client eigene Keys senden (x-anthropic-key / x-gemini-key); sonst greifen die
// Server-Keys aus .env (ANTHROPIC_API_KEY / GEMINI_API_KEY).
async function streamModel(
  req: Request,
  res: Response,
  opts: { system: string; messages: ModelMessage[]; userAnthropicKey: string; userGeminiKey: string; maxTokens?: number },
): Promise<void> {
  const { system, messages, userAnthropicKey, userGeminiKey, maxTokens = 4096 } = opts
  const aKey = userAnthropicKey || process.env.ANTHROPIC_API_KEY || ''
  const gKey = userGeminiKey || process.env.GEMINI_API_KEY || ''
  if (!aKey && !gKey) {
    res.status(400).json({
      error: 'Kein API-Key. Hinterlege einen Anthropic- ODER (kostenlosen) Gemini-Key in den Einstellungen (⚙️).',
    })
    return
  }

  res.setHeader('Content-Type', 'text/event-stream')
  res.setHeader('Cache-Control', 'no-cache')
  res.setHeader('Connection', 'keep-alive')
  const send = (payload: unknown) => res.write(`data: ${JSON.stringify(payload)}\n\n`)

  const ac = new AbortController()
  let anthropicStream: ReturnType<Anthropic['messages']['stream']> | undefined
  req.on('close', () => {
    try {
      ac.abort()
    } catch {
      /* ignore */
    }
    try {
      anthropicStream?.abort()
    } catch {
      /* ignore */
    }
  })

  try {
    if (aKey) {
      const ai = userAnthropicKey ? new Anthropic({ apiKey: userAnthropicKey }) : (envClient ?? new Anthropic({ apiKey: aKey }))
      anthropicStream = ai.messages.stream({ model: MODEL, max_tokens: maxTokens, system, messages })
      anthropicStream.on('text', (delta: string) => send({ type: 'delta', text: delta }))
      await anthropicStream.finalMessage()
    } else {
      await streamGemini({ apiKey: gKey, system, messages, maxTokens, send, signal: ac.signal })
    }
    send({ type: 'done' })
  } catch (err) {
    const message =
      err instanceof Anthropic.APIError
        ? `Claude-API-Fehler (${err.status}): ${err.message}`
        : (err as Error)?.message || 'Unbekannter Fehler'
    send({ type: 'error', message })
  } finally {
    res.end()
  }
}

// Google Gemini (REST, SSE-Streaming). Mappt assistant→model und system→system_instruction.
async function streamGemini(opts: {
  apiKey: string
  system: string
  messages: ModelMessage[]
  maxTokens: number
  send: (payload: unknown) => void
  signal: AbortSignal
}): Promise<void> {
  const { apiKey, system, messages, maxTokens, send, signal } = opts
  const contents = messages.map((m) => ({ role: m.role === 'assistant' ? 'model' : 'user', parts: [{ text: m.content }] }))
  const body = {
    contents,
    ...(system ? { system_instruction: { parts: [{ text: system }] } } : {}),
    generationConfig: { maxOutputTokens: maxTokens },
  }
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:streamGenerateContent?alt=sse&key=${encodeURIComponent(apiKey)}`
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal,
  })
  if (!resp.ok || !resp.body) {
    let detail = ''
    try {
      detail = ((await resp.json()) as { error?: { message?: string } })?.error?.message || ''
    } catch {
      /* ignore */
    }
    throw new Error(`Gemini-API-Fehler (${resp.status})${detail ? ': ' + detail : ''}`)
  }
  const reader = resp.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  for (;;) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true }).replace(/\r/g, '')
    const parts = buffer.split('\n\n')
    buffer = parts.pop() ?? ''
    for (const part of parts) {
      const line = part.split('\n').find((l) => l.startsWith('data:'))
      if (!line) continue
      const json = line.slice(5).trim()
      if (!json || json === '[DONE]') continue
      try {
        const obj = JSON.parse(json) as { candidates?: { content?: { parts?: { text?: string }[] } }[] }
        const text = (obj.candidates?.[0]?.content?.parts || []).map((p) => p.text || '').join('')
        if (text) send({ type: 'delta', text })
      } catch {
        /* unvollständiges JSON ignorieren */
      }
    }
  }
}

// Optionale, offline GeoIP-Auflösung der Client-IP über `geoip-lite`.
// Standardmäßig AUS: Das Paket lädt ~150 MB Daten in den Speicher – auf kleinen
// Instanzen (z. B. Render Free, 512 MB) würde das den Start belasten. Mit
// ENABLE_GEOIP=1 wird es im HINTERGRUND geladen (blockiert den Serverstart nie);
// bis es bereit ist – oder wenn aus – greifen CDN-Header bzw. das DEFAULT-Profil.
type GeoipLookup = (ip: string) => { country?: string } | null
let geoipLookup: GeoipLookup | null = null
const GEOIP_ENABLED = /^(1|true|yes|on)$/i.test(process.env.ENABLE_GEOIP || '')
async function loadGeoip(): Promise<void> {
  if (!GEOIP_ENABLED) return
  try {
    const mod = (await import('geoip-lite')) as unknown as {
      default?: { lookup?: GeoipLookup }
      lookup?: GeoipLookup
    }
    geoipLookup = mod.default?.lookup ?? mod.lookup ?? null
    console.log('GeoIP aktiv (geoip-lite geladen).')
  } catch {
    geoipLookup = null
  }
}

function clientIp(req: Request): string | null {
  const xff = req.headers['x-forwarded-for']
  if (xff) return String(xff).split(',')[0].trim()
  return req.socket?.remoteAddress || null
}

function countryFromIp(req: Request): string | null {
  if (!geoipLookup) return null
  const ip = clientIp(req)
  if (!ip) return null
  try {
    return geoipLookup(ip)?.country || null
  } catch {
    return null
  }
}

// GEO-Identifikation: erzwungenes Profil → CDN/Länder-Header → echte GeoIP-
// Auflösung der Client-IP (optional) → restriktivstes Fallback-Profil (DSGVO).
function resolveJurisdiction(req: Request): string {
  const forced = process.env.COMPLIANCE_FORCE_JURISDICTION
  if (forced) return forced.toUpperCase()
  const h = req.headers
  const country =
    (h['x-geo-country'] as string) ||
    (h['cf-ipcountry'] as string) ||
    (h['x-vercel-ip-country'] as string) ||
    (h['x-appengine-country'] as string) ||
    countryFromIp(req) ||
    null
  return mapCountryToJurisdiction(country)
}

const SYSTEM_PROMPT = [
  'Du bist ein hilfreicher Assistent für Markdown-Texte, Notizen und Wissensartikel.',
  'Regeln:',
  '- Antworte ausschließlich in sauberem Markdown, ohne einleitende oder abschließende Kommentare.',
  '- Umschließe das gesamte Dokument NICHT mit ``` Code-Fences.',
  '- Erfinde keine Fakten; nutze nur die gelieferten Inhalte.',
  '- Keine verbindliche Steuer- oder Rechtsberatung; weise bei Bedarf kurz darauf hin.',
  '- Antworte auf Deutsch, sofern nicht ausdrücklich eine andere Sprache verlangt wird.',
  '- Antworte direkt mit dem fertigen Inhalt (keine Gedanken, keine Meta-Erklärungen).',
].join('\n')

// System-Prompt der "Zentrale" (KI-Schaltzentrale + Steuerung per Aktionsblöcken).
const CHAT_SYSTEM_PROMPT = [
  'Du bist die zentrale Schaltzentrale ("Zentrale") eines KI-Hubs für Online-Creator.',
  'Du hilfst bei: (1) Content – Ideen, Hooks, Skripte, Captions, Hashtags, Wochen-/Themenpläne;',
  '(2) Content-Plan/Pipeline – Inhalte als Einträge mit Plattform und Status führen;',
  '(3) Wissen/Notizen schreiben & organisieren; (4) Support – Community-/Sponsor-Fragen',
  'sachlich aus der Wissensbasis im Snapshot beantworten.',
  '(5) Kanal-Check – aus „Mein Kanal" + „Konkurrenz" im Snapshot analysierst du, wie der Kanal läuft,',
  'gibst konkrete Verbesserungen und Konkurrenz-Insights (keine erfundenen Zahlen).',
  'Du erhältst bei jeder Anfrage einen Snapshot des App-Zustands. Nutze nur diese Daten, erfinde keine Fakten.',
  'Antworte auf Deutsch, in klarem Markdown, kompakt und konkret.',
  '',
  'Status-Pipeline eines Inhalts: idee → skript → aufnahme → schnitt → live (veröffentlicht).',
  '',
  'AKTIONEN: Möchte der Nutzer etwas TUN, erkläre es kurz und gib GENAU EINEN Aktionsblock aus –',
  'ein Code-Fence mit Sprache "action" und gültigem JSON:',
  '```action',
  '{"tool":"<name>","args":{ ... }}',
  '```',
  'Verfügbare tools und args:',
  '- add_task: {"title":"...","platform":"YouTube|TikTok|Instagram|… optional","status":"idee|skript|aufnahme|schnitt|live optional","priority":"low|normal|high optional","project":"optional","due":"YYYY-MM-DD optional","notes":"optional"}',
  '- set_status: {"id":"<id aus dem Snapshot>","status":"idee|skript|aufnahme|schnitt|live"}',
  '- complete_task: {"id":"<id>"}  (= als veröffentlicht markieren)',
  '- reopen_task: {"id":"<id>"}',
  '- update_task: {"id":"<id>","title":"opt","platform":"opt","status":"opt","priority":"opt","project":"opt","due":"opt","notes":"opt"}',
  '- delete_task: {"id":"<id>"}',
  '- append_note: {"content":"Markdown, wird an die Wissensbasis/Notiz angehängt"}',
  '- navigate: {"to":"/tasks"|"/channel"|"/notes"|"/compliance"|"/settings"|"/"}',
  '- compliance_check: {"text":"zu prüfender Inhalt","action":"optional","jurisdiction":"EU"|"UK"|"US"|"DEFAULT" optional}',
  'Ideen, Skripte, Captions, Hashtags, Pläne und Support-Antworten lieferst du direkt als Markdown – ohne Aktionsblock.',
  'Regeln: Nur IDs/Projekte aus dem Snapshot verwenden. Höchstens EIN Aktionsblock pro Antwort. Aktionen NICHT selbst',
  'ausführen – der Block wird dem Nutzer zur Bestätigung angezeigt. Ist keine Aktion nötig, gib keinen Block aus.',
].join('\n')

function buildPrompt(action: string, text: string, instruction: string, language: string): string | null {
  const doc = text && text.trim() ? `\n\nDaten / Dokument:\n"""\n${text}\n"""` : ''
  switch (action) {
    case 'finance':
      return `Aufgabe: ${instruction || 'Erstelle einen kompakten, verständlichen Finanzüberblick.'}\n\nNutze die folgenden aggregierten Finanzdaten und antworte als übersichtliches Markdown (Überschriften, kurze Absätze, bei Bedarf Listen/Tabellen).${doc}`
    case 'generate':
      return `Erstelle ein neues, vollständiges Markdown-Dokument zu folgendem Wunsch:\n${instruction || 'Ein nützliches Beispiel-Dokument.'}`
    case 'improve':
      return `Überarbeite und verbessere das folgende Markdown (Klarheit, Struktur, Rechtschreibung, Formatierung).${instruction ? ` Zusätzliche Vorgabe: ${instruction}.` : ''}${doc}`
    case 'continue':
      return `Schreibe das folgende Markdown-Dokument sinnvoll weiter. Gib NUR die Fortsetzung zurück, ohne den vorhandenen Text zu wiederholen.${instruction ? ` Vorgabe: ${instruction}.` : ''}${doc}`
    case 'summarize':
      return `Fasse das folgende Markdown-Dokument prägnant als Markdown zusammen (Kernpunkte als Liste).${doc}`
    case 'translate':
      return `Übersetze das folgende Markdown-Dokument nach ${language || 'Englisch'}. Behalte die Markdown-Formatierung exakt bei.${doc}`
    default:
      return null
  }
}

app.get('/api/health', (_req: Request, res: Response) => {
  res.json({ ok: true, envKey: !!process.env.ANTHROPIC_API_KEY, gemini: !!process.env.GEMINI_API_KEY, geoip: !!geoipLookup })
})

// Security Scanner: prüft HTTP-Sicherheitsheader + HTTPS einer URL.
app.post('/api/security/scan', async (req: Request, res: Response) => {
  const { url } = req.body ?? {}
  if (!url || typeof url !== 'string') return res.status(400).json({ error: 'URL fehlt.' })

  let target = url.trim()
  if (!/^https?:\/\//i.test(target)) target = 'https://' + target

  try {
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), 8000)

    let response: Response
    let usedHttps = target.startsWith('https')
    try {
      response = await fetch(target, { method: 'HEAD', signal: controller.signal, redirect: 'follow' })
    } catch {
      if (usedHttps) {
        const httpFallback = target.replace(/^https/i, 'http')
        response = await fetch(httpFallback, { method: 'HEAD', signal: controller.signal, redirect: 'follow' })
        usedHttps = false
      } else throw new Error('Verbindung fehlgeschlagen.')
    }
    clearTimeout(timer)

    const headers = Object.fromEntries(response.headers.entries())
    const checks = [
      { key: 'strict-transport-security', label: 'HSTS', weight: 20 },
      { key: 'content-security-policy', label: 'Content-Security-Policy', weight: 20 },
      { key: 'x-frame-options', label: 'X-Frame-Options', weight: 15 },
      { key: 'x-content-type-options', label: 'X-Content-Type-Options', weight: 15 },
      { key: 'referrer-policy', label: 'Referrer-Policy', weight: 10 },
      { key: 'permissions-policy', label: 'Permissions-Policy', weight: 10 },
      { key: 'x-xss-protection', label: 'X-XSS-Protection', weight: 10 },
    ]

    const results = checks.map((c) => ({
      label: c.label,
      present: !!headers[c.key],
      value: headers[c.key] || null,
      weight: c.weight,
    }))

    let score = usedHttps ? 10 : 0
    for (const r of results) if (r.present) score += r.weight

    const grade = score >= 90 ? 'A+' : score >= 80 ? 'A' : score >= 70 ? 'B' : score >= 50 ? 'C' : score >= 30 ? 'D' : 'F'

    res.json({ url: target, https: usedHttps, score, grade, checks: results, status: response.status, responseTime: Date.now() })
  } catch (err) {
    res.status(502).json({ error: (err as Error)?.message || 'Scan fehlgeschlagen.' })
  }
})

// ── Data Center Monitor: Real Agents + Simulated Fallback ────────────────────
const DC_AGENTS_FILE = join(dirname(fileURLToPath(import.meta.url)), 'dc-agents.json')

interface AgentRecord { id: string; name: string; token: string; role: string; location: string; registeredAt: string }
interface AgentReport { id: string; name: string; role: string; location: string; cpu: number; ram: number; net: number; disk: number; uptime: number; ts: string }

const agentReports = new Map<string, AgentReport>()

function loadAgents(): Record<string, AgentRecord> {
  try { return JSON.parse(readFileSync(DC_AGENTS_FILE, 'utf-8')) } catch { return {} }
}
function saveAgents(data: Record<string, AgentRecord>) {
  writeFileSync(DC_AGENTS_FILE, JSON.stringify(data, null, 2))
}
function generateToken(): string {
  return Array.from(crypto.getRandomValues(new Uint8Array(24))).map(b => b.toString(16).padStart(2, '0')).join('')
}

const SIMULATED_DC_NODES = [
  { id: 'sim-web-01', name: 'Web Server 01 (Demo)', role: 'Web', location: 'Frankfurt' },
  { id: 'sim-db-01', name: 'Database (Demo)', role: 'Database', location: 'Amsterdam' },
  { id: 'sim-cache-01', name: 'Redis Cache (Demo)', role: 'Cache', location: 'Frankfurt' },
]
function simMetric(base: number, variance: number) {
  return Math.min(100, Math.max(0, base + (Math.random() - 0.5) * variance * 2))
}

// Agent registrieren – gibt einen Token zurück
app.post('/api/dc/register', (req: Request, res: Response) => {
  const { name } = req.body ?? {}
  if (!name) return res.status(400).json({ error: 'Name erforderlich.' })
  const agents = loadAgents()
  const token = generateToken()
  const id = name.toLowerCase().replace(/[^a-z0-9]/g, '-').replace(/-+/g, '-').slice(0, 32)
  agents[token] = { id, name, token, role: 'Server', location: '', registeredAt: new Date().toISOString() }
  saveAgents(agents)
  console.log(`DC Agent registriert: ${name} (${id})`)
  res.json({ ok: true, token, id })
})

// Agent sendet Metriken
app.post('/api/dc/report', (req: Request, res: Response) => {
  const { token, id, name, role, location, cpu, ram, net, disk, uptime, ts } = req.body ?? {}
  if (!token || !id) return res.status(400).json({ error: 'token und id erforderlich.' })
  const agents = loadAgents()
  if (!agents[token]) return res.status(401).json({ error: 'Ungültiger Token.' })
  agentReports.set(id, { id, name: name || id, role: role || 'Server', location: location || '', cpu: +cpu || 0, ram: +ram || 0, net: +net || 0, disk: +disk || 0, uptime: +uptime || 0, ts: ts || new Date().toISOString() })
  res.json({ ok: true })
})

app.get('/api/dc/metrics', (_req: Request, res: Response) => {
  const now = Date.now()
  const STALE_MS = 90_000 // Agent gilt nach 90s als offline

  // Echte Agent-Berichte (nicht älter als 90s)
  const realNodes = Array.from(agentReports.values())
    .filter(r => now - new Date(r.ts).getTime() < STALE_MS)
    .map(r => {
      const status = r.cpu > 90 || r.ram > 95 ? 'critical' : r.cpu > 75 || r.ram > 85 ? 'warning' : 'ok' as const
      return { ...r, status }
    })

  // Simulierte Nodes als Fallback wenn keine echten vorhanden
  const simNodes = realNodes.length === 0 ? SIMULATED_DC_NODES.map(n => {
    const cpu = simMetric(n.role === 'Database' ? 45 : 30, 20)
    const ram = simMetric(n.role === 'Database' ? 70 : 50, 15)
    const net = simMetric(40, 30)
    const disk = simMetric(n.role === 'Database' ? 60 : 40, 5)
    const status = cpu > 90 || ram > 95 ? 'critical' : cpu > 75 || ram > 85 ? 'warning' : 'ok' as const
    return { ...n, cpu: +cpu.toFixed(1), ram: +ram.toFixed(1), net: +net.toFixed(1), disk: +disk.toFixed(1), status, uptime: Math.floor(Math.random() * 100 + 900) }
  }) : []

  const nodes = realNodes.length > 0 ? realNodes : simNodes
  const alerts = nodes.filter(n => n.status !== 'ok').map(n => ({
    node: n.name, level: n.status,
    msg: n.cpu > 90 ? `CPU ${n.cpu}% kritisch` : `RAM ${n.ram}% hoch`,
  }))
  res.json({ nodes, alerts, hasRealAgents: realNodes.length > 0, ts: new Date().toISOString() })
})

app.post('/api/assist', async (req: Request, res: Response) => {
  const { action = '', text = '', instruction = '', language = '', consent = false } = req.body ?? {}
  const jurisdiction = resolveJurisdiction(req)
  const ev = evaluate({ action, text, consent: consent === true, jurisdiction, maxChars: MAX_CHARS })

  // Sicherheitsrichtlinie: keine nicht nachverfolgbare Operation (fail-closed).
  try {
    await writeDecisionLog(ev.logEntry)
  } catch (err) {
    return res.status(403).json({
      blocked: true,
      error: 'Audit-Log nicht schreibbar – Operation blockiert.',
      reasons: [String((err as Error)?.message || err)],
    })
  }

  res.setHeader('X-Compliance-Status', ev.status)
  res.setHeader('X-Compliance-Jurisdiction', ev.jurisdiction)

  if (ev.status === 'BLOCK') {
    return res.status(403).json({ blocked: true, error: ev.decisionText, reasons: ev.reasons, compliance: ev.logEntry })
  }
  if (ev.originalStatus === 'WARN' && !ev.humanAuthorized) {
    return res.status(428).json({ authorizationRequired: true, error: ev.decisionText, reasons: ev.reasons, compliance: ev.logEntry })
  }

  const prompt = buildPrompt(action, text, instruction, language)
  if (!prompt) return res.status(400).json({ error: `Unbekannte Aktion: ${action}` })

  await streamModel(req, res, {
    system: SYSTEM_PROMPT,
    messages: [{ role: 'user', content: prompt }],
    userAnthropicKey: (req.headers['x-anthropic-key'] as string) || '',
    userGeminiKey: (req.headers['x-gemini-key'] as string) || '',
    maxTokens: 16000,
  })
})

// Zentrale: Mehr-Runden-Chat, der die ganze App bedient. Wie /api/assist läuft
// jede Anfrage durch das Compliance-Gateway (Audit-Log, WARN→428, BLOCK→403).
app.post('/api/chat', async (req: Request, res: Response) => {
  const { messages = [], context = '', consent = false } = req.body ?? {}

  const history = (Array.isArray(messages) ? messages : [])
    .filter(
      (m: { role?: string; content?: string }) =>
        m && (m.role === 'user' || m.role === 'assistant') && typeof m.content === 'string' && m.content.trim(),
    )
    .slice(-20)
    .map((m: { role: string; content: string }) => ({ role: m.role as 'user' | 'assistant', content: String(m.content) }))
  while (history.length && history[0].role !== 'user') history.shift()
  const lastUser = [...history].reverse().find((m) => m.role === 'user')
  if (!lastUser) return res.status(400).json({ error: 'Keine Nutzernachricht erhalten.' })

  const jurisdiction = resolveJurisdiction(req)
  const ev = evaluate({ action: 'chat', text: lastUser.content, consent: consent === true, jurisdiction, maxChars: MAX_CHARS })

  try {
    await writeDecisionLog(ev.logEntry)
  } catch (err) {
    return res.status(403).json({
      blocked: true,
      error: 'Audit-Log nicht schreibbar – Operation blockiert.',
      reasons: [String((err as Error)?.message || err)],
    })
  }

  res.setHeader('X-Compliance-Status', ev.status)
  res.setHeader('X-Compliance-Jurisdiction', ev.jurisdiction)

  if (ev.status === 'BLOCK') {
    return res.status(403).json({ blocked: true, error: ev.decisionText, reasons: ev.reasons, compliance: ev.logEntry })
  }
  if (ev.originalStatus === 'WARN' && !ev.humanAuthorized) {
    return res.status(428).json({ authorizationRequired: true, error: ev.decisionText, reasons: ev.reasons, compliance: ev.logEntry })
  }

  const system =
    CHAT_SYSTEM_PROMPT +
    (context && String(context).trim() ? `\n\nAktueller App-Zustand (Snapshot):\n${context}` : '')

  await streamModel(req, res, {
    system,
    messages: history,
    userAnthropicKey: (req.headers['x-anthropic-key'] as string) || '',
    userGeminiKey: (req.headers['x-gemini-key'] as string) || '',
    maxTokens: 4096,
  })
})

// Simulation: bewertet ohne Modell-Aufruf und ohne Schreiben ins Audit-Log.
app.post('/api/compliance/check', async (req: Request, res: Response) => {
  try {
    const { action = '', text = '', consent = false, jurisdiction = '' } = req.body ?? {}
    const jur = jurisdiction && String(jurisdiction).trim() ? String(jurisdiction) : resolveJurisdiction(req)
    const ev = evaluate({ action, text, consent: consent === true, jurisdiction: jur, maxChars: MAX_CHARS })
    res.json({
      status: ev.status,
      originalStatus: ev.originalStatus,
      requiresAuthorization: ev.originalStatus === 'WARN' && !ev.humanAuthorized,
      jurisdiction: ev.jurisdiction,
      findings: ev.findings,
      pii: ev.pii,
      reasons: ev.reasons,
      reference: ev.reference,
      decision: ev.decisionText,
      logEntry: ev.logEntry,
      simulated: true,
    })
  } catch (err) {
    res.status(500).json({ error: (err as Error)?.message || String(err) })
  }
})

app.get('/api/compliance/logs', async (req: Request, res: Response) => {
  try {
    const limit = Math.min(Number(req.query.limit) || 50, 500)
    res.json({ decisions: await readRecentDecisions(limit) })
  } catch (err) {
    res.status(500).json({ error: (err as Error)?.message || String(err) })
  }
})

// Digistore24 Webhook: wird aufgerufen wenn ein Kauf abgeschlossen wird.
// Im Digistore24-Dashboard unter Produkt → IPN/Webhook diese URL eintragen:
// https://deine-app.onrender.com/api/ds24/webhook
app.post('/api/ds24/webhook', async (req: Request, res: Response) => {
  const { order_id, product_id, buyer_email, affiliate, amount_gross } = req.body ?? {}
  console.log(`Digistore24 Kauf: ${buyer_email} – Produkt ${product_id} – ${amount_gross}€`)

  // Plan ermitteln anhand der Produkt-ID aus .env
  const proProductId   = process.env.DS24_PRO_PRODUCT_ID   || ''
  const bizProductId   = process.env.DS24_BIZ_PRODUCT_ID   || ''
  let newPlan = 'pro'
  if (bizProductId && product_id === bizProductId) newPlan = 'business'
  else if (proProductId && product_id === proProductId) newPlan = 'pro'

  // Supabase: User-Plan aktualisieren (braucht SUPABASE_URL + SUPABASE_SERVICE_KEY)
  const sbUrl = process.env.SUPABASE_URL
  const sbKey = process.env.SUPABASE_SERVICE_KEY
  if (sbUrl && sbKey && buyer_email) {
    try {
      const { createClient } = await import('@supabase/supabase-js')
      const admin = createClient(sbUrl, sbKey, { auth: { autoRefreshToken: false, persistSession: false } })
      const { data: list } = await admin.auth.admin.listUsers()
      const found = list?.users?.find((u: { email?: string }) => u.email === buyer_email)
      if (found) {
        await admin.auth.admin.updateUserById(found.id, { user_metadata: { plan: newPlan } })
        console.log(`Supabase Plan-Upgrade: ${buyer_email} → ${newPlan}`)
      }
    } catch (e) { console.error('Supabase-Upgrade-Fehler:', e) }
  }

  // Affiliate-Provision gutschreiben
  const affCode = (affiliate || '').toUpperCase()
  if (affCode) {
    const affs = loadAffiliates()
    const aff = affs[affCode]
    if (aff) {
      const amount = parseFloat(amount_gross) || 0
      const commission = +(amount * 0.3).toFixed(2)
      aff.conversions++
      aff.earnings = +(aff.earnings + commission).toFixed(2)
      aff.recentConversions.unshift({ date: new Date().toISOString(), plan: `${amount}€`, commission })
      if (aff.recentConversions.length > 20) aff.recentConversions.pop()
      saveAffiliates(affs)
      console.log(`Affiliate-Provision: ${affCode} → +${commission}€`)
    }
  }
  res.json({ received: true, order_id })
})

// Affiliate: Klick tracken (aufgerufen wenn jemand mit ?ref= landet).
app.post('/api/affiliate/click', (req: Request, res: Response) => {
  const { code } = req.body ?? {}
  if (!code) return res.status(400).json({ error: 'Code fehlt.' })
  const affs = loadAffiliates()
  const aff = affs[code.toUpperCase()]
  if (aff) { aff.clicks++; saveAffiliates(affs) }
  res.json({ ok: true })
})

// Affiliate: Registrierung.
app.post('/api/affiliate/register', (req: Request, res: Response) => {
  const { name, email, website = '' } = req.body ?? {}
  if (!name || !email) return res.status(400).json({ error: 'Name und E-Mail erforderlich.' })
  const affs = loadAffiliates()
  const existing = Object.values(affs).find(a => a.email === email)
  if (existing) return res.json({ code: existing.code, message: 'Konto bereits vorhanden.' })
  let code = generateCode(name)
  while (affs[code]) code = generateCode(name)
  affs[code] = { code, name, email, website, clicks: 0, conversions: 0, earnings: 0, recentConversions: [], createdAt: new Date().toISOString() }
  saveAffiliates(affs)
  console.log(`Neuer Affiliate: ${code} – ${email}`)
  res.json({ code, message: 'Affiliate-Konto erstellt.' })
})

// Affiliate: Statistiken abrufen.
app.get('/api/affiliate/stats/:code', (req: Request, res: Response) => {
  const code = req.params.code.toUpperCase()
  const affs = loadAffiliates()
  const aff = affs[code]
  if (!aff) return res.status(404).json({ error: 'Affiliate-Code nicht gefunden.' })
  res.json(aff)
})

// ── Monitoring / Automatische E-Mail-Berichte ────────────────────────────────
const MON_FILE = join(dirname(fileURLToPath(import.meta.url)), 'monitored-sites.json')

interface ScanResult {
  label: string; present: boolean; value: string | null; weight: number
}
interface MonitoredSite {
  url: string; email: string; label: string
  lastScore: number | null; lastGrade: string | null
  lastScan: string | null; addedAt: string
}

function loadSites(): MonitoredSite[] {
  try { return JSON.parse(readFileSync(MON_FILE, 'utf-8')) } catch { return [] }
}
function saveSites(sites: MonitoredSite[]) {
  writeFileSync(MON_FILE, JSON.stringify(sites, null, 2))
}

async function scanUrl(rawUrl: string): Promise<{ https: boolean; score: number; grade: string; checks: ScanResult[] } | null> {
  let target = rawUrl.trim()
  if (!/^https?:\/\//i.test(target)) target = 'https://' + target
  try {
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), 8000)
    let response: globalThis.Response
    let usedHttps = target.startsWith('https')
    try {
      response = await fetch(target, { method: 'HEAD', signal: controller.signal, redirect: 'follow' })
    } catch {
      if (usedHttps) {
        response = await fetch(target.replace(/^https/i, 'http'), { method: 'HEAD', signal: controller.signal, redirect: 'follow' })
        usedHttps = false
      } else return null
    }
    clearTimeout(timer)
    const headers = Object.fromEntries(response.headers.entries())
    const checks = [
      { key: 'strict-transport-security', label: 'HSTS', weight: 20 },
      { key: 'content-security-policy', label: 'Content-Security-Policy', weight: 20 },
      { key: 'x-frame-options', label: 'X-Frame-Options', weight: 15 },
      { key: 'x-content-type-options', label: 'X-Content-Type-Options', weight: 15 },
      { key: 'referrer-policy', label: 'Referrer-Policy', weight: 10 },
      { key: 'permissions-policy', label: 'Permissions-Policy', weight: 10 },
      { key: 'x-xss-protection', label: 'X-XSS-Protection', weight: 10 },
    ]
    const results: ScanResult[] = checks.map((c) => ({ label: c.label, present: !!headers[c.key], value: headers[c.key] || null, weight: c.weight }))
    let score = usedHttps ? 10 : 0
    for (const r of results) if (r.present) score += r.weight
    const grade = score >= 90 ? 'A+' : score >= 80 ? 'A' : score >= 70 ? 'B' : score >= 50 ? 'C' : score >= 30 ? 'D' : 'F'
    return { https: usedHttps, score, grade, checks: results }
  } catch { return null }
}

function createMailTransport() {
  const host = process.env.SMTP_HOST
  const port = Number(process.env.SMTP_PORT || 587)
  const user = process.env.SMTP_USER
  const pass = process.env.SMTP_PASS
  if (!host || !user || !pass) return null
  return nodemailer.createTransport({ host, port, secure: port === 465, auth: { user, pass } })
}

async function sendReportEmail(site: MonitoredSite, result: { https: boolean; score: number; grade: string; checks: ScanResult[] }) {
  const transport = createMailTransport()
  if (!transport) return
  const missing = result.checks.filter((c) => !c.present).map((c) => `<li>❌ ${c.label}</li>`).join('')
  const present = result.checks.filter((c) => c.present).map((c) => `<li>✅ ${c.label}</li>`).join('')
  const gradeColor = result.grade.startsWith('A') ? '#22c55e' : result.grade === 'B' ? '#84cc16' : result.grade === 'C' ? '#f59e0b' : '#ef4444'
  const html = `
    <div style="font-family:sans-serif;max-width:560px;margin:0 auto;background:#020817;color:#e2e8f0;border-radius:12px;padding:2rem;">
      <h2 style="color:#60a5fa;margin-top:0">🛡️ SecureHub – Wöchentlicher Sicherheitsbericht</h2>
      <p>Website: <strong>${site.url}</strong></p>
      <div style="background:#0f172a;border-radius:8px;padding:1rem;margin:1rem 0;display:flex;align-items:center;gap:1rem;">
        <span style="font-size:3rem;font-weight:800;color:${gradeColor}">${result.grade}</span>
        <div>
          <div style="font-size:1.5rem;font-weight:700">${result.score}/100 Punkte</div>
          <div style="color:#94a3b8;font-size:0.85rem">HTTPS: ${result.https ? '✅ Aktiv' : '❌ Fehlt'}</div>
        </div>
      </div>
      ${present ? `<h3 style="color:#22c55e">Vorhanden:</h3><ul style="color:#cbd5e1">${present}</ul>` : ''}
      ${missing ? `<h3 style="color:#ef4444">Fehlende Header:</h3><ul style="color:#cbd5e1">${missing}</ul>` : ''}
      <hr style="border-color:#1e293b;margin:1.5rem 0">
      <p style="color:#64748b;font-size:0.8rem">Du erhältst diesen Bericht wöchentlich von SecureHub.<br>
      Abmelden: Öffne die App unter dem Monitoring-Tab und entferne die Website.</p>
    </div>`
  await transport.sendMail({
    from: process.env.SMTP_FROM || process.env.SMTP_USER,
    to: site.email,
    subject: `SecureHub: ${site.url} – Note ${result.grade} (${result.score}/100)`,
    html,
  })
}

// Monitoring: Site hinzufügen
app.post('/api/monitor/add', async (req: Request, res: Response) => {
  const { url, email, label = '' } = req.body ?? {}
  if (!url || !email) return res.status(400).json({ error: 'URL und E-Mail erforderlich.' })
  const sites = loadSites()
  if (sites.find((s) => s.url === url && s.email === email)) return res.json({ ok: true, message: 'Bereits vorhanden.' })
  const result = await scanUrl(url)
  const site: MonitoredSite = {
    url, email,
    label: label || url,
    lastScore: result?.score ?? null,
    lastGrade: result?.grade ?? null,
    lastScan: result ? new Date().toISOString() : null,
    addedAt: new Date().toISOString(),
  }
  sites.push(site)
  saveSites(sites)
  res.json({ ok: true, site })
})

// Monitoring: Liste abrufen
app.get('/api/monitor/list', (req: Request, res: Response) => {
  const { email } = req.query
  const sites = loadSites()
  const filtered = email ? sites.filter((s) => s.email === String(email)) : sites
  res.json({ sites: filtered })
})

// Monitoring: Site entfernen
app.post('/api/monitor/remove', (req: Request, res: Response) => {
  const { url, email } = req.body ?? {}
  if (!url || !email) return res.status(400).json({ error: 'URL und E-Mail erforderlich.' })
  const sites = loadSites().filter((s) => !(s.url === url && s.email === email))
  saveSites(sites)
  res.json({ ok: true })
})

// Monitoring: Sofort-Scan einer Site
app.post('/api/monitor/scan-now', async (req: Request, res: Response) => {
  const { url, email } = req.body ?? {}
  if (!url) return res.status(400).json({ error: 'URL erforderlich.' })
  const result = await scanUrl(url)
  if (!result) return res.status(502).json({ error: 'Scan fehlgeschlagen.' })
  const sites = loadSites()
  const site = sites.find((s) => s.url === url)
  if (site) {
    site.lastScore = result.score
    site.lastGrade = result.grade
    site.lastScan = new Date().toISOString()
    saveSites(sites)
    if (email) await sendReportEmail(site, result).catch((e) => console.error('E-Mail-Fehler:', e))
  }
  res.json({ ok: true, ...result })
})

// Wöchentlicher Scan-Job: läuft alle 7 Tage und sendet E-Mail-Berichte.
// Für Render Free (24h Spin-Down): verwende stattdessen einen externen Cron-Dienst
// (z. B. cron-job.org), der POST /api/monitor/weekly-run aufruft.
async function weeklyRun() {
  const sites = loadSites()
  console.log(`Wöchentlicher Scan: ${sites.length} Seiten`)
  for (const site of sites) {
    try {
      const result = await scanUrl(site.url)
      if (!result) continue
      site.lastScore = result.score
      site.lastGrade = result.grade
      site.lastScan = new Date().toISOString()
      await sendReportEmail(site, result)
    } catch (e) { console.error(`Scan-Fehler ${site.url}:`, e) }
  }
  saveSites(sites)
  console.log('Wöchentlicher Scan abgeschlossen.')
}

// Externer Cron-Trigger (z. B. cron-job.org → POST /api/monitor/weekly-run)
app.post('/api/monitor/weekly-run', async (_req: Request, res: Response) => {
  res.json({ ok: true, message: 'Wöchentlicher Scan gestartet.' })
  weeklyRun().catch((e) => console.error('weeklyRun Fehler:', e))
})

// Interner Timer: alle 7 Tage (nur wenn Prozess dauerhaft läuft)
const WEEK_MS = 7 * 24 * 60 * 60 * 1000
setInterval(() => { weeklyRun().catch((e) => console.error('weeklyRun Fehler:', e)) }, WEEK_MS)

// Gebautes Frontend ausliefern (dist/). SPA: alle Nicht-/api-GETs -> index.html.
const dist = join(__dirname, '..', 'dist')
const hasDist = existsSync(dist)
if (hasDist) {
  app.use(express.static(dist))
  app.get(/^(?!\/api\/).*/, (_req: Request, res: Response) => res.sendFile(join(dist, 'index.html')))
} else {
  app.get('/', (_req: Request, res: Response) =>
    res
      .status(503)
      .type('text/plain')
      .send('Frontend nicht gebaut (dist/ fehlt). Bitte "npm run build" ausführen. Die API unter /api/... läuft.'),
  )
}

app.listen(PORT, () => {
  console.log(`finaz API + Compliance-Gateway: Port ${PORT}`)
  if (hasDist) console.log(`Frontend (dist/) wird ebenfalls auf Port ${PORT} ausgeliefert.`)
  else console.warn('⚠  dist/ fehlt – nur die API läuft. Bitte "npm run build".')
  if (!process.env.ANTHROPIC_API_KEY) {
    console.warn('ℹ  Kein Server-Key (.env). KI-Funktionen nutzen den im Browser hinterlegten Key (⚙️ Einstellungen).')
  }
  void loadGeoip()
})
