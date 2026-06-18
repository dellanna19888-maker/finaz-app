#!/bin/bash
set -e

echo "🧠 KI-Plattform starten..."

if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "⚠️  backend/.env erstellt — bitte HUGGINGFACE_TOKEN eintragen!"
fi

echo ""
echo "Wähle Startmethode:"
echo "1) Lokal (Python + Node.js)"
echo "2) Docker Compose"
read -p "Eingabe (1/2): " choice

if [ "$choice" = "2" ]; then
    echo "🐳 Starte mit Docker..."
    docker compose up --build
else
    echo "🐍 Starte Python-Backend..."
    cd backend
    pip install -r requirements.txt -q
    uvicorn main:app --reload --port 8000 &
    BACKEND_PID=$!
    cd ..

    echo "⚡ Starte Vue-Frontend..."
    cd frontend
    npm install -q
    npm run dev &
    FRONTEND_PID=$!
    cd ..

    echo ""
    echo "✅ KI-Plattform läuft!"
    echo "   Frontend: http://localhost:5173"
    echo "   Backend:  http://localhost:8000"
    echo "   API-Docs: http://localhost:8000/docs"
    echo ""
    echo "Drücke CTRL+C zum Beenden."

    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
    wait
fi
