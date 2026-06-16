#!/usr/bin/env python3
"""
business_master.py – Master-Controller für das Online-Business Multi-Agenten-System.

Module:
  A) Shop / E-Commerce   – ProductWriter + FAQBot + ShopCompliance
  B) Coaching            – EmailSequence + CourseOutliner + SalesFollowUp
  C) Affiliate           – ReviewWriter + SEOOptimizer + AffiliateCompliance
  D) Personal Brand      – ContentTransformer + Newsletter + EngagementAgent

Nutzung:
  python3 business_master.py                     # interaktives Menü
  python3 business_master.py a "Produktname"
  python3 business_master.py b "Coaching-Nische"
  python3 business_master.py c "Produkt" "Nische"
  python3 business_master.py d "Idee der Woche"
  python3 business_master.py a "Produkt" -m tinyllama
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

DEFAULT_MODEL = "qwen2.5:3b"

MENU = """
╔══════════════════════════════════════════╗
║   FinAz Online-Business Agenten v1.0    ║
╠══════════════════════════════════════════╣
║  A) Shop / E-Commerce                   ║
║  B) Coaching / Infoprodotti             ║
║  C) Affiliate Marketing                 ║
║  D) Personal Brand / Newsletter         ║
╚══════════════════════════════════════════╝
"""


def run_shop(args_list: list[str], model: str) -> None:
    from business.shop import run
    produkt = args_list[0] if args_list else input("Produktname: ").strip()
    beschreibung = args_list[1] if len(args_list) > 1 else input("Kurzbeschreibung (optional): ").strip()
    run(produkt, beschreibung, model)


def run_coaching(args_list: list[str], model: str) -> None:
    from business.coaching import run
    nische = args_list[0] if args_list else input("Coaching-Nische / Thema: ").strip()
    run(nische, model)


def run_affiliate(args_list: list[str], model: str) -> None:
    from business.affiliate import run
    produkt = args_list[0] if args_list else input("Produktname: ").strip()
    nische = args_list[1] if len(args_list) > 1 else input("Nische (optional): ").strip()
    run(produkt, nische, model)


def run_brand(args_list: list[str], model: str) -> None:
    from business.brand import run
    idee = args_list[0] if args_list else input("Idee / Thema der Woche: ").strip()
    run(idee, model)


MODULES = {
    "a": ("Shop / E-Commerce", run_shop),
    "b": ("Coaching / Infoprodotti", run_coaching),
    "c": ("Affiliate Marketing", run_affiliate),
    "d": ("Personal Brand / Newsletter", run_brand),
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="FinAz Online-Business Master-Controller"
    )
    parser.add_argument("modul", nargs="?", choices=list(MODULES.keys()),
                        help="Modul: a=Shop, b=Coaching, c=Affiliate, d=Brand")
    parser.add_argument("inputs", nargs="*", help="Eingabe-Parameter für das Modul")
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL,
                        help=f"Ollama-Modell (Standard: {DEFAULT_MODEL})")
    args = parser.parse_args()

    print(MENU)

    modul = args.modul
    if not modul:
        modul = input("Modul wählen (a/b/c/d): ").strip().lower()

    if modul not in MODULES:
        print(f"[FEHLER] Ungültiges Modul: '{modul}'. Wähle a, b, c oder d.")
        sys.exit(1)

    name, func = MODULES[modul]
    print(f"\n→ Starte Modul: {name}")
    print(f"→ Modell: {args.model}\n")

    func(args.inputs, args.model)


if __name__ == "__main__":
    main()
