import re
from pathlib import Path

BLOCKLIST_PATH = Path(__file__).parent / "blocklist.txt"

SUPERLATIVES = ["besten", "schnellsten", "einfachsten", "sichersten", "garantiert"]
AD_LABEL_REQUIRED = ["werbung", "anzeige", "ad", "sponsored", "#ad", "#werbung"]
PARAGRAPH_34F_SIGNALS = ["§34f", "anlageberatung", "finanzberatung", "wertpapierberatung"]


def _load_blocklist() -> list[str]:
    if not BLOCKLIST_PATH.exists():
        return []
    return [line.strip().lower() for line in BLOCKLIST_PATH.read_text().splitlines() if line.strip()]


def check(content: dict) -> dict:
    """
    Prüft hook, script, caption, hashtags gegen Compliance-Regeln.
    Gibt {'status': 'OK'|'BLOCKIERT', 'gruende': [...]} zurück.
    """
    blocklist = _load_blocklist()
    gruende = []

    fields = {
        "hook": content.get("hook", ""),
        "script": content.get("script", ""),
        "caption": content.get("caption", ""),
        "hashtags": " ".join(content.get("hashtags", [])),
    }

    full_text = " ".join(fields.values()).lower()

    for word in blocklist:
        if word in full_text:
            gruende.append(f"Verbotenes Wort gefunden: '{word}'")

    for signal in PARAGRAPH_34F_SIGNALS:
        if signal in full_text:
            gruende.append(f"§34f-Signal gefunden: '{signal}'")

    for sup in SUPERLATIVES:
        if sup in full_text:
            gruende.append(f"Superlativ gefunden: '{sup}'")

    caption_lower = fields["caption"].lower()
    hashtag_lower = fields["hashtags"].lower()
    has_ad_label = any(label in caption_lower or label in hashtag_lower for label in AD_LABEL_REQUIRED)
    if not has_ad_label:
        gruende.append("Fehlende Werbekennzeichnung (Werbung/Anzeige/#ad fehlt)")

    status = "BLOCKIERT" if gruende else "OK"
    return {"status": status, "gruende": gruende}
