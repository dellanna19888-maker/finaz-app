"""
Agent 2: Growth-Strategie (kompakt)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """Du bist Social-Media-Experte. Antworte immer auf Deutsch."""


def erstelle_plan(nische, profil_analyse, model, temp=0.5):
    prompt = (
        f"Erstelle einen Wachstumsplan auf Deutsch fuer die Nische: {nische}\n"
        f"Antworte NUR mit:\n"
        f"TIKTOK: [Frequenz + Uhrzeit + Hook-Formel]\n"
        f"INSTAGRAM: [Frequenz + Reels vs Stories]\n"
        f"WOCHE1: [eine Aufgabe]\n"
        f"WOCHE2: [eine Aufgabe]\n"
        f"ZIEL: [Follower-Ziel in 30 Tagen]"
    )
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 200},
        }, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"[Timeout/Fehler Agent 2: {e}]"
