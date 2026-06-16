"""Agent 5: DM-Vorlagen"""
from .groq_client import chat

SYSTEM_DM = """Du bist Vertriebs-Texter für eine Creator-Wachstums-Agentur.
Schreibe DMs die eine Agentur an einen Social-Media-Creator schickt. Auf Deutsch, kurz und direkt."""


def erstelle_dm(nische, angebot, preis, model=None, temp=0.7):
    prompt = (
        f"Unsere Agentur schreibt einem {nische}-Creator auf Instagram/TikTok an.\n"
        f"Schreibe 2 kurze DMs auf Deutsch:\n"
        f"DM1 (Erstkontakt): Lobe seinen {nische}-Content und biete konkret an, "
        f"mehr Follower und Einnahmen zu generieren. Kurz und direkt, 2-3 Sätze.\n"
        f"DM2 (Follow-up): Freundliche Nachfrage mit einem konkreten Mehrwert. 2 Sätze.\n"
        f"Schreibe NUR die zwei DMs, keine Erklärungen."
    )
    return chat(SYSTEM_DM, prompt, max_tokens=220, temp=temp)


def erstelle_salespage(nische, angebot, preis, zielgruppe, model=None, temp=0.75):
    system = "Du bist Copywriter. Schreibe eine kurze Salespage. Max 150 Wörter. Format: HEADLINE | PROBLEM | LÖSUNG | 3 LEISTUNGEN | PREIS | CTA"
    prompt = f"Nische:{nische} Angebot:{angebot} Preis:{preis} Zielgruppe:{zielgruppe}"
    return chat(system, prompt, max_tokens=250, temp=temp)
