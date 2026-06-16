"""Agent 7: Konkurrenz-Analyse"""
from .groq_client import chat

SYSTEM = """Du bist ein Social-Media-Stratege. Analysiere wie ein Creator seine Konkurrenz schlagen kann.
Antworte auf Deutsch, konkret und umsetzbar."""


def analysiere_konkurrenz(nische, konkurrenz, model=None, temp=0.65):
    if not konkurrenz or konkurrenz.lower() in ("kein", "keine", "-", "nein"):
        return "Keine Konkurrenz angegeben — fokussiere dich auf deine eigene Nische und authentischen Content!"

    prompt = (
        f"Ein {nische}-Creator analysiert seinen Konkurrenten: {konkurrenz}\n\n"
        f"Antworte genau so:\n"
        f"KONKURRENZ: {konkurrenz}\n"
        f"WAS SIE GUT MACHEN: <eine Stärke die man lernen kann>\n"
        f"DEINE LÜCKE: <was der Konkurrent nicht macht, wo du punkten kannst>\n"
        f"UNTERSCHEIDUNG: <wie du dich als {nische}-Creator klar abhebst>\n"
        f"AKTION: <eine konkrete Maßnahme diese Woche>"
    )
    return chat(SYSTEM, prompt, max_tokens=280, temp=temp)
