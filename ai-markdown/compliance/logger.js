import { appendFile, mkdir, readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));

// Audit-Log-Verzeichnis (überschreibbar per Umgebungsvariable).
const LOG_DIR = process.env.COMPLIANCE_LOG_DIR || join(__dirname, "logs");
const LOG_FILE = join(LOG_DIR, "decisions.log.jsonl");

/**
 * Schreibt einen Entscheidungs-Eintrag im Pflicht-Log-Format (JSON Lines).
 * Wirft bei Fehler – der Aufrufer MUSS dies als BLOCK behandeln
 * (Sicherheitsrichtlinie: keine nicht nachverfolgbare Operation zulassen).
 */
export async function writeDecisionLog(entry) {
  await mkdir(LOG_DIR, { recursive: true });
  await appendFile(LOG_FILE, JSON.stringify(entry) + "\n", "utf8");
}

/** Liest die letzten `limit` Entscheidungen aus dem Audit-Log. */
export async function readRecentDecisions(limit = 50) {
  try {
    const raw = await readFile(LOG_FILE, "utf8");
    const lines = raw.split("\n").filter(Boolean);
    return lines.slice(-limit).map((line) => JSON.parse(line));
  } catch (err) {
    if (err.code === "ENOENT") return [];
    throw err;
  }
}

export { LOG_FILE };
