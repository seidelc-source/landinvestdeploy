# SEC Auto-Reuse Final Held External Evidence

## TLDR

- Status: `final_held_external_evidence_ready_report_only`.
- Production model/rank/dashboard change: `False`.
- Open input rows: `4`.
- Accepted external-evidence rows: `4`.
- Held rows after external evidence: `0`.

## Metrics

| Metric | Value |
|---|---:|
| `open_input_rows` | 4 |
| `external_evidence_source_rows` | 4 |
| `accepted_external_evidence_rows` | 4 |
| `accepted_external_evidence_address_keys` | 2 |
| `held_rows_after_external_evidence` | 0 |
| `accepted_counties` | 2 |

## Status Counts

- `accepted_external_address_county_same_fips`: `4`

## Row Preview

| Entity | Filing Date | Filing Street | Status | County | Best Evidence |
|---|---|---|---|---|---|
| Apple Inc. | 2015-07-22 | 36743 Apple Inc. California 94-2404110 1 Infinite Loop | `accepted_external_address_county_same_fips` | Santa Clara County, California | OpenStreetMap Nominatim |
| Apple Inc. | 2015-10-28 | 36743 Apple Inc. California 94-2404110 1 Infinite Loop | `accepted_external_address_county_same_fips` | Santa Clara County, California | OpenStreetMap Nominatim |
| Clearway Energy, Inc. | 2016-11-04 | 804 Carnegie Center | `accepted_external_address_county_same_fips` | Mercer County, New Jersey | New Jersey Department of Environmental Protection 2017 news release archive |
| Clearway Energy, Inc. | 2017-02-28 | 804 Carnegie Center | `accepted_external_address_county_same_fips` | Mercer County, New Jersey | New Jersey Department of Environmental Protection 2017 news release archive |

## Sources

- `apple_infinite_loop_osm_nominatim_20260603`: OpenStreetMap Nominatim (https://nominatim.openstreetmap.org/search?format=jsonv2&addressdetails=1&limit=3&q=1%20Infinite%20Loop%2C%20Cupertino%2C%20CA%2095014) - Nominatim returned an exact addressdetails result for Infinite Loop 1 at 1 Infinite Loop, Cupertino, Santa Clara County, CA 95014.
- `apple_infinite_loop_commons_location_20260603`: Wikimedia Commons Infinite Loop category (https://commons.wikimedia.org/wiki/Category:Infinite_Loop_(street)) - The public location page identifies Infinite Loop at Apple Campus in Cupertino, Santa Clara County, CA.
- `clearway_nj_dep_804_carnegie_20260603`: New Jersey Department of Environmental Protection 2017 news release archive (https://dep.nj.gov/newsrel/category/2017/) - NJ DEP describes NRG Energy's 804 Carnegie Center building in Princeton, Mercer County.
- `clearway_njparcels_804_carnegie_20260603`: NJParcels parcel record (https://vpc24.njparcels.com/property/1113/7.13/12.05) - NJParcels identifies 804 Carnegie Center as Block 7.13, Lot 12.05 in West Windsor Twp, Mercer County.

## Decision

- Accepted only rows whose reviewed current snapshot county FIPS is corroborated by external address/county evidence. This closes the remaining auto-reuse spot-check queue for report-only source review, but it does not make SEC source-mature.
- Next action: Rerun SEC review queues, source maturity, scale-up gate, source registry, Evidence Center, and deploy bundle. Keep SEC report-only while current-address snapshot semantics and parse-review backlog remain unresolved.

## Boundary

- This is a report-only operator-resolution artifact.
- It does not modify manual overrides, reviewed SEC vintages, county-year candidates, model features, scoring, ranks, Product Mode policy, source promotion, or feature eligibility.
