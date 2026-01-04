# SOC Metrics Dashboard (MTTD / MTTR / SLA)

A lightweight SOC reporting utility that calculates **MTTD**, **MTTR**, and **SLA compliance** from incident data and generates an HTML dashboard.

## What it does
- Reads a CSV of SOC incidents (`data/incidents.csv`)
- Computes:
  - **MTTD** (Mean Time To Detect)
  - **MTTR** (Mean Time To Respond / Resolve)
  - SLA compliance based on a configurable SLA target (minutes)
- Outputs a single-file HTML report to `outputs/dashboard.html`

## Run
```bash
python dashboard.py --input data/incidents.csv --sla-minutes 60 --out outputs/dashboard.html
```

## Data format
See `data/incidents.csv` for an example. Timestamps must be ISO 8601 (UTC recommended).

## Notes
This is a portfolio/lab dashboard using **sanitized sample data**.
