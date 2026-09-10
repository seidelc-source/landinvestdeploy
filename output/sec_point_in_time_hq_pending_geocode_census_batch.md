# SEC Pending Point-In-Time HQ Geocode Census Candidate Pass

## TLDR

- Status: `census_candidates_ready_report_only`.
- Production model/rank/dashboard change: `False`.
- Pending geocode rows reviewed: `9`.
- Candidate-matched rows: `9`.
- Census-matched rows: `9`.
- Parser-repair snapshot candidates: `0`.
- Still unresolved after candidate pass: `0`.
- Override candidate rows: `6`.

## Metrics

| Metric | Value |
|---|---:|
| `pending_geocode_rows` | 9 |
| `census_attempt_rows` | 14 |
| `census_submitted` | True |
| `census_result_rows` | 14 |
| `census_match_attempt_rows` | 14 |
| `snapshot_repair_candidate_rows` | 0 |
| `candidate_matched_rows` | 9 |
| `candidate_census_matched_rows` | 9 |
| `candidate_snapshot_repair_rows` | 0 |
| `candidate_unresolved_rows` | 0 |
| `override_candidate_rows` | 6 |
| `candidate_counties` | 3 |
| `conflicting_fips_queue_rows` | 0 |

## Candidate Source Counts

- `census_geographies_addressbatch:parsed_original`: `9`

## Override Candidate Preview

| FIPS | County | Rows | Source |
|---|---|---:|---|
| 36047 | Kings County, New York | 1 | census_geographies_addressbatch:parsed_original |
| 36061 | New York County, New York | 2 | census_geographies_addressbatch:parsed_original |
| 36061 | New York County, New York | 1 | census_geographies_addressbatch:parsed_original |
| 36061 | New York County, New York | 1 | census_geographies_addressbatch:parsed_original |
| 36061 | New York County, New York | 1 | census_geographies_addressbatch:parsed_original |
| 48453 | Travis County, Texas | 3 | census_geographies_addressbatch:parsed_original |

## Decision

- External geocode candidates are staged for operator review only; no candidate is applied automatically.
- Next action: Review the override-candidate CSV, copy accepted rows into the manual override file, then rerun the SEC geocode review and source maturity gates.

## Boundary

- This is a report-only operator-review artifact.
- It does not modify manual overrides, reviewed SEC vintages, county-year candidates, model features, scoring, ranks, Product Mode policy, source promotion, or feature eligibility.
