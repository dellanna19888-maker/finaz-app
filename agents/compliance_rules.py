"""
compliance_rules.py – Deterministischer Compliance-Filter.

Prüft Hook + Skript + Caption + Hashtags gegen:
  - Sperrliste (blocklist.txt, jederzeit per echo erweiterbar)
  - §34f-Signale (Finanzberatung ohne Lizenz)
  - Superlative / irreführende Versprechen
  - Werbe-Kennzeichnungspflicht

Rückgabe: {'status': 'OK'|'REVIEW'|'BLOCKIERT', 'gruende': [...], 'report': str}
"""
from pathlib import Path

_DIR = Path(__file__).parent
BLOCKLIST_PATH = _DIR / "blocklist.txt"

PARAGRAPH_34F_SIGNALS = [
    "§34f", "anlageberatung", "finanzberatung", "wertpapierberatung",
    "kapitalanlage", "vermögensverwaltung", "investmentberatung",
]

SUPERLATIVE_SIGNALS = [
    "die beste", "der beste", "das beste", "am besten",
    "am schnellsten", "am einfachsten", "am sichersten",
    "am günstigsten", "am profitabelsten",
]

AD_LABELS = ["#werbung", "#anzeige", "#ad", "#sponsored", "werbung", "anzeige"]


def _load_blocklist() -> list[str]:
    if not BLOCKLIST_PATH.exists():
        return []
    return [
        line.strip().lower()
        for line in BLOCKLIST_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]


def check(content: dict) -> dict:
    """
    content erwartet die Felder: hook, script, caption, hashtags (list).
    Hooks werden explizit mitgeprüft – das ist der rechtlich riskanteste Teil.
    """
    blocklist = _load_blocklist()
    hard_blocker = []
    review_hints = []

    hooks = content.get("hooks", [])
    if isinstance(hooks, str):
        hooks = [hooks]
    hook_text = " ".join(str(h) for h in hooks) + " " + content.get("hook", "")

    full_text = " ".join([
        hook_text,
        content.get("script", ""),
        content.get("caption", ""),
        " ".join(content.get("hashtags", [])),
    ]).lower()

    # Sperrliste
    for word in blocklist:
        if word in full_text:
            hard_blocker.append(f"Verbotenes Wort/Versprechen: '{word}'")

    # §34f-Signale → immer BLOCKIERT
    for signal in PARAGRAPH_34F_SIGNALS:
        if signal in full_text:
            hard_blocker.append(f"§34f-Signal: '{signal}'")

    # Superlative → REVIEW
    for sup in SUPERLATIVE_SIGNALS:
        if sup in full_text:
            review_hints.append(f"Superlativ prüfen: '{sup}'")

    # Werbe-Kennzeichnung
    caption_lower = content.get("caption", "").lower()
    hashtag_lower = " ".join(content.get("hashtags", [])).lower()
    has_ad_label = any(label in caption_lower or label in hashtag_lower for label in AD_LABELS)
    if not has_ad_label:
        hard_blocker.append("Fehlende Werbe-Kennzeichnung (#Werbung/#Anzeige/#ad)")

    # Urteil
    if hard_blocker:
        status = "BLOCKIERT"
    elif review_hints:
        status = "REVIEW"
    else:
        status = "OK"

    # Lesbarer Report
    lines = ["=" * 48, "DETERMINISTISCHER COMPLIANCE-CHECK", f"URTEIL: {status}"]
    if hard_blocker:
        lines.append("\nHARTE VERSTÖSSE (→ nicht veröffentlichen):")
        for b in hard_blocker:
            lines.append(f"  ✗ {b}")
    if review_hints:
        lines.append("\nZUR PRÜFUNG:")
        for h in review_hints:
            lines.append(f"  ? {h}")
    if status == "OK":
        lines.append("  ✓ Keine Verstöße gefunden.")
    lines.append("=" * 48)

    report = "\n".join(lines)
    return {"status": status, "gruende": hard_blocker + review_hints, "report": report}


if __name__ == "__main__":
    # Selbsttest
    tests = [
        {
            "name": "Harter Verstoß",
            "hook": "Garantiert 5000€ in 30 Tagen – risikofrei!",
            "script": "So wirst du schnell reich ohne Risiko.",
            "caption": "Starte heute.", "hashtags": ["#geld"],
        },
        {
            "name": "Fehlende Kennzeichnung",
            "hook": "3 Tipps für deinen Vermögensaufbau",
            "script": "Diversifikation ist der Schlüssel.",
            "caption": "Fang klein an.", "hashtags": ["#finanzen"],
        },
        {
            "name": "Sauberer Post",
            "hook": "Was Finanzfreiheit wirklich bedeutet",
            "script": "Es geht um Optionen, nicht um Reichtum.",
            "caption": "Denk langfristig. #Werbung", "hashtags": ["#Werbung", "#finanzen"],
        },
    ]
    for t in tests:
        result = check(t)
        print(f"\n[TEST: {t['name']}]")
        print(result["report"])
