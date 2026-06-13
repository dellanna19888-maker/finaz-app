# Projekt 4: Backend mit Node.js

Bis jetzt lief alles nur im Browser. Dieses Projekt zeigt die **andere Hälfte**
einer echten Web-App: den **Server**. Er nimmt Anfragen entgegen, speichert die
Aufgaben zentral in einer Datei und stellt sie über eine **API** bereit.

## ▶️ So startest du

**Keine Installation nötig** – wir nutzen nur Node selbst:

```bash
cd 04-backend-node
node server.js
```

Im Terminal erscheint: `✅ Server läuft! Öffne im Browser: http://localhost:3000`

Öffne diese Adresse im Browser. Die App sieht aus wie Projekt 1 – aber die
Daten liegen jetzt auf dem Server (in `data/todos.json`), nicht im Browser.
Zum Stoppen drückst du im Terminal `Strg + C`.

## 🌐 Was ist eine API?

Eine **API** ist eine Schnittstelle: feste Adressen ("Routen"), über die ein
Programm Daten abfragen und ändern kann. Unser Server kennt diese Routen:

| Methode | Route | Bedeutung |
|---------|-------|-----------|
| `GET` | `/api/todos` | Alle Aufgaben holen |
| `POST` | `/api/todos` | Neue Aufgabe anlegen |
| `PATCH` | `/api/todos/:id` | Eine Aufgabe ändern (erledigt ja/nein) |
| `DELETE` | `/api/todos/:id` | Eine Aufgabe löschen |

Diese vier Methoden (GET, POST, PATCH/PUT, DELETE) sind der Standard für fast
alle Web-APIs der Welt.

## 🧪 Die API direkt ausprobieren

Während der Server läuft, kannst du die API auch ohne Browser testen – in einem
**zweiten** Terminal:

```bash
# Alle Aufgaben anzeigen
curl http://localhost:3000/api/todos

# Eine neue Aufgabe anlegen
curl -X POST http://localhost:3000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"text":"Node lernen"}'

# Nochmal abfragen – die neue Aufgabe ist jetzt dabei
curl http://localhost:3000/api/todos
```

## 🧩 Wie hängt alles zusammen?

```
  Browser (public/app.js)              Server (server.js)
  ───────────────────────              ──────────────────
        fetch("/api/todos")  ───────►  liest data/todos.json
        zeigt die Liste an   ◄───────  schickt JSON zurück
```

Das **Frontend** (im Ordner `public/`) ist für die Anzeige zuständig, das
**Backend** (`server.js`) für die Daten. Diese Trennung ist das Grundprinzip
fast jeder modernen Web-Anwendung – auch die große `finaz-app` eine Ebene höher
ist nach diesem Muster aufgebaut.

## 🔑 Konzepte in `server.js`

- **HTTP-Server** – `createServer(...)` lauscht auf Anfragen.
- **Routing** – je nach Adresse (`pfad`) und Methode (`GET`/`POST`/...) passiert
  etwas anderes.
- **Dateien lesen/schreiben** – mit `node:fs` speichern wir die Aufgaben dauerhaft.
- **Statische Dateien ausliefern** – derselbe Server schickt auch das Frontend.

## 💪 Übung & nächster Schritt

- Füge eine Route hinzu, die nur die **erledigten** Aufgaben zurückgibt.
- Lerne als Nächstes das Framework **Express**, das vieles davon kürzer macht:
  `npm install express`. Dann werden aus den `if`-Blöcken kurze Zeilen wie
  `app.get("/api/todos", ...)`.
