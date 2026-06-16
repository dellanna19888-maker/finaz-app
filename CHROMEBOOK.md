# FinazApp auf dem Chromebook selbst hosten (eigener Server)

Diese Anleitung zeigt, wie du den **eigenen Server** der FinazApp (Frontend +
API/Compliance-Backend) direkt auf deinem **Chromebook** betreibst – über die
**Linux-Entwicklungsumgebung (Crostini)** von ChromeOS. Für die Nutzung *auf dem
Chromebook selbst* brauchst du kein Cloud-Hosting.

> Voraussetzung: ein Chromebook, das die Linux-Umgebung unterstützt (die meisten
> Geräte ab ca. 2019). Auf verwalteten Schul-/Firmen-Geräten ist Linux teils
> gesperrt.

---

## 1. Linux-Umgebung aktivieren

**Einstellungen → Erweitert → Entwickler → „Linux-Entwicklungsumgebung" →
Aktivieren.**

ChromeOS lädt einmalig einen kleinen Debian-Container herunter (einige Minuten).
Danach gibt es die App **„Terminal"**. Alle folgenden Befehle laufen in diesem
Terminal.

## 2. Node.js installieren

Empfohlen über **nvm** (braucht kein root, liefert eine aktuelle Version):

```bash
sudo apt update && sudo apt install -y curl git
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
# Terminal neu öffnen ODER:
source ~/.bashrc
nvm install 22
node -v   # sollte v22.x zeigen
```

> Alternativ Debians eigenes Paket (`sudo apt install -y nodejs npm`) – das ist
> aber oft zu alt. Die App braucht **Node ≥ 18**, empfohlen 20/22.

## 3. Projekt holen und Abhängigkeiten installieren

```bash
git clone https://github.com/dellanna19888-maker/finaz-app.git
cd finaz-app
git checkout claude/dreamy-archimedes-hs8ofa   # aktueller Branch (oder Default nach PR-Merge)
npm install
```

## 4. API-Key festlegen (für KI-Funktionen)

Zwei Wege:

- **Bring Your Own Key (ohne Datei):** nichts einrichten – den Key später im
  Browser unter **⚙️ Einstellungen** eintragen. Er bleibt nur im Browser.
- **Server-Key (.env):**
  ```bash
  cp .env.example .env
  nano .env      # ANTHROPIC_API_KEY=sk-ant-... eintragen, speichern (Strg+O, Enter, Strg+X)
  ```

Ohne Key laufen Finanz-App und Compliance-Seite vollständig; nur Zentrale/KI-
Assistent/Notizen brauchen einen Key.

## 5. Server starten

**Eine URL, ein Befehl** (baut das Frontend und startet API + Auslieferung auf
Port 3001):

```bash
npm run demo
```

Dann im **Chrome-Browser des Chromebooks** öffnen:

```
http://localhost:3001
```

ChromeOS leitet `localhost` automatisch in den Linux-Container weiter.

> Entwicklungsmodus mit Auto-Reload (Frontend und Backend getrennt):
> `npm run dev:all` → Frontend unter **http://localhost:5173**, API unter 3001.

## 6. Im Hintergrund / dauerhaft laufen lassen (optional)

- **Einfach:** den Terminal-Tab offen lassen.
- **Hintergrund:**
  ```bash
  nohup npm run demo > finaz.log 2>&1 &
  ```
- **Robust (Prozessmanager):**
  ```bash
  npm i -g pm2
  pm2 start "npm run demo" --name finaz
  pm2 save
  ```

> Hinweis: Ein echter Autostart beim Hochfahren ist unter Crostini begrenzt, weil
> der Linux-Container erst beim Öffnen des Terminals startet. Nach einem Neustart
> also das Terminal (bzw. die App) einmal öffnen.

## 7. Zugriff von anderen Geräten (z. B. Handy im selben WLAN)

Crostini läuft in einem Container hinter NAT – der `localhost` des Chromebooks ist
von außen **nicht direkt** erreichbar. Optionen:

- **Tunnel (am einfachsten):** ein Tool wie `cloudflared` oder `ngrok` im Linux-
  Terminal starten und auf Port 3001 zeigen → du bekommst eine öffentliche URL.
- **Echtes Hosting:** lieber Render/Docker nehmen – siehe [`DEPLOY.md`](./DEPLOY.md).

## Sicherheit

- Der API-Key bleibt serverseitig (`.env`) bzw. im Browser (BYOK) – **nie** ins
  Repository committen (`.env` ist in `.gitignore`).
- Audit-Logs der Compliance-Entscheidungen liegen unter `server/logs/`.

## Häufige Probleme

- **`node: command not found`** nach nvm-Installation → Terminal neu öffnen oder
  `source ~/.bashrc`.
- **Port 3001 belegt** → mit anderem Port starten: `API_PORT=3010 npm run demo`
  und dann `http://localhost:3010` öffnen.
- **`npm install` schlägt fehl** → Node-Version prüfen (`node -v`, ≥ 18) und
  `sudo apt install -y build-essential` nachinstallieren.
