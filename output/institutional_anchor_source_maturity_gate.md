# Institutional Anchor Source Maturity Gate

## TLDR

- Status: `source_maturity_match_gate_ready_provider_geocode_review_open`.
- Production model/rank/dashboard change: `False`.
- Decision: Institutional anchors can support report-only evidence and archetype review queues. Production feature/rank promotion remains blocked until provider geocode review, remaining product-county issues, and leakage checks are resolved.
- Next action: Run the external/manual geocoder packet for 18 residual provider rows (1 weak same-FIPS context, 17 same-city unresolved, 0 external), then dry-run/apply the acceptance validator (0 rows currently pending review; 29 accepted and 128 held in latest validator output) or continue the residual Census retry lane (4 accepted, 124 held in latest retry acceptance) and residual context spot-check (8 accepted, 18 held in latest context acceptance) or continue the OSM/Nominatim external geocoder lane (32 accepted, 51 held in latest OSM acceptance) and same-city OSM/Nominatim lane (12 accepted, 20 held in latest same-city OSM acceptance) or work the residual triage packet (18 rows; 0 external follow-up; 0 P0) or review the CMS HGI P0 closeout lane (24 accepted, 1 held) or continue the CMS HGI P1 closeout lane (12 accepted, 6 held) and the CMS HGI P1 territory closeout lane (4 accepted, 1 held) or review the P1 Guayama authoritative lane (1 accepted, 0 held) or review the authoritative P0 closeout lane (1 accepted, 0 held) or review the P2 authoritative external-follow-up lane (8 accepted, 0 held) and rerun provider geocode/source maturity before any promotion review.

## Gate Checks

| Check | Pass |
|---|---:|
| `full_cms_extract_loaded` | `True` |
| `cms_all_jurisdiction_fips_match_share_ge_90` | `True` |
| `cms_product_universe_fips_match_share_ge_90` | `True` |
| `non_product_jurisdictions_classified` | `True` |
| `provider_geocode_review_queue_built` | `True` |
| `panel_has_dual_source_rows` | `True` |
| `review_queue_built` | `True` |
| `missingness_by_state_built` | `True` |

## Metrics

