"""
shop.py – Modul A: Shop / E-Commerce
Agenten: ProductWriter → FAQBot → ShopCompliance
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

SYSTEM_PRODUCT_WRITER = """Du bist ein erfahrener E-Commerce-Texter für den deutschsprachigen Markt.
Erstelle zu jedem Produkt:
TITEL: prägnanter Produkttitel (max. 80 Zeichen, SEO-optimiert)
BULLETPOINTS: 5 Vorteile als kurze Stichpunkte (je max. 1 Satz)
BESCHREIBUNG: 3–4 Sätze ausführliche Produktbeschreibung
CTA: ein klarer Kaufaufruf (1 Satz)
Kein "bestes Produkt", keine unbeweisbaren Superlative, keine Garantieversprechen."""

SYSTEM_FAQ_BOT = """Du bist ein Kundenservice-Experte für E-Commerce.
Erstelle 5 typische Kundenfragen (FAQ) mit präzisen Antworten zu einem Produkt.
Format: F: [Frage] / A: [Antwort]
Die Antworten sind ehrlich, hilfreich und rechtssicher (keine falschen Versprechen)."""

HARD_BLOCK_SHOP = [
    "garantiert beste qualität", "weltbeste", "einzigartiges produkt",
    "heilt", "kuriert", "medizinisch bewiesen", "klinisch getestet ohne belege",
    "100% zufriedenheitsgarantie ohne einschränkung",
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
        print("[FEHLER] Kein Ollama. Läuft 'ollama serve'?")
        sys.exit(1)


def _compliance_check(text: str) -> tuple[str, str]:
    found = [w for w in HARD_BLOCK_SHOP if w in text.lower()]
    has_price_condition = "zzgl" in text.lower() or "versandkosten" in text.lower() or "*" in text
    lines = ["=" * 48, "SHOP-COMPLIANCE-CHECK"]
    if found:
        for w in found:
            lines.append(f"  ✗ Problematisch: '{w}'")
        lines += ["URTEIL: BLOCKIERT", "=" * 48]
        return "BLOCKIERT", "\n".join(lines)
    lines.append("  ✓ Keine harten Verstöße")
    lines += [f"URTEIL: OK", "=" * 48]
    return "OK", "\n".join(lines)


def run(produkt: str, beschreibung: str = "", model: str = DEFAULT_MODEL) -> None:
    block = []
    prompt_input = f"Produkt: {produkt}\nKurzbeschreibung: {beschreibung}" if beschreibung else f"Produkt: {produkt}"

    print("\n[ProductWriter] Erstelle Produkttext ...")
    product_text = _ask(SYSTEM_PRODUCT_WRITER, prompt_input, model, 0.8)
    print(product_text)
    block.append("--- PRODUKTTEXT ---\n" + product_text)

    print("\n[FAQBot] Erstelle FAQ ...")
    faq_text = _ask(SYSTEM_FAQ_BOT, prompt_input, model, 0.7)
    print(faq_text)
    block.append("--- FAQ ---\n" + faq_text)

    print("\n[ShopCompliance] Prüfe ...")
    urteil, report = _compliance_check(product_text + " " + faq_text)
    print(report)
    block.append(report)

    if urteil == "BLOCKIERT":
        block.append("🛑 STOPP – Manuell prüfen, nicht veröffentlichen.")

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    pfad = OUTPUT_DIR / f"shop_{ts}.txt"
    pfad.write_text(f"PRODUKT: {produkt}\n\n" + "\n\n".join(block), encoding="utf-8")
    print(f"\nFERTIG – gespeichert in: {pfad}")


if __name__ == "__main__":
    produkt = input("Produktname: ").strip()
    beschreibung = input("Kurzbeschreibung (optional, Enter überspringen): ").strip()
    run(produkt, beschreibung)
