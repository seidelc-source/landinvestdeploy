# Institutional Anchor External/Manual Residual Triage Packet

## TLDR

- Status: `external_manual_residual_triage_ready_report_only`.
- Production model/rank/dashboard change: `False`.
- Triage rows: `18`.
- External-geocoder follow-up rows: `0`.
- Same-city held manual-review rows: `17`.
- Weak Census-context manual-review rows: `1`.
- P0 rows: `0`.

## Metrics

| Metric | Value |
|---|---:|
| `triage_rows` | 18 |
| `external_geocoder_followup_rows` | 0 |
| `same_city_held_manual_review_rows` | 17 |
| `weak_census_context_manual_review_rows` | 1 |
| `p0_rows` | 0 |
| `p1_rows` | 12 |
| `p2_rows` | 6 |
| `high_priority_rows` | 12 |
| `states_covered` | 11 |
| `prior_osm_no_result_rows` | 1 |
| `prior_osm_house_number_issue_rows` | 9 |
| `prior_osm_postcode_issue_rows` | 10 |
| `prior_osm_city_issue_rows` | 2 |
| `production_model_rank_or_dashboard_change` | False |

## Triage Lanes

- `same_city_held_manual_review`: `17`
- `weak_census_context_manual_review`: `1`

## Top States

| State | Rows | P0 | High Priority | External | Same-City Held | Weak Context |
|---|---:|---:|---:|---:|---:|---:|
| PR | 5 | 0 | 0 | 0 | 5 | 0 |
| LA | 2 | 0 | 2 | 0 | 2 | 0 |
| OK | 2 | 0 | 2 | 0 | 2 | 0 |
| TX | 2 | 0 | 1 | 0 | 2 | 0 |
| CA | 1 | 0 | 1 | 0 | 1 | 0 |
| FL | 1 | 0 | 1 | 0 | 1 | 0 |
| MD | 1 | 0 | 1 | 0 | 1 | 0 |
| NE | 1 | 0 | 1 | 0 | 0 | 1 |
| NV | 1 | 0 | 1 | 0 | 1 | 0 |
| VT | 1 | 0 | 1 | 0 | 1 | 0 |
| WV | 1 | 0 | 1 | 0 | 1 | 0 |

## Top Triage Rows

