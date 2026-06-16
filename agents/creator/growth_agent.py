"""
Agent 2: Growth-Strategie (kompakt)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """Antworte NUR auf Deutsch. Du bist TikTok+Instagram Wachstums-Experte fuer den deutschen Markt.
Fuelle diese Vorlage aus (max 80 Woerter):
TIKTOK: [Posting-Haeufigkeit + beste Uhrzeit + eine Hook-Formel fuer die Nische]
INSTAGRAM: [Posting-Haeufigkeit + Reels vs Stories Verhaeltnis]
WOCHE1: [eine konkrete Aufgabe in Woche 1]
WOCHE2: [eine konkrete Aufgabe in Woche 2]
ZIEL: [realistisches Follower-Ziel in 30 Tagen]
Schreibe NICHTS ausserhalb dieser Vorlage. Kein Englisch."""


def erstelle_plan(nische, profil_analyse, model, temp=0.5):
    prompt = f"Nische:{nische} Analyse:{profil_analyse[:100]}"
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 200},
        }, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"[Timeout/Fehler Agent 2: {e}]"
