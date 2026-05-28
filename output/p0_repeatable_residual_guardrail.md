# P0 Repeatable Residual Guardrail

Generated: `2026-05-25T17:38:44.839433+00:00`

## TLDR

- Status: `report_only_residual_review_guardrail_candidate`.
- Default model or rank change: `False`.
- Best policy: `keep90_src500_t60_b75_p75`.
- Top-100 P0 capture: baseline `2` -> best `8`.
- NDCG@25 delta: `0.000`; NDCG@100 delta: `0.002`.
- Guarded top-100 churn: `26.7%`; severe-QA share: `0.0%`.
- Recommendation: Use the best policy as a report-only residual review queue candidate. It preserves residual top-of-list quality while recovering the P0 analog capture lift; do not wire it into default ranks.

## Boundary

- This is a report-only residual review queue experiment.
- It preserves the top of the base structural-plus investable residual surface and only lets repeatable P0 evidence compete for lower top-100 slots.
- It does not use curated anchor/halo evidence, current freight/CBP diagnostics, or retrained model scores.

## Baseline Vs Best

| Policy | Top-100 Capture | Top-250 Capture | NDCG@25 | dNDCG@25 | NDCG@100 | dNDCG@100 | Strict Lift@25 | dStrict Lift@25 | Guarded Top-100 Churn | Severe QA |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline_structural_plus_investable_residual | 2 | 5 | 0.595 | 0.000 | 0.553 | 0.000 | 6.409 | 0.000 | 0.0% | 0.0% |
| keep90_src500_t60_b75_p75 | 8 | 8 | 0.595 | 0.000 | 0.556 | 0.002 | 6.409 | 0.000 | 26.7% | 0.0% |

## Top Sweep Policies By Objective

| Rank | Policy | Keep Top | Source Rank Max | Treatment Min | Base Weight | Prior Max | Top-100 Capture | dNDCG@25 | dNDCG@100 | Churn | Objective |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `keep50_src1500_t60_b60_p75` | 50 | 1500 | 0.600 | 0.600 | 0.750 | 8 | 0.000 | -0.037 | 57.3% | 32.004 |
| 2 | `keep90_src1000_t55_b75_p75` | 90 | 1000 | 0.550 | 0.750 | 0.750 | 8 | 0.000 | 0.002 | 33.7% | 32.000 |
| 3 | `keep90_src1500_t55_b75_p75` | 90 | 1500 | 0.550 | 0.750 | 0.750 | 8 | 0.000 | 0.002 | 34.0% | 32.000 |
| 4 | `keep50_src1500_t60_b75_p75` | 50 | 1500 | 0.600 | 0.750 | 0.750 | 8 | 0.000 | -0.038 | 57.3% | 31.984 |
| 5 | `keep50_src1500_t60_b45_p75` | 50 | 1500 | 0.600 | 0.450 | 0.750 | 8 | 0.000 | -0.048 | 57.9% | 31.826 |
| 6 | `keep75_src1000_t55_b75_p75` | 75 | 1000 | 0.550 | 0.750 | 0.750 | 8 | 0.000 | -0.007 | 39.7% | 31.797 |
| 7 | `keep75_src1500_t55_b75_p75` | 75 | 1500 | 0.550 | 0.750 | 0.750 | 8 | 0.000 | -0.007 | 40.1% | 31.788 |
| 8 | `keep50_src1000_t50_b75_p75` | 50 | 1000 | 0.500 | 0.750 | 0.750 | 8 | 0.000 | -0.023 | 46.0% | 31.441 |
| 9 | `keep50_src1500_t50_b75_p75` | 50 | 1500 | 0.500 | 0.750 | 0.750 | 8 | 0.000 | -0.023 | 46.0% | 31.441 |
| 10 | `keep50_src1000_t55_b75_p75` | 50 | 1000 | 0.550 | 0.750 | 0.750 | 8 | 0.000 | -0.024 | 50.3% | 31.336 |
| 11 | `keep50_src1500_t55_b75_p75` | 50 | 1500 | 0.550 | 0.750 | 0.750 | 8 | 0.000 | -0.024 | 51.0% | 31.322 |
| 12 | `keep25_src1500_t60_b75_p75` | 25 | 1500 | 0.600 | 0.750 | 0.750 | 8 | 0.000 | -0.077 | 66.6% | 31.213 |

## Decision Boundary

- A usable review guardrail should recover at least the prior `6 / 18` top-100 residual P0 capture, keep NDCG@25 within `-0.005`, keep NDCG@100 within `-0.015`, and avoid severe-QA drift.
- Passing this gate still means Product Mode/report-only review queue, not default ranking or model promotion.

## Files

- Summary CSV: `/Users/coryseidel/Desktop/IdeaTests/LandInvest/output/p0_repeatable_residual_guardrail_sweep.csv`
- P0 capture detail CSV: `/Users/coryseidel/Desktop/IdeaTests/LandInvest/output/p0_repeatable_residual_guardrail_p0_capture_detail.csv`
- Top candidates CSV: `/Users/coryseidel/Desktop/IdeaTests/LandInvest/output/p0_repeatable_residual_guardrail_top_candidates.csv`
- JSON: `/Users/coryseidel/Desktop/IdeaTests/LandInvest/output/p0_repeatable_residual_guardrail.json`
- Markdown: `/Users/coryseidel/Desktop/IdeaTests/LandInvest/output/p0_repeatable_residual_guardrail.md`
