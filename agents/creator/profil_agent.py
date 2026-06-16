"""
Agent 1: Profil-Analyse
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """Du bist ein erfahrener Creator-Coach. Antworte ausschliesslich auf Deutsch, kurz und konkret. Halte dich exakt an das vorgegebene Format."""


def analyse(nische, follower_tiktok, follower_instagram, posting_freq, problem, model, temp=0.6):
    prompt = (
        f"Analysiere dieses Creator-Profil:\n"
        f"- Nische: {nische}\n"
        f"- TikTok-Follower: {follower_tiktok}\n"
        f"- Instagram-Follower: {follower_instagram}\n"
        f"- Posts pro Woche: {posting_freq}\n"
        f"- Groesstes Problem: {problem}\n\n"
        f"Antworte genau in diesem Format:\n"
        f"NISCHE: <Nische>\n"
        f"LEVEL: <Anfaenger/Wachstum/Profi>\n"
        f"STAERKE: <ein Satz>\n"
        f"PROBLEM: <ein Satz>\n"
        f"TIPP: <eine konkrete Aktion fuer diese Woche>"
    )
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 220},
        }, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        print("[FEHLER] Kein Ollama.")
        sys.exit(1)
    except Exception as e:
        return f"[Timeout/Fehler Agent 1: {e}]"
