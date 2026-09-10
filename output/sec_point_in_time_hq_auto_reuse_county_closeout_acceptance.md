# SEC Auto-Reuse County Closeout Acceptance

## TLDR

- Status: `strict_census_county_closeout_accepted_report_only`.
- Production model/rank/dashboard change: `False`.
- Input rows: `25`.
- Strict Census candidates: `15`.
- Accepted strict Census rows: `15`.
- Held operator-review rows: `10`.
- Rejected strict candidates: `0`.

## Acceptance Status Counts

- `accepted_strict_census_same_county`: `15`
- `held_local_same_zip_candidate`: `2`
- `held_snapshot_only_support`: `8`

## Accepted Preview

| Entity | Filing Date | Filing Street | County | Census Match |
|---|---|---|---|---|
| DELTA AIR LINES, INC. | 2026-04-08 | 5424 DELTA AIR LINES, INC. Delaware 58-0218548 1030 Delta Boulevard | Fulton County, Georgia | 1030 DELTA BLVD, ATLANTA, GA, 30354 |
| Duke Energy CORP | 2019-02-28 | 550 South Tryon Street | Mecklenburg County, North Carolina | 550 S TRYON ST, CHARLOTTE, NC, 28202 |
| AIR INDUSTRIES GROUP | 2008-04-14 | 1479 North Clinton Avenue | Suffolk County, New York | 1479 N CLINTON AVE, BAY SHORE, NY, 11706 |
| AIR INDUSTRIES GROUP | 2008-04-17 | 1479 North Clinton Avenue | Suffolk County, New York | 1479 N CLINTON AVE, BAY SHORE, NY, 11706 |
| TRACTOR SUPPLY CO /DE/ | 2013-05-06 | 200 Powell Place | Williamson County, Tennessee | 200 POWELL PL, BRENTWOOD, TN, 37027 |
| TRACTOR SUPPLY CO /DE/ | 2014-02-19 | 200 Powell Place | Williamson County, Tennessee | 200 POWELL PL, BRENTWOOD, TN, 37027 |
| FedEx Freight Holding Company, Inc. | 2026-05-13 | 43059 Delaware 39-3560171 8285 Tournament Drive | Shelby County, Tennessee | 8285 TOURNAMENT DR, MEMPHIS, TN, 38125 |
| FedEx Freight Holding Company, Inc. | 2026-05-18 | 43059 Delaware 39-3560171 8285 Tournament Drive | Shelby County, Tennessee | 8285 TOURNAMENT DR, MEMPHIS, TN, 38125 |
| Cheniere Energy Partners, L.P. | 2007-05-09 | 700 Milam Street, Suite 800 | Harris County, Texas | 700 MILAM ST, HOUSTON, TX, 77002 |
| Cheniere Energy Partners, L.P. | 2008-02-27 | 700 Milam Street, Suite 800 | Harris County, Texas | 700 MILAM ST, HOUSTON, TX, 77002 |
| Cheniere Energy, Inc. | 2015-04-30 | 700 Milam Street, Suite 1900 | Harris County, Texas | 700 MILAM ST, HOUSTON, TX, 77002 |
| Cheniere Energy, Inc. | 2016-02-19 | 700 Milam Street, Suite 1900 | Harris County, Texas | 700 MILAM ST, HOUSTON, TX, 77002 |
| GENESIS ENERGY LP | 2012-05-04 | 919 Milam, Suite 2100 | Harris County, Texas | 919 MILAM ST, HOUSTON, TX, 77002 |
| GENESIS ENERGY LP | 2013-02-26 | 919 Milam, Suite 2100 | Harris County, Texas | 919 MILAM ST, HOUSTON, TX, 77002 |
| DOMINION ENERGY, INC | 2018-02-27 | 37591 DOMINION ENERGY GAS HOLDINGS, LLC 46-3639580 VIRGINIA 120 TREDEGAR STREET | Richmond city, Virginia | 120 TREDEGAR ST, RICHMOND, VA, 23219 |

## Decision

- Accepted only strict Census same-county auto-reuse closeout rows. Local same-ZIP candidates, snapshot-only support rows, and Census/snapshot conflicts remain held for operator review.
- Next action: Rerun SEC review queues, source maturity, scale-up gate, source registry, Evidence Center, and deploy bundle. Keep SEC report-only while current-address snapshot semantics and held rows remain open.

## Boundary

- This is a report-only operator acceptance artifact.
- It does not modify manual overrides, reviewed SEC vintages, county-year candidates, model features, scoring, ranks, Product Mode policy, source promotion, or feature eligibility.
