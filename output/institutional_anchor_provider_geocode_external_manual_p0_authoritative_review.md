# Institutional Anchor P0 Authoritative Review

## TLDR

- Status: `p0_authoritative_review_has_accepted_rows`.
- Production model/rank/dashboard change: `False`.
- Target rows: `1`.
- NPPES rows found: `1`.
- Census matched rows: `1`.
- Validator accept rows: `1`.
- Held rows: `0`.
- Decision: Prepared validator-ready reviewed results only for configured P0 rows with official NPPES address support, official Census county geographies, and recorded provider/county source URLs.
- Next action: Dry-run `scripts/accept_institutional_anchor_provider_geocode_external_manual_results.py` against the authoritative reviewed-results file, apply only if accepted metrics and conflicts are clean, then rebuild institutional source-maturity artifacts.

## Sources

- NPPES/NPI Registry API: https://npiregistry.cms.hhs.gov/api/
- Census geocoder API: https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress
- Provider site: https://bbhsnet.com/contact-us/
- Davis County behavioral health directory: https://www.daviscountyutah.gov/docs/librariesprovider5/reports-and-assessments/2024-behavioral-health-directory.pdf

## Metrics

| Metric | Value |
|---|---:|
| `target_priority` | P0 |
| `target_rows` | 1 |
| `nppes_found_rows` | 1 |
| `census_matched_rows` | 1 |
| `authority_fips_mapped_rows` | 1 |
| `reviewer_accept_rows` | 1 |
| `held_rows` | 0 |
| `accepted_candidate_counties` | 1 |
| `production_model_rank_or_dashboard_change` | False |

## Accepted Rows

| Provider | NPI | County | FIPS | NPPES Address | Census Address | Checks |
|---|---|---|---|---|---|---|
| BENCHMARK BEHAVIORAL HEALTH SYSTEM I | `-` | Davis County, Utah | `49011` | 592 W 1350 S, WOODS CROSS, UT, 840108180 | - | nppes_name_or_dba_match; nppes_active; state_match; nppes_city_woods_cross; street_match; nppes_zip_84010; census_current_geography_match; census_input_street_supported; provider_site_and_county_directory_urls_recorded |

## Held Rows

- No held rows.

## Boundary

- This helper only prepares reviewed results for the existing external/manual acceptance validator.
- It applies `0` overrides by itself.
- Institutional anchors remain report-only and must not enter production model features, scoring, ranks, Product Mode policy, source promotion, or feature eligibility until source-maturity, leakage, and model-impact gates clear.
