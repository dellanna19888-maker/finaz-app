"""
affiliate.py – Modul C: Affiliate Marketing
Agenten: ReviewWriter → SEOOptimizer → AffiliateCompliance
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:3b"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

SYSTEM_REVIEW_WRITER = """Du bist ein ehrlicher Produkttester und Affiliate-Blogger (deutschsprachiger Markt).
Schreibe eine ausgewogene Produktrezension:
INTRO: Warum du das Produkt getestet hast (2 Sätze)
VORTEILE: 3 konkrete Pluspunkte
NACHTEILE: 2 ehrliche Minuspunkte
FÜR WEN: Für wen ist das Produkt geeignet / nicht geeignet?
FAZIT: Empfehlung in 2 Sätzen
OFFENLEGUNG: *Dieser Beitrag enthält Affiliate-Links. Bei einem Kauf erhalte ich eine Provision ohne Mehrkosten für dich.*
Keine übertriebenen Superlative. Kein "bestes Produkt aller Zeiten"."""

SYSTEM_SEO_OPTIMIZER = """Du bist ein SEO-Experte für Affiliate-Content.
Erstelle für einen Blogartikel zur Produktrezension:
KEYWORDS: 10 relevante Suchbegriffe (Haupt-Keyword zuerst, Long-Tail-Keywords darunter)
META-TITEL: max. 60 Zeichen, enthält Haupt-Keyword
META-BESCHREIBUNG: max. 155 Zeichen, enthält Haupt-Keyword + CTA
H1-VORSCHLAG: Überschrift für den Artikel
URL-SLUG: SEO-freundliche URL"""

SYSTEM_AFFILIATE_COMPLIANCE = """Du bist ein Compliance-Prüfer für Affiliate-Marketing-Content.
Prüfe den Text auf:
1. Vorhandensein der Affiliate-Offenlegung (Pflicht nach §5a UWG)
2. Keine unzulässigen Gesundheits-/Finanzversprechen
3. Keine irreführenden Preisangaben
4. Keine falschen "Testsieger"/"Nr. 1"-Claims ohne Quelle
Antworte mit: URTEIL: FREIGABE | KORREKTUR | BLOCKIERT + BEGRÜNDUNG"""

HARD_BLOCK_AFFILIATE = [
    "heilt", "kuriert", "behandelt krankheiten", "medizinisch bewiesen",
    "garantierte rendite", "risikofrei investieren", "testsieger ohne quelle",
]


def _ask(system: str, prompt: str, model: str, temp: float) -> str:
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": model, "system": system, "prompt": prompt,
            "stream": False, "options": {"temperature": temp},
        }, timeout=180)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        print("[FEHLER] Kein Ollama.")
        sys.exit(1)


def _compliance_check(text: str, gate_output: str) -> tuple[str, str]:
    found = [w for w in HARD_BLOCK_AFFILIATE if w in text.lower()]
    has_disclosure = any(w in text.lower() for w in ["affiliate", "provision", "werbelink", "*dieser beitrag"])
    lines = ["=" * 48, "AFFILIATE-COMPLIANCE-CHECK"]
    if found:
        for w in found:
            lines.append(f"  ✗ Verboten: '{w}'")
        lines += ["URTEIL: BLOCKIERT", "=" * 48]
        return "BLOCKIERT", "\n".join(lines)
    if not has_disclosure:
        lines.append("  ✗ Affiliate-Offenlegung fehlt (§5a UWG)")
        lines += ["URTEIL: BLOCKIERT", "=" * 48]
        return "BLOCKIERT", "\n".join(lines)
    lines += ["  ✓ Offenlegung vorhanden", "  ✓ Keine harten Verstöße", "URTEIL: OK", "=" * 48]
    return "OK", "\n".join(lines)


def run(produkt: str, nische: str = "", model: str = DEFAULT_MODEL) -> None:
    block = []
    prompt_input = f"Produkt: {produkt}" + (f"\nNische: {nische}" if nische else "")

    print("\n[ReviewWriter] Erstelle Produktrezension ...")
    review = _ask(SYSTEM_REVIEW_WRITER, prompt_input, model, 0.8)
    print(review)
    block.append("--- REZENSION ---\n" + review)

    print("\n[SEOOptimizer] Optimiere für Suchmaschinen ...")
    seo = _ask(SYSTEM_SEO_OPTIMIZER, prompt_input, model, 0.3)
    print(seo)
    block.append("--- SEO ---\n" + seo)

    print("\n[AffiliateCompliance] Prüfe Compliance ...")
    gate = _ask(SYSTEM_AFFILIATE_COMPLIANCE, review, model, 0.2)
    urteil, report = _compliance_check(review, gate)
    print(report)
    block.append("--- GATEKEEPER ---\n" + gate)
    block.append(report)

    if urteil == "BLOCKIERT":
        block.append("🛑 STOPP – Manuell prüfen, nicht veröffentlichen.")

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    pfad = OUTPUT_DIR / f"affiliate_{ts}.txt"
    pfad.write_text(f"PRODUKT: {produkt}\n\n" + "\n\n".join(block), encoding="utf-8")
    print(f"\nFERTIG – gespeichert in: {pfad}")


if __name__ == "__main__":
    produkt = input("Produktname: ").strip()
    nische = input("Nische (optional): ").strip()
    run(produkt, nische)
