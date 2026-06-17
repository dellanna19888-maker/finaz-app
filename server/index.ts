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
