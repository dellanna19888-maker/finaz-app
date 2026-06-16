"""
Content-Agent 'Dan' – generiert Faceless-Content für SilentScale.
Kommuniziert lokal mit Ollama (kein externer API-Call nötig).
"""
import json
import subprocess


OLLAMA_MODEL = "qwen2.5:3b"

DAN_SYSTEM_PROMPT = """Du bist Dan, ein erfahrener Faceless-Content-Creator im Bereich Finanzen und Vermögensaufbau.
Dein Stil: dark, moody, premium. Keine leeren Versprechen. Keine Garantien. Keine Finanzberatung.
Jeder Post enthält eine Werbekennzeichnung (#Werbung oder #Anzeige).
Du antwortest IMMER als valides JSON mit diesen Feldern:
{
  "hook": "...",
  "script": "...",
  "caption": "...",
  "hashtags": ["...", "..."],
  "visual_prompt": "..."
}"""


def generate(thema: str) -> dict:
    """Generiert Content zu einem Thema. Gibt dict zurück."""
    user_msg = f"Erstelle einen kompletten Social-Media-Post zum Thema: {thema}"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"[SYSTEM]{DAN_SYSTEM_PROMPT}[/SYSTEM]\n\n{user_msg}",
        "stream": False,
        "format": "json",
    }

    result = subprocess.run(
        ["curl", "-s", "-X", "POST", "http://localhost:11434/api/generate",
         "-H", "Content-Type: application/json",
         "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=120
    )

    if result.returncode != 0:
        raise RuntimeError(f"Ollama-Fehler: {result.stderr}")

    response = json.loads(result.stdout)
    content = json.loads(response.get("response", "{}"))
    return content
