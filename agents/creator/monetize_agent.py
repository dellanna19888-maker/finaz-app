"""Agent 3: Monetisierung"""
from .groq_client import chat

SYSTEM = """Du bist ein Monetisierungs-Experte für Creator im deutschsprachigen Markt.
Nenne konkrete Produkte und realistische EUR-Preise passend zur Nische. Halte dich exakt an das Format."""


def erstelle_plan(nische, follower_total, profil_analyse, model=None, temp=0.6):
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
        f"Erstelle einen Monetisierungsplan für einen {nische}-Creator mit {follower_str}.\n\n"
        f"Antworte genau so:\n"
        f"SOFORT (0-30 Tage): <konkretes {nische}-Produkt + Preis + Verkaufskanal>\n"
        f"WACHSTUM (1-3 Monate): <skalierbareres {nische}-Produkt + Preis + Follower-Ziel>\n"
        f"VIP (3-6 Monate): <Premium {nische}-Angebot + Preis 500–5000 EUR>\n"
        f"AGENTUR_ANGEBOT: <was unsere Agentur dem Creator für {nische} anbietet + monatlicher Preis>"
    )
    return chat(SYSTEM, prompt, max_tokens=320, temp=temp)
