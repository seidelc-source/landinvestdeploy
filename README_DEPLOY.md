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

## Publishing the hosted demo (GitHub → Streamlit Community Cloud)

The hosted-demo lineage is the public GitHub repo `seidelc-source/landinvestdeploy` (Community Cloud deploys from GitHub only; the GitLab `origin` of the main repository is the research lineage). A working clone lives at `../landinvestdeploy` next to the main repo. To publish a refreshed bundle:

```bash
bash scripts/build_streamlit_deploy_bundle.sh
rsync -a --delete --exclude .git --exclude __pycache__ deploy/streamlit_app/ ../landinvestdeploy/
git -C ../landinvestdeploy add -A && git -C ../landinvestdeploy commit -m "Refresh hosted demo" && git -C ../landinvestdeploy push github main
```

A Community Cloud app pointed at that repo (branch `main`, main file `dashboard.py`) redeploys on push. If no app exists yet: share.streamlit.io → sign in with GitHub → New app → repository `seidelc-source/landinvestdeploy`, branch `main`, main file `dashboard.py` → Deploy. The repo is public, so the app is public: it carries no AirROI figures (stripped by the bundle script) but does carry ZHVI-derived yields — the Zillow/Redfin redistribution check is still open.

## Streamlit Community Cloud (original notes)

1. Create a new GitHub repo, for example `LandInvestDeploy`.
2. Copy the contents of this folder into that repo root.
3. Commit and push.
4. In Streamlit Community Cloud, choose the repo and set the main file to `dashboard.py`.
5. Deploy.

## Data boundary (2026-09-09)

- `output/recal/county_briefs.parquet` is now part of the bundle (tracked in git) so the hosted demo needs no data build.
- The bundle script strips every AirROI column (`str_*`, except the free NES host proxy) by default because AirROI's terms allow redistribution of aggregates only under a separately executed addendum. Build with `INCLUDE_AIRROI=1 bash scripts/build_streamlit_deploy_bundle.sh` for an internal-only build; never deploy that build publicly.

## Important Notes

- This is a demo/review app. It should not run source ingestion, feature engineering, or model training remotely.
- Watchlists, notes, compare sets, saved strategies, parcel checklists, and customer packet state are currently local SQLite state in `output/dashboard_user_data.sqlite3`; do not treat this as authentication, authorization, or private multi-user storage.
- If you need persistent per-user data later, add authentication plus a database such as Supabase/Postgres.
