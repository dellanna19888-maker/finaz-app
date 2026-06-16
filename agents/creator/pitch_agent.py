"""
Agent 5: Pitch Generator (kompakt)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM_DM = """Du bist Vertriebs-Texter für eine Creator-Wachstums-Agentur. Schreibe DMs die eine Agentur an einen Social-Media-Creator schickt, um ihm Wachstumshilfe anzubieten. Auf Deutsch, kurz und direkt."""

SYSTEM_SALESPAGE = """Du bist Copywriter. Schreibe eine kurze Salespage. Max 150 Woerter.
Format: HEADLINE | PROBLEM (1 Satz) | LOESUNG (1 Satz) | 3 LEISTUNGEN | PREIS | CTA"""


def erstelle_dm(nische, angebot, preis, model, temp=0.7):
    prompt = (
        f"Unsere Agentur schreibt einem {nische}-Creator auf Instagram/TikTok an.\n"
        f"Schreibe 2 kurze DMs auf Deutsch:\n"
        f"DM1 (Erstkontakt): Lobe seinen {nische}-Content und biete konkret an, "
        f"mehr Follower und Einnahmen zu generieren. Kurz und direkt, 2-3 Sätze.\n"
        f"DM2 (Follow-up): Freundliche Nachfrage mit einem konkreten Mehrwert. 2 Sätze.\n"
        f"Schreibe NUR die zwei DMs, keine Erklärungen."
    )
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM_DM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 160},
        }, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"[Timeout/Fehler DM: {e}]"


def erstelle_salespage(nische, angebot, preis, zielgruppe, model, temp=0.75):
    prompt = f"Nische:{nische} Angebot:{angebot} Preis:{preis} Zielgruppe:{zielgruppe}"
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM_SALESPAGE, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 200},
        }, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"[Timeout/Fehler Salespage: {e}]"
