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

| Variable            | Beschreibung                              | Standard          |
| ------------------- | ----------------------------------------- | ----------------- |
| `ANTHROPIC_API_KEY` | Dein Anthropic API-Key (**erforderlich**) | –                 |
| `CLAUDE_MODEL`      | Zu verwendendes Claude-Modell             | `claude-opus-4-8` |
| `PORT`              | Port des Servers                          | `3000`            |

## Projektstruktur

```
ai-markdown/
├── server.js           # Express-Backend, Proxy zur Claude-API (SSE-Streaming)
├── public/
│   ├── index.html      # Benutzeroberfläche
│   ├── styles.css      # Styling (Dark-Theme, responsiv)
│   └── app.js          # Editor-Logik, Vorschau, Streaming-Client
├── docs/
│   └── ARCHITEKTUR.md  # Architektur-Dokumentation
├── .env.example
├── package.json
└── LICENSE
```

## API

`POST /api/assist` – Body: `{ action, text, instruction, language }`
→ streamt das Ergebnis als Server-Sent Events.

Aktionen: `generate`, `improve`, `continue`, `summarize`, `translate`.

## In ein eigenes Repo übernehmen

Dieses Projekt liegt aktuell im Unterordner `ai-markdown/` des Repos `finaz-app`.
So machst du daraus dein eigenes, eigenständiges Repository:

1. Lege auf GitHub ein **leeres** Repo an, z. B. `ai-markdown` (ohne README/.gitignore).
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
kommuniziert nur mit dem eigenen Backend (`/api/assist`).

## Lizenz

[MIT](./LICENSE)
