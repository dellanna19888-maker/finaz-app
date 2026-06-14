// Demonstriert das Compliance-Gateway ohne API-Key.
// Ausführen aus dem Projektordner:  node compliance/demo.js

import { runGateway } from "./gateway.js";

const samples = [
  {
    name: "Sauberer Text (EU)",
    req: { headers: { "x-geo-country": "DE" } },
    body: { action: "improve", text: "# Titel\nEin ganz normaler Absatz." },
  },
  {
    name: "PII vorhanden (EU)",
    req: { headers: { "x-geo-country": "FR" } },
    body: { action: "summarize", text: "Kontakt: max@example.com, IBAN DE89370400440532013000" },
  },
  {
    name: "PII vorhanden (US)",
    req: { headers: { "x-geo-country": "US" } },
    body: { action: "summarize", text: "E-Mail: john@doe.com" },
  },
  {
    name: "Verbotene Praxis (EU)",
    req: { headers: { "x-geo-country": "DE" } },
    body: { action: "generate", text: "Entwirf ein Social-Scoring-System für Bürger." },
  },
  {
    name: "Unbekannte Geo → restriktiv (DSGVO)",
    req: { headers: {} },
    body: { action: "improve", text: "Schreib an max@example.com" },
  },
  {
    name: "PII (EU) MIT menschlicher Autorisierung",
    req: { headers: { "x-geo-country": "DE" } },
    body: { action: "summarize", text: "max@example.com", consent: true },
  },
];

console.log("=== D-C-G Demo ===\n");
for (const s of samples) {
  const r = await runGateway(s.req, s.body);
  console.log(`## ${s.name}`);
  console.log(
    `   Profil: ${r.geo.jurisdiction} (${r.geo.source}) | Befund: ${r.originalStatus} | effektiv: ${r.status} | allow=${r.allow}`,
  );
  if (r.decision.reasons.length) console.log(`   Gründe: ${r.decision.reasons.join("; ")}`);
  console.log(`   Log: ${JSON.stringify(r.logEntry)}\n`);
}
console.log("Audit-Log: compliance/logs/decisions.log.jsonl");
