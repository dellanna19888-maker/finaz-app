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
        f"Schreibe 2 DM-Vorlagen auf Deutsch für eine Agentur, die einen {nische}-Creator anschreibt.\n"
        f"Die DMs sollen persönlich klingen und den {nische}-Creator direkt ansprechen.\n\n"
        f"Antworte genau so:\n"
        f"DM1 (Erstkontakt): <3 Sätze: persönliche Ansprache + konkreter Nutzen für {nische}-Creator + klare Frage>\n"
        f"DM2 (Follow-up): <3 Sätze: Bezug auf erstes DM + zusätzlicher Mehrwert für {nische} + nächster Schritt>"
    )
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM_DM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 240},
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
