# Institutional Anchor External/Manual OSM Geocoder Batch

## TLDR

- Status: `osm_nominatim_external_geocoder_results_ready_report_only`.
- Production model/rank/dashboard change: `False`.
- Target rows: `32`.
- Accepted review rows: `12`.
- Held review rows: `20`.

## Metrics

| Metric | Value |
|---|---:|
| `packet_rows` | 84 |
| `target_rows` | 32 |
| `lane` | same_city_unresolved_after_census_external_geocoder |
| `attempt_rows` | 98 |
| `raw_result_rows` | 97 |
| `accepted_review_rows` | 12 |
| `held_review_rows` | 20 |
| `accepted_candidate_counties` | 11 |
| `min_accept_confidence` | 0.9 |

## Accepted Rows

| Provider | State | FIPS | County | Confidence | Geocoder Result |
|---|---|---|---|---:|---|
| HCA FLORIDA KENDALL HOSPITAL | FL | `12086` | Miami-Dade County, Florida | 0.96 | Kendall Regional Medical Center, 11750, Southwest 40th Street, Miami, Miami-Dade County, Florida, 33175, United States |
| OUR LADY OF THE LAKE RMC | LA | `22033` | East Baton Rouge Parish, Louisiana | 0.92 | Saint Francis Chapel at Our Lady of the Lake Regional Medical Center, 5000, Hennessy Boulevard, Baton Rouge, East Baton Rouge Parish, Louisiana, 70808, United States |
| CORPUS CHRISTI MEDICAL CENTER | TX | `48355` | Nueces County, Texas | 1.0 | Corpus Christi Medical Center - Bay Area, 7101, South Padre Island Drive, Corpus Christi, Nueces County, Texas, 78412, United States |
| BANNER ESTRELLA MEDICAL CENTER | AZ | `04013` | Maricopa County, Arizona | 1.0 | Banner Estrella Medical Center, 9201, West Thomas Road, Maryvale, Phoenix, Maricopa County, Arizona, 85037, United States |
| BAYLOR S&W MEDICAL CENTER - IRVING | TX | `48113` | Dallas County, Texas | 1.0 | Baylor Scott & White Medical Center – Irving, 1901, North MacArthur Boulevard, Irving, Dallas County, Texas, 75061, United States |
| OCHSNER MEDICAL CENTER -NORTHSHORE | LA | `22103` | St. Tammany Parish, Louisiana | 1.0 | Ochsner Medical Center - North Shore, 100, Medical Center Drive, Pearl Acres, Slidell, St. Tammany Parish, Louisiana, 70461, United States |
| JEWISH HOME FOR THE AGED | CA | `06075` | San Francisco County, California | 1.0 | San Francisco Campus for Jewish Living, 302, Silver Avenue, St. Mary's Park, Excelsior, San Francisco, California, 94112, United States |
| CUMBERLAND SURGICAL HOSPITAL | TX | `48029` | Bexar County, Texas | 1.0 | Cumberland Surgical Hospital, 5330, North Loop 1604 West, San Antonio, Bexar County, Texas, 78249, United States |
| CAREPARTNERS REHAB HOSPITAL | NC | `37021` | Buncombe County, North Carolina | 1.0 | CarePartners Rehabilitation Hospital, 68, Sweeten Creek Road, Biltmore, Biltmore Village, Asheville, Buncombe County, North Carolina, 28803, United States |
| SAN LUCAS PONCE | PR | `72113` | Ponce Muno | 1.0 | Hospital San Lucas, 917, Avenida Tito Castro, La Coroza, Sector Lajes, Machuelo Abajo, Ponce, Puerto Rico, 00733, United States |
| HOSPITAL DAMAS | PR | `72113` | Ponce Muno | 1.0 | Hospital Damas, 2213, Ponce Bypass, Playa, Ponce, Puerto Rico, 00717, United States |
| HOSPITAL FOR BEHAVIORAL MEDICINE | MA | `25027` | Worcester County, Massachusetts | 1.0 | Hospital for Behavioral Medicine, 100, Century Drive, Great Brook Valley, Worcester, Worcester County, Massachusetts, 01606, United States |

## Boundary

- This runner creates reviewed-result rows only; it does not append overrides.
- The external/manual acceptance validator remains the only script that can apply accepted rows.
- OpenStreetMap/Nominatim evidence is report-only review evidence and must not enter production model features, scoring, ranks, Product Mode policy, source promotion, or feature eligibility until all source-maturity, leakage, and model-impact gates pass.
