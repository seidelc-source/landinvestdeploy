# Controlled X-Factor Ablation Sprint

## TLDR

- Status: `controlled_report_only_ablation_sprint_complete`.
- Production model/rank/dashboard change: `False`.
- Default promotion recommendation: `do_not_promote_current_xfactor_surfaces`.
- Next action: Keep as contextual evidence; investigate capped overlay instead of raw feature promotion.

## Controlled Reads

| Surface | Family | Gate | Decision | AP Delta | NDCG@25 Delta | Top-100 Churn | Action |
|---|---|---|---|---:|---:|---:|---|
| `migration_affordability` | frontier_interaction | `top_frontier_interaction_ablation` | `mixed_no_promotion` | 0.007 | -0.004 | 16.9% | Keep report-only unless a capped overlay gate beats churn/false-positive controls. |
| `anchor_halo_optionality` | frontier_interaction | `top_frontier_interaction_ablation` | `reject_default_feature` | 0.001 | -0.008 | 16.9% | Keep report-only unless a capped overlay gate beats churn/false-positive controls. |
| `anchor_halo_affordability` | frontier_interaction | `top_frontier_interaction_ablation` | `reject_default_feature` | -0.002 | -0.002 | 19.2% | Keep report-only unless a capped overlay gate beats churn/false-positive controls. |
| `amenity_value` | frontier_interaction | `top_frontier_interaction_ablation` | `mixed_no_promotion` | 0.006 | -0.012 | 16.3% | Keep report-only unless a capped overlay gate beats churn/false-positive controls. |
| `scarcity_buildability` | frontier_interaction | `top_frontier_interaction_ablation` | `reject_default_feature` | -0.000 | -0.007 | 16.0% | Keep report-only unless a capped overlay gate beats churn/false-positive controls. |
| `population_supply_tightness` | preboom_interaction | `preboom_interaction_model_ablation` | `mixed_no_promotion` | 0.003 | -0.007 | 15.9% | Keep out of default features; use only as narrative context where component evidence is strong. |
| `ssurgo_scarcity` | preboom_interaction | `preboom_interaction_model_ablation` | `mixed_no_promotion` | 0.006 | -0.003 | 16.8% | Keep out of default features; use only as narrative context where component evidence is strong. |
| `jobs_affordability` | preboom_interaction | `preboom_interaction_model_ablation` | `reject_default_feature` | -0.002 | -0.004 | 15.8% | Keep out of default features; use only as narrative context where component evidence is strong. |
| `p0_repeatable_treatment` | repeatable_treatment | `p0_repeatable_treatment_model_ablation` | `repeatable_treatment_not_model_ready` | n/a | n/a | n/a | Use P0 treatment diagnostics only after source-policy and model-health review. |
| `announcement_anchor_events` | corporate_anchor_event | `announcement_anchor_event_model_impact_gate` | `announcement_anchor_event_model_impact_report_only_complete` | n/a | n/a | n/a | Keep in opt-in evidence/memo context; do not add default rank influence. |
| `institutional_anchor_official_panel` | institutional_anchor | `source_maturity_before_model_ablation` | `model_ablation_not_started_source_gate_open` | n/a | n/a | n/a | Run model-impact ablation only after provider geocode/leakage gates clear. |

## Metrics

- `surfaces_reviewed`: `11`
- `default_promotion_candidates`: `0`
- `no_default_promotion_rows`: `11`
- `command_loop_rows_loaded`: `38`

## Boundary

- This sprint summarizes report-only controlled gates.
- It does not retrain production models, change feature engineering defaults, scoring, rank artifacts, dashboard defaults, source promotion, or Product Mode rank policy.
