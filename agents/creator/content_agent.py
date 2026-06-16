"""
Agent 4: Content-Plan (kompakt - 10 Ideen statt 30)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """Du bist ein viraler Content-Stratege. Antworte ausschliesslich auf Deutsch. Erstelle nischen-spezifische Ideen mit fesselnden Hooks."""


def generiere(nische, growth_plan, model, temp=0.7):
    prompt = (
        f"Erstelle 6 Content-Ideen fuer die Nische '{nische}' (3 fuer TikTok, 3 fuer Instagram).\n\n"
        f"Schreibe jede Idee in genau einer Zeile in diesem Format:\n"
        f"<Plattform>: <HOOK> | <FORMAT> | <CTA>\n\n"
        f"Beginne jetzt mit den 6 Ideen:"
    )
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 280},
        }, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"[Timeout/Fehler Agent 4: {e}]"