| Metric | Value |
|---|---:|
| `ipeds_rows` | 6163 |
| `cms_rows` | 6103 |
| `panel_county_year_rows` | 3531 |
| `panel_counties` | 2598 |
| `cms_source_mode` | full_annual_csv |
| `cms_matched_fips_share` | 0.9963952154678027 |
| `cms_product_universe_matched_fips_share` | 0.9978412487545666 |
| `review_rows` | 2059 |
| `high_priority_review_rows` | 20 |
| `medium_priority_review_rows` | 1774 |
| `provider_geocode_review_rows` | 19 |
| `provider_geocode_same_zip_candidate_rows` | 4 |
| `provider_geocode_same_city_candidate_rows` | 18 |
| `provider_geocode_external_required_rows` | 0 |
| `provider_geocode_closeout_packet_rows` | 22 |
| `provider_geocode_closeout_local_candidate_rows` | 22 |
| `provider_geocode_closeout_same_zip_rows` | 4 |
| `provider_geocode_closeout_same_city_rows` | 18 |
| `provider_geocode_closeout_external_rows` | 0 |
| `provider_geocode_same_zip_accepted_override_rows` | 184 |
| `provider_geocode_same_zip_latest_accepted_override_rows` | 1 |
| `provider_geocode_same_zip_accepted_counties` | 1 |
| `provider_geocode_census_input_rows` | 413 |
| `provider_geocode_census_matched_result_rows` | 316 |
| `provider_geocode_same_city_census_confirmed_rows` | 77 |
| `provider_geocode_external_census_candidate_ready_rows` | 139 |
| `provider_geocode_external_census_accepted_override_rows` | 139 |
| `provider_geocode_external_census_latest_accepted_override_rows` | 139 |
| `provider_geocode_external_census_accepted_counties` | 128 |
| `provider_geocode_same_city_census_accepted_override_rows` | 77 |
| `provider_geocode_same_city_census_latest_accepted_override_rows` | 77 |
| `provider_geocode_same_city_census_accepted_counties` | 66 |
| `provider_geocode_same_city_review_packet_rows` | 18 |
| `provider_geocode_same_city_strict_conflict_candidate_rows` | 0 |
| `provider_geocode_same_city_strict_non_exact_same_fips_candidate_rows` | 0 |
| `provider_geocode_same_city_context_same_fips_rows` | 1 |
| `provider_geocode_same_city_unresolved_after_census_rows` | 17 |
| `provider_geocode_same_city_census_conflict_corrected_override_rows` | 4 |
| `provider_geocode_same_city_census_conflict_latest_accepted_override_rows` | 4 |
| `provider_geocode_same_city_census_conflict_accepted_counties` | 4 |
| `provider_geocode_same_city_census_context_accepted_override_rows` | 14 |
| `provider_geocode_same_city_census_context_latest_accepted_override_rows` | 14 |
| `provider_geocode_same_city_census_context_accepted_counties` | 13 |
| `provider_geocode_same_city_census_spotcheck_accepted_override_rows` | 18 |
| `provider_geocode_same_city_census_non_exact_conflict_corrected_override_rows` | 1 |
| `provider_geocode_same_city_census_spotcheck_latest_accepted_override_rows` | 19 |
| `provider_geocode_same_city_census_spotcheck_latest_held_rows` | 1 |
| `provider_geocode_same_city_census_spotcheck_accepted_counties` | 16 |
| `provider_geocode_external_manual_packet_rows` | 18 |
| `provider_geocode_external_manual_weak_same_fips_rows` | 1 |
| `provider_geocode_external_manual_same_city_unresolved_rows` | 17 |
| `provider_geocode_external_manual_external_geocoder_rows` | 0 |
| `provider_geocode_external_manual_high_priority_rows` | 12 |
| `provider_geocode_external_manual_accepted_override_rows` | 135 |
| `provider_geocode_external_manual_acceptance_result_rows` | 157 |
| `provider_geocode_external_manual_acceptance_pending_review_rows` | 0 |
| `provider_geocode_external_manual_acceptance_accepted_override_rows` | 29 |
| `provider_geocode_external_manual_acceptance_held_or_rejected_rows` | 128 |
| `provider_geocode_external_manual_acceptance_rejected_conflict_rows` | 0 |
| `provider_geocode_external_manual_residual_retry_attempt_rows` | 193 |
| `provider_geocode_external_manual_residual_retry_matched_result_rows` | 42 |
| `provider_geocode_external_manual_residual_retry_exact_conflict_corrected_rows` | 4 |
| `provider_geocode_external_manual_residual_retry_acceptance_accepted_override_rows` | 4 |
| `provider_geocode_external_manual_residual_retry_acceptance_held_or_rejected_rows` | 124 |
| `provider_geocode_external_manual_residual_context_spotcheck_review_rows` | 26 |
| `provider_geocode_external_manual_residual_context_spotcheck_accepted_review_rows` | 8 |
| `provider_geocode_external_manual_residual_context_spotcheck_held_review_rows` | 18 |
| `provider_geocode_external_manual_residual_context_spotcheck_acceptance_accepted_override_rows` | 8 |
| `provider_geocode_external_manual_residual_context_spotcheck_acceptance_held_or_rejected_rows` | 18 |
| `provider_geocode_external_manual_osm_geocode_target_rows` | 83 |
| `provider_geocode_external_manual_osm_geocode_attempt_rows` | 257 |
| `provider_geocode_external_manual_osm_geocode_accepted_review_rows` | 32 |
| `provider_geocode_external_manual_osm_geocode_held_review_rows` | 51 |
| `provider_geocode_external_manual_osm_geocode_acceptance_accepted_override_rows` | 32 |
| `provider_geocode_external_manual_osm_geocode_acceptance_held_or_rejected_rows` | 51 |
| `provider_geocode_external_manual_osm_same_city_geocode_target_rows` | 32 |
| `provider_geocode_external_manual_osm_same_city_geocode_attempt_rows` | 98 |
| `provider_geocode_external_manual_osm_same_city_geocode_accepted_review_rows` | 12 |
| `provider_geocode_external_manual_osm_same_city_geocode_held_review_rows` | 20 |
| `provider_geocode_external_manual_osm_same_city_geocode_acceptance_accepted_override_rows` | 12 |
| `provider_geocode_external_manual_osm_same_city_geocode_acceptance_held_or_rejected_rows` | 20 |
| `provider_geocode_external_manual_residual_triage_rows` | 18 |
| `provider_geocode_external_manual_residual_triage_external_followup_rows` | 0 |
| `provider_geocode_external_manual_residual_triage_same_city_manual_review_rows` | 17 |
| `provider_geocode_external_manual_residual_triage_weak_context_manual_review_rows` | 1 |
| `provider_geocode_external_manual_residual_triage_p0_rows` | 0 |
| `provider_geocode_external_manual_p0_cms_hgi_target_rows` | 25 |
| `provider_geocode_external_manual_p0_cms_hgi_found_rows` | 24 |
| `provider_geocode_external_manual_p0_cms_hgi_review_accept_rows` | 24 |
| `provider_geocode_external_manual_p0_cms_hgi_review_held_rows` | 1 |
| `provider_geocode_external_manual_p0_cms_hgi_acceptance_accepted_override_rows` | 24 |
| `provider_geocode_external_manual_p0_cms_hgi_acceptance_held_or_rejected_rows` | 1 |
| `provider_geocode_external_manual_p0_cms_hgi_acceptance_rejected_conflict_rows` | 0 |
| `provider_geocode_external_manual_p1_cms_hgi_target_rows` | 18 |
| `provider_geocode_external_manual_p1_cms_hgi_found_rows` | 18 |
| `provider_geocode_external_manual_p1_cms_hgi_review_accept_rows` | 12 |
| `provider_geocode_external_manual_p1_cms_hgi_review_held_rows` | 6 |
| `provider_geocode_external_manual_p1_cms_hgi_acceptance_accepted_override_rows` | 12 |
| `provider_geocode_external_manual_p1_cms_hgi_acceptance_held_or_rejected_rows` | 6 |
| `provider_geocode_external_manual_p1_cms_hgi_acceptance_rejected_conflict_rows` | 0 |
| `provider_geocode_external_manual_p1_territory_cms_hgi_target_rows` | 5 |
| `provider_geocode_external_manual_p1_territory_cms_hgi_found_rows` | 5 |
| `provider_geocode_external_manual_p1_territory_cms_hgi_review_accept_rows` | 4 |
| `provider_geocode_external_manual_p1_territory_cms_hgi_review_held_rows` | 1 |
| `provider_geocode_external_manual_p1_territory_cms_hgi_acceptance_accepted_override_rows` | 4 |
| `provider_geocode_external_manual_p1_territory_cms_hgi_acceptance_held_or_rejected_rows` | 1 |
| `provider_geocode_external_manual_p1_territory_cms_hgi_acceptance_rejected_conflict_rows` | 0 |
| `provider_geocode_external_manual_p1_guayama_authoritative_target_rows` | 1 |
| `provider_geocode_external_manual_p1_guayama_authoritative_source_rows` | 4 |
| `provider_geocode_external_manual_p1_guayama_authoritative_review_accept_rows` | 1 |
| `provider_geocode_external_manual_p1_guayama_authoritative_review_held_rows` | 0 |
| `provider_geocode_external_manual_p1_guayama_authoritative_acceptance_accepted_override_rows` | 1 |
| `provider_geocode_external_manual_p1_guayama_authoritative_acceptance_held_or_rejected_rows` | 0 |
| `provider_geocode_external_manual_p1_guayama_authoritative_acceptance_rejected_conflict_rows` | 0 |
| `provider_geocode_external_manual_p0_authoritative_target_rows` | 1 |
| `provider_geocode_external_manual_p0_authoritative_nppes_found_rows` | 1 |
| `provider_geocode_external_manual_p0_authoritative_census_matched_rows` | 1 |
| `provider_geocode_external_manual_p0_authoritative_review_accept_rows` | 1 |
| `provider_geocode_external_manual_p0_authoritative_review_held_rows` | 0 |
| `provider_geocode_external_manual_p0_authoritative_acceptance_accepted_override_rows` | 1 |
| `provider_geocode_external_manual_p0_authoritative_acceptance_held_or_rejected_rows` | 0 |
| `provider_geocode_external_manual_p0_authoritative_acceptance_rejected_conflict_rows` | 0 |
| `provider_geocode_external_manual_p2_authoritative_target_rows` | 8 |
| `provider_geocode_external_manual_p2_authoritative_source_rows` | 19 |
| `provider_geocode_external_manual_p2_authoritative_nppes_found_rows` | 5 |
| `provider_geocode_external_manual_p2_authoritative_review_accept_rows` | 8 |
| `provider_geocode_external_manual_p2_authoritative_review_held_rows` | 0 |
| `provider_geocode_external_manual_p2_authoritative_acceptance_accepted_override_rows` | 8 |
| `provider_geocode_external_manual_p2_authoritative_acceptance_held_or_rejected_rows` | 0 |
| `provider_geocode_external_manual_p2_authoritative_acceptance_rejected_conflict_rows` | 0 |
| `unresolved_product_county_fips_rows` | 1 |
| `institutional_feature_column_count` | 0 |
| `states_with_cms_unmatched_rows` | 11 |

