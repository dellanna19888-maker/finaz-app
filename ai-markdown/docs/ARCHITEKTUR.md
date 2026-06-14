# Architektur

Dieses Dokument beschreibt den Aufbau von **AI Markdown** – einem KI-gestützten
Markdown-Editor mit Live-Vorschau.

## Überblick

```
Browser (public/)                Node.js-Server (server.js)         Claude API
─────────────────                ──────────────────────────         ──────────
index.html / app.js  ──fetch──►  POST /api/assist            ──►   messages.stream()
   Editor + Vorschau   (JSON)        baut Prompt                       (Opus-Modell)
   KI-Panel          ◄──SSE────      streamt Antwort  ◄────────────    Text-Deltas
```

Der Browser spricht **ausschließlich** das eigene Backend an. Der API-Key liegt
nur serverseitig und verlässt den Server nie.

## Komponenten

### Frontend (`public/`)

- **index.html** – Grundgerüst: Toolbar, Editor- und Vorschau-Bereich, KI-Panel.
- **app.js** – Editor-Logik:
  - rendert die Live-Vorschau mit [marked](https://marked.js.org/),
  - sichert den Text in `localStorage`,
  - ruft `POST /api/assist` auf und liest die Antwort als SSE-Stream,
  - bietet *Übernehmen*, *Anhängen*, *Kopieren* für KI-Ergebnisse.
- **styles.css** – Dark-Theme, zweispaltiges Layout, responsiv.

### Backend (`server.js`)

- **Express** liefert die statischen Dateien aus `public/` aus.
- **`POST /api/assist`** nimmt `{ action, text, instruction, language }` entgegen,
  baut daraus einen Prompt und streamt die Claude-Antwort als
  Server-Sent Events zurück.
- Der **Anthropic-SDK-Client** (`@anthropic-ai/sdk`) wird nur erstellt, wenn ein
  `ANTHROPIC_API_KEY` gesetzt ist.

## Aktionen

| Aktion       | Bedeutung                                            |
| ------------ | --------------------------------------------------- |
| `generate`   | Neues Dokument aus einer Beschreibung erzeugen      |
| `improve`    | Vorhandenes Markdown überarbeiten                   |
| `continue`   | Dokument sinnvoll weiterschreiben                   |
| `summarize`  | Kernpunkte als Liste zusammenfassen                 |
| `translate`  | In die gewählte Zielsprache übersetzen              |

## Datenfluss (Streaming)

1. `app.js` sendet die Aktion per `fetch` an `/api/assist`.
2. `server.js` baut den Prompt und ruft `client.messages.stream(...)` auf.
3. Jeder Text-Abschnitt wird als `data: {"type":"delta","text":"..."}` gesendet.
4. Am Ende folgt `data: {"type":"done"}` (oder `{"type":"error"}`).
5. Das Frontend hängt die Deltas im KI-Panel an.

## Compliance-Gateway (D-C-G)

Vor jedem Modell-Aufruf prüft das Gateway (`compliance/`) die Operation:
`Browser → /api/assist → [D-C-G] → Claude API`.

Schritte: GEO-Identifikation → Norm-Mapping → Folgenabschätzung → Gatekeeping,
anschließend Audit-Log (JSONL, Pflichtformat).

- **PASS** → weiterreichen · **WARN** → HTTP 428 (Autorisierung) · **BLOCK** → HTTP 403
- Fail-closed (kein Log ⇒ Block), Standardprofil = DSGVO.

Details: [`../compliance/README.md`](../compliance/README.md).

## Konfiguration

| Variable            | Zweck                          | Standard          |
| ------------------- | ------------------------------ | ----------------- |
| `ANTHROPIC_API_KEY` | Authentifizierung (Pflicht)    | –                 |
| `CLAUDE_MODEL`      | Verwendetes Modell             | `claude-opus-4-8` |
| `PORT`              | Server-Port                    | `3000`            |

## Erweiterungsideen

- **Höhere Qualität:** in `server.js` adaptives Denken aktivieren
  (`thinking: { type: "adaptive" }`) – etwas langsamer, dafür gründlicher.
- Datei-Export (`.md` herunterladen) und Datei-Import.
- Mehrere Dokumente / Tabs.
- Auswahl-basiertes Bearbeiten (nur markierten Text an die KI senden).
