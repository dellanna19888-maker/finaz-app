# AI Markdown

KI-gestützter **Markdown-Editor** mit Live-Vorschau. Schreibe, verbessere,
übersetze und fasse Markdown mit **Claude** (Anthropic) zusammen.

## Features

- ✍️ Editor mit Live-Vorschau ([marked](https://marked.js.org/))
- 🤖 KI-Aktionen: **Generieren, Verbessern, Fortsetzen, Zusammenfassen, Übersetzen**
- ⚡ Streaming-Antworten (Server-Sent Events) – Text erscheint live
- 🔒 API-Key bleibt serverseitig, niemals im Browser
- 🧩 Kein Build-Schritt: Vanilla-JS-Frontend + schlankes Express-Backend
- 💾 Automatisches Speichern im Browser (`localStorage`)
- 🛡️ **Compliance-Gateway (D-C-G):** jurisdiktionsabhängiger Filter + Audit-Log

## Voraussetzungen

- [Node.js](https://nodejs.org/) ≥ 18
- Ein Anthropic API-Key – kostenlos anlegbar unter <https://platform.claude.com>

## Schnellstart

```bash
npm install
cp .env.example .env
# .env öffnen und ANTHROPIC_API_KEY eintragen
npm start
```

Dann <http://localhost:3000> im Browser öffnen.

## Konfiguration (`.env`)

| Variable                        | Beschreibung                                   | Standard          |
| ------------------------------- | ---------------------------------------------- | ----------------- |
| `ANTHROPIC_API_KEY`             | Dein Anthropic API-Key (**erforderlich**)      | –                 |
| `CLAUDE_MODEL`                  | Zu verwendendes Claude-Modell                  | `claude-opus-4-8` |
| `PORT`                          | Port des Servers                               | `3000`            |
| `COMPLIANCE_FORCE_JURISDICTION` | Profil erzwingen (`EU`/`UK`/`US`/`DEFAULT`)    | – (GEO-Erkennung) |
| `COMPLIANCE_MAX_CHARS`          | Max. Zeichen pro Anfrage (Datenminimierung)    | `50000`           |
| `COMPLIANCE_LOG_DIR`            | Verzeichnis für Audit-Logs                     | `compliance/logs` |

## Projektstruktur

```
ai-markdown/
├── server.js           # Express-Backend, Proxy zur Claude-API (SSE-Streaming)
├── public/
│   ├── index.html      # Editor-Oberfläche
│   ├── compliance.html # Compliance Console (Web-Tool)
│   ├── styles.css      # Styling (Dark-Theme, responsiv)
│   ├── app.js          # Editor-Logik, Vorschau, Streaming-Client
│   └── compliance.js   # Logik der Compliance Console
├── compliance/         # Dynamisches Compliance-Gateway (D-C-G)
│   ├── gateway.js      # GEO → Norm-Mapping → Folgenabschätzung → Gatekeeping
│   ├── rulesets.js     # Gerichtsbarkeits-Profile (EU/UK/US/DEFAULT)
│   ├── logger.js       # Audit-Log (JSONL, Pflichtformat)
│   ├── demo.js         # Demo ohne API-Key
│   └── README.md       # Doku des Gateways
├── docs/
│   └── ARCHITEKTUR.md  # Architektur-Dokumentation
├── .env.example
├── package.json
└── LICENSE
```

## API

`POST /api/assist` – Body: `{ action, text, instruction, language, consent }`
→ streamt das Ergebnis als Server-Sent Events.

Aktionen: `generate`, `improve`, `continue`, `summarize`, `translate`.

Gateway-Antworten: **403** (blockiert) und **428** (menschliche Autorisierung
erforderlich – erneut mit `consent: true` senden).

`GET /api/compliance/logs?limit=50` – liefert die letzten Audit-Entscheidungen.

## Compliance-Gateway (D-C-G)

Jede `/api/assist`-Anfrage durchläuft zuerst ein Compliance-Gateway, das die
Operation je nach Gerichtsbarkeit (GEO) prüft und protokolliert:

- **PASS** → Ausführung
- **WARN** → menschliche Autorisierung (Frontend fragt nach, sendet dann `consent: true`)
- **BLOCK** → Ablehnung mit begründetem Audit-Log

Fail-closed: ohne schreibbares Audit-Log wird blockiert; ohne sichere GEO-Daten
gilt das DSGVO-Profil. Echte **GeoIP-Auflösung** der IP läuft über die optionale
Abhängigkeit `geoip-lite` (offline); zusätzlich werden **besondere
Datenkategorien** nach DSGVO Art. 9 erkannt. Audit-Log per Button **Audit-Log**
in der Oberfläche oder `GET /api/compliance/logs`. Demo ohne API-Key:
`node compliance/demo.js`. Details: [`compliance/README.md`](./compliance/README.md).

**Web-Tool – Compliance Console:** Unter `/compliance.html` (Link „🛡️ Compliance"
im Editor) lassen sich Operationen interaktiv prüfen (Simulation via
`POST /api/compliance/check`, ohne API-Key) und das Audit-Log durchsuchen sowie
als **CSV** exportieren.

Zum **schnellen Ansehen ohne Setup** gibt es eine eigenständige Offline-Demo:
[`preview/console-preview.html`](./preview/console-preview.html) – einfach im
Browser öffnen (oder auf einen Static-Host wie GitHub Pages legen, um eine echte
URL zu erhalten).

> ⚠ Technisches Governance-Gerüst, **keine Rechtsberatung** und keine
> zertifizierte Compliance.

## In ein eigenes Repo übernehmen

Dieses Projekt liegt aktuell im Unterordner `ai-markdown/` des Repos `finaz-app`.
So machst du daraus dein eigenes, eigenständiges Repository:

1. Lege auf GitHub ein **leeres** Repo `ai-markdown` an (ohne README/.gitignore).
2. Lokal:

   ```bash
   # finaz-app holen (falls noch nicht geschehen)
   git clone https://github.com/dellanna19888-maker/finaz-app.git
   # nur den Ordner in einen neuen Projektordner kopieren
   cp -r finaz-app/ai-markdown ai-markdown
   cd ai-markdown

   git init
   git add .
   git commit -m "Initialer Commit: AI Markdown"
   git branch -M main
   git remote add origin https://github.com/dellanna19888-maker/ai-markdown.git
   git push -u origin main
   ```

Danach ist `ai-markdown` ein vollwertiges, separates Repository.

## Sicherheit

Der API-Key wird ausschließlich serverseitig verwendet. Das Frontend
kommuniziert nur mit dem eigenen Backend (`/api/assist`). Das Compliance-Gateway
protokolliert jede Entscheidung nachvollziehbar (Audit-Log).

## Lizenz

[MIT](./LICENSE)
