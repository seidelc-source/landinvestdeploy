# SEC Auto-Reuse Held Row Resolution

## TLDR

- Status: `held_row_resolution_ready_report_only`.
- Production model/rank/dashboard change: `False`.
- Held input rows: `10`.
- Accepted held rows: `6`.
- Held rows after resolution: `4`.
- Supplemental filing Census acceptances: `2`.
- Parser-fragment snapshot Census acceptances: `4`.

## Metrics

| Metric | Value |
|---|---:|
| `held_input_rows` | 10 |
| `supplemental_attempt_rows` | 14 |
| `supplemental_census_submitted` | True |
| `supplemental_census_result_rows` | 14 |
| `supplemental_census_match_attempt_rows` | 8 |
| `accepted_held_resolution_rows` | 6 |
| `accepted_supplemental_filing_census_same_county_rows` | 2 |
| `accepted_parser_fragment_snapshot_census_same_county_rows` | 4 |
| `held_rows_after_resolution` | 4 |
| `held_local_same_zip_candidate_rows` | 2 |
| `held_snapshot_support_not_parser_fragment_rows` | 2 |
| `held_supplemental_conflict_rows` | 0 |
| `parser_fragment_rows` | 4 |
| `accepted_counties` | 4 |

## Resolution Status Counts

- `accepted_parser_fragment_snapshot_census_same_county`: `4`
- `accepted_supplemental_filing_census_same_county`: `2`
- `held_local_same_zip_candidate`: `2`
- `held_snapshot_support_not_parser_fragment`: `2`

## Row Preview

| Entity | Filing Date | Filing Street | Status | County | Evidence |
|---|---|---|---|---|---|
| BARFRESH FOOD GROUP INC. | 2026-05-14 | 8 th Floor | `accepted_parser_fragment_snapshot_census_same_county` | Los Angeles County, California | 12100 WILSHIRE BLVD, LOS ANGELES, CA, 90025 |
| Data Storage Corp | 2026-04-14 | 5 th Avenue , Second Floor , Suite 2821 | `accepted_parser_fragment_snapshot_census_same_county` | New York County, New York | 244 5TH AVE, NEW YORK, NY, 10001 |
| Data Storage Corp | 2026-05-15 | 2 nd Fl, 2821 | `accepted_parser_fragment_snapshot_census_same_county` | New York County, New York | 244 5TH AVE, NEW YORK, NY, 10001 |
| Fervo Energy Co | 2026-05-15 | Suite 1700 | `accepted_parser_fragment_snapshot_census_same_county` | Harris County, Texas | 910 LOUISIANA ST, HOUSTON, TX, 77002 |
| B&G Foods, Inc. | 2006-03-07 | Four Gatehall Drive, Suite 110 | `accepted_supplemental_filing_census_same_county` | Morris County, New Jersey | 4 GATEHALL DR, PARSIPPANY, NJ, 07054 |
| B&G Foods, Inc. | 2007-03-08 | Four Gatehall Drive, Suite 110 | `accepted_supplemental_filing_census_same_county` | Morris County, New Jersey | 4 GATEHALL DR, PARSIPPANY, NJ, 07054 |
| Apple Inc. | 2015-07-22 | 36743 Apple Inc. California 94-2404110 1 Infinite Loop | `held_local_same_zip_candidate` | Santa Clara County, California | Local same-ZIP candidate remains held without a filing-derived Census match. |
| Apple Inc. | 2015-10-28 | 36743 Apple Inc. California 94-2404110 1 Infinite Loop | `held_local_same_zip_candidate` | Santa Clara County, California | Local same-ZIP candidate remains held without a filing-derived Census match. |
| Clearway Energy, Inc. | 2016-11-04 | 804 Carnegie Center | `held_snapshot_support_not_parser_fragment` | Mercer County, New Jersey | 300 CARNEGIE CENTER BLVD, PRINCETON, NJ, 08540 |
| Clearway Energy, Inc. | 2017-02-28 | 804 Carnegie Center | `held_snapshot_support_not_parser_fragment` | Mercer County, New Jersey | 300 CARNEGIE CENTER BLVD, PRINCETON, NJ, 08540 |

## Decision

- Accepted only held rows with supplemental filing-derived Census same-county evidence or parser-fragment snapshot-street Census support. Remaining local same-ZIP and plausible alternate-street snapshot-only rows stay held.
- Next action: Rerun SEC review queues, source maturity, scale-up gate, source registry, Evidence Center, and deploy bundle. Keep SEC report-only while current-address snapshot semantics and parse-review rows remain open.

## Boundary

- This is a report-only operator-resolution artifact.
- It does not modify manual overrides, reviewed SEC vintages, county-year candidates, model features, scoring, ranks, Product Mode policy, source promotion, or feature eligibility.
