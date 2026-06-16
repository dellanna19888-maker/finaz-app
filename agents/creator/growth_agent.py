"""
Agent 2: Growth-Strategie (kompakt)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

def erstelle_plan(nische, profil_analyse, model, temp=0.5):
    prompt = (
        f"TikTok+Instagram Wachstumsplan fuer {nische}:\n"
        f"TIKTOK: Poste"
    )
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 100},
        }, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"[Timeout/Fehler Agent 2: {e}]"
