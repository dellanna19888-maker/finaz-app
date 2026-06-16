"""
dashboard.py – Genera una Dashboard HTML con tutti i risultati e le statistiche CRM.

Apri il file generato nel browser del telefono:
  python3 dashboard.py
  → apri output/dashboard.html nel browser
"""
import json
import sqlite3
from datetime import date, datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
DB_PATH = OUTPUT_DIR / "crm.db"
DASHBOARD_PATH = OUTPUT_DIR / "dashboard.html"


def _load_crm() -> dict:
    if not DB_PATH.exists():
        return {"total": 0, "by_status": {}, "by_quelle": {}, "followups": 0, "leads": []}
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    total = con.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    by_status = {r[0]: r[1] for r in con.execute("SELECT status, COUNT(*) FROM leads GROUP BY status")}
    by_quelle = {r[0]: r[1] for r in con.execute("SELECT quelle, COUNT(*) FROM leads GROUP BY quelle")}
    followups = con.execute(
        "SELECT COUNT(*) FROM leads WHERE followup <= ? AND status NOT IN ('kunde','verloren')",
        (date.today().isoformat(),)
    ).fetchone()[0]
    leads = [dict(r) for r in con.execute("SELECT * FROM leads ORDER BY followup LIMIT 20")]
    con.close()
    return {"total": total, "by_status": by_status, "by_quelle": by_quelle,
            "followups": followups, "leads": leads}


def _load_content_files() -> list[dict]:
    files = []
    for f in sorted(OUTPUT_DIR.glob("*.txt"), reverse=True)[:20]:
        try:
            text = f.read_text(encoding="utf-8")
            first_line = text.split("\n")[0][:80]
            files.append({
                "name": f.name,
                "label": first_line,
                "date": datetime.fromtimestamp(f.stat().st_mtime).strftime("%d.%m.%Y %H:%M"),
                "size": f"{f.stat().st_size // 1024 + 1} KB",
                "type": f.stem.split("_")[0],
                "preview": text[:400].replace("<", "&lt;").replace(">", "&gt;"),
            })
        except Exception:
            continue
    return files


def _status_color(s: str) -> str:
    return {"neu": "#6c757d", "kontaktiert": "#0d6efd", "interessiert": "#fd7e14",
            "angebot": "#6f42c1", "kunde": "#198754", "verloren": "#dc3545"}.get(s, "#aaa")


def _type_color(t: str) -> str:
    return {"ergebnisse": "#6f42c1", "content": "#6f42c1", "shop": "#0d6efd",
            "coaching": "#198754", "affiliate": "#fd7e14", "brand": "#e91e63",
            "lead": "#17a2b8"}.get(t, "#6c757d")


