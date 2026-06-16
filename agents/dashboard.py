"""
dashboard.py – Dashboard HTML con 3 tab: Creator / Leads / Content
"""
import sqlite3
from datetime import date, datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
DB_PATH = OUTPUT_DIR / "crm.db"
DASHBOARD_PATH = OUTPUT_DIR / "dashboard.html"


def _load_crm() -> dict:
    if not DB_PATH.exists():
        return {"total": 0, "by_status": {}, "followups": 0, "leads": []}
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    total = con.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    by_status = {r[0]: r[1] for r in con.execute("SELECT status, COUNT(*) FROM leads GROUP BY status")}
    followups = con.execute(
        "SELECT COUNT(*) FROM leads WHERE followup <= ? AND status NOT IN ('kunde','verloren')",
        (date.today().isoformat(),)
    ).fetchone()[0]
    leads = [dict(r) for r in con.execute("SELECT * FROM leads ORDER BY followup LIMIT 30")]
    con.close()
    return {"total": total, "by_status": by_status, "followups": followups, "leads": leads}


def _load_files() -> tuple[list, list, list]:
    creator, content, other = [], [], []
    for f in sorted(OUTPUT_DIR.glob("*.txt"), reverse=True)[:40]:
        try:
            text = f.read_text(encoding="utf-8")
            first_line = text.split("\n")[0][:80]
            entry = {
                "name": f.name,
                "label": first_line,
                "date": datetime.fromtimestamp(f.stat().st_mtime).strftime("%d.%m.%Y %H:%M"),
                "size": f"{f.stat().st_size // 1024 + 1} KB",
                "preview": text[:500].replace("<", "&lt;").replace(">", "&gt;"),
            }
            stem = f.stem.lower()
            if stem.startswith("creator"):
                # Estrai nische dalla prima riga
                entry["nische"] = first_line.replace("CREATOR GROWTH SYSTEM", "").strip()
                creator.append(entry)
            elif any(stem.startswith(x) for x in ["ergebnisse", "content", "lead", "shop", "coaching", "affiliate", "brand"]):
                content.append(entry)
            else:
                other.append(entry)
        except Exception:
            continue
    return creator, content, other


def _status_color(s: str) -> str:
    return {"neu": "#6c757d", "kontaktiert": "#0d6efd", "interessiert": "#fd7e14",
            "angebot": "#6f42c1", "kunde": "#198754", "verloren": "#dc3545"}.get(s, "#aaa")


def _card(entry: dict, accent: str = "#6f42c1") -> str:
    return f"""<div class="card">
      <div class="card-header" style="border-left:4px solid {accent}">
        <strong>{entry['label']}</strong>
        <span class="meta">{entry['date']} · {entry['size']}</span>
      </div>
      <pre class="preview">{entry['preview']}...</pre>
    </div>"""


