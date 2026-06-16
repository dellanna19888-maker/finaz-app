"""
brand.py – Modul D: Personal Brand / Newsletter
Agenten: ContentTransformer → NewsletterWriter → EngagementAgent
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

SYSTEM_CONTENT_TRANSFORMER = """Du bist ein Content-Stratege für Personal Brands (deutschsprachiger Markt).
Verwandle eine Idee in drei Formate:
LINKEDIN-POST: 3–5 Absätze, professionell, endet mit Frage an die Community. Kein Hashtag-Spam (max. 3).
INSTAGRAM-CAPTION: prägnant, emotional, endet mit CTA. 5 relevante Hashtags inkl. #Werbung.
X-THREAD: 3 Tweets (Tweet 1: Hook, Tweet 2: Kern-Insight, Tweet 3: Fazit + CTA).
Stil: authentisch, direkt, kein Corporate-Speak."""

SYSTEM_NEWSLETTER_WRITER = """Du bist ein Newsletter-Texter für Personal Brands.
Erstelle einen wöchentlichen Newsletter:
BETREFF: neugierig machend, max. 50 Zeichen
HOOK: erster Satz der sofort fesselt
HAUPTTEIL: 3 Punkte / Insights (je 2–3 Sätze)
CTA: eine klare Handlungsaufforderung
PS: persönliche Randnotiz oder Bonus-Tipp
Länge gesamt: ca. 250–350 Wörter. Kein Spam-Sprache."""

SYSTEM_ENGAGEMENT_AGENT = """Du bist ein Community-Manager für Personal Brands.
Erstelle 5 Antwort-Vorlagen für Kommentare:
POSITIV: Dankbare, persönliche Antwort auf ein Lob
FRAGE: Hilfreiche Antwort auf eine inhaltliche Frage
KRITIK: Professionelle, deeskalierende Antwort auf sachliche Kritik
SPAM/WERBUNG: Freundliche aber klare Ablehnung
KOOPERATIONSANFRAGE: Offene, nicht-bindende Antwort
Jede Vorlage max. 2–3 Sätze. Authentisch, menschlich."""


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


def run(idee: str, model: str = DEFAULT_MODEL) -> None:
    block = []

    print("\n[ContentTransformer] Erstelle Multi-Format-Content ...")
    content = _ask(SYSTEM_CONTENT_TRANSFORMER, f"Idee/Thema der Woche: {idee}", model, 0.85)
    print(content)
    block.append("--- MULTI-FORMAT CONTENT ---\n" + content)

    print("\n[NewsletterWriter] Erstelle Newsletter ...")
    newsletter = _ask(SYSTEM_NEWSLETTER_WRITER, f"Thema: {idee}", model, 0.8)
    print(newsletter)
    block.append("--- NEWSLETTER ---\n" + newsletter)

    print("\n[EngagementAgent] Erstelle Antwort-Vorlagen ...")
    engagement = _ask(SYSTEM_ENGAGEMENT_AGENT, f"Kanal-Thema: {idee}", model, 0.7)
    print(engagement)
    block.append("--- ANTWORT-VORLAGEN ---\n" + engagement)

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    pfad = OUTPUT_DIR / f"brand_{ts}.txt"
    pfad.write_text(f"IDEE: {idee}\n\n" + "\n\n".join(block), encoding="utf-8")
    print(f"\nFERTIG – gespeichert in: {pfad}")


if __name__ == "__main__":
    idee = input("Idee / Thema der Woche: ").strip()
    run(idee)
