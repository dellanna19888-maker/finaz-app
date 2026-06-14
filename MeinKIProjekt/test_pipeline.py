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

MOCK_AGENT_D_APPROVED = json.dumps({
    "agent_d": {
        "status": "done",
        "decision": "APPROVED",
        "issues": [],
        "corrections": [],
        "required_disclaimer": "Keine Anlageberatung. Nur allgemeine Information.",
        "error": ""
    }
})

MOCK_AGENT_D_REJECTED = json.dumps({
    "agent_d": {
        "status": "done",
        "decision": "REJECTED",
        "issues": [
            "Satz enthält implizierte Renditegarantie.",
            "Kein Risikohinweis bei ETF-Erwähnung."
        ],
        "corrections": [
            "Ersetze garantierte Renditeaussage durch historische Durchschnittswerte.",
            "Füge nach ETF-Erwähnung hinzu: 'Wertpapiere können im Wert fallen.'"
        ],
        "required_disclaimer": "Keine Anlageberatung. Wertpapiere unterliegen Kursrisiken.",
        "error": ""
    }
})

MOCK_AGENT_C = json.dumps({
    "agent_c": {
        "status": "done",
        "thumbnail": (
            "A sleek dark background with glowing gold upward arrow, stock chart lines, "
            "'+2.3%' in large bold white text. Minimalist fintech aesthetic, sharp contrast. --ar 9:16 --style raw"
        ),
        "background": (
            "Abstract dark blue financial data visualization, floating numbers and graph lines, "
            "subtle gold glow, no text, cinematic depth of field, 4K quality. --ar 9:16"
        ),
        "text_overlay_style": (
            "Font: bold sans-serif (Inter/Helvetica). Colors: white text on dark (#0a0a0a) background, "
            "gold (#FFD700) for key numbers. Style: minimal, high contrast, no drop shadows."
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

_d_call_count = 0

def mock_call_ollama(prompt: str, model: str = "") -> str:
    """Gibt je nach Agenten-Kontext die passende Mock-Antwort zurück."""
    global _d_call_count
    if "SKRIPT VON AGENT B" in prompt:
        return MOCK_AGENT_C
    if "SKRIPT ZUR PRÜFUNG" in prompt:
        _d_call_count += 1
        return MOCK_AGENT_D_APPROVED
    if "DRAFT VON AGENT A" in prompt or "KORREKTUR-FEEDBACK" in prompt:
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
check("Workflow stage = agent_c_done", status["workflow_stage"] == "agent_c_done")
check("Agent A hat Draft",             bool(status["agent_a"]["draft"]))
check("Agent B hat final_output",      bool(status["agent_b"]["final_output"]))
check("HOOK im Draft",                 "HOOK" in status["agent_a"]["draft"])
check("SKRIPT im Output",              "SKRIPT" in status["agent_b"]["final_output"])
check("HASHTAGS im Output",            "HASHTAGS" in status["agent_b"]["final_output"])
check("FinazBrain im Output",          "FinazBrain" in status["agent_b"]["final_output"])
check("final_script.txt erstellt",     mc.OUTPUT_FILE.exists())
# Snapshot direkt nach Auto-Run sichern (Batch überschreibt status danach)
status_after_auto = mc.load_status()

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

# Erste Ausgabe-Datei inhaltlich prüfen (Skript + Thumbnails)
if output_files:
    content = output_files[0].read_text(encoding="utf-8")
    check("Header 'THEMA:' in Datei",        "THEMA:" in content)
    check("'SKRIPT' im Datei-Inhalt",         "SKRIPT" in content)
    check("'THUMBNAIL-PROMPTS' in Datei",     "THUMBNAIL-PROMPTS" in content)
    check("Midjourney-Prompt '--ar 9:16'",    "--ar 9:16" in content)

# Aufräumen
mc.BATCH_OUTPUT_DIR = original_dir
shutil.rmtree(test_output_dir, ignore_errors=True)

# --- Test 5: Agent D – Compliance-Check (APPROVED-Pfad) ---
print("\n[5] Agent D – Compliance-Check")
# status_after_auto wurde direkt nach Test 3 gespeichert
check("Agent D in status.json",             "agent_d" in status_after_auto)
check("Entscheidung = APPROVED",            status_after_auto.get("agent_d", {}).get("decision") == "APPROVED")
check("Keine Issues bei APPROVED",          status_after_auto.get("agent_d", {}).get("issues") == [])
check("Disclaimer vorhanden",               bool(status_after_auto.get("agent_d", {}).get("required_disclaimer")))
check("Agent D wurde im Auto-Run aufgerufen", _d_call_count >= 1)

# REJECTED→Retry-Flow testen
print("\n[5b] Agent D – Feedback-Loop (REJECTED → B korrigiert → APPROVED)")
_reject_count = 0
_orig_mock = mc.call_ollama

def mock_reject_once(prompt: str, model: str = "") -> str:
    """D lehnt beim ersten Mal ab, beim zweiten Mal approved."""
    global _reject_count
    if "SKRIPT ZUR PRÜFUNG" in prompt:
        _reject_count += 1
        if _reject_count == 1:
            return MOCK_AGENT_D_REJECTED
        return MOCK_AGENT_D_APPROVED
    if "SKRIPT VON AGENT B" in prompt:
        return MOCK_AGENT_C
    if "DRAFT VON AGENT A" in prompt or "KORREKTUR-FEEDBACK" in prompt:
        return MOCK_AGENT_B
    return MOCK_AGENT_A

mc.call_ollama = mock_reject_once
mc.reset_workflow("Retry-Test-Thema")
status = mc.load_status()
draft = "HOOK: Test\nIDEE: Test\nKERNPUNKTE: 1,2\nPLATTFORM: Instagram\nTONALITAET: seriös"
approved_retry, _ = mc.run_compliance_loop(draft, "llama3.1")
check("Retry-Loop: nach Korrektur APPROVED", approved_retry)
check("D wurde 2x aufgerufen (1x rejected, 1x approved)", _reject_count == 2, f"D-Aufrufe: {_reject_count}")
mc.call_ollama = _orig_mock  # Mock zurücksetzen

# --- Test 6: Agent C (Thumbnail-Prompts, Einzellauf) ---
print("\n[6] Agent C – Thumbnail-Prompt-Generator")
status = status_after_auto  # Snapshot vom vollständigen Auto-Run verwenden
check("Agent C in status.json",              "agent_c" in status)
check("Thumbnail nicht leer",                bool(status.get("agent_c", {}).get("thumbnail")))
check("'--ar 9:16' im Thumbnail-Prompt",     "--ar 9:16" in status.get("agent_c", {}).get("thumbnail", ""))
check("Hintergrund nicht leer",              bool(status.get("agent_c", {}).get("background")))
check("Text-Overlay-Stil nicht leer",        bool(status.get("agent_c", {}).get("text_overlay_style")))
check("thumbnail_prompts.txt erstellt",      mc.THUMBNAIL_FILE.exists())
if mc.THUMBNAIL_FILE.exists():
    tp_content = mc.THUMBNAIL_FILE.read_text(encoding="utf-8")
    check("'THUMBNAIL' im Prompt-File",      "THUMBNAIL" in tp_content)
    check("'Midjourney' im Prompt-File",     "Midjourney" in tp_content)

# --- Test 7: Dateiname-Generator ---
print("\n[7] Dateiname-Generator (_safe_filename)")
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
