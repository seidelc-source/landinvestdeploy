# Pre-Boom Archetype Diversity Follow-Up

## TLDR

- Status: `report_only_diversity_followup_ready_no_promotion`.
- Production model/rank/dashboard change: `False`.
- Queue rows: `100`.
- Secondary-archetype backfill rows: `34`.
- Covered archetypes: `8`; gap archetypes: `2`.
- Decision: Use this as the more diverse pre-boom operator queue; do not promote the pre-boom surface by default.

## Balance Counts

| Balance Archetype | Rows |
|---|---:|
| amenity migration | 29 |
| affordability spillover | 10 |
| constrained-supply demand | 10 |
| manufacturing reshoring | 10 |
| recovery/rebound market | 10 |
| remote-work lifestyle market | 10 |
| college/medical institutional anchor | 10 |
| retirement migration | 10 |
| logistics/corporate anchor | 1 |

## Gap Queue

| Archetype | Selected | Target | Gap | Status | Action |
|---|---:|---:|---:|---|---|
| affordability spillover | 10 | 10 | 0 | `covered` | review_selected_secondary_backfills |
| amenity migration | 29 | 10 | 0 | `covered` | review_selected_secondary_backfills |
| college/medical institutional anchor | 10 | 10 | 0 | `covered` | review_selected_secondary_backfills |
| constrained-supply demand | 10 | 10 | 0 | `covered` | review_selected_secondary_backfills |
| energy/commodity boom | 0 | 10 | 10 | `source_or_classifier_gap` | acquire_or_engineer cleaner evidence for this archetype before forcing review slots |
| logistics/corporate anchor | 1 | 10 | 9 | `source_or_classifier_gap` | acquire_or_engineer cleaner evidence for this archetype before forcing review slots |
| manufacturing reshoring | 10 | 10 | 0 | `covered` | review_selected_secondary_backfills |
| recovery/rebound market | 10 | 10 | 0 | `covered` | review_selected_secondary_backfills |
| remote-work lifestyle market | 10 | 10 | 0 | `covered` | review_selected_secondary_backfills |
| retirement migration | 10 | 10 | 0 | `covered` | review_selected_secondary_backfills |

## Top Diverse Review Rows

