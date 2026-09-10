# Institutional Anchor External/Manual Census Context Review

## TLDR

- Status: `strict_census_context_review_results_ready_report_only`.
- Production model/rank/dashboard change: `False`.
- Accepted review rows: `29`.
- Held review rows: `128`.

## Metrics

| Metric | Value |
|---|---:|
| `template_rows` | 157 |
| `packet_rows` | 157 |
| `prior_census_candidate_rows_for_packet` | 157 |
| `accepted_review_rows` | 29 |
| `held_review_rows` | 128 |
| `min_score` | 0.88 |
| `min_confidence` | 0.89 |

## Accepted Rows

| Provider | State | FIPS | County | Confidence | Matched Address |
|---|---|---|---|---:|---|
| YAKIMA VALLEY MEMORIAL HOSPITAL | WA | `53077` | Yakima County, Washington | 0.89 | 2811 W TIETON DR, YAKIMA, WA, 98902 |
| COREWELL HEALTH- FARMINGTON HILLS | MI | `26125` | Oakland County, Michigan | 0.89 | 28050 GRAND RIVER AVE, FARMINGTON HILLS, MI, 48336 |
| MACNEAL HOSPITAL | IL | `17031` | Cook County, Illinois | 0.89 | 3249 OAK PARK AVE, BERWYN, IL, 60402 |
| MEDICAL CITY LEWISVILLE | TX | `48121` | Denton County, Texas | 0.89 | 500 W MAIN ST, LEWISVILLE, TX, 75067 |
| COREWELL HEALTH WAYNE | MI | `26163` | Wayne County, Michigan | 0.89 | 33155 ANNAPOLIS ST, WAYNE, MI, 48184 |
| MONROE REGIONAL HOSPITAL | MI | `26115` | Monroe County, Michigan | 0.89 | 718 N MACOMB ST, MONROE, MI, 48162 |
| HAMPDEN MEDICAL CENTER | PA | `42041` | Cumberland County, Pennsylvania | 0.89 | 2200 N GOOD HOPE RD, ENOLA, PA, 17025 |
| WEST CALCASIEU-CAMERON HOSPITAL | LA | `22019` | Calcasieu Parish, Louisiana | 0.89 | 701 CYPRESS ST, SULPHUR, LA, 70663 |
| ST. CHARLES PARISH HOSPITAL | LA | `22089` | St. Charles Parish, Louisiana | 0.89 | 1057 PAUL MAILLARD RD, LULING, LA, 70070 |
| MERCY HOSPITAL LINCOLN | MO | `29113` | Lincoln County, Missouri | 0.89 | 1000 W CHERRY ST, TROY, MO, 63379 |
| FRANCISCAN HEALTH CRAWFORDSVILLE | IN | `18107` | Montgomery County, Indiana | 0.89 | 1710 LAFAYETTE AVE, CRAWFORDSVILLE, IN, 47933 |
| S.E. LACKEY MEMORIAL HOSPITAL | MS | `28123` | Scott County, Mississippi | 0.89 | 330 N BROAD ST, FOREST, MS, 39074 |
| DESERT VIEW REGIONAL MEDICAL CENTER | NV | `32023` | Nye County, Nevada | 0.89 | 360 LOLA, PAHRUMP, NV, 89048 |
| HILLCREST HOSPITAL PRYOR | OK | `40097` | Mayes County, Oklahoma | 0.89 | 111 N BAILEY ST, PRYOR, OK, 74361 |
| UNIVERSITY HOSPITAL MCDUFFIE | GA | `13189` | McDuffie County, Georgia | 0.89 | 2460 WASHINGTON RD, THOMSON, GA, 30824 |
| UNIVERSITY HOSPITAL MCDUFFIE | GA | `13189` | McDuffie County, Georgia | 0.89 | 2460 WASHINGTON RD, THOMSON, GA, 30824 |
| IROQUOIS MEMORIAL HOSPITAL | IL | `17075` | Iroquois County, Illinois | 0.89 | 200 E FAIRMAN AVE, WATSEKA, IL, 60970 |
| IROQUOIS MEMORIAL HOSPITAL | IL | `17075` | Iroquois County, Illinois | 0.89 | 200 E FAIRMAN AVE, WATSEKA, IL, 60970 |
| MID COAST MEDICAL CENTER-CENTRAL | TX | `48299` | Llano County, Texas | 0.89 | 200 W OLLIE ST, LLANO, TX, 78643 |
| HARMON MEMORIAL HOSPITAL | OK | `40057` | Harmon County, Oklahoma | 0.89 | 400 E CHESTNUT ST, HOLLIS, OK, 73550 |
| COON MEMORIAL HOSPITAL | TX | `48205` | Hartley County, Texas | 0.89 | 1411 DENVER AVE, DALHART, TX, 79022 |
| TANNER MEDICAL CENTER ALABAMA INC. | AL | `01111` | Randolph County, Alabama | 0.89 | 1032 N MAIN ST, WEDOWEE, AL, 36278 |
| HILLSBORO COMMUNITY HOSPITAL | KS | `20115` | Marion County, Kansas | 0.89 | 101 INDUSTRIAL RD, HILLSBORO, KS, 67063 |
| ASPIRUS EAGLE RIVER HOSPITAL | WI | `55125` | Vilas County, Wisconsin | 0.89 | 201 E HOSPITAL RD, EAGLE RIVER, WI, 54521 |
| ROYAL OAKS HOSPITAL | MO | `29083` | Henry County, Missouri | 0.89 | 307 N MAIN ST, WINDSOR, MO, 65360 |
| HOSPITAL METRO HATO REY INC. | PR | `72127` | San Juan Muno | 0.89 | 435 AVE PONCE DE LEON, HATO REY, PR, 00917 |
| HOSPITAL PSIQUIATRICO CABO ROJO | PR | `72023` | Cabo Rojo Muno | 0.89 | 108 CLL MUNOZ RIVERA, CABO ROJO, PR, 00623 |
| HOOD MEMORIAL HOSPITAL | LA | `22105` | Tangipahoa Parish, Louisiana | 0.89 | 301 WALNUT ST, AMITE, LA, 70422 |
| CORDOVA COMMUNITY MEDICAL CENTER | AK | `02063` | Chugach Census Area, Alaska | 0.89 | 602 CHASE AVE, CORDOVA, AK, 99574 |

## Boundary

- This builder only populates reviewed-result rows; it does not append overrides.
- The acceptance validator remains the only script that can apply these reviewed rows to the report-only override file.
- Institutional anchors remain blocked for production model, scoring, rank, Product Mode policy, source promotion, and feature eligibility until all source-maturity, leakage, and model-impact gates pass.
