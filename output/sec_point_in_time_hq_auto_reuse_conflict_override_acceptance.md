# SEC Auto-Reuse Conflict Override Acceptance

## TLDR

- Status: `conflict_overrides_accepted_report_only`.
- Production model/rank/dashboard change: `False`.
- Held conflict rows reviewed: `2`.
- Accepted conflict override rows: `0`.
- Covered existing conflict rows: `2`.
- Covered conflict rows: `2`.
- Accepted conflict address keys: `0`.
- Rejected conflict rows: `0`.
- Manual override rows after: `77`.

## Acceptance Rows

| Status | Entity | Filing Date | Filing Street | Snapshot County | Census County | Census Match |
|---|---|---|---|---|---|---|
| `covered_existing_conflict_override` | Delek Logistics Partners, LP | 2012-12-14 | 35721 DELEK LOGISTICS PARTNERS, LP Delaware 45-5379027 Identification No.) 7102 Commerce Way | Davidson County | Williamson County, Tennessee | 7102 COMMERCE WAY, BRENTWOOD, TN, 37027 |
| `covered_existing_conflict_override` | Delek Logistics Partners, LP | 2013-03-12 | 35721 DELEK LOGISTICS PARTNERS, LP Delaware 45-5379027 Identification No.) 7102 Commerce Way | Davidson County | Williamson County, Tennessee | 7102 COMMERCE WAY, BRENTWOOD, TN, 37027 |

## Decision

- Accepted only held Census/snapshot conflicts where filing-street Census geographies support a valid county different from the reused current snapshot county.
- Next action: Rerun SEC point-in-time geocode review, review queues, auto-reuse acceptance/closeout, source maturity, scale-up gate, source registry, Evidence Center, and deploy bundle.

## Boundary

- Accepted rows are report-only SEC source-review overrides.
- This does not change production model features, scoring, ranks, Product Mode policy, source promotion, or feature eligibility.
