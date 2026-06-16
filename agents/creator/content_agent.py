"""
Agent 4: Content-Plan (kompakt - 10 Ideen statt 30)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """Du bist Content-Stratege. Antworte immer auf Deutsch."""


def generiere(nische, growth_plan, model, temp=0.7):
    prompt = (
        f"Erstelle 6 Content-Ideen auf Deutsch fuer die Nische: {nische}\n"
        f"3x TikTok, 3x Instagram. Format pro Zeile:\n"
        f"HOOK | FORMAT | CTA\n"
        f"Beispiel: So verdienst du 500 EUR mit {nische} | Tutorial | Link in Bio\n"
        f"Schreibe NUR die 6 Ideen:"
    )
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 250},
        }, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"[Timeout/Fehler Agent 4: {e}]"
