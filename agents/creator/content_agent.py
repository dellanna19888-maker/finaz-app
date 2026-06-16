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
        f"Nische:{nische}\n"
        f"Schreibe 4 Content-Ideen auf Deutsch. Format: HOOK | FORMAT | CTA\n"
        f"1. "
    )
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 120},
        }, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"[Timeout/Fehler Agent 4: {e}]"
