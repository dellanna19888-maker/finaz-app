// Dynamisches Compliance-Gateway (D-C-G) – isomorpher Kern.
//
// Läuft im Browser (Vue) UND im Node-Server: keine fs-/process-/fetch-Zugriffe.
// Der Server reicht `maxChars` und die ermittelte `jurisdiction` herein.
//
// ⚠ Governance-Gerüst, keine Rechtsberatung / keine zertifizierte Compliance.

export type ComplianceStatus = 'PASS' | 'WARN' | 'BLOCK'

export interface FindingRule {
  status: ComplianceStatus
  ref: string
}
export interface Ruleset {
  label: string
  findings: Record<string, FindingRule>
  pass_ref: string
}

export interface LogEntry {
  timestamp: string
  angewandte_gerichtsbarkeit: string
  angeforderte_aktion: string
  konformitätsstatus: ComplianceStatus
  gesetzliche_referenz: string
  endgültige_entscheidung: string
}

export interface EvalResult {
  jurisdiction: string
  rulesetLabel: string
  findings: string[]
  pii: string[]
  reasons: string[]
  reference: string
  status: ComplianceStatus // effektiv (nach Autorisierung)
  originalStatus: ComplianceStatus
  decisionText: string
  humanAuthorized: boolean
  logEntry: LogEntry
}

export interface EvaluateOptions {
  action?: string
  text?: string
  consent?: boolean
  jurisdiction?: string
  maxChars?: number
}

const EU_EEA = new Set([
  'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR',
  'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK',
  'SI', 'ES', 'SE', 'IS', 'LI', 'NO',
])

export function mapCountryToJurisdiction(country?: string | null): string {
  if (!country) return 'DEFAULT'
  const c = String(country).toUpperCase()
  if (EU_EEA.has(c)) return 'EU'
  if (c === 'GB' || c === 'UK') return 'UK'
  if (c === 'US') return 'US'
  return 'DEFAULT'
}

const EU_FINDINGS: Record<string, FindingRule> = {
  PROHIBITED_PRACTICE: { status: 'BLOCK', ref: 'EU AI Act Art. 5 (verbotene Praktiken)' },
  SPECIAL_CATEGORY: { status: 'WARN', ref: 'DSGVO Art. 9 (besondere Kategorien personenbezogener Daten)' },
  PII_PRESENT: { status: 'WARN', ref: 'DSGVO Art. 6 / Art. 28 (Auftragsverarbeitung, Rechtsgrundlage)' },
  EXCESSIVE_DATA: { status: 'WARN', ref: 'DSGVO Art. 5(1)(c) (Datenminimierung)' },
}

export const RULESETS: Record<string, Ruleset> = {
  EU: {
    label: 'EU (DSGVO + EU AI Act)',
    findings: EU_FINDINGS,
    pass_ref: 'DSGVO / EU AI Act Art. 50 (Transparenzpflicht erfüllt)',
  },
  UK: {
    label: 'UK (UK GDPR)',
    findings: {
      PROHIBITED_PRACTICE: { status: 'BLOCK', ref: 'UK-Richtlinie / verbotene Praktiken' },
      SPECIAL_CATEGORY: { status: 'WARN', ref: 'UK GDPR Art. 9 (besondere Kategorien)' },
      PII_PRESENT: { status: 'WARN', ref: 'UK GDPR Art. 6 / Art. 28' },
      EXCESSIVE_DATA: { status: 'WARN', ref: 'UK GDPR Art. 5(1)(c) (Datenminimierung)' },
    },
    pass_ref: 'UK GDPR (Transparenz erfüllt)',
  },
  US: {
    label: 'USA (NIST AI RMF / CCPA)',
    findings: {
      PROHIBITED_PRACTICE: { status: 'BLOCK', ref: 'Interne Richtlinie / NIST AI RMF (GOVERN)' },
      SPECIAL_CATEGORY: { status: 'WARN', ref: 'CCPA/CPRA (sensible personenbezogene Daten)' },
      PII_PRESENT: { status: 'WARN', ref: 'CCPA §1798.100 (Notice at Collection)' },
      EXCESSIVE_DATA: { status: 'PASS', ref: 'NIST AI RMF (MAP)' },
    },
    pass_ref: 'NIST AI RMF (MEASURE / MANAGE)',
  },
  DEFAULT: {
    label: 'Unbekannt → restriktivstes Profil (DSGVO)',
    findings: EU_FINDINGS,
    pass_ref: 'DSGVO (restriktives Standardprofil)',
  },
}

