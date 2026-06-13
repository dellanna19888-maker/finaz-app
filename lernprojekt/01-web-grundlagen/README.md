# Projekt 1: Web-Grundlagen (HTML · CSS · JavaScript)

Das Fundament des gesamten Webs. **Jedes** Framework (auch Vue und React)
baut am Ende auf diesen drei Bausteinen auf. Wenn du verstehst, was hier
passiert, verstehst du den Rest viel schneller.

## ▶️ So startest du

**Du brauchst nichts zu installieren!** Öffne einfach die Datei `index.html`
in deinem Browser:

- Doppelklick auf `index.html`, **oder**
- Rechtsklick → „Öffnen mit" → dein Browser

Das war's. Die App läuft. 🎉

## 🧩 Die drei Dateien

| Datei | Aufgabe | Vergleich |
|-------|---------|-----------|
| `index.html` | Die **Struktur**: Welche Elemente gibt es? | Das Skelett |
| `style.css` | Das **Aussehen**: Farben, Abstände, Schrift | Die Kleidung |
| `app.js` | Die **Logik**: Was passiert bei Klicks? | Das Gehirn |

## 🔑 Diese Konzepte lernst du hier

- **DOM** – So nennt man die Struktur der Seite, wie der Browser sie sieht.
  Mit `document.querySelector(...)` greifen wir auf einzelne Elemente zu.
- **Events** – Reaktionen auf Aktionen, z.B. `addEventListener("click", ...)`,
  wenn der Nutzer etwas anklickt.
- **State (Zustand)** – Unsere Daten leben im Array `todos`. Ändern sich die
  Daten, müssen wir die Anzeige **selbst** neu aufbauen (`zeichneListe()`).
- **localStorage** – Ein kleiner Speicher im Browser, damit die Aufgaben nach
  dem Neuladen erhalten bleiben.

## 💪 Übungen zum Ausprobieren

1. Ändere in `style.css` die Hintergrundfarbe (suche nach `linear-gradient`).
2. Ändere den Platzhalter-Text im Eingabefeld in `index.html`.
3. **Etwas kniffliger:** Füge einen Button „Alle erledigten löschen" hinzu.

## 👉 Der Knackpunkt

Achte in `app.js` auf die Funktion `zeichneListe()`. Bei **jeder** Änderung
müssen wir die komplette Liste von Hand neu bauen. Das ist mühsam und
fehleranfällig. Genau dieses Problem lösen Frameworks wie Vue und React –
schau dir als Nächstes Projekt 2 an!
