// "Bring your own key": der Anthropic-API-Key wird NUR im Browser (localStorage)
// gespeichert und bei Anfragen an das eigene Backend mitgesendet. Niemals im Repo.

const KEY = 'finaz_anthropic_key'

export function getApiKey(): string {
  try {
    return localStorage.getItem(KEY) || ''
  } catch {
    return ''
  }
}

export function setApiKey(value: string): void {
  try {
    if (value) localStorage.setItem(KEY, value)
    else localStorage.removeItem(KEY)
  } catch {
    /* ignore */
  }
}

export function hasApiKey(): boolean {
  return getApiKey().length > 0
}

// Google Gemini (kostenlose Alternative). Ebenfalls nur im Browser gespeichert.
const GKEY = 'finaz_gemini_key'

export function getGeminiKey(): string {
  try {
    return localStorage.getItem(GKEY) || ''
  } catch {
    return ''
  }
}

export function setGeminiKey(value: string): void {
  try {
    if (value) localStorage.setItem(GKEY, value)
    else localStorage.removeItem(GKEY)
  } catch {
    /* ignore */
  }
}

export function hasGeminiKey(): boolean {
  return getGeminiKey().length > 0
}

/** True, wenn IRGENDEIN KI-Schlüssel (Anthropic oder Gemini) gesetzt ist. */
export function hasAnyKey(): boolean {
  return hasApiKey() || hasGeminiKey()
}
