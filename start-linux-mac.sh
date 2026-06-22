#!/usr/bin/env bash
# ============================================================
#  Creator Hub - Start fuer Linux / Mac
#  Ausfuehren:  bash start-linux-mac.sh
#  Im Browser dann:  http://localhost:3001
# ============================================================
set -e
cd "$(dirname "$0")"

echo ""
echo " === Creator Hub wird gestartet ==="
echo ""

if ! command -v node >/dev/null 2>&1; then
  echo " [FEHLER] Node.js ist nicht installiert."
  echo " Installieren: https://nodejs.org  (LTS) oder per Paketmanager."
  exit 1
fi

# Erststart: Pakete + Build
if [ ! -d node_modules ]; then
  echo " Erststart - installiere Pakete (1-2 Min)..."
  npm ci
fi
if [ ! -d dist ]; then
  echo " Baue die App..."
  npm run build
fi

# .env vorhanden?
if [ ! -f .env ]; then
  cp .env.example .env
  echo ""
  echo " [WICHTIG] Trage deinen kostenlosen Gemini-Key in .env ein:"
  echo "           GEMINI_API_KEY=AIza..."
  echo " Key holen: https://aistudio.google.com  (Get API key)"
  echo " Danach dieses Skript erneut starten."
  exit 0
fi

echo ""
echo " Server laeuft. Oeffne im Browser:  http://localhost:3001"
echo " (Zum Beenden: Strg+C)"
echo ""
npm run api
