# Institutional Anchor Same-City Spot-Check Acceptance

## TLDR

- Status: `same_city_spotcheck_overrides_accepted_report_only`.
- Production model/rank/dashboard change: `False`.
- Decision: Accepted only street/intersection-supported Census non-exact same-city spot-check rows in report-only overrides.
- Next action: Rerun institutional panel, provider review, same-city packet, source maturity, registry, Evidence Center, and deploy bundle. Held same-city rows should move to manual/external geocode review.

## Metrics

| Metric | Value |
|---|---:|
| `target_review_rows` | 20 |
| `accepted_override_rows` | 19 |
| `accepted_provider_years` | 19 |
| `accepted_candidate_counties` | 16 |
| `same_fips_spotcheck_accepted_rows` | 18 |
| `non_exact_conflict_corrected_rows` | 1 |
| `held_or_rejected_rows` | 1 |
| `skipped_existing_override_rows` | 0 |
| `skipped_duplicate_agrees_rows` | 0 |
| `external_or_manual_rows_not_in_scope` | 36 |
| `manual_override_rows_before` | 418 |
| `manual_override_rows_after` | 437 |

## Boundary

- Accepted rows are report-only source-review overrides for the institutional panel builder.
- This pass does not promote institutional anchors into training, scoring, default ranks, Product Mode policy, or source eligibility.
- Rows held by this pass require manual review or an approved external provider geocoder.
