"""
Sales-Engine – verarbeitet eingehende Leads und generiert Follow-up-Strategien.
Leads kommen als dict: {"name": "...", "email": "...", "interesse": "...", "quelle": "..."}
"""
import json
import subprocess

OLLAMA_MODEL = "qwen2.5:3b"

SALES_SYSTEM_PROMPT = """Du bist ein erfahrener Sales-Stratege im Finanzbereich.
Du analysierst eingehende Leads und erstellst maßgeschneiderte Follow-up-Strategien.
Keine Finanzberatung. Kein aggressives Pushing. Vertrauen aufbauen.
Antworte IMMER als valides JSON:
{
  "prioritaet": "hoch|mittel|niedrig",
  "naechste_aktion": "...",
  "follow_up_nachricht": "...",
  "notizen": "..."
}"""


def process_lead(lead: dict) -> dict:
    """Analysiert einen Lead und gibt Follow-up-Strategie zurück."""
    user_msg = f"Analysiere diesen Lead und erstelle eine Follow-up-Strategie:\n{json.dumps(lead, ensure_ascii=False)}"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"[SYSTEM]{SALES_SYSTEM_PROMPT}[/SYSTEM]\n\n{user_msg}",
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
    strategie = json.loads(response.get("response", "{}"))
    return strategie
