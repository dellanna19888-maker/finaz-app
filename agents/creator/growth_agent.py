"""
Agent 2: Growth-Strategie (kompakt)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """Du bist TikTok+Instagram-Experte. Antworte KURZ. Max 150 Woerter.
Format:
TIKTOK: [Frequenz + beste Zeit + 1 Hook-Formel]
INSTAGRAM: [Frequenz + Reels vs Stories]
WOCHE1: [eine konkrete Aufgabe]
WOCHE2: [eine konkrete Aufgabe]
ZIEL: [realistisches Follower-Ziel in 30 Tagen]"""


def erstelle_plan(nische, profil_analyse, model, temp=0.75):
    prompt = f"Nische:{nische} Analyse:{profil_analyse[:100]}"
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 200},
        }, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"[Timeout/Fehler Agent 2: {e}]"
