// Zuordnung Ländercode -> Gerichtsbarkeitsprofil und die zugehörigen Regelsätze.
//
// ⚠ HINWEIS: Stark vereinfacht und illustrativ. Dies ist KEINE Rechtsberatung
// und keine vollständige Abbildung von DSGVO, EU AI Act, CCPA oder NIST AI RMF.
// Die Zuordnungen müssen mit Fachjuristen abgestimmt werden.

const EU_EEA = new Set([
  "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR",
  "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
  "SI", "ES", "SE", "IS", "LI", "NO",
]);

/** Bildet einen ISO-Ländercode auf ein Gerichtsbarkeitsprofil ab. */
export function mapCountryToJurisdiction(country) {
  if (!country) return "DEFAULT";
  const c = String(country).toUpperCase();
  if (EU_EEA.has(c)) return "EU";
  if (c === "GB" || c === "UK") return "UK";
  if (c === "US") return "US";
  return "DEFAULT";
}

// Regelsätze: Pro Profil legen wir das Label, die Abbildung von Befund-Codes auf
// Konformitätsstatus (mit gesetzlicher Referenz) sowie eine PASS-Referenz fest.
const EU_FINDINGS = {
  PROHIBITED_PRACTICE: { status: "BLOCK", ref: "EU AI Act Art. 5 (verbotene Praktiken)" },
  SPECIAL_CATEGORY: { status: "WARN", ref: "DSGVO Art. 9 (besondere Kategorien personenbezogener Daten)" },
  PII_PRESENT: { status: "WARN", ref: "DSGVO Art. 6 / Art. 28 (Auftragsverarbeitung, Rechtsgrundlage)" },
  EXCESSIVE_DATA: { status: "WARN", ref: "DSGVO Art. 5(1)(c) (Datenminimierung)" },
};

export const RULESETS = {
  EU: {
    label: "EU (DSGVO + EU AI Act)",
    findings: EU_FINDINGS,
    pass_ref: "DSGVO / EU AI Act Art. 50 (Transparenzpflicht erfüllt)",
  },
  UK: {
    label: "UK (UK GDPR)",
    findings: {
      PROHIBITED_PRACTICE: { status: "BLOCK", ref: "UK-Richtlinie / verbotene Praktiken" },
      SPECIAL_CATEGORY: { status: "WARN", ref: "UK GDPR Art. 9 (besondere Kategorien)" },
      PII_PRESENT: { status: "WARN", ref: "UK GDPR Art. 6 / Art. 28" },
      EXCESSIVE_DATA: { status: "WARN", ref: "UK GDPR Art. 5(1)(c) (Datenminimierung)" },
    },
    pass_ref: "UK GDPR (Transparenz erfüllt)",
  },
  US: {
    label: "USA (NIST AI RMF / CCPA)",
    findings: {
      PROHIBITED_PRACTICE: { status: "BLOCK", ref: "Interne Richtlinie / NIST AI RMF (GOVERN)" },
      SPECIAL_CATEGORY: { status: "WARN", ref: "CCPA/CPRA (sensible personenbezogene Daten)" },
      PII_PRESENT: { status: "WARN", ref: "CCPA §1798.100 (Notice at Collection)" },
      EXCESSIVE_DATA: { status: "PASS", ref: "NIST AI RMF (MAP)" },
    },
    pass_ref: "NIST AI RMF (MEASURE / MANAGE)",
  },
  // Fallback = restriktivstes Profil (DSGVO), siehe Sicherheitsrichtlinie.
  DEFAULT: {
    label: "Unbekannt → restriktivstes Profil (DSGVO)",
    findings: EU_FINDINGS,
    pass_ref: "DSGVO (restriktives Standardprofil)",
  },
};
