# X-Factor Command Loop

## TLDR

- Status: `report_only_command_loop_ready`.
- Production model/rank/dashboard change: `False`.
- Surfaces ranked: `39`.
- Opt-in evidence-panel ready: `1`.
- Memo/context only: `3`.

## Top Priorities

| Rank | Surface | Family | Score | Readiness | Analog/Capture | False Positive | Churn | Action |
|---:|---|---|---:|---|---:|---:|---:|---|
| 1 | Guarded pre-boom two-score blend | preboom_shortlist | 93.1 | opt_in_evidence_panel_ready | 7.28 | 7.0% | n/a | Show in opt-in evidence panel with report-only label. |
| 2 | Land optionality breakout V1 | analog_label | 71.2 | operator_review_before_display | 1.00 | 61.4% | n/a | Review false-positive/already-hot behavior before display expansion. |
| 3 | Quiet breakout label V1 | analog_label | 59.8 | operator_review_before_display | 0.70 | 61.4% | n/a | Review false-positive/already-hot behavior before display expansion. |
| 4 | Anchor/halo support x land optionality | xfactor_interaction | 59.1 | report_only_memo_context | 0.56 | 30.6% | 16.9% | Keep as memo/context evidence; do not promote into default rank. |
| 5 | Sector depth x low prior momentum | xfactor_interaction | 54.4 | research_queue | 0.20 | 0.0% | n/a | Keep in research queue and gather cleaner evidence. |
| 6 | Anchor/halo support x buildability | xfactor_interaction | 53.8 | research_queue | 0.34 | 26.9% | n/a | Keep in research queue and gather cleaner evidence. |
| 7 | Logistics/trade depth x low prior momentum | xfactor_interaction | 51.5 | research_queue | 0.13 | 0.0% | n/a | Keep in research queue and gather cleaner evidence. |
| 8 | Peer price spillover x state-relative value | xfactor_interaction | 47.4 | research_queue | 0.10 | 14.4% | n/a | Keep in research queue and gather cleaner evidence. |
| 9 | Scarcity x buildability | xfactor_interaction | 47.1 | report_only_memo_context | 0.24 | 31.4% | 16.0% | Keep as memo/context evidence; do not promote into default rank. |
| 10 | Anchor/halo support x affordability | xfactor_interaction | 45.4 | research_queue | 0.07 | 18.9% | n/a | Keep in research queue and gather cleaner evidence. |
| 11 | Anchor/halo support x supply tightness | xfactor_interaction | 44.1 | research_queue | 0.06 | 22.1% | n/a | Keep in research queue and gather cleaner evidence. |
| 12 | Recreation access x affordability | xfactor_interaction | 44.0 | research_queue | 0.03 | 17.0% | n/a | Keep in research queue and gather cleaner evidence. |
| 13 | Income growth x value | xfactor_interaction | 43.9 | research_queue | 0.03 | 18.6% | n/a | Keep in research queue and gather cleaner evidence. |
| 14 | Migration pressure x affordability | xfactor_interaction | 43.7 | research_queue | 0.07 | 25.0% | n/a | Keep in research queue and gather cleaner evidence. |
| 15 | Sector depth x affordability | xfactor_interaction | 42.1 | research_queue | 0.00 | 21.1% | n/a | Keep in research queue and gather cleaner evidence. |
| 16 | Job growth x affordability | xfactor_interaction | 42.0 | research_queue | 0.04 | 28.1% | n/a | Keep in research queue and gather cleaner evidence. |
| 17 | Boom-onset LOFO research classifier | boom_onset_research | 41.8 | research_queue | 0.16 | n/a | n/a | Keep in research queue and gather cleaner evidence. |
| 18 | Guarded X-factor overlay | post_model_overlay | 40.6 | research_queue | n/a | n/a | 3.0% | Keep in research queue and gather cleaner evidence. |
| 19 | Buildability x scarcity | analog_interaction | 39.9 | operator_review_before_display | 0.18 | 61.4% | n/a | Review false-positive/already-hot behavior before display expansion. |
| 20 | Future growth rank oracle | analog_oracle | 39.8 | operator_review_before_display | 0.17 | 61.4% | n/a | Review false-positive/already-hot behavior before display expansion. |

## Readiness Counts

- `operator_review_before_display`: `18`
- `research_queue`: `17`
- `report_only_memo_context`: `3`
- `opt_in_evidence_panel_ready`: `1`

## Boundary

- This table is an operating loop for reports, county memos, and source work.
- It does not alter production model features, scoring, rank artifacts, source promotion, or dashboard defaults.
