# Hub – KI-Arbeits-Hub

Ein **KI-gesteuerter Arbeits-/Business-Hub für Online-Creator** (Vue 3 + Vite + TypeScript + Pinia, PWA):
**Content-Plan**, **Kanal-Check**, **Finanzen**, **Wissen/Notizen** und **Support** – alles über eine
zentrale **KI-Schaltzentrale** bedienbar, abgesichert durch ein **Compliance-Gateway**, das jede
KI-Operation prüft und protokolliert. **Ein Projekt, eine App** – alle früheren Einzelteile
(Finanz-App, Markdown-Editor, Compliance-Konsole, Creator-Tools) sind hier vereint.

## Funktionen

- 🧠 **Zentrale:** KI-Schaltzentrale (Startseite) – im Chat die ganze App steuern; die KI schlägt Aktionen vor (Aufgabe anlegen/bearbeiten/abhaken/löschen, Wissen/Notiz ergänzen, navigieren, Compliance-Prüfung), die du per Klick **bestätigst** und ausführst – inkl. **Rückgängig** für die letzte Aktion. Ergebnisse fließen in den Dialog zurück, sodass die KI den neuen Stand kennt
- 📋 **Aufgaben/Projekte:** To-dos mit Priorität, Projekt und Fälligkeit – per Hand oder über die Zentrale
- 💰 **Finanzen:** Einnahmen &amp; Ausgaben des Creator-Business (Kategorien, Saldo, Währung) – buchbar per Hand oder über die Zentrale, plus **KI-Finanzüberblick** auf Knopfdruck
- 📚 **Wissen/Notizen:** Markdown-Editor mit KI (Generieren, Verbessern, Fortsetzen, Zusammenfassen, Übersetzen)
- 💬 **Support-Assistent:** die Zentrale beantwortet Fragen sachlich aus deiner Wissensbasis
- 🛡️ **Compliance (D-C-G):** jede KI-Anfrage läuft durch ein Gateway → **PASS / WARN / BLOCK** + Audit-Log

## Architektur

```
Vue-SPA (src/)  ──/api──►  Express-Backend (server/)  ──►  Claude / Gemini API
   Views: Zentrale, Content,   Compliance-Gateway (evaluate)
   Kanal, Finanzen, Wissen,    + Audit-Log (JSONL)
   Compliance
        │
   src/compliance/gateway.ts  ← gemeinsamer, isomorpher Kern (Client + Server)
```

- Der **API-Key bleibt serverseitig** (im Backend), nie im Browser.
- Das **Compliance-Gateway** ist ein isomorphes Modul: die Client-Seite kann
  Operationen sofort lokal prüfen, der Server prüft + protokolliert echte Aufrufe.

## Setup

```bash
npm install
cp .env.example .env      # ANTHROPIC_API_KEY eintragen (nur für KI-Funktionen)
npm run dev:all           # startet Vite (Frontend) UND das API-Backend
```

- Frontend: http://localhost:5173  ·  API: http://localhost:3001 (per Vite-Proxy unter `/api`)
- Alternativ getrennt: `npm run dev` (nur Frontend) und `npm run api` (nur Backend)

### Als Demo mit eigenem Key (ein Befehl)

```bash
npm install
npm run demo     # baut das Frontend und startet ALLES auf http://localhost:3001
```

Dann **http://localhost:3001** öffnen und unter **⚙️ Einstellungen** deinen
**eigenen** KI-Schlüssel eintragen – Anthropic **oder kostenlos Google Gemini**. Der Key wird nur im
Browser gespeichert und pro Anfrage an dein lokales Backend gesendet – er landet
**nie** im Repository. Alternativ kann der Server einen Key aus `.env`
(`ANTHROPIC_API_KEY`) nutzen.

Ohne Key laufen die **Aufgaben**, die **Finanzen** (Buchungen + Kennzahlen) und die
**Compliance-Seite** (lokale Prüfung + Audit-Log) vollständig; nur die **Zentrale**,
der **KI-Finanzüberblick** und die KI-Funktionen der **Notizen** brauchen einen Key.

## Skripte

