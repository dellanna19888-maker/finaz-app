import { getApiKey, getGeminiKey } from './apiKey'

export interface JarisMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface JarisRequest {
  messages: JarisMessage[]
  consent?: boolean
}

export type JarisOutcome =
  | { kind: 'done'; status: string; jurisdiction: string }
  | { kind: 'needs-auth'; info: { error?: string; reasons?: string[] } }
  | { kind: 'blocked'; info: { error?: string; reasons?: string[] } }
  | { kind: 'error'; error: string }

export async function runJaris(
  req: JarisRequest,
  onDelta: (text: string) => void,
  signal?: AbortSignal,
): Promise<JarisOutcome> {
  const key = getApiKey()
  const gkey = getGeminiKey()
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (key) headers['x-anthropic-key'] = key
  if (gkey) headers['x-gemini-key'] = gkey

  let resp: Response
  try {
    resp = await fetch('/api/jaris', { method: 'POST', headers, body: JSON.stringify(req), signal })
  } catch (err) {
    return { kind: 'error', error: (err as Error).message || 'Netzwerkfehler – läuft das Backend?' }
  }

  if (resp.status === 428) {
    try { return { kind: 'needs-auth', info: await resp.json() } } catch { return { kind: 'needs-auth', info: {} } }
  }
  if (resp.status === 403) {
    try { return { kind: 'blocked', info: await resp.json() } } catch { return { kind: 'blocked', info: {} } }
  }
  if (!resp.ok || !resp.body) {
    let err = 'Anfrage fehlgeschlagen'
    try { err = ((await resp.json()) as { error?: string }).error || err } catch { /* ignore */ }
    return { kind: 'error', error: err }
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
      try {
        const evt = JSON.parse(json) as { type: string; text?: string; message?: string }
        if (evt.type === 'delta' && evt.text) onDelta(evt.text)
        else if (evt.type === 'error') streamError = evt.message || 'Fehler'
      } catch { /* ignore */ }
    }
  }
  if (streamError) return { kind: 'error', error: streamError }
  return { kind: 'done', status, jurisdiction }
}
