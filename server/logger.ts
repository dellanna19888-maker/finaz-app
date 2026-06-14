// Server-seitiger Audit-Logger (JSON Lines). Nur Node – wird per tsx ausgeführt.
import { appendFile, mkdir, readFile } from 'node:fs/promises'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const LOG_DIR = process.env.COMPLIANCE_LOG_DIR || join(__dirname, 'logs')
const LOG_FILE = join(LOG_DIR, 'decisions.log.jsonl')

/** Schreibt einen Entscheidungs-Eintrag. Wirft bei Fehler (Aufrufer: fail-closed). */
export async function writeDecisionLog(entry: unknown): Promise<void> {
  await mkdir(LOG_DIR, { recursive: true })
  await appendFile(LOG_FILE, JSON.stringify(entry) + '\n', 'utf8')
}

/** Liest die letzten `limit` Entscheidungen. */
export async function readRecentDecisions(limit = 50): Promise<unknown[]> {
  try {
    const raw = await readFile(LOG_FILE, 'utf8')
    return raw.split('\n').filter(Boolean).slice(-limit).map((line) => JSON.parse(line))
  } catch (err) {
    if ((err as NodeJS.ErrnoException).code === 'ENOENT') return []
    throw err
  }
}
