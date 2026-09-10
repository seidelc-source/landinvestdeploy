# 5yr Rank-Band Promotion Gate

## TLDR

- Status: `report_only_rank_band_gate_built_no_promotion`.
- Production model/rank/dashboard change: `False`.
- Decision: Keep active 5yr default unchanged. Use rank-band gates only as report-only operator review policy.

## Rank-Band Reads

| Band | Gate | Inside Rows | Stable | Watch | Do Not Promote | Stable Share | Dominant Issue | Action |
|---|---|---:|---:|---:|---:|---:|---|---|
| `top_25` | `operator_acceptance_only_watch_rows_open` | 11 | 7 | 4 | 0 | 63.6% | interval_uncertainty | Use as operator-review context only; watch rows need source/model review before any policy change. |
| `top_50` | `blocked_do_not_promote_inside_band` | 13 | 5 | 6 | 2 | 38.5% | interval_uncertainty | Do not use this rank band for promotion policy; reconcile do-not-promote boundary rows first. |
| `top_100` | `blocked_do_not_promote_inside_band` | 21 | 6 | 7 | 8 | 28.6% | interval_uncertainty | Do not use this rank band for promotion policy; reconcile do-not-promote boundary rows first. |

## Highest-Risk Inside-Band Examples

- `top_25`: #19 Lucas County, Ohio (watch); #22 Cambria County, Pennsylvania (watch); #23 Douglas County, Illinois (watch); #25 Williamson County, Illinois (watch); #18 Schuylkill County, Pennsylvania (stable)
- `top_50`: #39 Allegany County, New York (do_not_promote_boundary); #47 Lunenburg County, Virginia (do_not_promote_boundary); #43 Wood County, Wisconsin (watch); #50 Northumberland County, Pennsylvania (watch); #40 Wise County, Virginia (watch)
- `top_100`: #92 Tolland County, Connecticut (do_not_promote_boundary); #96 Westmoreland County, Pennsylvania (do_not_promote_boundary); #86 Ogemaw County, Michigan (do_not_promote_boundary); #82 Mercer County, West Virginia (do_not_promote_boundary); #88 Parke County, Indiana (do_not_promote_boundary)

## Boundary

- This gate is report-only and operator-facing.
- It does not alter active 5yr weights, score shaping, rank artifacts, model artifacts, dashboard defaults, or Product Mode rank policy.
