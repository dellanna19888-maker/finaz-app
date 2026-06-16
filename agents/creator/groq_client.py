"""
Zentraler Groq-API-Client für alle Agents.
Modell: llama-3.3-70b-versatile (kostenlos, sehr schnell)
"""
import os
from pathlib import Path
from groq import Groq

# .env laden falls vorhanden
_env = Path(__file__).parent.parent.parent / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

GROQ_MODEL = "llama-3.3-70b-versatile"

_client = None


def get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY nicht gesetzt!\n"
                "Setze ihn mit: export GROQ_API_KEY='gsk_...'"
            )
        _client = Groq(api_key=api_key)
    return _client


def chat(system: str, prompt: str, max_tokens: int = 400, temp: float = 0.6) -> str:
    """Sendet eine Anfrage an Groq und gibt den Text zurück."""
    try:
        client = get_client()
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temp,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[Groq-Fehler: {e}]"
