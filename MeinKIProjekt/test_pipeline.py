#!/usr/bin/env python3
"""
Vollständiger Pipeline-Test ohne echtes Ollama.
Simuliert realistische Agenten-Antworten und prüft jeden Schritt.
"""
import json
import sys
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent

# ---------- Mock: call_ollama durch realistische Antworten ersetzen ----------
import main_controller as mc

MOCK_AGENT_A = json.dumps({
    "agent_a": {
        "status": "done",
        "draft": (
            "HOOK: 'Die meisten ETF-Anleger machen diesen einen Fehler – KI nicht.'\n"
            "IDEE: Vergleich klassischer ETF-Sparplan vs. KI-gesteuertes Rebalancing.\n"
            "KERNPUNKTE: 1) ETF-Sparplan läuft passiv, ohne Anpassung. "
            "2) KI-Portfolio erkennt Marktverschiebungen in Echtzeit. "
            "3) Rendite-Unterschied 2023-2025: +2,3% durch KI-Rebalancing. "
            "4) Kosten beider Ansätze im Vergleich. "
            "5) Für wen lohnt sich was?\n"
            "PLATTFORM: Instagram Reel (30 Sek)\n"
            "TONALITAET: seriös, faktenbasiert, direkt"
        ),
        "error": ""
    }
})

MOCK_AGENT_B = json.dumps({
    "agent_b": {
        "status": "done",
        "final_output": (
            "SKRIPT:\n"
            "[Szene 1 – Text auf schwarzem Hintergrund]\n"
            "Voiceover: 'Die meisten ETF-Anleger machen diesen einen Fehler – KI nicht.'\n\n"
            "[Szene 2 – Diagramm: ETF vs. KI-Kurve]\n"
            "Voiceover: 'Ein klassischer Sparplan läuft passiv. Keine Anpassung, egal was der Markt macht.'\n\n"
            "[Szene 3 – Highlight +2,3%]\n"
            "Voiceover: 'KI-gesteuerte Portfolios haben von 2023 bis 2025 im Schnitt 2,3% mehr Rendite erzielt – durch automatisches Rebalancing.'\n\n"
            "[Szene 4 – Kosten-Vergleich Tabelle]\n"
            "Voiceover: 'Der Haken: KI-Dienste kosten zwischen 0,2 und 0,8% pro Jahr. Rechne das gegen deinen Vorteil.'\n\n"
            "[Szene 5 – FinazBrain Logo]\n"
            "Voiceover: 'Speicher dir das, bevor du deinen nächsten Sparplan startest.'\n\n"
            "ON-SCREEN-TEXT:\n"
            "Szene 1: 'ETF vs. KI – wer gewinnt?'\n"
            "Szene 2: 'ETF-Sparplan = passiv'\n"
            "Szene 3: '+2,3% Rendite durch KI'\n"
            "Szene 4: 'Kosten: 0,2–0,8% p.a.'\n"
            "Szene 5: 'FinazBrain'\n\n"
            "CAPTION:\n"
            "ETF oder KI-Portfolio? Die Antwort hängt von deinem Zeithorizont und deiner Risikobereitschaft ab. "
            "Was du oben siehst, sind Durchschnittswerte – kein Versprechen.\n\n"
            "Speicher dir das für deine nächste Anlage-Entscheidung 📌\n\n"
            "HASHTAGS:\n"
            "#finanzen #etf #kiinvestieren #investieren #finanzbildung #geldanlegen "
            "#aitools #finanzwissen #finanzbrain #passiveseinkommen"
        ),
        "error": ""
    }
})

def mock_call_ollama(prompt: str, model: str = "") -> str:
    """Gibt je nach Agenten-Kontext die passende Mock-Antwort zurück."""
    # Agent B bekommt den Draft als Eingabe – eindeutiges Erkennungsmerkmal
    if "DRAFT VON AGENT A" in prompt:
        return MOCK_AGENT_B
    return MOCK_AGENT_A

# Ollama-Funktion ersetzen
mc.call_ollama = mock_call_ollama

# ---------- Hilfsfunktionen ----------
PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
errors = []

def check(label: str, condition: bool, detail: str = ""):
    if condition:
        print(f"  {PASS} {label}")
    else:
        print(f"  {FAIL} {label}" + (f" → {detail}" if detail else ""))
        errors.append(label)

# ---------- Tests ----------
print("\n" + "="*60)
print("  PIPELINE-TEST: FinazBrain Content Creator")
print("="*60)

