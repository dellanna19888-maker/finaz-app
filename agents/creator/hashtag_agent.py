"""Agent 6: Hashtag-Generator"""
from .groq_client import chat

SYSTEM = """Du bist ein Social-Media-Hashtag-Experte für den deutschsprachigen Markt.
Gib ausschließlich Hashtags aus, keine Erklärungen."""


def generiere_hashtags(nische, model=None, temp=0.6):
    prompt = (
        f"Erstelle 15 Hashtags für einen {nische}-Creator im deutschsprachigen Raum.\n"
        f"5 große Hashtags (1M+ Posts), 5 mittlere (100K–1M), 5 kleine Nischen-Hashtags (<100K).\n"
        f"Format:\n"
        f"GROSS: #tag1 #tag2 #tag3 #tag4 #tag5\n"
        f"MITTEL: #tag1 #tag2 #tag3 #tag4 #tag5\n"
        f"NISCHE: #tag1 #tag2 #tag3 #tag4 #tag5"
    )
    return chat(SYSTEM, prompt, max_tokens=200, temp=temp)
