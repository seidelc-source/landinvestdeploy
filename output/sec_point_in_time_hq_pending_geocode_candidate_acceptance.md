# SEC Pending Point-In-Time HQ Geocode Candidate Acceptance

## TLDR

- Status: `candidate_overrides_accepted_report_only`.
- Production model/rank/dashboard change: `False`.
- Candidate override rows reviewed: `6`.
- Accepted override rows: `6`.
- Accepted queue rows: `9`.
- Skipped existing rows: `0`.
- Rejected rows: `0`.
- Manual override rows after: `83`.

## Acceptance Status Counts

- `accepted`: `6`

## Decision

- Accepted validated candidate override rows into the report-only SEC point-in-time manual override file.
- Next action: Rerun SEC geocode review, review queues, source maturity, scale-up gate, source registry, Evidence Center, and deploy bundle.

## Boundary

- Accepted rows are report-only SEC source-review rows.
- This does not change production model features, scoring, ranks, Product Mode policy, source promotion, or feature eligibility.
