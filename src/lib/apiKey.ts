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
