# 🤖 Projekt 5: Multi-KI-Agenten – Social-Media-Content-Team

Das fortgeschrittenste Projekt! Hier baust du ein **Team aus mehreren KI-Agenten**,
das **Social-Media-Content** (Instagram, TikTok & Co.) erstellt – mit **frischen
Ideen** und auf Basis der **neuesten Plattform-Regeln und Gesetze**. Gesteuert
wird alles über die **Claude-API**.

## 💡 Was ist ein Multi-Agenten-System?

Statt *einer* KI, die alles auf einmal macht, teilst du die Arbeit auf mehrere
**spezialisierte Agenten** auf. Jeder Agent hat eine eigene **Rolle** (über einen
eigenen „System-Prompt"). Ein **Orchestrator** (dein Programm) ruft sie in der
richtigen Reihenfolge auf und reicht die Ergebnisse weiter – wie ein echtes
Social-Media-Team:

```
  Nische + Plattform (z.B. "Fitness", "TikTok")
        │
        ▼
┌────────────────────────┐
│ 🔎 Trend- & Regel-      │  nutzt 🌐 Web-Suche für die NEUESTEN
│    Rechercheur          │  Trends, Richtlinien und Gesetze
└───────────┬────────────┘
            │ Briefing (Trends + Regeln)
            ▼
┌────────────────────────┐
│ 💡 Ideen-Agent          │  entwickelt frische Content-Ideen
└───────────┬────────────┘
            │ Ideen-Liste
            ▼
┌────────────────────────┐
│ ✍️  Content-Agent        │  schreibt Hook + Skript/Caption + Hashtags
└───────────┬────────────┘
            │ Roh-Post
            ▼
┌────────────────────────┐
│ ✅ Compliance-Lektor    │  verbessert UND prüft auf Regelkonformität
└───────────┬────────────┘
            ▼
      📄 output/social-media-post.md
```

Jeder Agent ist ein eigener Aufruf an Claude mit einem eigenen System-Prompt.
Diese Aufteilung in Rollen macht es zu einem *Multi-Agenten*-System.

## 🌐 Immer aktuell: die Web-Suche

Plattform-Regeln und Gesetze ändern sich ständig. Damit dein Team **nicht
veraltet**, hat der erste Agent ein **Web-Such-Werkzeug**: Er sucht live nach den
neuesten Community-Richtlinien (TikTok, Instagram …) und rechtlichen Vorgaben
(z.B. Werbekennzeichnung) und gibt sie als Briefing an die anderen weiter.

> Die Web-Suche ist ein serverseitiges Werkzeug von Anthropic und kostet ein
> wenig extra. Im Code kannst du sie mit `WEB_SUCHE_AKTIV = False/false`
> abschalten – dann nutzt der Agent nur sein vorhandenes Wissen.

## 📂 Drei Varianten zum Vergleichen

Dasselbe Agenten-Team in drei Verpackungen:

| Ordner | Variante | Start |
|--------|----------|-------|
| `python/` | Kommandozeile (Python) | `python agents.py "Fitness" "TikTok"` |
| `typescript/` | Kommandozeile (TypeScript) | `npm start -- "Fitness" "TikTok"` |
| `web/` | 🌐 **Webseite** (Server + Browser) | `npm start` → http://localhost:3000 |

Alle drei nutzen **dieselbe Agenten-Logik** – schau sie dir nebeneinander an!
Die Web-Version (`web/`) zeigt die Agenten **live im Browser** und ist ideal,
wenn du das System ohne Terminal benutzen möchtest.

---

## 🔑 Schritt 1: Einen Anthropic API-Schlüssel besorgen

Das Agenten-System spricht mit Claude über die **Anthropic-API**. Dafür brauchst
du einen Schlüssel (das ist wie ein Passwort für die API).

1. Gehe auf **https://console.anthropic.com** und melde dich an (oder registriere
   dich kostenlos).
2. Öffne **Settings → API Keys** (Einstellungen → API-Schlüssel).
3. Klicke auf **Create Key**, gib ihm einen Namen und kopiere den Schlüssel.
   Er beginnt mit `sk-ant-...`.
4. **Wichtig:** Bewahre ihn sicher auf und teile ihn mit niemandem!
5. Die API ist **kostenpflichtig** (nach Verbrauch abgerechnet). Lege in der
   Console unter **Billing** ein Guthaben an. Pro Durchlauf entstehen nur geringe
   Kosten (wenige Cent; die Web-Suche kommt leicht obendrauf).

> 💡 **Tipp zum Sparen:** Zum Experimentieren kannst du im Code das Modell von
> `claude-opus-4-8` auf das günstigere und schnellere `claude-haiku-4-5` ändern
> (eine einzige Zeile – siehe Kommentar im Code).

## 🔒 Schritt 2: Den Schlüssel sicher hinterlegen

In **beiden** Projektordnern liegt eine Datei `.env.example`. So gehst du vor:

1. Kopiere `.env.example` zu `.env`
2. Trage deinen Schlüssel ein: `ANTHROPIC_API_KEY=sk-ant-...`

Die Datei `.env` ist absichtlich in `.gitignore` eingetragen – so wird dein
Schlüssel **niemals** versehentlich mit hochgeladen. ⚠️ Trage deinen echten
Schlüssel nie direkt in den Code ein!

## ▶️ Schritt 3: Loslegen

Folge der `README.md` im jeweiligen Ordner (`python/` oder `typescript/`). Du
kannst Nische und Plattform frei wählen:

```bash
# Python
python agents.py "Nachhaltige Mode" "Instagram"

# TypeScript
npm start -- "Reise-Tipps" "TikTok"
```

---

## 🎓 Was du hier lernst

- **System-Prompts** geben einem Agenten seine Rolle.
- **Orchestrierung**: mehrere KI-Aufrufe zu einem sinnvollen Ablauf verketten.
- **Werkzeuge (Tool Use)**: ein Agent nutzt die **Web-Suche** für aktuelle Infos.
- **Die Claude-API** aufrufen und die Antwort verarbeiten.
- **Geheimnisse schützen**: API-Schlüssel über `.env` statt im Code.

## 🚀 Ideen zum Weitermachen

- Füge einen **Hashtag-Agenten** oder einen **Bild-Ideen-Agenten** hinzu.
- Lass den Content-Agenten **mehrere Posts** auf einmal erstellen (eine ganze
  Wochen-Planung).
- Baue einen **Koordinator-Agenten**, der selbst entscheidet, welcher Spezialist
  als Nächstes dran ist.
- Speichere die Ergebnisse pro Plattform in eigene Dateien.
