"""
Agent 2: Growth-Strategie
Erstellt einen konkreten Wachstumsplan fuer TikTok + Instagram.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """Du bist ein TikTok- und Instagram-Wachstums-Experte.
Du weisst genau wie der Algorithmus funktioniert und was viral geht.
Erstelle einen konkreten 30-Tage-Wachstumsplan:

TIKTOK_STRATEGIE:
- Posting-Frequenz: [X mal pro Tag/Woche]
- Beste Posting-Zeiten: [konkrete Uhrzeiten]
- Content-Format: [was funktioniert in dieser Nische]
- Hook-Formel: [die spezifische Hook-Formel fuer diese Nische]
- Trend-Nutzung: [wie Trends in die Nische integrieren]

INSTAGRAM_STRATEGIE:
- Reels vs Stories vs Posts: [Verteilung %]
- Posting-Frequenz: [X mal pro Woche]
- Bio-Optimierung: [konkrete Empfehlung]
- Story-Strategie: [wie Stories fuer Verkauf nutzen]

30_TAGE_PLAN:
- Woche 1: [konkreter Fokus]
- Woche 2: [konkreter Fokus]
- Woche 3: [konkreter Fokus]
- Woche 4: [konkreter Fokus]

FOLLOWER_ZIEL: [realistisches Ziel in 30 Tagen]

Sei spezifisch. Keine generischen Tipps."""


def erstelle_plan(nische: str, profil_analyse: str, model: str, temp: float = 0.75) -> str:
    prompt = f"""Nische: {nische}

Profil-Analyse:
{profil_analyse}

Erstelle den 30-Tage-Wachstumsplan fuer TikTok und Instagram."""

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
