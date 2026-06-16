"""Agent 4: Content-Ideen"""
from .groq_client import chat

SYSTEM = """Du bist ein viraler Content-Stratege spezialisiert auf den deutschsprachigen Markt.
Hooks müssen sofort die Zielgruppe der Nische ansprechen und neugierig machen."""


def generiere(nische, growth_plan, model=None, temp=0.7):
    prompt = (
        f"Erstelle 6 virale Content-Ideen für einen {nische}-Creator (3 für TikTok, 3 für Instagram).\n"
        f"Die Hooks müssen spezifisch für die {nische}-Zielgruppe sein und auf Deutsch.\n\n"
        f"Format:\n"
        f"TikTok: <Hook> | <Videoformat> | <Call-to-Action>\n"
        f"Instagram: <Hook> | <Post-Format> | <Call-to-Action>\n\n"
        f"Die 6 Ideen:"
    )
    return chat(SYSTEM, prompt, max_tokens=380, temp=temp)
