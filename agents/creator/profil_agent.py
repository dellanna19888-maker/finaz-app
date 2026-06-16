"""
Agent 1: Profil-Analyse (kompakt fuer Handy/tinyllama)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """Du bist Creator-Coach. Antworte immer auf Deutsch."""


def analyse(nische, follower_tiktok, follower_instagram, posting_freq, problem, model, temp=0.5):
    prompt = (
        f"Analysiere diesen Creator auf Deutsch:\n"
        f"Nische: {nische}, TikTok: {follower_tiktok} Follower, Instagram: {follower_instagram} Follower, "
        f"{posting_freq} Posts/Woche, Problem: {problem}\n"
        f"Antworte NUR mit:\n"
        f"NISCHE: {nische}\n"
        f"LEVEL: [Anfaenger/Wachstum/Profi]\n"
        f"STAERKE: [ein Satz]\n"
        f"PROBLEM: [ein Satz]\n"
        f"TIPP: [eine konkrete Aktion]"
    )
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
