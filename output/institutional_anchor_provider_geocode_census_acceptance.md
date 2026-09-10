# Institutional Anchor Provider Census Acceptance

## TLDR

- Status: `same_city_census_overrides_accepted_report_only`.
- Production model/rank/dashboard change: `False`.
- Decision: Accepted only exact Census-confirmed same-city provider candidates into the report-only override file.
- Next action: Rerun the institutional official panel, provider review, closeout packet, source maturity gate, registry, Evidence Center, and deploy bundle.

## Metrics

| Metric | Value |
|---|---:|
| `candidate_rows` | 413 |
| `same_city_census_confirmed_rows` | 77 |
| `accepted_override_rows` | 77 |
| `accepted_provider_years` | 77 |
| `accepted_candidate_counties` | 66 |
| `skipped_existing_override_rows` | 0 |
| `skipped_duplicate_agrees_rows` | 0 |
| `held_or_rejected_rows` | 336 |
| `manual_override_rows_before` | 181 |
| `manual_override_rows_after` | 258 |

## Acceptance Status Counts

- `accepted`: `77`
- `held_or_rejected`: `336`

## Boundary

- Only same-city rows with exact Census confirmation are accepted.
- External Census candidates remain staged separately.
- Institutional anchors remain report-only until source-maturity, leakage, and model-impact gates clear.
