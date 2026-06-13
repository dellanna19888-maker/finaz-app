# Social-Media-Agenten-Team in Python

Die Python-Version des Social-Media-Content-Teams (4 Agenten + Web-Suche).

## ▶️ So startest du

```bash
cd python

# 1. Pakete installieren (am besten in einer virtuellen Umgebung)
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. API-Schlüssel hinterlegen
cp .env.example .env
#   .env öffnen und deinen Schlüssel eintragen (siehe ../README.md)

# 3. Starten – mit Nische und Plattform:
python agents.py "Fitness für Anfänger" "TikTok"

#   ... oder ohne Angaben (nutzt Standardwerte):
python agents.py
```

Du siehst, wie die vier Agenten nacheinander arbeiten. Am Ende liegt der fertige,
regelgeprüfte Post in `output/social-media-post.md`.

## 🔑 Konzepte in `agents.py`

- **`client = Anthropic()`** – verbindet sich mit der Claude-API (liest den
  Schlüssel aus `ANTHROPIC_API_KEY`).
- **`frage_agent(...)`** – ruft einen einzelnen Agenten auf. Der `system`-Text
  legt die **Rolle** fest, die `messages` enthalten die **Aufgabe**. Optional
  bekommt der Agent **Werkzeuge** (die Web-Suche).
- **Die vier Agenten** – `trend_und_regel_rechercheur`, `ideen_agent`,
  `content_agent`, `compliance_lektor`.
- **`main()`** – der **Orchestrator**: ruft die Agenten der Reihe nach auf.

## 🌐 Web-Suche an/aus

Oben im Code steht `WEB_SUCHE_AKTIV = True`. Damit sucht der Rechercheur live
nach den neuesten Regeln. Falls dein Konto die Web-Suche nicht unterstützt,
setze den Wert auf `False`.

## 🆚 Vergleich

Öffne `../typescript/src/agents.ts` daneben – dort steht dasselbe Programm in
TypeScript. Achte darauf, wie ähnlich die Struktur ist!
