// Daten-Sicherung: exportiert/importiert alle Inhalte des Hubs (Content-Plan,
// Finanzen, Wissen, Kanal) als eine JSON-Datei. Alles liegt im localStorage –
// ein Export ist die einzige Möglichkeit, Daten zu sichern oder auf ein anderes
// Gerät zu übertragen. API-Schlüssel und der flüchtige Chat-Verlauf werden
// bewusst NICHT mitexportiert (Datenschutz).

export const BACKUP_KEYS = [
  'finaz_tasks',
  'finaz_finance',
  'finaz_currency',
  'finaz_notes',
  'finaz_channel',
  'finaz_competitors',
] as const

export interface Backup {
  app: 'creator-hub'
  version: 1
  exportedAt: string
  data: Record<string, string>
}

/** Sammelt alle vorhandenen Inhalte als serialisierbares Backup-Objekt. */
export function collectBackup(): Backup {
  const data: Record<string, string> = {}
  for (const key of BACKUP_KEYS) {
    const v = localStorage.getItem(key)
    if (v !== null) data[key] = v
  }
  return { app: 'creator-hub', version: 1, exportedAt: new Date().toISOString(), data }
}

/** Backup als formatiertes JSON. */
export function exportJson(): string {
  return JSON.stringify(collectBackup(), null, 2)
}

/** Löst im Browser einen Datei-Download des Backups aus. */
export function downloadBackup(): void {
  const blob = new Blob([exportJson()], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `creator-hub-backup-${new Date().toISOString().slice(0, 10)}.json`
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

export interface ImportResult {
  imported: string[]
  skipped: string[]
}

/**
 * Spielt ein zuvor exportiertes Backup ein. Schreibt nur bekannte Schlüssel
 * (Whitelist) und nur, wenn die Datei das erwartete Format hat. Wirft bei
 * ungültigem JSON/Format – der Aufrufer zeigt die Meldung an.
 */
export function importJson(raw: string): ImportResult {
  let parsed: unknown
  try {
    parsed = JSON.parse(raw)
  } catch {
    throw new Error('Datei ist kein gültiges JSON.')
  }
  const obj = parsed as Partial<Backup>
  if (!obj || obj.app !== 'creator-hub' || typeof obj.data !== 'object' || obj.data === null) {
    throw new Error('Keine gültige Creator-Hub-Sicherung.')
  }
  const imported: string[] = []
  const skipped: string[] = []
  for (const [key, value] of Object.entries(obj.data as Record<string, unknown>)) {
    if ((BACKUP_KEYS as readonly string[]).includes(key) && typeof value === 'string') {
      localStorage.setItem(key, value)
      imported.push(key)
    } else {
      skipped.push(key)
    }
  }
  return { imported, skipped }
}

/** Entfernt alle Inhalte (Reset). Schlüssel und Chat-Verlauf bleiben unberührt. */
export function resetData(): void {
  for (const key of BACKUP_KEYS) localStorage.removeItem(key)
}
