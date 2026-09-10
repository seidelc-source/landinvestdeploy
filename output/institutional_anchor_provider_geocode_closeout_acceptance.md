# Institutional Anchor Provider Geocode Closeout Acceptance

## TLDR

- Status: `provider_same_zip_closeout_accepted_report_only`.
- Production model/rank/dashboard change: `False`.
- Decision: Accepted only same-state/same-ZIP unique matched CMS provider county candidates into the report-only institutional provider geocode override file.
- Next action: Rerun the institutional official source panel, provider geocode review, source maturity gate, Evidence Center, and deploy bundle. Same-city and external-geocode provider rows remain blocked.

## Metrics

| Metric | Value |
|---|---:|
| `packet_rows` | 177 |
| `same_zip_packet_rows` | 1 |
| `accepted_override_rows` | 1 |
| `accepted_provider_years` | 1 |
| `accepted_candidate_counties` | 1 |
| `skipped_duplicate_agrees_rows` | 0 |
| `skipped_existing_override_rows` | 0 |
| `rejected_or_held_rows` | 176 |
| `same_city_rows_left_unaccepted` | 56 |
| `external_geocode_rows_left_unaccepted` | 120 |
| `local_closeout_rows_remaining_after_acceptance` | 56 |
| `manual_override_rows_before` | 417 |
| `manual_override_rows_after` | 418 |

## Boundary

- Same-city and external-geocode rows are intentionally left in review.
- Accepted rows are a report-only source-review override for the institutional panel builder.
- Do not use institutional anchors in model training, scoring, default ranks, or source promotion until all maturity, leakage, and model-impact gates pass.
