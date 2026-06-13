# Social-Media-Agenten-Team in TypeScript

Die TypeScript-Version des Social-Media-Content-Teams (4 Agenten + Web-Suche).

## ▶️ So startest du

```bash
cd typescript

# 1. Pakete installieren
npm install

# 2. API-Schlüssel hinterlegen
cp .env.example .env
#   .env öffnen und deinen Schlüssel eintragen (siehe ../README.md)

# 3. Starten – mit Nische und Plattform:
npm start -- "Fitness für Anfänger" "TikTok"

#   ... oder ohne Angaben (nutzt Standardwerte):
npm start
```

> Das `--` vor den Angaben sorgt dafür, dass npm den Text an das Programm
> weitergibt und nicht selbst auswertet.

Du siehst, wie die vier Agenten nacheinander arbeiten. Am Ende liegt der fertige,
regelgeprüfte Post in `output/social-media-post.md`.

## 🔑 Konzepte in `src/agents.ts`

- **`new Anthropic()`** – verbindet sich mit der Claude-API (liest den Schlüssel
  aus `ANTHROPIC_API_KEY`).
- **`frageAgent(...)`** – ruft einen einzelnen Agenten auf. Der `system`-Text
  legt die **Rolle** fest, die `messages` enthalten die **Aufgabe**. Optional
  bekommt der Agent **Werkzeuge** (die Web-Suche).
- **Die vier Agenten** – `trendUndRegelRechercheur`, `ideenAgent`,
  `contentAgent`, `complianceLektor`.
- **`main()`** – der **Orchestrator**: ruft die Agenten der Reihe nach auf.

## 🌐 Web-Suche an/aus

Oben im Code steht `const WEB_SUCHE_AKTIV = true;`. Damit sucht der Rechercheur
live nach den neuesten Regeln. Falls dein Konto die Web-Suche nicht unterstützt,
setze den Wert auf `false`.

## 🛠️ Verwendete Werkzeuge

- **`@anthropic-ai/sdk`** – die offizielle Claude-Bibliothek.
- **`tsx`** – führt TypeScript direkt aus (ohne vorher zu kompilieren).
- **`dotenv`** – liest den Schlüssel aus der `.env`-Datei.

## 🆚 Vergleich

Öffne `../python/agents.py` daneben – dort steht dasselbe Programm in Python.
Achte darauf, wie ähnlich die Struktur ist!
