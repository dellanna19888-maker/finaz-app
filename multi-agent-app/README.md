# 🤖 Multi-Agent App

Eine **eigenständige** Multi-Agenten-KI-App auf Basis der **Claude API**. Ein
**Orchestrator** nimmt deine Aufgabe entgegen, zerlegt sie in Teilaufgaben und
delegiert diese an spezialisierte Agenten – anschließend fasst er alles zu einer
Endantwort zusammen.

> Dieses Projekt ist bewusst **unabhängig** und nutzt sein **eigenes**
> Anthropic-Konto bzw. einen eigenen API-Schlüssel (siehe `.env`).

## Architektur

```
              ┌──────────────┐
   Aufgabe →  │ Orchestrator │  plant & delegiert (Werkzeug: delegate_to_agent)
              └──────┬───────┘
          ┌──────────┼───────────┐
          ▼          ▼           ▼
     researcher   analyst      writer
     (Websuche)  (Code/Daten)  (Texte)
```

| Agent        | Aufgabe                                  | Werkzeuge             |
| ------------ | ---------------------------------------- | --------------------- |
| `researcher` | Aktuelle Informationen recherchieren     | Websuche, Seitenabruf |
| `analyst`    | Analysieren, rechnen, Daten verarbeiten  | Code-Ausführung       |
| `writer`     | Hochwertige Texte formulieren            | –                     |

Alle Agenten laufen auf dem Modell `claude-opus-4-8` mit adaptivem Thinking.

## Setup

Voraussetzung: **Node.js 18+**.

```bash
# 1. Abhängigkeiten installieren
npm install

# 2. Eigenen API-Schlüssel hinterlegen
cp .env.example .env
#    -> ANTHROPIC_API_KEY in .env eintragen
```

Einen API-Schlüssel erstellst du in der Anthropic Console:
<https://console.anthropic.com/>

## Nutzung

Interaktiv:

```bash
npm start
```

Einmal-Modus (Aufgabe direkt übergeben):

```bash
npm start "Vergleiche die Vor- und Nachteile von Zug und Flug für Berlin–München und empfiehl die beste Option."
```

Mit `exit` (oder `Strg+C`) beendest du den interaktiven Modus.

## Erweitern

Einen neuen Agenten hinzufügen: in `src/agents.ts` einen Eintrag zu `AGENTS`
ergänzen (Beschreibung, System-Prompt, Werkzeuge, Effort). Der Orchestrator
erkennt ihn automatisch über `agentRoster()`.

## Projektstruktur

```
src/
├── index.ts         CLI (interaktiv + Einmal-Modus)
├── orchestrator.ts  Orchestrator-Schleife + delegate_to_agent
├── agents.ts        Definition & Ausführung der Spezial-Agenten
├── client.ts        Anthropic-Client
├── config.ts        Modell & Limits
└── logger.ts        Konsolenausgabe
```

## Skripte

| Befehl              | Wirkung                    |
| ------------------- | -------------------------- |
| `npm start`         | App starten (via tsx)      |
| `npm run dev`       | Mit Auto-Reload starten    |
| `npm run typecheck` | Typprüfung ohne Ausführung |
| `npm run build`     | Nach `dist/` kompilieren   |

## Hinweise

- `@anthropic-ai/sdk` ist auf `latest` gesetzt. Für reproduzierbare Builds kannst
  du auf eine feste Version pinnen.
- Server-seitige Werkzeuge (Websuche, Code-Ausführung) können je nach Tarif
  zusätzliche Kosten verursachen.
- Der API-Schlüssel gehört in `.env` (wird per `.gitignore` nicht eingecheckt).
