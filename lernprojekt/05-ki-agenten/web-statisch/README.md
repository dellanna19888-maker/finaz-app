# 📤 Statische Webseite zum Weitergeben

Diese Variante ist **eine einzige Datei** (`index.html`) – ganz **ohne Server**.
Perfekt, um sie an eine andere Person weiterzugeben: Jede Person trägt einmal
ihren **eigenen** Anthropic-Schlüssel ein, und schon kann sie das Agenten-Team
benutzen.

## 🧠 Wichtig: Wie der Schlüssel funktioniert

- Jede Person braucht einen **eigenen** Anthropic API-Schlüssel
  (kostenlos erstellen unter https://console.anthropic.com).
- Der Schlüssel wird **nur im Browser** der Person gespeichert (localStorage)
  und **direkt** an Anthropic gesendet – an sonst niemanden, es gibt keinen
  Server dazwischen.
- Jede Person zahlt also **ihre eigene** Nutzung. Du zahlst nichts für andere.
- Über den Knopf **„Löschen"** kann der Schlüssel jederzeit wieder entfernt werden.

> ℹ️ Unterschied zur Variante im Ordner `../web/`: Dort läuft ein **Server** mit
> **deinem** Schlüssel (du zahlst für alle). Hier gibt es **keinen Server** und
> jede Person nutzt ihren **eigenen** Schlüssel.

## 📤 Drei Wege, sie weiterzugeben

### A) Einfach die Datei verschicken (am schnellsten)
Schick die Datei `index.html` per E-Mail, Chat oder USB-Stick. Die andere Person
macht einen **Doppelklick** darauf – sie öffnet sich im Browser.

> Falls ein Browser den direkten Aufruf von einer lokalen Datei blockiert,
> nutze einfach Weg B oder C (online stellen).

### B) Als echte Webseite mit Link (GitHub Pages, kostenlos)
1. Lege die Datei `index.html` in ein GitHub-Repository.
2. Im Repo: **Settings → Pages → Source: Branch wählen → Save**.
3. Nach kurzer Zeit bekommst du einen **öffentlichen Link**
   (z.B. `https://deinname.github.io/...`), den du an jeden weitergeben kannst.

### C) Drag &amp; Drop ins Netz (Netlify Drop, kostenlos)
1. Gehe auf **https://app.netlify.com/drop**.
2. Ziehe die Datei `index.html` (oder diesen Ordner) ins Browserfenster.
3. Du bekommst sofort einen **öffentlichen Link** zum Teilen.

## ▶️ So benutzt man die Seite

1. Oben den eigenen **API-Schlüssel** eintragen und auf **Speichern** klicken.
2. **Nische/Thema** eingeben und eine **Plattform** wählen.
3. Auf **„✨ Content erstellen"** klicken – die vier Agenten arbeiten nacheinander,
   die Ergebnisse erscheinen live.
4. Den fertigen Post mit **„📋 Kopieren"** übernehmen.

## 🔧 Anpassen (im `<script>`-Teil der Datei)

- **Modell/Geschwindigkeit:** `MODELL` auf `claude-haiku-4-5` ändern
  (günstiger + schneller).
- **Web-Suche:** lässt sich direkt auf der Seite per Häkchen an-/abschalten.

## 🆚 Vergleich

Die Agenten-Logik ist dieselbe wie in `../python/`, `../typescript/` und
`../web/`. Neu ist hier: alles steckt in **einer** Datei und läuft **ohne Server**
direkt im Browser.
