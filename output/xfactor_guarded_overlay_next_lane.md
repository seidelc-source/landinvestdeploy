# X-Factor Guarded Overlay Next Lane

## TLDR

- Decision: `pass_guardrails`
- Top-25 churn: `4.0%`
- Top-100 churn: `3.0%`
- Mean absolute rank shift: `24.58`
- P95 absolute rank shift: `64.00`
- This is a report-only post-model overlay prototype. It does not change production ranks.

## Guardrail Read

- Overlay passes rank-impact guardrails at the tested cap.

## Recommendation

- Keep current interaction features out of default model training.
- If this overlay passes guardrails, review top movers manually before any Product Mode use.
- If this overlay fails guardrails, lower the cap or keep the concepts as narrative-only memo context.

## Outputs

- CSV: `/Users/coryseidel/PersonalProjects/IdeaTests/LandInvest/output/xfactor_guarded_overlay_next_lane.csv`
- Top movers CSV: `/Users/coryseidel/PersonalProjects/IdeaTests/LandInvest/output/xfactor_guarded_overlay_top_movers.csv`
- JSON: `/Users/coryseidel/PersonalProjects/IdeaTests/LandInvest/output/xfactor_guarded_overlay_next_lane.json`
- Markdown: `/Users/coryseidel/PersonalProjects/IdeaTests/LandInvest/output/xfactor_guarded_overlay_next_lane.md`