# --- Test 1: Profil laden ---
print("\n[1] Profil laden")
profile_block = mc.load_profile_block()
check("profile.json vorhanden", bool(profile_block))
check("Kanal-Name 'FinazBrain' im Profil", "FinazBrain" in profile_block)
check("Tonalität im Profil", "seriös" in profile_block)

# --- Test 2: JSON-Extraktion ---
print("\n[2] JSON-Extraktion (extract_json)")
cases = [
    ("Sauberes JSON",       '{"a": 1}',                           '{"a": 1}'),
    ("Mit Text drumherum",  'Antwort: {"a": 1} Ende',             '{"a": 1}'),
    ("Markdown-Fence",      '```json\n{"a": 1}\n```',              '{"a": 1}'),
    ("Fence ohne 'json'",   '```\n{"a": 1}\n```',                  '{"a": 1}'),
]
for label, raw, expected in cases:
    result = mc.extract_json(raw)
    check(label, result == expected, f"erhalten: {repr(result)}")

# --- Test 3: Einzelner Auto-Workflow ---
print("\n[3] Auto-Workflow (einzelnes Thema)")
mc.OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
mc.run_auto("ETF vs. KI-Portfolio – was bringt 2026 mehr Rendite?")

status = mc.load_status()
check("Workflow stage = agent_b_done", status["workflow_stage"] == "agent_b_done")
check("Agent A hat Draft",             bool(status["agent_a"]["draft"]))
check("Agent B hat final_output",      bool(status["agent_b"]["final_output"]))
check("HOOK im Draft",                 "HOOK" in status["agent_a"]["draft"])
check("SKRIPT im Output",              "SKRIPT" in status["agent_b"]["final_output"])
check("HASHTAGS im Output",            "HASHTAGS" in status["agent_b"]["final_output"])
check("FinazBrain im Output",          "FinazBrain" in status["agent_b"]["final_output"])
check("final_script.txt erstellt",     mc.OUTPUT_FILE.exists())

# --- Test 4: Batch-Modus ---
print("\n[4] Batch-Modus (3 Themen)")
test_output_dir = BASE_DIR / "outputs_test"
original_dir = mc.BATCH_OUTPUT_DIR
mc.BATCH_OUTPUT_DIR = test_output_dir
test_output_dir.mkdir(parents=True, exist_ok=True)

batch_themen = [
    "3 KI-Tools, die deine Finanzen automatisch tracken",
    "So nutzt du ChatGPT für deine Steuererklärung",
    "Budgetplan erstellen in 60 Sekunden – mit KI",
]
mc.run_batch(batch_themen)

output_files = list(test_output_dir.glob("*.txt"))
log_files    = list(test_output_dir.glob("batch_log*.json"))
check("3 Output-Dateien erstellt",     len(output_files) == 3,
      f"gefunden: {len(output_files)}")
check("batch_log.json erstellt",       len(log_files) == 1)
if log_files:
    log = json.loads(log_files[0].read_text(encoding="utf-8"))
    ok_count = sum(1 for e in log if e["status"] == "ok")
    check("Alle 3 im Log als 'ok'",    ok_count == 3, f"ok: {ok_count}/3")

# Erste Ausgabe-Datei inhaltlich prüfen
if output_files:
    content = output_files[0].read_text(encoding="utf-8")
    check("Header 'THEMA:' in Datei",  "THEMA:" in content)
    check("'SKRIPT' im Datei-Inhalt",  "SKRIPT" in content)

# Aufräumen
mc.BATCH_OUTPUT_DIR = original_dir
shutil.rmtree(test_output_dir, ignore_errors=True)

# --- Test 5: Dateiname-Generator ---
print("\n[5] Dateiname-Generator (_safe_filename)")
check("Umlaute & Sonderzeichen",
      mc._safe_filename("Über KI & Geld?!") != "",
      mc._safe_filename("Über KI & Geld?!"))
check("Längen-Limit (50 Zeichen)",
      len(mc._safe_filename("A" * 100)) <= 50)

# --- Ergebnis ---
print("\n" + "="*60)
if errors:
    print(f"  ERGEBNIS: {len(errors)} Test(s) fehlgeschlagen:")
    for e in errors:
        print(f"    - {e}")
    sys.exit(1)
else:
    print(f"  ERGEBNIS: Alle Tests bestanden ✓")
print("="*60 + "\n")
