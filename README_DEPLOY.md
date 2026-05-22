# LandInvest Remote Demo Deploy

This folder is a compact, read-only Streamlit deployment bundle for remote testers.

It intentionally includes only:

- `dashboard.py`
- minimal `requirements.txt`
- `output/county_rankings_2024.parquet`
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
- Watchlists/notes are currently local JSON state in `output/dashboard_user_data.json`; do not treat them as private multi-user accounts.
- If you need persistent per-user data later, add authentication plus a database such as Supabase/Postgres.
