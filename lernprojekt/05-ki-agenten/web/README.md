# 🌐 Web-Version: Social-Media-Content-Team

Dieselbe Idee wie die Kommandozeilen-Versionen – aber als **Webseite**! Du gibst
Nische und Plattform ein und schaust **live zu**, wie die vier Agenten arbeiten.

## 🧠 Wie ist das aufgebaut?

Ein API-Schlüssel darf **niemals** in den Browser gelangen. Deshalb gibt es zwei Teile:

```
   Browser (Frontend)                 Server (Backend)
   public/index.html  ── Anfrage ──▶  server.ts
   public/app.js      ◀─ Ergebnisse ─  (hält den Schlüssel geheim,
   public/style.css      (live)         ruft die 4 Agenten auf)
```

- **`server.ts`** – kleiner Node-Server (Express). Hält den Schlüssel, ruft die
  Agenten auf und schickt jede Stufe **live** an den Browser
  (per „Server-Sent Events").
- **`public/`** – die Webseite: `index.html` (Aufbau), `style.css` (Aussehen),
  `app.js` (Logik im Browser).

## ▶️ So startest du

```bash
cd web

# 1. Pakete installieren
npm install

# 2. API-Schlüssel hinterlegen
cp .env.example .env
#   .env öffnen und deinen Schlüssel eintragen (siehe ../README.md)

# 3. Server starten
npm start

# 4. Im Browser öffnen:
#    http://localhost:3000
```

Gib eine Nische ein, wähle eine Plattform und klick auf **„Content erstellen"**.
Die vier Karten füllen sich nacheinander – am Ende steht dein fertiger,
regelgeprüfter Post.

> 💡 Die Seite lädt auch **ohne** Schlüssel (zum Anschauen). Für das Generieren
> brauchst du aber einen `ANTHROPIC_API_KEY`.

## 🔧 Anpassen

- **Modell/Geschwindigkeit:** Oben in `server.ts` `MODELL` auf
  `claude-haiku-4-5` ändern (günstiger + schneller).
- **Web-Suche:** `WEB_SUCHE_AKTIV = false` schaltet die Live-Suche ab.
- **Port:** über `PORT` in der `.env` ändern (Standard: 3000).

## 🆚 Vergleich

Die reine Logik der Agenten ist dieselbe wie in `../python/agents.py` und
`../typescript/src/agents.ts`. Neu ist hier nur die Verpackung als Webseite mit
Server und Browser-Oberfläche.
