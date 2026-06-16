"""
Agent 3: Monetisierung (kompakt)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """Du bist Business-Coach. Antworte immer auf Deutsch."""


def erstelle_plan(nische, follower_total, profil_analyse, model, temp=0.5):
    prompt = (
        f"Nische:{nische} Follower:{follower_total}\n"
        f"Monetisierungsplan auf Deutsch, NUR diese Zeilen:\n"
        f"SOFORT: "
    )
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 100},
        }, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"[Timeout/Fehler Agent 3: {e}]"