## Sub-Gates

| Gate | Status |
|---|---|
| `provider_geocode_review` | `provider_geocode_review_candidates_ready_report_only` |
| `provider_geocode_closeout_packet` | `provider_geocode_closeout_packet_ready_report_only` |
| `provider_geocode_closeout_acceptance` | `provider_same_zip_closeout_accepted_report_only` |
| `provider_geocode_census_batch` | `census_candidates_ready_report_only` |
| `provider_geocode_census_acceptance` | `same_city_census_overrides_accepted_report_only` |
| `provider_geocode_external_census_acceptance` | `external_census_overrides_accepted_report_only` |
| `provider_geocode_same_city_review_packet` | `same_city_review_packet_ready_report_only` |
| `provider_geocode_same_city_conflict_acceptance` | `same_city_conflict_census_overrides_accepted_report_only` |
| `provider_geocode_same_city_context_acceptance` | `same_city_context_census_overrides_accepted_report_only` |
| `provider_geocode_same_city_spotcheck_acceptance` | `same_city_spotcheck_overrides_accepted_report_only` |
| `provider_geocode_external_manual_packet` | `external_manual_geocoder_packet_ready_report_only` |
| `provider_geocode_external_manual_acceptance` | `external_manual_overrides_accepted_report_only` |
| `provider_geocode_external_manual_residual_census_retry` | `residual_census_retry_candidates_ready_report_only` |
| `provider_geocode_external_manual_residual_census_retry_acceptance` | `external_manual_overrides_accepted_report_only` |
| `provider_geocode_external_manual_residual_context_spotcheck` | `strict_residual_census_context_spotcheck_results_ready_report_only` |
| `provider_geocode_external_manual_residual_context_spotcheck_acceptance` | `external_manual_overrides_accepted_report_only` |
| `provider_geocode_external_manual_osm_geocode` | `osm_nominatim_external_geocoder_results_ready_report_only` |
| `provider_geocode_external_manual_osm_geocode_acceptance` | `external_manual_overrides_accepted_report_only` |
| `provider_geocode_external_manual_osm_same_city_geocode` | `osm_nominatim_external_geocoder_results_ready_report_only` |
| `provider_geocode_external_manual_osm_same_city_geocode_acceptance` | `external_manual_overrides_accepted_report_only` |
| `provider_geocode_external_manual_residual_triage` | `external_manual_residual_triage_ready_report_only` |
| `provider_geocode_external_manual_p0_cms_hgi_review` | `cms_hgi_p0_review_has_accepted_rows` |
| `provider_geocode_external_manual_p0_cms_hgi_acceptance` | `external_manual_overrides_accepted_report_only` |
| `provider_geocode_external_manual_p1_cms_hgi_review` | `cms_hgi_p1_review_has_accepted_rows` |
| `provider_geocode_external_manual_p1_cms_hgi_acceptance` | `external_manual_overrides_accepted_report_only` |
| `provider_geocode_external_manual_p1_territory_cms_hgi_review` | `cms_hgi_p1_review_has_accepted_rows` |
| `provider_geocode_external_manual_p1_territory_cms_hgi_acceptance` | `external_manual_overrides_accepted_report_only` |
| `provider_geocode_external_manual_p1_guayama_authoritative_review` | `p1_guayama_authoritative_review_has_accepted_rows` |
| `provider_geocode_external_manual_p1_guayama_authoritative_acceptance` | `external_manual_overrides_accepted_report_only` |
| `provider_geocode_external_manual_p0_authoritative_review` | `p0_authoritative_review_has_accepted_rows` |
| `provider_geocode_external_manual_p0_authoritative_acceptance` | `external_manual_overrides_accepted_report_only` |
| `provider_geocode_external_manual_p2_authoritative_review` | `p2_authoritative_review_has_accepted_rows` |
| `provider_geocode_external_manual_p2_authoritative_acceptance` | `external_manual_overrides_accepted_report_only` |
| `leakage_gate` | `training_blocked_insufficient_historical_observed_years` |

