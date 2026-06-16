"""
Agent 4: Content-Plan (kompakt - 10 Ideen statt 30)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """Du bist ein viraler Content-Stratege spezialisiert auf den deutschsprachigen Markt. Hooks müssen sofort die Zielgruppe der Nische ansprechen und neugierig machen."""


def generiere(nische, growth_plan, model, temp=0.7):
    prompt = (
        f"Erstelle 6 virale Content-Ideen für einen {nische}-Creator (3 für TikTok, 3 für Instagram).\n"
        f"Die Hooks müssen spezifisch für die {nische}-Zielgruppe sein und auf Deutsch.\n\n"
        f"Format (eine Idee pro Zeile):\n"
        f"TikTok: <Hook der {nische}-Fans fesselt> | <Videoformat> | <Call-to-Action>\n"
        f"Instagram: <Hook der {nische}-Fans fesselt> | <Post-Format> | <Call-to-Action>\n\n"
        f"Die 6 Ideen:"
    )
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 280},
        }, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"[Timeout/Fehler Agent 4: {e}]"
