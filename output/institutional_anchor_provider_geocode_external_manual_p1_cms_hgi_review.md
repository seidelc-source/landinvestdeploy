# Institutional Anchor P1 CMS HGI Review

## TLDR

- Status: `cms_hgi_p1_review_has_accepted_rows`.
- Production model/rank/dashboard change: `False`.
- Target rows: `18`.
- CMS HGI rows found: `18`.
- Validator accept rows: `12`.
- Held rows: `6`.
- Decision: Prepared validator-ready reviewed results only for P0 rows where official CMS Hospital General Information returned a same-state Facility ID county/parish mapping.
- Next action: Dry-run `scripts/accept_institutional_anchor_provider_geocode_external_manual_results.py` against the CMS HGI reviewed-results file, apply only if accepted metrics and conflicts are clean, then rebuild institutional source-maturity artifacts.

## Source

- CMS Provider Data Catalog Hospital General Information dataset: `xubh-q36u`.
- Dataset URL: https://data.cms.gov/provider-data/dataset/xubh-q36u

## Metrics

| Metric | Value |
|---|---:|
| `target_priority` | P1 |
| `target_rows` | 18 |
| `cms_hgi_found_rows` | 18 |
| `cms_hgi_fips_mapped_rows` | 13 |
| `reviewer_accept_rows` | 12 |
| `held_rows` | 6 |
| `accepted_candidate_counties` | 8 |
| `production_model_rank_or_dashboard_change` | False |

## Accepted Rows

| Provider | State | CMS HGI County | FIPS | CMS HGI Address | Prior Issue |
|---|---|---|---|---|---|
| HOSPITAL HIMA SAN PABLO BAYAMON | PR | Bayamón Muno | `72021` | CALLE SANTA CRUZ NUM 70 URB SANTA CRUZ, BAYAMON, PR, 00961 | city_not_supported |
| DOCTOR CENTER HOSPITAL MANATI INC. | PR | Manatí Muno | `72091` | MARGINAL CARRETERA NO 2, KM 47.7, MANATI, PR, 00674 | house_number_not_supported; postcode_not_supported; result_type_name_or_road_not_supported; confidence_below_0_90 |
| MERCY CATHOLIC MEDICAL CENTER | PA | Delaware County, Pennsylvania | `42045` | 1500 LANSDOWNE AVE, DARBY, PA, 19023 | no_geocoder_result |
| BAYAMON MEDICAL CENTER | PR | Bayamón Muno | `72021` | CARRETERA #2 KM 11 7, BAYAMON, PR, 00960 | house_number_not_supported; city_not_supported; confidence_below_0_90 |
| HOSPITAL UPR | PR | Carolina Muno | `72031` | CARR 3 KM 8 3 AVE 65TH INFANTERIA BOX 6021, CAROLINA, PR, 00984 | house_number_not_supported; confidence_below_0_90 |
| FIRST HOSPITAL PANAMERICANO | PR | Cidra Muno | `72041` | CARR ESTATAL NUM 787 KM 1 5, CIDRA, PR, 00739 | house_number_not_supported; confidence_below_0_90 |
| HOSPITAL PAVIA SANTURCE | PR | San Juan Muno | `72127` | STREET PROFESOR AUGUSTO RODRIGUEZ #1462, SAN JUAN, PR, 00910 | house_number_not_supported; confidence_below_0_90 |
| DOCTORS CENTER HOSPITAL BAYAMON | PR | Bayamón Muno | `72021` | CALLE J 9 EXTENSION HERMANAS DAVILA, BAYAMON, PR, 00960 | house_number_not_supported; postcode_not_supported; city_not_supported; confidence_below_0_90 |
| TOWER BEHAVIORAL HEALTH | PA | Berks County, Pennsylvania | `42011` | 201 WELLNESS WAY, READING, PA, 19605 | no_geocoder_result |
| PUERTO RICO WOMEN AND CHILDRENS HOSP | PR | Bayamón Muno | `72021` | CARR PR-2 KM11 6 INTERIOR ALEDANO HOSPITAL HERMANO, BAYAMON, PR, 00959 | no_geocoder_result |
| ASOCIACION HOSPITAL DEL MAESTRO | PR | San Juan Muno | `72127` | SERGIO CUEVAS BUSTAMANTE STREET 550, SAN JUAN, PR, 00918 | no_geocoder_result |
| THE MEADOWS HOSPITAL | PA | Centre County, Pennsylvania | `42027` | 132 MEADOWS DRIVE, CENTRE HALL, PA, 16828 | house_number_not_supported; confidence_below_0_90 |

## Held Rows

| Provider | State | Issue |
|---|---|---|
| GUAM REGIONAL MEDICAL CITY | GU | CMS HGI county/parish could not be mapped to local county FIPS. |
| GUAM MEMORIAL HOSPITAL | GU | CMS HGI county/parish could not be mapped to local county FIPS. |
| HOSPITAL MENONITA GUAYAMA | PR | CMS HGI Puerto Rico city/municipio and county/parish values conflict. |
| COMMONWEALTH HEALTH CENTER | MP | CMS HGI county/parish could not be mapped to local county FIPS. |
| ROY L SCHNEIDER HOSPITAL | VI | CMS HGI county/parish could not be mapped to local county FIPS. |
| GOV. JUAN F. LUIS HOSPITAL | VI | CMS HGI county/parish could not be mapped to local county FIPS. |

## Boundary

- This helper only prepares reviewed results for the existing external/manual acceptance validator.
- It applies `0` overrides by itself.
- Institutional anchors remain report-only and must not enter production model features, scoring, ranks, Product Mode policy, source promotion, or feature eligibility until source-maturity, leakage, and model-impact gates clear.
