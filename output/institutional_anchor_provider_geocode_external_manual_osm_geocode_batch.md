# Institutional Anchor External/Manual OSM Geocoder Batch

## TLDR

- Status: `osm_nominatim_external_geocoder_results_ready_report_only`.
- Production model/rank/dashboard change: `False`.
- Target rows: `83`.
- Accepted review rows: `32`.
- Held review rows: `51`.

## Metrics

| Metric | Value |
|---|---:|
| `packet_rows` | 116 |
| `target_rows` | 83 |
| `lane` | external_geocoder_required_no_local_candidate |
| `attempt_rows` | 257 |
| `raw_result_rows` | 139 |
| `accepted_review_rows` | 32 |
| `held_review_rows` | 51 |
| `accepted_candidate_counties` | 32 |
| `min_accept_confidence` | 0.9 |

## Accepted Rows

| Provider | State | FIPS | County | Confidence | Geocoder Result |
|---|---|---|---|---:|---|
| NORTHBAY HOSPITAL GROUP | CA | `06095` | Solano County, California | 1.0 | NorthBay Medical Center, 1200, B Gale Wilson Boulevard, Fairfield, Solano County, California, 94533, United States |
| BAPTIST MEM HOSPITAL DESOTO | MS | `28033` | DeSoto County, Mississippi | 1.0 | Baptist Memorial Hospital-DeSoto, 7601, Southcrest Parkway, Southaven, DeSoto County, Mississippi, 38671, United States |
| FRANCISCAN HEALTH MICHIGAN CITY | IN | `18091` | LaPorte County, Indiana | 1.0 | Franciscan Health Michigan City, 3500, Franciscan Way, Michigan City, LaPorte County, Indiana, 46360, United States |
| MEMORIAL HOSPITAL OF CARBONDALE | IL | `17077` | Jackson County, Illinois | 1.0 | Memorial Hospital of Carbondale, 405, West Jackson Street, Carbondale, Jackson County, Illinois, 62902, United States |
| HCA FLORIDA WOODMONT HOSPITAL | FL | `12011` | Broward County, Florida | 1.0 | HCA Florida Woodmont Hospital, 7201, North University Drive, Tamarac, Broward County, Florida, 33321, United States |
| ATHENS REGIONAL MEDICAL CENTER | TN | `47107` | McMinn County, Tennessee | 1.0 | Starr Regional Medical Center, 1114, West Madison Avenue, Avalon Heights, Athens, McMinn County, East Tennessee, Tennessee, 37303, United States |
| NORTHCREST MEDICAL CENTER | TN | `47147` | Robertson County, Tennessee | 1.0 | TriStar NorthCrest Medical Center, 100, Northcrest Drive, Springfield, Robertson County, Middle Tennessee, Tennessee, 37172, United States |
| GRAND RIVER HOSPITAL DISTRICT | CO | `08045` | Garfield County, Colorado | 1.0 | Grand River Medical Center, 501, Airport Road, Rifle, Garfield County, Colorado, 81650, United States |
| WILLAMETTE VALLEY MEDICAL CENTER | OR | `41071` | Yamhill County, Oregon | 1.0 | Willamette Valley Medical Center, 2700, Southeast Stratus Avenue, McMinnville, Yamhill County, Oregon, 97128, United States |
| MYMICHIGAN MEDICAL CTR WEST BRAN | MI | `26129` | Ogemaw County, Michigan | 1.0 | MyMichigan Medical Center West Branch, 2463, South M-30, West Branch, Ogemaw County, Michigan, 48661, United States |
| RIVERSIDE DOCTORS HOSPITAL WILLIAMSB | VA | `51830` | Williamsburg city, Virginia | 1.0 | Riverside Doctors Hospital Williamsburg, 1500, Commonwealth Avenue, Quarterpath, Williamsburg, Virginia, 23185, United States |
| FRISBIE MEMORIAL HOSPITAL | NH | `33017` | Strafford County, New Hampshire | 1.0 | Frisbie Memorial Hospital, 11, Whitehall Road, Rochester, Strafford County, New Hampshire, 03867, United States |
| INTEGRIS GROVE HOSPITAL | OK | `40041` | Delaware County, Oklahoma | 1.0 | INTEGRIS Grove Hospital, 1001, East 18th Street, Grove, Delaware County, Oklahoma, 74344, United States |
| RUSSELLVILLE HOSPITAL | AL | `01059` | Franklin County, Alabama | 0.96 | Russellville Hospital, 15155, Gandy Street Northeast, Russellville, Franklin County, Alabama, 35653, United States |
| ASCENSION ST. JOSEPH HOSPITAL | MI | `26069` | Iosco County, Michigan | 0.96 | MyMichigan Medical Center Tawas, 200, Hemlock Street, Tawas City, Iosco County, Michigan, 48764, United States |
| UPMC BEDFORD | PA | `42009` | Bedford County, Pennsylvania | 1.0 | UPMC Bedford, 10455, Lincoln Highway, Penn Wood, Everett, Bedford County, Pennsylvania, 15537, United States |
| HOCKING VALLEY | OH | `39073` | Hocking County, Ohio | 0.96 | Hocking Valley Community Hospital, 601, SR 664, West Logan, Logan, Falls Township, Hocking County, Ohio, 43138, United States |
| MARTIN COUNTY HOSPITAL | TX | `48317` | Martin County, Texas | 0.92 | 610, North Saint Peter Street, Stanton, Martin County, Texas, 79782, United States |
| ENCOMPASS HEALTH REHABILITATION OF W | TX | `48309` | McLennan County, Texas | 1.0 | Encompass Health Rehabilitation Hospital of Waco, 3600, South Loop 340, Robinson, McLennan County, Texas, 76706, United States |
| BAYLOR SCOTT & WHITE - BUDA | TX | `48209` | Hays County, Texas | 1.0 | Baylor Scott And White Medical Center - Buda, 5330, Overpass Road, Buda, Hays County, Texas, 78610, United States |
| MCDOWELL ARH | KY | `21071` | Floyd County, Kentucky | 0.96 | McDowell ARH Hospital, 9879, KY 122, Minnie, McDowell, Floyd County, Kentucky, 41647, United States |
| LIFEBRITE COMM HOSP OF STOKES | NC | `37169` | Stokes County, North Carolina | 1.0 | LifeBrite Community Hospital of Stokes, 1570, NC 8;NC 89, Danbury, Stokes County, North Carolina, 27016, United States |
| UPMC KANE | PA | `42083` | McKean County, Pennsylvania | 0.96 | UPMC Kane, 4372, Grand Army of the Republic Highway, Kane, McKean County, Pennsylvania, 16735, United States |
| LAKEWOOD HEALTH CENTER | MN | `27077` | Lake of the Woods County, Minnesota | 1.0 | LakeWood Health Center, 600, Main Avenue South, Baudette, Lake of the Woods County, Minnesota, 56623, United States |
| DRUMRIGHT REGIONAL HOSPITAL | OK | `40037` | Creek County, Oklahoma | 0.96 | Drumright Regional Hospital, 610, Veterans Memorial Highway, Drumright, Creek County, Oklahoma, 74030, United States |
| ROGER MILLS MEMORIAL HOSPITAL | OK | `40129` | Roger Mills County, Oklahoma | 1.0 | Roger Mills Memorial Hospital, 501, South L. L. Males Avenue, Cheyenne, Roger Mills County, Oklahoma, 73628, United States |
| PRAIRIECARE | MN | `27053` | Hennepin County, Minnesota | 1.0 | PrairieCare Children's Psychiatric Hospital, 9400, Zane Avenue North, Brooklyn Park, Hennepin County, Minnesota, 55443, United States |
| EMMA P BRADLEY HOSPITAL | RI | `44007` | Providence County, Rhode Island | 1.0 | Bradley Hospital, 1011, Veterans Memorial Parkway, Silver Spring, East Providence, Providence County, Rhode Island, 02915, United States |
| CUMBERLAND HOSPITAL LLC | VA | `51127` | New Kent County, Virginia | 1.0 | Cumberland Hospital for Children and Adolescents, 9407, Cumberland Road, New Kent County, Virginia, 23124, United States |
| HIGHLAND CLARKSBURG HOSPITAL INC | WV | `54033` | Harrison County, West Virginia | 1.0 | Highland-Clarksburg Hospital, 3, Hospital Plaza, Clarksburg, Harrison County, West Virginia, 26301, United States |
| SANFORD HOSPITAL CANBY | MN | `27173` | Yellow Medicine County, Minnesota | 1.0 | Sanford Canby Medical Center, 112, Saint Olaf Avenue South, Canby, Yellow Medicine County, Minnesota, 56220, United States |
| CIMARRON MEMORIAL HOSPITAL | OK | `40025` | Cimarron County, Oklahoma | 1.0 | Cimarron Memorial Hospital and Nursing Home, 100, South Ellis Avenue, Boise City, Cimarron County, Oklahoma, 73933, United States |

## Boundary

- This runner creates reviewed-result rows only; it does not append overrides.
- The external/manual acceptance validator remains the only script that can apply accepted rows.
- OpenStreetMap/Nominatim evidence is report-only review evidence and must not enter production model features, scoring, ranks, Product Mode policy, source promotion, or feature eligibility until all source-maturity, leakage, and model-impact gates pass.
