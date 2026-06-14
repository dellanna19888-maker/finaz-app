# MeinKIProjekt – Content Creator für Social Media

Ein JSON-basiertes Multi-Agenten-System, das aus einem Thema ein fertiges
Social-Media-Skript erstellt. Zwei KI-Agenten arbeiten zusammen, ohne sich
direkt zu „sehen“ – die Kommunikation läuft über eine `status.json`.

## Die Agenten

| Agent | Rolle | Aufgabe |
|-------|-------|---------|
| **Agent A** | Kreativ-Agent | Analysiert Thema/Trend/Konkurrenz-Reel → Content-Konzept (Hook, Idee, Kernpunkte) |
| **Agent B** | Skript-Agent | Macht aus dem Konzept ein post-fertiges Skript (Voiceover, Caption, Hashtags) |

## Struktur

```
MeinKIProjekt/
├── agent_a_scripts/system_prompt_agent_a.txt   # System-Prompt Agent A
├── agent_b_scripts/system_prompt_agent_b.txt   # System-Prompt Agent B
├── config/profile.json                         # Dein Kanal-Profil (Stil, Stimme, Hashtags)
├── shared_memory/status.json                   # Kommunikations-Datei
├── shared_memory/final_script.txt              # Generiertes Endergebnis
└── main_controller.py                          # Der "Postbote" (Python)
```

## Kanal-Profil

In `config/profile.json` legst du **einmal** deinen Stil fest – Markenstimme,
Zielgruppe, Tonalität, No-Gos und Standard-Hashtags. Der Controller fügt dieses
Profil **automatisch** in jeden Agenten-Prompt ein, damit jeder Post konsistent
in deinem Stil klingt. Einfach die Felder anpassen – keine Code-Änderung nötig.

## Workflow

### Variante A – Auto-Modus (empfohlen, via Ollama)

Vollautomatisch: Thema rein → fertiges Skript raus. Kein Copy-Paste.

```bash
# Einmalig: Ollama installieren (https://ollama.com) und ein Modell laden
ollama pull llama3.1
ollama serve            # Server starten (falls nicht schon aktiv)

# Dann: kompletter Workflow in EINEM Befehl
python3 main_controller.py auto "3 KI-Tools, die deine Finanzen automatisieren"
```

Der Controller ruft Agent A und Agent B nacheinander automatisch auf,
reicht den Draft selbstständig weiter und speichert das Ergebnis in
`shared_memory/final_script.txt`.

**Konfiguration** (optional, per Umgebungsvariable):

```bash
OLLAMA_MODEL=mistral python3 main_controller.py auto "Mein Thema"
OLLAMA_URL=http://192.168.1.50:11434 python3 main_controller.py auto "Mein Thema"
```

### Variante B – Batch-Modus (mehrere Themen auf einmal)

Alle Themen aus `config/batch_topics.json` werden nacheinander verarbeitet.
Jedes Ergebnis landet als eigene Datei in `outputs/`.

```bash
# Themen in config/batch_topics.json eintragen, dann:
python3 main_controller.py batch

# Oder Themen direkt als Argumente übergeben:
python3 main_controller.py batch "ETF vs. KI-Portfolio" "3 KI-Tools für Finanzen"
```

Ausgabe-Struktur:

```
outputs/
├── 20260614_091500_01_3_KI-Tools_die_deine_Finanzen....txt
├── 20260614_091532_02_ETF_vs_KI-Portfolio_2026.txt
└── batch_log_20260614_091600.json    ← Protokoll (ok / fehler pro Thema)
```

### Variante C – Manueller Modus (Copy-Paste, z. B. mit Claude-App)

```bash
# 1. Workflow starten – zeigt den Prompt für Agent A
python3 main_controller.py start "3 KI-Tools, die deine Finanzen automatisieren"

# 2. Prompt in Claude einfügen → JSON-Antwort kopieren → einspeisen
python3 main_controller.py inject-a '{"agent_a": {"status": "done", "draft": "...", "error": ""}}'

# 3. Prompt für Agent B anzeigen (enthält automatisch den Draft von A)
python3 main_controller.py prompt-b

# 4. Antwort von Agent B einspeisen → final_script.txt wird erstellt
python3 main_controller.py inject-b '{"agent_b": {"status": "done", "final_output": "...", "error": ""}}'

# Status jederzeit prüfen
python3 main_controller.py status
```

## Warum dieser Aufbau

- **Offline-ready:** Die Steuer-Logik (Python) läuft lokal.
- **Modell-frei:** Funktioniert mit Claude (Copy-Paste) oder lokalen Modellen via Ollama.
- **Sauber getrennt:** Jeder Agent hat nur eine Aufgabe und gibt nur JSON aus → kein „Verstopfen“ des Systems.
