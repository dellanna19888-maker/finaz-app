#!/usr/bin/env python3
"""
master.py – Master-Controller für das lokale Multi-Agenten-System.

Läuft auf Android (Termux → Ubuntu proot) mit lokalem Ollama.
Workflow: Dan generiert Content → deterministischer CODE-CHECK →
          bei BLOCKIERT sofort STOPP, sonst Gatekeeper + Editor → Speichern.

Nutzung:
  python3 master.py                          # interaktiv
  python3 master.py "Thema"                  # direkt
  python3 master.py "Thema" -m qwen2.5:3b    # anderes Modell
  python3 master.py "Thema" -t 0.3           # Temperatur anpassen
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import requests

# ──────────────────────────────────────────────
# Konfiguration
# ──────────────────────────────────────────────
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:3b"
DEFAULT_TEMP_DAN = 0.8       # kreativ
DEFAULT_TEMP_GATE = 0.2      # streng

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ──────────────────────────────────────────────
# System-Prompts
# ──────────────────────────────────────────────
SYSTEM_DAN = """Du bist Dan, Content-Manager für einen Faceless-Business-Kanal (SilentScale).
Stil: dark, moody, premium – kein Smalltalk, kein Emoji-Spam.
Erstelle zu jedem Thema:
  HOOK: eine provokante Einstiegsfrage oder These (1 Satz)
  SKRIPT: 3–5 Sätze für ein 30-Sek-Reel
  CAPTION: 2–3 Sätze + Call-to-Action
  HASHTAGS: 5 relevante Hashtags, davon IMMER #Werbung oder #Anzeige