| Rank | Priority | Lane | Provider | State | City | Prior OSM Issue | Next Action |
|---:|---|---|---|---|---|---|---|
| 1 | `P1` | `same_city_held_manual_review` | OU MEDICAL CENTER | OK | OKLAHOMA CITY | house_number_not_supported; confidence_below_0_90 | Reserve for manual/source-backed review for Oklahoma County, Oklahoma; do not accept the same-city heuristic alone. |
| 2 | `P1` | `same_city_held_manual_review` | SUMMERLIN HOSPITAL MEDICAL CENTER | NV | LAS VEGAS | postcode_not_supported; confidence_below_0_90 | Reserve for manual/source-backed review for Clark County, Nevada; do not accept the same-city heuristic alone. |
| 3 | `P1` | `same_city_held_manual_review` | COMANCHE COUNTY MEMORIAL HOSPITAL | OK | LAWTON | postcode_not_supported; confidence_below_0_90 | Reserve for manual/source-backed review for Comanche County, Oklahoma; do not accept the same-city heuristic alone. |
| 4 | `P1` | `same_city_held_manual_review` | IBERIA MEDICAL CENTER | LA | NEW IBERIA | postcode_not_supported; confidence_below_0_90 | Reserve for manual/source-backed review for Iberia Parish, Louisiana; do not accept the same-city heuristic alone. |
| 5 | `P1` | `same_city_held_manual_review` | BRATTLEBORO RETREAT | VT | BRATTLEBORO | house_number_not_supported; confidence_below_0_90 | Reserve for manual/source-backed review for Windham County, Vermont; do not accept the same-city heuristic alone. |
| 6 | `P1` | `same_city_held_manual_review` | MILDRED MITCHELL-BATEMAN HOSPITAL | WV | HUNTINGTON | postcode_not_supported; confidence_below_0_90 | Reserve for manual/source-backed review for Cabell County, West Virginia; do not accept the same-city heuristic alone. |
| 7 | `P1` | `same_city_held_manual_review` | WESTERN MARYLAND HOSPITAL CENTER | MD | HAGERSTOWN | postcode_not_supported; confidence_below_0_90 | Reserve for manual/source-backed review for Washington County, Maryland; do not accept the same-city heuristic alone. |
| 8 | `P1` | `same_city_held_manual_review` | ACADIA GENERAL HOSPITAL | LA | CROWLEY | house_number_not_supported; postcode_not_supported; confidence_below_0_90 | Reserve for manual/source-backed review for Acadia Parish, Louisiana; do not accept the same-city heuristic alone. |
| 9 | `P1` | `same_city_held_manual_review` | LEGENT ORTHOPEDIC HOSPITAL CARROLLTO | TX | CARROLLTON | postcode_not_supported; confidence_below_0_90 | Reserve for manual/source-backed review for Denton County, Texas; do not accept the same-city heuristic alone. |
| 10 | `P1` | `same_city_held_manual_review` | ENCOMPASS HEALTH REHABILITATION HOSP | FL | JACKSONVILLE | house_number_not_supported; confidence_below_0_90 | Reserve for manual/source-backed review for Duval County, Florida; do not accept the same-city heuristic alone. |
| 11 | `P1` | `same_city_held_manual_review` | WILLOW ROCK CENTER | CA | SAN LEANDRO | house_number_not_supported; confidence_below_0_90 | Reserve for manual/source-backed review for Alameda County, California; do not accept the same-city heuristic alone. |
| 12 | `P2` | `same_city_held_manual_review` | UNIVERSITY DISCTRICT HOSPITAL | PR | SAN JUAN | house_number_not_supported; postcode_not_supported; result_type_name_or_road_not_supported; confidence_below_0_90 | Reserve for manual/source-backed review for San Juan Muno; do not accept the same-city heuristic alone. |
| 13 | `P2` | `same_city_held_manual_review` | ADMIN DE SERVICIOS MEDICOS DE PR | PR | SAN JUAN | house_number_not_supported; postcode_not_supported; result_type_name_or_road_not_supported; confidence_below_0_90 | Reserve for manual/source-backed review for San Juan Muno; do not accept the same-city heuristic alone. |
| 14 | `P2` | `same_city_held_manual_review` | SAN JUAN MUNICIPAL HOSPITAL | PR | SAN JUAN | house_number_not_supported; postcode_not_supported; confidence_below_0_90 | Reserve for manual/source-backed review for San Juan Muno; do not accept the same-city heuristic alone. |
| 15 | `P2` | `same_city_held_manual_review` | HOSPITAL SAN FRANCISCO | PR | RIO PIEDRAS | city_not_supported | Reserve for manual/source-backed review for San Juan Muno; do not accept the same-city heuristic alone. |
| 16 | `P2` | `same_city_held_manual_review` | HOSPITAL METROPOLITANO | PR | RIO PIEDRAS | house_number_not_supported; city_not_supported; confidence_below_0_90 | Reserve for manual/source-backed review for San Juan Muno; do not accept the same-city heuristic alone. |
| 17 | `P2` | `same_city_held_manual_review` | BAYLOR SURGICAL HOSPITAL LAS COLINAS | TX | IRVING | no_geocoder_result | Reserve for manual/source-backed review for Dallas County, Texas; do not accept the same-city heuristic alone. |
| 18 | `P1` | `weak_census_context_manual_review` | LINCOLN REGIONAL CENTER | NE | LINCOLN | - | Manual review only; require independent street/ZIP evidence before any override. |

## Boundary

- This packet only triages residual rows; it applies `0` overrides.
- The external/manual acceptance validator remains the only path for appending reviewed provider-year overrides.
- Institutional anchors remain report-only and must not enter production model features, scoring, ranks, Product Mode policy, source promotion, or feature eligibility until source-maturity, leakage, and model-impact gates clear.
