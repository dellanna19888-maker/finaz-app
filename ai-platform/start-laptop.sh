#!/bin/bash
set -e

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   🧠 KI-Plattform — Laptop Demo Start   ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── 1. HF Token prüfen ──────────────────────────────────────────────────────
ENV_FILE="backend-demo/.env"
if [ ! -f "$ENV_FILE" ]; then
    cp backend-demo/.env.example "$ENV_FILE"
fi

HF_TOKEN=$(grep "^HUGGINGFACE_TOKEN=" "$ENV_FILE" | cut -d= -f2)
if [ -z "$HF_TOKEN" ] || [ "$HF_TOKEN" = "hf_deinTokenHier" ]; then
    echo "⚠️  Kein Hugging Face Token gefunden!"
    echo ""
    echo "Bitte:"
    echo "  1. Gehe auf https://huggingface.co/settings/tokens"
    echo "  2. Erstelle ein kostenloses Token"
    echo "  3. Trage es ein in: ai-platform/backend-demo/.env"
    echo "     HUGGINGFACE_TOKEN=hf_dein_token_hier"
    echo ""
    read -p "Token jetzt eingeben (oder Enter zum Überspringen): " token
    if [ -n "$token" ]; then
        sed -i "s|HUGGINGFACE_TOKEN=.*|HUGGINGFACE_TOKEN=$token|" "$ENV_FILE"
        echo "✅ Token gespeichert"
    fi
fi

# ── 2. Python prüfen ────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
    echo "❌ Python nicht gefunden!"
    echo "   → https://python.org/downloads"
    exit 1
fi
PY=$(command -v python3 || command -v python)
echo "✅ Python: $($PY --version)"

# ── 3. Node prüfen ──────────────────────────────────────────────────────────
if ! command -v node &>/dev/null; then
    echo "❌ Node.js nicht gefunden!"
    echo "   → https://nodejs.org"
    exit 1
fi
echo "✅ Node.js: $(node --version)"

echo ""
echo "📦 Installiere Backend-Abhängigkeiten (nur 8 kleine Pakete)..."
cd backend-demo
$PY -m pip install -r requirements.txt -q
echo "✅ Backend bereit"

echo ""
echo "🚀 Starte Backend auf Port 8000..."
$PY -m uvicorn main:app --reload --port 8000 &
BACK_PID=$!
sleep 2

cd ../frontend
echo ""
echo "📦 Installiere Frontend-Abhängigkeiten..."
npm install -q
echo "✅ Frontend bereit"

echo ""
echo "⚡ Starte Frontend auf Port 5173..."
npm run dev &
FRONT_PID=$!

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  ✅ KI-Plattform läuft!                 ║"
echo "║                                          ║"
echo "║  🌐 App:      http://localhost:5173      ║"
echo "║  📖 API-Docs: http://localhost:8000/docs ║"
echo "║                                          ║"
echo "║  Drücke CTRL+C zum Beenden              ║"
echo "╚══════════════════════════════════════════╝"
echo ""

trap "echo ''; echo 'Beende...'; kill $BACK_PID $FRONT_PID 2>/dev/null" EXIT INT
wait
