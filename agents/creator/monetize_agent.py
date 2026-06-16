"""
Agent 3: Monetisierungs-Strategie
Erstellt einen Monetisierungsplan - von 0 bis High-Ticket/VIP.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """Du bist ein Experte fuer Creator-Monetisierung und Online-Business.
Du weisst wie Creator von 0 auf ihr erstes Einkommen kommen und wie sie skalieren.
Erstelle einen Monetisierungsplan in 3 Stufen:

STUFE_1_SOFORT (0-30 Tage, fuer Anfaenger):
- Produkt: [einfachstes Angebot das sofort verkauft werden kann]
- Preis: [realistischer Einstiegspreis]
- Verkaufsweg: [wie genau verkaufen - DM, Link in Bio, etc.]
- Erster_Umsatz: [wie der erste Euro verdient wird - Schritt fuer Schritt]

STUFE_2_WACHSTUM (1-3 Monate):
- Produkt: [naechstes Angebot]
- Preis: [Preis]
- Ziel_Umsatz: [realistisches Monatsziel]
- Automatisierung: [was automatisiert werden kann]

STUFE_3_VIP (3-6 Monate):
- High_Ticket_Angebot: [Premium-Angebot Beschreibung]
- Preis: [High-Ticket Preis 500-5000 EUR]
- Zielgruppe: [wer kauft das]
- Akquise: [wie VIP-Kunden gewinnen]

TOOL_SYSTEM_ANGEBOT:
- Was die Agentur/Tool anbietet: [konkretes Angebot fuer Creator]
- Preis_Modell: [monatlich / einmalig / prozentual]
- USP: [warum bei dieser Agentur/Tool und nicht woanders]"""


def erstelle_plan(nische: str, follower_total: str, profil_analyse: str,
                  model: str, temp: float = 0.7) -> str:
    prompt = f"""Creator-Daten:
- Nische: {nische}
- Follower gesamt: {follower_total}
- Profil-Analyse: {profil_analyse[:300]}

Erstelle den vollstaendigen Monetisierungsplan in 3 Stufen."""

    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": SYSTEM, "prompt": prompt,
            "stream": False, "options": {"temperature": temp},
        }, timeout=180)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        print("[FEHLER] Kein Ollama.")
        sys.exit(1)
