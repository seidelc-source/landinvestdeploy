# Institutional Anchor Provider External/Manual Acceptance

## TLDR

- Status: `external_manual_overrides_accepted_report_only`.
- Apply mode: `True`.
- Production model/rank/dashboard change: `False`.
- Decision: Validated reviewed external/manual geocode rows. Accepted rows are report-only provider-year overrides only when reviewer decision, FIPS/state, confidence, source, match type, reviewer, and note checks pass.
- Next action: Rerun the institutional official panel, provider review, closeout packet, external/manual packet, source maturity gate, registry, Evidence Center, and deploy bundle.

## Metrics

| Metric | Value |
|---|---:|
| `result_rows` | 25 |
| `packet_rows` | 72 |
| `reviewer_accept_rows` | 24 |
| `pending_review_rows` | 0 |
| `accepted_override_rows` | 24 |
| `accepted_provider_years` | 24 |
| `accepted_candidate_counties` | 23 |
| `held_or_rejected_rows` | 1 |
| `skipped_existing_override_rows` | 0 |
| `skipped_duplicate_agrees_rows` | 0 |
| `rejected_conflict_rows` | 0 |
| `manual_override_rows_before` | 522 |
| `manual_override_rows_after` | 546 |

## Acceptance Status Counts

- `accepted`: `24`
- `held_or_rejected`: `1`

## Acceptance Rules

- Accepted rows require reviewer decision `accept` or equivalent.
- Provider/year must exist in the external/manual packet and must not conflict with existing overrides.
- Manual FIPS must resolve to the provider state in the county lookup.
- Manual confidence must be at least `0.85`.
- Geocode source, non-low-precision match type, reviewer, reviewed timestamp, and a substantive note are required.

## Boundary

- This script is dry-run unless `--apply` is passed.
- Accepted rows are report-only source-review overrides for the institutional panel builder.
- Do not use institutional anchors in model training, scoring, default ranks, Product Mode policy, source promotion, or feature eligibility until all maturity, leakage, and model-impact gates pass.
