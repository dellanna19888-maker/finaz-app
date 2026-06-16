"""
crm.py – CRM locale per la gestione dei lead.
Database: SQLite (nessuna dipendenza esterna).

Comandi:
  python3 crm.py add        – aggiungere un lead
  python3 crm.py list       – lista tutti i lead
  python3 crm.py update ID  – aggiornare stato di un lead
  python3 crm.py followup   – mostra lead con follow-up oggi
  python3 crm.py stats      – statistiche generali
  python3 crm.py note ID    – aggiungere nota a un lead
"""
import argparse
import sqlite3
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "output" / "crm.db"
DB_PATH.parent.mkdir(exist_ok=True)

STATI = ["nuovo", "kontaktiert", "interessiert", "angebot", "kunde", "verloren"]
QUELLEN = ["instagram", "tiktok", "linkedin", "email", "empfehlung", "website", "sonstige"]


def _conn() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS leads (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        email       TEXT,
        telefon     TEXT,
        interesse   TEXT,
        quelle      TEXT DEFAULT 'sonstige',
        status      TEXT DEFAULT 'neu',
        followup    TEXT,
        erstellt    TEXT DEFAULT (date('now')),
        notizen     TEXT DEFAULT ''
    )""")
    con.commit()
    return con


def _status_icon(s: str) -> str:
    return {"neu": "🆕", "kontaktiert": "📬", "interessiert": "🔥",
            "angebot": "💼", "kunde": "✅", "verloren": "❌"}.get(s, "•")


def cmd_add() -> None:
    print("\n── Neuen Lead hinzufügen ──")
    name = input("Name: ").strip()
    if not name:
        print("[FEHLER] Name ist Pflichtfeld.")
        return
    email = input("E-Mail (optional): ").strip()
    telefon = input("Telefon (optional): ").strip()
    interesse = input("Interesse / Produkt: ").strip()

    print(f"Quelle {QUELLEN}: ")
    quelle = input("Quelle: ").strip().lower() or "sonstige"
    if quelle not in QUELLEN:
        quelle = "sonstige"

    tage = input("Follow-up in X Tagen (Enter = 3): ").strip()
    tage = int(tage) if tage.isdigit() else 3
    followup = (date.today() + timedelta(days=tage)).isoformat()

    with _conn() as con:
        cur = con.execute(
            "INSERT INTO leads (name, email, telefon, interesse, quelle, status, followup) VALUES (?,?,?,?,?,?,?)",
            (name, email, telefon, interesse, quelle, "neu", followup)
        )
        lid = cur.lastrowid
    print(f"\n✅ Lead #{lid} '{name}' gespeichert. Follow-up: {followup}")


def cmd_list(filter_status: str = "") -> None:
    with _conn() as con:
        if filter_status:
            rows = con.execute("SELECT * FROM leads WHERE status=? ORDER BY followup", (filter_status,)).fetchall()
        else:
            rows = con.execute("SELECT * FROM leads ORDER BY followup, id").fetchall()

    if not rows:
        print("Keine Leads gefunden.")
        return

    print(f"\n{'ID':<4} {'Name':<20} {'Status':<14} {'Follow-up':<12} {'Quelle':<12} {'Interesse'}")
    print("─" * 80)
    for r in rows:
        icon = _status_icon(r["status"])
        fu = r["followup"] or "—"
        today = date.today().isoformat()
        marker = " ◄" if fu <= today and r["status"] not in ("kunde", "verloren") else ""
        print(f"{r['id']:<4} {r['name']:<20} {icon} {r['status']:<12} {fu:<12} {r['quelle']:<12} {r['interesse']}{marker}")
    print(f"\nTotal: {len(rows)} Lead(s)")


def cmd_update(lid: int) -> None:
    with _conn() as con:
        row = con.execute("SELECT * FROM leads WHERE id=?", (lid,)).fetchone()
        if not row:
            print(f"[FEHLER] Lead #{lid} nicht gefunden.")
            return

        print(f"\nLead #{lid}: {row['name']} – aktuell: {row['status']}")
        print(f"Verfügbare Status: {', '.join(STATI)}")
        neuer_status = input("Neuer Status: ").strip().lower()
        if neuer_status not in STATI:
            print(f"[FEHLER] Ungültiger Status.")
            return

        tage = input("Follow-up neu setzen in X Tagen (Enter = überspringen): ").strip()
        if tage.isdigit():
            followup = (date.today() + timedelta(days=int(tage))).isoformat()
            con.execute("UPDATE leads SET status=?, followup=? WHERE id=?", (neuer_status, followup, lid))
        else:
            con.execute("UPDATE leads SET status=? WHERE id=?", (neuer_status, lid))
        con.commit()
    print(f"✅ Lead #{lid} aktualisiert → {neuer_status}")


def cmd_note(lid: int) -> None:
    with _conn() as con:
        row = con.execute("SELECT * FROM leads WHERE id=?", (lid,)).fetchone()
        if not row:
            print(f"[FEHLER] Lead #{lid} nicht gefunden.")
            return
        print(f"\nAktuelle Notizen für {row['name']}:\n{row['notizen'] or '(leer)'}")
        neue_notiz = input("\nNeue Notiz hinzufügen: ").strip()
        if neue_notiz:
            ts = datetime.now().strftime("%d.%m.%Y %H:%M")
            combined = f"{row['notizen']}\n[{ts}] {neue_notiz}".strip()
            con.execute("UPDATE leads SET notizen=? WHERE id=?", (combined, lid))
            con.commit()
            print("✅ Notiz gespeichert.")


def cmd_followup() -> None:
    today = date.today().isoformat()
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM leads WHERE followup <= ? AND status NOT IN ('kunde','verloren') ORDER BY followup",
            (today,)
        ).fetchall()

    if not rows:
        print("✅ Keine offenen Follow-ups heute.")
        return

    print(f"\n🔔 Follow-ups fällig ({len(rows)}):\n")
    for r in rows:
        print(f"  #{r['id']} {r['name']} ({r['quelle']}) – {r['interesse']}")
        print(f"      Status: {r['status']} | Follow-up war: {r['followup']}")
        if r["notizen"]:
            letzte = r["notizen"].strip().split("\n")[-1]
            print(f"      Letzte Notiz: {letzte}")
        print()


def cmd_stats() -> None:
    with _conn() as con:
        total = con.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        by_status = con.execute("SELECT status, COUNT(*) as n FROM leads GROUP BY status").fetchall()
        by_quelle = con.execute("SELECT quelle, COUNT(*) as n FROM leads GROUP BY quelle ORDER BY n DESC").fetchall()
        heute = con.execute(
            "SELECT COUNT(*) FROM leads WHERE followup <= ? AND status NOT IN ('kunde','verloren')",
            (date.today().isoformat(),)
        ).fetchone()[0]

    print(f"\n── CRM Statistiken ──")
    print(f"Total Leads: {total}")
    print(f"Follow-ups fällig: {heute}")
    print("\nNach Status:")
    for r in by_status:
        icon = _status_icon(r["status"])
        print(f"  {icon} {r['status']:<14} {r['n']}")
    print("\nNach Quelle:")
    for r in by_quelle:
        print(f"  {r['quelle']:<14} {r['n']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="FinAz CRM – Lead-Verwaltung")
    parser.add_argument("cmd", choices=["add", "list", "update", "followup", "stats", "note"],
                        help="Kommando")
    parser.add_argument("id", nargs="?", type=int, help="Lead-ID (für update/note)")
    parser.add_argument("-s", "--status", help="Filter nach Status (für list)")
    args = parser.parse_args()

    if args.cmd == "add":
        cmd_add()
    elif args.cmd == "list":
        cmd_list(args.status or "")
    elif args.cmd == "update":
        if not args.id:
            print("[FEHLER] ID erforderlich: python3 crm.py update 5")
            sys.exit(1)
        cmd_update(args.id)
    elif args.cmd == "note":
        if not args.id:
            print("[FEHLER] ID erforderlich: python3 crm.py note 5")
            sys.exit(1)
        cmd_note(args.id)
    elif args.cmd == "followup":
        cmd_followup()
    elif args.cmd == "stats":
        cmd_stats()


if __name__ == "__main__":
    main()
