"""
Agent 3: Monetisierung (kompakt)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """Du bist ein Monetisierungs-Experte fuer Creator. Antworte ausschliesslich auf Deutsch, kurz und konkret mit realistischen Preisen in EUR. Halte dich exakt an das vorgegebene Format."""


def erstelle_plan(nische, follower_total, profil_analyse, model, temp=0.6):
    prompt = (
        f"Erstelle einen Monetisierungsplan fuer einen Creator in der Nische '{nische}' mit {follower_total} Followern.\n\n"
        f"Antworte genau in diesem Format:\n"
        f"SOFORT (0-30 Tage): <Produkt + Preis + wie verkaufen>\n"
        f"WACHSTUM (1-3 Monate): <Produkt + Preis + Ziel>\n"
        f"VIP (3-6 Monate): <High-Ticket Angebot + Preis 500-5000 EUR>\n"
        f"AGENTUR_ANGEBOT: <was die Agentur anbietet + Preis>"
    )
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 240},
        }, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"[Timeout/Fehler Agent 3: {e}]"
