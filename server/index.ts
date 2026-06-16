// API-Backend für finaz-app: KI-Assistent (Claude) + Compliance-Gateway.
// Mit tsx ausführen:  npm run api   (Dev: npm run api:dev, Demo: npm run demo)
import express from 'express'
import type { Request, Response } from 'express'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'
import { existsSync } from 'node:fs'
import Anthropic from '@anthropic-ai/sdk'
import 'dotenv/config'
import { evaluate, mapCountryToJurisdiction } from '../src/compliance/gateway'
import { writeDecisionLog, readRecentDecisions } from './logger'

const __dirname = dirname(fileURLToPath(import.meta.url))
const PORT = Number(process.env.API_PORT || process.env.PORT || 3001)
const MODEL = process.env.CLAUDE_MODEL || 'claude-opus-4-8'
const MAX_CHARS = Number(process.env.COMPLIANCE_MAX_CHARS) || 50000

const app = express()
app.set('trust proxy', true)
app.use(express.json({ limit: '2mb' }))

const envClient = process.env.ANTHROPIC_API_KEY ? new Anthropic() : null

// "Bring your own key": pro Anfrage darf der Client einen eigenen Key senden
// (Header x-anthropic-key). Sonst greift der Server-Key aus .env (falls gesetzt).
function getClient(userKey: string): Anthropic | null {
  const apiKey = userKey || process.env.ANTHROPIC_API_KEY
  if (!apiKey) return null
  if (!userKey && envClient) return envClient
  return new Anthropic({ apiKey })
}

// Optionale, offline GeoIP-Auflösung (Paket `geoip-lite`). Ist es nicht
// installiert, bleibt die IP-Auflösung deaktiviert und es greifen Header/Fallback.
type GeoipLookup = (ip: string) => { country?: string } | null
let geoipLookup: GeoipLookup | null = null
try {
  const mod = (await import('geoip-lite')) as unknown as {
    default?: { lookup?: GeoipLookup }
    lookup?: GeoipLookup
  }
  geoipLookup = mod.default?.lookup ?? mod.lookup ?? null
} catch {
  geoipLookup = null
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
  'Du bist ein hilfreicher Assistent für eine persönliche Finanz-App und für Markdown.',
  'Regeln:',
  '- Antworte ausschließlich in sauberem Markdown, ohne einleitende oder abschließende Kommentare.',
  '- Umschließe das gesamte Dokument NICHT mit ``` Code-Fences.',
  '- Bei Finanzdaten: gib nüchterne, konkrete Hinweise; erfinde keine Zahlen und nutze nur die gelieferten Daten.',
  '- Keine verbindliche Steuer- oder Rechtsberatung; weise bei Bedarf kurz darauf hin.',
  '- Antworte auf Deutsch, sofern nicht ausdrücklich eine andere Sprache verlangt wird.',
  '- Antworte direkt mit dem fertigen Inhalt (keine Gedanken, keine Meta-Erklärungen).',
].join('\n')

