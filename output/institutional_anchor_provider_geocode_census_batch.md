# Institutional Anchor Provider Census Geocode Batch

## TLDR

- Status: `census_candidates_ready_report_only`.
- Production model/rank/dashboard change: `False`.
- Decision: Census geocoder candidates are staged for institutional provider source review only.
- Next action: Accept only same-city Census-confirmed rows through the controlled acceptance script; keep external candidates staged for separate policy review.

## Metrics

| Metric | Value |
|---|---:|
| `input_provider_rows` | 413 |
| `same_city_input_rows` | 152 |
| `external_input_rows` | 261 |
| `census_attempt_rows` | 432 |
| `census_submitted` | True |
| `raw_result_rows` | 432 |
| `matched_result_rows` | 316 |
| `candidate_rows` | 413 |
| `same_city_census_confirmed_rows` | 77 |
| `same_city_census_conflict_rows` | 5 |
| `external_census_candidate_ready_rows` | 139 |
| `unresolved_rows` | 106 |

## Candidate Status Counts

- `external_census_candidate_ready`: `139`
- `external_census_context_only`: `53`
- `same_city_census_confirms_candidate`: `77`
- `same_city_census_conflicts_candidate`: `5`
- `same_city_census_context_only`: `33`
- `unresolved_after_census_batch`: `106`

## Boundary

- This batch is report-only source-review evidence.
- It does not modify institutional provider overrides, source promotion, model features, scoring, ranks, or dashboard defaults.
