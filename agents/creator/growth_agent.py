"""
Agent 2: Growth-Strategie (kompakt)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """You are a TikTok and Instagram growth expert. Answer ONLY about the given niche. Max 100 words. Use German.
Fill in this exact template:
TIKTOK: [post frequency + best time + one hook formula for this niche]
INSTAGRAM: [post frequency + Reels vs Stories ratio]
WOCHE1: [one specific task to do in week 1]
WOCHE2: [one specific task to do in week 2]
ZIEL: [realistic follower goal in 30 days based on current numbers]
Do NOT write anything outside this template. Do NOT invent unrelated topics."""


def erstelle_plan(nische, profil_analyse, model, temp=0.5):
    prompt = f"Nische:{nische} Analyse:{profil_analyse[:100]}"
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp, "num_predict": 200},
        }, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"[Timeout/Fehler Agent 2: {e}]"