// System-Prompt der "Zentrale" (KI-Schaltzentrale + Steuerung per Aktionsblöcken).
const CHAT_SYSTEM_PROMPT = [
  'Du bist die zentrale Schaltzentrale ("Zentrale") der FinazApp – ein hilfreicher, präziser KI-Assistent.',
  'Über dich steuert und erreicht der Nutzer die ganze App: Finanzen (Dashboard, Transaktionen, Budgets, Berichte), Notizen und Compliance.',
  'Du erhältst bei jeder Anfrage einen Snapshot des aktuellen App-Zustands. Nutze ausschließlich diese Daten, erfinde keine Zahlen.',
  'Antworte auf Deutsch, in klarem Markdown, kompakt und konkret. Keine verbindliche Steuer-/Rechtsberatung.',
  '',
  'AKTIONEN: Möchte der Nutzer etwas TUN (Transaktion erfassen, Budget setzen, Notiz schreiben, zu einem Bereich wechseln, Compliance-Prüfung),',
  'erkläre es kurz und gib GENAU EINEN Aktionsblock aus – ein Code-Fence mit Sprache "action" und gültigem JSON:',
  '```action',
  '{"tool":"<name>","args":{ ... }}',
  '```',
  'Verfügbare tools und args:',
  '- add_transaction: {"type":"income"|"expense","amount":Zahl,"category":"<gültige Kategorie>","description":"optional","date":"YYYY-MM-DD optional"}',
  '- set_budget: {"category":"<Kategorie>","limit":Zahl}',
  '- append_note: {"content":"Markdown, wird an die Notiz angehängt"}',
  '- navigate: {"to":"/dashboard"|"/transactions"|"/budget"|"/reports"|"/notes"|"/compliance"|"/settings"}',
  '- compliance_check: {"text":"zu prüfender Inhalt","action":"optional","jurisdiction":"EU"|"UK"|"US"|"DEFAULT" optional}',
  'Regeln: Nur Kategorien aus dem Snapshot verwenden. Höchstens EIN Aktionsblock pro Antwort. Aktionen NICHT selbst ausführen –',
  'der Block wird dem Nutzer zur Bestätigung angezeigt. Ist keine Aktion nötig, gib keinen Block aus.',
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
  res.json({ ok: true, envKey: !!process.env.ANTHROPIC_API_KEY, geoip: !!geoipLookup })
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

  const userKey = (req.headers['x-anthropic-key'] as string) || ''
  const ai = getClient(userKey)
  if (!ai) {
    return res.status(400).json({
      error: 'Kein API-Key. Hinterlege ihn in den Einstellungen (⚙️) oder als ANTHROPIC_API_KEY in .env.',
    })
  }

  const prompt = buildPrompt(action, text, instruction, language)
  if (!prompt) return res.status(400).json({ error: `Unbekannte Aktion: ${action}` })

  res.setHeader('Content-Type', 'text/event-stream')
  res.setHeader('Cache-Control', 'no-cache')
  res.setHeader('Connection', 'keep-alive')
  const send = (payload: unknown) => res.write(`data: ${JSON.stringify(payload)}\n\n`)

  let stream: ReturnType<typeof ai.messages.stream> | undefined
  try {
    stream = ai.messages.stream({
      model: MODEL,
      max_tokens: 16000,
      system: SYSTEM_PROMPT,
      messages: [{ role: 'user', content: prompt }],
    })
    req.on('close', () => {
      try {
        stream?.abort()
      } catch {
        /* ignore */
      }
    })
    stream.on('text', (delta: string) => send({ type: 'delta', text: delta }))
    await stream.finalMessage()
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

  const userKey = (req.headers['x-anthropic-key'] as string) || ''
  const ai = getClient(userKey)
  if (!ai) {
    return res.status(400).json({
      error: 'Kein API-Key. Hinterlege ihn in den Einstellungen (⚙️) oder als ANTHROPIC_API_KEY in .env.',
    })
  }

  const system =
    CHAT_SYSTEM_PROMPT +
    (context && String(context).trim() ? `\n\nAktueller App-Zustand (Snapshot):\n${context}` : '')

  res.setHeader('Content-Type', 'text/event-stream')
  res.setHeader('Cache-Control', 'no-cache')
  res.setHeader('Connection', 'keep-alive')
  const send = (payload: unknown) => res.write(`data: ${JSON.stringify(payload)}\n\n`)

  let stream: ReturnType<typeof ai.messages.stream> | undefined
  try {
    stream = ai.messages.stream({ model: MODEL, max_tokens: 4096, system, messages: history })
    req.on('close', () => {
      try {
        stream?.abort()
      } catch {
        /* ignore */
      }
    })
    stream.on('text', (delta: string) => send({ type: 'delta', text: delta }))
    await stream.finalMessage()
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

// Optional: gebautes Frontend ausliefern (Einzel-Prozess-Demo: npm run demo).
const dist = join(__dirname, '..', 'dist')
if (existsSync(dist)) app.use(express.static(dist))

app.listen(PORT, () => {
  console.log(`finaz API + Compliance-Gateway: http://localhost:${PORT}`)
  if (existsSync(dist)) console.log(`Demo-UI (gebaut) ebenfalls unter http://localhost:${PORT}`)
  if (!process.env.ANTHROPIC_API_KEY) {
    console.warn('ℹ  Kein Server-Key (.env). KI-Funktionen nutzen den im Browser hinterlegten Key (⚙️ Einstellungen).')
  }
})
