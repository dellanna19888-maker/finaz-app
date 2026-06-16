"""
Agent 4: Content-Plan (kompakt - 10 Ideen statt 30)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """Antworte NUR auf Deutsch. Du bist viraler Content-Stratege fuer den deutschen Markt.
Erstelle genau 6 Content-Ideen fuer die gegebene Nische (3 TikTok, 3 Instagram).
Format pro Zeile: HOOK | FORMAT | CTA
Hooks muessen nischen-spezifisch und auf Deutsch sein.
Schreibe NICHTS ausserhalb dieser Liste. Kein Englisch."""


def generiere(nische, growth_plan, model, temp=0.7):
    prompt = f"Nische:{nische}"
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 250},
        }, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"[Timeout/Fehler Agent 4: {e}]"
