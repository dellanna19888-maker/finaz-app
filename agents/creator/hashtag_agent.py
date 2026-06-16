"""
Agent 6: Hashtag-Generator
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """Du bist ein Social-Media-Hashtag-Experte für den deutschsprachigen Markt.
Gib ausschließlich Hashtags aus, keine Erklärungen."""


def generiere_hashtags(nische, model, temp=0.6):
    prompt = (
        f"Erstelle 15 Hashtags für einen {nische}-Creator im deutschsprachigen Raum.\n"
        f"5 große Hashtags (1M+ Posts), 5 mittlere (100K–1M), 5 kleine Nischen-Hashtags (<100K).\n"
        f"Format:\n"
        f"GROSS: #tag1 #tag2 #tag3 #tag4 #tag5\n"
        f"MITTEL: #tag1 #tag2 #tag3 #tag4 #tag5\n"
        f"NISCHE: #tag1 #tag2 #tag3 #tag4 #tag5\n"
        f"Alle Hashtags auf Deutsch oder gemischt Deutsch/Englisch."
    )
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 180},
        }, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"[Timeout/Fehler Hashtags: {e}]"
