# SEC Point-In-Time HQ Auto-Reuse Spot-Check Acceptance

## TLDR

- Status: `auto_reuse_spotcheck_partially_accepted_report_only`.
- Production model/rank/dashboard change: `False`.
- Auto-reuse queue rows: `203`.
- Accepted spot-check rows: `178`.
- Open spot-check rows: `25`.
- Accepted share: `87.7%`.
- Open high-priority rows: `25`.

## Acceptance Status Counts

- `accepted_normalized_street_match`: `113`
- `accepted_parsed_street_embedded_in_snapshot`: `20`
- `accepted_parser_noise_snapshot_tokens_present`: `1`
- `accepted_same_street_number_unit_variation`: `14`
- `accepted_snapshot_street_embedded_in_parse`: `30`
- `operator_review_required_street_mismatch_same_city_zip`: `25`

## Open Priority Counts

- `high`: `25`

## Decision

- Accept only auto snapshot reuses with strong same-street, same-building, or parser-noise evidence. Keep true street-change rows open for operator review before SEC source promotion.
- Next action: Review the remaining open same-city/state/ZIP street mismatches, then rerun SEC source maturity. Do not promote SEC HQ evidence while current-address snapshot semantics remain unresolved.

## Boundary

- This packet is a report-only source-review artifact.
- It does not change production model features, scoring, ranks, Product Mode policy, source promotion, or feature eligibility.
