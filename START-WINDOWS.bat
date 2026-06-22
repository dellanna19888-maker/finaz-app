@echo off
REM ============================================================
REM  Creator Hub - Start fuer Windows (Doppelklick auf diese Datei)
REM  Startet die KI + Server. Im Browser dann: http://localhost:3001
REM ============================================================
title Creator Hub Server
cd /d "%~dp0"

echo.
echo  === Creator Hub wird gestartet ===
echo.

REM Node.js vorhanden?
where node >nul 2>nul
if errorlevel 1 (
  echo  [FEHLER] Node.js ist nicht installiert.
  echo  Bitte hier installieren: https://nodejs.org  (LTS-Version)
  echo  Danach diese Datei erneut doppelklicken.
  pause
  exit /b 1
)

REM Erststart: Pakete installieren + bauen
if not exist "node_modules" (
  echo  Erststart - installiere Pakete ^(dauert 1-2 Minuten^)...
  call npm ci
)
if not exist "dist" (
  echo  Baue die App...
  call npm run build
)

REM .env vorhanden? Sonst aus Vorlage erstellen + Hinweis
if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo.
  echo  [WICHTIG] Trage deinen kostenlosen Gemini-Key in die Datei .env ein:
  echo            GEMINI_API_KEY=AIza...
  echo  Key holen: https://aistudio.google.com  ^(Get API key^)
  echo  Danach diese Datei erneut starten.
  notepad .env
  pause
  exit /b 0
)

echo.
echo  Server laeuft. Oeffne im Browser:  http://localhost:3001
echo  ^(Dieses Fenster offen lassen. Zum Beenden: Fenster schliessen.^)
echo.
start "" http://localhost:3001
call npm run api
pause
