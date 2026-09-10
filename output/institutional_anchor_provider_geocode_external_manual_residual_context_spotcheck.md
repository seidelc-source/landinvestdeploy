# Institutional Anchor External/Manual Residual Census Context Spot-Check

## TLDR

- Status: `strict_residual_census_context_spotcheck_results_ready_report_only`.
- Production model/rank/dashboard change: `False`.
- Accepted review rows: `8`.
- Held review rows: `18`.

## Metrics

| Metric | Value |
|---|---:|
| `candidate_rows` | 128 |
| `packet_rows` | 124 |
| `context_candidate_rows` | 26 |
| `reviewed_results_rows` | 26 |
| `accepted_review_rows` | 8 |
| `held_review_rows` | 18 |
| `accepted_candidate_counties` | 8 |
| `min_score` | 0.88 |
| `min_confidence` | 0.86 |

## Accepted Rows

| Provider | State | FIPS | County | Confidence | Matched Address |
|---|---|---|---|---:|---|
| HCA FLORIDA NORTHWEST HOSPITAL | FL | `12011` | Broward County, Florida | 0.86 | 2801 STATE HWY 7, MARGATE, FL, 33063 |
| SAN JOSE BEHAVIORAL HEALTH | CA | `06085` | Santa Clara County, California | 0.86 | 455 SILICON VALLEY BLVD, SAN JOSE, CA, 95138 |
| MIRAMOUNT BEHAVIORAL HEALTH | WI | `55025` | Dane County, Wisconsin | 0.86 | 3169 DEMING WAY, MIDDLETON, WI, 53562 |
| MYMICHIGAN MEDICAL CENTER GLADWIN | MI | `26051` | Gladwin County, Michigan | 0.86 | 515 QUARTER ST, GLADWIN, MI, 48624 |
| MOUNTAIN VIEW HOSPITAL | AL | `01055` | Etowah County, Alabama | 0.86 | 3001 SCENIC HWY, GADSDEN, AL, 35904 |
| MERCY BEHAVIORAL HOSPITAL | LA | `22079` | Rapides Parish, Louisiana | 0.86 | 2810 US HWY 71, LECOMPTE, LA, 71346 |
| PIEDMONT FAYETTE HOSPITAL INC. | GA | `13113` | Fayette County, Georgia | 0.86 | 1255 STATE RTE 54, FAYETTEVILLE, GA, 30214 |
| LONE PEAK HOSPITAL | UT | `49035` | Salt Lake County, Utah | 0.86 | 11925 STATE ST, DRAPER, UT, 84020 |

## Boundary

- This builder only populates reviewed-result rows; it does not append overrides.
- The acceptance validator remains the only script that can apply these reviewed rows to the report-only override file.
- Institutional anchors remain blocked for production model, scoring, rank, Product Mode policy, source promotion, and feature eligibility until all source-maturity, leakage, and model-impact gates pass.
