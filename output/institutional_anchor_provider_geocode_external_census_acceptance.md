# Institutional Anchor Provider External Census Acceptance

## TLDR

- Status: `external_census_overrides_accepted_report_only`.
- Production model/rank/dashboard change: `False`.
- Decision: Accepted only provider-original exact Census-confirmed external provider rows into the report-only override file.
- Next action: Rerun the institutional official panel, provider review, closeout packet, source maturity gate, registry, Evidence Center, and deploy bundle.

## Metrics

| Metric | Value |
|---|---:|
| `candidate_rows` | 413 |
| `external_census_candidate_ready_rows` | 139 |
| `accepted_override_rows` | 139 |
| `accepted_provider_years` | 139 |
| `accepted_candidate_counties` | 128 |
| `skipped_existing_override_rows` | 0 |
| `skipped_duplicate_agrees_rows` | 0 |
| `held_or_rejected_rows` | 274 |
| `manual_override_rows_before` | 259 |
| `manual_override_rows_after` | 398 |

## Acceptance Status Counts

- `accepted`: `139`
- `held_or_rejected`: `274`

## Boundary

- Only external rows with provider-original exact Census confirmation are accepted.
- Institutional anchors remain report-only until source-maturity, leakage, and model-impact gates clear.
