# Institutional Anchor Same-City Census Conflict Acceptance

## TLDR

- Status: `same_city_conflict_census_overrides_accepted_report_only`.
- Production model/rank/dashboard change: `False`.
- Decision: Accepted only exact Census conflict corrections from the residual same-city review packet.
- Next action: Rerun the institutional official panel, provider review, closeout packet, same-city review packet, source maturity gate, registry, Evidence Center, and deploy bundle.

## Metrics

| Metric | Value |
|---|---:|
| `packet_rows` | 75 |
| `strict_conflict_correction_candidate_rows` | 4 |
| `accepted_override_rows` | 4 |
| `accepted_provider_years` | 4 |
| `accepted_candidate_counties` | 4 |
| `skipped_existing_override_rows` | 0 |
| `skipped_duplicate_agrees_rows` | 0 |
| `held_or_rejected_rows` | 71 |
| `manual_override_rows_before` | 399 |
| `manual_override_rows_after` | 403 |

## Acceptance Status Counts

- `accepted`: `4`
- `held_or_rejected`: `71`

## Boundary

- Only exact Census conflict corrections from the same-city review packet are accepted.
- Institutional anchors remain report-only until source-maturity, leakage, and model-impact gates clear.