const SEVERITY: Record<ComplianceStatus, number> = { PASS: 1, WARN: 2, BLOCK: 3 }

const PATTERNS: Record<string, RegExp> = {
  email: /[\w.+-]+@[\w-]+\.[\w.-]+/,
  iban: /\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b/,
  kreditkarte: /\b(?:\d[ -]?){13,16}\b/,
  telefon: /\+\d{2,3}[ -]?\d{3,}/,
}
const PROHIBITED =
  /\b(social[\s-]?scoring|sozial(es)?[\s-]?scoring|biometr\w*\s+(kategorisierung|identifizierung)|mass\s+surveillance|massen[üu]berwachung)\b/i
const SPECIAL_CATEGORY =
  /\b(gesundheit|krankheit|diagnose|patient\w*|medizinisch\w*|health|disease|medical|religion|religi(?:ö|oe)s|konfession|ethnisch\w*|rasse|race|ethnic\w*|politische\s+(?:meinung|überzeugung|einstellung)|political\s+opinion|gewerkschaft\w*|trade\s+union|sexuelle\s+(?:orientierung|identität)|sexual\s+orientation|biometr\w*|genetisch\w*|genetic|dna)\b/i

function tsNow(): string {
  const d = new Date()
  const p = (n: number) => String(n).padStart(2, '0')
  return (
    `${d.getUTCFullYear()}-${p(d.getUTCMonth() + 1)}-${p(d.getUTCDate())} ` +
    `${p(d.getUTCHours())}:${p(d.getUTCMinutes())}`
  )
}

export function assess(action: string, text: string, maxChars = 50000): { findings: string[]; pii: string[] } {
  const findings: string[] = []
  const haystack = `${action}\n${text}`

  if (PROHIBITED.test(haystack)) findings.push('PROHIBITED_PRACTICE')
  if (SPECIAL_CATEGORY.test(text)) findings.push('SPECIAL_CATEGORY')

  const pii = Object.entries(PATTERNS)
    .filter(([, re]) => re.test(text))
    .map(([name]) => name)
  if (pii.length) findings.push('PII_PRESENT')

  if (text.length > maxChars) findings.push('EXCESSIVE_DATA')

  return { findings, pii }
}

/** Vollständige Bewertung (Schritte 1–4) ohne Logging/IO. */
export function evaluate(opts: EvaluateOptions): EvalResult {
  const { action = '', text = '', consent = false, jurisdiction = 'DEFAULT', maxChars = 50000 } = opts
  const jur = (jurisdiction || 'DEFAULT').toUpperCase()
  const ruleset = RULESETS[jur] ?? RULESETS.DEFAULT

  const { findings, pii } = assess(action, text, maxChars)

  let status: ComplianceStatus = 'PASS'
  let reference = ruleset.pass_ref
  const reasons: string[] = []
  for (const code of findings) {
    const rule = ruleset.findings[code]
    if (!rule) continue
    reasons.push(`${code} → ${rule.status} (${rule.ref})`)
    if (SEVERITY[rule.status] > SEVERITY[status]) {
      status = rule.status
      reference = rule.ref
    }
  }

  const decisionText =
    status === 'BLOCK'
      ? 'Ausführung blockiert.'
      : status === 'WARN'
        ? 'Menschliche Autorisierung erforderlich.'
        : 'Ausführung autorisiert.'

  const humanAuthorized = status === 'WARN' && consent === true
  const effectiveStatus: ComplianceStatus = humanAuthorized ? 'PASS' : status
  const finalDecisionText = humanAuthorized
    ? 'Ausführung nach menschlicher Autorisierung freigegeben.'
    : decisionText

  const logEntry: LogEntry = {
    timestamp: tsNow(),
    angewandte_gerichtsbarkeit: ruleset.label,
    angeforderte_aktion: action,
    konformitätsstatus: status,
    gesetzliche_referenz: reference,
    endgültige_entscheidung: finalDecisionText,
  }

  return {
    jurisdiction: jur,
    rulesetLabel: ruleset.label,
    findings,
    pii,
    reasons,
    reference,
    status: effectiveStatus,
    originalStatus: status,
    decisionText,
    humanAuthorized,
    logEntry,
  }
}
