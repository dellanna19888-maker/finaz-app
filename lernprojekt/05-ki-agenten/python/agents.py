"""
============================================================
 Social-Media-Content-Team  (Python)
============================================================
Ein Team aus VIER KI-Agenten erstellt Content für Social Media
(Instagram, TikTok & Co.) – mit frischen Ideen UND auf Basis der
neuesten Plattform-Regeln und Gesetze:

  1. 🔎 Trend- & Regel-Rechercheur -> sucht im Web nach aktuellen Trends,
        den neuesten Plattform-Richtlinien und relevanten Gesetzen
  2. 💡 Ideen-Agent   -> entwickelt frische Content-Ideen
  3. ✍️  Content-Agent -> schreibt einen fertigen Post (Hook, Skript, Hashtags)
  4. ✅ Compliance-Lektor -> verbessert und prüft auf Regelkonformität

Die Funktion main() ist der "Orchestrator": Sie ruft die Agenten der Reihe
nach auf und reicht die Ergebnisse weiter.

Start:  python agents.py "<Nische>" "<Plattform>"
Bsp.:   python agents.py "Fitness für Anfänger" "TikTok"
"""

import os
import sys

from anthropic import Anthropic
from dotenv import load_dotenv

# Liest ANTHROPIC_API_KEY aus einer .env-Datei (falls vorhanden).
load_dotenv()

# Ein einziger Client für alle Agenten.
# Der Schlüssel wird automatisch aus ANTHROPIC_API_KEY gelesen.
client = Anthropic()

# Das Modell zentral festlegen, damit man es leicht ändern kann.
# Tipp: "claude-haiku-4-5" ist günstiger und schneller zum Experimentieren.
MODELL = "claude-opus-4-8"

# Die Web-Suche sorgt dafür, dass der Rechercheur die NEUESTEN Regeln und
# Trends findet. Sie ist ein serverseitiges Werkzeug von Anthropic und
# verursacht geringe Zusatzkosten. Falls dein Konto sie (noch) nicht
# unterstützt, setze dies auf False – dann nutzt der Agent sein vorhandenes
# Wissen statt der Live-Suche.
WEB_SUCHE_AKTIV = True
WEB_SUCH_WERKZEUG = {"type": "web_search_20260209", "name": "web_search"}


def frage_agent(system_prompt: str, aufgabe: str, werkzeuge=None) -> str:
    """
    Ruft EINEN Agenten auf und gibt seinen Antworttext zurück.

    - system_prompt: beschreibt, WER der Agent ist (seine Rolle).
    - aufgabe:       die konkrete Eingabe, WAS er tun soll.
    - werkzeuge:     optionale Werkzeuge (z.B. die Web-Suche).
    """
    nachrichten = [{"role": "user", "content": aufgabe}]

    # Bei der Web-Suche kann Claude mehrere Runden brauchen. "pause_turn"
    # bedeutet: die Suche läuft serverseitig noch weiter -> wir setzen fort.
    for _ in range(6):
        antwort = client.messages.create(
            model=MODELL,
            max_tokens=4000,
            system=system_prompt,
            thinking={"type": "adaptive"},        # Claude denkt bei Bedarf selbst nach
            output_config={"effort": "medium"},   # Qualität vs. Kosten: low | medium | high | max
            tools=werkzeuge or [],
            messages=nachrichten,
        )
        if antwort.stop_reason == "pause_turn":
            nachrichten.append({"role": "assistant", "content": antwort.content})
            continue
        break

    # Die Antwort besteht aus "Blöcken" (Denk-Block, Suchergebnisse, Text ...).
    # Wir sammeln nur den sichtbaren Text aus den "text"-Blöcken.
    return "".join(block.text for block in antwort.content if block.type == "text")


# --- Die vier Agenten -----------------------------------------------------

def trend_und_regel_rechercheur(nische: str, plattform: str) -> str:
    """Agent 1: sucht aktuelle Trends, Plattform-Regeln und Gesetze (mit Web-Suche)."""
    system = (
        "Du bist ein Social-Media-Analyst. Du recherchierst gründlich und nutzt "
        "die Web-Suche, um IMMER die neuesten Informationen zu finden. "
        "Du gibst ein kompaktes Briefing auf Deutsch mit Stichpunkten und nennst, "
        "wann/woher die Infos stammen."
    )
    aufgabe = (
        f"Recherchiere für die Nische '{nische}' auf der Plattform {plattform}:\n"
        f"1) aktuelle Trends und beliebte Formate,\n"
        f"2) die neuesten Community-Richtlinien der Plattform,\n"
        f"3) relevante rechtliche Regeln (z.B. Werbekennzeichnung, Urheberrecht, "
        f"Jugendschutz, Datenschutz).\n"
        f"Gib ein kompaktes Briefing mit Stichpunkten und Quellen."
    )
    werkzeuge = [WEB_SUCH_WERKZEUG] if WEB_SUCHE_AKTIV else None
    return frage_agent(system, aufgabe, werkzeuge)


