# Institutional Anchor External/Manual Residual Census Retry

## TLDR

- Status: `residual_census_retry_candidates_ready_report_only`.
- Production model/rank/dashboard change: `False`.
- Decision: Residual Census retry candidates are staged as report-only source-review evidence.
- Next action: Dry-run the external/manual acceptance validator against the residual retry results, then apply only if accepted rows are conflict-free.

## Metrics

| Metric | Value |
|---|---:|
| `packet_rows` | 128 |
| `attempt_rows` | 193 |
| `census_submitted` | True |
| `raw_result_rows` | 193 |
| `matched_result_rows` | 42 |
| `candidate_rows` | 128 |
| `reviewer_accept_rows` | 4 |
| `same_city_exact_confirmed_rows` | 0 |
| `same_city_exact_conflict_corrected_rows` | 4 |
| `external_exact_candidate_ready_rows` | 0 |
| `weak_context_exact_confirmed_rows` | 0 |
| `held_result_rows` | 124 |

## Candidate Status Counts

- `residual_census_context_only`: `26`
- `same_city_residual_census_exact_conflict_correction`: `4`
- `unresolved_after_residual_census_retry`: `98`

## Boundary

- This retry only writes report-only review evidence and a validator-ready results CSV.
- It does not append provider overrides; use the external/manual acceptance validator for that.
- Institutional anchors remain out of production model features, scoring, ranks, Product Mode policy, source promotion, and feature eligibility until all maturity, leakage, and model-impact gates clear.
