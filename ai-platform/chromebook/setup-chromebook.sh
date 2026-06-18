#!/bin/bash
set -e
clear
echo "╔══════════════════════════════════════════════╗"
echo "║  🧠 KI-Plattform — Chromebook Setup         ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── 1. System-Pakete ─────────────────────────────────────────────────────────
echo "📦 System aktualisieren..."
sudo apt update -qq
sudo apt install -y python3 python3-pip python3-venv git curl -qq
echo "✅ System bereit (Python $(python3 --version))"

# ── 2. Virtuelle Umgebung ────────────────────────────────────────────────────
VENV_DIR="$HOME/.ki-plattform-venv"
if [ ! -d "$VENV_DIR" ]; then
    echo ""
    echo "🐍 Erstelle Python-Umgebung..."
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

# ── 3. Python-Pakete ─────────────────────────────────────────────────────────
echo ""
echo "📦 Installiere Pakete (nur 7 kleine Pakete, ~30 MB)..."
pip install -q -r requirements.txt
echo "✅ Pakete installiert"

# ── 4. HF Token ──────────────────────────────────────────────────────────────
echo ""
if [ ! -f .env ]; then
    cp .env.example .env
fi
HF_TOKEN=$(grep "^HUGGINGFACE_TOKEN=" .env | cut -d= -f2-)
if [ -z "$HF_TOKEN" ] || [ "$HF_TOKEN" = "hf_deinTokenHier" ]; then
    echo "🔑 Hugging Face Token benötigt"
    echo "   → Kostenlos erstellen: https://huggingface.co/settings/tokens"
    echo ""
    read -p "   Token eingeben (hf_...): " TOKEN
    if [ -n "$TOKEN" ]; then
        sed -i "s|HUGGINGFACE_TOKEN=.*|HUGGINGFACE_TOKEN=$TOKEN|" .env
        echo "✅ Token gespeichert"
    else
        echo "⚠️  Kein Token — du kannst ihn später in .env eintragen"
    fi
fi

# ── 5. Autostart-Alias ───────────────────────────────────────────────────────
ALIAS_LINE='alias ki-plattform="cd '"$PWD"' && source '"$VENV_DIR"'/bin/activate && python server.py"'
if ! grep -q "alias ki-plattform" ~/.bashrc 2>/dev/null; then
    echo "" >> ~/.bashrc
    echo "# KI-Plattform" >> ~/.bashrc
    echo "$ALIAS_LINE" >> ~/.bashrc
    echo "✅ Alias 'ki-plattform' in ~/.bashrc gespeichert"
fi

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  ✅ Setup abgeschlossen!                    ║"
echo "╠══════════════════════════════════════════════╣"
echo "║                                              ║"
echo "║  Starten:                                    ║"
echo "║    python server.py                          ║"
echo "║                                              ║"
echo "║  Oder nach Terminal-Neustart:                ║"
echo "║    ki-plattform                              ║"
echo "║                                              ║"
echo "║  Browser: http://localhost:7860              ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Direkt starten?
read -p "Jetzt sofort starten? (j/n): " START
if [ "$START" = "j" ] || [ "$START" = "J" ]; then
    echo ""
    echo "🚀 Starte Server..."
    python server.py
fi
