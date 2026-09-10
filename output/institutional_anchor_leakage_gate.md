# Institutional Anchor Leakage Gate

## TLDR

- Status: `training_blocked_insufficient_historical_observed_years`.
- Production model/rank/dashboard change: `False`.
- Decision: Keep institutional anchors out of default model training. Current official panel has clean report-only observed-year semantics but insufficient historical depth for leakage-safe training.
- Next action: Resolve provider geocode/source maturity first; for modeling, build a historical multi-year institutional panel before any controlled training gate.

## Gate Checks

| Check | Pass |
|---|---:|
| `institutional_columns_absent_from_default_features` | `True` |
| `observed_years_not_backfilled_for_training` | `True` |
| `sufficient_historical_depth_for_training` | `False` |
| `source_maturity_gate_required_before_training` | `True` |

## Metrics

| Metric | Value |
|---|---:|
| `panel_rows` | 3483 |
| `panel_year_min` | 2022 |
| `panel_year_max` | 2024 |
| `panel_year_count` | 3 |
| `features_rows_loaded` | 82755 |
| `feature_year_min` | 2000 |
| `feature_year_max` | 2024 |
| `institutional_feature_column_count` | 0 |

## Feature Columns

- No institutional/IPEDS/CMS/HCRIS columns were found in the default feature panel.

## Boundary

- This gate is report-only.
- It does not alter feature engineering, model artifacts, scoring, ranks, source promotion, Product Mode policy, or feature eligibility.
