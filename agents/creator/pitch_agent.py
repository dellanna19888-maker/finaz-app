"""
Agent 5: Pitch Generator
Schreibt personalisierte Verkaufsnachrichten fuer DM, Email oder Salespage.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM_DM = """Du bist ein Experte fuer High-Converting DM-Verkaufsnachrichten auf TikTok und Instagram.
Du schreibst Nachrichten die sich menschlich anfuehlen, nicht wie Spam.
Erstelle 3 DM-Varianten:

DM_VARIANTE_1 (Kalt-Ansprache, kurz):
[Max. 3 Saetze. Direkt zum Punkt. Konkreter Nutzen.]

DM_VARIANTE_2 (Nach Kommentar/Interaktion):
[Max. 4 Saetze. Bezug auf Interaktion. Personalisiert.]

DM_VARIANTE_3 (Follow-up nach erstem Kontakt):
[Max. 4 Saetze. Sanfter Druck. Mehrwert hinzufuegen.]

TIPP: [ein konkreter Tipp wie man die Antwortrate erhoeht]"""

SYSTEM_SALESPAGE = """Du bist ein Copywriter fuer Creator-Angebote.
Schreibe eine kurze Salespage (fuer Link-in-Bio oder Notion):

HEADLINE: [starke Ueberschrift die sofort klar macht was das Angebot ist]
SUBHEADLINE: [konkrete Versprechen in 1 Satz]
PROBLEM: [das groesste Problem das der Creator hat - 2-3 Saetze]
LOESUNG: [wie das Angebot das Problem loest - 2-3 Saetze]
LEISTUNGEN: [5 konkrete Punkte was enthalten ist]
PREIS: [Preis + Zahlungsmodalitaeten]
GARANTIE: [falls angeboten - keine unrealistischen Versprechen]
CTA: [klarer Handlungsaufruf - DM, Link, etc.]"""


def erstelle_dm(nische: str, angebot: str, preis: str, model: str, temp: float = 0.8) -> str:
    prompt = f"""Creator-Nische: {nische}
Angebot: {angebot}
Preis: {preis}

Erstelle 3 DM-Varianten fuer die Kaltakquise von neuen Creator-Kunden."""

    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM_DM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp},
        }, timeout=180)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        print("[FEHLER] Kein Ollama.")
        sys.exit(1)


def erstelle_salespage(nische: str, angebot: str, preis: str,
                       zielgruppe: str, model: str, temp: float = 0.75) -> str:
    prompt = f"""Nische: {nische}
Angebot: {angebot}
Preis: {preis}
Zielgruppe: {zielgruppe}

Schreibe die komplette Salespage."""

    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM_SALESPAGE, "prompt": prompt,
            "stream": False, "options": {"temperature": temp},
        }, timeout=180)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        print("[FEHLER] Kein Ollama.")
        sys.exit(1)
