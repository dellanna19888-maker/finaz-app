# FinazApp

Persönliche **Finanz-App** (Vue 3 + Vite + TypeScript + Pinia, PWA) – mit
integriertem **KI-Assistenten**, **Markdown-Notizen** und einem **Compliance-Gateway**,
das jede KI-Operation prüft und protokolliert.

## Funktionen

- 💰 **Finanzen:** Dashboard, Transaktionen, Budgets, Berichte (Charts)
- 🤖 **KI-Assistent:** erzeugt aus deinen Daten Monatsberichte, Budget-Insights und Spar-Tipps (Claude)
- 📝 **Notizen:** Markdown-Editor mit KI (Generieren, Verbessern, Fortsetzen, Zusammenfassen, Übersetzen)
- 🛡️ **Compliance (D-C-G):** jede KI-Anfrage läuft durch ein Gateway → **PASS / WARN / BLOCK** + Audit-Log

## Architektur

```
Vue-SPA (src/)  ──/api──►  Express-Backend (server/)  ──►  Claude API
   Views: Assistant,          Compliance-Gateway (evaluate)
   Notes, Compliance          + Audit-Log (JSONL)
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
**eigenen** Anthropic-API-Key eintragen (Bring Your Own Key). Der Key wird nur im
Browser gespeichert und pro Anfrage an dein lokales Backend gesendet – er landet
**nie** im Repository. Alternativ kann der Server einen Key aus `.env`
(`ANTHROPIC_API_KEY`) nutzen.

Ohne Key laufen Finanz-App und die **Compliance-Seite** (lokale Prüfung +
Audit-Log) vollständig; nur KI-Assistent/Notizen brauchen einen Key.

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
| `API_PORT`                      | Port des Backends (= Vite-Proxy-Ziel)       | `3001`            |
| `COMPLIANCE_FORCE_JURISDICTION` | Profil erzwingen (`EU`/`UK`/`US`/`DEFAULT`) | – (GEO-Erkennung) |
| `COMPLIANCE_MAX_CHARS`          | Datenminimierung (max. Zeichen)             | `50000`           |

## Compliance-Gateway (D-C-G)

Vor jedem Modell-Aufruf: GEO-Identifikation → Norm-Mapping (EU/UK/US/DEFAULT) →
Folgenabschätzung (PII, besondere Kategorien nach DSGVO Art. 9, Datenmenge,
verbotene Praktiken) → Gatekeeping. **Fail-closed** (kein Audit-Log ⇒ Block),
Standardprofil ist **DSGVO**. Endpoints: `POST /api/assist`,
`POST /api/compliance/check` (Simulation), `GET /api/compliance/logs`.

> ⚠ Technisches Governance-Gerüst, **keine Rechtsberatung** und keine
> zertifizierte Compliance. Regeln/GEO sind illustrativ.

## Deployment

`npm run build` erzeugt ein statisches Frontend (`dist/`, z. B. für GitHub Pages).
Die **KI-Funktionen benötigen das laufende Backend** (`server/`) – dieses separat
hosten (oder denselben Prozess nutzen: der Server liefert `dist/` mit aus, falls
vorhanden). Die Compliance-Seite funktioniert auch rein statisch (lokale Prüfung).

---

Hinweis: Das eigenständige KI-Markdown-Projekt liegt zusätzlich unter
[`ai-markdown/`](./ai-markdown/) (separater Express-Server + Compliance Console).
