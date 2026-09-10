# Institutional Anchor Same-City Census Context Acceptance

## TLDR

- Status: `same_city_context_census_overrides_accepted_report_only`.
- Production model/rank/dashboard change: `False`.
- Decision: Accepted only strict non-exact same-FIPS Census context rows from the residual same-city review packet.
- Next action: Rerun the institutional official panel, provider review, closeout packet, same-city review packet, source maturity gate, registry, Evidence Center, and deploy bundle.

## Metrics

| Metric | Value |
|---|---:|
| `packet_rows` | 71 |
| `strict_non_exact_same_fips_candidate_rows` | 14 |
| `accepted_override_rows` | 14 |
| `accepted_provider_years` | 14 |
| `accepted_candidate_counties` | 13 |
| `skipped_existing_override_rows` | 0 |
| `skipped_duplicate_agrees_rows` | 0 |
| `held_or_rejected_rows` | 57 |
| `manual_override_rows_before` | 403 |
| `manual_override_rows_after` | 417 |

## Acceptance Status Counts

- `accepted`: `14`
- `held_or_rejected`: `57`

## Boundary

- Only strict non-exact same-FIPS Census context rows from the same-city review packet are accepted.
- Institutional anchors remain report-only until source-maturity, leakage, and model-impact gates clear.
