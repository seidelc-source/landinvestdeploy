# LandInvest Remote Demo Deploy

This folder is a compact, read-only Streamlit deployment bundle for remote testers.

The dashboard includes Product Mode, Customer Mode, and Legacy Mode. Customer Mode is the cleaner customer-facing workflow with radar, opportunity cards, county story, compare, watchlist, and packet exports; it defaults to the Product Mode-aligned General Opportunity view and is still a presentation layer over the included ranking artifacts.

It intentionally includes only:

- `dashboard.py`
- minimal `requirements.txt`
- bundled map asset at `assets/geojson-counties-fips.json`
- bundled brand asset at `assets/landinvest-logo.svg`
- `output/county_rankings_2024.parquet`
- latest run metadata under `output/runs/<latest_run>/run_summary.json` and `run_deltas.json`
- `output/evaluation_report.json`
- small optional `output/*.csv` / `output/*.json` dashboard context files
- optional quantile diagnostics under `models/artifacts/quantile/`

It intentionally excludes:

- `data/raw/`
- `data/processed/`
- training scripts and model-training data
- local `.env` secrets

## Local Smoke Test

From this folder:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard.py
```

## Streamlit Community Cloud

1. Create a new GitHub repo, for example `LandInvestDeploy`.
2. Copy the contents of this folder into that repo root.
3. Commit and push.
4. In Streamlit Community Cloud, choose the repo and set the main file to `dashboard.py`.
5. Deploy.

## Important Notes

- This is a demo/review app. It should not run source ingestion, feature engineering, or model training remotely.
- Watchlists, notes, compare sets, saved strategies, parcel checklists, and customer packet state are currently local SQLite state in `output/dashboard_user_data.sqlite3`; do not treat this as authentication, authorization, or private multi-user storage.
- If you need persistent per-user data later, add authentication plus a database such as Supabase/Postgres.
