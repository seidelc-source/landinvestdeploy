# Institutional Anchor Provider External/Manual Geocode Packet

## TLDR

- Status: `external_manual_geocoder_packet_ready_report_only`.
- Production model/rank/dashboard change: `False`.
- Packet rows: `18`.
- Weak same-FIPS Census context manual-review rows: `1`.
- Same-city unresolved after Census rows: `17`.
- External geocoder required rows: `0`.
- Accepted override rows: `0`.

## Metrics

| Metric | Value |
|---|---:|
| `packet_rows` | 18 |
| `geocoder_input_rows` | 18 |
| `results_template_rows` | 18 |
| `weak_same_fips_census_context_manual_review_rows` | 1 |
| `same_city_unresolved_after_census_rows` | 17 |
| `external_geocoder_required_rows` | 0 |
| `cms_county_blank_rows` | 15 |
| `county_text_unmatched_rows` | 3 |
| `high_priority_rows` | 12 |
| `states_covered` | 11 |
| `accepted_override_rows` | 0 |

## Lane Counts

- `same_city_unresolved_after_census_external_geocoder`: `17`
- `weak_same_fips_census_context_manual_review`: `1`

## Top States

| State | Rows | High Priority | External | Same-City Unresolved | Weak Census Context |
|---|---:|---:|---:|---:|---:|
| PR | 5 | 0 | 0 | 5 | 0 |
| LA | 2 | 2 | 0 | 2 | 0 |
| OK | 2 | 2 | 0 | 2 | 0 |
| TX | 2 | 1 | 0 | 2 | 0 |
| CA | 1 | 1 | 0 | 1 | 0 |
| FL | 1 | 1 | 0 | 1 | 0 |
| MD | 1 | 1 | 0 | 1 | 0 |
| NE | 1 | 1 | 0 | 0 | 1 |
| NV | 1 | 1 | 0 | 1 | 0 |
| VT | 1 | 1 | 0 | 1 | 0 |
| WV | 1 | 1 | 0 | 1 | 0 |

## Top Packet Rows

| Rank | Lane | Provider | State | City | ZIP | Query | Priority |
|---:|---|---|---|---|---|---|---|
| 1 | `weak_same_fips_census_context_manual_review` | LINCOLN REGIONAL CENTER | NE | LINCOLN | 68509 | FOLSOM & PROSPECTOR, LINCOLN, NE, 68509 | `high` |
| 2 | `same_city_unresolved_after_census_external_geocoder` | OU MEDICAL CENTER | OK | OKLAHOMA CITY | 73104 | 1200 CHILDRENS AVE, OKLAHOMA CITY, OK, 73104 | `high` |
| 3 | `same_city_unresolved_after_census_external_geocoder` | SUMMERLIN HOSPITAL MEDICAL CENTER | NV | LAS VEGAS | 89114 | 657 TOWN CENTER DRIVE, LAS VEGAS, NV, 89114 | `high` |
| 4 | `same_city_unresolved_after_census_external_geocoder` | COMANCHE COUNTY MEMORIAL HOSPITAL | OK | LAWTON | 73502 | 3401 W GORE, LAWTON, OK, 73502 | `high` |
| 5 | `same_city_unresolved_after_census_external_geocoder` | IBERIA MEDICAL CENTER | LA | NEW IBERIA | 70562 | 2315 W MAIN STREET, NEW IBERIA, LA, 70562 | `high` |
| 6 | `same_city_unresolved_after_census_external_geocoder` | BRATTLEBORO RETREAT | VT | BRATTLEBORO | 05302 | ANNA MARSH LANE, BRATTLEBORO, VT, 05302 | `high` |
| 7 | `same_city_unresolved_after_census_external_geocoder` | MILDRED MITCHELL-BATEMAN HOSPITAL | WV | HUNTINGTON | 25706 | 1530 NORWAY AVENUE, HUNTINGTON, WV, 25706 | `high` |
| 8 | `same_city_unresolved_after_census_external_geocoder` | WESTERN MARYLAND HOSPITAL CENTER | MD | HAGERSTOWN | 21740 | 1500 PENNSYLVANIA AVENUE, HAGERSTOWN, MD, 21740 | `high` |
| 9 | `same_city_unresolved_after_census_external_geocoder` | ACADIA GENERAL HOSPITAL | LA | CROWLEY | 70526 | 190044, CROWLEY, LA, 70526 | `high` |
| 10 | `same_city_unresolved_after_census_external_geocoder` | LEGENT ORTHOPEDIC HOSPITAL CARROLLTO | TX | CARROLLTON | 75007 | 1401 EAST TRINITY MILLS ROAD, CARROLLTON, TX, 75007 | `high` |
| 11 | `same_city_unresolved_after_census_external_geocoder` | ENCOMPASS HEALTH REHABILITATION HOSP | FL | JACKSONVILLE | 32256 | 11595 BURNT MILL ROAD, JACKSONVILLE, FL, 32256 | `high` |
| 12 | `same_city_unresolved_after_census_external_geocoder` | WILLOW ROCK CENTER | CA | SAN LEANDRO | 94578 | 22050 FAIRMONT DRIVE, SAN LEANDRO, CA, 94578 | `high` |
| 13 | `same_city_unresolved_after_census_external_geocoder` | UNIVERSITY DISCTRICT HOSPITAL | PR | SAN JUAN | 00922 | BO. MONACILLO, SAN JUAN, PR, 00922 | `medium` |
| 14 | `same_city_unresolved_after_census_external_geocoder` | ADMIN DE SERVICIOS MEDICOS DE PR | PR | SAN JUAN | 00922 | CENTRO MEDICO, SAN JUAN, PR, 00922 | `medium` |
| 15 | `same_city_unresolved_after_census_external_geocoder` | SAN JUAN MUNICIPAL HOSPITAL | PR | SAN JUAN | 00928 | RIO PIEDRAS STATION, SAN JUAN, PR, 00928 | `medium` |
| 16 | `same_city_unresolved_after_census_external_geocoder` | HOSPITAL SAN FRANCISCO | PR | RIO PIEDRAS | 00923 | DE DIEGO AVE. #371, RIO PIEDRAS, PR, 00923 | `medium` |
| 17 | `same_city_unresolved_after_census_external_geocoder` | HOSPITAL METROPOLITANO | PR | RIO PIEDRAS | 00922 | 21 #1785, RIO PIEDRAS, PR, 00922 | `medium` |
| 18 | `same_city_unresolved_after_census_external_geocoder` | BAYLOR SURGICAL HOSPITAL LAS COLINAS | TX | IRVING | 75063 | 400 W I-635 SUITE 101, IRVING, TX, 75063 | `medium` |

## Result Template Contract

- Use the geocoder input CSV for provider address lookup.
- Return reviewed assignments in the results template columns.
- `reviewer_decision` should be `accept`, `hold`, or `reject`; accepted rows require county FIPS, county name, confidence, source, match type, reviewer, and note.

## Boundary

- This packet is report-only and applies `0` overrides.
- Do not use these rows in model training, scoring, default ranks, Product Mode policy, or source promotion until reviewed results are accepted through a separate validation pass.
