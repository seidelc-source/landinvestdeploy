# X-Factor Evidence Center

## TLDR

- Status: `report_only_evidence_center_ready`.
- Production model/rank/dashboard change: `False`.
- Decision: Use this as the report-only operating center for x-factor evidence. Keep all default model/rank promotions behind source, rank, and ablation gates.

## Surfaces

| Rank | Surface | Family | Status | Allowed Use | Display | Priority | Blocker | Next Action |
|---:|---|---|---|---|---|---:|---|---|
| 1 | Guarded pre-boom two-score blend | preboom_shortlist | `opt_in_evidence_panel_ready` | opt-in report-only panel | County Evidence Panel | 100.0 | guarded_shortlist_only | Show in opt-in evidence panel with report-only label. |
| 2 | Land optionality breakout V1 | analog_label | `operator_review_before_display` | memo/context or research queue | County Evidence Panel | 97.0 | source_and_false_positive_review_required | Review false-positive/already-hot behavior before display expansion. |
| 3 | Quiet breakout label V1 | analog_label | `operator_review_before_display` | memo/context or research queue | County Evidence Panel | 67.1 | source_and_false_positive_review_required | Review false-positive/already-hot behavior before display expansion. |
| 4 | Announcement anchor events | corporate_anchor_event | `report_only_display_gate_spec_ready_default_rank_blocked` | opt-in display with source/status labels | Evidence Panel: Events | 55.0 | default_product_rank_or_score_influence | opt_in_report_only_event_evidence_panel_or_packet_section |
| 5 | Institutional anchor official panel | institutional_anchor | `source_maturity_match_gate_ready_provider_geocode_review_open` | report-only evidence and archetype review | Evidence Panel / archetype queue | 50.0 | 19 provider geocode rows (4 ZIP, 18 city, 0 external; 22 local closeout candidates); 184 same-ZIP and 77 Census-confirmed same-city overrides accepted report-only; 4 exact Census same-city conflict corrections accepted report-only; 14 non-exact same-FIPS Census context overrides accepted report-only; 18 same-FIPS spot-check rows and 1 non-exact conflict corrections accepted report-only; 139 external Census overrides accepted report-only from 139 staged candidates; 18 residual rows packaged for external/manual geocoding (1 weak same-FIPS context, 17 same-city unresolved, 0 external geocoder); latest validator has 0 pending review rows, 29 accepted overrides, and 128 held rows; residual Census retry matched 42 rows and accepted 4 exact conflict corrections with 124 held; residual context spot-check reviewed 26 rows, accepted 8, and held 18; OSM external geocoder reviewed 83 rows, accepted 32, and held 51; OSM same-city geocoder reviewed 32 rows, accepted 12, and held 20; residual triage packet has 18 rows, 0 external follow-up rows, and 0 P0 rows; CMS HGI P0 review accepted 24 rows, applied 24, and held 1; CMS HGI P1 review accepted 12 rows, applied 12, and held 6; CMS HGI P1 territory review accepted 4 rows, applied 4, and held 1; P1 Guayama authoritative review accepted 1 rows, applied 1, and held 0; authoritative P0 review accepted 1 rows, applied 1, and held 0; P2 authoritative review accepted 8 rows, applied 8, and held 0; external/manual total accepted overrides now 135; training_blocked_insufficient_historical_observed_years | Run the 18-row external/manual geocoder packet, dry-run the acceptance validator, accept only reviewed county assignments, and keep default feature columns at 0 until ablation gates clear. |
| 6 | 5yr rank-band boundary gate | rank_stability | `report_only_rank_band_gate_built_no_promotion` | operator-review labels only | Evidence Panel: 5yr Boundary | 45.0 | 10 inside do-not-promote boundary rows | Use top-25 only for operator acceptance; keep top-50/top-100 blocked where do-not-promote rows remain. |
| 7 | College/medical archetype gap closure | institutional_anchor | `report_only_college_medical_archetype_gap_closure_ready` | shortlist/review queue only | Research queue | 44.0 | source maturity and model-impact gates not cleared | Review top 100 gap-closure rows for geographic and false-positive behavior. |
| 8 | Pre-boom archetype diversity queue | preboom_archetypes | `report_only_diversity_followup_ready_no_promotion` | balanced review queue | Research queue | 37.0 | 2 archetype gaps remain | Backfill remaining energy/logistics archetype gaps before treating archetype coverage as complete. |
| 9 | Anchor/halo support x land optionality | xfactor_interaction | `report_only_memo_context` | memo/context or research queue | County Evidence Panel | 35.7 | model-ablation-candidate | Keep as memo/context evidence; do not promote into default rank. |
| 10 | Anchor/halo support x buildability | xfactor_interaction | `research_queue` | memo/context or research queue | County Evidence Panel | 31.2 | report-only | Keep in research queue and gather cleaner evidence. |
| 11 | National CBP P0 diagnostic | business_pattern_diagnostic | `p0_national_cbp_product_gate_complete` | product diagnostic only | Research queue | 27.0 | top-100 P0 capture did not improve default rank behavior | Keep as report-only P0 diagnostic until controlled model/source gates pass. |
| 12 | Sector depth x low prior momentum | xfactor_interaction | `research_queue` | memo/context or research queue | County Evidence Panel | 17.1 | report-only | Keep in research queue and gather cleaner evidence. |
| 13 | Controlled X-factor ablation sprint | model_gate | `controlled_report_only_ablation_sprint_complete` | promotion gate evidence only | Research queue | 15.0 | do_not_promote_current_xfactor_surfaces | Keep as contextual evidence; investigate capped overlay instead of raw feature promotion. |
| 14 | Logistics/trade depth x low prior momentum | xfactor_interaction | `research_queue` | memo/context or research queue | County Evidence Panel | 9.8 | report-only | Keep in research queue and gather cleaner evidence. |
| 15 | Peer price spillover x state-relative value | xfactor_interaction | `research_queue` | memo/context or research queue | County Evidence Panel | 7.1 | report-only | Keep in research queue and gather cleaner evidence. |
| 16 | SEC point-in-time HQ scale-up | corporate_hq_history | `scaleup_county_year_ready_source_maturity_blocked` | report-only source maturity queue | Research queue | 7.0 | current-address snapshot semantics still block promotion; 203 of 282 auto snapshot-reuse rows accepted (15 strict Census closeouts, 6 held-row resolutions, 4 final external-evidence rows), 0 held open; 17 county closeout candidates (15 strict Census), 8 pre-acceptance remaining review rows; 23 candidate queue rows accepted, 0 parsed geocode rows unresolved; 7 parser-pattern candidates and 96 manual parse rows | Auto-reuse spot checks are closed; implement 7 parser-pattern candidates and keep 96 rows in manual parse review. |
| 17 | Anchor/halo support x affordability | xfactor_interaction | `research_queue` | memo/context or research queue | County Evidence Panel | 4.4 | report-only | Keep in research queue and gather cleaner evidence. |
| 18 | Scarcity x buildability | xfactor_interaction | `report_only_memo_context` | memo/context or research queue | County Evidence Panel | 4.2 | model-ablation-candidate | Keep as memo/context evidence; do not promote into default rank. |

## Metrics

- `surfaces`: `18`
- `evidence_panel_surfaces`: `13`
- `research_queue_surfaces`: `5`
- `high_risk_surfaces`: `5`

## Boundary

- The Evidence Center is an operating/readiness artifact only.
- It does not alter production model features, scoring, county ranks, Product Mode policy, source promotion, or dashboard defaults.
