"""
Agent 5: Pitch Generator (kompakt)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM_DM = """Du bist ein DM-Texter für eine Creator-Wachstums-Agentur im deutschsprachigen Raum. Schreibe kurze, persönliche DMs die sich nicht wie Werbung anfühlen. Auf Deutsch."""

SYSTEM_SALESPAGE = """Du bist Copywriter. Schreibe eine kurze Salespage. Max 150 Woerter.
Format: HEADLINE | PROBLEM (1 Satz) | LOESUNG (1 Satz) | 3 LEISTUNGEN | PREIS | CTA"""


def erstelle_dm(nische, angebot, preis, model, temp=0.7):
    prompt = (
        f"2 kurze DM-Vorlagen für {nische}-Creator auf Deutsch:\n"
        f"DM1: <persönliche Ansprache + Nutzen in 2 Sätzen>\n"
        f"DM2: <Nachfass in 2 Sätzen>"
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
