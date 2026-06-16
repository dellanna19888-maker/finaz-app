"""
sales_receiver.py – Sales-Engine con integrazione CRM automatica.

Workflow:
  1. Riceve un lead (dict o input interattivo)
  2. Ollama genera strategia di follow-up
  3. Lead + strategia salvati automaticamente nel CRM (crm.py)
  4. Output salvato in output/lead_*.json

Uso standalone:
  python3 sales_receiver.py
"""
import json
import sys
from datetime import datetime
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

SALES_SYSTEM_PROMPT = """Du bist ein erfahrener Sales-Stratege im Finanzbereich.
Du analysierst eingehende Leads und erstellst maßgeschneiderte Follow-up-Strategien.
Keine Finanzberatung. Kein aggressives Pushing. Vertrauen aufbauen.
Antworte IMMER als valides JSON mit diesen Feldern:
{
  "prioritaet": "hoch|mittel|niedrig",
  "followup_tage": <Zahl zwischen 1 und 7>,
  "naechste_aktion": "...",
  "follow_up_nachricht": "...",
  "notizen": "..."
}"""


def _ask_ollama(lead: dict) -> dict:
    user_msg = f"Analysiere diesen Lead und erstelle eine Follow-up-Strategie:\n{json.dumps(lead, ensure_ascii=False)}"
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": f"[SYSTEM]{SALES_SYSTEM_PROMPT}[/SYSTEM]\n\n{user_msg}",
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.4},
        }, timeout=180)
        r.raise_for_status()
        raw = r.json().get("response", "{}")
        return json.loads(raw)
    except requests.exceptions.ConnectionError:
        print("[FEHLER] Kein Ollama. Läuft 'ollama serve'?")
        sys.exit(1)
    except json.JSONDecodeError:
        return {"prioritaet": "mittel", "followup_tage": 3,
                "naechste_aktion": "Manuell prüfen",
                "follow_up_nachricht": "", "notizen": "JSON-Fehler bei Analyse"}


def _save_to_crm(lead: dict, strategie: dict) -> int | None:
    try:
        from crm import save_lead
        followup_tage = int(strategie.get("followup_tage", 3))
        notizen = f"[AUTO] {strategie.get('notizen', '')} | Aktion: {strategie.get('naechste_aktion', '')}"
        lid = save_lead(
            name=lead.get("name", "Unbekannt"),
            email=lead.get("email", ""),
            telefon=lead.get("telefon", ""),
            interesse=lead.get("interesse", ""),
            quelle=lead.get("quelle", "sonstige"),
            notizen=notizen.strip(" |"),
            followup_tage=followup_tage,
        )
        return lid
    except Exception as e:
        print(f"[WARNUNG] CRM-Speicherung fehlgeschlagen: {e}")
        return None


def process_lead(lead: dict, save_crm: bool = True) -> dict:
    """
    Analysiert einen Lead und gibt die Strategie zurück.
    Speichert automatisch im CRM wenn save_crm=True.
    """
    strategie = _ask_ollama(lead)

    if save_crm:
        lid = _save_to_crm(lead, strategie)
        if lid:
            strategie["crm_id"] = lid

    # Speichere auch als JSON-Datei
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    pfad = OUTPUT_DIR / f"lead_{ts}.json"
    pfad.write_text(
        json.dumps({"lead": lead, "strategie": strategie}, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    strategie["_output_file"] = str(pfad)
    return strategie


def _input_lead_interactive() -> dict:
    print("\n── Neuen Lead eingeben ──")
    name = input("Name: ").strip()
    email = input("E-Mail: ").strip()
    telefon = input("Telefon (optional): ").strip()
    interesse = input("Interesse / Produkt: ").strip()
    quelle = input("Quelle (instagram/tiktok/linkedin/email/empfehlung/website): ").strip() or "sonstige"
    return {"name": name, "email": email, "telefon": telefon,
            "interesse": interesse, "quelle": quelle}


def main() -> None:
    print("╔══════════════════════════════════════╗")
    print("║   Sales-Engine + CRM Integration    ║")
    print("╚══════════════════════════════════════╝")

    lead = _input_lead_interactive()
    if not lead["name"]:
        print("[FEHLER] Name ist Pflichtfeld.")
        sys.exit(1)

    print(f"\n[SALES] Analysiere Lead '{lead['name']}' ...")
    strategie = process_lead(lead, save_crm=True)

    print(f"\n{'='*48}")
    print(f"PRIORITÄT:      {strategie.get('prioritaet', '?').upper()}")
    print(f"FOLLOW-UP IN:   {strategie.get('followup_tage', 3)} Tagen")
    print(f"NÄCHSTE AKTION: {strategie.get('naechste_aktion', '')}")
    print(f"\nFOLLOW-UP NACHRICHT:")
    print(f"  {strategie.get('follow_up_nachricht', '')}")
    print(f"\nNOTIZEN: {strategie.get('notizen', '')}")

    if "crm_id" in strategie:
        print(f"\n✅ Im CRM gespeichert als Lead #{strategie['crm_id']}")
        print(f"   → python3 crm.py list")
    print(f"   → Datei: {strategie.get('_output_file', '')}")
    print("=" * 48)


if __name__ == "__main__":
    main()
