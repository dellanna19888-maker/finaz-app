"""
Agent 5: Pitch Generator (kompakt)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM_DM = """You are a DM copywriter. Write exactly 2 short DM templates in German for the given niche. Max 80 words total.
DM1 (Kaltakquise): direct, concrete benefit, max 3 sentences.
DM2 (Follow-up): gentle, add value, max 3 sentences.
Format:
DM1: [text]
DM2: [text]
Do NOT write anything outside this template."""

SYSTEM_SALESPAGE = """Du bist Copywriter. Schreibe eine kurze Salespage. Max 150 Woerter.
Format: HEADLINE | PROBLEM (1 Satz) | LOESUNG (1 Satz) | 3 LEISTUNGEN | PREIS | CTA"""


def erstelle_dm(nische, angebot, preis, model, temp=0.6):
    prompt = f"Nische:{nische} Angebot:{angebot} Preis:{preis}"
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM_DM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 200},
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
