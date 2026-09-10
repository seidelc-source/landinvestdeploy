# Institutional Anchor Official Source Panel

## TLDR

- Task: `XB-026-official-ipeds-cms-hcris-source-seed`.
- Status: `official_full_extract_report_only_no_promotion`.
- Production model/rank/dashboard change: `False`.
- Decision: Use as a report-only institutional-anchor seed. Full CMS annual rows are staged, but county/provider review, missingness checks, and leakage gates must pass before model or rank experiments.

## Source Metrics

| Metric | Value |
|---|---:|
| `ipeds_rows` | 6163 |
| `ipeds_county_fips_rows` | 6163 |
| `ipeds_county_fips_share` | 1.0 |
| `cms_source_mode` | full_annual_csv |
| `cms_rows` | 6103 |
| `cms_sample_rows` | 0 |
| `cms_full_extract_rows` | 6103 |
| `cms_matched_fips_rows` | 6081 |
| `cms_unmatched_fips_rows` | 22 |
| `cms_matched_fips_share` | 0.9963952154678027 |
| `cms_product_universe_rows` | 6022 |
| `cms_product_universe_matched_fips_rows` | 6009 |
| `cms_product_universe_matched_fips_share` | 0.9978412487545666 |
| `cms_source_county_missing_rows` | 556 |
| `cms_non_product_jurisdiction_rows` | 81 |
| `cms_provider_geocode_override_file_rows` | 572 |
| `cms_provider_geocode_override_valid_rows` | 572 |
| `cms_provider_geocode_override_conflict_rows` | 0 |
| `cms_provider_geocode_override_applied_rows` | 575 |
| `cms_provider_geocode_override_applied_counties` | 382 |
| `panel_county_year_rows` | 3531 |
| `panel_counties` | 2598 |
| `panel_year_min` | 2022 |
| `panel_year_max` | 2024 |
| `panel_dual_source_rows` | 1000 |

## Top County-Year Rows By Institutional Scale

| County | Year | IPEDS Institutions | IPEDS Enrollment | CMS Providers | CMS Beds |
|---|---:|---:|---:|---:|---:|
| Los Angeles County, CA | 2023 | 194 | 972425 | 59 | 13352 |
| Maricopa County, AZ | 2023 | 79 | 734918 | 45 | 8037 |
| Cook County, IL | 2023 | 105 | 368309 | 24 | 5637 |
| New York County, NY | 2023 | 76 | 333567 | 10 | 6273 |
| Harris County, TX | 2023 | 65 | 267187 | 40 | 7543 |
| San Diego County, CA | 2023 | 66 | 416559 | 16 | 4246 |
| Orange County, CA | 2023 | 63 | 356922 | 17 | 3095 |
| Miami-Dade County, FL | 2023 | 72 | 226096 | 17 | 5251 |
| Orange County, FL | 2023 | 22 | 213403 | 8 | 5100 |
| Suffolk County, MA | 2023 | 31 | 189705 | 18 | 5562 |
| Los Angeles County, California, CA | 2024 | 0 | 0 | 40 | 9042 |
| Cook County, Illinois, IL | 2024 | 0 | 0 | 37 | 8535 |
| Salt Lake County, UT | 2023 | 25 | 337284 | 12 | 1709 |
| Hennepin County, MN | 2023 | 21 | 247960 | 10 | 3362 |
| Marion County, IN | 2023 | 19 | 231716 | 13 | 3310 |
| Tarrant County, TX | 2023 | 28 | 150398 | 27 | 3797 |
| Harris County, Texas, TX | 2024 | 0 | 0 | 23 | 6679 |
| Dallas County, TX | 2023 | 53 | 191234 | 21 | 2818 |
| Cuyahoga County, OH | 2023 | 26 | 73272 | 20 | 5139 |
| Hillsborough County, FL | 2023 | 22 | 118604 | 9 | 4028 |

## Boundary

- The CMS/HCRIS rows use the staged official 2023 final public-use annual CSV when available; otherwise the bounded API seed sample is used.
- The panel is report-only and should not train, score, rank, or default-display until source maturity and leakage gates pass.
- No production model, scoring policy, rank artifact, source-promotion gate, or dashboard default changed.