def generate() -> Path:
    crm = _load_crm()
    files = _load_content_files()
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    status_bars = ""
    stati_all = ["neu", "kontaktiert", "interessiert", "angebot", "kunde", "verloren"]
    for s in stati_all:
        n = crm["by_status"].get(s, 0)
        pct = round(n / crm["total"] * 100) if crm["total"] else 0
        color = _status_color(s)
        status_bars += f"""
        <div class="stat-row">
          <span class="stat-label">{s}</span>
          <div class="bar-wrap"><div class="bar" style="width:{pct}%;background:{color}"></div></div>
          <span class="stat-n">{n}</span>
        </div>"""

    leads_rows = ""
    for l in crm["leads"]:
        color = _status_color(l.get("status", ""))
        fu = l.get("followup") or "—"
        overdue = fu != "—" and fu <= date.today().isoformat() and l.get("status") not in ("kunde", "verloren")
        fu_cell = f'<span class="overdue">{fu} ◄</span>' if overdue else fu
        leads_rows += f"""
        <tr>
          <td>{l['id']}</td>
          <td><strong>{l['name']}</strong><br><small>{l.get('email','')}</small></td>
          <td><span class="badge" style="background:{color}">{l.get('status','')}</span></td>
          <td>{l.get('interesse','')}</td>
          <td>{l.get('quelle','')}</td>
          <td>{fu_cell}</td>
        </tr>"""

    content_cards = ""
    for f in files:
        color = _type_color(f["type"])
        content_cards += f"""
        <div class="card">
          <div class="card-header" style="border-left:4px solid {color}">
            <span class="badge" style="background:{color}">{f['type']}</span>
            <strong>{f['label']}</strong>
            <span class="meta">{f['date']} · {f['size']}</span>
          </div>
          <pre class="preview">{f['preview']}…</pre>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FinAz Dashboard</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: system-ui, sans-serif; background: #0f0f13; color: #e0e0e0; padding: 16px; }}
  h1 {{ font-size: 1.4rem; color: #fff; margin-bottom: 4px; }}
  .sub {{ color: #888; font-size: .85rem; margin-bottom: 20px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px,1fr)); gap: 12px; margin-bottom: 24px; }}
  .kpi {{ background: #1a1a24; border-radius: 10px; padding: 16px; text-align: center; }}
  .kpi .n {{ font-size: 2rem; font-weight: 700; color: #fff; }}
  .kpi .label {{ font-size: .8rem; color: #888; margin-top: 4px; }}
  .kpi.alert .n {{ color: #fd7e14; }}
  section {{ margin-bottom: 28px; }}
  h2 {{ font-size: 1rem; color: #bbb; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px; }}
  .stat-row {{ display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }}
  .stat-label {{ width: 110px; font-size: .85rem; color: #bbb; }}
  .bar-wrap {{ flex: 1; background: #2a2a38; border-radius: 4px; height: 10px; }}
  .bar {{ height: 10px; border-radius: 4px; min-width: 4px; }}
  .stat-n {{ width: 24px; text-align: right; font-size: .85rem; color: #888; }}
  table {{ width: 100%; border-collapse: collapse; font-size: .85rem; }}
  th {{ text-align: left; color: #888; border-bottom: 1px solid #2a2a38; padding: 8px 6px; }}
  td {{ padding: 8px 6px; border-bottom: 1px solid #1a1a24; vertical-align: top; }}
  tr:hover td {{ background: #1a1a24; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: .75rem; color: #fff; }}
  .overdue {{ color: #fd7e14; font-weight: bold; }}
  .card {{ background: #1a1a24; border-radius: 10px; margin-bottom: 12px; overflow: hidden; }}
  .card-header {{ padding: 12px; display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }}
  .card-header strong {{ flex: 1; font-size: .9rem; }}
  .meta {{ color: #666; font-size: .75rem; }}
  pre.preview {{ padding: 12px; font-size: .75rem; color: #888; white-space: pre-wrap; word-break: break-word;
                 border-top: 1px solid #2a2a38; max-height: 120px; overflow: hidden; }}
  small {{ color: #666; }}
</style>
</head>
<body>
<h1>FinAz Dashboard</h1>
<p class="sub">Zuletzt aktualisiert: {now}</p>

<section>
  <div class="grid">
    <div class="kpi"><div class="n">{crm['total']}</div><div class="label">Leads gesamt</div></div>
    <div class="kpi {'alert' if crm['followups'] > 0 else ''}">
      <div class="n">{crm['followups']}</div><div class="label">Follow-ups fällig</div>
    </div>
    <div class="kpi"><div class="n">{crm['by_status'].get('kunde', 0)}</div><div class="label">Kunden</div></div>
    <div class="kpi"><div class="n">{len(files)}</div><div class="label">Content-Dateien</div></div>
  </div>
</section>

<section>
  <h2>Lead-Status</h2>
  {status_bars}
</section>

{'<section><h2>Leads (neueste 20)</h2><table><thead><tr><th>#</th><th>Name</th><th>Status</th><th>Interesse</th><th>Quelle</th><th>Follow-up</th></tr></thead><tbody>' + leads_rows + '</tbody></table></section>' if crm['total'] else ''}

<section>
  <h2>Generierter Content</h2>
  {content_cards if content_cards else '<p style="color:#666">Noch keine Content-Dateien vorhanden.</p>'}
</section>

</body>
</html>"""

    DASHBOARD_PATH.write_text(html, encoding="utf-8")
    return DASHBOARD_PATH


if __name__ == "__main__":
    pfad = generate()
    print(f"✅ Dashboard generiert: {pfad}")
    print(f"\nÖffne im Browser: file://{pfad.resolve()}")
    print("Auf Android: Im Datei-Manager navigieren → output/dashboard.html → mit Browser öffnen")
