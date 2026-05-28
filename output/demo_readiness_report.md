# LandInvest Demo Readiness Report

- Generated at: `2026-05-27T22:19:31.151050+00:00`
- Overall status: `pass`
- Ranking rows: `3144`
- Demo strategy: `Long-term appreciation`

## Checklist

| Area | Status | Detail |
|---|---|---|
| Rankings | pass | 3,144 county rows loaded. |
| X-factor gate | pass | no_default_interaction_promotion |
| Share exports | pass | Top 25, Top 100, shortlist CSV, compare Markdown, and compare JSON generated. |
| Deploy bundle | pass | bash scripts/build_streamlit_deploy_bundle.sh |
| Deploy artifacts | pass | 0 required missing, 0 optional missing. |
| App tests | pass | Local and deploy Streamlit AppTest smoke tests. |
| Model research gate | pass | do_not_promote_current_interactions |

## Review Exports

- top25_markdown: `/Users/coryseidel/PersonalProjects/IdeaTests/LandInvest/output/demo_readiness/landinvest_top25_opportunity_report.md`
- top100_markdown: `/Users/coryseidel/PersonalProjects/IdeaTests/LandInvest/output/demo_readiness/landinvest_top100_opportunity_report.md`
- shortlist_csv: `/Users/coryseidel/PersonalProjects/IdeaTests/LandInvest/output/demo_readiness/landinvest_active_shortlist_top100.csv`
- compare_markdown: `/Users/coryseidel/PersonalProjects/IdeaTests/LandInvest/output/demo_readiness/landinvest_compare_set_summary.md`
- compare_json: `/Users/coryseidel/PersonalProjects/IdeaTests/LandInvest/output/demo_readiness/landinvest_compare_set.json`

## Commands

- py_compile: `pass` - `/Users/coryseidel/PersonalProjects/IdeaTests/LandInvest/.venv/bin/python -m py_compile dashboard.py scripts/evaluate_xfactor_frontier_interactions.py scripts/build_xfactor_ablation_autopsy.py scripts/build_xfactor_guarded_overlay_next_lane.py scripts/evaluate_p0_repeatable_residual_guardrail.py scripts/build_demo_readiness_bundle.py`
- xfactor_gate: `pass` - `/Users/coryseidel/PersonalProjects/IdeaTests/LandInvest/.venv/bin/python scripts/evaluate_xfactor_frontier_interactions.py`
- xfactor_autopsy: `pass` - `/Users/coryseidel/PersonalProjects/IdeaTests/LandInvest/.venv/bin/python scripts/build_xfactor_ablation_autopsy.py`
- xfactor_guarded_overlay: `pass` - `/Users/coryseidel/PersonalProjects/IdeaTests/LandInvest/.venv/bin/python scripts/build_xfactor_guarded_overlay_next_lane.py`
- deploy_bundle: `pass` - `bash scripts/build_streamlit_deploy_bundle.sh`

## Deploy Artifact Checks

- Deploy dashboard: `pass` - `/Users/coryseidel/PersonalProjects/IdeaTests/LandInvest/deploy/streamlit_app/dashboard.py`
- Deploy rankings: `pass` - `/Users/coryseidel/PersonalProjects/IdeaTests/LandInvest/deploy/streamlit_app/output/county_rankings_2024.parquet`
- Deploy project status: `pass` - `/Users/coryseidel/PersonalProjects/IdeaTests/LandInvest/deploy/streamlit_app/output/project_status_bundle.json`
- Deploy demo readiness: `pass` - `/Users/coryseidel/PersonalProjects/IdeaTests/LandInvest/deploy/streamlit_app/output/demo_readiness_report.json`
- Deploy X-factor gate: `pass` - `/Users/coryseidel/PersonalProjects/IdeaTests/LandInvest/deploy/streamlit_app/output/xfactor_interaction_promotion_gate.json`
- Deploy X-factor autopsy: `pass` - `/Users/coryseidel/PersonalProjects/IdeaTests/LandInvest/deploy/streamlit_app/output/xfactor_interaction_ablation_autopsy.json`
- Deploy X-factor guarded overlay: `pass` - `/Users/coryseidel/PersonalProjects/IdeaTests/LandInvest/deploy/streamlit_app/output/xfactor_guarded_overlay_next_lane.json`
- Deploy repeatable P0 residual guardrail: `pass` - `/Users/coryseidel/PersonalProjects/IdeaTests/LandInvest/deploy/streamlit_app/output/p0_repeatable_residual_guardrail.json`
- Deploy repeatable P0 residual guardrail preview: `pass` - `/Users/coryseidel/PersonalProjects/IdeaTests/LandInvest/deploy/streamlit_app/output/p0_repeatable_residual_guardrail_top_candidates.csv`

## X-Factor Gate

- Production promotion status: `no_default_interaction_promotion`
- Default-promotion candidates: `0`
- Completed but blocked candidates: `2`

## X-Factor Guarded Overlay

- Decision: `pass_guardrails`
- Top-25 churn: `4.0%`
- Mean absolute rank shift: `24.58`

## Notes

- Review exports are county-level screening material, not investment advice.
- Exports include public-source attribution and avoid saved user notes by default.
- Current X-factor interaction gate keeps candidates report-only because controlled ablations block default promotion.

## Source Attribution

- Home-value and price-history artifacts are built from FHFA and Zillow-derived project outputs.
- Economic, labor, establishment, income, and demographic features draw from public BLS, BEA, Census, CBP/QCEW, and related staged artifacts.
- Climate, terrain, broadband, land-constraint, and environmental overlays draw from public NOAA, USGS, FCC, PAD-US/wetlands-derived, and project-staged source layers.
- Corporate-anchor and X-factor evidence includes report-only SEC EDGAR proof lanes and staged anchor diagnostics.
