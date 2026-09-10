# Source Registry Report

## TLDR

- Task: `XB-120`.
- Status: `report_only_complete`.
- Production model/rank/dashboard change: `False`.
- Sources: `15`.
- OK: `13`.
- Needs review/missing: `2`.

## Sources

| Source | Family | Eligibility | Promotion Status | Path Coverage | Max Year | Audit |
|---|---|---|---|---:|---:|---|
| noaa_sea_level | climate_hazard | report_only | guarded_candidate | 100.0% |  | ok |
| corporate_anchor_spillover | corporate_anchor | report_only | curated_source_quality_blocked | 100.0% | 2024 | ok |
| announcement_anchor_events | corporate_anchor_event | report_only | promotion_candidate_display_gate_required | 100.0% | 2024 | ok |
| census_1990_pep_demographics | demographics | research | long_history_research_panel | 100.0% | 1999 | ok |
| pre1990_decennial_demographics | demographics | research | staged_population_only | 100.0% | 2000 | ok |
| cbp_anchor_size_national_candidate | establishments_anchor_size | report_only | source_policy_gate_required | 100.0% | 2023 | ok |
| bls_qcew_core | labor | production_eligible_existing | default_panel | 100.0% | 2024 | ok |
| qcew_sector_mix | labor_sector_mix | diagnostic_only | report_only_rejected_direct_training | 100.0% | 2023 | ok |
| wave3_static_land_sources | land_supply_hazard | product_overlay_report_only | capped_overlay_preferred | 100.0% | 2024 | ok |
| ntad_freight_access | logistics_access | panel_product_only | static_snapshot_report_only | 100.0% |  | ok |
| zillow_zhvi | price_history | production_eligible_existing | default_panel | 100.0% | 2024 | ok |
| fhfa_county_hpi | public_price_history | production_eligible_existing | default_panel | 100.0% | 2024 | ok |
| usgs_hydrography | water_hydrography | product_context | staging_documented | 100.0% |  | ok |
| sec_edgar_hq_expansion | corporate_anchor | report_only | source_maturity_blocked_point_in_time_scaleup_open | 100.0% | 2026 | qa_review_needed |
| institutional_anchor_ipeds_cms_hcris | institutional_anchor | report_only | full_extract_match_gate_ready_provider_geocode_review_open_p2_authoritative_external_followup_closed_report_only | 100.0% | 2024 | qa_review_needed |

## Boundary

- The registry is descriptive and does not change source eligibility.
- Promotion still requires the source-specific gates listed in the backlog and promotion-gate documentation.
