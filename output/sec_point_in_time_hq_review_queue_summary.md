# SEC Point-In-Time HQ Review Queues

## TLDR

- Status: `sec_point_in_time_review_queues_ready_report_only`.
- Production model/rank/dashboard change: `False`.
- Decision: Use these queues for operator review before any SEC source-promotion review.
- Next action: Review 0 open auto snapshot reuses after strict Census and held-row resolution, keep parsed geocode review closed, and decide whether parser-pattern work is worth doing for the remaining parse-review rows.
- Auto-reuse spot checks accepted total: `203`.
- Auto-reuse strict Census acceptances: `15`.
- Auto-reuse held-row resolution acceptances: `6`.
- Auto-reuse final external-evidence acceptances: `4`.
- Auto-reuse spot checks open after final external evidence: `0`.

## Metrics

| Metric | Value |
|---|---:|
| `reviewed_rows` | 521 |
| `point_in_time_ready_rows` | 367 |
| `geocode_ready_rows` | 367 |
| `manual_or_matched_geocode_ready_rows` | 85 |
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
| `pending_geocode_rows` | 0 |
| `parse_review_rows` | 154 |
| `county_year_candidate_rows` | 216 |

## Auto Reuse Priority Counts

- `low`: `161`
- `high`: `69`
- `medium`: `52`

## Pending Geocode Reason Counts

- None.

## Parse Review Category Counts

- `address_marker_or_address_text_not_found`: `98`
- `city_zip_found_street_pattern_unclear`: `29`
- `snapshot_address_text_found_needs_parser_pattern`: `23`
- `fetch_or_cache_failure`: `4`

## Boundary

- These queues are report-only operator worklists.
- They do not change SEC source promotion, model features, scoring, ranks, Product Mode policy, or feature eligibility.
