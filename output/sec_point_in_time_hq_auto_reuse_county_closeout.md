# SEC Auto-Reuse County Closeout Packet

## TLDR

- Status: `auto_reuse_county_closeout_candidates_ready_report_only`.
- Production model/rank/dashboard change: `False`.
- Open spot-check rows reviewed: `25`.
- County-level closeout candidate rows: `17`.
- Strict Census same-county rows: `15`.
- Local same-ZIP single-county candidate rows: `2`.
- Operator-review remaining rows: `8`.

## Metrics

| Metric | Value |
|---|---:|
| `open_spotcheck_rows` | 25 |
| `open_spotcheck_address_keys` | 16 |
| `open_spotcheck_counties` | 12 |
| `census_attempt_rows` | 66 |
| `census_submitted` | True |
| `census_result_rows` | 66 |
| `census_match_attempt_rows` | 46 |
| `county_closeout_candidate_rows` | 17 |
| `strict_census_current_fips_match_rows` | 15 |
| `local_same_zip_single_open_fips_candidate_rows` | 2 |
| `snapshot_only_support_rows` | 8 |
| `conflict_rows` | 0 |
| `ambiguous_zip_county_rows` | 0 |
| `unresolved_rows` | 0 |
| `operator_review_remaining_rows` | 8 |
| `packet_rows` | 13 |

## Status Counts

- `county_closeout_candidate_census_matches_current_fips`: `15`
- `snapshot_only_support_current_fips_not_filing_street`: `8`
- `county_closeout_candidate_local_same_zip_single_open_fips`: `2`

## Packet Preview

| Rank | Status | County | Rows | ZIP | Action | Source |
|---:|---|---|---:|---|---|---|
| 1 | `county_closeout_candidate_census_matches_current_fips` | Harris County, Texas | 6 | TX 77002 | review_for_county_level_acceptance | `census_geographies_addressbatch:parsed_original` |
| 2 | `county_closeout_candidate_census_matches_current_fips` | Suffolk County, New York | 2 | NY 11706 | review_for_county_level_acceptance | `census_geographies_addressbatch:parsed_original` |
| 3 | `county_closeout_candidate_census_matches_current_fips` | Shelby County, Tennessee | 2 | TN 38125 | review_for_county_level_acceptance | `census_geographies_addressbatch:parser_repair` |
| 4 | `county_closeout_candidate_census_matches_current_fips` | Williamson County, Tennessee | 2 | TN 37027 | review_for_county_level_acceptance | `census_geographies_addressbatch:parsed_original` |
| 5 | `county_closeout_candidate_census_matches_current_fips` | Fulton County, Georgia | 1 | GA 30354-1989 | review_for_county_level_acceptance | `census_geographies_addressbatch:parser_repair` |
| 6 | `county_closeout_candidate_census_matches_current_fips` | Mecklenburg County, North Carolina | 1 | NC 28202-1803 | review_for_county_level_acceptance | `census_geographies_addressbatch:parsed_original` |
| 7 | `county_closeout_candidate_census_matches_current_fips` | Richmond city, Virginia | 1 | VA 23219 | review_for_county_level_acceptance | `census_geographies_addressbatch:parser_repair` |
| 8 | `county_closeout_candidate_local_same_zip_single_open_fips` | Santa Clara County | 2 | CA 95014 | review_for_county_level_acceptance | `local_same_city_state_zip_single_open_fips` |
| 9 | `snapshot_only_support_current_fips_not_filing_street` | Mercer County, New Jersey | 2 | NJ 08540 | review_street_or_external_geocode | `census_geographies_addressbatch:snapshot_street_after_parser_repair` |
| 10 | `snapshot_only_support_current_fips_not_filing_street` | Morris County, New Jersey | 2 | NJ 07054 | review_street_or_external_geocode | `census_geographies_addressbatch:snapshot_street_after_parser_repair` |
| 11 | `snapshot_only_support_current_fips_not_filing_street` | New York County, New York | 2 | NY 10001 | review_street_or_external_geocode | `census_geographies_addressbatch:snapshot_street_after_parser_repair` |
| 12 | `snapshot_only_support_current_fips_not_filing_street` | Los Angeles County, California | 1 | CA 90025 | review_street_or_external_geocode | `census_geographies_addressbatch:snapshot_street_after_parser_repair` |
| 13 | `snapshot_only_support_current_fips_not_filing_street` | Harris County, Texas | 1 | TX 77002 | review_street_or_external_geocode | `census_geographies_addressbatch:snapshot_street_after_parser_repair` |

## Decision

- County-level closeout evidence is staged for operator review only. Street-level point-in-time truth and SEC source promotion remain blocked until explicit review gates pass.
- Next action: Review strict Census same-county rows first, then local same-ZIP single-county candidates; keep conflicts, ambiguous ZIPs, and snapshot-only support in manual or external geocode review.

## Boundary

- This is a report-only operator-review artifact.
- It does not modify SEC manual overrides, reviewed vintages, county-year candidates, model features, scoring, ranks, Product Mode policy, source promotion, or feature eligibility.
