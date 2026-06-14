// Dynamisches Compliance-Gateway (D-C-G)
//
// Intelligenter Filter zwischen KI-Aktivität und Endnutzer. Führt pro Operation
// vier Schritte aus: GEO-Identifikation → Norm-Mapping → Folgenabschätzung →
// Gatekeeping, und protokolliert jede Entscheidung im Pflicht-Log-Format.
//
// ⚠ Governance-Gerüst, keine Rechtsberatung / keine zertifizierte Compliance.

import { mapCountryToJurisdiction, RULESETS } from "./rulesets.js";
import { writeDecisionLog } from "./logger.js";

const SEVERITY = { PASS: 1, WARN: 2, BLOCK: 3 };

// Zeitstempel im Pflichtformat "JJJJ-MM-TT HH:MM" (UTC).
function tsNow() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return (
    `${d.getUTCFullYear()}-${p(d.getUTCMonth() + 1)}-${p(d.getUTCDate())} ` +
    `${p(d.getUTCHours())}:${p(d.getUTCMinutes())}`
  );
}

// --- 1) GEO-IDENTIFIKATION ---------------------------------------------------
// Ermittelt das Gerichtsbarkeitsprofil aus (Reihenfolge): erzwungenem Profil,
// gängigen GeoIP-Headern, sonst Fallback auf das restriktivste Profil.
export function identifyGeo(req) {
  const forced = process.env.COMPLIANCE_FORCE_JURISDICTION;
  if (forced) {
    return { country: null, source: "env:FORCE", jurisdiction: forced.toUpperCase() };
  }

  const headers = req?.headers || {};
  const country =
    headers["x-geo-country"] ||
    headers["cf-ipcountry"] ||
    headers["x-vercel-ip-country"] ||
    headers["x-appengine-country"] ||
    null;

  const jurisdiction = mapCountryToJurisdiction(country);
  return {
    country: country || null,
    source: country ? "header" : "fallback",
    jurisdiction,
  };
}

// --- 2) NORM-MAPPING ---------------------------------------------------------
export function loadRuleset(jurisdiction) {
  return RULESETS[jurisdiction] || RULESETS.DEFAULT;
}

// Illustrative Muster-Erkennung (PII / verbotene Praktiken).
const PATTERNS = {
  email: /[\w.+-]+@[\w-]+\.[\w.-]+/,
  iban: /\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b/,
  kreditkarte: /\b(?:\d[ -]?){13,16}\b/,
  telefon: /\+\d{2,3}[ -]?\d{3,}/,
};
const PROHIBITED =
  /\b(social[\s-]?scoring|sozial(es)?[\s-]?scoring|biometr\w*\s+(kategorisierung|identifizierung)|mass\s+surveillance|massen[üu]berwachung)\b/i;

// --- 3) FOLGENABSCHÄTZUNG ----------------------------------------------------
// Prüft die angeforderte Aktion gegen die Einschränkungen und liefert Befunde.
export function assess({ action = "", text = "" }) {
  const findings = [];
  const haystack = `${action}\n${text}`;

  if (PROHIBITED.test(haystack)) findings.push("PROHIBITED_PRACTICE");

  const pii = Object.entries(PATTERNS)
    .filter(([, re]) => re.test(text))
    .map(([name]) => name);
  if (pii.length) findings.push("PII_PRESENT");

  const maxChars = Number(process.env.COMPLIANCE_MAX_CHARS) || 50000;
  if (text.length > maxChars) findings.push("EXCESSIVE_DATA");

  return { findings, pii };
}

// --- 4) GATEKEEPING (Entscheidungsfindung, ohne Logging) ---------------------
export function decide({ ruleset, assessment }) {
  let status = "PASS";
  let ref = ruleset.pass_ref;
  const reasons = [];

  for (const code of assessment.findings) {
    const rule = ruleset.findings[code];
    if (!rule) continue;
    reasons.push(`${code} → ${rule.status} (${rule.ref})`);
    if (SEVERITY[rule.status] > SEVERITY[status]) {
      status = rule.status;
      ref = rule.ref;
    }
  }

  const decisionText =
    status === "BLOCK"
      ? "Ausführung blockiert."
      : status === "WARN"
        ? "Menschliche Autorisierung erforderlich."
        : "Ausführung autorisiert.";

  return { status, ref, reasons, decisionText };
}

/**
 * Orchestriert das gesamte Gateway für eine Operation und protokolliert die
 * Entscheidung. `consent === true` steht für eine erteilte menschliche
 * Autorisierung (hebt einen WARN-Befund für diese Operation auf).
 *
 * Rückgabe u. a.:
 *   allow                 – darf die Operation ausgeführt werden?
 *   requiresAuthorization – WARN ohne erteilte Autorisierung?
 *   status                – effektiver Status nach Autorisierung
 *   originalStatus        – ursprünglicher Befund (PASS/WARN/BLOCK)
 *   logEntry              – geschriebener Pflicht-Log-Eintrag
 */
export async function runGateway(req, { action, text = "", consent = false }) {
  const geo = identifyGeo(req);
  const ruleset = loadRuleset(geo.jurisdiction);
  const assessment = assess({ action, text });
  const decision = decide({ ruleset, assessment });

  const humanAuthorized = decision.status === "WARN" && consent === true;
  const effectiveStatus = humanAuthorized ? "PASS" : decision.status;

  const finalDecisionText = humanAuthorized
    ? "Ausführung nach menschlicher Autorisierung freigegeben."
    : decision.decisionText;

  // Pflicht-Log-Format (exakt diese Felder).
  const logEntry = {
    timestamp: tsNow(),
    angewandte_gerichtsbarkeit: ruleset.label,
    angeforderte_aktion: action,
    konformitätsstatus: decision.status,
    gesetzliche_referenz: decision.ref,
    endgültige_entscheidung: finalDecisionText,
  };

  // Sicherheitsrichtlinie: Keine nicht nachverfolgbare Operation zulassen.
  // Schlägt das Schreiben des Audit-Logs fehl, wird hart blockiert.
  try {
    await writeDecisionLog(logEntry);
  } catch (err) {
    return {
      allow: false,
      requiresAuthorization: false,
      status: "BLOCK",
      originalStatus: "BLOCK",
      geo,
      ruleset: ruleset.label,
      decision: {
        status: "BLOCK",
        ref: "Sicherheitsrichtlinie (Audit-Pflicht)",
        reasons: [`Audit-Log nicht schreibbar: ${err.message}`],
        decisionText: "Operation blockiert – Audit-Log nicht schreibbar.",
      },
      assessment,
      logEntry,
      logged: false,
    };
  }

  return {
    allow: effectiveStatus === "PASS",
    requiresAuthorization: decision.status === "WARN" && !humanAuthorized,
    status: effectiveStatus,
    originalStatus: decision.status,
    geo,
    ruleset: ruleset.label,
    decision,
    assessment,
    logEntry,
    logged: true,
  };
}
