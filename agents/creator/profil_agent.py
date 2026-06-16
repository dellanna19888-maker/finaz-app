"""
Agent 1: Profil-Analyse (kompakt fuer Handy/tinyllama)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """Du bist Creator-Coach. Antworte KURZ und KONKRET. Max 150 Woerter.
Format:
NISCHE: [ein Wort]
LEVEL: [Anfaenger/Wachstum/Profi]
STAERKE: [ein Satz]
PROBLEM: [ein Satz]
TIPP: [eine konkrete Aktion die sofort hilft]"""


def analyse(nische, follower_tiktok, follower_instagram, posting_freq, problem, model, temp=0.7):
    prompt = f"Nische:{nische} TikTok:{follower_tiktok} IG:{follower_instagram} Posts/Woche:{posting_freq} Problem:{problem}"
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 200},
        }, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        print("[FEHLER] Kein Ollama.")
        sys.exit(1)
    except Exception as e:
        return f"[Timeout/Fehler Agent 1: {e}]"
