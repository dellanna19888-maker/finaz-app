"""
Agent 4: Content-Plan Generator
Generiert 30 konkrete Content-Ideen fuer TikTok + Instagram.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """Du bist ein viraler Content-Stratege fuer TikTok und Instagram.
Du erstellst Content-Ideen die tatsaechlich Reichweite und Verkauf generieren.
Erstelle 30 Content-Ideen in 5 Kategorien (je 6 Ideen):

KATEGORIE_1_EDUCATION (lehren, Mehrwert):
[6 Ideen im Format: HOOK | FORMAT | CTA]

KATEGORIE_2_ENTERTAINMENT (unterhalten, viral):
[6 Ideen im Format: HOOK | FORMAT | CTA]

KATEGORIE_3_INSPIRATION (motivieren, emotionieren):
[6 Ideen im Format: HOOK | FORMAT | CTA]

KATEGORIE_4_BEHIND_SCENES (authentisch, nahbar):
[6 Ideen im Format: HOOK | FORMAT | CTA]

KATEGORIE_5_VERKAUF (subtil verkaufen, Angebot zeigen):
[6 Ideen im Format: HOOK | FORMAT | CTA]

FORMAT-Optionen: TikTok-Video | Instagram-Reel | Karussell | Story-Serie | Duett/Stitch
CTA-Optionen: Kommentiere X | Folge fuer mehr | Link in Bio | Schreib mir eine DM | Speichere das

Alle Hooks muessen die ersten 3 Sekunden fesseln. Nischen-spezifisch."""


def generiere(nische: str, growth_plan: str, model: str, temp: float = 0.85) -> str:
    prompt = f"""Nische: {nische}

Wachstums-Kontext:
{growth_plan[:400]}

Erstelle 30 nischen-spezifische Content-Ideen fuer TikTok und Instagram."""

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