def generate() -> Path:
    crm = _load_crm()
    creator_files, content_files, _ = _load_files()
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    # KPI
    n_creator = len(creator_files)
    n_leads = crm["total"]
    n_kunden = crm["by_status"].get("kunde", 0)
    n_followup = crm["followups"]

    # Status bars
    status_bars = ""
    for s in ["neu", "kontaktiert", "interessiert", "angebot", "kunde", "verloren"]:
        n = crm["by_status"].get(s, 0)
        pct = round(n / n_leads * 100) if n_leads else 0
        color = _status_color(s)
        status_bars += f"""<div class="stat-row">
          <span class="stat-label">{s}</span>
          <div class="bar-wrap"><div class="bar" style="width:{pct}%;background:{color}"></div></div>
          <span class="stat-n">{n}</span>
        </div>"""

    # Leads table
    leads_rows = ""
    for l in crm["leads"]:
        color = _status_color(l.get("status", ""))
        fu = l.get("followup") or "—"
        overdue = fu != "—" and fu <= date.today().isoformat() and l.get("status") not in ("kunde", "verloren")
        fu_cell = f'<span class="overdue">{fu} ◄</span>' if overdue else fu
        leads_rows += f"""<tr>
          <td>{l['id']}</td>
          <td><strong>{l['name']}</strong><br><small>{l.get('email','')}</small></td>
          <td><span class="badge" style="background:{color}">{l.get('status','')}</span></td>
          <td>{l.get('interesse','')}</td>
          <td>{l.get('quelle','')}</td>
          <td>{fu_cell}</td>
        </tr>"""

    # Creator cards
    creator_cards = "".join(_card(f, "#e91e63") for f in creator_files) or \
        '<p style="color:#666">Noch keine Creator-Analysen vorhanden.<br>Starte mit: python3 creator_master.py</p>'

    # Content cards
    content_cards = "".join(_card(f, "#6f42c1") for f in content_files) or \
        '<p style="color:#666">Noch keine Content-Dateien vorhanden.</p>'

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Creator Dashboard</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:system-ui,sans-serif;background:#0f0f13;color:#e0e0e0;padding:16px}}
  h1{{font-size:1.4rem;color:#fff;margin-bottom:4px}}
  .sub{{color:#888;font-size:.85rem;margin-bottom:20px}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:12px;margin-bottom:24px}}
  .kpi{{background:#1a1a24;border-radius:10px;padding:16px;text-align:center}}
  .kpi .n{{font-size:2rem;font-weight:700;color:#fff}}
  .kpi .label{{font-size:.8rem;color:#888;margin-top:4px}}
  .kpi.alert .n{{color:#fd7e14}}
  .kpi.pink .n{{color:#e91e63}}
  .tabs{{display:flex;gap:8px;margin-bottom:20px;border-bottom:2px solid #2a2a38;padding-bottom:0}}
  .tab{{padding:10px 16px;cursor:pointer;border-radius:8px 8px 0 0;font-size:.9rem;color:#888;border:none;background:none;transition:.2s}}
  .tab.active{{background:#1a1a24;color:#fff;border-bottom:2px solid #e91e63;margin-bottom:-2px}}
  .tab-content{{display:none}}.tab-content.active{{display:block}}
  h2{{font-size:1rem;color:#bbb;margin-bottom:12px;text-transform:uppercase;letter-spacing:1px}}
  .stat-row{{display:flex;align-items:center;gap:10px;margin-bottom:8px}}
  .stat-label{{width:110px;font-size:.85rem;color:#bbb}}
  .bar-wrap{{flex:1;background:#2a2a38;border-radius:4px;height:10px}}
  .bar{{height:10px;border-radius:4px;min-width:4px}}
  .stat-n{{width:24px;text-align:right;font-size:.85rem;color:#888}}
  table{{width:100%;border-collapse:collapse;font-size:.85rem}}
  th{{text-align:left;color:#888;border-bottom:1px solid #2a2a38;padding:8px 6px}}
  td{{padding:8px 6px;border-bottom:1px solid #1a1a24;vertical-align:top}}
  tr:hover td{{background:#1a1a24}}
  .badge{{display:inline-block;padding:2px 8px;border-radius:10px;font-size:.75rem;color:#fff}}
  .overdue{{color:#fd7e14;font-weight:bold}}
  .card{{background:#1a1a24;border-radius:10px;margin-bottom:12px;overflow:hidden}}
  .card-header{{padding:12px;display:flex;flex-wrap:wrap;align-items:center;gap:8px}}
  .card-header strong{{flex:1;font-size:.9rem}}
  .meta{{color:#666;font-size:.75rem}}
  pre.preview{{padding:12px;font-size:.75rem;color:#888;white-space:pre-wrap;word-break:break-word;
    border-top:1px solid #2a2a38;max-height:140px;overflow:hidden}}
  small{{color:#666}}
  section{{margin-bottom:24px}}
</style>
</head>
<body>
<h1>Creator Agency Dashboard</h1>
<p class="sub">Aggiornato: {now}</p>

<div class="grid">
  <div class="kpi pink"><div class="n">{n_creator}</div><div class="label">Creator Analysen</div></div>
  <div class="kpi"><div class="n">{n_leads}</div><div class="label">Leads</div></div>
  <div class="kpi"><div class="n">{n_kunden}</div><div class="label">Kunden</div></div>
  <div class="kpi {'alert' if n_followup > 0 else ''}"><div class="n">{n_followup}</div><div class="label">Follow-ups</div></div>
</div>

<div class="tabs">
  <button class="tab active" onclick="showTab('creator')">Creator</button>
  <button class="tab" onclick="showTab('leads')">Leads / CRM</button>
  <button class="tab" onclick="showTab('content')">Content</button>
</div>

<!-- TAB: CREATOR -->
<div id="tab-creator" class="tab-content active">
  <section>
    <h2>Creator Analysen ({n_creator})</h2>
    {creator_cards}
  </section>
</div>

<!-- TAB: LEADS -->
<div id="tab-leads" class="tab-content">
  <section>
    <h2>Lead-Status</h2>
    {status_bars}
  </section>
  {'<section><h2>Leads (' + str(n_leads) + ')</h2><table><thead><tr><th>#</th><th>Name</th><th>Status</th><th>Interesse</th><th>Quelle</th><th>Follow-up</th></tr></thead><tbody>' + leads_rows + '</tbody></table></section>' if n_leads else '<p style="color:#666">Noch keine Leads. Starte mit: python3 crm.py add</p>'}
</div>

<!-- TAB: CONTENT -->
<div id="tab-content" class="tab-content">
  <section>
    <h2>Generierter Content ({len(content_files)})</h2>
    {content_cards}
  </section>
</div>

<script>
function showTab(name) {{
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  event.target.classList.add('active');
}}
</script>
</body>
</html>"""

    DASHBOARD_PATH.write_text(html, encoding="utf-8")
    return DASHBOARD_PATH


if __name__ == "__main__":
    pfad = generate()
    print(f"Dashboard generiert: {pfad}")
    print("Server starten: cd /root/output && python3 -m http.server 8080")
