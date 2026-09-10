# SEC Point-In-Time HQ Parse-Review Pattern Candidates

## TLDR

- Status: `parse_review_pattern_candidates_ready_report_only`.
- Production model/rank/dashboard change: `False`.
- Parse-review rows: `154`.
- Pattern candidate rows: `7`.
- Street + city/ZIP candidates: `0`.
- Street-only candidates: `0`.
- City/ZIP-only candidates: `7`.
- Manual review needed rows: `96`.
- Non-geocode excluded rows: `47`.

## Status Counts

- `fetch_or_cache_failure`: `4`
- `manual_review_needed_no_local_snippet`: `96`
- `non_geocode_candidate_excluded_from_parser_work`: `47`
- `pattern_candidate_city_zip_only`: `7`

## Decision

- Use these snippets to prioritize parser-pattern work for rows where the cached filing already contains the snapshot street and/or city+ZIP text. Keep parsed-output changes behind a separate parser batch rerun.
- Next action: Implement parser rules for high-confidence snippet patterns, rerun the parse batch from cache, then rebuild geocode review.

## Boundary

- This is a report-only parser work packet.
- It does not change parsed address rows, geocodes, model features, scoring, ranks, Product Mode policy, source promotion, or feature eligibility.
