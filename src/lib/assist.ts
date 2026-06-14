// Client-Helfer: ruft /api/assist auf, verarbeitet den SSE-Stream und meldet
// die Compliance-Antworten (428 = Autorisierung nötig, 403 = blockiert) zurück.
// Sendet den im Browser hinterlegten API-Key (BYOK) als Header mit.

import { getApiKey } from './apiKey'

export interface AssistRequest {
  action: string
  text?: string
  instruction?: string
  language?: string
  consent?: boolean
}

export interface ComplianceInfo {
  error?: string
  reasons?: string[]
  compliance?: Record<string, unknown>
}

export type AssistOutcome =
  | { kind: 'done'; status: string; jurisdiction: string }
  | { kind: 'needs-auth'; info: ComplianceInfo }
  | { kind: 'blocked'; info: ComplianceInfo }
  | { kind: 'error'; error: string }

export async function runAssist(
  req: AssistRequest,
  onDelta: (text: string) => void,
  signal?: AbortSignal,
): Promise<AssistOutcome> {
  const key = getApiKey()
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (key) headers['x-anthropic-key'] = key

  let resp: Response
  try {
    resp = await fetch('/api/assist', {
      method: 'POST',
      headers,
      body: JSON.stringify(req),
      signal,
    })
  } catch (err) {
    return {
      kind: 'error',
      error: (err as Error).message || 'Netzwerkfehler – läuft das Backend (npm run api)?',
    }
  }

  if (resp.status === 428) return { kind: 'needs-auth', info: await safeJson(resp) }
  if (resp.status === 403) return { kind: 'blocked', info: await safeJson(resp) }
  if (!resp.ok || !resp.body) {
    const data = await safeJson(resp)
    return { kind: 'error', error: data.error || 'Anfrage fehlgeschlagen' }
  }

  const status = resp.headers.get('X-Compliance-Status') || 'PASS'
  const jurisdiction = resp.headers.get('X-Compliance-Jurisdiction') || ''

  const reader = resp.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let streamError = ''
  for (;;) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const parts = buffer.split('\n\n')
    buffer = parts.pop() ?? ''
    for (const part of parts) {
      const line = part.trim()
      if (!line.startsWith('data:')) continue
      const json = line.slice(5).trim()
      if (!json) continue
      const evt = JSON.parse(json) as { type: string; text?: string; message?: string }
      if (evt.type === 'delta' && evt.text) onDelta(evt.text)
      else if (evt.type === 'error') streamError = evt.message || 'Fehler'
    }
  }
  if (streamError) return { kind: 'error', error: streamError }
  return { kind: 'done', status, jurisdiction }
}

async function safeJson(resp: Response): Promise<ComplianceInfo> {
  try {
    return (await resp.json()) as ComplianceInfo
  } catch {
    return { error: resp.statusText }
  }
}
