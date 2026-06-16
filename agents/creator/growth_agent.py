"""Agent 2: Growth-Strategie"""
from .groq_client import chat

SYSTEM = """Du bist ein TikTok- und Instagram-Wachstumsexperte im deutschsprachigen Raum.
Antworte auf Deutsch mit nischen-spezifischen, sofort umsetzbaren Tipps. Halte dich exakt an das Format."""


def erstelle_plan(nische, profil_analyse, model=None, temp=0.6):
    prompt = (
        f"Erstelle einen 30-Tage-Wachstumsplan für einen {nische}-Creator im deutschsprachigen Markt.\n\n"
        f"Antworte genau so:\n"
        f"TIKTOK: <Postings/Woche + beste Uhrzeit + eine Hook-Formel für {nische}>\n"
        f"INSTAGRAM: <Postings/Woche + Verhältnis Reels zu Stories>\n"
        f"WOCHE1: <eine konkrete {nische}-Aufgabe mit klarem Ergebnis>\n"
        f"WOCHE2: <eine konkrete {nische}-Aufgabe mit klarem Ergebnis>\n"
        f"ZIEL: <realistisches Follower-Ziel nach 30 Tagen>"
    )
    return chat(SYSTEM, prompt, max_tokens=320, temp=temp)
