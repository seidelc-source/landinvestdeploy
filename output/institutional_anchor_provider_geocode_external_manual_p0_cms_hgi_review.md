# Institutional Anchor P0 CMS HGI Review

## TLDR

- Status: `cms_hgi_p0_review_has_accepted_rows`.
- Production model/rank/dashboard change: `False`.
- Target rows: `25`.
- CMS HGI rows found: `24`.
- Validator accept rows: `24`.
- Held rows: `1`.
- Decision: Prepared validator-ready reviewed results only for P0 rows where official CMS Hospital General Information returned a same-state Facility ID county/parish mapping.
- Next action: Dry-run `scripts/accept_institutional_anchor_provider_geocode_external_manual_results.py` against the CMS HGI reviewed-results file, apply only if accepted metrics and conflicts are clean, then rebuild institutional source-maturity artifacts.

## Source

- CMS Provider Data Catalog Hospital General Information dataset: `xubh-q36u`.
- Dataset URL: https://data.cms.gov/provider-data/dataset/xubh-q36u

## Metrics

| Metric | Value |
|---|---:|
| `target_priority` | P0 |
| `target_rows` | 25 |
| `cms_hgi_found_rows` | 24 |
| `cms_hgi_fips_mapped_rows` | 24 |
| `reviewer_accept_rows` | 24 |
| `held_rows` | 1 |
| `accepted_candidate_counties` | 23 |
| `production_model_rank_or_dashboard_change` | False |

## Accepted Rows

| Provider | State | CMS HGI County | FIPS | CMS HGI Address | Prior Issue |
|---|---|---|---|---|---|
| HOAG MEMORIAL HOSPITAL PRESBYTERIAN | CA | Orange County, California | `06059` | ONE HOAG DRIVE, NEWPORT BEACH, CA, 92663 | house_number_not_supported; postcode_not_supported; confidence_below_0_90 |
| CROZER CHESTER MEDICAL CENTER | PA | Delaware County, Pennsylvania | `42045` | ONE MEDICAL CENTER BOULEVARD, UPLAND, PA, 19013 | house_number_not_supported; confidence_below_0_90 |
| EMERSON HOSPITAL | MA | Middlesex County, Massachusetts | `25017` | 133 OLD ROAD TO 9 ACRE CORNER, W CONCORD, MA, 01742 | house_number_not_supported; confidence_below_0_90 |
| HCA FLORIDA PALMS WEST HOSPITAL | FL | Palm Beach County, Florida | `12099` | 13001 SOUTHERN BLVD, LOXAHATCHEE, FL, 33470 | no_geocoder_result |
| PIEDMONT EASTSIDE MEDICAL CENTER | GA | Gwinnett County, Georgia | `13135` | 1700 MEDICAL WAY, SNELLVILLE, GA, 30078 | postcode_not_supported; confidence_below_0_90 |
| ST. LOUIS FORENSIC TREATMENT CENTER | MO | St. Louis city, Missouri | `29510` | 5400 ARSENAL ST, SAINT LOUIS, MO, 63139 | postcode_not_supported; city_not_supported; confidence_below_0_90 |
| TRISTAR HENDERSONVILLE MEDICAL CENTE | TN | Sumner County, Tennessee | `47165` | 355 NEW SHACKLE ISLAND RD, HENDERSONVILLE, TN, 37075 | postcode_not_supported; confidence_below_0_90 |
| GOTTLIEB MEMORIAL HOSPITAL | IL | Cook County, Illinois | `17031` | 701 WEST NORTH AVE, MELROSE PARK, IL, 60160 | house_number_not_supported; confidence_below_0_90 |
| ADVENTHEALTH GORDON | GA | Gordon County, Georgia | `13129` | 1035 RED BUD ROAD, CALHOUN, GA, 30701 | postcode_not_supported; confidence_below_0_90 |
| HCA FLORIDA POINCIANA HOSPITAL | FL | Osceola County, Florida | `12097` | 325 CYPRESS PKWY, KISSIMMEE, FL, 34758 | no_geocoder_result |
| MCLAREN LAPEER REGION | MI | Lapeer County, Michigan | `26087` | 1375 N MAIN ST, LAPEER, MI, 48446 | postcode_not_supported; confidence_below_0_90 |
| HENDRICK MEDICAL CENTER BROWNWOOD | TX | Brown County, Texas | `48049` | 1501 BURNET DR, BROWNWOOD, TX, 76801 | no_geocoder_result |
| MEADOWS REGIONAL MEDICAL CENTER | GA | Toombs County, Georgia | `13279` | ONE MEADOWS PARKWAY, VIDALIA, GA, 30474 | no_geocoder_result |
| MOUNTAIN VIEW HOSPITAL | UT | Utah County, Utah | `49049` | 1000 EAST 100 NORTH, PAYSON, UT, 84651 | house_number_not_supported; confidence_below_0_90 |
| OCHSNER ST. MARY | LA | St. Mary Parish, Louisiana | `22101` | 1125 MARGUERITE STREET, MORGAN CITY, LA, 70380 | postcode_not_supported; confidence_below_0_90 |
| VIA CHRISTI HOSPITAL PITTSBURG INC. | KS | Crawford County, Kansas | `20037` | 1 MT CARMEL WAY, PITTSBURG, KS, 66762 | no_geocoder_result |
| RIVER PLACE BEHAVIORAL HEALTH | LA | St. John the Baptist Parish, Louisiana | `22095` | 500 RUE DE SANTE, LAPLACE, LA, 70068 | confidence_below_0_90 |
| GLENCOE REGIONAL HEALTH SERVICES | MN | McLeod County, Minnesota | `27085` | 1805 HENNEPIN AVENUE NORTH, GLENCOE, MN, 55336 | house_number_not_supported; confidence_below_0_90 |
| JOHN J MADDEN MENTAL HEALTH CENTER | IL | Cook County, Illinois | `17031` | 1200 S FIRST AVE, HINES, IL, 60141 | no_geocoder_result |
| CHI MEMORIAL HOSPITAL - GEORGIA | GA | Catoosa County, Georgia | `13047` | 4710 BATTLEFIELD PARKWAY, RINGGOLD, GA, 30736 | house_number_not_supported; postcode_not_supported; city_not_supported; confidence_below_0_90 |
| ADAIR COUNTY HEALTH CENTER | OK | Adair County, Oklahoma | `40001` | 1401 WEST LOCUST, STILWELL, OK, 74960 | no_geocoder_result |
| SUMMERS COUNTY ARH | WV | Summers County, West Virginia | `54089` | 115 SUMMERS HOSPITAL ROAD, HINTON, WV, 25951 | house_number_not_supported; postcode_not_supported; confidence_below_0_90 |
| KINGWOOD EMERGENCY HOSPITAL | TX | Harris County, Texas | `48201` | 23330 HIGHWAY 59 N, KINGWOOD, TX, 77339 | no_geocoder_result |
| COOK CHILDREN CARE | TX | Collin County, Texas | `48085` | 4100 W UNIVERSITY DRIVE, PROSPER, TX, 75078 | house_number_not_supported; postcode_not_supported; confidence_below_0_90 |

## Held Rows

| Provider | State | Issue |
|---|---|---|
| BENCHMARK BEHAVIORAL HEALTH SYSTEM I | UT | CMS HGI did not return a row for this Facility ID. |

## Boundary

- This helper only prepares reviewed results for the existing external/manual acceptance validator.
- It applies `0` overrides by itself.
- Institutional anchors remain report-only and must not enter production model features, scoring, ranks, Product Mode policy, source promotion, or feature eligibility until source-maturity, leakage, and model-impact gates clear.
