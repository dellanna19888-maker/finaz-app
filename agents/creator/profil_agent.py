"""Agent 1: Profil-Analyse"""
from .groq_client import chat

SYSTEM = """Du bist ein erfahrener Creator-Coach spezialisiert auf TikTok und Instagram im deutschsprachigen Raum.
Antworte auf Deutsch, kurz und nischen-spezifisch. Halte dich exakt an das Format."""


def analyse(nische, follower_tiktok, follower_instagram, posting_freq, problem, model=None, temp=0.6):
    total = int(follower_tiktok or 0) + int(follower_instagram or 0)
    level = "Anfänger" if total < 2000 else ("Wachstum" if total < 20000 else "Profi")
    prompt = (
        f"Analysiere diesen {nische}-Creator:\n"
        f"- TikTok: {follower_tiktok} Follower | Instagram: {follower_instagram} Follower\n"
        f"- {posting_freq} Posts/Woche | Problem: {problem}\n\n"
        f"Antworte genau so:\n"
        f"NISCHE: {nische}\n"
        f"LEVEL: {level}\n"
        f"STÄRKE: <was in der {nische}-Nische gut funktioniert, 1 Satz>\n"
        f"PROBLEM: <konkrete Ursache für '{problem}' in dieser Nische, 1 Satz>\n"
        f"TIPP: <eine sofort umsetzbare Aktion speziell für {nische}-Creator diese Woche>"
    )
    return chat(SYSTEM, prompt, max_tokens=300, temp=temp)
