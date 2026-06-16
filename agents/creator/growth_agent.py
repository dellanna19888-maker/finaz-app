"""
Agent 2: Growth-Strategie (kompakt)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """Du bist ein TikTok- und Instagram-Wachstumsexperte. Antworte ausschliesslich auf Deutsch, kurz und konkret. Halte dich exakt an das vorgegebene Format."""


def erstelle_plan(nische, profil_analyse, model, temp=0.6):
    prompt = (
        f"Erstelle einen 30-Tage-Wachstumsplan fuer einen Creator in der Nische '{nische}'.\n\n"
        f"Antworte genau in diesem Format:\n"
        f"TIKTOK: <Frequenz + beste Uhrzeit + eine Hook-Formel>\n"
        f"INSTAGRAM: <Frequenz + Reels vs Stories>\n"
        f"WOCHE1: <eine konkrete Aufgabe>\n"
        f"WOCHE2: <eine konkrete Aufgabe>\n"
        f"ZIEL: <realistisches Follower-Ziel in 30 Tagen>"
    )
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 240},
        }, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"[Timeout/Fehler Agent 2: {e}]"
