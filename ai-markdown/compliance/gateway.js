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

// --- Echte GeoIP-Auflösung (optional, offline via geoip-lite) ----------------
// Wird einmalig geladen. Ist das Paket nicht installiert, bleibt die
// IP-Auflösung deaktiviert und es greifen Header/Fallback.
let geoipLookup = null;
let geoipLoaded = false;
async function ensureGeoip() {
  if (geoipLoaded) return;
  geoipLoaded = true;
  try {
    const mod = await import("geoip-lite");
    geoipLookup = (mod.default ?? mod).lookup ?? null;
  } catch {
    geoipLookup = null;
  }
}

function clientIp(req) {
  const xff = req?.headers?.["x-forwarded-for"];
  if (xff) return String(xff).split(",")[0].trim();
  return req?.socket?.remoteAddress || req?.connection?.remoteAddress || null;
}

function countryFromIp(req) {
  if (!geoipLookup) return null;
  const ip = clientIp(req);
  if (!ip) return null;
  try {
    return geoipLookup(ip)?.country || null;
  } catch {
    return null;
  }
}

// --- 1) GEO-IDENTIFIKATION ---------------------------------------------------
// Reihenfolge: erzwungenes Profil → Länder-Header (CDN/explizit) →
// echte GeoIP-Auflösung der IP → Fallback (restriktivstes Profil).
export function identifyGeo(req) {
  const forced = process.env.COMPLIANCE_FORCE_JURISDICTION;
  if (forced) {
    return {
      country: null,
      source: "env:FORCE",
      jurisdiction: forced.toUpperCase(),
      geoipActive: !!geoipLookup,
    };
  }

  const headers = req?.headers || {};
  const headerCountry =
    headers["x-geo-country"] ||
    headers["cf-ipcountry"] ||
    headers["x-vercel-ip-country"] ||
    headers["x-appengine-country"] ||
    null;

  let country = headerCountry;
  let source = headerCountry ? "header" : null;

  if (!country) {
    const ipCountry = countryFromIp(req);
    if (ipCountry) {
      country = ipCountry;
      source = "geoip";
    }
  }

  return {
    country: country || null,
    source: source || "fallback",
    jurisdiction: mapCountryToJurisdiction(country),
    geoipActive: !!geoipLookup,
  };
}

// --- 2) NORM-MAPPING ---------------------------------------------------------
export function loadRuleset(jurisdiction) {
  return RULESETS[jurisdiction] || RULESETS.DEFAULT;
}

// Illustrative Muster-Erkennung (PII / verbotene Praktiken / Art. 9).
const PATTERNS = {
  email: /[\w.+-]+@[\w-]+\.[\w.-]+/,
  iban: /\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b/,
  kreditkarte: /\b(?:\d[ -]?){13,16}\b/,
  telefon: /\+\d{2,3}[ -]?\d{3,}/,
};
const PROHIBITED =
  /\b(social[\s-]?scoring|sozial(es)?[\s-]?scoring|biometr\w*\s+(kategorisierung|identifizierung)|mass\s+surveillance|massen[üu]berwachung)\b/i;

// Besondere Kategorien personenbezogener Daten (DSGVO Art. 9), illustrativ.
const SPECIAL_CATEGORY =
  /\b(gesundheit|krankheit|diagnose|patient\w*|medizinisch\w*|health|disease|medical|religion|religi(?:ö|oe)s|konfession|ethnisch\w*|rasse|race|ethnic\w*|politische\s+(?:meinung|überzeugung|einstellung)|political\s+opinion|gewerkschaft\w*|trade\s+union|sexuelle\s+(?:orientierung|identität)|sexual\s+orientation|biometr\w*|genetisch\w*|genetic|dna)\b/i;

// --- 3) FOLGENABSCHÄTZUNG ----------------------------------------------------
// Prüft die angeforderte Aktion gegen die Einschränkungen und liefert Befunde.
export function assess({ action = "", text = "" }) {
  const findings = [];
  const haystack = `${action}\n${text}`;

  if (PROHIBITED.test(haystack)) findings.push("PROHIBITED_PRACTICE");
  if (SPECIAL_CATEGORY.test(text)) findings.push("SPECIAL_CATEGORY");

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
 */
export async function runGateway(req, { action, text = "", consent = false }) {
  await ensureGeoip();

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
