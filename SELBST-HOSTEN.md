# Creator Hub – auf eigenem Server / PC betreiben (24/7)

Dein Plan: **Multi-Agent als eine KI, fest auf dem Server installiert, läuft immer.**
Hier die komplette Anleitung – vom einmaligen Start bis „läuft automatisch nach
jedem Neustart".

---

## 0. Voraussetzungen (einmalig)

- **Node.js 18+** → https://nodejs.org (LTS-Version)
- Ein kostenloser **Gemini-Key** → https://aistudio.google.com → *Get API key*
- Das Projekt liegt auf der Festplatte (z. B. `C:\creator-hub` oder `/opt/creator-hub`)

---

## 1. Schnellstart (zum Testen)

**Windows:** Doppelklick auf **`START-WINDOWS.bat`**
**Mac/Linux:** `bash start-linux-mac.sh`

Beim ersten Mal wird automatisch installiert, gebaut und eine `.env` erstellt.
Trage dort deinen Gemini-Key ein, dann erneut starten.
→ Browser öffnen: **http://localhost:3001**

---

## 2. Dauerhaft laufen lassen ("immer an")

Damit die KI nach jedem Neustart automatisch wieder startet:

### A) Linux-Server (systemd) – empfohlen

```bash
sudo nano /etc/systemd/system/creator-hub.service
```

```ini
[Unit]
Description=Creator Hub (KI Multi-Agent)
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/creator-hub
ExecStart=/usr/bin/npm run api
Restart=always
RestartSec=5
EnvironmentFile=/opt/creator-hub/.env

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable creator-hub     # startet bei jedem Boot
sudo systemctl start creator-hub      # jetzt starten
sudo systemctl status creator-hub     # Status prüfen
```

Logs ansehen: `journalctl -u creator-hub -f`

### B) Windows-PC (Aufgabenplanung)

1. **Aufgabenplanung** öffnen → *Aufgabe erstellen*
2. Trigger: *Beim Start des Computers*
3. Aktion: Programm `START-WINDOWS.bat` aus dem Projektordner
4. Häkchen: *Unabhängig von Benutzeranmeldung ausführen*

So startet die App automatisch, wenn der PC hochfährt.

### C) Alternative überall (PM2)

```bash
npm install -g pm2
pm2 start "npm run api" --name creator-hub
pm2 save
pm2 startup     # folge dem ausgegebenen Befehl -> Autostart
```

---

## 3. Für Besucher aus dem Internet erreichbar machen

Standardmäßig läuft alles nur lokal (`localhost`). Wenn andere drauf sollen:

| Schritt | Was |
|---|---|
| **Feste Adresse** | DynDNS einrichten (gratis: duckdns.org), da Heim-IP wechselt |
| **Port öffnen** | Im Router Portfreigabe für Port 3001 (oder 80/443) |
| **HTTPS** | Nginx als Reverse-Proxy + `certbot` (Let's Encrypt, gratis) |

### Nginx-Beispiel (Port 80 → 3001)

```nginx
server {
    listen 80;
    server_name deine-domain.de;
    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection keep-alive;
        proxy_set_header Host $host;
    }
}
```

```bash
sudo certbot --nginx -d deine-domain.de
```

---

## 4. Welcher Server lohnt sich?

| Lösung | Kosten | Immer an? | Für wen |
|---|---|---|---|
| **Eigener PC (localhost)** | 0 € | nur wenn PC läuft | Testen, privat |
| **Alter PC / Mini-PC / NAS als Server** | Strom | ✅ | Bastler, volle Kontrolle |
| **Raspberry Pi 4/5** | ~80 € einmalig | ✅ | sparsam, leise, 24/7 |
| **Hetzner VPS (CX22)** | ~3,50 €/Mo | ✅ | Vermarktung, stabil |
| **Render (Free)** | 0 € | schläft nach 15 Min | schnellster Start |

**Empfehlung für deinen Plan (immer an, eigene Festplatte):**
Ein **Mini-PC oder Raspberry Pi**, der durchläuft → einmalig einrichten mit
systemd (Schritt 2A) → läuft dauerhaft, ohne dass du etwas tun musst.

---

## 5. Update einspielen

```bash
cd /opt/creator-hub
git pull
npm ci
npm run build
sudo systemctl restart creator-hub   # oder: pm2 restart creator-hub
```

---

⚠ **Sicherheit:** Sobald der Server aus dem Internet erreichbar ist, halte das
System aktuell (`sudo apt update && sudo apt upgrade`) und gib den Gemini-Key
NIE im Code/öffentlich weiter – nur in der `.env`.
