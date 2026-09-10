# Institutional Anchor Same-City Provider Review Packet

## TLDR

- Status: `same_city_review_packet_ready_report_only`.
- Production model/rank/dashboard change: `False`.
- Decision: Residual same-city rows are staged for controlled review; strict exact conflicts, strict same-FIPS context rows, and street/intersection-supported spot-check rows have separate report-only acceptance scripts.
- Next action: Run the next applicable acceptance or geocode-review packet, then rebuild institutional panel, review, closeout, source maturity, registry, and Evidence Center artifacts.

## Metrics

| Metric | Value |
|---|---:|
| `same_city_review_rows` | 18 |
| `strict_conflict_correction_candidate_rows` | 0 |
| `strict_non_exact_same_fips_candidate_rows` | 0 |
| `operator_spot_check_census_context_same_fips_rows` | 1 |
| `manual_same_city_census_conflict_review_rows` | 0 |
| `operator_spot_check_census_context_other_rows` | 0 |
| `external_or_manual_geocode_required_rows` | 17 |

## Review Action Counts

- `external_or_manual_geocode_required`: `17`
- `operator_spot_check_census_context_same_fips`: `1`

## Census Status Counts

- `same_city_census_context_only`: `1`
- `unresolved_after_census_batch`: `17`

## Top Rows

| Rank | Action | Provider | State | City | ZIP | Suggested County | Census County | Census Type |
|---:|---|---|---|---|---|---|---|---|
| 1 | `operator_spot_check_census_context_same_fips` | LINCOLN REGIONAL CENTER | NE | LINCOLN | 68509 | Lancaster County, Nebraska | Lancaster County, Nebraska | Non_Exact |
| 2 | `external_or_manual_geocode_required` | OU MEDICAL CENTER | OK | OKLAHOMA CITY | 73104 | Oklahoma County, Oklahoma | - | - |
| 3 | `external_or_manual_geocode_required` | SUMMERLIN HOSPITAL MEDICAL CENTER | NV | LAS VEGAS | 89114 | Clark County, Nevada | - | - |
| 4 | `external_or_manual_geocode_required` | COMANCHE COUNTY MEMORIAL HOSPITAL | OK | LAWTON | 73502 | Comanche County, Oklahoma | - | - |
| 5 | `external_or_manual_geocode_required` | IBERIA MEDICAL CENTER | LA | NEW IBERIA | 70562 | Iberia Parish, Louisiana | - | - |
| 6 | `external_or_manual_geocode_required` | BRATTLEBORO RETREAT | VT | BRATTLEBORO | 05302 | Windham County, Vermont | - | - |
| 7 | `external_or_manual_geocode_required` | MILDRED MITCHELL-BATEMAN HOSPITAL | WV | HUNTINGTON | 25706 | Cabell County, West Virginia | - | - |
| 8 | `external_or_manual_geocode_required` | WESTERN MARYLAND HOSPITAL CENTER | MD | HAGERSTOWN | 21740 | Washington County, Maryland | - | - |
| 9 | `external_or_manual_geocode_required` | ACADIA GENERAL HOSPITAL | LA | CROWLEY | 70526 | Acadia Parish, Louisiana | - | - |
| 10 | `external_or_manual_geocode_required` | LEGENT ORTHOPEDIC HOSPITAL CARROLLTO | TX | CARROLLTON | 75007 | Denton County, Texas | - | - |
| 11 | `external_or_manual_geocode_required` | ENCOMPASS HEALTH REHABILITATION HOSP | FL | JACKSONVILLE | 32256 | Duval County, Florida | - | - |
| 12 | `external_or_manual_geocode_required` | WILLOW ROCK CENTER | CA | SAN LEANDRO | 94578 | Alameda County, California | - | - |
| 13 | `external_or_manual_geocode_required` | UNIVERSITY DISCTRICT HOSPITAL | PR | SAN JUAN | 00922 | San Juan Muno | - | - |
| 14 | `external_or_manual_geocode_required` | ADMIN DE SERVICIOS MEDICOS DE PR | PR | SAN JUAN | 00922 | San Juan Muno | - | - |
| 15 | `external_or_manual_geocode_required` | SAN JUAN MUNICIPAL HOSPITAL | PR | SAN JUAN | 00928 | San Juan Muno | - | - |
| 16 | `external_or_manual_geocode_required` | HOSPITAL SAN FRANCISCO | PR | RIO PIEDRAS | 00923 | San Juan Muno | - | - |
| 17 | `external_or_manual_geocode_required` | HOSPITAL METROPOLITANO | PR | RIO PIEDRAS | 00922 | San Juan Muno | - | - |
| 18 | `external_or_manual_geocode_required` | BAYLOR SURGICAL HOSPITAL LAS COLINAS | TX | IRVING | 75063 | Dallas County, Texas | - | - |

## Boundary

- This packet is report-only source-review evidence.
- It does not modify provider overrides, source promotion, model features, scoring, ranks, or dashboard defaults.
