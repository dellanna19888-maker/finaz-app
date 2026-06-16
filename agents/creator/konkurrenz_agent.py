"""
Agent 7: Konkurrenz-Analyse
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """Du bist ein Social-Media-Stratege. Analysiere wie ein Creator seine Konkurrenz schlagen kann.
Antworte auf Deutsch, konkret und umsetzbar."""


def analysiere_konkurrenz(nische, konkurrenz, model, temp=0.65):
    if not konkurrenz or konkurrenz.lower() in ("kein", "keine", "-", "nein"):
        return "Keine Konkurrenz angegeben — fokussiere dich auf deine eigene Nische!"

    prompt = (
        f"Ein {nische}-Creator analysiert seinen Konkurrenten: {konkurrenz}\n\n"
        f"Antworte genau so:\n"
        f"KONKURRENZ: {konkurrenz}\n"
        f"WAS SIE GUT MACHEN: <eine Stärke die man lernen kann>\n"
        f"DEINE LÜCKE: <was der Konkurrent nicht macht, wo du punkten kannst>\n"
        f"UNTERSCHEIDUNG: <wie du dich als {nische}-Creator klar abhebst>\n"
        f"AKTION: <eine konkrete Maßnahme diese Woche>"
    )
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 200},
        }, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"[Timeout/Fehler Konkurrenz: {e}]"
