# 5yr Boundary Review Packet

## TLDR

- Status: `report_only_boundary_labels_ready_no_promotion`.
- Production model/rank/dashboard change: `False`.
- Decision: Keep the active 5yr default unchanged. Boundary counties now have report-only operator labels for policy review.
- Review rows: `87`.
- Labels: stable `28`, watch `34`, do-not-promote `25`.

## Boundary Label Counts

| Boundary | Label | Counties |
|---|---|---:|
| `top_100` | `do_not_promote_boundary` | 17 |
| `top_100` | `stable` | 7 |
| `top_100` | `watch` | 17 |
| `top_25` | `do_not_promote_boundary` | 2 |
| `top_25` | `stable` | 11 |
| `top_25` | `watch` | 8 |
| `top_50` | `do_not_promote_boundary` | 6 |
| `top_50` | `stable` | 10 |
| `top_50` | `watch` | 9 |

## Highest-Risk Review Rows

| Boundary | Label | County | Rank | Main Issue | Summary |
|---|---|---|---:|---|---|
| `top_50` | `do_not_promote_boundary` | Danville city, Virginia, VA | 57 | `interval_uncertainty` | rank #57 at top_50 (outside); interval 0.742; model gap 0.119; source confidence 68.3; run std 93.0; run range 312. |
| `top_50` | `do_not_promote_boundary` | Elk County, Kansas, KS | 54 | `interval_uncertainty` | rank #54 at top_50 (outside); interval 0.722; model gap 0.072; source confidence 64.3; run std 319.9; run range 1124. |
| `top_25` | `do_not_promote_boundary` | Windham County, Connecticut, CT | 33 | `source_confidence` | rank #33 at top_25 (outside); interval 0.628; model gap 0.045; source confidence 29.9; run std 57.9; run range 203. |
| `top_100` | `do_not_promote_boundary` | Tolland County, Connecticut, CT | 92 | `source_confidence` | rank #92 at top_100 (inside); interval 0.627; model gap 0.057; source confidence 29.9; run std 74.6; run range 271. |
| `top_100` | `do_not_promote_boundary` | Ogemaw County, Michigan, MI | 86 | `run_history_churn` | rank #86 at top_100 (inside); interval 0.643; model gap 0.097; source confidence 73.3; run std 29.9; run range 123. |
| `top_100` | `do_not_promote_boundary` | Lake County, Ohio, OH | 108 | `model_disagreement` | rank #108 at top_100 (outside); interval 0.600; model gap 0.118; source confidence 77.1; run std 18.7; run range 54. |
| `top_100` | `do_not_promote_boundary` | Cumberland County, North Carolina, NC | 107 | `run_history_churn` | rank #107 at top_100 (outside); interval 0.563; model gap 0.089; source confidence 77.1; run std 24.8; run range 103. |
| `top_100` | `do_not_promote_boundary` | Westmoreland County, Pennsylvania, PA | 96 | `model_disagreement` | rank #96 at top_100 (inside); interval 0.556; model gap 0.176; source confidence 77.1; run std 25.3; run range 96. |
| `top_100` | `do_not_promote_boundary` | Mercer County, West Virginia, WV | 82 | `interval_uncertainty` | rank #82 at top_100 (inside); interval 0.807; model gap 0.065; source confidence 72.0; run std 35.8; run range 95. |
| `top_100` | `do_not_promote_boundary` | Harrison County, Missouri, MO | 117 | `interval_uncertainty` | rank #117 at top_100 (outside); interval 0.752; model gap 0.059; source confidence 73.3; run std 56.0; run range 177. |
| `top_50` | `do_not_promote_boundary` | Allegany County, New York, NY | 39 | `interval_uncertainty` | rank #39 at top_50 (inside); interval 0.725; model gap 0.021; source confidence 73.3; run std 34.1; run range 119. |
| `top_50` | `do_not_promote_boundary` | Lunenburg County, Virginia, VA | 47 | `interval_uncertainty` | rank #47 at top_50 (inside); interval 0.713; model gap 0.090; source confidence 68.3; run std 33.1; run range 94. |
| `top_100` | `do_not_promote_boundary` | Edgecombe County, North Carolina, NC | 119 | `interval_uncertainty` | rank #119 at top_100 (outside); interval 0.700; model gap 0.005; source confidence 77.1; run std 72.4; run range 267. |
| `top_25` | `do_not_promote_boundary` | Florence County, Wisconsin, WI | 29 | `interval_uncertainty` | rank #29 at top_25 (outside); interval 0.686; model gap 0.006; source confidence 68.3; run std 31.4; run range 112. |
| `top_100` | `do_not_promote_boundary` | Alcona County, Michigan, MI | 100 | `interval_uncertainty` | rank #100 at top_100 (inside); interval 0.676; model gap 0.021; source confidence 77.1; run std 65.4; run range 230. |
| `top_100` | `do_not_promote_boundary` | Lake County, Michigan, MI | 113 | `interval_uncertainty` | rank #113 at top_100 (outside); interval 0.652; model gap 0.006; source confidence 73.3; run std 25.3; run range 82. |
| `top_50` | `do_not_promote_boundary` | Allen County, Kansas, KS | 60 | `interval_uncertainty` | rank #60 at top_50 (outside); interval 0.652; model gap 0.027; source confidence 77.1; run std 41.1; run range 148. |
| `top_100` | `do_not_promote_boundary` | Walker County, Alabama, AL | 99 | `run_history_churn` | rank #99 at top_100 (inside); interval 0.649; model gap 0.000; source confidence 77.1; run std 34.2; run range 141. |
| `top_100` | `do_not_promote_boundary` | Herkimer County, New York, NY | 116 | `interval_uncertainty` | rank #116 at top_100 (outside); interval 0.645; model gap 0.074; source confidence 73.3; run std 16.2; run range 67. |
| `top_100` | `do_not_promote_boundary` | Oscoda County, Michigan, MI | 89 | `run_history_churn` | rank #89 at top_100 (inside); interval 0.636; model gap 0.040; source confidence 73.3; run std 107.1; run range 374. |

## Boundary

- This packet is for operator review around top-rank cutoffs only.
- A `stable` label is not an automatic promotion; it only means the boundary row does not trigger the packet's uncertainty/source/churn blocks.
- No production model, scoring policy, rank artifact, source-promotion gate, or dashboard default changed.
