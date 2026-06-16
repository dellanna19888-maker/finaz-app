"""
Agent 1: Profil-Analyse
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """Du bist ein erfahrener Creator-Coach spezialisiert auf TikTok und Instagram im deutschsprachigen Raum. Antworte auf Deutsch, kurz und nischen-spezifisch. Halte dich exakt an das Format."""


def analyse(nische, follower_tiktok, follower_instagram, posting_freq, problem, model, temp=0.6):
    total = int(follower_tiktok or 0) + int(follower_instagram or 0)
    level = "Anfänger" if total < 2000 else ("Wachstum" if total < 20000 else "Profi")
    prompt = (
        f"Analysiere diesen {nische}-Creator:\n"
        f"- TikTok: {follower_tiktok} Follower | Instagram: {follower_instagram} Follower\n"
        f"- {posting_freq} Posts/Woche | Problem: {problem}\n\n"
        f"Schreibe eine Analyse speziell für die Nische '{nische}'. Antworte genau so:\n"
        f"NISCHE: {nische}\n"
        f"LEVEL: {level}\n"
        f"STÄRKE: <was in der {nische}-Nische gut funktioniert, 1 Satz>\n"
        f"PROBLEM: <konkrete Ursache für '{problem}' in dieser Nische, 1 Satz>\n"
        f"TIPP: <eine sofort umsetzbare Aktion speziell für {nische}-Creator diese Woche>"
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