Gib KEINE Gewinnversprechen, keine konkreten Eurobeträge, keine Renditeversprechen.
Kein "garantiert", kein "risikofrei", kein "100% sicher"."""

SYSTEM_GATEKEEPER = """Du bist ein strenger Compliance-Gatekeeper für Finanz-Content (Deutschland/EU).
Prüfe den Text auf:
1. Verstöße gegen §34f GewO (Finanzberatung ohne Lizenz)
2. Irreführende Versprechen nach UWG (Gewinnversprechen, Renditegarantien)
3. DSGVO-Relevanz (persönliche Daten, Tracking)
4. Fehlende Werbe-Kennzeichnung
Antworte mit: URTEIL: FREIGABE | KORREKTUR | BLOCKIERT
Dann: BEGRÜNDUNG (max. 3 Sätze).
Dann: EMPFEHLUNG was zu ändern ist (oder "Keine Änderung nötig")."""

SYSTEM_EDITOR = """Du bist ein präziser Content-Editor.
Du erhältst einen Text und das Urteil des Gatekeepers.
Wenn KORREKTUR nötig: Schreibe den HOOK und die CAPTION neu – compliant, aber trotzdem wirkungsvoll.
Wenn BLOCKIERT: Schreibe "NICHT FREIGEGEBEN – manuelle Prüfung erforderlich."
Wenn FREIGABE: Schreibe "FREIGEGEBEN – keine Korrektur nötig." """

# ──────────────────────────────────────────────
# Ollama-Aufruf
# ──────────────────────────────────────────────
def ask_ollama(system: str, prompt: str, model: str, temp: float) -> str:
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temp},
    }
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=180)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        print("\n[FEHLER] Keine Verbindung zu Ollama. Läuft 'ollama serve'?")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("\n[FEHLER] Ollama hat nicht rechtzeitig geantwortet (Timeout 180s).")
        sys.exit(1)

# ──────────────────────────────────────────────
# Deterministischer Compliance-Check
# ──────────────────────────────────────────────
def code_check(content_text: str) -> tuple[str, str]:
    """
    Gibt (urteil, report) zurück.
    urteil: 'OK' | 'REVIEW' | 'BLOCKIERT'
    Importiert compliance_rules wenn vorhanden, sonst Minimal-Check.
    """
    try:
        from compliance_rules import check as cr_check
        # Verpacke den Rohtext als Pseudo-Content-Dict
        result = cr_check({
            "hook": content_text,
            "script": "",
            "caption": content_text,
            "hashtags": content_text.split(),
        })
        return result["status"], result["report"]
    except ImportError:
        pass

    # Minimal-Fallback ohne compliance_rules.py
    HARD_BLOCK = [
        "garantiert", "risikofrei", "risikolos", "100% sicher",
        "reich werden", "schnell reich", "ohne risiko",
    ]
    found = [w for w in HARD_BLOCK if w in content_text.lower()]
    has_ad = any(label in content_text.lower() for label in ["#werbung", "#anzeige", "#ad"])

    lines = ["=" * 48, "CODE-CHECK (deterministisch)"]
    if found:
        lines += [f"  ✗ Verbotenes Wort: '{w}'" for w in found]
        lines.append("URTEIL: BLOCKIERT")
        urteil = "BLOCKIERT"
    else:
        if not has_ad:
            lines.append("  ? Werbe-Kennzeichnung fehlt")
            urteil = "REVIEW"
        else:
            lines.append("  ✓ Keine harten Verstöße")
            urteil = "OK"
        lines.append(f"URTEIL: {urteil}")
    lines.append("=" * 48)
    return urteil, "\n".join(lines)

# ──────────────────────────────────────────────
# Speichern
# ──────────────────────────────────────────────
def speichern(thema: str, block: list[str]) -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    pfad = OUTPUT_DIR / f"ergebnisse_{timestamp}.txt"
    text = f"THEMA: {thema}\nDATUM: {timestamp}\n\n" + "\n\n".join(block)
    pfad.write_text(text, encoding="utf-8")
    return pfad

# ──────────────────────────────────────────────
# Haupt-Workflow
# ──────────────────────────────────────────────
def run(thema: str, model: str, temp_dan: float, temp_gate: float) -> None:
    block: list[str] = []

    # ── Schritt 1: Dan generiert Content ──
    print(f"\n{'='*48}")
    print(f"[DAN] Generiere Content für: '{thema}' ...")
    dan_output = ask_ollama(SYSTEM_DAN, f"Thema: {thema}", model, temp_dan)
    print("\n--- CONTENT (Dan) ---")
    print(dan_output)
    block.append("--- CONTENT (Dan) ---\n" + dan_output)

    # ── Schritt 2: Deterministischer Check ──
    print(f"\n[CODE-CHECK] Prüfe ...")
    urteil, report = code_check(dan_output)
    print(report)
    block.append(report)

    if urteil == "BLOCKIERT":
        stopp = "🛑 STOPP – BLOCKIERT durch deterministischen Filter.\nNICHT VERÖFFENTLICHEN – manuelle Prüfung erforderlich."
        print(f"\n{stopp}")
        block.append(stopp)
        pfad = speichern(thema, block)
        print(f"\nFERTIG – gespeichert in: {pfad}")
        sys.exit(0)

    # ── Schritt 3: Gatekeeper ──
    print(f"\n[GATEKEEPER] Prüft ...")
    gate_output = ask_ollama(SYSTEM_GATEKEEPER, dan_output, model, temp_gate)
    print("\n--- GATEKEEPER ---")
    print(gate_output)
    block.append("--- GATEKEEPER ---\n" + gate_output)

    # ── Schritt 4: Editor ──
    print(f"\n[EDITOR] Überarbeitet ...")
    editor_prompt = f"CONTENT:\n{dan_output}\n\nGATEKEEPER-URTEIL:\n{gate_output}"
    editor_output = ask_ollama(SYSTEM_EDITOR, editor_prompt, model, temp_gate)
    print("\n--- EDITOR ---")
    print(editor_output)
    block.append("--- EDITOR ---\n" + editor_output)

    # ── Speichern ──
    pfad = speichern(thema, block)
    print(f"\n{'='*48}")
    print(f"FERTIG – gespeichert in: {pfad}")

# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="FinAz Master-Controller – lokales Multi-Agenten-System"
    )
    parser.add_argument("thema", nargs="?", default=None,
                        help="Thema für den Content (optional, sonst interaktiv)")
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL,
                        help=f"Ollama-Modell (Standard: {DEFAULT_MODEL})")
    parser.add_argument("-t", "--temp", type=float, default=None,
                        help="Temperatur für beide Agenten (überschreibt Defaults)")
    args = parser.parse_args()

    thema = args.thema or input("Thema eingeben: ").strip()
    if not thema:
        print("[FEHLER] Kein Thema angegeben.")
        sys.exit(1)

    temp_dan = args.temp if args.temp is not None else DEFAULT_TEMP_DAN
    temp_gate = args.temp if args.temp is not None else DEFAULT_TEMP_GATE

    print("╔══════════════════════════════════════╗")
    print("║   FinAz Master-Controller v2.0       ║")
    print(f"║   Modell: {args.model:<27}║")
    print("╚══════════════════════════════════════╝")

    run(thema, args.model, temp_dan, temp_gate)


if __name__ == "__main__":
    main()
