import argparse, csv
from datetime import datetime
from statistics import mean

def parse_dt(s: str) -> datetime:
    # Accept ISO 8601 with 'Z' or offset (e.g., 2026-01-04T10:15:00Z)
    s = s.strip().replace("Z", "+00:00")
    return datetime.fromisoformat(s)

def minutes_between(a: datetime, b: datetime) -> float:
    return (b - a).total_seconds() / 60.0

def load_incidents(path: str):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows

def compute_metrics(incidents, sla_minutes: int):
    detect_mins = []
    resolve_mins = []
    sla_hits = 0
    per_incident = []

    for i in incidents:
        created = parse_dt(i["created_time"])
        detected = parse_dt(i["detected_time"])
        resolved = parse_dt(i["resolved_time"])

        mttd = minutes_between(created, detected)
        mttr = minutes_between(detected, resolved)
        total = minutes_between(created, resolved)

        detect_mins.append(mttd)
        resolve_mins.append(mttr)

        hit = total <= sla_minutes
        sla_hits += 1 if hit else 0

        per_incident.append({
            "incident_id": i["incident_id"],
            "severity": i["severity"],
            "category": i["category"],
            "mttd_min": round(mttd, 1),
            "mttr_min": round(mttr, 1),
            "total_min": round(total, 1),
            "sla_met": "Yes" if hit else "No"
        })

    summary = {
        "incidents": len(incidents),
        "mttd_avg": round(mean(detect_mins), 1) if detect_mins else 0.0,
        "mttr_avg": round(mean(resolve_mins), 1) if resolve_mins else 0.0,
        "sla_minutes": sla_minutes,
        "sla_compliance": round((sla_hits / len(incidents)) * 100.0, 1) if incidents else 0.0
    }
    return summary, per_incident

def render_html(summary, per_incident):
    rows_html = ""
    for r in per_incident:
        rows_html += f"""<tr>
<td>{r['incident_id']}</td>
<td>{r['severity']}</td>
<td>{r['category']}</td>
<td>{r['mttd_min']}</td>
<td>{r['mttr_min']}</td>
<td>{r['total_min']}</td>
<td>{r['sla_met']}</td>
</tr>"""

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<title>SOC Metrics Dashboard</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 24px; }}
h1 {{ margin-bottom: 6px; }}
small {{ color: #666; }}
.cards {{ display: flex; gap: 12px; flex-wrap: wrap; margin: 16px 0; }}
.card {{ border: 1px solid #ddd; border-radius: 10px; padding: 12px 14px; min-width: 180px; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 14px; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background: #f7f7f7; }}
</style>
</head>
<body>
<h1>SOC Metrics Dashboard</h1>
<small>Portfolio sample report (sanitized data)</small>

<div class="cards">
  <div class="card"><b>Incidents</b><div>{summary['incidents']}</div></div>
  <div class="card"><b>Avg MTTD (min)</b><div>{summary['mttd_avg']}</div></div>
  <div class="card"><b>Avg MTTR (min)</b><div>{summary['mttr_avg']}</div></div>
  <div class="card"><b>SLA Target (min)</b><div>{summary['sla_minutes']}</div></div>
  <div class="card"><b>SLA Compliance</b><div>{summary['sla_compliance']}%</div></div>
</div>

<h2>Incident Table</h2>
<table>
  <thead>
    <tr>
      <th>ID</th><th>Severity</th><th>Category</th>
      <th>MTTD</th><th>MTTR</th><th>Total</th><th>SLA Met</th>
    </tr>
  </thead>
  <tbody>
    {rows_html}
  </tbody>
</table>
</body>
</html>"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/incidents.csv")
    ap.add_argument("--sla-minutes", type=int, default=60)
    ap.add_argument("--out", default="outputs/dashboard.html")
    args = ap.parse_args()

    incidents = load_incidents(args.input)
    summary, per_incident = compute_metrics(incidents, args.sla_minutes)
    html = render_html(summary, per_incident)

    import os
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html)

    print("[OK] Wrote:", args.out)

if __name__ == "__main__":
    main()