## Top Review Issues

| Issue | Priority | Rows |
|---|---|---:|
| `fiscal_year_outside_2023` | `medium` | 1000 |
| `missing_net_patient_revenue` | `medium` | 237 |
| `missing_enrollment_total` | `medium` | 204 |
| `inactive_or_nonstandard_status` | `low` | 191 |
| `missing_discharges_total` | `medium` | 121 |
| `missing_beds_total` | `medium` | 112 |
| `missing_total_costs` | `medium` | 82 |
| `non_product_jurisdiction_classified` | `low` | 72 |
| `cms_county_missing_provider_geocode_required` | `high` | 19 |
| `duplicate_provider_fiscal_year` | `medium` | 18 |
| `non_product_jurisdiction_unmatched` | `low` | 2 |
| `county_fips_unmatched` | `high` | 1 |

## States With Lowest CMS FIPS Match

| State | CMS Rows | Match Share | Unmatched |
|---|---:|---:|---:|
| PR | 64 | 85.9% | 9 |
| VT | 16 | 93.8% | 1 |
| NV | 56 | 98.2% | 1 |
| MD | 58 | 98.3% | 1 |
| WV | 62 | 98.4% | 1 |
| OK | 152 | 98.7% | 2 |
| NE | 96 | 99.0% | 1 |
| LA | 205 | 99.0% | 2 |
| FL | 264 | 99.6% | 1 |
| TX | 587 | 99.7% | 2 |
| CA | 407 | 99.8% | 1 |
| OH | 231 | 100.0% | 0 |
| PA | 212 | 100.0% | 0 |
| IL | 210 | 100.0% | 0 |
| NY | 189 | 100.0% | 0 |

## Boundary

- This gate is report-only. It is suitable for review queues and opt-in evidence surfaces.
- Do not use the institutional panel in model training, scoring, default ranks, or source promotion until the review and leakage gates are explicitly cleared.
