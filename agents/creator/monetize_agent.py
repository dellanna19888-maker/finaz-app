"""
Agent 3: Monetisierung (kompakt)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """You are a monetization expert for social media creators. Answer ONLY about the given niche. Max 100 words. Use German.
Fill in this exact template:
SOFORT (0-30 Tage): [product idea + price + how to sell, 2 sentences]
WACHSTUM (1-3 Monate): [product idea + price + follower goal]
VIP (3-6 Monate): [high-ticket offer + price between 500-5000 EUR]
AGENTUR_ANGEBOT: [what the agency offers + price, 1 sentence]
Do NOT write anything outside this template."""


def erstelle_plan(nische, follower_total, profil_analyse, model, temp=0.5):
    prompt = f"Nische:{nische} Follower:{follower_total}"
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 200},
        }, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"[Timeout/Fehler Agent 3: {e}]"
