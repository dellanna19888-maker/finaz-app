@echo off
title KI-Plattform Laptop Demo

echo.
echo =============================================
echo    KI-Plattform -- Laptop Demo Start
echo =============================================
echo.

:: Backend starten
echo Installiere Backend (Python)...
cd backend-demo
pip install -r requirements.txt -q
echo Backend-Pakete installiert!

echo.
echo Starte Backend auf Port 8000...
start "KI-Backend" cmd /k "python -m uvicorn main:app --reload --port 8000"
timeout /t 3 /nobreak >nul

:: Frontend starten
cd ..\frontend
echo.
echo Installiere Frontend (Node.js)...
call npm install -q
echo.
echo Starte Frontend auf Port 5173...
start "KI-Frontend" cmd /k "npm run dev"

echo.
echo =============================================
echo   App laeuft unter: http://localhost:5173
echo   API-Docs:         http://localhost:8000/docs
echo =============================================
echo.
echo Beide Fenster offen lassen!
echo Zum Beenden: beide CMD-Fenster schliessen.
echo.
pause
