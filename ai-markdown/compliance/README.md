# Dynamisches Compliance-Gateway (D-C-G)

Ein nachvollziehbarer Filter **zwischen KI-Aktivität und Endnutzer**. Er passt
operative Einschränkungen anhand der Gerichtsbarkeit (GEO) und der lokalen
Vorschriften an und protokolliert jede Entscheidung.

> ⚠ **Wichtig:** Dies ist ein **technisches Governance-Gerüst**, **keine
> Rechtsberatung** und **keine zertifizierte Compliance**. Die GEO-Erkennung ist
> nur ein Indiz (kein verlässlicher Standortnachweis), und die Regeln sind
> illustrativ. Inhalte müssen mit Fachjuristen abgestimmt werden.

## Ablauf (pro Operation)

1. **GEO-Identifikation** – Profil aus erzwungenem Wert, Länder-Header
   (`x-geo-country`, `cf-ipcountry`, `x-vercel-ip-country`, `x-appengine-country`),
   echter **GeoIP-Auflösung der IP** (offline via `geoip-lite`, optionale
   Abhängigkeit) oder Fallback.
2. **Norm-Mapping** – passenden Regelsatz laden (EU = DSGVO/AI Act, UK = UK GDPR,
   US = NIST AI RMF/CCPA).
3. **Folgenabschätzung** – Aktion gegen die Einschränkungen prüfen: PII,
   **besondere Datenkategorien (DSGVO Art. 9)**, Datenmenge, verbotene Praktiken.
4. **Gatekeeping** –
   - **PASS:** ausführen
   - **WARN:** menschliche Autorisierung anfordern
   - **BLOCK:** ablehnen, begründetes Protokoll schreiben

## Erkannte Befunde

| Befund-Code           | Beispiel                                   | EU-Status |
| --------------------- | ------------------------------------------ | --------- |
| `PROHIBITED_PRACTICE` | „Social Scoring", Massenüberwachung        | BLOCK     |
| `SPECIAL_CATEGORY`    | Gesundheit, Religion, Gewerkschaft (Art. 9)| WARN      |
| `PII_PRESENT`         | E-Mail, IBAN, Kreditkarte, Telefon         | WARN      |
| `EXCESSIVE_DATA`      | Anfrage über `COMPLIANCE_MAX_CHARS`        | WARN      |

## Sicherheitsrichtlinie

- **Fail-closed:** Lässt sich der Audit-Log-Eintrag nicht schreiben, wird die
  Operation **blockiert** (keine nicht nachverfolgbare Operation).
- **Restriktiver Standard:** Ohne sichere GEO-Daten gilt das **DSGVO-Profil**.

## Pflicht-Log-Format

Jede Entscheidung wird als JSON-Zeile in `logs/decisions.log.jsonl` geschrieben:

```json
{
  "timestamp": "JJJJ-MM-TT HH:MM",
  "angewandte_gerichtsbarkeit": "...",
  "angeforderte_aktion": "...",
  "konformitätsstatus": "PASS/BLOCK/WARN",
  "gesetzliche_referenz": "...",
  "endgültige_entscheidung": "..."
}
```

## GeoIP (echte IP-Auflösung)

Die IP→Land-Auflösung nutzt das offline arbeitende Paket
[`geoip-lite`](https://www.npmjs.com/package/geoip-lite) (als
`optionalDependencies` eingetragen, wird bei `npm install` mitinstalliert).

- Ist es vorhanden, wird die Client-IP (`x-forwarded-for` bzw. Socket) aufgelöst.
- Fehlt es, bleibt die IP-Auflösung inaktiv und es greifen Header/Fallback –
  das Gateway funktioniert weiterhin.

Bewusst ohne externe API: keine zusätzlichen Datenflüsse, kein Schlüssel.

## Konfiguration (Umgebungsvariablen)

| Variable                        | Zweck                                            | Standard            |
| ------------------------------- | ------------------------------------------------ | ------------------- |
| `COMPLIANCE_FORCE_JURISDICTION` | Profil erzwingen (`EU`/`UK`/`US`/`DEFAULT`)      | – (GEO-Erkennung)   |
| `COMPLIANCE_MAX_CHARS`          | Max. Zeichen pro Anfrage (Datenminimierung)      | `50000`             |
| `COMPLIANCE_LOG_DIR`            | Verzeichnis für Audit-Logs                       | `compliance/logs`   |

## Einbindung

Das Gateway ist in `server.js` vor jeden `/api/assist`-Aufruf geschaltet:

- `BLOCK` → HTTP **403** mit Begründung
- `WARN` ohne Zustimmung → HTTP **428** (Frontend fragt Autorisierung ab und
  sendet erneut mit `consent: true`)
- `PASS` → Anfrage wird an Claude weitergereicht

Audit-Log abrufen: `GET /api/compliance/logs?limit=50` oder Button **Audit-Log**
in der Oberfläche.

## Demo (ohne API-Key)

```bash
node compliance/demo.js
```

Zeigt PASS/WARN/BLOCK für Beispieleingaben und schreibt echte Log-Einträge.

## Wiederverwendung

Das Modul ist eigenständig. Kernfunktion:

```js
import { runGateway } from "./compliance/gateway.js";

const result = await runGateway(req, { action, text, consent });
// result.allow, result.status, result.requiresAuthorization, result.logEntry ...
```
