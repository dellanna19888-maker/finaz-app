"""
Agent 1: Profil-Analyse
Analysiert den Creator (Nische, Level, Probleme) und gibt eine Basis-Diagnose.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """Du bist ein erfahrener Creator-Coach mit Fokus auf TikTok und Instagram.
Du analysierst Creator-Profile und erkennst sofort die echten Probleme.
Strukturiere deine Analyse so:

NISCHE: [Thema des Creators]
LEVEL: [Anfaenger | Wachstum | Fortgeschritten | Profi]
STAERKEN: [2-3 konkrete Staerken]
SCHWAECHEN: [2-3 konkrete Probleme die Wachstum blockieren]
GROESSTE_CHANCE: [die eine Sache die sofort mehr Reichweite bringt]
PRIORITAET: [was der Creator ALS ERSTES tun soll - konkret und umsetzbar]

Sei direkt, ehrlich und konkret. Kein Bullshit. Kein "das kommt drauf an"."""


def analyse(nische: str, follower_tiktok: str, follower_instagram: str,
            posting_freq: str, problem: str, model: str, temp: float = 0.7) -> str:
    prompt = f"""Creator-Profil:
- Nische: {nische}
- TikTok Follower: {follower_tiktok}
- Instagram Follower: {follower_instagram}
- Posting-Frequenz: {posting_freq} pro Woche
- Groesstes Problem: {problem}

Erstelle eine ehrliche Profil-Analyse."""

    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp},
        }, timeout=180)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        print("[FEHLER] Kein Ollama.")
        sys.exit(1)
