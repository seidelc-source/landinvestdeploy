# Institutional Anchor P1 CMS HGI Review

## TLDR

- Status: `cms_hgi_p1_review_has_accepted_rows`.
- Production model/rank/dashboard change: `False`.
- Target rows: `5`.
- CMS HGI rows found: `5`.
- Validator accept rows: `4`.
- Held rows: `1`.
- Decision: Prepared validator-ready reviewed results only for P0 rows where official CMS Hospital General Information returned a same-state Facility ID county/parish mapping.
- Next action: Dry-run `scripts/accept_institutional_anchor_provider_geocode_external_manual_results.py` against the CMS HGI reviewed-results file, apply only if accepted metrics and conflicts are clean, then rebuild institutional source-maturity artifacts.

## Source

- CMS Provider Data Catalog Hospital General Information dataset: `xubh-q36u`.
- Dataset URL: https://data.cms.gov/provider-data/dataset/xubh-q36u

## Metrics

| Metric | Value |
|---|---:|
| `target_priority` | P1 |
| `target_rows` | 5 |
| `cms_hgi_found_rows` | 5 |
| `cms_hgi_fips_mapped_rows` | 5 |
| `reviewer_accept_rows` | 4 |
| `held_rows` | 1 |
| `accepted_candidate_counties` | 3 |
| `production_model_rank_or_dashboard_change` | False |

## Accepted Rows

| Provider | State | CMS HGI County | FIPS | CMS HGI Address | Prior Issue |
|---|---|---|---|---|---|
| GUAM REGIONAL MEDICAL CITY | GU | Guam | `66010` | 133 ROUTE 3, DEDEDO, GU, 96929 | geocoder_point_not_in_county_lookup; geocoder_point_state_mismatch_provider_state; postcode_not_supported; confidence_below_0_90 |
| GUAM MEMORIAL HOSPITAL | GU | Guam | `66010` | 85O GOV CARLOS G CAMACHO ROAD, TAMUNING, GU, 96913 | no_geocoder_result |
| ROY L SCHNEIDER HOSPITAL | VI | St. Thomas Island | `78030` | 9048 SUGAR ESTATE, ST THOMAS, VI, 00801 | no_geocoder_result |
| COMMONWEALTH HEALTH CENTER | MP | Saipan Municipality | `69110` | 1 LOWER NAVY HILL ROAD (PO BOX 409CK), GARAPAN, MP, 96950 | geocoder_point_not_in_county_lookup; geocoder_point_state_mismatch_provider_state; house_number_not_supported; confidence_below_0_90 |

## Held Rows

| Provider | State | Issue |
|---|---|---|
| HOSPITAL MENONITA GUAYAMA | PR | CMS HGI Puerto Rico city/municipio and county/parish values conflict. |

## Boundary

- This helper only prepares reviewed results for the existing external/manual acceptance validator.
- It applies `0` overrides by itself.
- Institutional anchors remain report-only and must not enter production model features, scoring, ranks, Product Mode policy, source promotion, or feature eligibility until source-maturity, leakage, and model-impact gates clear.
