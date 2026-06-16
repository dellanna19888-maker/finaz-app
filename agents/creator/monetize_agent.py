"""
Agent 3: Monetisierung (kompakt)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """Du bist ein Monetisierungs-Experte für Creator im deutschsprachigen Markt. Nenne konkrete Produkte und realistische EUR-Preise passend zur Nische. Halte dich exakt an das Format."""


def erstelle_plan(nische, follower_total, profil_analyse, model, temp=0.6):
    # follower_total kann "TikTok:400 IG:200" oder eine Zahl sein
    try:
        if isinstance(follower_total, str) and "TikTok" in follower_total:
            parts = follower_total.replace("TikTok:", "").replace("IG:", "").split()
            total_n = sum(int(x) for x in parts if x.isdigit())
            follower_str = f"{total_n} Gesamt-Followern"
        else:
            follower_str = f"{follower_total} Followern"
    except Exception:
        follower_str = "wenigen Followern"

    prompt = (
        f"Erstelle einen Monetisierungsplan für einen {nische}-Creator mit {follower_str} im deutschsprachigen Markt.\n\n"
        f"Nenne konkrete {nische}-Produkte mit realistischen EUR-Preisen. Antworte genau so:\n"
        f"SOFORT (0-30 Tage): <konkretes {nische}-Produkt + Preis + Verkaufskanal>\n"
        f"WACHSTUM (1-3 Monate): <skalierbareres {nische}-Produkt + Preis + Follower-Ziel>\n"
        f"VIP (3-6 Monate): <Premium {nische}-Angebot + Preis 500–5000 EUR>\n"
        f"AGENTUR_ANGEBOT: <was unsere Agentur dem Creator für {nische} anbietet + monatlicher Preis>"
    )
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 240},
        }, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"[Timeout/Fehler Agent 3: {e}]"
