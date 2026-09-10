# Institutional Anchor Provider Geocode Review

## TLDR

- Status: `provider_geocode_review_candidates_ready_report_only`.
- Production model/rank/dashboard change: `False`.
- Decision: Provider geocode candidates are ready for operator review, but no county assignments are written back until approved.

## Metrics

| Metric | Value |
|---|---:|
| `review_rows` | 22 |
| `high_priority_rows` | 12 |
| `same_zip_candidate_rows` | 4 |
| `same_city_candidate_rows` | 18 |
| `external_geocode_required_rows` | 0 |
| `existing_source_maturity_review_rows` | 2060 |

## Candidate Method Counts

- `same_state_city_unique_matched_cms_rows`: `18`
- `same_state_zip5_unique_matched_cms_rows`: `4`

## Top Review Rows

| Provider | State | City | ZIP | Method | Suggested County | Confidence | Action |
|---|---|---|---|---|---|---:|---|
| WILLOW ROCK CENTER | CA | SAN LEANDRO | 94578 | `same_state_city_unique_matched_cms_rows` | Alameda County, California | 0.76 | operator_review_city_match_before_assigning |
| ENCOMPASS HEALTH REHABILITATION HOSP | FL | JACKSONVILLE | 32256 | `same_state_city_unique_matched_cms_rows` | Duval County, Florida | 0.76 | operator_review_city_match_before_assigning |
| ACADIA GENERAL HOSPITAL | LA | CROWLEY | 70526 | `same_state_city_unique_matched_cms_rows` | Acadia Parish, Louisiana | 0.76 | operator_review_city_match_before_assigning |
| IBERIA MEDICAL CENTER | LA | NEW IBERIA | 70562 | `same_state_city_unique_matched_cms_rows` | Iberia Parish, Louisiana | 0.76 | operator_review_city_match_before_assigning |
| WESTERN MARYLAND HOSPITAL CENTER | MD | HAGERSTOWN | 21740 | `same_state_city_unique_matched_cms_rows` | Washington County, Maryland | 0.76 | operator_review_city_match_before_assigning |
| LINCOLN REGIONAL CENTER | NE | LINCOLN | 68509 | `same_state_city_unique_matched_cms_rows` | Lancaster County, Nebraska | 0.76 | operator_review_city_match_before_assigning |
| SUMMERLIN HOSPITAL MEDICAL CENTER | NV | LAS VEGAS | 89114 | `same_state_city_unique_matched_cms_rows` | Clark County, Nevada | 0.76 | operator_review_city_match_before_assigning |
| COMANCHE COUNTY MEMORIAL HOSPITAL | OK | LAWTON | 73502 | `same_state_city_unique_matched_cms_rows` | Comanche County, Oklahoma | 0.76 | operator_review_city_match_before_assigning |
| OU MEDICAL CENTER | OK | OKLAHOMA CITY | 73104 | `same_state_city_unique_matched_cms_rows` | Oklahoma County, Oklahoma | 0.76 | operator_review_city_match_before_assigning |
| LEGENT ORTHOPEDIC HOSPITAL CARROLLTO | TX | CARROLLTON | 75007 | `same_state_city_unique_matched_cms_rows` | Denton County, Texas | 0.76 | operator_review_city_match_before_assigning |
| BRATTLEBORO RETREAT | VT | BRATTLEBORO | 05302 | `same_state_city_unique_matched_cms_rows` | Windham County, Vermont | 0.76 | operator_review_city_match_before_assigning |
| MILDRED MITCHELL-BATEMAN HOSPITAL | WV | HUNTINGTON | 25706 | `same_state_city_unique_matched_cms_rows` | Cabell County, West Virginia | 0.76 | operator_review_city_match_before_assigning |
| AUXILIO MUTUO HOSPITAL | PR | SAN JUAN | 00919 | `same_state_zip5_unique_matched_cms_rows` | San Juan Muno | 0.86 | operator_spot_check_then_assign_if_address_confirms |
| BAYAMON REGIONAL HOSPITAL | PR | BAYAMON | 00956 | `same_state_zip5_unique_matched_cms_rows` | Bayamón Muno | 0.86 | operator_spot_check_then_assign_if_address_confirms |
| DOCTORS CENTER HOSPITAL SAN JUAN I | PR | SAN JUAN | 00910 | `same_state_zip5_unique_matched_cms_rows` | San Juan Muno | 0.86 | operator_spot_check_then_assign_if_address_confirms |
| UNIVERSITY PEDIATRIC HOSPITAL | PR | SAN JUAN | 00910 | `same_state_zip5_unique_matched_cms_rows` | San Juan Muno | 0.86 | operator_spot_check_then_assign_if_address_confirms |
| ADMIN DE SERVICIOS MEDICOS DE PR | PR | SAN JUAN | 00922 | `same_state_city_unique_matched_cms_rows` | San Juan Muno | 0.76 | operator_review_city_match_before_assigning |
| HOSPITAL METROPOLITANO | PR | RIO PIEDRAS | 00922 | `same_state_city_unique_matched_cms_rows` | San Juan Muno | 0.76 | operator_review_city_match_before_assigning |
| HOSPITAL SAN FRANCISCO | PR | RIO PIEDRAS | 00923 | `same_state_city_unique_matched_cms_rows` | San Juan Muno | 0.76 | operator_review_city_match_before_assigning |
| SAN JUAN MUNICIPAL HOSPITAL | PR | SAN JUAN | 00928 | `same_state_city_unique_matched_cms_rows` | San Juan Muno | 0.76 | operator_review_city_match_before_assigning |
| UNIVERSITY DISCTRICT HOSPITAL | PR | SAN JUAN | 00922 | `same_state_city_unique_matched_cms_rows` | San Juan Muno | 0.76 | operator_review_city_match_before_assigning |
| BAYLOR SURGICAL HOSPITAL LAS COLINAS | TX | IRVING | 75063 | `same_state_city_unique_matched_cms_rows` | Dallas County, Texas | 0.76 | operator_review_city_match_before_assigning |

## Boundary

- Same ZIP/city candidates are review aids, not applied geocodes.
- This artifact does not change source rows, model features, scoring, ranks, Product Mode policy, or feature eligibility.
