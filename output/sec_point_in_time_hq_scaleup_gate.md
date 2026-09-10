# SEC Point-In-Time HQ Scale-Up Gate

## TLDR

- Status: `scaleup_county_year_ready_source_maturity_blocked`.
- Production model/rank/dashboard change: `False`.
- Decision: SEC point-in-time HQ remains report-only. Accepted Census-backed geocode candidates reduce open geocode review, and the auto-reuse spot-check / county-closeout / held-row packets reduce the open review queue, but current-address snapshot semantics and any remaining auto-reuse spot checks still block source promotion.

## Metrics

| Metric | Value |
|---|---:|
| `filing_queue_rows` | 521 |
| `parsed_vintage_rows` | 521 |
| `parsed_point_in_time_ready_rows` | 367 |
| `reviewed_point_in_time_ready_rows` | 367 |
| `geocode_ready_rows` | 367 |
| `parse_review_rows` | 154 |
| `parse_review_pattern_candidate_rows` | 7 |
| `parse_review_manual_rows` | 96 |
| `county_year_candidate_rows` | 216 |
| `county_year_candidate_counties` | 69 |
| `auto_snapshot_reuse_rows` | 282 |
| `auto_snapshot_reuse_spotcheck_accepted_rows` | 203 |
| `auto_snapshot_reuse_spotcheck_base_accepted_rows` | 178 |
| `auto_snapshot_reuse_spotcheck_strict_census_accepted_rows` | 15 |
| `auto_snapshot_reuse_spotcheck_open_rows_before_county_acceptance` | 25 |
| `auto_snapshot_reuse_spotcheck_open_rows_before_held_resolution` | 10 |
| `auto_snapshot_reuse_spotcheck_held_resolution_accepted_rows` | 6 |
| `auto_snapshot_reuse_spotcheck_open_rows_before_final_external_evidence` | 4 |
| `auto_snapshot_reuse_spotcheck_final_external_evidence_accepted_rows` | 4 |
| `auto_snapshot_reuse_spotcheck_open_rows` | 0 |
| `auto_snapshot_reuse_county_closeout_candidate_rows` | 17 |
| `auto_snapshot_reuse_county_closeout_strict_census_rows` | 15 |
| `auto_snapshot_reuse_county_closeout_local_same_zip_rows` | 2 |
| `auto_snapshot_reuse_county_closeout_remaining_rows` | 8 |
| `auto_snapshot_reuse_county_closeout_conflict_rows` | 0 |
| `auto_snapshot_reuse_county_closeout_held_rows` | 10 |
| `auto_snapshot_reuse_held_resolution_rows_after_resolution` | 4 |
| `auto_snapshot_reuse_final_external_evidence_rows_after_resolution` | 0 |
| `manual_applied_review_rows` | 85 |
| `pending_point_in_time_geocode_rows` | 0 |
| `pending_geocode_candidate_matched_rows` | 9 |
| `pending_geocode_candidate_unresolved_rows` | 0 |
| `pending_geocode_override_candidate_rows` | 6 |
| `accepted_pending_geocode_override_rows` | 6 |
| `accepted_pending_geocode_queue_rows` | 9 |
| `accepted_residual_geocode_override_rows` | 12 |
| `accepted_residual_geocode_queue_rows` | 14 |

## Lane Status

| Lane | Status | Rows | Ready Rows | Blocker | Next Action |
|---|---|---:|---:|---|---|
| `filing_queue` | `available` | 521 | 410 | none | continue bounded parse batches |
| `address_parse` | `report_only_address_parse_batch_built` | 521 | 367 | parse review rows open | implement parser patterns for 7 candidate rows; keep 96 rows in manual/alternate-document review |
| `geocode_review` | `report_only_geocode_review_applied` | 521 | 367 | none | auto same-city/state/ZIP reuse spot checks accepted |
| `county_year_candidates` | `built` | 216 | 216 | none | keep report-only until SEC source maturity passes |
| `source_maturity` | `source_maturity_blocked` | 216 | 367 | current_address_snapshot_not_point_in_time | Geocode review and first county-year candidates are ready; extend the filing parse batch and rerun source maturity before promotion review. |

## Parse Status Counts

- `fetch_failed_or_missing`: `4`
- `parse_review_needed`: `150`
- `parsed_principal_office_city_zip_context`: `41`
- `parsed_principal_office_marker`: `303`
- `parsed_principal_office_marker_snapshot_zip_fallback`: `5`
- `parsed_snapshot_address_text_match`: `18`

## Geocode Status Counts

- `manual_review_matched`: `85`
- `not_attempted`: `154`
- `snapshot_geocode_reused_same_city_state_zip`: `282`

## Boundary

- This is a report-only source-maturity artifact.
- It does not change model features, scoring, ranks, Product Mode policy, source promotion, or feature eligibility.
