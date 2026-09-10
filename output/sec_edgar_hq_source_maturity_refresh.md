# SEC EDGAR HQ Source Maturity Refresh

## TLDR

- Task: `XB-022`.
- Status: `source_maturity_blocked`.
- Production model/rank/dashboard change: `False`.
- Domestic HQ geocode match share: `100.0%`.
- Unresolved review rows: `40`.
- Unresolved domestic review rows: `0`.
- Point-in-time ready rows: `0`.
- Filing-observed address rows parsed: `521`.
- Filing-observed manual/matched geocode-ready rows: `85`.
- Filing-observed auto snapshot-reuse rows: `282`.
- Filing-observed auto snapshot-reuse spot checks accepted: `203`.
- Filing-observed auto snapshot-reuse strict Census acceptances: `15`.
- Filing-observed auto snapshot-reuse held-row resolution acceptances: `6`.
- Filing-observed auto snapshot-reuse final external-evidence acceptances: `4`.
- Filing-observed auto snapshot-reuse spot checks open: `0`.
- Filing-observed auto snapshot-reuse county closeout candidates: `17`.
- Filing-observed auto snapshot-reuse county closeout remaining rows: `8`.
- Filing-observed rows pending geocode review: `0`.
- Filing-observed parse-review pattern candidates: `7`.
- Filing-observed parse-review manual rows: `96`.
- Filing-observed county-year candidate rows: `216`.

## Blockers

- `current_address_snapshot_not_point_in_time`

## Decision

- `keep_sec_edgar_hq_report_only_until_geocode_and_point_in_time_gates_pass`.
- Next action: Geocode review and first county-year candidates are ready; extend the filing parse batch and rerun source maturity before promotion review.

## Boundary

- This refresh does not fetch SEC data or assign fallback counties.
- Current-address HQ evidence remains report-only until historical filing-address or event-validity semantics pass.
