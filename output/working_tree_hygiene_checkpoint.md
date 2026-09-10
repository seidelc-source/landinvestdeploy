# Working Tree Hygiene Checkpoint

## TLDR

- Status: `working_batch_left_unstaged_by_design`.
- Branch: `Baseline`.
- Changed paths: `291`.
- Decision: No files were staged or committed by this checkpoint. The working batch remains available for operator review.
- Recommended next action: After reviewing generated outputs, stage source scripts/dashboard modules plus selected lightweight deploy artifacts; keep raw data and ignored heavy outputs out of Git.

## Class Counts

- `documentation_or_checkpoint`: `1`
- `dashboard_source`: `4`
- `data_source_or_registry`: `1`
- `deploy_bundle`: `236`
- `source_script`: `49`

## Changed Paths

| Status | Class | Path |
|---|---|---|
| ` M` | `documentation_or_checkpoint` | `AGENTS.md` |
| ` M` | `dashboard_source` | `dashboard.py` |
| ` M` | `dashboard_source` | `dashboard_modules/evidence_panel.py` |
| ` M` | `data_source_or_registry` | `data/source_registry.yaml` |
| ` M` | `deploy_bundle` | `deploy/streamlit_app/dashboard.py` |
| ` M` | `deploy_bundle` | `deploy/streamlit_app/dashboard_modules/evidence_panel.py` |
| ` M` | `deploy_bundle` | `deploy/streamlit_app/output/xfactor_command_loop.csv` |
| ` M` | `source_script` | `scripts/apply_sec_point_in_time_hq_geocode_review.py` |
| ` M` | `source_script` | `scripts/audit_streamlit_ui_accessibility.py` |
| ` M` | `source_script` | `scripts/build_sec_edgar_hq_source_maturity_refresh.py` |
| ` M` | `source_script` | `scripts/build_streamlit_deploy_bundle.sh` |
| ` M` | `source_script` | `scripts/build_xfactor_command_loop.py` |
| ` M` | `source_script` | `scripts/run_sec_point_in_time_hq_address_parse_batch.py` |
| `??` | `dashboard_source` | `dashboard_modules/county_memo.py` |
| `??` | `dashboard_source` | `dashboard_modules/customer_story.py` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/dashboard_modules/county_memo.py` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/dashboard_modules/customer_story.py` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/controlled_xfactor_ablation_sprint.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/controlled_xfactor_ablation_sprint.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/controlled_xfactor_ablation_sprint.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/fiveyr_boundary_review_packet.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/fiveyr_boundary_review_packet.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/fiveyr_boundary_review_packet.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/fiveyr_rank_band_promotion_gate.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/fiveyr_rank_band_promotion_gate.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/fiveyr_rank_band_promotion_gate.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_archetype_gap_closure_2024.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_archetype_gap_closure_2024.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_archetype_gap_closure_2024.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_county_provider_review_queue.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_leakage_gate.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_leakage_gate.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_missingness_by_state.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_official_county_year.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_official_source_panel.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_official_source_panel.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_census_acceptance.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_census_acceptance.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_census_acceptance.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_census_attempts.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_census_batch.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_census_batch.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_census_candidates.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_census_input.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_census_raw_results.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_closeout_acceptance.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_closeout_acceptance.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_closeout_acceptance.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_closeout_packet.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_closeout_packet.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_closeout_packet.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_census_acceptance.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_census_acceptance.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_census_acceptance.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_acceptance.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_acceptance.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_acceptance.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_census_context_review.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_census_context_review.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_census_context_review.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_geocoder_input.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_osm_geocode_acceptance.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_osm_geocode_acceptance.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_osm_geocode_acceptance.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_osm_geocode_attempts.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_osm_geocode_batch.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_osm_geocode_batch.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_osm_geocode_candidates.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_osm_geocode_raw_results.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_osm_geocode_results.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_osm_same_city_geocode_acceptance.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_osm_same_city_geocode_acceptance.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_osm_same_city_geocode_acceptance.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_osm_same_city_geocode_attempts.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_osm_same_city_geocode_batch.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_osm_same_city_geocode_batch.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_osm_same_city_geocode_candidates.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_osm_same_city_geocode_raw_results.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_osm_same_city_geocode_results.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p0_authoritative_acceptance.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p0_authoritative_acceptance.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p0_authoritative_acceptance.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p0_authoritative_census_rows.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p0_authoritative_nppes_rows.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p0_authoritative_results.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p0_authoritative_review.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p0_authoritative_review.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p0_authoritative_review.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p0_cms_hgi_acceptance.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p0_cms_hgi_acceptance.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p0_cms_hgi_acceptance.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p0_cms_hgi_results.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p0_cms_hgi_review.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p0_cms_hgi_review.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p0_cms_hgi_review.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p0_cms_hgi_rows.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p1_cms_hgi_acceptance.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p1_cms_hgi_acceptance.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p1_cms_hgi_acceptance.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p1_cms_hgi_results.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p1_cms_hgi_review.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p1_cms_hgi_review.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p1_cms_hgi_review.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p1_cms_hgi_rows.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p1_guayama_authoritative_acceptance.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p1_guayama_authoritative_acceptance.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p1_guayama_authoritative_acceptance.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p1_guayama_authoritative_results.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p1_guayama_authoritative_review.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p1_guayama_authoritative_review.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p1_guayama_authoritative_review.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p1_guayama_authoritative_sources.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p1_territory_cms_hgi_acceptance.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p1_territory_cms_hgi_acceptance.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p1_territory_cms_hgi_acceptance.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p1_territory_cms_hgi_results.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p1_territory_cms_hgi_review.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p1_territory_cms_hgi_review.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p1_territory_cms_hgi_review.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p2_authoritative_acceptance.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p2_authoritative_acceptance.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p2_authoritative_acceptance.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p2_authoritative_nppes_rows.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p2_authoritative_results.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p2_authoritative_review.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p2_authoritative_review.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p2_authoritative_review.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_p2_authoritative_sources.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_packet.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_packet.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_packet.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_residual_census_retry.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_residual_census_retry.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_residual_census_retry_acceptance.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_residual_census_retry_acceptance.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_residual_census_retry_acceptance.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_residual_census_retry_attempts.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_residual_census_retry_candidates.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_residual_census_retry_input.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_residual_census_retry_raw_results.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_residual_census_retry_results.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_residual_context_spotcheck.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_residual_context_spotcheck.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_residual_context_spotcheck.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_residual_context_spotcheck_acceptance.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_residual_context_spotcheck_acceptance.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_residual_context_spotcheck_acceptance.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_residual_context_spotcheck_results.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_residual_triage_external_followup.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_residual_triage_manual_review.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_residual_triage_packet.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_residual_triage_packet.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_residual_triage_packet.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_residual_triage_summary_by_state.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_results_CENSUS_CONTEXT_REVIEW.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_results_TEMPLATE.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_external_manual_summary_by_state.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_review.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_review.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_review.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_same_city_conflict_acceptance.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_same_city_conflict_acceptance.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_same_city_conflict_acceptance.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_same_city_context_acceptance.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_same_city_context_acceptance.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_same_city_context_acceptance.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_same_city_review_packet.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_same_city_review_packet.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_same_city_review_packet.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_same_city_spotcheck_acceptance.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_same_city_spotcheck_acceptance.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_provider_geocode_same_city_spotcheck_acceptance.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_source_maturity_gate.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/institutional_anchor_source_maturity_gate.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/preboom_archetype_diversity_followup_2024.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/preboom_archetype_diversity_followup_2024.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/preboom_archetype_diversity_followup_2024.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/preboom_archetype_diversity_gap_queue_2024.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_edgar_hq_source_maturity_refresh.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_edgar_hq_source_maturity_refresh.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_conflict_override_acceptance.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_conflict_override_acceptance.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_conflict_override_acceptance.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_county_closeout.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_county_closeout.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_county_closeout_acceptance.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_county_closeout_acceptance.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_county_closeout_acceptance.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_county_closeout_attempts.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_county_closeout_candidates.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_county_closeout_census_input.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_county_closeout_packet.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_county_closeout_raw_results.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_final_held_external_evidence.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_final_held_external_evidence.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_final_held_external_evidence.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_held_row_resolution.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_held_row_resolution.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_held_row_resolution.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_held_row_resolution_attempts.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_held_row_resolution_census_input.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_held_row_resolution_raw_results.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_spotcheck_acceptance.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_spotcheck_acceptance.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_spotcheck_acceptance.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_auto_reuse_spotcheck_queue.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_county_year_candidates.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_geocode_review_applied.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_geocode_review_applied.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_geocode_review_applied.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_parse_review_pattern_candidates.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_parse_review_pattern_candidates.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_parse_review_pattern_candidates.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_parse_review_triage.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_pending_geocode_candidate_acceptance.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_pending_geocode_candidate_acceptance.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_pending_geocode_candidate_acceptance.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_pending_geocode_candidates.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_pending_geocode_census_attempts.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_pending_geocode_census_batch.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_pending_geocode_census_batch.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_pending_geocode_census_input.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_pending_geocode_census_raw_results.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_pending_geocode_override_candidates.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_pending_geocode_queue.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_residual_geocode_acceptance.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_residual_geocode_acceptance.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_residual_geocode_acceptance.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_residual_geocode_candidates.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_residual_geocode_candidates.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_residual_geocode_override_candidates.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_review_queue_summary.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_review_queue_summary.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_scaleup_gate.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_scaleup_gate.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/sec_point_in_time_hq_scaleup_gate.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/source_registry_report.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/source_registry_report.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/source_registry_report.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/ui_accessibility_audit.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/ui_accessibility_audit.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/working_tree_hygiene_checkpoint.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/working_tree_hygiene_checkpoint.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/xfactor_command_loop.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/xfactor_command_loop.md` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/xfactor_evidence_center.csv` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/xfactor_evidence_center.json` |
| `??` | `deploy_bundle` | `deploy/streamlit_app/output/xfactor_evidence_center.md` |
| `??` | `source_script` | `scripts/accept_institutional_anchor_provider_geocode_census_candidates.py` |
| `??` | `source_script` | `scripts/accept_institutional_anchor_provider_geocode_closeout.py` |
| `??` | `source_script` | `scripts/accept_institutional_anchor_provider_geocode_external_census_candidates.py` |
| `??` | `source_script` | `scripts/accept_institutional_anchor_provider_geocode_external_manual_results.py` |
| `??` | `source_script` | `scripts/accept_institutional_anchor_provider_geocode_same_city_conflict_census_candidates.py` |
| `??` | `source_script` | `scripts/accept_institutional_anchor_provider_geocode_same_city_context_census_candidates.py` |
| `??` | `source_script` | `scripts/accept_institutional_anchor_provider_geocode_same_city_spotcheck_candidates.py` |
| `??` | `source_script` | `scripts/accept_sec_point_in_time_hq_auto_reuse_conflict_overrides.py` |
| `??` | `source_script` | `scripts/accept_sec_point_in_time_hq_auto_reuse_county_closeout.py` |
| `??` | `source_script` | `scripts/accept_sec_point_in_time_hq_pending_geocode_candidates.py` |
| `??` | `source_script` | `scripts/build_controlled_xfactor_ablation_sprint.py` |
| `??` | `source_script` | `scripts/build_fiveyr_boundary_review_packet.py` |
| `??` | `source_script` | `scripts/build_fiveyr_rank_band_promotion_gate.py` |
| `??` | `source_script` | `scripts/build_institutional_anchor_archetype_gap_closure.py` |
| `??` | `source_script` | `scripts/build_institutional_anchor_leakage_gate.py` |
| `??` | `source_script` | `scripts/build_institutional_anchor_official_source_panel.py` |
| `??` | `source_script` | `scripts/build_institutional_anchor_provider_geocode_closeout_packet.py` |
| `??` | `source_script` | `scripts/build_institutional_anchor_provider_geocode_external_manual_census_context_review.py` |
| `??` | `source_script` | `scripts/build_institutional_anchor_provider_geocode_external_manual_p0_authoritative_review.py` |
| `??` | `source_script` | `scripts/build_institutional_anchor_provider_geocode_external_manual_p0_cms_hgi_review.py` |
| `??` | `source_script` | `scripts/build_institutional_anchor_provider_geocode_external_manual_p1_guayama_authoritative_review.py` |
| `??` | `source_script` | `scripts/build_institutional_anchor_provider_geocode_external_manual_p2_authoritative_review.py` |
| `??` | `source_script` | `scripts/build_institutional_anchor_provider_geocode_external_manual_packet.py` |
| `??` | `source_script` | `scripts/build_institutional_anchor_provider_geocode_external_manual_residual_context_spotcheck.py` |
| `??` | `source_script` | `scripts/build_institutional_anchor_provider_geocode_external_manual_residual_triage_packet.py` |
| `??` | `source_script` | `scripts/build_institutional_anchor_provider_geocode_review.py` |
| `??` | `source_script` | `scripts/build_institutional_anchor_provider_geocode_same_city_review_packet.py` |
| `??` | `source_script` | `scripts/build_institutional_anchor_source_maturity_gate.py` |
| `??` | `source_script` | `scripts/build_preboom_archetype_diversity_followup.py` |
| `??` | `source_script` | `scripts/build_sec_point_in_time_hq_auto_reuse_county_closeout.py` |
| `??` | `source_script` | `scripts/build_sec_point_in_time_hq_auto_reuse_final_held_external_evidence.py` |
| `??` | `source_script` | `scripts/build_sec_point_in_time_hq_auto_reuse_held_row_resolution.py` |
| `??` | `source_script` | `scripts/build_sec_point_in_time_hq_auto_reuse_spotcheck_acceptance.py` |
| `??` | `source_script` | `scripts/build_sec_point_in_time_hq_parse_review_pattern_candidates.py` |
| `??` | `source_script` | `scripts/build_sec_point_in_time_hq_residual_geocode_candidates.py` |
| `??` | `source_script` | `scripts/build_sec_point_in_time_hq_review_queues.py` |
| `??` | `source_script` | `scripts/build_sec_point_in_time_hq_scaleup_gate.py` |
| `??` | `source_script` | `scripts/build_working_tree_hygiene_checkpoint.py` |
| `??` | `source_script` | `scripts/build_xfactor_evidence_center.py` |
| `??` | `source_script` | `scripts/run_institutional_anchor_provider_geocode_census_batch.py` |
| `??` | `source_script` | `scripts/run_institutional_anchor_provider_geocode_external_manual_osm_batch.py` |
| `??` | `source_script` | `scripts/run_institutional_anchor_provider_geocode_external_manual_residual_census_retry.py` |
| `??` | `source_script` | `scripts/run_sec_point_in_time_hq_pending_geocode_census_batch.py` |

## Boundary

- This checkpoint does not stage, commit, revert, or delete files.
- It is an audit aid for deciding the next Git checkpoint.
