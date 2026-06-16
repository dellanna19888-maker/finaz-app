"""
coaching.py – Modul B: Coaching / Infoprodotti
Agenten: EmailSequenceWriter → CourseOutliner → SalesFollowUp
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:3b"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

SYSTEM_EMAIL_SEQUENCE = """Du bist ein E-Mail-Marketing-Experte für Online-Coaches (deutschsprachiger Markt).
Erstelle eine 5-teilige Welcome-Sequence für neue Leads:
EMAIL 1: Herzliche Begrüßung + was sie erwartet
EMAIL 2: Wertvoller Tipp / Quick Win
EMAIL 3: Fallstudie oder Transformation (anonym)
EMAIL 4: Einwandbehandlung (Häufigstes Einwand direkt ansprechen)
EMAIL 5: Angebot / CTA
Format pro Email: BETREFF: / INHALT: (3–5 Sätze) / CTA:
Keine Erfolgsversprechen. Kein "du wirst garantiert Erfolg haben"."""

SYSTEM_COURSE_OUTLINER = """Du bist ein Instruktions-Designer für Online-Kurse.
Erstelle eine Kursstruktur mit:
- 5 Module (mit Modultitel)
- Pro Modul: 3 Lektionen (mit Lektionstitel + Lernziel in 1 Satz)
Format: MODUL 1: [Titel] / LEKTION 1.1: [Titel] – Lernziel: ...
Der Kurs soll praxisorientiert und umsetzbar sein."""

SYSTEM_SALES_FOLLOWUP = """Du bist ein Sales-Coach für persönliche Kurz-Nachrichten (WhatsApp/DM-Stil).
Erstelle 3 Follow-up-Nachrichten:
FOLLOW-UP 1: (Tag 2) – freundliche Erinnerung, kein Druck
FOLLOW-UP 2: (Tag 4) – Mehrwert/Tipp hinzufügen
FOLLOW-UP 3: (Tag 7) – letzter Kontaktversuch, Tür offen lassen
Jede Nachricht max. 3 Sätze. Persönlich, nicht spammig."""


def _ask(system: str, prompt: str, model: str, temp: float) -> str:
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": system, "prompt": prompt,
            "stream": False, "options": {"temperature": temp},
        }, timeout=180)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        print("[FEHLER] Kein Ollama.")
        sys.exit(1)


def run(nische: str, model: str = DEFAULT_MODEL) -> None:
    block = []

    print("\n[EmailSequenceWriter] Erstelle 5-Email-Sequenz ...")
    emails = _ask(SYSTEM_EMAIL_SEQUENCE, f"Coaching-Nische: {nische}", model, 0.8)
    print(emails)
    block.append("--- EMAIL-SEQUENZ ---\n" + emails)

    print("\n[CourseOutliner] Erstelle Kursstruktur ...")
    course = _ask(SYSTEM_COURSE_OUTLINER, f"Kurs-Thema: {nische}", model, 0.7)
    print(course)
    block.append("--- KURSSTRUKTUR ---\n" + course)

    print("\n[SalesFollowUp] Erstelle Follow-up-Nachrichten ...")
    followup = _ask(SYSTEM_SALES_FOLLOWUP, f"Angebot/Nische: {nische}", model, 0.8)
    print(followup)
    block.append("--- FOLLOW-UP NACHRICHTEN ---\n" + followup)

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    pfad = OUTPUT_DIR / f"coaching_{ts}.txt"
    pfad.write_text(f"NISCHE: {nische}\n\n" + "\n\n".join(block), encoding="utf-8")
    print(f"\nFERTIG – gespeichert in: {pfad}")


if __name__ == "__main__":
    nische = input("Coaching-Nische / Thema: ").strip()
    run(nische)
