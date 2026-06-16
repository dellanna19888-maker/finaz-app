#!/usr/bin/env python3
"""
master.py – Zentraler Orchestrator für das FinAz Multi-Agenten-System.

Modi:
  1) content  – Content-Agent 'Dan' generiert Post → Compliance-Check → Ausgabe
  2) lead     – Sales-Engine verarbeitet einen Lead → Follow-up-Strategie
  3) batch    – Mehrere Themen aus einer Datei verarbeiten
"""
import json
import sys
from datetime import datetime
from pathlib import Path

import compliance_rules
import silentscale
import sales_receiver


OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def _speichern(prefix: str, daten: dict) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pfad = OUTPUT_DIR / f"{prefix}_{timestamp}.json"
    pfad.write_text(json.dumps(daten, ensure_ascii=False, indent=2))
    return pfad


def run_content(thema: str) -> None:
    print(f"\n[DAN] Generiere Content für: '{thema}' ...")

    try:
        content = silentscale.generate(thema)
    except Exception as e:
        print(f"[FEHLER] Content-Generierung fehlgeschlagen: {e}")
        return

    print("[CODE-CHECK] Compliance-Prüfung läuft ...")
    pruefung = compliance_rules.check(content)

    ergebnis = {
        "thema": thema,
        "content": content,
        "compliance": pruefung,
        "freigabe": pruefung["status"] == "OK",
        "hinweis": "NICHT VERÖFFENTLICHEN – manuelle Prüfung erforderlich"
                   if pruefung["status"] == "BLOCKIERT" else "Freigegeben zur Veröffentlichung",
    }

    pfad = _speichern("content", ergebnis)

    print(f"\n{'='*50}")
    print(f"STATUS: {pruefung['status']}")
    if pruefung["gruende"]:
        print("GRÜNDE:")
        for g in pruefung["gruende"]:
            print(f"  • {g}")
    print(f"\nHINWEIS: {ergebnis['hinweis']}")
    print(f"Gespeichert: {pfad}")
    print("="*50)

    if pruefung["status"] == "BLOCKIERT":
        print("\n🛑 STOPP – Manuelle Prüfung erforderlich. Nicht veröffentlichen.")
        sys.exit(1)

    print("\n✅ Content freigegeben:")
    print(f"  HOOK:    {content.get('hook', '')}")
    print(f"  CAPTION: {content.get('caption', '')[:80]}...")
    print(f"  VISUAL:  {content.get('visual_prompt', '')[:80]}...")


def run_lead(lead_json: str) -> None:
    try:
        lead = json.loads(lead_json)
    except json.JSONDecodeError as e:
        print(f"[FEHLER] Ungültiges Lead-JSON: {e}")
        sys.exit(1)

    print(f"\n[SALES] Verarbeite Lead: {lead.get('name', 'Unbekannt')} ...")

    try:
        strategie = sales_receiver.process_lead(lead)
    except Exception as e:
        print(f"[FEHLER] Sales-Analyse fehlgeschlagen: {e}")
        return

    ergebnis = {"lead": lead, "strategie": strategie}
    pfad = _speichern("lead", ergebnis)

    print(f"\n{'='*50}")
    print(f"PRIORITÄT:      {strategie.get('prioritaet', '?').upper()}")
    print(f"NÄCHSTE AKTION: {strategie.get('naechste_aktion', '')}")
    print(f"NACHRICHT:      {strategie.get('follow_up_nachricht', '')[:100]}...")
    print(f"Gespeichert: {pfad}")
    print("="*50)


def run_batch(datei: str) -> None:
    pfad = Path(datei)
    if not pfad.exists():
        print(f"[FEHLER] Datei nicht gefunden: {datei}")
        sys.exit(1)

    themen = [line.strip() for line in pfad.read_text().splitlines() if line.strip()]
    print(f"\n[BATCH] {len(themen)} Themen gefunden.")
    for i, thema in enumerate(themen, 1):
        print(f"\n--- [{i}/{len(themen)}] ---")
        run_content(thema)


def main() -> None:
    print("╔══════════════════════════════════════╗")
    print("║   FinAz Multi-Agenten-System v1.0    ║")
    print("╚══════════════════════════════════════╝")
    print("\nModi: [1] Content  [2] Lead  [3] Batch")

    modus = input("\nModus wählen (1/2/3): ").strip()

    if modus == "1":
        thema = input("Thema eingeben: ").strip()
        if not thema:
            print("[FEHLER] Kein Thema angegeben.")
            sys.exit(1)
        run_content(thema)

    elif modus == "2":
        print("Lead-Daten als JSON eingeben (Beispiel: {\"name\":\"Max\",\"email\":\"max@x.de\",\"interesse\":\"ETF\",\"quelle\":\"Instagram\"})")
        lead_json = input("Lead JSON: ").strip()
        run_lead(lead_json)

    elif modus == "3":
        datei = input("Pfad zur Themen-Datei (eine Zeile = ein Thema): ").strip()
        run_batch(datei)

    else:
        print("[FEHLER] Ungültiger Modus.")
        sys.exit(1)


if __name__ == "__main__":
    main()