| Skript            | Zweck                                            |
| ----------------- | ------------------------------------------------ |
| `npm run dev`     | Vite-Frontend                                    |
| `npm run api`     | API-Backend (Claude + Compliance-Gateway)        |
| `npm run dev:all` | Frontend + Backend parallel                      |
| `npm run demo`    | Build + Backend auf **einem** Port (eine URL)    |
| `npm run build`   | Typecheck + Produktions-Build (`dist/`)          |

## Konfiguration (`.env`)

| Variable                        | Zweck                                       | Standard          |
| ------------------------------- | ------------------------------------------- | ----------------- |
| `ANTHROPIC_API_KEY`             | Claude-Key (optional – sonst Key im Browser via ⚙️) | –           |
| `CLAUDE_MODEL`                  | Modell                                      | `claude-opus-4-8` |
| `GEMINI_API_KEY`                | Gratis-Alternative (Google Gemini, falls kein Anthropic-Key) | –   |
| `GEMINI_MODEL`                  | Gemini-Modell                               | `gemini-2.0-flash` |
| `API_PORT`                      | Port des Backends (= Vite-Proxy-Ziel)       | `3001`            |
| `COMPLIANCE_FORCE_JURISDICTION` | Profil erzwingen (`EU`/`UK`/`US`/`DEFAULT`) | – (GEO-Erkennung) |
| `COMPLIANCE_MAX_CHARS`          | Datenminimierung (max. Zeichen)             | `50000`           |
| `ENABLE_GEOIP`                  | Echte GeoIP-Auflösung der IP (geoip-lite, ~150 MB RAM) | aus    |

## Compliance-Gateway (D-C-G)

Vor jedem Modell-Aufruf: GEO-Identifikation → Norm-Mapping (EU/UK/US/DEFAULT) →
Folgenabschätzung (PII, besondere Kategorien nach DSGVO Art. 9, Datenmenge,
verbotene Praktiken) → Gatekeeping. **Fail-closed** (kein Audit-Log ⇒ Block),
Standardprofil ist **DSGVO**. Die **GEO-Identifikation** wertet CDN-Header aus;
optional (per `ENABLE_GEOIP=1`, Paket `geoip-lite`, ~150 MB RAM) wird zusätzlich
die Client-IP offline zu einem Land aufgelöst. Endpoints: `POST /api/assist`,
`POST /api/chat` (Zentrale/Dialog), `POST /api/compliance/check` (Simulation),
`GET /api/compliance/logs`.

> ⚠ Technisches Governance-Gerüst, **keine Rechtsberatung** und keine
> zertifizierte Compliance. Regeln/GEO sind illustrativ.

## Deployment

Vollständige Anleitung: [`DEPLOY.md`](./DEPLOY.md). Auf einem **Chromebook**
selbst hosten (Linux-Umgebung): [`CHROMEBOOK.md`](./CHROMEBOOK.md).

**Volle Version inkl. KI (mit eigenem Key):**

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/dellanna19888-maker/finaz-app)

In Render den richtigen Branch wählen (oder vorher nach `main` mergen) und
`ANTHROPIC_API_KEY` als Secret setzen. Universell auch per `Dockerfile`
(jeder Container-Host) – siehe `DEPLOY.md`.

**Kostenloser Vorschau-Link (GitHub Pages, ohne Key):** Der Workflow
`.github/workflows/deploy.yml` veröffentlicht das statische Frontend. Dort laufen
Aufgaben + Compliance; die **KI braucht ein Backend** (siehe oben). Voraussetzung:
GitHub Pages aktiviert (Settings → Pages → Source: „GitHub Actions").

**Bonus – Offline-Finanz-Demo (Vorgänger):** Die Datei
[`finazapp.html`](./finazapp.html) ist die eigenständige Single-Page-**Finanz**-Demo,
aus der dieses Projekt hervorging. Ihre Funktion lebt jetzt **im Hub** unter
**💰 Finanzen** weiter; die HTML-Datei bleibt als reine Offline-Variante erhalten:
Sie nutzt die lokal im Ordner [`vendor/`](./vendor/) mitgelieferten Bibliotheken und
läuft **komplett ohne Internet** und ohne Backend – einfach `finazapp.html` (mit dem
`vendor/`-Ordner daneben) im Browser öffnen.