def ideen_agent(nische: str, plattform: str, briefing: str) -> str:
    """Agent 2: entwickelt frische Content-Ideen."""
    system = (
        "Du bist ein kreativer Social-Media-Ideengeber. Du lieferst frische, "
        "originelle Content-Ideen, die zu aktuellen Trends passen und die Regeln "
        "einhalten."
    )
    aufgabe = (
        f"Entwickle 5 frische Content-Ideen für die Nische '{nische}' auf {plattform}. "
        f"Berücksichtige dieses Briefing (Trends + Regeln):\n\n{briefing}\n\n"
        f"Gib pro Idee: einen Titel, das Format (z.B. Reel, Story, Karussell) und "
        f"den Aufhänger (Hook)."
    )
    return frage_agent(system, aufgabe)


def content_agent(plattform: str, ideen: str) -> str:
    """Agent 3: schreibt aus der besten Idee einen fertigen Post."""
    system = (
        "Du bist ein erfahrener Social-Media-Content-Creator. Du schreibst fertige "
        "Posts im Stil der jeweiligen Plattform: ein starker Hook, ein kurzes Skript "
        "bzw. eine Caption und passende Hashtags."
    )
    aufgabe = (
        f"Wähle die beste der folgenden Ideen und erstelle daraus einen fertigen "
        f"Post für {plattform}:\n"
        f"- einen Hook (die ersten 3 Sekunden / die erste Zeile),\n"
        f"- ein kurzes Skript bzw. eine Caption,\n"
        f"- 5 bis 10 passende Hashtags.\n\n"
        f"Ideen:\n{ideen}"
    )
    return frage_agent(system, aufgabe)


def compliance_lektor(post: str, briefing: str) -> str:
    """Agent 4: verbessert den Post und prüft ihn gegen die Regeln/Gesetze."""
    system = (
        "Du bist Lektor und Compliance-Prüfer für Social Media. Du verbesserst den "
        "Text in Stil und Klarheit UND prüfst ihn gegen die genannten Regeln und "
        "Gesetze (z.B. korrekte Werbekennzeichnung). Gib zuerst den finalen, "
        "regelkonformen Post zurück, danach eine kurze Checkliste der beachteten Regeln."
    )
    aufgabe = (
        f"Hier sind die geltenden Regeln (aus dem Briefing):\n\n{briefing}\n\n"
        f"Überarbeite und prüfe diesen Post auf Regelkonformität:\n\n{post}"
    )
    return frage_agent(system, aufgabe)


# --- Der Orchestrator -----------------------------------------------------

def main() -> None:
    # Ohne Schlüssel können wir die API nicht aufrufen -> freundlich hinweisen.
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠️  Kein API-Schlüssel gefunden!")
        print("    Bitte lege eine .env-Datei mit ANTHROPIC_API_KEY an.")
        print("    (Siehe README.md, Schritt 1 und 2.)")
        sys.exit(1)

    # Nische und Plattform aus der Kommandozeile lesen (mit Standardwerten).
    args = sys.argv[1:]
    nische = args[0] if len(args) >= 1 else "Gesunde Ernährung"
    plattform = args[1] if len(args) >= 2 else "Instagram und TikTok"

    print(f"\n🎯 Nische: {nische}")
    print(f"📱 Plattform: {plattform}\n")

    print("🔎 Agent 1 (Trend- & Regel-Rechercheur) sucht im Web ...")
    briefing = trend_und_regel_rechercheur(nische, plattform)
    print(briefing + "\n")

    print("💡 Agent 2 (Ideen-Agent) sammelt Ideen ...")
    ideen = ideen_agent(nische, plattform, briefing)
    print(ideen + "\n")

    print("✍️  Agent 3 (Content-Agent) schreibt den Post ...")
    post = content_agent(plattform, ideen)
    print(post + "\n")

    print("✅ Agent 4 (Compliance-Lektor) prüft die Regeln ...")
    fertig = compliance_lektor(post, briefing)
    print(fertig + "\n")

    # Das Endergebnis als Markdown-Datei speichern.
    os.makedirs("output", exist_ok=True)
    dateiname = os.path.join("output", "social-media-post.md")
    with open(dateiname, "w", encoding="utf-8") as f:
        f.write(f"# {nische} – {plattform}\n\n{fertig}\n")

    print(f"✅ Fertig! Der Post wurde gespeichert in: {dateiname}")


if __name__ == "__main__":
    main()