| Rank | Lane | Balance Archetype | County | Prior Momentum | Thesis |
|---:|---|---|---|---:|---|
| 1 | `primary_archetype_slot` | affordability spillover | Upton County, Texas, TX | 1.8% | High quiet-breakout probability with low residual-upside magnitude. Prior momentum rank is 1.8%, inside the not-hot gate. Market-depth adequacy is low (0.155). |
| 2 | `primary_archetype_slot` | affordability spillover | Reeves County, Texas, TX | 0.1% | High quiet-breakout probability with low residual-upside magnitude. Prior momentum rank is 0.1%, inside the not-hot gate. Market-depth adequacy is moderate (0.469). |
| 3 | `primary_archetype_slot` | amenity migration | Clarion County, Pennsylvania, PA | 23.8% | High quiet-breakout probability with high residual-upside magnitude. Prior momentum rank is 23.8%, inside the not-hot gate. Market-depth adequacy is high (0.881). |
| 4 | `primary_archetype_slot` | amenity migration | Lawrence County, Ohio, OH | 38.1% | High quiet-breakout probability with high residual-upside magnitude. Prior momentum rank is 38.1%, inside the not-hot gate. Market-depth adequacy is high (0.957). |
| 5 | `primary_archetype_slot` | amenity migration | Clearfield County, Pennsylvania, PA | 4.1% | High quiet-breakout probability with high residual-upside magnitude. Prior momentum rank is 4.1%, inside the not-hot gate. Market-depth adequacy is high (0.830). |
| 6 | `primary_archetype_slot` | amenity migration | Venango County, Pennsylvania, PA | 46.0% | High quiet-breakout probability with high residual-upside magnitude. Prior momentum rank is 46.0%, inside the not-hot gate. Market-depth adequacy is high (0.985). |
| 7 | `primary_archetype_slot` | amenity migration | Elk County, Pennsylvania, PA | 27.4% | High quiet-breakout probability with high residual-upside magnitude. Prior momentum rank is 27.4%, inside the not-hot gate. Market-depth adequacy is high (0.855). |
| 8 | `primary_archetype_slot` | amenity migration | Northumberland County, Pennsylvania, PA | 24.3% | High quiet-breakout probability with high residual-upside magnitude. Prior momentum rank is 24.3%, inside the not-hot gate. Market-depth adequacy is high (0.813). |
| 9 | `primary_archetype_slot` | amenity migration | Fannin County, Georgia, GA | 19.6% | High quiet-breakout probability with high residual-upside magnitude. Prior momentum rank is 19.6%, inside the not-hot gate. Market-depth adequacy is high (0.865). |
| 10 | `primary_archetype_slot` | amenity migration | Wayne County, West Virginia, WV | 45.4% | High quiet-breakout probability with high residual-upside magnitude. Prior momentum rank is 45.4%, inside the not-hot gate. Market-depth adequacy is high (0.863). |
| 11 | `primary_archetype_slot` | amenity migration | Jefferson County, Pennsylvania, PA | 10.7% | High quiet-breakout probability with high residual-upside magnitude. Prior momentum rank is 10.7%, inside the not-hot gate. Market-depth adequacy is high (0.977). |
| 12 | `primary_archetype_slot` | amenity migration | Grant County, Wisconsin, WI | 55.2% | High quiet-breakout probability with high residual-upside magnitude. Prior momentum rank is 55.2%, inside the not-hot gate. Market-depth adequacy is high (0.978). |
| 13 | `primary_archetype_slot` | constrained-supply demand | San Miguel County, Colorado, CO | 35.2% | Moderate quiet-breakout probability with high residual-upside magnitude. Prior momentum rank is 35.2%, inside the not-hot gate. Market-depth adequacy is moderate (0.488). |
| 14 | `primary_archetype_slot` | constrained-supply demand | Grand County, Utah, UT | 24.0% | Moderate quiet-breakout probability with high residual-upside magnitude. Prior momentum rank is 24.0%, inside the not-hot gate. Market-depth adequacy is moderate (0.494). |
| 15 | `primary_archetype_slot` | constrained-supply demand | Chaffee County, Colorado, CO | 34.9% | Low quiet-breakout probability with moderate residual-upside magnitude. Prior momentum rank is 34.9%, inside the not-hot gate. Market-depth adequacy is high (0.788). |
| 16 | `primary_archetype_slot` | constrained-supply demand | Park County, Montana, MT | 23.2% | High quiet-breakout probability with low residual-upside magnitude. Prior momentum rank is 23.2%, inside the not-hot gate. Market-depth adequacy is moderate (0.693). |
| 17 | `primary_archetype_slot` | constrained-supply demand | Ward County, Texas, TX | 0.5% | High quiet-breakout probability with low residual-upside magnitude. Prior momentum rank is 0.5%, inside the not-hot gate. Market-depth adequacy is moderate (0.456). |
| 18 | `primary_archetype_slot` | manufacturing reshoring | Baltimore city, Maryland, MD | 29.3% | High quiet-breakout probability with high residual-upside magnitude. Prior momentum rank is 29.3%, inside the not-hot gate. Market-depth adequacy is moderate (0.522). |
| 19 | `primary_archetype_slot` | manufacturing reshoring | Bronx County, New York, NY | 3.2% | High quiet-breakout probability with high residual-upside magnitude. Prior momentum rank is 3.2%, inside the not-hot gate. Market-depth adequacy is moderate (0.523). |
| 20 | `primary_archetype_slot` | manufacturing reshoring | Philadelphia County, Pennsylvania, PA | 27.0% | High quiet-breakout probability with high residual-upside magnitude. Prior momentum rank is 27.0%, inside the not-hot gate. Market-depth adequacy is moderate (0.476). |

## Boundary

- This is an operator review queue, not a model input or ranking replacement.
- Secondary-archetype rows make the review set more varied without changing production scores.
- No production model, scoring policy, rank artifact, source-promotion gate, or dashboard default changed.
