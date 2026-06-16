#!/usr/bin/env python3
"""
creator_master.py - Master-Controller fuer das Creator Growth System.

5 Agenten in Sequenz:
  1. Profil-Analyse    - Nische, Level, Staerken, Probleme
  2. Growth-Strategie  - 30-Tage-Plan TikTok + Instagram
  3. Monetisierung     - Stufe 1 (sofort) bis VIP High-Ticket
  4. Content-Plan      - 30 Ideen in 5 Kategorien
  5. Pitch Generator   - DM-Vorlagen + Salespage

Nutzung:
  python3 creator_master.py              # interaktiv
  python3 creator_master.py -m tinyllama # anderes Modell
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

DEFAULT_MODEL = "qwen2.5:3b"

BANNER = """
╔══════════════════════════════════════════════╗
║      CREATOR GROWTH SYSTEM  v1.0            ║
║      TikTok + Instagram | Agency Tool       ║
╚══════════════════════════════════════════════╝"""


def _speichern(nische: str, block: list[str]) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    safe = nische[:30].replace(" ", "_").replace("/", "-")
    pfad = OUTPUT_DIR / f"creator_{safe}_{ts}.txt"
    pfad.write_text("\n\n".join(block), encoding="utf-8")
    return pfad


def _banner(text: str) -> None:
    print(f"\n{'='*50}")
    print(f"  {text}")
    print('='*50)


def run(model: str) -> None:
    print(BANNER)

    # ── Input ──
    print("\nCreator-Daten eingeben:\n")
    nische = input("Nische / Thema des Creators: ").strip()
    if not nische:
        print("[FEHLER] Nische ist Pflichtfeld.")
        sys.exit(1)

    follower_tt = input("TikTok Follower (z.B. 1200): ").strip() or "unbekannt"
    follower_ig = input("Instagram Follower (z.B. 800): ").strip() or "unbekannt"
    posting = input("Posting-Frequenz pro Woche (z.B. 3): ").strip() or "unbekannt"
    problem = input("Groesstes Problem des Creators: ").strip() or "zu wenig Wachstum"

    angebot = input("\nDein Angebot als Agentur/Tool (z.B. 'Growth Coaching 1:1'): ").strip() or "Creator Growth Coaching"
    preis = input("Dein Preis (z.B. '297 EUR/Monat'): ").strip() or "auf Anfrage"
    zielgruppe = input("Zielgruppe (z.B. 'Creator 1k-50k Follower'): ").strip() or "Creator mit 500-50k Follower"

    block = [f"CREATOR GROWTH SYSTEM\nNische: {nische}\nTikTok: {follower_tt} | Instagram: {follower_ig}\n"]

    # ── Agent 1: Profil-Analyse ──
    _banner("AGENT 1: PROFIL-ANALYSE")
    from creator.profil_agent import analyse
    profil = analyse(nische, follower_tt, follower_ig, posting, problem, model)
    print(profil)
    block.append("=== PROFIL-ANALYSE ===\n" + profil)

    # ── Agent 2: Growth-Strategie ──
    _banner("AGENT 2: GROWTH-STRATEGIE (30 Tage)")
    from creator.growth_agent import erstelle_plan as growth_plan
    growth = growth_plan(nische, profil, model)
    print(growth)
    block.append("=== GROWTH-STRATEGIE ===\n" + growth)

    # ── Agent 3: Monetisierung ──
    _banner("AGENT 3: MONETISIERUNGS-STRATEGIE")
    from creator.monetize_agent import erstelle_plan as mono_plan
    follower_total = f"TikTok: {follower_tt}, Instagram: {follower_ig}"
    mono = mono_plan(nische, follower_total, profil, model)
    print(mono)
    block.append("=== MONETISIERUNG ===\n" + mono)

    # ── Agent 4: Content-Plan ──
    _banner("AGENT 4: CONTENT-PLAN (30 Ideen)")
    from creator.content_agent import generiere
    content = generiere(nische, growth, model)
    print(content)
    block.append("=== CONTENT-PLAN ===\n" + content)

    # ── Agent 5: Pitch Generator ──
    _banner("AGENT 5: PITCH GENERATOR")
    from creator.pitch_agent import erstelle_dm, erstelle_salespage

    print("\n[DM-Vorlagen]")
    dm = erstelle_dm(nische, angebot, preis, model)
    print(dm)
    block.append("=== DM-VORLAGEN ===\n" + dm)

    print("\n[Salespage]")
    salespage = erstelle_salespage(nische, angebot, preis, zielgruppe, model)
    print(salespage)
    block.append("=== SALESPAGE ===\n" + salespage)

    # ── Speichern ──
    pfad = _speichern(nische, block)
    print(f"\n{'='*50}")
    print(f"FERTIG - gespeichert in: {pfad}")
    print(f"{'='*50}")
    print("\nNaechste Schritte:")
    print("  cat " + str(pfad) + "  # alles lesen")
    print("  python3 crm.py add        # Creator als Lead speichern")
    print("  python3 dashboard.py      # Dashboard aktualisieren")


def main() -> None:
    parser = argparse.ArgumentParser(description="Creator Growth System")
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL,
                        help=f"Ollama-Modell (Standard: {DEFAULT_MODEL})")
    args = parser.parse_args()
    run(args.model)


if __name__ == "__main__":
    main()
