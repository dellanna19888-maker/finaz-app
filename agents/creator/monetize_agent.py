"""
Agent 3: Monetisierung (kompakt)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """Du bist Monetisierungs-Experte fuer Creator. Antworte KURZ. Max 150 Woerter.
Format:
SOFORT (0-30 Tage): [Produkt + Preis + wie verkaufen in 2 Saetzen]
WACHSTUM (1-3 Monate): [Produkt + Preis + Ziel]
VIP (3-6 Monate): [High-Ticket Angebot + Preis 500-5000 EUR]
AGENTUR_ANGEBOT: [was du anbietest + Preis in 1 Satz]"""


def erstelle_plan(nische, follower_total, profil_analyse, model, temp=0.7):
    prompt = f"Nische:{nische} Follower:{follower_total}"
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 200},
        }, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"[Timeout/Fehler Agent 3: {e}]"
