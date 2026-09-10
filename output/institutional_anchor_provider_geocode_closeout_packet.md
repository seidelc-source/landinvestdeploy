# Institutional Anchor Provider Geocode Closeout Packet

## TLDR

- Status: `provider_geocode_closeout_packet_ready_report_only`.
- Production model/rank/dashboard change: `False`.
- Packet rows: `22`.
- Same-ZIP closeout rows: `4`.
- Same-city closeout rows: `18`.
- External geocode rows: `0`.

## Metrics

| Metric | Value |
|---|---:|
| `packet_rows` | 22 |
| `same_zip_closeout_rows` | 4 |
| `same_city_closeout_rows` | 18 |
| `external_geocode_required_rows` | 0 |
| `local_closeout_candidate_rows` | 22 |
| `high_priority_rows` | 12 |
| `top100_same_zip_rows` | 4 |
| `top100_same_city_rows` | 18 |
| `top100_external_rows` | 0 |
| `source_maturity_provider_geocode_review_rows` | 26 |
| `source_maturity_unresolved_product_county_rows` | 2 |
| `review_artifact_rows` | 22 |

## Action Counts

- `spot_check_same_city_candidate_before_assignment`: `18`
- `approve_same_zip_candidate_after_address_spotcheck`: `4`

## Top Packet Rows

| Rank | Action | Provider | State | City | ZIP | Suggested County | Confidence | Volume |
|---:|---|---|---|---|---|---|---:|---:|
| 1 | `approve_same_zip_candidate_after_address_spotcheck` | AUXILIO MUTUO HOSPITAL | PR | SAN JUAN | 00919 | San Juan Muno | 0.86 | 0.96 |
| 2 | `approve_same_zip_candidate_after_address_spotcheck` | DOCTORS CENTER HOSPITAL SAN JUAN I | PR | SAN JUAN | 00910 | San Juan Muno | 0.86 | 0.22 |
| 3 | `approve_same_zip_candidate_after_address_spotcheck` | BAYAMON REGIONAL HOSPITAL | PR | BAYAMON | 00956 | Bayamón Muno | 0.86 | 0.17 |
| 4 | `approve_same_zip_candidate_after_address_spotcheck` | UNIVERSITY PEDIATRIC HOSPITAL | PR | SAN JUAN | 00910 | San Juan Muno | 0.86 | 0.00 |
| 5 | `spot_check_same_city_candidate_before_assignment` | OU MEDICAL CENTER | OK | OKLAHOMA CITY | 73104 | Oklahoma County, Oklahoma | 0.76 | 1.00 |
| 6 | `spot_check_same_city_candidate_before_assignment` | SUMMERLIN HOSPITAL MEDICAL CENTER | NV | LAS VEGAS | 89114 | Clark County, Nevada | 0.76 | 0.96 |
| 7 | `spot_check_same_city_candidate_before_assignment` | COMANCHE COUNTY MEMORIAL HOSPITAL | OK | LAWTON | 73502 | Comanche County, Oklahoma | 0.76 | 0.57 |
| 8 | `spot_check_same_city_candidate_before_assignment` | LINCOLN REGIONAL CENTER | NE | LINCOLN | 68509 | Lancaster County, Nebraska | 0.76 | 0.53 |
| 9 | `spot_check_same_city_candidate_before_assignment` | IBERIA MEDICAL CENTER | LA | NEW IBERIA | 70562 | Iberia Parish, Louisiana | 0.76 | 0.26 |
| 10 | `spot_check_same_city_candidate_before_assignment` | BRATTLEBORO RETREAT | VT | BRATTLEBORO | 05302 | Windham County, Vermont | 0.76 | 0.22 |
| 11 | `spot_check_same_city_candidate_before_assignment` | MILDRED MITCHELL-BATEMAN HOSPITAL | WV | HUNTINGTON | 25706 | Cabell County, West Virginia | 0.76 | 0.22 |
| 12 | `spot_check_same_city_candidate_before_assignment` | WESTERN MARYLAND HOSPITAL CENTER | MD | HAGERSTOWN | 21740 | Washington County, Maryland | 0.76 | 0.12 |
| 13 | `spot_check_same_city_candidate_before_assignment` | ACADIA GENERAL HOSPITAL | LA | CROWLEY | 70526 | Acadia Parish, Louisiana | 0.76 | 0.12 |
| 14 | `spot_check_same_city_candidate_before_assignment` | LEGENT ORTHOPEDIC HOSPITAL CARROLLTO | TX | CARROLLTON | 75007 | Denton County, Texas | 0.76 | 0.10 |
| 15 | `spot_check_same_city_candidate_before_assignment` | ENCOMPASS HEALTH REHABILITATION HOSP | FL | JACKSONVILLE | 32256 | Duval County, Florida | 0.76 | 0.10 |
| 16 | `spot_check_same_city_candidate_before_assignment` | WILLOW ROCK CENTER | CA | SAN LEANDRO | 94578 | Alameda County, California | 0.76 | 0.00 |
| 17 | `spot_check_same_city_candidate_before_assignment` | UNIVERSITY DISCTRICT HOSPITAL | PR | SAN JUAN | 00922 | San Juan Muno | 0.76 | 0.40 |
| 18 | `spot_check_same_city_candidate_before_assignment` | ADMIN DE SERVICIOS MEDICOS DE PR | PR | SAN JUAN | 00922 | San Juan Muno | 0.76 | 0.39 |
| 19 | `spot_check_same_city_candidate_before_assignment` | SAN JUAN MUNICIPAL HOSPITAL | PR | SAN JUAN | 00928 | San Juan Muno | 0.76 | 0.29 |
| 20 | `spot_check_same_city_candidate_before_assignment` | HOSPITAL SAN FRANCISCO | PR | RIO PIEDRAS | 00923 | San Juan Muno | 0.76 | 0.27 |
| 21 | `spot_check_same_city_candidate_before_assignment` | HOSPITAL METROPOLITANO | PR | RIO PIEDRAS | 00922 | San Juan Muno | 0.76 | 0.26 |
| 22 | `spot_check_same_city_candidate_before_assignment` | BAYLOR SURGICAL HOSPITAL LAS COLINAS | TX | IRVING | 75063 | Dallas County, Texas | 0.76 | 0.13 |

## Decision

- Provider geocode closeout is staged for operator review only; no CMS county assignment is applied.
- Next action: Close same-ZIP candidates first, spot-check same-city candidates second, and route external rows through an approved provider street-address geocoder before rerunning the institutional source maturity gate.

## Boundary

- This packet is report-only and suitable for operator closeout sequencing.
- It does not write source rows, change model features, retrain models, score counties, alter ranks, or change Product Mode behavior.
