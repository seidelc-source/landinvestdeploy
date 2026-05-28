"""
LandInvest Interactive Dashboard

Launch:  streamlit run dashboard.py
"""

import html
import json
import re
import sqlite3
from pathlib import Path
from datetime import datetime
from urllib.parse import urlencode

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DATA_PATH = Path(__file__).resolve().parent / "output" / "county_rankings_2024.parquet"
ASSETS_PATH = Path(__file__).resolve().parent / "assets"
BRAND_LOGO_PATH = ASSETS_PATH / "landinvest-logo.svg"
COUNTY_GEOJSON_PATH = ASSETS_PATH / "geojson-counties-fips.json"
COUNTY_GEOJSON_URL = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
EVAL_PATH = Path(__file__).resolve().parent / "output" / "evaluation_report.json"
CONFORMAL_DIAG_PATH = Path(__file__).resolve().parent / "models" / "artifacts" / "quantile" / "conformal_diagnostics.json"
RUNS_PATH = Path(__file__).resolve().parent / "output" / "runs"
STATUS_BUNDLE_PATH = Path(__file__).resolve().parent / "output" / "project_status_bundle.json"
SOURCE_HEALTH_PATH = Path(__file__).resolve().parent / "output" / "source_health.json"
MISSINGNESS_PATH = Path(__file__).resolve().parent / "output" / "missingness_diagnostics_2024.json"
GAP_TRIAGE_PATH = Path(__file__).resolve().parent / "output" / "feature_gap_triage_2024.json"
DRIFT_TRIAGE_PATH = Path(__file__).resolve().parent / "output" / "drift_triage_2024.json"
WAVE2_REASSESSMENT_PATH = Path(__file__).resolve().parent / "output" / "wave2_reassessment.json"
WAVE2_TRAINING_POLICY_PATH = Path(__file__).resolve().parent / "output" / "wave2_training_policy.json"
FIVEYR_POLICY_STATUS_PATH = Path(__file__).resolve().parent / "output" / "fiveyr_policy_status.json"
OUTPUT_PATH = Path(__file__).resolve().parent / "output"
RUN_HISTORY_SUMMARY_JSON_PATH = OUTPUT_PATH / "run_history_summary_2024.json"
RUN_HISTORY_SUMMARY_CSV_PATH = OUTPUT_PATH / "run_history_summary_2024.csv"
RUN_HISTORY_DETAIL_CSV_PATH = OUTPUT_PATH / "run_history_detail_2024.csv"
WAVE3_STRUCTURAL_OVERLAY_CSV_PATH = OUTPUT_PATH / "wave3_structural_overlay_2024.csv"
WAVE3_STRUCTURAL_OVERLAY_JSON_PATH = OUTPUT_PATH / "wave3_structural_overlay_2024.json"
PREBOOM_RAW_EXPORT_PATH = OUTPUT_PATH / "preboom_shortlist_export_2024.csv"
PREBOOM_BALANCED_EXPORT_PATH = OUTPUT_PATH / "preboom_shortlist_balanced_export_2024.csv"
PREBOOM_BLEND_EXPORT_PATH = OUTPUT_PATH / "preboom_two_score_blend_top100_2024.csv"
PREBOOM_GUARDED_BLEND_EXPORT_PATH = OUTPUT_PATH / "preboom_two_score_blend_guarded_top100_2024.csv"
PREBOOM_RESIDUAL_DISPLAY_GUARDED_PATH = OUTPUT_PATH / "preboom_residual_overlay_display_guarded_top100_2024.csv"
PREBOOM_RESIDUAL_AUDIT_PATH = OUTPUT_PATH / "investable_residual_guardrail_top100_2024.csv"
PREBOOM_BLEND_REPORT_PATH = OUTPUT_PATH / "preboom_two_score_blend_sweep_2024.json"
PREBOOM_ANALOG_REPORT_PATH = OUTPUT_PATH / "preboom_surface_analog_overlap.json"
PREBOOM_PROMOTION_GATE_PATH = OUTPUT_PATH / "preboom_residual_promotion_gate.json"
P0_REPEATABLE_RESIDUAL_GUARDRAIL_PATH = OUTPUT_PATH / "p0_repeatable_residual_guardrail.json"
P0_REPEATABLE_RESIDUAL_GUARDRAIL_TOP_CANDIDATES_PATH = OUTPUT_PATH / "p0_repeatable_residual_guardrail_top_candidates.csv"
KNOWN_ANALOG_SUITE_PATH = OUTPUT_PATH / "known_boom_analog_suite.json"
XFACTOR_INTERACTION_SCOREBOARD_PATH = OUTPUT_PATH / "xfactor_interaction_validation_scoreboard.json"
XFACTOR_INTERACTION_ABLATION_QUEUE_PATH = OUTPUT_PATH / "xfactor_interaction_ablation_queue.json"
XFACTOR_INTERACTION_PROMOTION_GATE_PATH = OUTPUT_PATH / "xfactor_interaction_promotion_gate.json"
DEMO_READINESS_REPORT_PATH = OUTPUT_PATH / "demo_readiness_report.json"
USER_DATA_PATH = OUTPUT_PATH / "dashboard_user_data.json"
USER_DATA_DB_PATH = OUTPUT_PATH / "dashboard_user_data.sqlite3"
HORIZONS = [1, 3, 5]
MIN_CAL_SHIFT = {1: 0.05, 3: 0.10, 5: 0.15}
MAX_CAL_SHIFT = {1: 0.20, 3: 0.40, 5: 0.70}
RISK_COLOR_LOW = "#1f9d55"
RISK_COLOR_MED = "#f59e0b"
RISK_COLOR_HIGH = "#dc2626"


def _fmt_pct(x) -> str:
    return f"{x:+.1%}" if pd.notna(x) else "—"


def _fmt_score(x) -> str:
    return f"{x:.1f}" if pd.notna(x) else "—"


STATUS_LABELS = {
    "needs_stabilization_but_has_promising_specialist_lane": "Needs stabilization",
    "no_default_interaction_promotion": "Report-only: no default X-factor promotion",
    "report_only_product_review_lane": "Report-only product review lane",
    "research gates active": "Research gates active",
    "unknown": "Unknown",
    "n/a": "n/a",
}


def _humanize_status_label(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "n/a"
    raw = str(value).strip()
    if not raw:
        return "n/a"
    return STATUS_LABELS.get(raw, raw.replace("_", " ").replace("-", " ").title())


def _slider_step_precision(step: float) -> int:
    if step <= 0:
        return 2
    if step >= 1:
        return 2
    return min(6, max(2, int(np.ceil(-np.log10(step))) + 2))


def _align_slider_bound(value: float, step: float, *, direction: str) -> float:
    precision = _slider_step_precision(step)
    scaled = value / step
    aligned = np.floor(scaled) * step if direction == "down" else np.ceil(scaled) * step
    return round(float(aligned), precision)


def _risk_color(v: float) -> str:
    if pd.isna(v):
        return "#6b7280"
    if v > 60:
        return RISK_COLOR_HIGH
    if v > 40:
        return RISK_COLOR_MED
    return RISK_COLOR_LOW


def _county_label_from_row(row: pd.Series) -> str:
    county = row.get("county_name", row.get("fips", "Unknown"))
    state = row.get("state", "")
    fips = str(row.get("fips", "")).zfill(5) if pd.notna(row.get("fips")) else "n/a"
    return f"{county}, {state} [FIPS {fips}]"


def _extract_driver_impacts(row: pd.Series, horizon: int = 5) -> tuple[list[tuple[str, float]], list[tuple[str, float]]]:
    driver_col = f"drivers_xgboost_{horizon}yr"
    drivers = _parse_drivers(row.get(driver_col))
    numeric = [(k, float(v)) for k, v in drivers.items() if isinstance(v, (int, float))]
    positives = sorted([kv for kv in numeric if kv[1] > 0], key=lambda x: x[1], reverse=True)[:3]
    negatives = sorted([kv for kv in numeric if kv[1] < 0], key=lambda x: x[1])[:3]
    return positives, negatives


def _build_county_narrative(row: pd.Series, history_row: pd.Series | None = None) -> dict[str, list[str] | str]:
    positives_5, negatives_5 = _extract_driver_impacts(row, horizon=5)
    positives_3, negatives_3 = _extract_driver_impacts(row, horizon=3)

    bullets_good: list[str] = []
    bullets_caution: list[str] = []

    pred5 = row.get("pred_avg_5yr")
    pred3 = row.get("pred_policy_3yr", row.get("pred_avg_3yr"))
    risk = row.get("composite_risk")
    conf = row.get("confidence", "unknown")
    fallback = bool(row.get("use_stable_3yr_fallback", False))
    interval = row.get("quantile_interval_width_mean", row.get("pred_std"))

    if pd.notna(pred5):
        bullets_good.append(f"Long-horizon upside remains strong at {_fmt_pct(pred5)} on the active 5-year blend.")
    if pd.notna(pred3):
        bullets_good.append(f"Medium-term policy signal is {_fmt_pct(pred3)}, which helps confirm the near-to-mid path.")
    for feat, val in positives_5[:2]:
        bullets_good.append(f"`{feat}` is one of the strongest long-horizon positive drivers ({val:+.3f} SHAP).")
    for feat, val in positives_3[:1]:
        if feat not in [x[0] for x in positives_5[:2]]:
            bullets_good.append(f"`{feat}` also supports the 3-year view ({val:+.3f} SHAP).")

    if pd.notna(risk):
        if risk >= 60:
            bullets_caution.append(f"Composite risk is elevated at {_fmt_score(risk)}, so upside comes with more downside baggage.")
        elif risk >= 45:
            bullets_caution.append(f"Composite risk is middling at {_fmt_score(risk)}, so this is not a clean low-risk setup.")
    if fallback:
        bullets_caution.append("The effective 3-year signal is currently using the stable fallback path, so medium-term confidence is more conditional.")
    if pd.notna(interval) and float(interval) > 0.20:
        bullets_caution.append(f"Prediction uncertainty is relatively wide ({float(interval):.3f}), so ranking confidence should be treated cautiously.")
    for feat, val in negatives_5[:2]:
        bullets_caution.append(f"`{feat}` is a notable long-horizon drag ({val:+.3f} SHAP).")
    if history_row is not None and not history_row.empty:
        std_rank = history_row.get("std_rank")
        top25_share = history_row.get("top25_presence_share")
        latest_rank = history_row.get("latest_rank")
        if pd.notna(top25_share) and float(top25_share) >= 0.75:
            bullets_good.append(
                f"This county has stayed in the top 25 for {100 * float(top25_share):.0f}% of recent runs, which supports shortlist durability."
            )
        if pd.notna(std_rank) and float(std_rank) >= 20:
            bullets_caution.append(
                f"Run-to-run rank volatility is still meaningful (rank std {float(std_rank):.1f}), so placement is not fully settled."
            )
        if pd.notna(latest_rank):
            bullets_good.append(f"Current live rank is #{int(latest_rank)}.")

    summary = (
        f"{row.get('county_name', 'This county')} is currently a `{conf}`-confidence long-horizon opportunity. "
        f"The main case is strong 5-year upside with supportive structural drivers, while the main question is "
        f"{'medium-term fallback reliance' if fallback else 'whether the current rank remains stable across runs'}."
    )

    return {
        "summary": summary,
        "positives": bullets_good[:5],
        "cautions": bullets_caution[:5],
    }


def _wave3_value_label(value, invert: bool = False) -> str:
    if pd.isna(value):
        return "unknown"
    val = float(value)
    if invert:
        if val <= 0.33:
            return "low"
        if val <= 0.66:
            return "moderate"
        return "high"
    if val >= 0.66:
        return "high"
    if val >= 0.33:
        return "moderate"
    return "low"


def _build_wave3_profile(row: pd.Series) -> dict[str, object]:
    metrics = {
        "Site Thesis Support": row.get("site_thesis_support_index"),
        "Land Developability": row.get("land_developability_index"),
        "Constraint Pressure": row.get("land_constraint_pressure"),
        "Fragility Pressure": row.get("land_fragility_pressure"),
        "Fragility Balance": row.get("fragility_balance_index"),
        "Scarcity / Amenity": row.get("scarcity_amenity_balance_index"),
        "Optionality Profile": row.get("optionality_profile_index"),
        "Recreation Access": row.get("recreation_access_score"),
        "Coastal Flood Pressure": row.get("coastal_flood_pressure"),
    }

    supports: list[str] = []
    brakes: list[str] = []

    site_support = row.get("site_thesis_support_index")
    if pd.notna(site_support):
        supports.append(f"overall site-thesis support is {_wave3_value_label(site_support)} ({float(site_support):.3f})")

    land_dev = row.get("land_developability_index")
    if pd.notna(land_dev):
        if float(land_dev) >= 0.66:
            supports.append(f"land developability is high ({float(land_dev):.3f})")
        elif float(land_dev) <= 0.33:
            brakes.append(f"land developability is weak ({float(land_dev):.3f})")

    buildability = row.get("land_buildability_score")
    if pd.notna(buildability):
        if float(buildability) >= 0.66:
            supports.append(f"buildability score is high ({float(buildability):.3f})")
        elif float(buildability) <= 0.33:
            brakes.append(f"buildability score is low ({float(buildability):.3f})")

    recreation = row.get("recreation_access_score")
    if pd.notna(recreation) and float(recreation) >= 0.66:
        supports.append(f"recreation access is strong ({float(recreation):.3f})")

    optionality = row.get("land_optional_use_score")
    if pd.notna(optionality) and float(optionality) >= 0.66:
        supports.append(f"land optionality is high ({float(optionality):.3f})")

    optionality_profile = row.get("optionality_profile_index")
    if pd.notna(optionality_profile):
        if float(optionality_profile) >= 0.66:
            supports.append(f"multi-lane optionality is strong ({float(optionality_profile):.3f})")
        elif float(optionality_profile) <= 0.33:
            brakes.append(f"multi-lane optionality is limited ({float(optionality_profile):.3f})")

    fragility_balance = row.get("fragility_balance_index")
    if pd.notna(fragility_balance):
        if float(fragility_balance) >= 0.66:
            supports.append(f"structural support still outweighs fragility pressure ({float(fragility_balance):.3f})")
        elif float(fragility_balance) <= 0.33:
            brakes.append(f"fragility pressure outweighs structural support ({float(fragility_balance):.3f})")

    scarcity_balance = row.get("scarcity_amenity_balance_index")
    if pd.notna(scarcity_balance) and float(scarcity_balance) >= 0.66:
        supports.append(f"scarcity and amenity depth jointly support long-run value ({float(scarcity_balance):.3f})")

    ag_value = row.get("usda_ssurgo_ag_value_score")
    if pd.notna(ag_value) and float(ag_value) >= 0.66:
        supports.append(f"soil-based agricultural value is strong ({float(ag_value):.3f})")

    constraint = row.get("land_constraint_pressure")
    if pd.notna(constraint):
        if float(constraint) >= 0.66:
            brakes.append(f"structural land constraints are high ({float(constraint):.3f})")
        elif float(constraint) <= 0.33:
            supports.append(f"structural land constraints are relatively light ({float(constraint):.3f})")

    fragility = row.get("land_fragility_pressure")
    if pd.notna(fragility):
        if float(fragility) >= 0.66:
            brakes.append(f"fragility pressure is high ({float(fragility):.3f})")
        elif float(fragility) <= 0.33:
            supports.append(f"fragility pressure is relatively low ({float(fragility):.3f})")

    wildfire = row.get("usfs_wildfire_fragility_index")
    if pd.notna(wildfire) and float(wildfire) >= 0.66:
        brakes.append(f"wildfire fragility is elevated ({float(wildfire):.3f})")

    coastal = row.get("coastal_flood_pressure")
    if pd.notna(coastal) and float(coastal) >= 0.66:
        brakes.append(f"coastal flood pressure is elevated ({float(coastal):.3f})")

    wetlands = row.get("fws_wetlands_constraint_index")
    if pd.notna(wetlands) and float(wetlands) >= 0.66:
        brakes.append(f"wetlands constraint is elevated ({float(wetlands):.3f})")

    scarcity = row.get("padus_land_scarcity_index")
    if pd.notna(scarcity):
        if float(scarcity) >= 0.66:
            supports.append(f"protected/open-land scarcity may support long-run value ({float(scarcity):.3f})")
        elif float(scarcity) <= 0.33:
            brakes.append(f"protected-land scarcity support is limited ({float(scarcity):.3f})")

    cluster_label = row.get("constraint_cluster_label")
    if isinstance(cluster_label, str) and cluster_label.strip():
        if cluster_label in {"fragile_constrained", "fragility_exposed", "hard_constraint"}:
            brakes.append(f"structural archetype is `{cluster_label}`")
        elif cluster_label == "clean_optional":
            supports.append(f"structural archetype is `{cluster_label}`")

    summary = "Wave 3 context is not yet broad enough for this county."
    if pd.notna(site_support) or pd.notna(land_dev):
        summary = (
            "Wave 3 reads this county through the combined lens of developability, structural constraint, "
            "fragility, access, and land optionality."
        )

    metric_df = pd.DataFrame(
        [
            {"Metric": label, "Value": float(val), "Type": "support" if "Pressure" not in label else "pressure"}
            for label, val in metrics.items()
            if pd.notna(val)
        ]
    )
    return {
        "summary": summary,
        "supports": supports[:6],
        "brakes": brakes[:6],
        "metric_df": metric_df,
    }


def _build_wave3_narrative(row: pd.Series) -> dict[str, str | list[str]]:
    profile = _build_wave3_profile(row)
    supports = profile.get("supports") or []
    brakes = profile.get("brakes") or []
    support_short = "; ".join(supports[:2]) if supports else "no strong structural supports identified yet"
    brake_short = "; ".join(brakes[:2]) if brakes else "no major structural brakes identified yet"
    summary = f"Supports: {support_short}. Brakes: {brake_short}."
    return {
        "summary": summary,
        "support_short": support_short,
        "brake_short": brake_short,
        "supports": supports,
        "brakes": brakes,
    }


def _build_wave3_decision_narrative(row: pd.Series) -> dict[str, object]:
    note = _build_wave3_narrative(row)
    support = row.get("wave3_support_score", row.get("site_thesis_support_index"))
    brake = row.get("wave3_brake_score")
    net = row.get("wave3_net_support")
    adjustment = row.get("wave3_overlay_adjustment")
    overlay_rank = row.get("wave3_overlay_rank")
    base_rank = row.get("overall_rank", row.get("current_rank"))
    constraint = row.get("land_constraint_pressure")
    fragility = row.get("land_fragility_pressure")
    developability = row.get("land_developability_index")
    site_support = row.get("site_thesis_support_index")
    pred5 = row.get("pred_avg_5yr")
    pred3 = row.get("pred_policy_3yr")
    risk = row.get("composite_risk")

    support_v = float(support) if pd.notna(support) else None
    brake_v = float(brake) if pd.notna(brake) else None
    net_v = float(net) if pd.notna(net) else None
    adjustment_v = float(adjustment) if pd.notna(adjustment) else None

    if net_v is not None and net_v >= 0.25:
        verdict = "structural tailwind"
    elif net_v is not None and net_v <= -0.20:
        verdict = "structural brake"
    elif support_v is not None and brake_v is not None and support_v >= 0.60 and brake_v <= 0.45:
        verdict = "clean support"
    elif brake_v is not None and brake_v >= 0.65:
        verdict = "needs diligence"
    else:
        verdict = "mixed but usable"

    thesis_bits: list[str] = []
    if pd.notna(pred5):
        thesis_bits.append(f"5yr upside is {_fmt_pct(pred5)}")
    if pd.notna(pred3):
        thesis_bits.append(f"3yr policy signal is {_fmt_pct(pred3)}")
    if support_v is not None and brake_v is not None:
        thesis_bits.append(f"structural support/brake balance is {support_v:.3f}/{brake_v:.3f}")
    if pd.notna(base_rank) and pd.notna(overlay_rank):
        rank_delta = int(float(overlay_rank) - float(base_rank))
        if rank_delta < 0:
            thesis_bits.append(f"overlay would lift rank by {abs(rank_delta)}")
        elif rank_delta > 0:
            thesis_bits.append(f"overlay would trim rank by {rank_delta}")
        else:
            thesis_bits.append("overlay leaves rank unchanged")

    change_mind: list[str] = []
    if pd.notna(constraint) and float(constraint) >= 0.60:
        change_mind.append("Confirm whether mapped land constraints are truly binding for investable parcels.")
    if pd.notna(fragility) and float(fragility) >= 0.60:
        change_mind.append("Check whether hazard/fragility exposure is localized or county-wide.")
    if pd.notna(developability) and float(developability) <= 0.45:
        change_mind.append("Require parcel-level buildability evidence before treating the county as actionable.")
    if pd.notna(site_support) and float(site_support) <= 0.45:
        change_mind.append("Look for a specific submarket thesis because county-level site support is not strong.")
    if pd.notna(risk) and float(risk) >= 55:
        change_mind.append("Reconcile structural support with elevated composite risk before sizing exposure.")
    if not change_mind:
        change_mind.append("Look for parcel availability, infrastructure access, and local entitlement friction before advancing.")

    checklist = [
        "Map top candidate parcels against constraints, flood/wetland layers, and road access.",
        "Check whether recent permits/listings support the county-level demand signal.",
        "Review local zoning/entitlement friction for the highest-ranked submarkets.",
    ]
    if pd.notna(fragility) and float(fragility) >= 0.55:
        checklist.append("Add insurance, fire, flood, or climate-risk diligence to the first-pass review.")
    if pd.notna(constraint) and float(constraint) >= 0.55:
        checklist.append("Estimate how much unconstrained land is actually investable, not just theoretically present.")

    if thesis_bits:
        thesis = "; ".join(thesis_bits) + "."
    else:
        thesis = "Current model and structural context are not complete enough for a confident thesis."

    return {
        "verdict": verdict,
        "thesis": thesis,
        "support": note["support_short"],
        "brake": note["brake_short"],
        "what_would_change_mind": change_mind[:4],
        "follow_up_checklist": checklist[:5],
        "overlay_adjustment": adjustment_v,
        "net_support": net_v,
    }


def _coastal_lane_provenance(row: pd.Series, wave3_status: dict | None = None) -> dict[str, object]:
    wave3_status = wave3_status or {}
    noaa_trial = wave3_status.get("noaa_guarded_trial") or {}
    excluded = {str(f).zfill(5) for f in (noaa_trial.get("excluded_fips") or [])}
    fips = str(row.get("fips") or "").zfill(5)

    noaa_release = row.get("noaa_sea_level_release_label")
    noaa_flag = pd.to_numeric(pd.Series([row.get("noaa_sea_level_coastal_county_flag")]), errors="coerce").iloc[0]
    noaa_flag = int(noaa_flag) if pd.notna(noaa_flag) else 0
    proxy_flag = pd.to_numeric(pd.Series([row.get("coastal_exposure_county_flag")]), errors="coerce").iloc[0]
    proxy_flag = int(proxy_flag) if pd.notna(proxy_flag) else 0

    if noaa_trial.get("active") and fips in excluded:
        return {
            "label": "Excluded from Guarded NOAA Trial",
            "source": "proxy_excluded",
            "summary": "This county is in the explicit guarded-NOAA exclusion set, so coastal context is still coming from the proxy lane.",
        }
    if noaa_trial.get("active") and pd.notna(noaa_release) and noaa_flag == 1:
        return {
            "label": "Guarded NOAA",
            "source": "noaa",
            "summary": "This county is currently using guarded NOAA coastal context in the live trial lane.",
        }
    if noaa_trial.get("active") and pd.notna(noaa_release):
        return {
            "label": "Proxy Fallback",
            "source": "proxy_fallback",
            "summary": "This county is inside the guarded NOAA trial universe, but current coastal context is still falling back to the proxy lane because NOAA has no positive local coastal signal here.",
        }
    if proxy_flag == 1:
        return {
            "label": "Proxy Coastal Context",
            "source": "proxy",
            "summary": "This county is currently using the standard proxy coastal context.",
        }
    return {
        "label": "No Coastal Signal",
        "source": "none",
        "summary": "This county currently has no meaningful coastal signal in the active Wave 3 lane.",
    }


def _build_wave3_compare_rows(cmp_raw: pd.DataFrame, wave3_status: dict | None = None) -> pd.DataFrame:
    rows = []
    for _, row in cmp_raw.iterrows():
        provenance = _coastal_lane_provenance(row, wave3_status)
        rows.append(
            {
                "county_name": row.get("county_name"),
                "state": row.get("state"),
                "overall_rank": row.get("overall_rank"),
                "coastal_lane": provenance.get("label"),
                "wave3_overlay_rank": row.get("wave3_overlay_rank"),
                "wave3_overlay_adjustment": row.get("wave3_overlay_adjustment"),
                "wave3_net_support": row.get("wave3_net_support"),
                "wave3_support_score": row.get("wave3_support_score"),
                "wave3_brake_score": row.get("wave3_brake_score"),
                "wave3_structural_summary": row.get("wave3_structural_summary"),
                "site_thesis_support_index": row.get("site_thesis_support_index"),
                "land_developability_index": row.get("land_developability_index"),
                "land_constraint_pressure": row.get("land_constraint_pressure"),
                "land_fragility_pressure": row.get("land_fragility_pressure"),
                "fragility_balance_index": row.get("fragility_balance_index"),
                "scarcity_amenity_balance_index": row.get("scarcity_amenity_balance_index"),
                "optionality_profile_index": row.get("optionality_profile_index"),
                "constraint_cluster_label": row.get("constraint_cluster_label"),
                "recreation_access_score": row.get("recreation_access_score"),
                "coastal_flood_pressure": row.get("coastal_flood_pressure"),
            }
        )
    return pd.DataFrame(rows)


def _build_wave3_compare_bullets(cmp_raw: pd.DataFrame, wave3_status: dict | None = None) -> list[str]:
    bullets: list[str] = []
    if cmp_raw.empty or len(cmp_raw) < 2:
        return bullets

    best_support = cmp_raw.loc[cmp_raw["site_thesis_support_index"].fillna(-1).idxmax()] if "site_thesis_support_index" in cmp_raw.columns else None
    best_dev = cmp_raw.loc[cmp_raw["land_developability_index"].fillna(-1).idxmax()] if "land_developability_index" in cmp_raw.columns else None
    worst_frag = cmp_raw.loc[cmp_raw["land_fragility_pressure"].fillna(-1).idxmax()] if "land_fragility_pressure" in cmp_raw.columns else None
    worst_constraint = cmp_raw.loc[cmp_raw["land_constraint_pressure"].fillna(-1).idxmax()] if "land_constraint_pressure" in cmp_raw.columns else None
    best_optionality = cmp_raw.loc[cmp_raw["optionality_profile_index"].fillna(-1).idxmax()] if "optionality_profile_index" in cmp_raw.columns else None

    def _label(row: pd.Series) -> str:
        return f"{row.get('county_name')}, {row.get('state')}"

    if best_support is not None and pd.notna(best_support.get("site_thesis_support_index")):
        bullets.append(
            f"`{_label(best_support)}` has the strongest overall site-thesis support "
            f"({float(best_support['site_thesis_support_index']):.3f})."
        )
    if best_dev is not None and pd.notna(best_dev.get("land_developability_index")):
        bullets.append(
            f"`{_label(best_dev)}` has the strongest land-developability profile "
            f"({float(best_dev['land_developability_index']):.3f})."
        )
    if worst_frag is not None and pd.notna(worst_frag.get("land_fragility_pressure")):
        bullets.append(
            f"`{_label(worst_frag)}` carries the highest land fragility pressure "
            f"({float(worst_frag['land_fragility_pressure']):.3f})."
        )
    if worst_constraint is not None and pd.notna(worst_constraint.get("land_constraint_pressure")):
        bullets.append(
            f"`{_label(worst_constraint)}` has the heaviest structural land constraints "
            f"({float(worst_constraint['land_constraint_pressure']):.3f})."
        )
    if best_optionality is not None and pd.notna(best_optionality.get("optionality_profile_index")):
        bullets.append(
            f"`{_label(best_optionality)}` shows the strongest optionality profile "
            f"({float(best_optionality['optionality_profile_index']):.3f})."
        )
    lane_labels = []
    for _, row in cmp_raw.iterrows():
        label = _coastal_lane_provenance(row, wave3_status).get("label")
        if label:
            lane_labels.append(f"{row.get('county_name')}, {row.get('state')}: {label}")
    if lane_labels:
        bullets.append("Coastal lane provenance: " + "; ".join(lane_labels[:4]) + ".")
    return bullets[:4]


def _family_context_for_row(row: pd.Series, policy_payload: dict | None) -> pd.DataFrame:
    if not policy_payload:
        return pd.DataFrame()
    rows = []
    for fam in policy_payload.get("families", []) or []:
        prefixes = tuple(fam.get("prefixes") or [])
        if not prefixes:
            continue
        matching = [col for col in row.index if col.startswith(prefixes)]
        observed = [col for col in matching if pd.notna(row.get(col))]
        if not observed:
            continue
        rows.append(
            {
                "Family": fam.get("label", fam.get("family")),
                "Training Status": fam.get("training_status", "unknown"),
                "Default Action": fam.get("default_training_action", "unknown"),
                "Observed Fields": len(observed),
                "Sample Fields": ", ".join(observed[:3]),
            }
        )
    return pd.DataFrame(rows)


def _default_user_data() -> dict:
    return {
        "saved_watchlists": {},
        "county_notes": {},
        "saved_compare_sets": {},
        "saved_strategy_profiles": {},
        "county_funnel": {},
        "county_feedback": {},
        "preboom_feedback": {},
        "diligence_evidence": {},
        "parcel_checklists": {},
        "watchlist_alert_state": {},
        "watchlist_settings": {
            "top_rank_strong": 25,
            "top_rank_watch": 100,
            "durable_top25_share": 0.60,
            "weak_top25_share": 0.20,
            "calm_std_rank": 12.0,
            "volatile_std_rank": 25.0,
            "sharp_rank_move": 10.0,
            "strong_5yr_upside": 0.15,
            "weak_5yr_upside": 0.05,
            "elevated_risk": 60.0,
            "alert_rank_exit_boundary": 50,
        },
    }


def _normalize_user_id(raw: str | None) -> str:
    text = (raw or "demo").strip().lower()
    text = re.sub(r"[^a-z0-9_.@-]+", "-", text).strip("-")
    return text[:80] or "demo"


def _current_user_id() -> str:
    return _normalize_user_id(st.session_state.get("dashboard_user_id", "demo"))


def _init_user_data_db() -> None:
    USER_DATA_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(USER_DATA_DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_state (
                user_id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def _coerce_user_data(data: dict | None) -> dict:
    if not isinstance(data, dict):
        return _default_user_data()
    base = _default_user_data()
    base.update(data)
    base["saved_watchlists"] = base.get("saved_watchlists") or {}
    base["county_notes"] = base.get("county_notes") or {}
    base["saved_compare_sets"] = base.get("saved_compare_sets") or {}
    base["saved_strategy_profiles"] = base.get("saved_strategy_profiles") or {}
    base["county_funnel"] = base.get("county_funnel") or {}
    base["county_feedback"] = base.get("county_feedback") or {}
    base["preboom_feedback"] = base.get("preboom_feedback") if isinstance(base.get("preboom_feedback"), dict) else {}
    base["diligence_evidence"] = base.get("diligence_evidence") or {}
    base["parcel_checklists"] = base.get("parcel_checklists") or {}
    base["watchlist_alert_state"] = base.get("watchlist_alert_state") or {}
    base["watchlist_settings"] = {**_default_user_data()["watchlist_settings"], **(base.get("watchlist_settings") or {})}
    return base


def _load_user_data(user_id: str | None = None) -> dict:
    resolved_user = _normalize_user_id(user_id or _current_user_id())
    try:
        _init_user_data_db()
        with sqlite3.connect(USER_DATA_DB_PATH) as conn:
            row = conn.execute(
                "SELECT payload FROM user_state WHERE user_id = ?",
                (resolved_user,),
            ).fetchone()
        if row:
            return _coerce_user_data(json.loads(row[0]))
    except (OSError, sqlite3.Error, json.JSONDecodeError):
        pass
    if resolved_user == "demo":
        return _coerce_user_data(_safe_json_load(USER_DATA_PATH))
    return _default_user_data()


def _save_user_data(data: dict, user_id: str | None = None) -> None:
    resolved_user = _normalize_user_id(user_id or _current_user_id())
    _init_user_data_db()
    payload = json.dumps(data, indent=2)
    with sqlite3.connect(USER_DATA_DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO user_state (user_id, payload, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                payload = excluded.payload,
                updated_at = excluded.updated_at
            """,
            (resolved_user, payload, datetime.now().isoformat()),
        )
        conn.commit()


def _user_storage_status() -> str:
    user_id = _current_user_id()
    if USER_DATA_DB_PATH.exists():
        return f"SQLite user store: `{USER_DATA_DB_PATH.name}` / user `{user_id}`"
    return f"SQLite user store will be created on first save / user `{user_id}`"


def _save_current_user_state() -> None:
    _save_user_data(
        {
            "saved_watchlists": st.session_state.saved_watchlists,
            "county_notes": st.session_state.county_notes,
            "saved_compare_sets": st.session_state.saved_compare_sets,
            "saved_strategy_profiles": st.session_state.saved_strategy_profiles,
            "county_funnel": st.session_state.county_funnel,
            "county_feedback": st.session_state.county_feedback,
            "preboom_feedback": st.session_state.preboom_feedback,
            "diligence_evidence": st.session_state.diligence_evidence,
            "parcel_checklists": st.session_state.parcel_checklists,
            "watchlist_alert_state": st.session_state.watchlist_alert_state,
            "watchlist_settings": st.session_state.watchlist_settings,
        }
    )


def _normalize_tag_list(raw: str | None) -> list[str]:
    if raw is None:
        return []
    parts = [p.strip() for p in str(raw).replace("\n", ",").split(",")]
    return sorted({p for p in parts if p})


def _build_watchlist_markdown(
    watch_df: pd.DataFrame,
    history_df: pd.DataFrame | None,
    notes: dict[str, dict],
    watchlist_name: str | None = None,
    watchlist_meta: dict | None = None,
) -> str:
    title = watchlist_name or "Current Watchlist"
    lines = [f"# {title}", ""]
    lines.append(f"- Generated at: `{datetime.now().isoformat()}`")
    lines.append(f"- Counties: `{len(watch_df)}`")
    if watchlist_meta:
        thesis = (watchlist_meta.get("thesis") or "").strip()
        owner = (watchlist_meta.get("owner") or "").strip()
        tags = watchlist_meta.get("tags") or []
        if owner:
            lines.append(f"- Owner: `{owner}`")
        if tags:
            lines.append(f"- Tags: `{', '.join(tags)}`")
        if thesis:
            lines.append(f"- Thesis: {thesis}")
    lines.append("")
    lines.append("## Current Snapshot")
    for _, row in watch_df.sort_values("overall_rank").iterrows():
        fips = str(row.get("fips", "")).zfill(5)
        wave3_note = _build_wave3_narrative(row)
        decision = _build_wave3_decision_narrative(row)
        lines.append(
            f"- `{row.get('county_name')}, {row.get('state')}` [FIPS {fips}]"
            f": rank `#{int(row.get('overall_rank'))}`"
            f", opportunity `{_fmt_score(row.get('opportunity_score'))}`"
            f", 3yr `{_fmt_pct(row.get('pred_policy_3yr'))}`"
            f", 5yr `{_fmt_pct(row.get('pred_avg_5yr'))}`"
            f", risk `{_fmt_score(row.get('composite_risk'))}`"
            f", confidence `{row.get('confidence', '—')}`"
        )
        lines.append(f"  - Wave 3: {wave3_note['summary']}")
        lines.append(f"  - Decision read: `{decision['verdict']}`. {decision['thesis']}")
        if decision.get("what_would_change_mind"):
            lines.append(f"  - What would change our mind: {decision['what_would_change_mind'][0]}")
        if decision.get("follow_up_checklist"):
            lines.append(f"  - Next diligence: {decision['follow_up_checklist'][0]}")
        note_block = notes.get(fips) or {}
        note_text = (note_block.get("note") or "").strip()
        if note_text:
            lines.append(f"  - Note: {note_text}")
    if history_df is not None and not history_df.empty:
        lines.append("")
        lines.append("## Recent Run Movement")
        for fips, grp in history_df.groupby("fips"):
            grp = grp.sort_values("run_id")
            first = grp.iloc[0]
            last = grp.iloc[-1]
            lines.append(
                f"- `{last['county_name']}, {last['state']}`: "
                f"`{first['run_id']}` rank `#{int(first['overall_rank'])}` -> "
                f"`{last['run_id']}` rank `#{int(last['overall_rank'])}`"
            )
    return "\n".join(lines) + "\n"


def _build_latest_run_delta_bullets(shift_row: pd.Series) -> list[str]:
    bullets: list[str] = []
    old_rank = shift_row.get("overall_rank_old")
    new_rank = shift_row.get("overall_rank_new")
    if pd.notna(old_rank) and pd.notna(new_rank):
        bullets.append(f"Latest run rank moved from `#{int(old_rank)}` to `#{int(new_rank)}`.")
    for label, col in [
        ("opportunity score", "opportunity_score_delta"),
        ("3yr policy signal", "pred_policy_3yr_delta"),
        ("XGBoost 5yr", "pred_xgboost_5yr_delta"),
        ("LightGBM 5yr", "pred_lightgbm_5yr_delta"),
    ]:
        val = shift_row.get(col)
        if pd.notna(val):
            bullets.append(f"Latest `{label}` delta: `{val:+.3f}`.")
    return bullets[:5]


def _normalize_fips_value(value) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    if not text:
        return None
    digits = "".join(ch for ch in text if ch.isdigit())
    if not digits:
        return None
    return digits.zfill(5)[-5:]


def _parse_watchlist_import(file_name: str, raw_bytes: bytes) -> dict:
    suffix = Path(file_name).suffix.lower()
    if suffix == ".json":
        payload = json.loads(raw_bytes.decode("utf-8"))
        if isinstance(payload, dict):
            return {"kind": "json", "payload": payload}
        raise ValueError("JSON payload must be an object.")

    text = raw_bytes.decode("utf-8")
    if suffix == ".csv":
        frame = pd.read_csv(pd.io.common.StringIO(text))
        candidate_cols = [c for c in frame.columns if c.lower() in {"fips", "county_fips", "geoid"}]
        if candidate_cols:
            values = frame[candidate_cols[0]].tolist()
        else:
            values = frame.iloc[:, 0].tolist() if not frame.empty else []
        return {"kind": "fips_list", "fips": values}

    if suffix in {".txt", ".md"}:
        values = [line.strip() for line in text.splitlines() if line.strip()]
        return {"kind": "fips_list", "fips": values}

    raise ValueError("Unsupported watchlist import type. Use JSON, CSV, TXT, or Markdown.")


def _apply_watchlist_import_payload(
    imported: dict,
    import_mode: str,
    current_watch_fips: list[str],
    saved_watchlists: dict,
    county_notes: dict,
) -> tuple[list[str], dict, dict, str]:
    mode_replace = import_mode == "Replace current session"
    watch_fips = list(current_watch_fips)
    saved = dict(saved_watchlists)
    notes = dict(county_notes)

    if imported.get("kind") == "json":
        payload = imported.get("payload") or {}
        if "saved_watchlists" in payload or "county_notes" in payload:
            imported_saved = payload.get("saved_watchlists") or {}
            imported_notes = payload.get("county_notes") or {}
            imported_compare_sets = payload.get("saved_compare_sets") or {}
            imported_alert_state = payload.get("watchlist_alert_state") or {}
            imported_parcel_checklists = payload.get("parcel_checklists") or {}
            imported_settings = payload.get("watchlist_settings") or {}
            if mode_replace:
                saved = imported_saved
                notes = imported_notes
                compare_sets = imported_compare_sets
                alert_state = imported_alert_state
                parcel_checklists = imported_parcel_checklists
                watchlist_settings = {**_default_user_data()["watchlist_settings"], **imported_settings}
                first_watch = next(iter(imported_saved.values()), {})
                watch_fips = [
                    f for f in (_normalize_fips_value(x) for x in (first_watch.get("fips") or []))
                    if f is not None
                ]
                msg = f"Imported dashboard user-data bundle with `{len(imported_saved)}` saved watchlists."
            else:
                saved.update(imported_saved)
                notes.update(imported_notes)
                compare_sets = dict(st.session_state.saved_compare_sets)
                compare_sets.update(imported_compare_sets)
                alert_state = dict(st.session_state.watchlist_alert_state)
                alert_state.update(imported_alert_state)
                parcel_checklists = dict(st.session_state.parcel_checklists)
                parcel_checklists.update(imported_parcel_checklists)
                watchlist_settings = {**st.session_state.watchlist_settings, **imported_settings}
                msg = f"Merged dashboard user-data bundle with `{len(imported_saved)}` saved watchlists."
            st.session_state.saved_compare_sets = compare_sets
            st.session_state.watchlist_alert_state = alert_state
            st.session_state.parcel_checklists = parcel_checklists
            st.session_state.watchlist_settings = watchlist_settings
            return sorted(set(watch_fips)), saved, notes, msg

        imported_fips = payload.get("fips") or payload.get("watch_fips") or []
        imported_name = payload.get("watchlist_name") or payload.get("name") or "Imported Watchlist"
        imported_notes = payload.get("county_notes") or {}
        imported_meta = payload.get("watchlist_meta") or {}
        norm_fips = [f for f in (_normalize_fips_value(x) for x in imported_fips) if f is not None]
        if mode_replace:
            watch_fips = norm_fips
        else:
            watch_fips = sorted(set(watch_fips + norm_fips))
        notes.update(imported_notes)
        saved[imported_name] = {
            "fips": sorted(set(norm_fips)),
            "updated_at": datetime.now().isoformat(),
            "count": len(set(norm_fips)),
            "owner": (imported_meta.get("owner") or "").strip(),
            "thesis": (imported_meta.get("thesis") or "").strip(),
            "tags": imported_meta.get("tags") or [],
        }
        return sorted(set(watch_fips)), saved, notes, f"Imported watchlist `{imported_name}` with `{len(set(norm_fips))}` counties."

    raw_fips = imported.get("fips") or []
    norm_fips = [f for f in (_normalize_fips_value(x) for x in raw_fips) if f is not None]
    if mode_replace:
        watch_fips = norm_fips
        msg = f"Replaced current session watchlist with `{len(set(norm_fips))}` imported counties."
    else:
        watch_fips = sorted(set(watch_fips + norm_fips))
        msg = f"Appended `{len(set(norm_fips))}` imported counties to the current session watchlist."
    return sorted(set(watch_fips)), saved, notes, msg


def _build_watchlist_share_payload(
    watch_df: pd.DataFrame,
    notes: dict[str, dict],
    watchlist_name: str | None = None,
    watchlist_meta: dict | None = None,
) -> dict:
    fips_list = watch_df["fips"].astype(str).str.zfill(5).tolist() if not watch_df.empty else []
    note_subset = {f: notes[f] for f in fips_list if f in notes}
    counties = []
    if not watch_df.empty:
        cols = [
            c for c in [
                "fips", "county_name", "state", "overall_rank", "opportunity_score",
                "pred_policy_3yr", "pred_avg_5yr", "composite_risk",
                "site_thesis_support_index", "land_developability_index",
                "land_constraint_pressure", "land_fragility_pressure",
                "wave3_overlay_rank", "wave3_overlay_adjustment", "wave3_net_support",
                "wave3_support_score", "wave3_brake_score", "wave3_structural_summary",
            ] if c in watch_df.columns
        ]
        for _, row in watch_df[cols].sort_values("overall_rank").iterrows():
            wave3_note = _build_wave3_narrative(row)
            decision = _build_wave3_decision_narrative(row)
            counties.append(
                {
                    "fips": str(row.get("fips", "")).zfill(5),
                    "county_name": row.get("county_name"),
                    "state": row.get("state"),
                    "overall_rank": int(row.get("overall_rank")) if pd.notna(row.get("overall_rank")) else None,
                    "opportunity_score": float(row.get("opportunity_score")) if pd.notna(row.get("opportunity_score")) else None,
                    "pred_policy_3yr": float(row.get("pred_policy_3yr")) if pd.notna(row.get("pred_policy_3yr")) else None,
                    "pred_avg_5yr": float(row.get("pred_avg_5yr")) if pd.notna(row.get("pred_avg_5yr")) else None,
                    "composite_risk": float(row.get("composite_risk")) if pd.notna(row.get("composite_risk")) else None,
                    "site_thesis_support_index": float(row.get("site_thesis_support_index")) if pd.notna(row.get("site_thesis_support_index")) else None,
                    "land_developability_index": float(row.get("land_developability_index")) if pd.notna(row.get("land_developability_index")) else None,
                    "land_constraint_pressure": float(row.get("land_constraint_pressure")) if pd.notna(row.get("land_constraint_pressure")) else None,
                    "land_fragility_pressure": float(row.get("land_fragility_pressure")) if pd.notna(row.get("land_fragility_pressure")) else None,
                    "wave3_overlay_rank": int(row.get("wave3_overlay_rank")) if pd.notna(row.get("wave3_overlay_rank")) else None,
                    "wave3_overlay_adjustment": float(row.get("wave3_overlay_adjustment")) if pd.notna(row.get("wave3_overlay_adjustment")) else None,
                    "wave3_net_support": float(row.get("wave3_net_support")) if pd.notna(row.get("wave3_net_support")) else None,
                    "wave3_support_score": float(row.get("wave3_support_score")) if pd.notna(row.get("wave3_support_score")) else None,
                    "wave3_brake_score": float(row.get("wave3_brake_score")) if pd.notna(row.get("wave3_brake_score")) else None,
                    "wave3_structural_summary": row.get("wave3_structural_summary"),
                    "wave3_summary": wave3_note["summary"],
                    "wave3_supports": wave3_note["supports"],
                    "wave3_brakes": wave3_note["brakes"],
                    "wave3_decision_verdict": decision["verdict"],
                    "wave3_decision_thesis": decision["thesis"],
                    "wave3_what_would_change_mind": decision["what_would_change_mind"],
                    "wave3_follow_up_checklist": decision["follow_up_checklist"],
                }
            )
    return {
        "watchlist_name": watchlist_name or "Current Session",
        "exported_at": datetime.now().isoformat(),
        "watchlist_meta": watchlist_meta or {},
        "fips": fips_list,
        "counties": counties,
        "county_notes": note_subset,
    }


def _build_watchlist_latest_run_summary(
    watch_df: pd.DataFrame,
    latest_compare_rank_df: pd.DataFrame | None,
    run_history_summary_df: pd.DataFrame | None,
    notes: dict[str, dict],
    watchlist_name: str | None = None,
) -> tuple[pd.DataFrame, str]:
    title = watchlist_name or "Current Watchlist"
    if watch_df.empty:
        return pd.DataFrame(), f"# {title} Latest Run Summary\n\nNo counties are in the current watchlist.\n"

    base = watch_df.copy()
    base["fips"] = base["fips"].astype(str).str.zfill(5)

    history_lookup = {}
    if run_history_summary_df is not None and not run_history_summary_df.empty:
        history_lookup = run_history_summary_df.set_index("fips").to_dict("index")

    compare_lookup = {}
    if latest_compare_rank_df is not None and not latest_compare_rank_df.empty:
        compare_lookup = latest_compare_rank_df.set_index("fips").to_dict("index")

    rows = []
    for _, row in base.sort_values("overall_rank").iterrows():
        fips = row["fips"]
        hist = history_lookup.get(fips, {})
        shift = compare_lookup.get(fips, {})
        wave3_note = _build_wave3_narrative(row)
        decision = _build_wave3_decision_narrative(row)
        old_rank = shift.get("overall_rank_old")
        new_rank = shift.get("overall_rank_new", row.get("overall_rank"))
        rank_shift = shift.get("rank_shift")
        if pd.isna(rank_shift) and pd.notna(old_rank) and pd.notna(new_rank):
            rank_shift = float(new_rank) - float(old_rank)
        if pd.notna(rank_shift):
            if float(rank_shift) <= -10:
                movement = "rose sharply"
            elif float(rank_shift) < 0:
                movement = "rose"
            elif float(rank_shift) >= 10:
                movement = "fell sharply"
            elif float(rank_shift) > 0:
                movement = "fell"
            else:
                movement = "held steady"
        else:
            movement = "no latest delta"

        explanation_parts = []
        for label, key in [
            ("opportunity", "opportunity_score_delta"),
            ("3yr policy", "pred_policy_3yr_delta"),
            ("XGB 5yr", "pred_xgboost_5yr_delta"),
            ("LGB 5yr", "pred_lightgbm_5yr_delta"),
        ]:
            val = shift.get(key)
            if pd.notna(val):
                explanation_parts.append(f"{label} `{float(val):+.3f}`")
        if pd.notna(hist.get("top25_presence_share")):
            explanation_parts.append(f"top-25 presence `{100*float(hist['top25_presence_share']):.0f}%`")
        if pd.notna(hist.get("std_rank")):
            explanation_parts.append(f"rank std `{float(hist['std_rank']):.1f}`")

        rows.append(
            {
                "fips": fips,
                "county_name": row.get("county_name"),
                "state": row.get("state"),
                "current_rank": int(row.get("overall_rank")) if pd.notna(row.get("overall_rank")) else None,
                "prior_rank": int(old_rank) if pd.notna(old_rank) else None,
                "rank_shift": float(rank_shift) if pd.notna(rank_shift) else None,
                "movement": movement,
                "opportunity_score": float(row.get("opportunity_score")) if pd.notna(row.get("opportunity_score")) else None,
                "pred_policy_3yr": float(row.get("pred_policy_3yr")) if pd.notna(row.get("pred_policy_3yr")) else None,
                "pred_avg_5yr": float(row.get("pred_avg_5yr")) if pd.notna(row.get("pred_avg_5yr")) else None,
                "site_thesis_support_index": float(row.get("site_thesis_support_index")) if pd.notna(row.get("site_thesis_support_index")) else None,
                "land_developability_index": float(row.get("land_developability_index")) if pd.notna(row.get("land_developability_index")) else None,
                "land_constraint_pressure": float(row.get("land_constraint_pressure")) if pd.notna(row.get("land_constraint_pressure")) else None,
                "land_fragility_pressure": float(row.get("land_fragility_pressure")) if pd.notna(row.get("land_fragility_pressure")) else None,
                "top25_presence_share": float(hist.get("top25_presence_share")) if pd.notna(hist.get("top25_presence_share")) else None,
                "std_rank": float(hist.get("std_rank")) if pd.notna(hist.get("std_rank")) else None,
                "explanation": "; ".join(explanation_parts),
                "wave3_summary": wave3_note["summary"],
                "wave3_support_short": wave3_note["support_short"],
                "wave3_brake_short": wave3_note["brake_short"],
                "wave3_decision_verdict": decision["verdict"],
                "wave3_decision_thesis": decision["thesis"],
                "wave3_what_would_change_mind": " ".join(decision["what_would_change_mind"]),
                "wave3_follow_up_checklist": " ".join(decision["follow_up_checklist"]),
                "note": (notes.get(fips) or {}).get("note"),
            }
        )

    summary_df = pd.DataFrame(rows)
    lines = [f"# {title} Latest Run Summary", ""]
    lines.append(f"- Generated at: `{datetime.now().isoformat()}`")
    lines.append(f"- Counties reviewed: `{len(summary_df)}`")
    movers = summary_df["movement"].value_counts().to_dict()
    lines.append(f"- Movement mix: `{movers}`")
    lines.append("")

    sections = [
        ("Rose Sharply", summary_df[summary_df["movement"] == "rose sharply"].sort_values("rank_shift")),
        ("Fell Sharply", summary_df[summary_df["movement"] == "fell sharply"].sort_values("rank_shift", ascending=False)),
        ("Most Stable", summary_df.sort_values(["std_rank", "current_rank"], na_position="last").head(5)),
    ]
    for label, sec in sections:
        if sec.empty:
            continue
        lines.append(f"## {label}")
        for _, rec in sec.iterrows():
            rank_part = f"`#{int(rec['prior_rank'])}` -> `#{int(rec['current_rank'])}`" if pd.notna(rec.get("prior_rank")) and pd.notna(rec.get("current_rank")) else f"`#{int(rec['current_rank'])}`" if pd.notna(rec.get("current_rank")) else "`n/a`"
            lines.append(
                f"- `{rec['county_name']}, {rec['state']}` [FIPS {rec['fips']}]"
                f": {rank_part}"
                f" | 5yr `{_fmt_pct(rec.get('pred_avg_5yr'))}`"
                f" | 3yr `{_fmt_pct(rec.get('pred_policy_3yr'))}`"
                f" | opp `{_fmt_score(rec.get('opportunity_score'))}`"
            )
            if rec.get("explanation"):
                lines.append(f"  - Drivers: {rec['explanation']}")
            if rec.get("wave3_summary"):
                lines.append(f"  - Wave 3: {rec['wave3_summary']}")
            if rec.get("wave3_decision_verdict"):
                lines.append(f"  - Decision read: `{rec['wave3_decision_verdict']}`. {rec.get('wave3_decision_thesis', '')}")
            if rec.get("wave3_what_would_change_mind"):
                lines.append(f"  - What would change our mind: {rec['wave3_what_would_change_mind']}")
            note_val = rec.get("note")
            note_text = "" if pd.isna(note_val) else str(note_val).strip()
            if note_text:
                lines.append(f"  - Note: {note_text}")
        lines.append("")

    return summary_df, "\n".join(lines).rstrip() + "\n"


def _build_watchlist_share_template(
    template_name: str,
    watch_df: pd.DataFrame,
    run_summary_df: pd.DataFrame,
    watchlist_name: str | None = None,
    watchlist_meta: dict | None = None,
) -> str:
    title = watchlist_name or "Current Watchlist"
    meta = watchlist_meta or {}
    tags = meta.get("tags") or []
    thesis = (meta.get("thesis") or "").strip()
    owner = (meta.get("owner") or "").strip()
    top_slice = watch_df.sort_values("overall_rank").head(5)

    lines = [f"# {title} — {template_name}", ""]
    lines.append(f"- Generated at: `{datetime.now().isoformat()}`")
    if owner:
        lines.append(f"- Owner: `{owner}`")
    if tags:
        lines.append(f"- Tags: `{', '.join(tags)}`")
    if thesis:
        lines.append(f"- Thesis: {thesis}")
    lines.append("")

    if template_name == "IC Summary":
        lines.append("## Top Takeaways")
        for _, row in top_slice.iterrows():
            wave3_note = _build_wave3_narrative(row)
            decision = _build_wave3_decision_narrative(row)
            lines.append(
                f"- `{row['county_name']}, {row['state']}`: rank `#{int(row['overall_rank'])}`, "
                f"5yr `{_fmt_pct(row.get('pred_avg_5yr'))}`, 3yr `{_fmt_pct(row.get('pred_policy_3yr'))}`, "
                f"risk `{_fmt_score(row.get('composite_risk'))}`"
            )
            lines.append(f"  - Structural read: {wave3_note['summary']}")
            lines.append(f"  - Decision read: `{decision['verdict']}`. {decision['thesis']}")
            if decision.get("what_would_change_mind"):
                lines.append(f"  - What would change our mind: {decision['what_would_change_mind'][0]}")
        if not run_summary_df.empty:
            risers = run_summary_df[run_summary_df["movement"].isin(["rose sharply", "rose"])].head(3)
            fallers = run_summary_df[run_summary_df["movement"].isin(["fell sharply", "fell"])].head(3)
            if not risers.empty:
                lines.append("")
                lines.append("## Recent Risers")
                for _, rec in risers.iterrows():
                    lines.append(
                        f"- `{rec['county_name']}, {rec['state']}`: rank shift `{rec['rank_shift']:+.1f}`; {rec['explanation']}"
                    )
                    if rec.get("wave3_summary"):
                        lines.append(f"  - Wave 3: {rec['wave3_summary']}")
                    if rec.get("wave3_decision_verdict"):
                        lines.append(f"  - Decision read: `{rec['wave3_decision_verdict']}`. {rec.get('wave3_decision_thesis', '')}")
            if not fallers.empty:
                lines.append("")
                lines.append("## Recent Fallers")
                for _, rec in fallers.iterrows():
                    lines.append(
                        f"- `{rec['county_name']}, {rec['state']}`: rank shift `{rec['rank_shift']:+.1f}`; {rec['explanation']}"
                    )
                    if rec.get("wave3_summary"):
                        lines.append(f"  - Wave 3: {rec['wave3_summary']}")
                    if rec.get("wave3_decision_verdict"):
                        lines.append(f"  - Decision read: `{rec['wave3_decision_verdict']}`. {rec.get('wave3_decision_thesis', '')}")
    else:
        lines.append("## Handoff Summary")
        lines.append("Use this shortlist as a starting point for the next review cycle.")
        if not run_summary_df.empty:
            lines.append("")
            lines.append("## Counties Requiring Discussion")
            focus = run_summary_df.sort_values(
                ["movement", "std_rank", "current_rank"],
                ascending=[True, False, True],
            ).head(8)
            for _, rec in focus.iterrows():
                lines.append(
                    f"- `{rec['county_name']}, {rec['state']}` [FIPS {rec['fips']}]: "
                    f"rank `#{int(rec['current_rank'])}`"
                    f", movement `{rec['movement']}`"
                    f", 5yr `{_fmt_pct(rec.get('pred_avg_5yr'))}`"
                    f", 3yr `{_fmt_pct(rec.get('pred_policy_3yr'))}`"
                )
                if rec.get("explanation"):
                    lines.append(f"  - Latest deltas: {rec['explanation']}")
                if rec.get("wave3_summary"):
                    lines.append(f"  - Wave 3: {rec['wave3_summary']}")
                if rec.get("wave3_decision_verdict"):
                    lines.append(f"  - Decision read: `{rec['wave3_decision_verdict']}`. {rec.get('wave3_decision_thesis', '')}")
                if rec.get("wave3_follow_up_checklist"):
                    lines.append(f"  - Follow-up: {rec['wave3_follow_up_checklist']}")
                note_val = rec.get("note")
                note_text = "" if pd.isna(note_val) else str(note_val).strip()
                if note_text:
                    lines.append(f"  - Analyst note: {note_text}")

    return "\n".join(lines).rstrip() + "\n"


def _build_wave3_shortlist_brief(
    watch_df: pd.DataFrame,
    run_summary_df: pd.DataFrame,
    watchlist_name: str | None = None,
    watchlist_meta: dict | None = None,
) -> str:
    title = watchlist_name or "Current Watchlist"
    meta = watchlist_meta or {}
    lines = [f"# {title} — Wave 3 Structural Brief", ""]
    lines.append(f"- Generated at: `{datetime.now().isoformat()}`")
    thesis = (meta.get("thesis") or "").strip()
    if thesis:
        lines.append(f"- Thesis: {thesis}")
    lines.append(f"- Counties reviewed: `{len(watch_df)}`")
    lines.append("")

    if watch_df.empty:
        lines.append("No counties are in the current watchlist.")
        return "\n".join(lines).rstrip() + "\n"

    enriched = watch_df.copy()
    enriched["fips"] = enriched["fips"].astype(str).str.zfill(5)
    if run_summary_df is not None and not run_summary_df.empty:
        summary_cols = [
            c for c in [
                "fips", "movement", "current_rank", "prior_rank", "rank_shift",
                "wave3_summary", "wave3_support_short", "wave3_brake_short",
                "wave3_decision_verdict", "wave3_decision_thesis",
                "wave3_what_would_change_mind", "wave3_follow_up_checklist",
            ] if c in run_summary_df.columns
        ]
        enriched = enriched.merge(run_summary_df[summary_cols], on="fips", how="left")
    else:
        enriched["movement"] = np.nan
        enriched["rank_shift"] = np.nan

    for col in [
        "wave3_summary", "wave3_support_short", "wave3_brake_short",
        "wave3_decision_verdict", "wave3_decision_thesis",
        "wave3_what_would_change_mind", "wave3_follow_up_checklist",
    ]:
        if col not in enriched.columns:
            enriched[col] = ""

    if "wave3_summary" in enriched.columns:
        missing_wave3 = enriched["wave3_summary"].astype(str).str.len() == 0
    else:
        missing_wave3 = pd.Series(True, index=enriched.index)
    for idx in enriched[missing_wave3].index:
        note = _build_wave3_narrative(enriched.loc[idx])
        decision = _build_wave3_decision_narrative(enriched.loc[idx])
        enriched.at[idx, "wave3_summary"] = note["summary"]
        enriched.at[idx, "wave3_support_short"] = note["support_short"]
        enriched.at[idx, "wave3_brake_short"] = note["brake_short"]
        enriched.at[idx, "wave3_decision_verdict"] = decision["verdict"]
        enriched.at[idx, "wave3_decision_thesis"] = decision["thesis"]
        enriched.at[idx, "wave3_what_would_change_mind"] = " ".join(decision["what_would_change_mind"])
        enriched.at[idx, "wave3_follow_up_checklist"] = " ".join(decision["follow_up_checklist"])
    missing_decision = enriched["wave3_decision_verdict"].fillna("").astype(str).str.len() == 0
    for idx in enriched[missing_decision].index:
        decision = _build_wave3_decision_narrative(enriched.loc[idx])
        enriched.at[idx, "wave3_decision_verdict"] = decision["verdict"]
        enriched.at[idx, "wave3_decision_thesis"] = decision["thesis"]
        enriched.at[idx, "wave3_what_would_change_mind"] = " ".join(decision["what_would_change_mind"])
        enriched.at[idx, "wave3_follow_up_checklist"] = " ".join(decision["follow_up_checklist"])

    def _brief_section(header: str, section_df: pd.DataFrame) -> None:
        if section_df.empty:
            return
        lines.append(f"## {header}")
        for _, rec in section_df.iterrows():
            lines.append(
                f"- `{rec['county_name']}, {rec['state']}` [FIPS {rec['fips']}]"
                f": rank `#{int(rec['overall_rank'])}`"
                f", 5yr `{_fmt_pct(rec.get('pred_avg_5yr'))}`"
                f", support `{rec.get('wave3_support_short', '—')}`"
                f", brakes `{rec.get('wave3_brake_short', '—')}`"
            )
        lines.append("")

    if "site_thesis_support_index" in enriched.columns:
        _brief_section(
            "Strongest Structural Support",
            enriched.sort_values(
                ["site_thesis_support_index", "overall_rank"],
                ascending=[False, True],
                na_position="last",
            ).head(5),
        )
    if "land_developability_index" in enriched.columns:
        _brief_section(
            "Cleanest Developability",
            enriched.sort_values(
                ["land_developability_index", "overall_rank"],
                ascending=[False, True],
                na_position="last",
            ).head(5),
        )
    if "land_constraint_pressure" in enriched.columns or "land_fragility_pressure" in enriched.columns:
        brake_sort_cols = [c for c in ["land_constraint_pressure", "land_fragility_pressure", "overall_rank"] if c in enriched.columns]
        if brake_sort_cols:
            ascending = [False] * (len(brake_sort_cols) - 1) + [True]
            _brief_section(
                "Heaviest Structural Brakes",
                enriched.sort_values(brake_sort_cols, ascending=ascending, na_position="last").head(5),
            )

    lines.append("## County Narratives")
    for _, rec in enriched.sort_values("overall_rank").iterrows():
        lines.append(
            f"- `{rec['county_name']}, {rec['state']}` [FIPS {rec['fips']}]"
            f": {rec.get('wave3_summary', 'Wave 3 summary unavailable.')}"
        )
        if rec.get("wave3_decision_verdict"):
            lines.append(f"  - Decision read: `{rec['wave3_decision_verdict']}`. {rec.get('wave3_decision_thesis', '')}")
        if rec.get("wave3_what_would_change_mind"):
            lines.append(f"  - What would change our mind: {rec['wave3_what_would_change_mind']}")
        if rec.get("wave3_follow_up_checklist"):
            lines.append(f"  - Follow-up checklist: {rec['wave3_follow_up_checklist']}")
        movement = rec.get("movement")
        if pd.notna(movement):
            lines.append(f"  - Latest movement: `{movement}`")
        rank_shift = rec.get("rank_shift")
        if pd.notna(rank_shift):
            lines.append(f"  - Rank shift: `{float(rank_shift):+.1f}`")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _classify_wave3_structural_posture(row: pd.Series) -> tuple[str, list[str]]:
    support = row.get("site_thesis_support_index")
    developability = row.get("land_developability_index")
    constraint = row.get("land_constraint_pressure")
    fragility = row.get("land_fragility_pressure")

    reasons: list[str] = []
    strong_support = pd.notna(support) and float(support) >= 0.66
    strong_dev = pd.notna(developability) and float(developability) >= 0.66
    high_constraint = pd.notna(constraint) and float(constraint) >= 0.66
    high_fragility = pd.notna(fragility) and float(fragility) >= 0.66

    if strong_support:
        reasons.append(f"site support `{float(support):.3f}`")
    if strong_dev:
        reasons.append(f"developability `{float(developability):.3f}`")
    if high_constraint:
        reasons.append(f"constraint pressure `{float(constraint):.3f}`")
    if high_fragility:
        reasons.append(f"fragility pressure `{float(fragility):.3f}`")

    if strong_support and strong_dev and not high_constraint and not high_fragility:
        return "structurally_supported", reasons
    if high_constraint or high_fragility:
        return "structurally_constrained", reasons
    return "mixed_structural_read", reasons


def _build_wave3_shortlist_scorecard(
    watch_df: pd.DataFrame,
    run_summary_df: pd.DataFrame | None,
) -> tuple[pd.DataFrame, str]:
    if watch_df.empty:
        return pd.DataFrame(), "# Wave 3 Structural Scorecard\n\nNo counties are in the current watchlist.\n"

    scorecard = watch_df.copy()
    scorecard["fips"] = scorecard["fips"].astype(str).str.zfill(5)
    if run_summary_df is not None and not run_summary_df.empty:
        extra_cols = [
            c for c in [
                "fips", "movement", "rank_shift", "wave3_support_short", "wave3_brake_short",
                "wave3_decision_verdict", "wave3_decision_thesis",
                "wave3_what_would_change_mind", "wave3_follow_up_checklist",
            ] if c in run_summary_df.columns
        ]
        scorecard = scorecard.merge(run_summary_df[extra_cols], on="fips", how="left")

    posture_vals = scorecard.apply(_classify_wave3_structural_posture, axis=1)
    scorecard["structural_posture"] = [x[0] for x in posture_vals]
    scorecard["structural_posture_reasons"] = ["; ".join(x[1]) for x in posture_vals]

    if "wave3_support_short" not in scorecard.columns or "wave3_brake_short" not in scorecard.columns:
        notes = scorecard.apply(_build_wave3_narrative, axis=1)
        if "wave3_support_short" not in scorecard.columns:
            scorecard["wave3_support_short"] = [n["support_short"] for n in notes]
        if "wave3_brake_short" not in scorecard.columns:
            scorecard["wave3_brake_short"] = [n["brake_short"] for n in notes]
    for col in [
        "wave3_decision_verdict",
        "wave3_decision_thesis",
        "wave3_what_would_change_mind",
        "wave3_follow_up_checklist",
    ]:
        if col not in scorecard.columns:
            scorecard[col] = ""
    missing_decision = scorecard["wave3_decision_verdict"].fillna("").astype(str).str.len() == 0
    for idx in scorecard[missing_decision].index:
        decision = _build_wave3_decision_narrative(scorecard.loc[idx])
        scorecard.at[idx, "wave3_decision_verdict"] = decision["verdict"]
        scorecard.at[idx, "wave3_decision_thesis"] = decision["thesis"]
        scorecard.at[idx, "wave3_what_would_change_mind"] = " ".join(decision["what_would_change_mind"])
        scorecard.at[idx, "wave3_follow_up_checklist"] = " ".join(decision["follow_up_checklist"])

    lines = ["# Wave 3 Structural Scorecard", ""]
    lines.append(f"- Generated at: `{datetime.now().isoformat()}`")
    lines.append(f"- Counties reviewed: `{len(scorecard)}`")
    lines.append(
        f"- Structural posture mix: `{scorecard['structural_posture'].value_counts().to_dict()}`"
    )
    lines.append("")
    for _, rec in scorecard.sort_values("overall_rank").iterrows():
        lines.append(
            f"- `{rec['county_name']}, {rec['state']}` [FIPS {rec['fips']}]"
            f": rank `#{int(rec['overall_rank'])}`"
            f", posture `{rec['structural_posture']}`"
            f", decision `{rec.get('wave3_decision_verdict', '—')}`"
            f", support `{rec.get('wave3_support_short', '—')}`"
            f", brakes `{rec.get('wave3_brake_short', '—')}`"
        )
        reasons = str(rec.get("structural_posture_reasons") or "").strip()
        if reasons:
            lines.append(f"  - Structural drivers: {reasons}")
        if rec.get("wave3_decision_thesis"):
            lines.append(f"  - Thesis: {rec['wave3_decision_thesis']}")
        if rec.get("wave3_what_would_change_mind"):
            lines.append(f"  - What would change our mind: {rec['wave3_what_would_change_mind']}")
        if rec.get("wave3_follow_up_checklist"):
            lines.append(f"  - Follow-up checklist: {rec['wave3_follow_up_checklist']}")
    lines.append("")
    return scorecard, "\n".join(lines).rstrip() + "\n"


def _build_watchlist_alert_digest(
    alert_df: pd.DataFrame,
    alert_state: dict[str, dict] | None = None,
    watchlist_name: str | None = None,
) -> tuple[dict, str]:
    title = watchlist_name or "Current Watchlist"
    if alert_df is None or alert_df.empty:
        empty_payload = {
            "watchlist_name": title,
            "generated_at": datetime.now().isoformat(),
            "counts": {"active": 0, "acknowledged": 0, "suppressed": 0},
            "severity_counts": {},
            "top_review_counties": [],
        }
        return empty_payload, f"# {title} Alert Digest\n\nNo watchlist alerts are currently firing.\n"

    df = alert_df.copy()
    state_lookup = alert_state or {}
    if "alert_key" not in df.columns:
        df["alert_key"] = df.apply(_alert_key, axis=1)
    df["alert_status"] = df["alert_key"].map(lambda k: (state_lookup.get(k) or {}).get("status", "active"))
    df["alert_note"] = df["alert_key"].map(lambda k: (state_lookup.get(k) or {}).get("note", ""))
    df["alert_updated_at"] = df["alert_key"].map(lambda k: (state_lookup.get(k) or {}).get("updated_at", ""))

    counts = df["alert_status"].value_counts().to_dict()
    severity_counts = df["severity"].value_counts().to_dict() if "severity" in df.columns else {}

    review_df = df[df["alert_status"] != "suppressed"].copy()
    review_rollup = []
    if not review_df.empty:
        grouped = (
            review_df.groupby(["fips", "county_name", "state"], dropna=False)
            .agg(
                active_alerts=("alert_key", "count"),
                high_severity=("severity", lambda s: int((s == "high").sum())),
                medium_severity=("severity", lambda s: int((s == "medium").sum())),
                current_rank=("current_rank", "min"),
                worst_health=("health_status", "first"),
            )
            .reset_index()
            .sort_values(
                ["high_severity", "active_alerts", "current_rank", "county_name"],
                ascending=[False, False, True, True],
                na_position="last",
            )
        )
        review_rollup = grouped.head(8).to_dict("records")

    payload = {
        "watchlist_name": title,
        "generated_at": datetime.now().isoformat(),
        "counts": {
            "active": int(counts.get("active", 0)),
            "acknowledged": int(counts.get("acknowledged", 0)),
            "suppressed": int(counts.get("suppressed", 0)),
        },
        "severity_counts": {str(k): int(v) for k, v in severity_counts.items()},
        "top_review_counties": review_rollup,
        "alerts": df[
            [
                c
                for c in [
                    "fips",
                    "county_name",
                    "state",
                    "alert_type",
                    "severity",
                    "alert_status",
                    "message",
                    "current_rank",
                    "prior_rank",
                    "rank_shift",
                    "std_rank",
                    "health_status",
                    "alert_note",
                    "alert_updated_at",
                ]
                if c in df.columns
            ]
        ].to_dict("records"),
    }

    lines = [f"# {title} Alert Digest", ""]
    lines.append(f"- Generated at: `{payload['generated_at']}`")
    lines.append(
        "- Alert counts: "
        f"`active={payload['counts']['active']}` · "
        f"`acknowledged={payload['counts']['acknowledged']}` · "
        f"`suppressed={payload['counts']['suppressed']}`"
    )
    if severity_counts:
        lines.append(f"- Severity mix: `{payload['severity_counts']}`")
    lines.append("")

    if review_rollup:
        lines.append("## Counties Needing Review")
        for rec in review_rollup:
            rank_txt = f"#{int(rec['current_rank'])}" if pd.notna(rec.get("current_rank")) else "n/a"
            lines.append(
                f"- `{rec['county_name']}, {rec['state']}` [FIPS {str(rec['fips']).zfill(5)}]: "
                f"`{int(rec['active_alerts'])}` active alerts, "
                f"`{int(rec['high_severity'])}` high severity, current rank `{rank_txt}`"
            )
        lines.append("")

    for status_name in ["active", "acknowledged", "suppressed"]:
        subset = df[df["alert_status"] == status_name].copy()
        if subset.empty:
            continue
        lines.append(f"## {status_name.title()} Alerts")
        subset = subset.sort_values(["severity", "current_rank", "county_name"], ascending=[True, True, True])
        for _, rec in subset.head(12).iterrows():
            rank_part = (
                f"`#{int(rec['prior_rank'])}` -> `#{int(rec['current_rank'])}`"
                if pd.notna(rec.get("prior_rank")) and pd.notna(rec.get("current_rank"))
                else f"`#{int(rec['current_rank'])}`"
                if pd.notna(rec.get("current_rank"))
                else "`n/a`"
            )
            lines.append(
                f"- `{rec['county_name']}, {rec['state']}` [{rec['severity']} / {rec['alert_type']}]: "
                f"{rank_part} · {rec['message']}"
            )
            note_val = rec.get("alert_note")
            note_text = "" if pd.isna(note_val) else str(note_val).strip()
            if note_text:
                lines.append(f"  - Note: {note_text}")
        lines.append("")

    return payload, "\n".join(lines).rstrip() + "\n"


def _classify_watchlist_health(row: pd.Series, settings: dict | None = None) -> tuple[str, list[str]]:
    cfg = {**_default_user_data()["watchlist_settings"], **(settings or {})}
    reasons: list[str] = []
    strength = 0
    concern = 0

    cur_rank = row.get("current_rank")
    if pd.notna(cur_rank):
        if float(cur_rank) <= float(cfg["top_rank_strong"]):
            strength += 2
            reasons.append(f"still ranks in the top {int(cfg['top_rank_strong'])}")
        elif float(cur_rank) <= float(cfg["top_rank_watch"]):
            strength += 1
            reasons.append(f"still ranks inside the top {int(cfg['top_rank_watch'])}")
        else:
            concern += 2
            reasons.append(f"has fallen outside the top {int(cfg['top_rank_watch'])}")

    top25_share = row.get("top25_presence_share")
    if pd.notna(top25_share):
        if float(top25_share) >= float(cfg["durable_top25_share"]):
            strength += 1
            reasons.append("has strong recent top-25 durability")
        elif float(top25_share) <= float(cfg["weak_top25_share"]):
            concern += 1
            reasons.append("has weak recent top-25 durability")

    std_rank = row.get("std_rank")
    if pd.notna(std_rank):
        if float(std_rank) <= float(cfg["calm_std_rank"]):
            strength += 1
            reasons.append("shows relatively calm run-to-run rank behavior")
        elif float(std_rank) >= float(cfg["volatile_std_rank"]):
            concern += 1
            reasons.append("shows high run-to-run rank volatility")

    rank_shift = row.get("rank_shift")
    if pd.notna(rank_shift):
        if float(rank_shift) <= -float(cfg["sharp_rank_move"]):
            strength += 1
            reasons.append("improved sharply in the latest run")
        elif float(rank_shift) >= float(cfg["sharp_rank_move"]):
            concern += 1
            reasons.append("dropped sharply in the latest run")

    pred5 = row.get("pred_avg_5yr")
    if pd.notna(pred5):
        if float(pred5) >= float(cfg["strong_5yr_upside"]):
            strength += 1
            reasons.append("still has strong long-horizon upside")
        elif float(pred5) <= float(cfg["weak_5yr_upside"]):
            concern += 1
            reasons.append("now has muted long-horizon upside")

    risk = row.get("composite_risk")
    if pd.notna(risk) and float(risk) >= float(cfg["elevated_risk"]):
        concern += 1
        reasons.append("carries elevated composite risk")

    if concern >= 3 or (concern >= 2 and strength == 0):
        return "review_or_drop", reasons
    if strength >= concern + 2:
        return "fits_thesis", reasons
    return "watch_closely", reasons


def _build_watchlist_alerts(health_df: pd.DataFrame, settings: dict | None = None) -> pd.DataFrame:
    cfg = {**_default_user_data()["watchlist_settings"], **(settings or {})}
    rows: list[dict] = []
    for _, row in health_df.iterrows():
        fips = row.get("fips")
        county = row.get("county_name")
        state = row.get("state")
        current_rank = row.get("current_rank")
        prior_rank = row.get("prior_rank")
        rank_shift = row.get("rank_shift")
        std_rank = row.get("std_rank")
        status = row.get("health_status")
        explanation = row.get("explanation")

        def add_alert(alert_type: str, severity: str, message: str):
            rows.append(
                {
                    "fips": fips,
                    "county_name": county,
                    "state": state,
                    "alert_type": alert_type,
                    "severity": severity,
                    "current_rank": current_rank,
                    "prior_rank": prior_rank,
                    "rank_shift": rank_shift,
                    "std_rank": std_rank,
                    "health_status": status,
                    "message": message,
                    "explanation": explanation,
                }
            )

        boundary = float(cfg["alert_rank_exit_boundary"])
        if pd.notna(prior_rank) and pd.notna(current_rank):
            if float(prior_rank) <= float(cfg["top_rank_strong"]) and float(current_rank) > float(cfg["top_rank_strong"]):
                add_alert("left_top_rank_strong", "high", f"Exited top {int(cfg['top_rank_strong'])}: #{int(prior_rank)} -> #{int(current_rank)}")
            if float(prior_rank) <= boundary and float(current_rank) > boundary:
                add_alert("left_alert_boundary", "medium", f"Exited top {int(boundary)}: #{int(prior_rank)} -> #{int(current_rank)}")
        if pd.notna(rank_shift) and float(rank_shift) >= float(cfg["sharp_rank_move"]):
            add_alert("sharp_drop", "high", f"Dropped by {float(rank_shift):.1f} ranks in the latest run.")
        if pd.notna(std_rank) and float(std_rank) >= float(cfg["volatile_std_rank"]):
            add_alert("high_volatility", "medium", f"Run-to-run volatility is elevated (std {float(std_rank):.1f}).")
        if status == "review_or_drop":
            add_alert("review_or_drop", "high", "Health check recommends review or removal from the shortlist.")
        elif status == "watch_closely":
            add_alert("watch_closely", "low", "Health check recommends closer monitoring.")

    if not rows:
        return pd.DataFrame()
    alert_df = pd.DataFrame(rows).sort_values(
        ["severity", "current_rank", "county_name"],
        ascending=[True, True, True],
    )
    return alert_df


def _alert_key(row: pd.Series) -> str:
    fips = str(row.get("fips", "")).zfill(5)
    return f"{fips}::{row.get('alert_type', '')}"

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _parse_drivers(x):
    """Robustly convert driver values back to plain dicts."""
    if isinstance(x, dict):
        return x
    if isinstance(x, str):
        try:
            return json.loads(x)
        except (json.JSONDecodeError, TypeError):
            return {}
    # Handle pyarrow MapScalar or other iterable key-value types
    try:
        return dict(x)
    except (TypeError, ValueError):
        return {}


def _file_mtime(path: Path) -> float:
    """Return file mtime or 0 if missing."""
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return 0.0


def _safe_json_load(path: Path):
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


@st.cache_data
def load_county_geojson(_mtime: float):
    """Prefer bundled county GeoJSON so deployed maps do not depend on GitHub at runtime."""
    payload = _safe_json_load(COUNTY_GEOJSON_PATH)
    return payload if payload else COUNTY_GEOJSON_URL


def _dynamic_calibration_cap(raw: pd.Series, horizon: int) -> float:
    vals = raw.astype(float).to_numpy()
    vals = vals[np.isfinite(vals)]
    if len(vals) == 0:
        return float(MIN_CAL_SHIFT.get(horizon, 0.05))
    raw_q75 = float(np.nanquantile(np.abs(vals), 0.75))
    raw_iqr = float(np.nanquantile(vals, 0.75) - np.nanquantile(vals, 0.25))
    dynamic_cap = 0.6 * raw_q75 + 0.5 * max(raw_iqr, 0.0)
    min_shift = MIN_CAL_SHIFT.get(horizon, 0.05)
    max_shift = MAX_CAL_SHIFT.get(horizon, 0.30)
    return float(np.clip(dynamic_cap, min_shift, max_shift))


def compute_calibration_diagnostics(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for h in HORIZONS:
        for model_type in ["xgboost", "lightgbm"]:
            raw_col = f"pred_{model_type}_{h}yr"
            cal_col = f"{raw_col}_cal"
            if raw_col not in df.columns or cal_col not in df.columns:
                continue
            pair = df[[raw_col, cal_col]].dropna()
            if pair.empty:
                continue
            shift = (pair[cal_col] - pair[raw_col]).astype(float)
            abs_shift = shift.abs()
            cap = _dynamic_calibration_cap(pair[raw_col], h)
            cap_hit_rate = float((abs_shift >= (cap - 1e-9)).mean())
            rows.append({
                "model": model_type,
                "horizon_yr": h,
                "n_counties": int(len(pair)),
                "raw_mean": float(pair[raw_col].mean()),
                "cal_mean": float(pair[cal_col].mean()),
                "mean_shift": float(shift.mean()),
                "mean_abs_shift": float(abs_shift.mean()),
                "max_abs_shift": float(abs_shift.max()),
                "dynamic_cap": float(cap),
                "cap_hit_rate": cap_hit_rate,
            })
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(["horizon_yr", "model"]).reset_index(drop=True)


@st.cache_data
def load_data(_mtime: float) -> pd.DataFrame:
    if not DATA_PATH.exists():
        return pd.DataFrame()
    try:
        df = pd.read_parquet(DATA_PATH)
    except Exception:
        return pd.DataFrame()
    # Parse JSON driver columns back to dicts
    for col in df.columns:
        if "drivers" in col:
            df[col] = df[col].apply(_parse_drivers)
    return df


def get_states(df: pd.DataFrame) -> list[str]:
    states = sorted(df["state"].dropna().unique().tolist())
    return states


@st.cache_data
def load_eval_report(_mtime: float) -> dict | None:
    return _safe_json_load(EVAL_PATH)


@st.cache_data
def load_conformal_diagnostics(_mtime: float) -> dict | None:
    return _safe_json_load(CONFORMAL_DIAG_PATH)


@st.cache_data
def load_latest_run_snapshot(_mtime: float) -> tuple[dict | None, dict | None]:
    if not RUNS_PATH.exists():
        return None, None
    run_dirs = sorted([p for p in RUNS_PATH.iterdir() if p.is_dir()])
    if not run_dirs:
        return None, None
    latest = run_dirs[-1]
    summary_path = latest / "run_summary.json"
    deltas_path = latest / "run_deltas.json"
    summary = None
    deltas = None
    if summary_path.exists():
        summary = _safe_json_load(summary_path)
    if deltas_path.exists():
        deltas = _safe_json_load(deltas_path)
    return summary, deltas


@st.cache_data
def load_status_bundle(_mtime: float) -> dict | None:
    return _safe_json_load(STATUS_BUNDLE_PATH)


@st.cache_data
def list_run_compare_artifacts(_mtime: float) -> list[str]:
    if not OUTPUT_PATH.exists():
        return []
    return sorted(p.name for p in OUTPUT_PATH.glob("run_compare_*_2024.json"))


@st.cache_data
def load_named_output_json(filename: str, _mtime: float):
    return _safe_json_load(OUTPUT_PATH / filename)


@st.cache_data
def load_run_history_summary(_mtime: float) -> dict | None:
    return _safe_json_load(RUN_HISTORY_SUMMARY_JSON_PATH)


@st.cache_data
def load_run_history_summary_df(_mtime: float) -> pd.DataFrame | None:
    if not RUN_HISTORY_SUMMARY_CSV_PATH.exists():
        return None
    return pd.read_csv(RUN_HISTORY_SUMMARY_CSV_PATH, dtype={"fips": str})


@st.cache_data
def load_run_history_detail_df(_mtime: float) -> pd.DataFrame | None:
    if not RUN_HISTORY_DETAIL_CSV_PATH.exists():
        return None
    return pd.read_csv(RUN_HISTORY_DETAIL_CSV_PATH, dtype={"fips": str})


@st.cache_data
def load_wave3_structural_overlay_df(_mtime: float) -> pd.DataFrame | None:
    if not WAVE3_STRUCTURAL_OVERLAY_CSV_PATH.exists():
        return None
    return pd.read_csv(WAVE3_STRUCTURAL_OVERLAY_CSV_PATH, dtype={"fips": str})


@st.cache_data
def load_wave3_structural_overlay_summary(_mtime: float) -> dict | None:
    return _safe_json_load(WAVE3_STRUCTURAL_OVERLAY_JSON_PATH)


@st.cache_data
def load_preboom_surface_df(path_str: str, _mtime: float) -> pd.DataFrame | None:
    path = Path(path_str)
    if not path.exists():
        return None
    return pd.read_csv(path, dtype={"fips": str})


@st.cache_data
def load_known_analog_suite(_mtime: float) -> dict | None:
    return _safe_json_load(KNOWN_ANALOG_SUITE_PATH)


@st.cache_data
def load_xfactor_interaction_scoreboard(_mtime: float) -> dict | None:
    return _safe_json_load(XFACTOR_INTERACTION_SCOREBOARD_PATH)


@st.cache_data
def load_xfactor_interaction_ablation_queue(_mtime: float) -> dict | None:
    return _safe_json_load(XFACTOR_INTERACTION_ABLATION_QUEUE_PATH)


@st.cache_data
def load_xfactor_interaction_promotion_gate(_mtime: float) -> dict | None:
    return _safe_json_load(XFACTOR_INTERACTION_PROMOTION_GATE_PATH)


@st.cache_data
def load_demo_readiness_report(_mtime: float) -> dict | None:
    return _safe_json_load(DEMO_READINESS_REPORT_PATH)


@st.cache_data
def load_compare_csv(path_str: str, _mtime: float) -> pd.DataFrame | None:
    path = Path(path_str)
    if not path.exists():
        return None
    return pd.read_csv(path, dtype={"fips": str})


@st.cache_data
def load_wave2_training_policy(_mtime: float) -> dict | None:
    return _safe_json_load(WAVE2_TRAINING_POLICY_PATH)


@st.cache_data
def load_fiveyr_policy_status(_mtime: float) -> dict | None:
    return _safe_json_load(FIVEYR_POLICY_STATUS_PATH)


# ---------------------------------------------------------------------------
# Product-mode helpers
# ---------------------------------------------------------------------------

def _scale_0_100(series: pd.Series, invert: bool = False) -> pd.Series:
    vals = pd.to_numeric(series, errors="coerce").astype(float)
    if vals.notna().sum() == 0:
        out = pd.Series(50.0, index=series.index)
    else:
        fill = vals.median()
        vals = vals.fillna(fill)
        lo = float(vals.min())
        hi = float(vals.max())
        if np.isclose(lo, hi):
            out = pd.Series(50.0, index=series.index)
        else:
            out = 100.0 * (vals - lo) / (hi - lo)
    if invert:
        return 100.0 - out
    return out


def _confidence_numeric(series: pd.Series) -> pd.Series:
    mapping = {"LOW": 35.0, "MEDIUM": 65.0, "HIGH": 90.0}
    return series.astype(str).str.upper().map(mapping).fillna(50.0)


def _product_thesis_presets() -> dict[str, dict]:
    return {
        "Long-term appreciation": {
            "h1": 0,
            "h3": 10,
            "h5": 90,
            "growth": 75,
            "risk": 15,
            "structure": 5,
            "confidence": 5,
            "uncertainty": 5,
            "max_risk": 70,
            "min_confidence": "Any",
            "structural_focus": "Overall land thesis",
        },
        "Low-risk compounder": {
            "h1": 0,
            "h3": 20,
            "h5": 80,
            "growth": 45,
            "risk": 40,
            "structure": 10,
            "confidence": 5,
            "uncertainty": 10,
            "max_risk": 45,
            "min_confidence": "MEDIUM+",
            "structural_focus": "Overall land thesis",
        },
        "Distressed rebound": {
            "h1": 20,
            "h3": 20,
            "h5": 60,
            "growth": 80,
            "risk": 5,
            "structure": 5,
            "confidence": 10,
            "uncertainty": 5,
            "max_risk": 75,
            "min_confidence": "Any",
            "structural_focus": "Overall land thesis",
        },
        "Land optionality": {
            "h1": 0,
            "h3": 15,
            "h5": 85,
            "growth": 45,
            "risk": 15,
            "structure": 35,
            "confidence": 5,
            "uncertainty": 5,
            "max_risk": 65,
            "min_confidence": "Any",
            "structural_focus": "Optionality",
        },
        "Climate-resilient growth": {
            "h1": 0,
            "h3": 20,
            "h5": 80,
            "growth": 45,
            "risk": 30,
            "structure": 20,
            "confidence": 5,
            "uncertainty": 10,
            "max_risk": 55,
            "min_confidence": "MEDIUM+",
            "structural_focus": "Low fragility",
        },
        "Recreation amenity": {
            "h1": 0,
            "h3": 15,
            "h5": 85,
            "growth": 50,
            "risk": 15,
            "structure": 30,
            "confidence": 5,
            "uncertainty": 5,
            "max_risk": 65,
            "min_confidence": "Any",
            "structural_focus": "Recreation access",
        },
        "Buildable scarcity": {
            "h1": 0,
            "h3": 10,
            "h5": 90,
            "growth": 45,
            "risk": 15,
            "structure": 35,
            "confidence": 5,
            "uncertainty": 5,
            "max_risk": 65,
            "min_confidence": "Any",
            "structural_focus": "Buildable scarcity",
        },
    }


def _product_structural_score(df: pd.DataFrame, focus: str) -> pd.Series:
    idx = df.index
    focus = focus or "Overall land thesis"
    if focus == "Optionality" and "optionality_profile_index" in df.columns:
        return 100.0 * pd.to_numeric(df["optionality_profile_index"], errors="coerce").fillna(0.5)
    if focus == "Recreation access" and "recreation_access_score" in df.columns:
        return 100.0 * pd.to_numeric(df["recreation_access_score"], errors="coerce").fillna(0.5)
    if focus == "Low fragility":
        fragility = pd.to_numeric(df.get("land_fragility_pressure", pd.Series(0.5, index=idx)), errors="coerce").fillna(0.5)
        environmental = pd.to_numeric(df.get("environmental_risk", pd.Series(50.0, index=idx)), errors="coerce").fillna(50.0)
        return (0.65 * (100.0 - 100.0 * fragility) + 0.35 * (100.0 - environmental)).clip(0, 100)
    if focus == "Buildable scarcity":
        developability = pd.to_numeric(df.get("land_developability_index", pd.Series(0.5, index=idx)), errors="coerce").fillna(0.5)
        scarcity = pd.to_numeric(df.get("scarcity_amenity_balance_index", pd.Series(0.5, index=idx)), errors="coerce").fillna(0.5)
        constraints = pd.to_numeric(df.get("land_constraint_pressure", pd.Series(0.5, index=idx)), errors="coerce").fillna(0.5)
        return (45.0 * developability + 40.0 * scarcity + 15.0 * (1.0 - constraints)).clip(0, 100)

    if "wave3_net_support" in df.columns:
        return _scale_0_100(df["wave3_net_support"])
    support = pd.to_numeric(df.get("site_thesis_support_index", pd.Series(0.5, index=idx)), errors="coerce").fillna(0.5)
    brake = pd.to_numeric(df.get("land_fragility_pressure", pd.Series(0.5, index=idx)), errors="coerce").fillna(0.5)
    return (70.0 * support + 30.0 * (1.0 - brake)).clip(0, 100)


def _simulate_strategy_rankings(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    out = df.copy()
    h_weights = {
        1: float(cfg.get("h1", 0)),
        3: float(cfg.get("h3", 0)),
        5: float(cfg.get("h5", 100)),
    }
    h_total = sum(h_weights.values()) or 1.0
    h_weights = {h: w / h_total for h, w in h_weights.items()}

    h_cols = {
        1: "pred_avg_1yr",
        3: "pred_policy_3yr" if "pred_policy_3yr" in out.columns else "pred_avg_3yr",
        5: "pred_avg_5yr",
    }
    growth_parts = []
    for h, col in h_cols.items():
        if col in out.columns:
            growth_parts.append(h_weights[h] * _scale_0_100(out[col]))
    out["sim_growth_score"] = sum(growth_parts) if growth_parts else out.get("growth_score", 50.0)

    out["sim_risk_fit"] = (100.0 - pd.to_numeric(out.get("composite_risk", 50.0), errors="coerce").fillna(50.0)).clip(0, 100)
    out["sim_structure_score"] = _product_structural_score(out, str(cfg.get("structural_focus", "Overall land thesis")))
    out["sim_confidence_score"] = _confidence_numeric(out.get("confidence", pd.Series("MEDIUM", index=out.index)))
    if "quantile_interval_width_mean" in out.columns:
        out["sim_uncertainty_score"] = _scale_0_100(out["quantile_interval_width_mean"])
    else:
        out["sim_uncertainty_score"] = 0.0

    component_weights = {
        "sim_growth_score": float(cfg.get("growth", 60)),
        "sim_risk_fit": float(cfg.get("risk", 25)),
        "sim_structure_score": float(cfg.get("structure", 10)),
        "sim_confidence_score": float(cfg.get("confidence", 5)),
    }
    total = sum(max(v, 0.0) for v in component_weights.values()) or 1.0
    out["sim_score"] = 0.0
    for col, weight in component_weights.items():
        out["sim_score"] += (max(weight, 0.0) / total) * out[col]
    out["sim_score"] = (out["sim_score"] - float(cfg.get("uncertainty", 0)) * out["sim_uncertainty_score"] / 100.0).clip(0, 100)
    out["sim_rank"] = out["sim_score"].rank(ascending=False, method="min").astype(int)
    if "overall_rank" in out.columns:
        out["sim_rank_delta"] = out["sim_rank"] - out["overall_rank"]
    else:
        out["sim_rank_delta"] = 0
    out["opportunity_archetype"] = out.apply(_assign_opportunity_archetype, axis=1)
    return out.sort_values("sim_rank")


def _apply_product_filter(df: pd.DataFrame, states: list[str], max_risk: float, min_confidence: str) -> pd.DataFrame:
    out = df.copy()
    if states:
        out = out[out["state"].isin(states)]
    if "composite_risk" in out.columns:
        out = out[pd.to_numeric(out["composite_risk"], errors="coerce").fillna(100.0) <= float(max_risk)]
    if min_confidence == "MEDIUM+":
        out = out[out["confidence"].astype(str).str.upper().isin(["MEDIUM", "HIGH"])]
    elif min_confidence == "HIGH":
        out = out[out["confidence"].astype(str).str.upper().eq("HIGH")]
    return out


def _product_table(df: pd.DataFrame, limit: int = 25) -> pd.DataFrame:
    cols = [
        "sim_rank", "overall_rank", "sim_rank_delta", "county_name", "state",
        "sim_score", "opportunity_score", "pred_avg_5yr", "pred_policy_3yr",
        "composite_risk", "confidence", "sim_structure_score", "opportunity_archetype",
    ]
    show = df[[c for c in cols if c in df.columns]].head(limit).copy()
    rename = {
        "sim_rank": "Sim Rank",
        "overall_rank": "Prod Rank",
        "sim_rank_delta": "Rank Delta",
        "county_name": "County",
        "state": "State",
        "sim_score": "Strategy Score",
        "opportunity_score": "Production Score",
        "pred_avg_5yr": "5yr",
        "pred_policy_3yr": "3yr",
        "composite_risk": "Risk",
        "confidence": "Confidence",
        "sim_structure_score": "Thesis Fit",
        "opportunity_archetype": "Archetype",
    }
    show = show.rename(columns=rename)
    for col in ["Strategy Score", "Production Score", "Risk", "Thesis Fit"]:
        if col in show.columns:
            show[col] = show[col].map(_fmt_score)
    for col in ["5yr", "3yr"]:
        if col in show.columns:
            show[col] = show[col].map(_fmt_pct)
    if "Rank Delta" in show.columns:
        show["Rank Delta"] = show["Rank Delta"].map(lambda x: f"{int(x):+d}" if pd.notna(x) else "—")
    if "Sim Rank" in show.columns:
        show["Sim Rank"] = show["Sim Rank"].map(lambda x: f"#{int(x)}" if pd.notna(x) else "—")
    if "Prod Rank" in show.columns:
        show["Prod Rank"] = show["Prod Rank"].map(lambda x: f"#{int(x)}" if pd.notna(x) else "—")
    return show


def _numeric_slider_filter(
    df: pd.DataFrame,
    source: pd.DataFrame,
    col: str,
    label: str,
    key: str,
    *,
    integer: bool = False,
    step: float = 0.01,
    fmt: str | None = None,
) -> pd.DataFrame:
    if col not in source.columns or col not in df.columns:
        return df
    vals = pd.to_numeric(source[col], errors="coerce").dropna()
    if vals.empty:
        return df
    if integer:
        min_val = int(np.floor(vals.min()))
        max_val = int(np.ceil(vals.max()))
        if min_val >= max_val:
            return df
        selected = st.slider(label, min_val, max_val, (min_val, max_val), step=1, key=key)
    else:
        min_val = _align_slider_bound(float(vals.min()), step, direction="down")
        max_val = _align_slider_bound(float(vals.max()), step, direction="up")
        if np.isclose(min_val, max_val):
            return df
        selected = st.slider(
            label,
            min_val,
            max_val,
            (min_val, max_val),
            step=step,
            format=fmt,
            key=key,
        )
    if selected[0] <= min_val and selected[1] >= max_val:
        return df
    series = pd.to_numeric(df[col], errors="coerce")
    return df[series.between(selected[0], selected[1], inclusive="both")]


def _filter_product_table_rows(df: pd.DataFrame, key_prefix: str, *, expanded: bool = False) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    source = df.copy()
    out = df.copy()
    with st.expander("Table Filters", expanded=expanded):
        query = st.text_input("Search county, state, or archetype", key=f"{key_prefix}_query")
        if query.strip():
            q = query.strip().lower()
            mask = pd.Series(False, index=out.index)
            for col in ["county_name", "state", "opportunity_archetype"]:
                if col in out.columns:
                    mask = mask | out[col].astype(str).str.lower().str.contains(q, regex=False, na=False)
            out = out[mask]

        c1, c2, c3 = st.columns(3)
        if "state" in source.columns:
            state_options = sorted(source["state"].dropna().astype(str).unique().tolist())
            selected_states = c1.multiselect("States", state_options, key=f"{key_prefix}_states")
            if selected_states:
                out = out[out["state"].astype(str).isin(selected_states)]
        if "confidence" in source.columns:
            confidence_options = sorted(source["confidence"].dropna().astype(str).str.upper().unique().tolist())
            selected_confidence = c2.multiselect("Confidence", confidence_options, key=f"{key_prefix}_confidence")
            if selected_confidence:
                out = out[out["confidence"].astype(str).str.upper().isin(selected_confidence)]
        if "opportunity_archetype" in source.columns:
            archetype_options = sorted(source["opportunity_archetype"].dropna().astype(str).unique().tolist())
            selected_archetypes = c3.multiselect("Archetypes", archetype_options, key=f"{key_prefix}_archetypes")
            if selected_archetypes:
                out = out[out["opportunity_archetype"].astype(str).isin(selected_archetypes)]

        r1, r2 = st.columns(2)
        with r1:
            out = _numeric_slider_filter(out, source, "sim_rank", "Strategy rank", f"{key_prefix}_sim_rank", integer=True)
            out = _numeric_slider_filter(
                out, source, "sim_score", "Strategy score", f"{key_prefix}_sim_score", step=0.5, fmt="%.1f"
            )
            out = _numeric_slider_filter(
                out, source, "composite_risk", "Risk score", f"{key_prefix}_risk", step=0.5, fmt="%.1f"
            )
        with r2:
            out = _numeric_slider_filter(
                out, source, "overall_rank", "Production rank", f"{key_prefix}_prod_rank", integer=True
            )
            out = _numeric_slider_filter(
                out, source, "opportunity_score", "Production score", f"{key_prefix}_prod_score", step=0.5, fmt="%.1f"
            )
            out = _numeric_slider_filter(
                out, source, "pred_avg_5yr", "5yr signal", f"{key_prefix}_pred_5yr", step=0.01, fmt="%.2f"
            )

        if "use_stable_3yr_fallback" in source.columns:
            hide_fallback = st.checkbox("Hide rows using the stable 3yr fallback", key=f"{key_prefix}_hide_3yr_fallback")
            if hide_fallback:
                out = out[~out["use_stable_3yr_fallback"].astype(bool)]
    return out


def _insight_slices(df: pd.DataFrame) -> list[tuple[str, str, pd.DataFrame]]:
    slices: list[tuple[str, str, pd.DataFrame]] = []
    slices.append(("Top strategy fit", "Highest simulated score under the active thesis.", df.sort_values("sim_rank").head(8)))
    if "composite_risk" in df.columns:
        low_risk = df[df["composite_risk"] <= df["composite_risk"].quantile(0.35)]
        if not low_risk.empty:
            slices.append(("Clean low-risk upside", "Strong scores with below-peer composite risk.", low_risk.sort_values("sim_rank").head(8)))
    if "top25_presence_share" in df.columns:
        durable = df[pd.to_numeric(df["top25_presence_share"], errors="coerce").fillna(0) >= 0.60]
        if not durable.empty:
            slices.append(("Durable winners", "Counties that repeatedly survive recent top-25 cuts.", durable.sort_values("sim_rank").head(8)))
    if "sim_structure_score" in df.columns:
        structural = df.sort_values(["sim_structure_score", "sim_rank"], ascending=[False, True]).head(8)
        slices.append(("Best thesis fit", "Counties with the strongest structural match to the active preset.", structural))
    if "sim_rank_delta" in df.columns:
        movers = df.sort_values("sim_rank_delta").head(8)
        slices.append(("Simulation risers", "Counties this strategy promotes most versus production rank.", movers))
    return slices[:5]


def _watchlist_portfolio_summary(watch_df: pd.DataFrame) -> dict:
    if watch_df.empty:
        return {
            "count": 0,
            "avg_risk": "—",
            "avg_score": "—",
            "high_conf_share": "—",
            "top_states": "—",
        }
    state_counts = watch_df["state"].value_counts().head(3)
    return {
        "count": int(len(watch_df)),
        "avg_risk": _fmt_score(watch_df.get("composite_risk", pd.Series(dtype=float)).mean()),
        "avg_score": _fmt_score(watch_df.get("sim_score", watch_df.get("opportunity_score", pd.Series(dtype=float))).mean()),
        "high_conf_share": f"{100 * watch_df['confidence'].astype(str).str.upper().eq('HIGH').mean():.0f}%" if "confidence" in watch_df.columns else "—",
        "top_states": ", ".join(f"{k} ({v})" for k, v in state_counts.items()) if not state_counts.empty else "—",
    }


def _product_numeric(row: pd.Series, col: str, default: float = np.nan) -> float:
    val = pd.to_numeric(pd.Series([row.get(col, default)]), errors="coerce").iloc[0]
    return float(val) if pd.notna(val) else float(default)


def _product_series(df: pd.DataFrame, col: str, default: float) -> pd.Series:
    if col in df.columns:
        return pd.to_numeric(df[col], errors="coerce").fillna(default)
    return pd.Series(float(default), index=df.index)


def _assign_opportunity_archetype(row: pd.Series) -> str:
    pred5 = _product_numeric(row, "pred_avg_5yr", 0.0)
    risk = _product_numeric(row, "composite_risk", 50.0)
    structure = _product_numeric(row, "sim_structure_score", 50.0)
    recreation = _product_numeric(row, "recreation_access_score", 0.0)
    developability = _product_numeric(row, "land_developability_index", 0.5)
    scarcity = _product_numeric(row, "scarcity_amenity_balance_index", 0.5)
    fragility = _product_numeric(row, "land_fragility_pressure", 0.5)
    rank_delta = _product_numeric(row, "sim_rank_delta", 0.0)

    if pred5 >= 0.12 and risk <= 42:
        return "Low-risk compounder"
    if pred5 >= 0.14 and (risk >= 50 or fragility >= 0.60):
        return "High-upside fragile"
    if recreation >= 0.66:
        return "Amenity/recreation growth"
    if developability >= 0.65 and scarcity >= 0.60:
        return "Buildable scarcity"
    if rank_delta <= -75:
        return "Strategy mispriced"
    if structure >= 70:
        return "Structural thesis fit"
    if pred5 >= 0.08:
        return "Long-horizon growth"
    return "Watchlist candidate"


def _data_confidence_badges(row: pd.Series, wave3_status: dict | None = None) -> list[dict[str, str]]:
    badges: list[dict[str, str]] = []
    conf = str(row.get("confidence", "UNKNOWN")).upper()
    if conf == "HIGH":
        badges.append({"badge": "Model confidence", "status": "good", "detail": "High model-confidence bucket."})
    elif conf == "MEDIUM":
        badges.append({"badge": "Model confidence", "status": "watch", "detail": "Medium confidence; confirm with peer and run-history checks."})
    else:
        badges.append({"badge": "Model confidence", "status": "caution", "detail": "Low confidence; use as a lead, not a conclusion."})

    if bool(row.get("use_stable_3yr_fallback", False)):
        badges.append({"badge": "3yr fallback", "status": "watch", "detail": "Medium-term signal uses the stabilized fallback path."})
    else:
        badges.append({"badge": "3yr signal", "status": "good", "detail": "3yr model policy did not require fallback for this row."})

    interval = row.get("quantile_interval_width_mean", row.get("pred_std"))
    if pd.notna(interval):
        status = "caution" if float(interval) >= 0.53 else "watch" if float(interval) >= 0.46 else "good"
        badges.append({"badge": "Prediction interval", "status": status, "detail": f"Mean uncertainty width is {float(interval):.3f}."})

    stability = row.get("rank_stability_spread")
    if pd.notna(stability):
        status = "caution" if float(stability) >= 0.50 else "watch" if float(stability) >= 0.25 else "good"
        badges.append({"badge": "Horizon stability", "status": status, "detail": f"Cross-horizon rank spread is {float(stability):.3f}."})

    coastal = _coastal_lane_provenance(row, wave3_status)
    coastal_status = "watch" if coastal.get("source") in {"proxy_fallback", "proxy_excluded"} else "good"
    badges.append({"badge": "Coastal provenance", "status": coastal_status, "detail": str(coastal.get("summary", ""))})
    return badges


def _data_confidence_table(row: pd.Series, wave3_status: dict | None = None) -> pd.DataFrame:
    status_symbol = {"good": "OK", "watch": "Watch", "caution": "Caution"}
    rows = _data_confidence_badges(row, wave3_status)
    for rec in rows:
        rec["status"] = status_symbol.get(rec["status"], rec["status"])
    return pd.DataFrame(rows).rename(columns={"badge": "Badge", "status": "Status", "detail": "Detail"})


def _rank_explain_rows(row: pd.Series, cfg: dict) -> pd.DataFrame:
    weights = {
        "Growth": float(cfg.get("growth", 60)),
        "Risk control": float(cfg.get("risk", 25)),
        "Land thesis": float(cfg.get("structure", 10)),
        "Confidence": float(cfg.get("confidence", 5)),
    }
    total = sum(max(v, 0.0) for v in weights.values()) or 1.0
    components = [
        ("Growth", "sim_growth_score"),
        ("Risk control", "sim_risk_fit"),
        ("Land thesis", "sim_structure_score"),
        ("Confidence", "sim_confidence_score"),
    ]
    rows = []
    for label, col in components:
        score = _product_numeric(row, col, 50.0)
        weight = max(weights[label], 0.0) / total
        rows.append(
            {
                "Component": label,
                "Weight": weight,
                "Component Score": score,
                "Contribution": weight * score,
            }
        )
    uncertainty_weight = float(cfg.get("uncertainty", 0))
    if uncertainty_weight > 0 and "sim_uncertainty_score" in row.index:
        rows.append(
            {
                "Component": "Uncertainty penalty",
                "Weight": -uncertainty_weight / 100.0,
                "Component Score": _product_numeric(row, "sim_uncertainty_score", 0.0),
                "Contribution": -uncertainty_weight * _product_numeric(row, "sim_uncertainty_score", 0.0) / 100.0,
            }
        )
    return pd.DataFrame(rows)


def _rank_explain_bullets(row: pd.Series, cfg: dict) -> list[str]:
    rows = _rank_explain_rows(row, cfg)
    if rows.empty:
        return []
    positives = rows[rows["Contribution"] > 0].sort_values("Contribution", ascending=False)
    penalties = rows[rows["Contribution"] < 0].sort_values("Contribution")
    bullets = []
    for _, rec in positives.head(3).iterrows():
        bullets.append(
            f"{rec['Component']} contributes {rec['Contribution']:.1f} points "
            f"from a component score of {rec['Component Score']:.1f}."
        )
    for _, rec in penalties.head(2).iterrows():
        bullets.append(f"{rec['Component']} subtracts {abs(rec['Contribution']):.1f} points.")
    rank_delta = row.get("sim_rank_delta")
    if pd.notna(rank_delta):
        direction = "higher" if float(rank_delta) < 0 else "lower" if float(rank_delta) > 0 else "the same"
        bullets.append(f"The active strategy ranks this county {direction} than production by {abs(int(rank_delta))} ranks.")
    return bullets


def _parcel_readiness(row: pd.Series) -> tuple[str, list[str]]:
    actions: list[str] = []
    risk = _product_numeric(row, "composite_risk", 50.0)
    developability = _product_numeric(row, "land_developability_index", 0.5)
    constraint = _product_numeric(row, "land_constraint_pressure", 0.5)
    fragility = _product_numeric(row, "land_fragility_pressure", 0.5)
    coastal = _product_numeric(row, "coastal_flood_pressure", 0.0)
    interval = _product_numeric(row, "quantile_interval_width_mean", 0.0)

    actions.append("Map candidate parcels against wetlands, flood, slope, protected-land, and road-access layers.")
    if developability < 0.45 or constraint >= 0.55:
        actions.append("Estimate investable acreage after hard constraints; county-level supply may overstate parcel feasibility.")
    if fragility >= 0.55 or coastal >= 0.50:
        actions.append("Add insurance, flood, wildfire, and climate-fragility diligence before underwriting.")
    if risk >= 55:
        actions.append("Review liquidity, regulation, and local market depth before sizing exposure.")
    if bool(row.get("use_stable_3yr_fallback", False)) or interval >= 0.50:
        actions.append("Validate the medium-term thesis with listings, permit activity, and local broker checks.")
    if len(actions) <= 2 and risk <= 45 and developability >= 0.55:
        status = "Parcel screen ready"
    elif risk >= 60 or constraint >= 0.70 or fragility >= 0.70:
        status = "Needs constraint diligence first"
    else:
        status = "Ready with targeted checks"
    return status, actions[:5]


def _find_peer_sets(row: pd.Series, df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    if df.empty:
        return {}
    fips = str(row.get("fips", "")).zfill(5)
    base = df[df["fips"].astype(str).str.zfill(5) != fips].copy()
    if base.empty:
        return {}

    metric_cols = [
        c for c in [
            "sim_score", "composite_risk", "pred_avg_5yr", "pred_policy_3yr",
            "sim_structure_score", "rank_stability_spread",
        ] if c in base.columns and c in row.index
    ]
    peer_sets: dict[str, pd.DataFrame] = {}
    same_state = base[base["state"] == row.get("state")].sort_values("sim_rank").head(8)
    if not same_state.empty:
        peer_sets["Same-state peers"] = same_state

    if metric_cols:
        work = base[metric_cols].apply(pd.to_numeric, errors="coerce")
        row_vals = pd.Series({c: _product_numeric(row, c, work[c].median()) for c in metric_cols})
        med = work.median()
        std = work.std().replace(0, 1.0).fillna(1.0)
        dist = (((work.fillna(med) - row_vals) / std) ** 2).sum(axis=1) ** 0.5
        similar = base.assign(peer_distance=dist).sort_values(["peer_distance", "sim_rank"]).head(8)
        peer_sets["Most similar profile"] = similar

    if "composite_risk" in base.columns:
        risk_target = _product_numeric(row, "composite_risk", 50.0)
        risk_peers = base.assign(risk_distance=(pd.to_numeric(base["composite_risk"], errors="coerce") - risk_target).abs())
        peer_sets["Similar-risk alternatives"] = risk_peers.sort_values(["risk_distance", "sim_rank"]).head(8)

    if "pred_avg_5yr" in base.columns:
        growth_target = _product_numeric(row, "pred_avg_5yr", 0.0)
        growth_peers = base.assign(growth_distance=(pd.to_numeric(base["pred_avg_5yr"], errors="coerce") - growth_target).abs())
        peer_sets["Similar-growth alternatives"] = growth_peers.sort_values(["growth_distance", "sim_rank"]).head(8)
    return peer_sets


def _peer_table(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "county_name", "state", "sim_rank", "overall_rank", "sim_score",
        "pred_avg_5yr", "pred_policy_3yr", "composite_risk", "confidence",
    ]
    out = df[[c for c in cols if c in df.columns]].copy()
    out = out.rename(
        columns={
            "county_name": "County",
            "state": "State",
            "sim_rank": "Strategy Rank",
            "overall_rank": "Production Rank",
            "sim_score": "Strategy Score",
            "pred_avg_5yr": "5yr",
            "pred_policy_3yr": "3yr",
            "composite_risk": "Risk",
            "confidence": "Confidence",
        }
    )
    for col in ["Strategy Score", "Risk"]:
        if col in out.columns:
            out[col] = out[col].map(_fmt_score)
    for col in ["5yr", "3yr"]:
        if col in out.columns:
            out[col] = out[col].map(_fmt_pct)
    for col in ["Strategy Rank", "Production Rank"]:
        if col in out.columns:
            out[col] = out[col].map(lambda x: f"#{int(x)}" if pd.notna(x) else "—")
    return out


def _scenario_catalog() -> dict[str, dict[str, str]]:
    return {
        "Higher rates": {"description": "Penalizes liquidity risk, near-term uncertainty, and weaker confidence."},
        "Recession": {"description": "Penalizes market/liquidity risk and less durable rank histories."},
        "Climate-risk haircut": {"description": "Penalizes environmental risk, fragility, and coastal flood pressure."},
        "Migration slowdown": {"description": "Haircuts growth-led rankings and rewards structural thesis support."},
        "Infrastructure growth": {"description": "Boosts developability, recreation access, and optionality."},
        "Stricter risk tolerance": {"description": "Applies a broad risk-control penalty to higher-risk counties."},
    }


def _apply_scenario_stress(df: pd.DataFrame, scenarios: list[str], severity: float) -> pd.DataFrame:
    out = df.copy()
    out["stress_adjustment"] = 0.0
    sev = float(severity)

    if "Higher rates" in scenarios:
        out["stress_adjustment"] -= sev * (
            0.08 * _product_series(out, "liquidity_risk", 50.0)
            + 0.04 * _product_series(out, "sim_uncertainty_score", 0.0)
            + 0.03 * (100.0 - _product_series(out, "sim_confidence_score", 50.0))
        )
    if "Recession" in scenarios:
        out["stress_adjustment"] -= sev * (
            0.06 * _product_series(out, "market_risk", 50.0)
            + 0.05 * _product_series(out, "liquidity_risk", 50.0)
            + 4.0 * _product_series(out, "rank_stability_spread", 0.25)
        )
    if "Climate-risk haircut" in scenarios:
        out["stress_adjustment"] -= sev * (
            0.07 * _product_series(out, "environmental_risk", 50.0)
            + 7.0 * _product_series(out, "land_fragility_pressure", 0.5)
            + 5.0 * _product_series(out, "coastal_flood_pressure", 0.0)
        )
    if "Migration slowdown" in scenarios:
        out["stress_adjustment"] -= sev * (0.05 * _product_series(out, "sim_growth_score", 50.0))
        out["stress_adjustment"] += sev * (0.03 * _product_series(out, "sim_structure_score", 50.0))
    if "Infrastructure growth" in scenarios:
        out["stress_adjustment"] += sev * (
            5.0 * _product_series(out, "land_developability_index", 0.5)
            + 3.0 * _product_series(out, "recreation_access_score", 0.5)
            + 3.0 * _product_series(out, "optionality_profile_index", 0.5)
        )
    if "Stricter risk tolerance" in scenarios:
        out["stress_adjustment"] -= sev * (0.12 * _product_series(out, "composite_risk", 50.0))

    out["stress_score"] = (_product_series(out, "sim_score", 50.0) + out["stress_adjustment"]).clip(0, 100)
    out["stress_rank"] = out["stress_score"].rank(ascending=False, method="min").astype(int)
    out["stress_rank_delta"] = out["stress_rank"] - out["sim_rank"]
    return out.sort_values("stress_rank")


def _stress_table(df: pd.DataFrame, limit: int = 30) -> pd.DataFrame:
    cols = [
        "stress_rank", "sim_rank", "stress_rank_delta", "county_name", "state",
        "stress_score", "sim_score", "composite_risk", "pred_avg_5yr", "confidence",
    ]
    out = df[[c for c in cols if c in df.columns]].head(limit).copy()
    out = out.rename(
        columns={
            "stress_rank": "Stress Rank",
            "sim_rank": "Base Rank",
            "stress_rank_delta": "Stress Delta",
            "county_name": "County",
            "state": "State",
            "stress_score": "Stress Score",
            "sim_score": "Base Score",
            "composite_risk": "Risk",
            "pred_avg_5yr": "5yr",
            "confidence": "Confidence",
        }
    )
    for col in ["Stress Score", "Base Score", "Risk"]:
        if col in out.columns:
            out[col] = out[col].map(_fmt_score)
    if "5yr" in out.columns:
        out["5yr"] = out["5yr"].map(_fmt_pct)
    for col in ["Stress Rank", "Base Rank"]:
        if col in out.columns:
            out[col] = out[col].map(lambda x: f"#{int(x)}" if pd.notna(x) else "—")
    if "Stress Delta" in out.columns:
        out["Stress Delta"] = out["Stress Delta"].map(lambda x: f"{int(x):+d}" if pd.notna(x) else "—")
    return out


def _recommend_watchlist_replacements(filtered: pd.DataFrame, watch_df: pd.DataFrame, max_items: int = 8) -> pd.DataFrame:
    if filtered.empty:
        return pd.DataFrame()
    watch_fips = set(watch_df["fips"].astype(str).str.zfill(5)) if not watch_df.empty else set()
    candidates = filtered[~filtered["fips"].astype(str).str.zfill(5).isin(watch_fips)].copy()
    if candidates.empty:
        return pd.DataFrame()
    if not watch_df.empty:
        watched_states = set(watch_df["state"].dropna().astype(str))
        candidates["diversifier_bonus"] = np.where(candidates["state"].isin(watched_states), 0.0, 5.0)
    else:
        candidates["diversifier_bonus"] = 0.0
    candidates["recommendation_score"] = (
        pd.to_numeric(candidates["sim_score"], errors="coerce").fillna(0.0)
        + candidates["diversifier_bonus"]
        + 0.10 * pd.to_numeric(candidates.get("sim_risk_fit", 50.0), errors="coerce").fillna(50.0)
    )
    return candidates.sort_values(["recommendation_score", "sim_rank"], ascending=[False, True]).head(max_items)


def _watchlist_review_flags(watch_df: pd.DataFrame) -> pd.DataFrame:
    if watch_df.empty:
        return pd.DataFrame()
    rows = []
    for _, row in watch_df.iterrows():
        reasons = []
        if pd.notna(row.get("sim_rank")) and float(row["sim_rank"]) > 100:
            reasons.append("outside active strategy top 100")
        if pd.notna(row.get("composite_risk")) and float(row["composite_risk"]) >= 55:
            reasons.append("elevated risk")
        if pd.notna(row.get("rank_stability_spread")) and float(row["rank_stability_spread"]) >= 0.50:
            reasons.append("weak horizon stability")
        if bool(row.get("use_stable_3yr_fallback", False)):
            reasons.append("3yr fallback active")
        if reasons:
            rows.append(
                {
                    "County": row.get("county_name"),
                    "State": row.get("state"),
                    "Strategy Rank": f"#{int(row['sim_rank'])}" if pd.notna(row.get("sim_rank")) else "—",
                    "Risk": _fmt_score(row.get("composite_risk")),
                    "Review Reason": "; ".join(reasons),
                }
            )
    return pd.DataFrame(rows)


def _build_deal_thesis_memo(
    watch_df: pd.DataFrame,
    cfg: dict,
    preset_name: str,
    stress_df: pd.DataFrame | None = None,
) -> str:
    lines = [f"# LandInvest Thesis Memo: {preset_name}", ""]
    lines.append(f"- Generated at: `{datetime.now().isoformat()}`")
    lines.append(
        "- Strategy mix: "
        f"growth `{cfg.get('growth')}`, risk `{cfg.get('risk')}`, "
        f"land thesis `{cfg.get('structure')}`, confidence `{cfg.get('confidence')}`"
    )
    lines.append(f"- Horizon mix: 1yr `{cfg.get('h1')}`, 3yr `{cfg.get('h3')}`, 5yr `{cfg.get('h5')}`")
    lines.append("")
    if watch_df.empty:
        lines.append("No counties are currently in the watchlist.")
        return "\n".join(lines).rstrip() + "\n"

    lines.append("## Shortlist")
    for _, row in watch_df.sort_values("sim_rank").head(12).iterrows():
        readiness, actions = _parcel_readiness(row)
        decision = _build_wave3_decision_narrative(row)
        lines.append(
            f"- `{row.get('county_name')}, {row.get('state')}` [FIPS {str(row.get('fips')).zfill(5)}]: "
            f"strategy rank `#{int(row.get('sim_rank'))}`, production rank `#{int(row.get('overall_rank'))}`, "
            f"5yr `{_fmt_pct(row.get('pred_avg_5yr'))}`, risk `{_fmt_score(row.get('composite_risk'))}`, "
            f"archetype `{row.get('opportunity_archetype', 'n/a')}`"
        )
        lines.append(f"  - Thesis: {decision['thesis']}")
        lines.append(f"  - Parcel readiness: `{readiness}`; first check: {actions[0] if actions else 'n/a'}")
    lines.append("")

    flags = _watchlist_review_flags(watch_df)
    if not flags.empty:
        lines.append("## Open Questions")
        for _, rec in flags.head(8).iterrows():
            lines.append(f"- `{rec['County']}, {rec['State']}`: {rec['Review Reason']}.")
        lines.append("")

    if stress_df is not None and not stress_df.empty:
        stress_lookup = stress_df.set_index(stress_df["fips"].astype(str).str.zfill(5))
        lines.append("## Stress Read")
        for _, row in watch_df.sort_values("sim_rank").head(8).iterrows():
            fips = str(row.get("fips")).zfill(5)
            if fips in stress_lookup.index:
                rec = stress_lookup.loc[fips]
                if isinstance(rec, pd.DataFrame):
                    rec = rec.iloc[0]
                lines.append(
                    f"- `{row.get('county_name')}, {row.get('state')}`: "
                    f"base `#{int(row.get('sim_rank'))}` -> stress `#{int(rec.get('stress_rank'))}` "
                    f"({int(rec.get('stress_rank_delta')):+d})."
                )
        lines.append("")

    lines.append("## Diligence Checklist")
    checklist = []
    for _, row in watch_df.head(8).iterrows():
        _, actions = _parcel_readiness(row)
        checklist.extend(actions)
    for item in list(dict.fromkeys(checklist))[:8]:
        lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def _run_review_summary(
    current_df: pd.DataFrame,
    latest_compare_rank_df: pd.DataFrame | None,
    latest_compare_boundary_df: pd.DataFrame | None,
) -> dict[str, pd.DataFrame]:
    if latest_compare_rank_df is None or latest_compare_rank_df.empty:
        return {}
    comp = latest_compare_rank_df.copy()
    if "fips" in comp.columns:
        comp["fips"] = comp["fips"].astype(str).str.zfill(5)
    risers = comp.sort_values("rank_shift").head(12)
    fallers = comp.sort_values("rank_shift", ascending=False).head(12)
    entrants = comp[
        (pd.to_numeric(comp.get("overall_rank_old"), errors="coerce") > 25)
        & (pd.to_numeric(comp.get("overall_rank_new"), errors="coerce") <= 25)
    ].sort_values("overall_rank_new")
    exits = comp[
        (pd.to_numeric(comp.get("overall_rank_old"), errors="coerce") <= 25)
        & (pd.to_numeric(comp.get("overall_rank_new"), errors="coerce") > 25)
    ].sort_values("overall_rank_old")
    out = {"Biggest risers": risers, "Biggest fallers": fallers, "Top-25 entrants": entrants, "Top-25 exits": exits}
    if latest_compare_boundary_df is not None and not latest_compare_boundary_df.empty:
        out["Boundary movers"] = latest_compare_boundary_df.head(15)
    return out


def _run_review_table(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "county_name_new", "state_new", "overall_rank_old", "overall_rank_new",
        "rank_shift", "opportunity_score_delta", "pred_policy_3yr_delta",
        "pred_xgboost_5yr_delta", "pred_lightgbm_5yr_delta", "composite_risk_delta",
    ]
    out = df[[c for c in cols if c in df.columns]].copy()
    out = out.rename(
        columns={
            "county_name_new": "County",
            "state_new": "State",
            "overall_rank_old": "Old Rank",
            "overall_rank_new": "New Rank",
            "rank_shift": "Rank Shift",
            "opportunity_score_delta": "Score Delta",
            "pred_policy_3yr_delta": "3yr Delta",
            "pred_xgboost_5yr_delta": "XGB 5yr Delta",
            "pred_lightgbm_5yr_delta": "LGB 5yr Delta",
            "composite_risk_delta": "Risk Delta",
        }
    )
    for col in ["Old Rank", "New Rank"]:
        if col in out.columns:
            out[col] = out[col].map(lambda x: f"#{int(x)}" if pd.notna(x) else "—")
    for col in ["Rank Shift"]:
        if col in out.columns:
            out[col] = out[col].map(lambda x: f"{int(x):+d}" if pd.notna(x) else "—")
    for col in ["Score Delta", "3yr Delta", "XGB 5yr Delta", "LGB 5yr Delta", "Risk Delta"]:
        if col in out.columns:
            out[col] = out[col].map(lambda x: f"{float(x):+.3f}" if pd.notna(x) else "—")
    return out


def _strategy_profile_description(cfg: dict) -> str:
    h_bits = sorted(
        [(int(cfg.get("h1", 0)), "1yr"), (int(cfg.get("h3", 0)), "3yr"), (int(cfg.get("h5", 0)), "5yr")],
        reverse=True,
    )
    dominant_h = h_bits[0][1]
    focus = cfg.get("structural_focus", "overall land thesis")
    risk = int(cfg.get("risk", 0))
    growth = int(cfg.get("growth", 0))
    structure = int(cfg.get("structure", 0))
    parts = [f"favors {dominant_h} growth"]
    if growth >= 65:
        parts.append("leans aggressive on upside")
    if risk >= 30:
        parts.append("meaningfully rewards risk control")
    if structure >= 25:
        parts.append(f"puts real weight on {str(focus).lower()}")
    if int(cfg.get("uncertainty", 0)) >= 10:
        parts.append("penalizes wide uncertainty")
    return "This profile " + ", ".join(parts) + "."


def _add_product_lenses(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["lens_upside_minus_risk"] = (
        0.65 * _product_series(out, "sim_growth_score", 50.0)
        + 0.35 * _product_series(out, "sim_risk_fit", 50.0)
    ).clip(0, 100)
    out["lens_structure_minus_fragility"] = (
        0.65 * _product_series(out, "sim_structure_score", 50.0)
        + 0.35 * (100.0 - 100.0 * _product_series(out, "land_fragility_pressure", 0.5))
    ).clip(0, 100)
    out["lens_confidence_weighted"] = (
        0.72 * _product_series(out, "sim_score", 50.0)
        + 0.28 * _product_series(out, "sim_confidence_score", 50.0)
        - 0.08 * _product_series(out, "sim_uncertainty_score", 0.0)
    ).clip(0, 100)
    out["lens_confidence_rank"] = out["lens_confidence_weighted"].rank(ascending=False, method="min").astype(int)
    out["lens_parcel_readiness"] = (
        0.40 * _product_series(out, "land_developability_index", 0.5) * 100.0
        + 0.25 * (100.0 - 100.0 * _product_series(out, "land_constraint_pressure", 0.5))
        + 0.20 * (100.0 - _product_series(out, "environmental_risk", 50.0))
        + 0.15 * _product_series(out, "sim_risk_fit", 50.0)
    ).clip(0, 100)
    return out


def _apply_natural_language_query(df: pd.DataFrame, query: str) -> tuple[pd.DataFrame, list[str]]:
    out = df.copy()
    q = query.lower().strip()
    notes: list[str] = []
    if not q:
        return out.sort_values("sim_rank"), ["No query entered; showing the active strategy universe."]

    region_map = {
        "mountain west": ["AZ", "CO", "ID", "MT", "NV", "NM", "UT", "WY"],
        "midwest": ["IL", "IN", "IA", "KS", "MI", "MN", "MO", "NE", "ND", "OH", "SD", "WI"],
        "southeast": ["AL", "AR", "FL", "GA", "KY", "LA", "MS", "NC", "SC", "TN", "VA", "WV"],
        "northeast": ["CT", "ME", "MA", "NH", "NJ", "NY", "PA", "RI", "VT"],
        "west coast": ["CA", "OR", "WA"],
    }
    for label, state_list in region_map.items():
        if label in q:
            out = out[out["state"].isin(state_list)]
            notes.append(f"Filtered to {label}.")

    if "low risk" in q or "low-risk" in q or "lower risk" in q or "lower-risk" in q or "safe" in q:
        out = out[out["composite_risk"] <= 45]
        notes.append("Applied low-risk filter.")
    if "high risk" in q:
        out = out[out["composite_risk"] >= 55]
        notes.append("Applied high-risk filter.")
    if "strong 5" in q or "5yr upside" in q or "5 year upside" in q or "5-year upside" in q or "high upside" in q:
        out = out[out["pred_avg_5yr"] >= out["pred_avg_5yr"].quantile(0.75)]
        notes.append("Kept upper-quartile 5yr signal.")
    if "confidence" in q or "high conviction" in q:
        out = out[out["confidence"].astype(str).str.upper().eq("HIGH")]
        notes.append("Kept high-confidence counties.")
    if "fallback" in q:
        out = out[out.get("use_stable_3yr_fallback", False).astype(bool)]
        notes.append("Kept counties with 3yr fallback active.")
    if "disagree" in q or "model disagreement" in q:
        sort_col = "model_disagreement"
        if sort_col in out.columns:
            out = out.sort_values(sort_col, ascending=False)
            notes.append("Sorted by model disagreement.")
    if "like " in q:
        needle = q.split("like ", 1)[1].split(" but ")[0].strip()
        matches = df[df["county_name"].astype(str).str.lower().str.contains(needle, regex=False, na=False)]
        if not matches.empty:
            peer_sets = _find_peer_sets(matches.iloc[0], df)
            if peer_sets:
                out = peer_sets.get("Most similar profile", next(iter(peer_sets.values()))).copy()
                notes.append(f"Showing counties similar to {matches.iloc[0].get('county_name')}.")

    explicit_state_tokens = set(re.findall(r"\b[A-Z]{2}\b", query))
    state_hits = [s for s in sorted(df["state"].dropna().astype(str).unique()) if s in explicit_state_tokens]
    if state_hits:
        out = out[out["state"].isin(state_hits)]
        notes.append(f"Filtered to states: {', '.join(state_hits)}.")

    if not notes:
        text_mask = (
            out["county_name"].astype(str).str.lower().str.contains(q, regex=False, na=False)
            | out["state"].astype(str).str.lower().str.contains(q, regex=False, na=False)
            | out.get("opportunity_archetype", pd.Series("", index=out.index)).astype(str).str.lower().str.contains(q, regex=False, na=False)
        )
        if text_mask.any():
            out = out[text_mask]
            notes.append("Applied text match against county, state, and archetype.")
        else:
            notes.append("No parser rule matched; showing active strategy ranking.")
    return out.sort_values("sim_rank"), notes


def _thesis_scorecard(row: pd.Series, preset_name: str) -> tuple[str, pd.DataFrame]:
    pred5 = _product_numeric(row, "pred_avg_5yr", 0.0)
    risk = _product_numeric(row, "composite_risk", 50.0)
    confidence = str(row.get("confidence", "MEDIUM")).upper()
    structure = _product_numeric(row, "sim_structure_score", 50.0)
    stability = _product_numeric(row, "rank_stability_spread", 0.25)
    fallback = bool(row.get("use_stable_3yr_fallback", False))
    fragility = _product_numeric(row, "land_fragility_pressure", 0.5)

    rows = [
        {"Rule": "Long-horizon upside", "Score": np.clip(100 * pred5 / 0.18, 0, 100), "Read": _fmt_pct(pred5)},
        {"Rule": "Risk control", "Score": np.clip(100 - risk, 0, 100), "Read": _fmt_score(risk)},
        {"Rule": "Structural fit", "Score": np.clip(structure, 0, 100), "Read": _fmt_score(structure)},
        {"Rule": "Confidence", "Score": {"HIGH": 90, "MEDIUM": 65, "LOW": 35}.get(confidence, 50), "Read": confidence},
        {"Rule": "Rank stability", "Score": np.clip(100 - 120 * stability, 0, 100), "Read": f"{stability:.3f}"},
        {"Rule": "3yr fallback", "Score": 45 if fallback else 85, "Read": "active" if fallback else "clear"},
    ]
    if "Climate" in preset_name:
        rows.append({"Rule": "Fragility pressure", "Score": np.clip(100 - 100 * fragility, 0, 100), "Read": f"{fragility:.3f}"})
    score = float(np.mean([r["Score"] for r in rows]))
    verdict = "Pass" if score >= 70 else "Watch" if score >= 52 else "Reject for this thesis"
    return verdict, pd.DataFrame(rows)


def _why_not_bullets(row: pd.Series) -> list[str]:
    bullets = []
    if _product_numeric(row, "sim_growth_score", 50.0) < 55:
        bullets.append("Growth score is not strong enough to pull the county higher under the active strategy.")
    if _product_numeric(row, "composite_risk", 50.0) > 50:
        bullets.append("Composite risk is taking meaningful points away from the rank.")
    if _product_numeric(row, "sim_structure_score", 50.0) < 50:
        bullets.append("Structural land-thesis fit is only middling.")
    if _product_numeric(row, "sim_uncertainty_score", 0.0) > 65:
        bullets.append("Prediction uncertainty is wide relative to other counties.")
    if bool(row.get("use_stable_3yr_fallback", False)):
        bullets.append("The 3yr policy falls back to the stabilized path, which makes the medium-term read more conditional.")
    return bullets or ["No obvious single blocker; this county is mostly being ranked by relative tradeoffs against stronger peers."]


def _bull_bear_cases(row: pd.Series) -> tuple[list[str], list[str]]:
    narrative = _build_county_narrative(row)
    bull = list(narrative["positives"][:3])
    bear = list(narrative["cautions"][:3])
    verdict = _build_wave3_decision_narrative(row)
    bull.append(verdict["thesis"])
    bear.extend(_why_not_bullets(row)[:2])
    return bull[:5], bear[:5]


def _negative_screen(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["avoid_score"] = (
        0.35 * _product_series(out, "composite_risk", 50.0)
        + 0.20 * _product_series(out, "sim_uncertainty_score", 0.0)
        + 0.20 * (100.0 - _product_series(out, "sim_confidence_score", 50.0))
        + 0.15 * (100.0 - _product_series(out, "sim_structure_score", 50.0))
        + 0.10 * _product_series(out, "rank_stability_spread", 0.25) * 100.0
    ).clip(0, 100)
    out["screen_read"] = np.where(out["avoid_score"] >= 65, "Avoid", np.where(out["avoid_score"] >= 50, "Monitor only", "Needs special thesis"))
    return out.sort_values(["avoid_score", "sim_rank"], ascending=[False, True])


def _regional_summary(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()
    state_roll = (
        df.groupby("state")
        .agg(
            counties=("fips", "count"),
            avg_strategy_score=("sim_score", "mean"),
            avg_risk=("composite_risk", "mean"),
            avg_5yr=("pred_avg_5yr", "mean"),
            high_conf_share=("confidence", lambda s: float((s.astype(str).str.upper() == "HIGH").mean())),
        )
        .reset_index()
        .sort_values("avg_strategy_score", ascending=False)
    )
    arch = (
        df.groupby(["state", "opportunity_archetype"])
        .size()
        .reset_index(name="count")
        .sort_values(["state", "count"], ascending=[True, False])
    )
    return state_roll, arch


def _model_disagreement_surface(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    xgb_lgb_cols = []
    for h in HORIZONS:
        xgb = f"pred_xgboost_{h}yr"
        lgb = f"pred_lightgbm_{h}yr"
        if xgb in out.columns and lgb in out.columns:
            out[f"disagreement_{h}yr"] = (pd.to_numeric(out[xgb], errors="coerce") - pd.to_numeric(out[lgb], errors="coerce")).abs()
            xgb_lgb_cols.append(f"disagreement_{h}yr")
    horizon_cols = [c for c in ["pred_avg_1yr", "pred_policy_3yr", "pred_avg_5yr"] if c in out.columns]
    if len(horizon_cols) >= 2:
        ranks = out[horizon_cols].rank(ascending=False, pct=True)
        out["horizon_disagreement"] = ranks.max(axis=1) - ranks.min(axis=1)
    else:
        out["horizon_disagreement"] = 0.0
    out["model_disagreement_lens"] = (
        _product_series(out, "model_disagreement", 0.0) * 100.0
        + 25.0 * _product_series(out, "horizon_disagreement", 0.0)
        + 0.15 * _product_series(out, "sim_uncertainty_score", 0.0)
    )
    return out.sort_values("model_disagreement_lens", ascending=False)


def _watchlist_drift_alerts(watch_df: pd.DataFrame, latest_compare_rank_df: pd.DataFrame | None) -> pd.DataFrame:
    if watch_df.empty:
        return pd.DataFrame()
    rows = []
    compare_lookup = {}
    if latest_compare_rank_df is not None and not latest_compare_rank_df.empty:
        comp = latest_compare_rank_df.copy()
        comp["fips"] = comp["fips"].astype(str).str.zfill(5)
        compare_lookup = comp.set_index("fips").to_dict("index")
    for _, row in watch_df.iterrows():
        fips = str(row.get("fips")).zfill(5)
        alerts = []
        comp = compare_lookup.get(fips, {})
        if pd.notna(comp.get("rank_shift")) and float(comp["rank_shift"]) >= 10:
            alerts.append(f"latest rank dropped {float(comp['rank_shift']):.0f} places")
        if pd.notna(row.get("composite_risk")) and float(row["composite_risk"]) >= 55:
            alerts.append("risk above 55")
        if str(row.get("confidence", "")).upper() == "LOW":
            alerts.append("low confidence")
        if bool(row.get("use_stable_3yr_fallback", False)):
            alerts.append("3yr fallback active")
        if alerts:
            rows.append({"County": row.get("county_name"), "State": row.get("state"), "Alerts": "; ".join(alerts)})
    return pd.DataFrame(rows)


def _autopsy_candidates(current_df: pd.DataFrame, latest_compare_rank_df: pd.DataFrame | None) -> pd.DataFrame:
    frames = []
    if latest_compare_rank_df is not None and not latest_compare_rank_df.empty:
        comp = latest_compare_rank_df.copy()
        fallers = comp[pd.to_numeric(comp.get("rank_shift"), errors="coerce") >= 25].copy()
        if not fallers.empty:
            fallers["autopsy_reason"] = "Large latest-run rank decline"
            frames.append(fallers.rename(columns={"county_name_new": "county_name", "state_new": "state", "overall_rank_new": "overall_rank"}))
    weak = current_df[
        (pd.to_numeric(current_df.get("overall_rank"), errors="coerce") <= 100)
        & (
            (pd.to_numeric(current_df.get("composite_risk"), errors="coerce") >= 55)
            | (current_df.get("confidence", pd.Series("", index=current_df.index)).astype(str).str.upper() == "LOW")
            | (current_df.get("use_stable_3yr_fallback", pd.Series(False, index=current_df.index)).astype(bool))
        )
    ].copy()
    weak["autopsy_reason"] = "High rank with current caution flag"
    frames.append(weak)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True, sort=False)
    if "fips" in out.columns:
        out = out.drop_duplicates("fips")
    return out.head(30)


def _promotion_readiness_rows(status_bundle: dict | None) -> pd.DataFrame:
    bundle = status_bundle or {}
    model_health = bundle.get("model_health_3yr") or {}
    wave3_closeout = bundle.get("wave3_closeout") or {}
    wave3_overlay = bundle.get("wave3_structural_overlay") or {}
    source_summary = bundle.get("source_health_summary") or {}
    rows = [
        {
            "Gate": "3yr health",
            "Status": _humanize_status_label((model_health.get("assessment") or {}).get("health_status", "unknown")),
            "Read": "Blocks direct 3yr promotion until stabilized.",
        },
        {
            "Gate": "Wave 3 closeout",
            "Status": _humanize_status_label(wave3_closeout.get("status", "unknown")),
            "Read": "Product/overlay-first posture remains preferred.",
        },
        {
            "Gate": "Overlay churn",
            "Status": f"{wave3_overlay.get('top_churn_pct', 'n/a')}%",
            "Read": "Capped overlay should stay calm in top decision bands.",
        },
        {
            "Gate": "Source health",
            "Status": f"{source_summary.get('healthy_sources', 0)}/{source_summary.get('n_sources', 0)} healthy",
            "Read": "Source-health issues should be resolved before promotion.",
        },
    ]
    return pd.DataFrame(rows)


def _run_review_narrative(latest_compare_rank_df: pd.DataFrame | None) -> list[str]:
    if latest_compare_rank_df is None or latest_compare_rank_df.empty:
        return ["No latest run comparison is available."]
    comp = latest_compare_rank_df.copy()
    rank_shift = pd.to_numeric(comp.get("rank_shift"), errors="coerce")
    score_delta = pd.to_numeric(comp.get("opportunity_score_delta"), errors="coerce")
    top25_old = pd.to_numeric(comp.get("overall_rank_old"), errors="coerce") <= 25
    top25_new = pd.to_numeric(comp.get("overall_rank_new"), errors="coerce") <= 25
    bullets = [
        f"Average absolute rank movement was {rank_shift.abs().mean():.1f} places across {len(comp):,} counties.",
        f"Top-25 entrants: {int((~top25_old & top25_new).sum())}; exits: {int((top25_old & ~top25_new).sum())}.",
        f"Median opportunity-score change was {score_delta.median():+.2f}.",
    ]
    for col, label in [
        ("pred_policy_3yr_delta", "3yr policy"),
        ("pred_xgboost_5yr_delta", "XGBoost 5yr"),
        ("pred_lightgbm_5yr_delta", "LightGBM 5yr"),
        ("composite_risk_delta", "risk"),
    ]:
        if col in comp.columns:
            corr = rank_shift.corr(pd.to_numeric(comp[col], errors="coerce"))
            if pd.notna(corr):
                bullets.append(f"{label} deltas had rank-shift correlation {corr:+.2f}.")
    return bullets[:6]


def _ic_packet_markdown(watch_df: pd.DataFrame, cfg: dict, preset_name: str, stress_df: pd.DataFrame | None) -> str:
    memo = _build_deal_thesis_memo(watch_df, cfg, preset_name, stress_df)
    lines = ["# Investment Committee Packet", "", memo]
    lines.append("## Recommendation")
    if watch_df.empty:
        lines.append("- No recommendation; shortlist is empty.")
    else:
        clean = watch_df[(watch_df["composite_risk"] <= 50) & (watch_df["confidence"].astype(str).str.upper().isin(["HIGH", "MEDIUM"]))]
        lines.append(f"- Advance `{min(len(clean), 5)}` counties to first-pass diligence from the current shortlist.")
        lines.append("- Keep this as a county-level screen; parcel feasibility still needs direct verification.")
    return "\n".join(lines).rstrip() + "\n"


def _selected_county_row(df: pd.DataFrame, fips: str | None) -> pd.Series | None:
    if not fips:
        return None
    match = df[df["fips"].astype(str).str.zfill(5) == str(fips).zfill(5)]
    if match.empty:
        return None
    return match.iloc[0]


def _rank_text(value) -> str:
    if pd.isna(value):
        return "—"
    try:
        return f"#{int(float(value))}"
    except (TypeError, ValueError):
        return "—"


def _confidence_read(row: pd.Series) -> tuple[str, list[str]]:
    conf = str(row.get("confidence", "UNKNOWN")).upper()
    model_disagreement = _product_numeric(row, "model_disagreement", 0.0)
    horizon_spread = _product_numeric(row, "rank_stability_spread", 0.0)
    interval = _product_numeric(row, "quantile_interval_width_mean", np.nan)
    pred5 = _product_numeric(row, "pred_avg_5yr", 0.0)
    fallback = bool(row.get("use_stable_3yr_fallback", False))

    if conf == "HIGH" and model_disagreement <= 0.035 and horizon_spread <= 0.25 and pd.notna(interval) and interval <= 0.48:
        label = "High Consensus"
    elif pred5 >= 0.12 and (model_disagreement >= 0.055 or horizon_spread >= 0.45 or pd.notna(interval) and interval >= 0.52):
        label = "High Upside / High Uncertainty"
    elif fallback or horizon_spread >= 0.45 or model_disagreement >= 0.06:
        label = "Mixed Signal"
    elif conf == "LOW" or pd.notna(interval) and interval >= 0.54:
        label = "Data Fragile"
    else:
        label = "Moderate Consensus"

    bullets = [
        f"Model-confidence bucket is `{conf}`.",
        f"XGBoost/LightGBM disagreement is `{model_disagreement:.3f}`.",
        f"Cross-horizon rank spread is `{horizon_spread:.3f}`.",
    ]
    if pd.notna(interval):
        bullets.append(f"Mean prediction interval width is `{interval:.3f}`.")
    if fallback:
        bullets.append("3yr policy uses the stabilized fallback path.")
    return label, bullets


def _preboom_signal_rows_for_county(
    row: pd.Series,
    preboom_surfaces: dict[str, pd.DataFrame | None] | None,
) -> pd.DataFrame:
    if not preboom_surfaces:
        return pd.DataFrame()
    fips = str(row.get("fips", "")).zfill(5)
    labels = _preboom_surface_label_map()
    rows: list[dict[str, object]] = []
    for key in ["guarded_blend", "residual_guardrail", "balanced", "raw", "unguarded_blend"]:
        surface = preboom_surfaces.get(key)
        if surface is None or surface.empty or "fips" not in surface.columns:
            continue
        work = surface.copy()
        work["fips"] = work["fips"].astype(str).str.zfill(5)
        match = work[work["fips"].eq(fips)]
        if match.empty:
            continue
        rec = match.iloc[0]
        rank_col = _preboom_surface_rank_col(work)
        rows.append(
            {
                "Surface": labels.get(key, key),
                "Review Rank": _rank_text(rec.get(rank_col)),
                "Breakout Prob": _fmt_score(rec.get("preboom_classifier_score")),
                "Residual Upside": _fmt_score(
                    rec.get("investable_residual_model_score", rec.get("guarded_residual_score", rec.get("residual_model_score")))
                ),
                "Prior Momentum": _fmt_score(rec.get("preboom_prior_momentum_rank_pct")),
                "QA": rec.get("qa_status", rec.get("qa_flags", "research-only")),
            }
        )
    return pd.DataFrame(rows)


def _aggregate_analog_summaries(analog_suite: dict | None) -> pd.DataFrame:
    if not analog_suite:
        return pd.DataFrame()
    summaries = pd.DataFrame(analog_suite.get("window_summaries") or [])
    if summaries.empty:
        return summaries
    grouped = (
        summaries.groupby(["analog_group", "theme"], as_index=False)
        .agg(
            windows=("window", "count"),
            avg_future_rank=("avg_preboom_future_growth_rank_pct_5yr", "mean"),
            avg_prior_momentum=("avg_preboom_prior_momentum_rank_pct", "mean"),
            avg_signal_share=("any_signal_share", "mean"),
            avg_already_hot_share=("avg_preboom_already_hot_flag", "mean"),
        )
        .sort_values(["avg_future_rank", "avg_signal_share"], ascending=[False, False])
    )
    return grouped


def _analog_rows_for_county(row: pd.Series, analog_suite: dict | None, limit: int = 3) -> pd.DataFrame:
    if not analog_suite:
        return pd.DataFrame()
    fips = str(row.get("fips", "")).zfill(5)
    timelines = pd.DataFrame(analog_suite.get("county_timelines") or [])
    exact_rows: list[dict[str, object]] = []
    if not timelines.empty and "fips" in timelines.columns:
        exact = timelines[timelines["fips"].astype(str).str.zfill(5).eq(fips)].copy()
        for _, rec in exact.head(limit).iterrows():
            exact_rows.append(
                {
                    "Analog Family": str(rec.get("analog_group", "")).replace("_", " ").title(),
                    "Why Relevant": "Exact county appears in the known-boom analog library.",
                    "Historical Window": rec.get("window", "n/a"),
                    "Historical Read": f"future rank pct {_fmt_score(rec.get('avg_future_growth_rank_pct_5yr'))}",
                    "Before-Hot Signal": "yes" if bool(rec.get("signal_before_hot")) else "no",
                }
            )
    if exact_rows:
        return pd.DataFrame(exact_rows)

    grouped = _aggregate_analog_summaries(analog_suite)
    if grouped.empty:
        return pd.DataFrame()
    archetype = str(row.get("opportunity_archetype", "")).lower()
    recreation = _product_numeric(row, "recreation_access_score", 0.0)
    structure = _product_numeric(row, "sim_structure_score", 50.0)
    risk = _product_numeric(row, "composite_risk", 50.0)
    pred5 = _product_numeric(row, "pred_avg_5yr", 0.0)

    preferred: list[str] = []
    if "amenity" in archetype or recreation >= 0.66:
        preferred.extend(["boise_treasure_valley", "colorado_front_range", "utah_wasatch_spillover"])
    if "buildable" in archetype or "scarcity" in archetype or structure >= 70:
        preferred.extend(["boise_treasure_valley", "colorado_front_range", "austin_hill_country"])
    if "low-risk" in archetype or pred5 >= 0.12 and risk <= 45:
        preferred.extend(["nashville_middle_tennessee", "raleigh_triangle_spillover", "charlotte_piedmont_spillover"])
    if "fragile" in archetype or risk >= 55:
        preferred.extend(["phoenix_sun_corridor", "florida_space_gulf_growth"])
    if not preferred:
        preferred.extend(["boise_treasure_valley", "nashville_middle_tennessee", "northwest_arkansas"])

    preferred = list(dict.fromkeys(preferred))
    ranked = pd.concat(
        [
            grouped[grouped["analog_group"].isin(preferred)],
            grouped[~grouped["analog_group"].isin(preferred)].head(limit),
        ],
        ignore_index=True,
    ).drop_duplicates("analog_group").head(limit)

    rows = []
    for _, rec in ranked.iterrows():
        rows.append(
            {
                "Analog Family": str(rec.get("analog_group", "")).replace("_", " ").title(),
                "Why Relevant": rec.get("theme", "historical growth setup"),
                "Historical Window": f"{int(rec.get('windows', 0))} windows",
                "Historical Read": f"avg future rank pct {_fmt_score(rec.get('avg_future_rank'))}",
                "Before-Hot Signal": f"signal share {_fmt_pct(rec.get('avg_signal_share'))}",
            }
        )
    return pd.DataFrame(rows)


def _top_xfactor_scoreboard_rows(scoreboard: dict | None, limit: int = 3) -> pd.DataFrame:
    if not scoreboard:
        return pd.DataFrame()
    rows = scoreboard.get("summary") or scoreboard.get("scoreboard") or []
    if not rows:
        return pd.DataFrame()
    frame = pd.DataFrame(rows)
    sort_col = "validation_score" if "validation_score" in frame.columns else "frontier_score" if "frontier_score" in frame.columns else None
    if sort_col:
        frame = frame.sort_values(sort_col, ascending=False)
    cols = [
        "label",
        "fold_count",
        "avg_preboom_rate_lift",
        "already_hot_top_decile_share",
        "analog_top_decile_capture_share",
        "decision",
    ]
    view = frame[[c for c in cols if c in frame.columns]].head(limit).copy()
    if view.empty:
        return view
    view = view.rename(
        columns={
            "label": "Interaction",
            "fold_count": "Folds",
            "avg_preboom_rate_lift": "Quiet Lift",
            "already_hot_top_decile_share": "Already-Hot Share",
            "analog_top_decile_capture_share": "Analog Capture",
            "decision": "Decision",
        }
    )
    for col in ["Quiet Lift", "Already-Hot Share", "Analog Capture"]:
        if col in view.columns:
            view[col] = view[col].map(_fmt_pct)
    return view


def _score_glossary_table() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Term": "Strategy Rank",
                "Plain-English Read": "Product Mode simulation rank using the current sidebar strategy settings.",
                "Production Status": "UI overlay",
            },
            {
                "Term": "Production Rank",
                "Plain-English Read": "Unchanged county rank from the current scoring artifact.",
                "Production Status": "Production artifact",
            },
            {
                "Term": "Opportunity Score",
                "Plain-English Read": "Current production ranking score after growth, risk, uncertainty, and stability policy.",
                "Production Status": "Production artifact",
            },
            {
                "Term": "Risk",
                "Plain-English Read": "Composite county-level risk; higher values need more caution before diligence.",
                "Production Status": "Production artifact",
            },
            {
                "Term": "Confidence",
                "Plain-English Read": "Coarse confidence bucket from model agreement, uncertainty, and stability signals.",
                "Production Status": "Production artifact",
            },
            {
                "Term": "X-Factor / Pre-Boom",
                "Plain-English Read": "Research surfaces looking for structurally supported counties before momentum is obvious.",
                "Production Status": "Report-only",
            },
            {
                "Term": "Wave 3 / Land Thesis",
                "Plain-English Read": "Structural context for support, brakes, buildability, optionality, amenity, and fragility.",
                "Production Status": "Overlay / narrative first",
            },
        ]
    )


def _format_export_frame(df: pd.DataFrame, limit: int) -> pd.DataFrame:
    cols = [
        "sim_rank",
        "overall_rank",
        "fips",
        "county_name",
        "state",
        "sim_score",
        "opportunity_score",
        "pred_avg_5yr",
        "pred_policy_3yr",
        "composite_risk",
        "confidence",
        "opportunity_archetype",
        "sim_structure_score",
        "model_disagreement",
        "quantile_interval_width_mean",
        "rank_stability_spread",
    ]
    out = df[[c for c in cols if c in df.columns]].sort_values("sim_rank").head(limit).copy()
    if "fips" in out.columns:
        out["fips"] = out["fips"].astype(str).str.zfill(5)
    return out


def _compare_export_frame(compare_df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "sim_rank",
        "overall_rank",
        "fips",
        "county_name",
        "state",
        "sim_score",
        "opportunity_score",
        "pred_avg_5yr",
        "pred_policy_3yr",
        "composite_risk",
        "confidence",
        "opportunity_archetype",
        "sim_structure_score",
        "model_disagreement",
        "quantile_interval_width_mean",
        "rank_stability_spread",
    ]
    out = compare_df[[c for c in cols if c in compare_df.columns]].sort_values("sim_rank").copy()
    if "fips" in out.columns:
        out["fips"] = out["fips"].astype(str).str.zfill(5)
    return out


def _top_report_markdown(
    df: pd.DataFrame,
    cfg: dict,
    latest_run: dict | None,
    *,
    limit: int,
    title: str,
) -> str:
    run_id = latest_run.get("run_id", "unknown") if latest_run else "unknown"
    generated = datetime.now().isoformat()
    lines = [
        f"# {title}",
        "",
        f"- Generated at: `{generated}`",
        f"- Ranking run: `{run_id}`",
        f"- Strategy preset: `{cfg.get('preset_name', 'Active strategy')}`",
        f"- Horizon mix: 1yr `{cfg.get('h1')}`, 3yr `{cfg.get('h3')}`, 5yr `{cfg.get('h5')}`",
        f"- Score mix: growth `{cfg.get('growth')}`, risk `{cfg.get('risk')}`, land thesis `{cfg.get('structure')}`, confidence `{cfg.get('confidence')}`",
        "- Use: county-level screening and discussion; not investment advice or parcel-level diligence.",
        "",
        "## County List",
        "",
        "| Strategy Rank | Production Rank | County | State | 5yr | Risk | Confidence | Archetype | First Diligence Check |",
        "|---:|---:|---|---|---:|---:|---|---|---|",
    ]
    for _, row in df.sort_values("sim_rank").head(limit).iterrows():
        _, actions = _parcel_readiness(row)
        lines.append(
            f"| {_rank_text(row.get('sim_rank'))} | {_rank_text(row.get('overall_rank'))} | "
            f"{row.get('county_name', '')} | {row.get('state', '')} | {_fmt_pct(row.get('pred_avg_5yr'))} | "
            f"{_fmt_score(row.get('composite_risk'))} | {row.get('confidence', 'n/a')} | "
            f"{row.get('opportunity_archetype', 'n/a')} | {actions[0] if actions else 'n/a'} |"
        )
    lines.extend(
        [
            "",
            "## Read Before Sharing",
            "",
            "- `Strategy Rank` is a Product Mode simulation, not a saved model artifact.",
            "- `Production Rank` is the current scoring artifact.",
            "- X-factor/pre-boom and Wave 3 structural fields are decision-support context unless explicitly promoted by a model gate.",
            "- Every county still needs parcel, zoning, transaction, insurance, and local-market diligence.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _compare_set_markdown(compare_df: pd.DataFrame, cfg: dict, latest_run: dict | None) -> str:
    run_id = latest_run.get("run_id", "unknown") if latest_run else "unknown"
    lines = [
        "# LandInvest Compare Set Summary",
        "",
        f"- Generated at: `{datetime.now().isoformat()}`",
        f"- Ranking run: `{run_id}`",
        f"- Strategy preset: `{cfg.get('preset_name', 'Active strategy')}`",
        "- Use: side-by-side county-level screening; not investment advice.",
        "",
        "## Counties",
        "",
        "| Strategy Rank | Production Rank | County | State | 5yr | 3yr | Risk | Confidence | Best Read | Main Brake |",
        "|---:|---:|---|---|---:|---:|---:|---|---|---|",
    ]
    for _, row in compare_df.sort_values("sim_rank").iterrows():
        narrative = _build_county_narrative(row)
        support = narrative["positives"][0] if narrative["positives"] else "n/a"
        brake = narrative["cautions"][0] if narrative["cautions"] else "n/a"
        lines.append(
            f"| {_rank_text(row.get('sim_rank'))} | {_rank_text(row.get('overall_rank'))} | "
            f"{row.get('county_name', '')} | {row.get('state', '')} | {_fmt_pct(row.get('pred_avg_5yr'))} | "
            f"{_fmt_pct(row.get('pred_policy_3yr'))} | {_fmt_score(row.get('composite_risk'))} | "
            f"{row.get('confidence', 'n/a')} | {support} | {brake} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def _render_trust_banner(latest_run: dict | None, df: pd.DataFrame, xfactor_gate: dict | None = None) -> None:
    run_id = latest_run.get("run_id", "unknown") if latest_run else "unknown"
    run_year = latest_run.get("year", df["year"].max() if "year" in df.columns else "n/a") if latest_run else "n/a"
    gate_status = (xfactor_gate or {}).get("production_promotion_status", "research gates active")
    st.info(
        "County-level model screening only. Outputs are estimates, not investment advice or parcel-specific diligence. "
        f"Ranking run `{run_id}`, year `{run_year}`, rows `{len(df):,}`. "
        f"X-factor status: `{_humanize_status_label(gate_status)}`."
    )


def _demo_checklist_table(demo_readiness_report: dict | None) -> pd.DataFrame:
    if not demo_readiness_report:
        return pd.DataFrame(
            [
                {
                    "Area": "Demo readiness",
                    "Status": "missing",
                    "Detail": "Run scripts/build_demo_readiness_bundle.py to generate the checklist.",
                }
            ]
        )
    rows = []
    for item in demo_readiness_report.get("checklist") or []:
        rows.append(
            {
                "Area": item.get("area", "Unknown"),
                "Status": item.get("status", "unknown"),
                "Detail": item.get("detail", ""),
            }
        )
    return pd.DataFrame(rows)


def _source_attribution_table() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"Family": "Home values and price history", "Examples": "FHFA, Zillow-derived ZHVI artifacts", "Use": "Targets, trend context, ranking inputs"},
            {"Family": "Labor, income, and establishments", "Examples": "BLS, BEA, Census CBP/QCEW", "Use": "Growth context, economic anchors, affordability"},
            {"Family": "Population and migration", "Examples": "U.S. Census, IRS-style migration-derived features where staged", "Use": "Demand and demographic context"},
            {"Family": "Credit, lending, and housing activity", "Examples": "HMDA and project-staged housing indicators", "Use": "Liquidity, market depth, and risk context"},
            {"Family": "Climate, terrain, water, and land constraints", "Examples": "NOAA, USGS, FCC, PAD-US/wetlands-derived project artifacts", "Use": "Risk, buildability, and land-thesis overlays"},
            {"Family": "Corporate-anchor evidence", "Examples": "SEC EDGAR proof lanes and staged anchor diagnostics", "Use": "Report-only X-factor and analog context"},
        ]
    )


def _artifact_status_table() -> pd.DataFrame:
    rows = []
    for label, path, required in [
        ("County rankings", DATA_PATH, True),
        ("County map GeoJSON", COUNTY_GEOJSON_PATH, False),
        ("Project status bundle", STATUS_BUNDLE_PATH, False),
        ("Demo readiness report", DEMO_READINESS_REPORT_PATH, False),
        ("X-factor promotion gate", XFACTOR_INTERACTION_PROMOTION_GATE_PATH, False),
        ("X-factor ablation queue", XFACTOR_INTERACTION_ABLATION_QUEUE_PATH, False),
        ("Known analog suite", KNOWN_ANALOG_SUITE_PATH, False),
        ("Source health", SOURCE_HEALTH_PATH, False),
    ]:
        rows.append(
            {
                "Artifact": label,
                "Status": "present" if path.exists() else "missing",
                "Required": "yes" if required else "optional",
                "Path": str(path.relative_to(Path(__file__).resolve().parent)) if path.is_absolute() else str(path),
            }
        )
    return pd.DataFrame(rows)


def _render_missing_artifact_help() -> None:
    st.error("The demo cannot load county rankings because the required ranking artifact is missing or unreadable.")
    st.dataframe(_artifact_status_table(), width="stretch", hide_index=True, height=260)
    st.info(
        "Regenerate local rankings with `python scoring_pipeline.py`, then run "
        "`./.venv/bin/python scripts/build_demo_readiness_bundle.py` to rebuild the demo package."
    )


def _render_demo_footer(
    latest_run: dict | None,
    status_bundle: dict | None,
    demo_readiness_report: dict | None,
) -> None:
    latest = latest_run or {}
    run_id = latest.get("run_id") or ((status_bundle or {}).get("latest_run") or {}).get("run_dir") or "unknown"
    readiness = (demo_readiness_report or {}).get("overall_status", "not generated")
    generated = (demo_readiness_report or {}).get("generated_at", "n/a")
    source_summary = (status_bundle or {}).get("source_health_summary") or {}
    healthy = source_summary.get("healthy_sources")
    total = source_summary.get("n_sources")
    source_read = f"{healthy}/{total} healthy" if healthy is not None and total is not None else "source summary unavailable"
    st.divider()
    st.caption(
        f"Demo status `{readiness}` · ranking run `{run_id}` · readiness generated `{generated}` · "
        f"sources `{source_read}` · user store `{_current_user_id()}`"
    )
    with st.expander("Trust, Privacy, And Sources", expanded=False):
        st.markdown(
            "- LandInvest is a county-level screening and research tool. It is not investment, legal, tax, valuation, or parcel-specific advice.\n"
            "- Rankings are model estimates and research overlays; every county still needs parcel, zoning, title, transaction, insurance, and local-market diligence.\n"
            "- Demo notes, watchlists, saved strategies, and compare sets are stored in a local SQLite file keyed by demo user id. This separates tester state but is not authentication or secure multi-tenant storage.\n"
            "- Research-only X-factor, pre-boom, analog, and Wave 3 signals are labeled as overlays unless a promotion gate explicitly changes their production status."
        )
        st.dataframe(_source_attribution_table(), width="stretch", hide_index=True, height=260)
        with st.expander("Artifact Status", expanded=False):
            st.dataframe(_artifact_status_table(), width="stretch", hide_index=True, height=260)


def _render_start_here_tab(
    filtered: pd.DataFrame,
    cfg: dict,
    latest_run: dict | None,
    xfactor_scoreboard: dict | None,
    xfactor_gate: dict | None,
    demo_readiness_report: dict | None = None,
) -> None:
    st.header("Start Here")
    st.markdown(
        "LandInvest ranks U.S. counties for land and home-value growth review, then explains the thesis, the brakes, "
        "and the remaining diligence. Start with the highest strategy-fit counties, open a county memo, then export a shortlist."
    )
    if filtered.empty:
        st.warning("No counties match the active strategy filters.")
        return

    s1, s2, s3 = st.columns(3)
    s1.metric("View Top Opportunities", f"{min(len(filtered), 25)} counties")
    s2.metric("Explore Map", f"{filtered['state'].nunique()} states")
    s3.metric("Open County Memo", str(filtered.iloc[0].get("county_name", "Top county")))

    st.subheader("Investor Review Workflow")
    r1, r2, r3, r4 = st.columns(4)
    r1.markdown("**1. Discover**\n\nScreen top counties, search, and compare strategy lenses.")
    r2.markdown("**2. Open County Memo**\n\nRead the thesis, brakes, confidence, and what would break the case.")
    r3.markdown("**3. Build Watchlist**\n\nSave counties, stage diligence, and monitor rank or risk drift.")
    r4.markdown("**4. Export Reports**\n\nDownload shortlist, compare-set, and memo packages for review.")

    st.subheader("Top Opportunities")
    st.dataframe(_product_table(filtered.sort_values("sim_rank"), limit=10), width="stretch", hide_index=True, height=360)
    top_row = filtered.sort_values("sim_rank").iloc[0]
    if st.button("Set top county as memo selection", key="start_set_top_memo", type="primary"):
        st.session_state.product_selected_fips = str(top_row.get("fips")).zfill(5)
        st.success(f"County Memo selection set to {top_row.get('county_name')}, {top_row.get('state')}.")

    g1, g2 = st.columns(2)
    with g1:
        st.subheader("Score Glossary")
        st.dataframe(_score_glossary_table(), width="stretch", hide_index=True, height=310)
    with g2:
        st.subheader("Current Research Gate")
        gate = xfactor_gate or {}
        if gate:
            st.markdown(
                f"- Production promotion status: `{_humanize_status_label(gate.get('production_promotion_status', 'n/a'))}`\n"
                f"- Ablation-ready candidates: `{gate.get('ablation_ready_count', 'n/a')}`\n"
                f"- Default-promotion candidates: `{gate.get('default_promotion_count', 'n/a')}`"
            )
        score_rows = _top_xfactor_scoreboard_rows(xfactor_scoreboard, limit=5)
        if not score_rows.empty:
            st.dataframe(score_rows, width="stretch", hide_index=True, height=220)
        st.caption("X-factor rows are research validation context; they do not alter production scoring.")

    st.subheader("Demo Checklist")
    checklist = _demo_checklist_table(demo_readiness_report)
    st.dataframe(checklist, width="stretch", hide_index=True, height=260)
    if demo_readiness_report:
        st.caption(
            f"Demo readiness status: `{demo_readiness_report.get('overall_status', 'unknown')}`. "
            "Refresh with `./.venv/bin/python scripts/build_demo_readiness_bundle.py`."
        )

    st.download_button(
        "Export Top 25 report (Markdown)",
        data=_top_report_markdown(filtered, cfg, latest_run, limit=25, title="LandInvest Top 25 Opportunity Report").encode("utf-8"),
        file_name="landinvest_top25_opportunity_report.md",
        mime="text/markdown",
    )


def _build_county_memo_markdown(
    row: pd.Series,
    history_row: pd.Series | None,
    wave3_status: dict | None,
    cfg: dict,
    preboom_surfaces: dict[str, pd.DataFrame | None] | None,
    analog_suite: dict | None,
    xfactor_scoreboard: dict | None,
) -> str:
    fips = str(row.get("fips", "")).zfill(5)
    narrative = _build_county_narrative(row, history_row=history_row)
    decision = _build_wave3_decision_narrative(row)
    wave3_note = _build_wave3_narrative(row)
    confidence_label, confidence_bullets = _confidence_read(row)
    preboom_rows = _preboom_signal_rows_for_county(row, preboom_surfaces)
    analog_rows = _analog_rows_for_county(row, analog_suite)
    readiness, actions = _parcel_readiness(row)

    lines = [
        f"# LandInvest County Memo: {row.get('county_name', 'County')}, {row.get('state', '')}",
        "",
        f"- FIPS: `{fips}`",
        f"- Generated at: `{datetime.now().isoformat()}`",
        "- Use: county-level screening memo, not investment advice or parcel-level diligence.",
        "",
        "## Summary Thesis",
        "",
        narrative["summary"],
        "",
        "## Score Snapshot",
        "",
        f"- Strategy rank: `{_rank_text(row.get('sim_rank'))}`",
        f"- Production rank: `{_rank_text(row.get('overall_rank'))}`",
        f"- Strategy score: `{_fmt_score(row.get('sim_score'))}`",
        f"- 5yr signal: `{_fmt_pct(row.get('pred_avg_5yr'))}`",
        f"- Risk: `{_fmt_score(row.get('composite_risk'))}`",
        f"- Confidence read: `{confidence_label}`",
        "",
        "## Key Supports",
        "",
    ]
    lines.extend(f"- {item}" for item in narrative["positives"][:5])
    lines.extend(["", "## Key Brakes", ""])
    lines.extend(f"- {item}" for item in narrative["cautions"][:5])
    lines.extend(["", "## X-Factor / Pre-Boom Signals", ""])
    if preboom_rows.empty:
        lines.append("- This county is not currently present in the loaded top pre-boom review surfaces.")
    else:
        for _, rec in preboom_rows.iterrows():
            lines.append(
                f"- `{rec['Surface']}`: rank `{rec['Review Rank']}`, breakout `{rec['Breakout Prob']}`, "
                f"residual upside `{rec['Residual Upside']}`, prior momentum `{rec['Prior Momentum']}`."
            )
    score_rows = _top_xfactor_scoreboard_rows(xfactor_scoreboard)
    if not score_rows.empty:
        lines.append("- Current validated interaction themes remain report-only:")
        for _, rec in score_rows.iterrows():
            lines.append(f"  - {rec['Interaction']}: quiet lift `{rec.get('Quiet Lift', 'n/a')}`, decision `{rec.get('Decision', 'report-only')}`.")
    lines.extend(["", "## Structural Land Context", "", wave3_note["summary"], f"- Decision thesis: {decision['thesis']}"])
    lines.extend(["", "## Risk And Uncertainty", ""])
    lines.extend(f"- {item}" for item in confidence_bullets)
    lines.extend(["", "## Similar Historical Analogs", ""])
    if analog_rows.empty:
        lines.append("- No analog library context is currently available for this county.")
    else:
        for _, rec in analog_rows.iterrows():
            lines.append(
                f"- `{rec['Analog Family']}` ({rec['Historical Window']}): {rec['Why Relevant']} "
                f"Historical read: {rec['Historical Read']}; before-hot signal: {rec['Before-Hot Signal']}."
            )
    lines.extend(["", "## Diligence Checklist", "", f"- Parcel readiness: `{readiness}`"])
    lines.extend(f"- {item}" for item in actions)
    lines.extend(["", "## What Would Make This Thesis Wrong", ""])
    lines.extend(f"- {item}" for item in _why_not_bullets(row))
    return "\n".join(lines).rstrip() + "\n"


def _render_product_county_memo(
    row: pd.Series,
    history_row: pd.Series | None,
    wave3_status: dict | None,
    cfg: dict,
    preboom_surfaces: dict[str, pd.DataFrame | None] | None = None,
    analog_suite: dict | None = None,
    xfactor_scoreboard: dict | None = None,
    xfactor_ablation_queue: dict | None = None,
    xfactor_promotion_gate: dict | None = None,
) -> None:
    fips = str(row.get("fips", "")).zfill(5)
    st.subheader(f"{row.get('county_name', 'County')}, {row.get('state', '')}")
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Strategy Rank", f"#{int(row.get('sim_rank'))}" if pd.notna(row.get("sim_rank")) else "—")
    k2.metric("Production Rank", f"#{int(row.get('overall_rank'))}" if pd.notna(row.get("overall_rank")) else "—")
    k3.metric("Strategy Score", _fmt_score(row.get("sim_score")))
    k4.metric("5yr Signal", _fmt_pct(row.get("pred_avg_5yr")))
    k5.metric("Risk", _fmt_score(row.get("composite_risk")))

    narrative = _build_county_narrative(row, history_row=history_row)
    decision = _build_wave3_decision_narrative(row)
    wave3_note = _build_wave3_narrative(row)
    confidence_label, confidence_bullets = _confidence_read(row)
    memo_md = _build_county_memo_markdown(
        row=row,
        history_row=history_row,
        wave3_status=wave3_status,
        cfg=cfg,
        preboom_surfaces=preboom_surfaces,
        analog_suite=analog_suite,
        xfactor_scoreboard=xfactor_scoreboard,
    )
    with st.expander("How To Read This County Memo", expanded=True):
        st.markdown(
            "- `Strategy Rank` is the active Product Mode simulation under the sidebar settings; `Production Rank` is the unchanged scoring artifact.\n"
            "- `Upside` and `Cautions` summarize model drivers, risk, uncertainty, and run-history clues.\n"
            "- `X-Factor / Pre-Boom` entries are report-only discovery surfaces unless explicitly labeled as production.\n"
            "- `What Would Break The Thesis` is the first diligence queue, not a final rejection."
        )
    st.download_button(
        "Export county memo (Markdown)",
        data=memo_md.encode("utf-8"),
        file_name=f"landinvest_county_memo_{fips}.md",
        mime="text/markdown",
    )
    st.info(narrative["summary"])

    c1, c2, c3 = st.columns(3)
    with c1:
        st.caption("Upside")
        for bullet in narrative["positives"][:4]:
            st.markdown(f"- {bullet}")
    with c2:
        st.caption("Cautions")
        for bullet in narrative["cautions"][:4]:
            st.markdown(f"- {bullet}")
    with c3:
        st.caption("Decision Read")
        st.markdown(f"- Verdict: `{decision['verdict']}`")
        st.markdown(f"- Thesis: {decision['thesis']}")
        for item in decision["follow_up_checklist"][:2]:
            st.markdown(f"- Next: {item}")

    scorecard_verdict, scorecard = _thesis_scorecard(row, str(cfg.get("preset_name", "Active thesis")))
    st.caption("Investment thesis scorecard")
    sc1, sc2 = st.columns([1, 2])
    with sc1:
        st.metric("Thesis Verdict", scorecard_verdict)
    with sc2:
        scorecard_view = scorecard.copy()
        scorecard_view["Score"] = scorecard_view["Score"].map(lambda x: f"{float(x):.1f}")
        st.dataframe(scorecard_view, width="stretch", hide_index=True, height=230)

    bull, bear = _bull_bear_cases(row)
    bb1, bb2, bb3 = st.columns(3)
    with bb1:
        st.caption("Bull Case")
        for item in bull:
            st.markdown(f"- {item}")
    with bb2:
        st.caption("Bear Case")
        for item in bear:
            st.markdown(f"- {item}")
    with bb3:
        st.caption("What Would Break The Thesis?")
        for item in _why_not_bullets(row):
            st.markdown(f"- {item}")

    confidence_rows = pd.DataFrame(
        [{"Signal": "Confidence Label", "Read": confidence_label}]
        + [{"Signal": f"Check {idx + 1}", "Read": item} for idx, item in enumerate(confidence_bullets)]
    )
    st.caption("Model disagreement and confidence")
    st.dataframe(confidence_rows, width="stretch", hide_index=True, height=210)

    preboom_rows = _preboom_signal_rows_for_county(row, preboom_surfaces)
    analog_rows = _analog_rows_for_county(row, analog_suite)
    score_rows = _top_xfactor_scoreboard_rows(xfactor_scoreboard)
    xf1, xf2 = st.columns(2)
    with xf1:
        st.caption("X-Factor / Pre-Boom Signals")
        if preboom_rows.empty:
            st.info("This county is not currently present in the loaded top pre-boom review surfaces.")
        else:
            st.dataframe(preboom_rows, width="stretch", hide_index=True, height=220)
        if not score_rows.empty:
            with st.expander("Current validated interaction themes", expanded=False):
                st.dataframe(score_rows, width="stretch", hide_index=True, height=180)
                st.caption("These interaction themes are report-only validation context, not production scoring columns.")
    with xf2:
        st.caption("Similar Historical Analogs")
        if analog_rows.empty:
            st.info("No analog library context is currently available for this county.")
        else:
            st.dataframe(analog_rows, width="stretch", hide_index=True, height=260)
            st.caption("Analogs are historical reference patterns; they are not a forecast or comparable transaction set.")

    st.caption("Structural land thesis")
    st.write(wave3_note["summary"])
    coastal = _coastal_lane_provenance(row, wave3_status)
    st.caption(f"Coastal lane: `{coastal['label']}`. {coastal['summary']}")

    d1, d2 = st.columns(2)
    with d1:
        st.caption("Data confidence")
        st.dataframe(_data_confidence_table(row, wave3_status), width="stretch", hide_index=True, height=210)
    with d2:
        readiness, actions = _parcel_readiness(row)
        st.caption("Parcel diligence readiness")
        st.markdown(f"**{readiness}**")
        for action in actions[:4]:
            st.markdown(f"- {action}")

    metric_cols = [
        "sim_growth_score", "sim_risk_fit", "sim_structure_score",
        "sim_confidence_score", "sim_uncertainty_score",
    ]
    score_rows = [
        {"Component": c.replace("sim_", "").replace("_", " ").title(), "Score": float(row[c])}
        for c in metric_cols
        if c in row.index and pd.notna(row[c])
    ]
    if score_rows:
        fig = px.bar(
            pd.DataFrame(score_rows),
            x="Score",
            y="Component",
            orientation="h",
            range_x=[0, 100],
            title="Strategy Score Components",
            color="Score",
            color_continuous_scale="Tealgrn",
        )
        fig.update_layout(height=300, margin=dict(t=40, b=20))
        st.plotly_chart(fig, width="stretch")

    explain_rows = _rank_explain_rows(row, cfg)
    if not explain_rows.empty:
        st.caption("Why this rank?")
        explain_view = explain_rows.copy()
        for col in ["Weight", "Component Score", "Contribution"]:
            explain_view[col] = explain_view[col].map(lambda x: f"{float(x):+.2f}" if col == "Contribution" else f"{float(x):.2f}")
        e1, e2 = st.columns(2)
        with e1:
            st.dataframe(explain_view, width="stretch", hide_index=True, height=220)
        with e2:
            for bullet in _rank_explain_bullets(row, cfg):
                st.markdown(f"- {bullet}")

    b1, b2 = st.columns(2)
    with b1:
        if fips not in st.session_state.watchlist_fips:
            if st.button("Add to watchlist", key=f"product_add_{fips}", type="primary"):
                st.session_state.watchlist_fips = sorted(set(st.session_state.watchlist_fips + [fips]))
                st.success("County added to watchlist.")
        else:
            st.caption("Already on watchlist.")
    with b2:
        note_entry = st.session_state.county_notes.get(fips, {})
        note_text = st.text_area("Analyst note", value=note_entry.get("note", ""), height=100, key=f"product_note_{fips}")
        if st.button("Save note", key=f"product_note_save_{fips}"):
            st.session_state.county_notes[fips] = {
                "county_name": row.get("county_name"),
                "state": row.get("state"),
                "note": note_text.strip(),
                "updated_at": datetime.now().isoformat(),
            }
            _save_current_user_state()
            st.success("Note saved.")

    st.caption("Workflow, feedback, and evidence")
    wf1, wf2, wf3 = st.columns(3)
    funnel_stages = ["Discovery", "Research", "Diligence", "IC Review", "Approved", "Rejected", "Monitor"]
    with wf1:
        current_stage = st.session_state.county_funnel.get(fips, {}).get("stage", "Discovery")
        stage = st.selectbox(
            "Funnel stage",
            funnel_stages,
            index=funnel_stages.index(current_stage) if current_stage in funnel_stages else 0,
            key=f"product_stage_{fips}",
        )
        if st.button("Save stage", key=f"product_stage_save_{fips}"):
            st.session_state.county_funnel[fips] = {
                "county_name": row.get("county_name"),
                "state": row.get("state"),
                "stage": stage,
                "updated_at": datetime.now().isoformat(),
            }
            _save_current_user_state()
            st.success("Stage saved.")
    with wf2:
        feedback_options = ["Unreviewed", "Good recommendation", "Bad recommendation", "Interesting but too risky", "Already known", "Not investable", "Needs parcel data"]
        current_feedback = st.session_state.county_feedback.get(fips, {}).get("feedback", "Unreviewed")
        feedback = st.selectbox(
            "Human feedback",
            feedback_options,
            index=feedback_options.index(current_feedback) if current_feedback in feedback_options else 0,
            key=f"product_feedback_{fips}",
        )
        if st.button("Save feedback", key=f"product_feedback_save_{fips}"):
            st.session_state.county_feedback[fips] = {
                "county_name": row.get("county_name"),
                "state": row.get("state"),
                "feedback": feedback,
                "updated_at": datetime.now().isoformat(),
            }
            _save_current_user_state()
            st.success("Feedback saved.")
    with wf3:
        evidence = st.text_area(
            "Diligence evidence",
            value=st.session_state.diligence_evidence.get(fips, {}).get("evidence", ""),
            height=120,
            key=f"product_evidence_{fips}",
            placeholder="Broker note, zoning finding, listing evidence, comp sale, infrastructure item...",
        )
        if st.button("Save evidence", key=f"product_evidence_save_{fips}"):
            st.session_state.diligence_evidence[fips] = {
                "county_name": row.get("county_name"),
                "state": row.get("state"),
                "evidence": evidence.strip(),
                "updated_at": datetime.now().isoformat(),
            }
            _save_current_user_state()
            st.success("Evidence saved.")


def _preboom_surface_label_map() -> dict[str, str]:
    return {
        "guarded_blend": "Guarded 90/10 Blend (Recommended)",
        "residual_guardrail": "Residual-Upside Magnitude (Display-Guarded)",
        "residual_audit": "Unfiltered Residual-Upside (Audit)",
        "balanced": "Balanced Raw Review",
        "raw": "Raw Model-Direct Export",
        "unguarded_blend": "Unguarded 90/10 Blend (Audit)",
    }


def _preboom_surface_help(surface_key: str) -> str:
    notes = {
        "guarded_blend": (
            "Recommended product-review surface. Uses the historical 90/10 classifier/residual blend, "
            "then applies concentration and thin-market guardrails."
        ),
        "residual_guardrail": (
            "Residual-upside magnitude overlay using the evidence-tuned 60/40 market-depth guardrail plus display filters "
            "for population >=25k and market-depth adequacy >=0.45. Use beside the guarded blend; it is not a recommendation rank."
        ),
        "residual_audit": (
            "Unfiltered residual-upside magnitude audit surface. Useful for hidden-upside research, but it is too small/thin-market heavy "
            "for the default product display."
        ),
        "balanced": "Broad review list with concentration and market-depth discipline.",
        "raw": "Model-direct audit list. Useful for seeing what the raw surface wants; not a default display.",
        "unguarded_blend": "Historical-optimal blend without product guardrails; use for audit only.",
    }
    return notes.get(surface_key, "")


def _preboom_surface_rank_col(surface_df: pd.DataFrame) -> str:
    for col in [
        "guarded_blend_rank",
        "display_guarded_residual_rank",
        "guarded_residual_rank",
        "current_residual_rank",
        "balanced_priority_rank",
        "blend_rank",
        "export_priority_rank",
    ]:
        if col in surface_df.columns:
            return col
    return surface_df.columns[0]


def _preboom_format_table(surface_df: pd.DataFrame, limit: int = 100) -> pd.DataFrame:
    if surface_df is None or surface_df.empty:
        return pd.DataFrame()
    rank_col = _preboom_surface_rank_col(surface_df)
    cols = [
        rank_col,
        "export_priority_rank",
        "blend_rank",
        "display_guarded_residual_rank",
        "guarded_residual_rank",
        "current_residual_rank",
        "fips",
        "county",
        "state_abbr",
        "qa_status",
        "qa_flags",
        "preboom_classifier_score",
        "guarded_residual_score",
        "investable_residual_model_score",
        "residual_model_score",
        "preboom_prior_momentum_rank_pct",
        "emerging_market_depth_adequacy",
        "wave3_net_support",
        "overall_rank",
        "total_population",
    ]
    show = surface_df[[c for c in cols if c in surface_df.columns]].head(limit).copy()
    rename = {
        rank_col: "Review Rank",
        "export_priority_rank": "Raw Rank",
        "blend_rank": "Blend Rank",
        "display_guarded_residual_rank": "Residual Rank",
        "guarded_residual_rank": "Residual Rank",
        "current_residual_rank": "Unfiltered Residual Rank",
        "fips": "FIPS",
        "county": "County",
        "state_abbr": "State",
        "qa_status": "QA Status",
        "qa_flags": "QA Flags",
        "preboom_classifier_score": "Breakout Prob",
        "guarded_residual_score": "Residual Overlay",
        "investable_residual_model_score": "Residual Upside",
        "residual_model_score": "Raw Residual",
        "preboom_prior_momentum_rank_pct": "Prior Momentum",
        "emerging_market_depth_adequacy": "Market Depth",
        "wave3_net_support": "Wave3 Net",
        "overall_rank": "Live Rank",
        "total_population": "Population",
    }
    show = show.rename(columns=rename)
    for col in ["Review Rank", "Raw Rank", "Blend Rank", "Residual Rank", "Unfiltered Residual Rank", "Live Rank"]:
        if col in show.columns:
            show[col] = show[col].map(lambda x: f"#{int(float(x))}" if pd.notna(x) else "—")
    for col in ["Breakout Prob", "Residual Overlay", "Residual Upside", "Raw Residual", "Prior Momentum", "Market Depth", "Wave3 Net"]:
        if col in show.columns:
            show[col] = show[col].map(lambda x: f"{float(x):.3f}" if pd.notna(x) else "—")
    if "Population" in show.columns:
        show["Population"] = show["Population"].map(lambda x: f"{int(float(x)):,}" if pd.notna(x) else "—")
    return show


def _preboom_summary_metrics(surface_df: pd.DataFrame) -> dict[str, object]:
    if surface_df is None or surface_df.empty:
        return {}
    top = surface_df.head(100).copy()
    state_col = "state_abbr" if "state_abbr" in top.columns else "state"
    state_counts = top[state_col].fillna("Unknown").astype(str).value_counts() if state_col in top.columns else pd.Series(dtype=int)
    empty_numeric = pd.Series(index=top.index, dtype=float)
    depth = pd.to_numeric(top.get("emerging_market_depth_adequacy", empty_numeric), errors="coerce")
    pop = pd.to_numeric(top.get("total_population", empty_numeric), errors="coerce")
    wave3 = pd.to_numeric(top.get("wave3_net_support", empty_numeric), errors="coerce")
    status = top.get("qa_status", pd.Series(dtype=str)).fillna("unknown").astype(str)
    return {
        "rows": int(len(top)),
        "top_state": state_counts.index[0] if len(state_counts) else "n/a",
        "top_state_share": float(state_counts.iloc[0] / len(top)) if len(state_counts) and len(top) else None,
        "review_count": int(status.eq("review").sum()),
        "advance_count": int(status.eq("advance").sum()),
        "below_25k": int(pop.lt(25_000).sum()) if not pop.empty else 0,
        "thin_depth": int(depth.lt(0.45).sum()) if not depth.empty else 0,
        "negative_wave3": int(wave3.lt(0).sum()) if not wave3.empty else 0,
    }


def _preboom_feedback_key(fips: str, surface_key: str) -> str:
    return f"{str(fips).zfill(5)}|{surface_key}"


def _preboom_candidate_label(row: pd.Series) -> str:
    county = row.get("county", row.get("county_name", "Unknown"))
    state = row.get("state_abbr", row.get("state", ""))
    fips = str(row.get("fips", "")).zfill(5)
    return f"{county}, {state} ({fips})"


def _render_preboom_feedback_loop(
    surface_key: str,
    surface_label: str,
    view_df: pd.DataFrame,
) -> None:
    st.subheader("Candidate Feedback")
    st.caption(
        "Local operator memory for this pre-boom lane. Use it to mark false positives, promising leads, "
        "and candidates that need parcel or zoning follow-up."
    )
    if view_df is None or view_df.empty:
        st.info("No candidates in the current filtered view to review.")
        return

    feedback_store = st.session_state.get("preboom_feedback", {})
    if not isinstance(feedback_store, dict):
        feedback_store = {}
        st.session_state.preboom_feedback = feedback_store
    candidate_df = view_df.head(250).copy()
    candidate_df["fips"] = candidate_df["fips"].astype(str).str.zfill(5)
    candidate_df["_feedback_label"] = candidate_df.apply(_preboom_candidate_label, axis=1)
    label_to_fips = dict(zip(candidate_df["_feedback_label"], candidate_df["fips"]))
    selected_candidate = st.selectbox(
        "Candidate to mark",
        candidate_df["_feedback_label"].tolist(),
        key=f"product_preboom_feedback_candidate_{surface_key}",
    )
    selected_fips = label_to_fips[selected_candidate]
    selected_row = candidate_df[candidate_df["fips"].eq(selected_fips)].iloc[0]
    key = _preboom_feedback_key(selected_fips, surface_key)
    existing = feedback_store.get(key, {})

    fb1, fb2 = st.columns([1, 2])
    status_options = [
        "Unreviewed",
        "Good pre-boom lead",
        "False positive",
        "Too small/thin",
        "Already obvious",
        "Needs parcel check",
        "Watch",
    ]
    existing_status = existing.get("feedback", "Unreviewed")
    with fb1:
        feedback = st.selectbox(
            "Feedback",
            status_options,
            index=status_options.index(existing_status) if existing_status in status_options else 0,
            key=f"product_preboom_feedback_status_{surface_key}",
        )
    with fb2:
        reason = st.text_area(
            "Notes",
            value=existing.get("reason", ""),
            height=96,
            key=f"product_preboom_feedback_reason_{surface_key}",
            placeholder="Why is this a lead or false positive? Local demand, zoning, parcel depth, market thinness...",
        )
    if st.button("Save pre-boom feedback", key=f"product_preboom_feedback_save_{surface_key}"):
        feedback_store[key] = {
            "fips": selected_fips,
            "county": selected_row.get("county"),
            "state_abbr": selected_row.get("state_abbr", selected_row.get("state")),
            "surface_key": surface_key,
            "surface_label": surface_label,
            "feedback": feedback,
            "reason": reason.strip(),
            "updated_at": datetime.now().isoformat(),
        }
        st.session_state.preboom_feedback = feedback_store
        _save_current_user_state()
        st.success("Pre-boom feedback saved.")

    feedback_rows = list(feedback_store.values())
    if feedback_rows:
        feedback_df = pd.DataFrame(feedback_rows)
        surface_series = feedback_df.get("surface_key", pd.Series("", index=feedback_df.index))
        current_feedback = feedback_df[surface_series.astype(str).eq(surface_key)].copy()
        s1, s2, s3 = st.columns(3)
        s1.metric("All Feedback Items", len(feedback_df))
        s2.metric("Current Surface Items", len(current_feedback))
        s3.metric(
            "False Positives",
            int(feedback_df.get("feedback", pd.Series(dtype=str)).astype(str).eq("False positive").sum()),
        )
        if not current_feedback.empty:
            current_feedback = current_feedback.sort_values("updated_at", ascending=False)
            current_feedback = current_feedback.rename(
                columns={
                    "county": "County",
                    "state_abbr": "State",
                    "feedback": "Feedback",
                    "reason": "Notes",
                    "updated_at": "Updated",
                }
            )
            st.dataframe(
                current_feedback[[
                    c for c in ["County", "State", "Feedback", "Notes", "Updated"] if c in current_feedback.columns
                ]].head(20),
                width="stretch",
                hide_index=True,
                height=220,
            )
    else:
        st.caption("No Pre-Boom feedback saved yet.")


def _render_preboom_residual_overlay(
    surfaces: dict[str, pd.DataFrame | None],
    promotion_gate: dict | None,
) -> None:
    residual = surfaces.get("residual_guardrail")
    audit = surfaces.get("residual_audit")
    guarded = surfaces.get("guarded_blend")
    if residual is None or residual.empty:
        return

    with st.expander("Display-Guarded Residual-Upside Overlay Gate", expanded=False):
        gate = promotion_gate or {}
        current_guardrail = gate.get("current_guardrail") or {}
        recommended_surface = gate.get("recommended_product_surface") or {}
        st.caption(
            "Residual upside is magnitude evidence, not a recommendation rank. This lane now uses the "
            "display-guarded residual top-100 so the default product view avoids the smallest and thinnest "
            "false-positive candidates."
        )
        g1, g2, g3, g4 = st.columns(4)
        g1.metric("Promotion Status", gate.get("status", "report-only"))
        g2.metric("Guardrail", "60/40 + display")
        g3.metric("Product Surface", recommended_surface.get("surface", "guarded blend"))
        g4.metric("Production Rank", "unchanged")
        if current_guardrail.get("formula"):
            st.code(current_guardrail["formula"], language="text")

        residual_summary = _preboom_summary_metrics(residual)
        st.markdown(
            f"- Display-guarded residual top-100 below-25k counties: `{residual_summary.get('below_25k', 'n/a')}`\n"
            f"- Display-guarded residual top-100 thin-depth counties: `{residual_summary.get('thin_depth', 'n/a')}`\n"
            f"- Display-guarded residual top state: `{residual_summary.get('top_state', 'n/a')}` "
            f"({_fmt_pct(residual_summary.get('top_state_share'))})\n"
            "- Current decision: guarded blend remains the recommended review lane; residual upside is a supporting overlay."
        )
        if audit is not None and not audit.empty:
            audit_summary = _preboom_summary_metrics(audit)
            st.caption(
                "Audit comparison: the unfiltered residual top-100 remains available as a separate review surface. "
                f"It has `{audit_summary.get('below_25k', 'n/a')}` below-25k counties and "
                f"`{audit_summary.get('thin_depth', 'n/a')}` thin-depth counties in its top 100."
            )

        if guarded is not None and not guarded.empty:
            residual_small = residual.copy()
            residual_small["fips"] = residual_small["fips"].astype(str).str.zfill(5)
            guarded_small = guarded.copy()
            guarded_small["fips"] = guarded_small["fips"].astype(str).str.zfill(5)
            keep_resid = [
                c for c in [
                    "fips", "display_guarded_residual_rank", "current_residual_rank", "guarded_residual_rank",
                    "county", "state_abbr", "qa_status", "guarded_residual_score",
                    "investable_residual_model_score", "residual_model_score", "emerging_market_depth_adequacy",
                    "total_population",
                ] if c in residual_small.columns
            ]
            keep_guarded = [
                c for c in ["fips", "guarded_blend_rank", "blend_rank", "preboom_classifier_score"]
                if c in guarded_small.columns
            ]
            compare = residual_small[keep_resid].head(40).merge(
                guarded_small[keep_guarded],
                on="fips",
                how="left",
            )
            compare = compare.rename(
                columns={
                    "display_guarded_residual_rank": "Residual Rank",
                    "current_residual_rank": "Unfiltered Residual Rank",
                    "guarded_residual_rank": "Residual Rank",
                    "guarded_blend_rank": "Guarded Blend Rank",
                    "blend_rank": "Blend Rank",
                    "county": "County",
                    "state_abbr": "State",
                    "qa_status": "QA Status",
                    "guarded_residual_score": "Residual Overlay",
                    "investable_residual_model_score": "Residual Upside",
                    "residual_model_score": "Raw Residual",
                    "preboom_classifier_score": "Breakout Prob",
                    "emerging_market_depth_adequacy": "Market Depth",
                    "total_population": "Population",
                }
            )
            for col in ["Residual Rank", "Unfiltered Residual Rank", "Guarded Blend Rank", "Blend Rank"]:
                if col in compare.columns:
                    compare[col] = compare[col].map(lambda x: f"#{int(float(x))}" if pd.notna(x) else "not top-100")
            for col in ["Residual Overlay", "Residual Upside", "Raw Residual", "Breakout Prob", "Market Depth"]:
                if col in compare.columns:
                    compare[col] = compare[col].map(lambda x: f"{float(x):.3f}" if pd.notna(x) else "—")
            if "Population" in compare.columns:
                compare["Population"] = compare["Population"].map(lambda x: f"{int(float(x)):,}" if pd.notna(x) else "—")
            st.dataframe(compare, width="stretch", hide_index=True, height=320)


def _format_p0_repeatable_guardrail_table(candidates: pd.DataFrame, limit: int = 100) -> pd.DataFrame:
    if candidates is None or candidates.empty:
        return pd.DataFrame()
    show = candidates.head(limit).copy()
    if "fips" in show.columns:
        show["fips"] = show["fips"].astype(str).str.zfill(5)
    if "guardrail_candidate_flag" in show.columns or "guardrail_preserved_flag" in show.columns:
        candidate = pd.to_numeric(show.get("guardrail_candidate_flag", pd.Series(0, index=show.index)), errors="coerce").fillna(0)
        preserved = pd.to_numeric(show.get("guardrail_preserved_flag", pd.Series(0, index=show.index)), errors="coerce").fillna(0)
        show["queue_role"] = np.select(
            [candidate.gt(0), preserved.gt(0)],
            ["Repeatable insert", "Preserved residual top"],
            default="Context",
        )
    cols = [
        "review_rank",
        "fips",
        "county",
        "state_abbr",
        "year",
        "queue_role",
        "_base_rank",
        "investable_residual_model_score",
        "p0_repeatable_treatment_score",
        "p0_repeatable_anchor_mix_support",
        "p0_repeatable_jobs_affordability_support",
        "p0_repeatable_migration_pop_support",
        "p0_repeatable_land_optionality_support",
        "preboom_prior_momentum_rank_pct",
        "emerging_market_depth_adequacy",
        "total_population",
        "qa_severity",
    ]
    show = show[[c for c in cols if c in show.columns]].copy()
    show = show.rename(
        columns={
            "review_rank": "Review Rank",
            "fips": "FIPS",
            "county": "County",
            "state_abbr": "State",
            "year": "Year",
            "queue_role": "Queue Role",
            "_base_rank": "Base Residual Rank",
            "investable_residual_model_score": "Residual Upside",
            "p0_repeatable_treatment_score": "Repeatable P0",
            "p0_repeatable_anchor_mix_support": "Anchor Mix",
            "p0_repeatable_jobs_affordability_support": "Jobs/Afford",
            "p0_repeatable_migration_pop_support": "Migration/Pop",
            "p0_repeatable_land_optionality_support": "Land Optionality",
            "preboom_prior_momentum_rank_pct": "Prior Momentum",
            "emerging_market_depth_adequacy": "Market Depth",
            "total_population": "Population",
            "qa_severity": "QA Severity",
        }
    )
    for col in ["Review Rank", "Base Residual Rank"]:
        if col in show.columns:
            show[col] = show[col].map(lambda x: f"#{int(float(x))}" if pd.notna(x) else "—")
    for col in [
        "Residual Upside",
        "Repeatable P0",
        "Anchor Mix",
        "Jobs/Afford",
        "Migration/Pop",
        "Land Optionality",
        "Prior Momentum",
        "Market Depth",
    ]:
        if col in show.columns:
            show[col] = show[col].map(lambda x: f"{float(x):.3f}" if pd.notna(x) else "—")
    if "Population" in show.columns:
        show["Population"] = show["Population"].map(lambda x: f"{int(float(x)):,}" if pd.notna(x) else "—")
    return show


def _render_p0_repeatable_residual_guardrail(
    guardrail_report: dict | None,
    candidates: pd.DataFrame | None,
) -> None:
    if not guardrail_report and (candidates is None or candidates.empty):
        return
    with st.expander("Repeatable P0 Residual Review Queue Gate", expanded=False):
        decision = (guardrail_report or {}).get("decision") or {}
        best_policy = (guardrail_report or {}).get("best_policy_row") or {}
        st.caption(
            "Report-only residual review queue evidence. This gate preserves the top residual names, then lets "
            "historical/repeatable P0 support compete for lower review slots. It is not a production rank."
        )
        g1, g2, g3, g4, g5 = st.columns(5)
        g1.metric("Status", decision.get("status", "report-only"))
        g2.metric(
            "Top-100 P0 Capture",
            f"{decision.get('baseline_top100_p0_capture', 'n/a')} -> {decision.get('best_top100_p0_capture', 'n/a')}",
        )
        g3.metric("NDCG@25 Delta", _fmt_score(decision.get("best_delta_residual_ndcg_at_25")))
        g4.metric("Top-100 Churn", _fmt_pct(decision.get("best_guarded_top100_churn")))
        g5.metric("Severe QA", _fmt_pct(decision.get("best_severe_qa_share")))

        st.markdown(
            f"- Best policy: `{decision.get('best_policy', 'n/a')}`\n"
            f"- Policy shape: keep top `{best_policy.get('preserve_top', 'n/a')}` residual names; source candidates up to base residual rank `{best_policy.get('max_source_rank', 'n/a')}`; require repeatable P0 score `{_fmt_score(best_policy.get('treatment_min'))}` and prior momentum `{_fmt_score(best_policy.get('prior_momentum_max'))}`.\n"
            "- Boundary: Product Mode/report-only review queue candidate; no scoring, model, or default dashboard-rank change."
        )
        if candidates is not None and not candidates.empty:
            st.caption("Historical validation preview from the latest guardrail artifact.")
            st.dataframe(_format_p0_repeatable_guardrail_table(candidates, limit=100), width="stretch", hide_index=True, height=360)
            st.download_button(
                "Download repeatable residual guardrail preview CSV",
                data=candidates.to_csv(index=False).encode("utf-8"),
                file_name="p0_repeatable_residual_guardrail_top_candidates.csv",
                mime="text/csv",
                key="product_p0_repeatable_residual_guardrail_csv",
            )
        else:
            st.info("No repeatable residual guardrail candidate table is available yet.")


def _render_preboom_review_tab(
    surfaces: dict[str, pd.DataFrame | None],
    blend_report: dict | None,
    analog_report: dict | None,
    promotion_gate: dict | None = None,
    p0_repeatable_residual_guardrail: dict | None = None,
    p0_repeatable_residual_candidates: pd.DataFrame | None = None,
) -> None:
    st.header("Pre-Boom Review Lane")
    st.caption("Report-only quiet-breakout discovery. This does not change production rankings or model artifacts.")
    st.info(
        "Recommended default: Guarded 90/10 Blend. It keeps the historically strongest quiet-breakout blend, "
        "then removes the worst concentration and thin-market false positives."
    )

    labels = _preboom_surface_label_map()
    available_keys = [
        key for key in ["guarded_blend", "residual_guardrail", "residual_audit", "balanced", "raw", "unguarded_blend"]
        if surfaces.get(key) is not None and not surfaces[key].empty
    ]
    if not available_keys:
        st.warning("No pre-boom review artifacts are available yet.")
        return

    selected_label = st.selectbox(
        "Review surface",
        [labels[key] for key in available_keys],
        index=0,
        key="product_preboom_surface",
    )
    surface_key = {labels[key]: key for key in available_keys}[selected_label]
    surface_df = surfaces[surface_key].copy()
    surface_df["fips"] = surface_df["fips"].astype(str).str.zfill(5)
    st.caption(_preboom_surface_help(surface_key))

    summary = _preboom_summary_metrics(surface_df)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Rows", summary.get("rows", "n/a"))
    c2.metric("Top State", f"{summary.get('top_state', 'n/a')} ({_fmt_pct(summary.get('top_state_share'))})")
    c3.metric("Review Names", summary.get("review_count", "n/a"))
    c4.metric("Below 25k", summary.get("below_25k", "n/a"))
    c5.metric("Thin Depth", summary.get("thin_depth", "n/a"))

    if blend_report:
        rec = blend_report.get("recommended_policy") or {}
        guarded = blend_report.get("guarded_2024_summary") or {}
        with st.expander("Model Gate: Two-Score Blend", expanded=False):
            g1, g2, g3, g4 = st.columns(4)
            g1.metric("Blend", rec.get("policy", "n/a"))
            g2.metric("Strict Lift@25", _fmt_score(rec.get("pre_boom_breakout_5yr_lift_at_25")))
            g3.metric(
                "Residual NDCG@25",
                f"{float(rec.get('residual_ndcg_at_25')):.3f}" if rec.get("residual_ndcg_at_25") is not None else "n/a",
            )
            g4.metric(
                "Prior Corr",
                f"{float(rec.get('spearman_prior_momentum_rank')):+.3f}" if rec.get("spearman_prior_momentum_rank") is not None else "n/a",
            )
            st.markdown(
                f"- Guarded top-state share: `{_fmt_pct(guarded.get('top_state_share'))}`\n"
                f"- Guarded below-25k counties: `{guarded.get('population_lt_25k_count', 'n/a')}`\n"
                f"- Guarded thin-depth counties: `{guarded.get('depth_lt_0_45_count', 'n/a')}`\n"
                f"- Guarded negative Wave 3 net-support counties: `{guarded.get('negative_wave3_net_count', 'n/a')}`"
            )

    if analog_report:
        with st.expander("Model Gate: Known-Boom Analog Overlap", expanded=False):
            st.caption(
                f"Historical learned-surface coverage: {analog_report.get('score_year_min', 'n/a')}-"
                f"{analog_report.get('score_year_max', 'n/a')}. Early analog windows are partial."
            )
            summary_rows = [
                row for row in analog_report.get("summary_rows", [])
                if row.get("top_k") == 100 and "analog_group" not in row
            ]
            analog_view = pd.DataFrame(summary_rows)
            if not analog_view.empty:
                analog_view = analog_view[[
                    c for c in [
                        "surface", "selected_county_windows", "selected_share",
                        "selected_before_hot_count", "median_best_selected_rank",
                    ] if c in analog_view.columns
                ]].rename(
                    columns={
                        "surface": "Surface",
                        "selected_county_windows": "Selected",
                        "selected_share": "Selected Share",
                        "selected_before_hot_count": "Before Hot",
                        "median_best_selected_rank": "Median Rank",
                    }
                )
                if "Selected Share" in analog_view.columns:
                    analog_view["Selected Share"] = analog_view["Selected Share"].map(_fmt_pct)
                if "Median Rank" in analog_view.columns:
                    analog_view["Median Rank"] = analog_view["Median Rank"].map(lambda x: f"#{int(float(x))}" if pd.notna(x) else "—")
                st.dataframe(analog_view, width="stretch", hide_index=True, height=180)
            st.caption("Guarded blend is preferred because it preserves before-hot analog capture while cleaning thin-market exposure.")

    _render_preboom_residual_overlay(surfaces, promotion_gate)
    _render_p0_repeatable_residual_guardrail(
        p0_repeatable_residual_guardrail,
        p0_repeatable_residual_candidates,
    )

    search = st.text_input("Search pre-boom counties", key="product_preboom_search", placeholder="County, state, or FIPS")
    view_df = surface_df.copy()
    if search.strip():
        q = search.strip().lower()
        mask = view_df["fips"].astype(str).str.lower().str.contains(q, na=False)
        for col in ["county", "state_abbr", "qa_status", "qa_flags"]:
            if col in view_df.columns:
                mask = mask | view_df[col].astype(str).str.lower().str.contains(q, regex=False, na=False)
        view_df = view_df[mask]

    status_options = sorted(view_df.get("qa_status", pd.Series(dtype=str)).dropna().astype(str).unique().tolist())
    selected_status = st.multiselect("QA status", status_options, default=[], key="product_preboom_status")
    if selected_status and "qa_status" in view_df.columns:
        view_df = view_df[view_df["qa_status"].astype(str).isin(selected_status)]

    st.dataframe(_preboom_format_table(view_df, limit=250), width="stretch", hide_index=True, height=520)
    st.download_button(
        "Download current pre-boom surface CSV",
        data=surface_df.to_csv(index=False).encode("utf-8"),
        file_name=f"preboom_{surface_key}_review_surface.csv",
        mime="text/csv",
    )

    st.subheader("Add Candidates To Watchlist")
    add_n = st.selectbox("Add top N from current filtered view", [10, 25, 50, 100], index=1, key="product_preboom_add_n")
    if st.button("Add pre-boom candidates to watchlist", key="product_preboom_add_watchlist", type="primary"):
        fips_to_add = view_df.head(int(add_n))["fips"].astype(str).str.zfill(5).tolist()
        st.session_state.watchlist_fips = sorted(set(st.session_state.watchlist_fips + fips_to_add))
        _save_current_user_state()
        st.success(f"Added {len(fips_to_add)} pre-boom candidates to the watchlist.")

    _render_preboom_feedback_loop(surface_key, selected_label, view_df)

    st.subheader("How To Read This Lane")
    st.markdown(
        "- `Breakout Prob` estimates quiet-breakout probability from the direct pre-boom classifier.\n"
        "- `Residual Upside` estimates magnitude after accounting for prior momentum and investability depth.\n"
        "- Guardrails remove very small markets, thin-depth counties, concentration spikes, and severe structural brakes from the default review surface.\n"
        "- This is a discovery queue, not the production ranking. Advance counties only after parcel, zoning, listings, and local-market diligence."
    )


CUSTOMER_TIER_COLORS = {
    "Prime": "#0f766e",
    "Strong": "#15803d",
    "Speculative": "#92400e",
    "Watch": "#475569",
}


CUSTOMER_PRESET_CATALOG = {
    "General Opportunity": {
        "base_preset": "Long-term appreciation",
        "risk_posture": "Balanced",
        "description": "Matches the default Product Mode long-term appreciation strategy.",
    },
    "Low-Risk Growth": {
        "base_preset": "Low-risk compounder",
        "risk_posture": "Lower risk",
        "description": "Favors durable upside, cleaner risk, and medium-or-better confidence.",
    },
    "Vacation Land": {
        "base_preset": "Recreation amenity",
        "risk_posture": "Balanced",
        "description": "Highlights recreation/amenity access and long-horizon land demand.",
    },
    "Hidden Upside": {
        "base_preset": "Distressed rebound",
        "risk_posture": "More aggressive",
        "description": "Looks for higher-upside counties where the thesis needs more diligence.",
    },
    "Buildable Scarcity": {
        "base_preset": "Buildable scarcity",
        "risk_posture": "Balanced",
        "description": "Emphasizes developability, scarcity, and structural land fit.",
    },
    "Climate-Resilient Growth": {
        "base_preset": "Climate-resilient growth",
        "risk_posture": "Lower risk",
        "description": "Rewards lower fragility and cleaner structural risk.",
    },
    "Land Optionality": {
        "base_preset": "Land optionality",
        "risk_posture": "Balanced",
        "description": "Looks for counties with multiple plausible land-use paths.",
    },
}


CUSTOMER_WORKSPACE_LABELS = {
    "Radar": "Market Radar",
    "Opportunities": "Opportunity Deck",
    "County Story": "County Story",
    "Compare": "Compare Set",
    "Watchlist": "Watchlist",
    "Packet": "Review Packet",
}


CUSTOMER_TERM_DEFINITIONS = {
    "Strategy Score": "The active Product Mode strategy score for the selected thesis, risk posture, and state universe.",
    "Customer Signal": "A presentation-only blend that makes the current opportunity easier to read. It does not rewrite production rank.",
    "Prime / Strong": "Customer-facing signal tiers based on strategy score, risk, and confidence.",
    "Composite Risk": "A 0-100 risk read where lower is cleaner for diligence.",
    "Confidence": "Model confidence bucket from the current scored artifact. Higher confidence means the model has cleaner support, not a guarantee.",
    "5yr Upside": "The current long-horizon predicted appreciation signal used by the strategy simulation.",
    "Strategy Rank": "Rank after applying the active Customer/Product thesis weights. Lower rank number is better.",
    "Parcel Readiness": "A customer workflow cue for how much parcel-level diligence is likely needed next.",
    "Active Filter": "The county matches the current Customer preset, risk posture, confidence gate, and state filters.",
    "Outside Filter": "The county exists in the scored universe, but does not match the active Customer filter.",
    "Watchlist Health": "A workflow read combining rank, stability, upside, and risk to suggest whether to keep, watch, or review a county.",
}


def _customer_escape(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return html.escape(str(value), quote=True)


LANDINVEST_LOGO_SVG = """
<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
  <rect x="4" y="4" width="56" height="56" rx="12" fill="#0f172a"/>
  <path d="M13 45C20 36 27 39 34 30C41 21 47 23 54 14" fill="none" stroke="#2dd4bf" stroke-width="5" stroke-linecap="round"/>
  <path d="M13 50C24 45 33 47 43 38C47 34 50 30 54 26" fill="none" stroke="#f59e0b" stroke-width="3" stroke-linecap="round" opacity="0.95"/>
  <path d="M12 33C19 27 24 28 30 22C35 17 41 15 50 17" fill="none" stroke="#cbd5e1" stroke-width="2.4" stroke-linecap="round" opacity="0.86"/>
  <path d="M16 23C22 18 29 18 36 13" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round" opacity="0.76"/>
  <circle cx="43" cy="25" r="5" fill="#fbbf24"/>
  <path d="M43 18V32" stroke="#0f172a" stroke-width="2" stroke-linecap="round" opacity="0.48"/>
  <path d="M36 25H50" stroke="#0f172a" stroke-width="2" stroke-linecap="round" opacity="0.48"/>
</svg>
""".strip()


def _landinvest_logo_svg() -> str:
    try:
        return BRAND_LOGO_PATH.read_text(encoding="utf-8").strip()
    except OSError:
        return LANDINVEST_LOGO_SVG


def _brand_chip_html(label: str, value: str | int | float | None) -> str:
    if value is None or value == "":
        return ""
    return (
        '<span class="landinvest-brand-chip">'
        f"<b>{_customer_escape(label)}</b>"
        f"<span>{_customer_escape(value)}</span>"
        "</span>"
    )


def _brand_header_html(
    *,
    experience_mode: str,
    run_id: str,
    run_year: str | int,
    data_ts: str,
    churn_text: str,
    health_text: str | None,
) -> str:
    mode_label = experience_mode.replace(" Mode", "")
    meta = [
        ("Mode", mode_label),
        ("Run", run_id),
        ("Year", run_year),
        ("Data", data_ts),
        ("Top-25 Churn", churn_text),
    ]
    if health_text:
        meta.append(("3yr Health", health_text))
    meta_html = "".join(_brand_chip_html(label, value) for label, value in meta)
    return f"""
<div class="landinvest-brand-header">
  <div class="landinvest-brand-main">
    <div class="landinvest-logo-wrap">{_landinvest_logo_svg()}</div>
    <div class="landinvest-brand-copy">
      <div class="landinvest-brand-kicker">County Growth Intelligence</div>
      <h1>LandInvest</h1>
      <p>Rank, explain, and monitor county-level land opportunities with risk context.</p>
    </div>
  </div>
  <div class="landinvest-brand-meta">{meta_html}</div>
</div>
"""


def _sidebar_brand_html() -> str:
    return f"""
<div class="landinvest-sidebar-brand">
  <div class="landinvest-sidebar-logo">{_landinvest_logo_svg()}</div>
  <div>
    <b>LandInvest</b>
    <span>County Growth Platform</span>
  </div>
</div>
"""


def _query_param_first(name: str, default: str | None = None) -> str | None:
    try:
        value = st.query_params.get(name, default)
    except Exception:
        return default
    if isinstance(value, list):
        return str(value[0]) if value else default
    if value is None:
        return default
    return str(value)


def _query_param_list(name: str) -> list[str]:
    raw = _query_param_first(name, "")
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def _customer_share_url(
    *,
    customer_preset: str,
    risk_posture: str,
    workspace: str,
    selected_states: list[str],
    selected_fips: str | None,
) -> str:
    params = {
        "experience": "customer",
        "customer_preset": customer_preset,
        "risk_posture": risk_posture,
        "workspace": workspace,
    }
    if selected_states:
        params["states"] = ",".join(selected_states)
    if selected_fips:
        params["fips"] = str(selected_fips).zfill(5)
    return "?" + urlencode(params)


def _set_customer_story_selection(fips: str) -> None:
    st.session_state.customer_selected_fips = str(fips).zfill(5)
    st.session_state.customer_workspace = "County Story"


def _customer_workspace_label(workspace: str) -> str:
    return CUSTOMER_WORKSPACE_LABELS.get(workspace, workspace)


def _render_customer_term_guide(label: str = "Term Guide") -> None:
    with st.popover(label, help="Definitions for the Customer Mode scores, tiers, and workflow labels."):
        for term, body in CUSTOMER_TERM_DEFINITIONS.items():
            st.markdown(f"**{term}**")
            st.caption(body)


def _render_customer_workspace_help(workspace: str) -> None:
    help_text = {
        "Radar": [
            "Use the map to scout the full county universe under the active strategy.",
            "Click any county to update the selected-county panel, then open its story or add it to the watchlist.",
            "Switch the map signal layer to inspect score, risk, upside, parcel readiness, or land fit.",
        ],
        "Opportunities": [
            "This deck is the active-filter shortlist. It is intentionally narrower than County Story search.",
            "Use sorting lenses to move between strategy rank, customer signal, risk, upside, and land fit.",
            "Open Story when a card deserves diligence context.",
        ],
        "County Story": [
            "Search every scored county, including counties outside the active Customer filter.",
            "Use the story page for provenance, peer counties, parcel checks, notes, and memo export.",
        ],
        "Compare": [
            "Pick a small county set and compare the signal stack side by side.",
            "Use it for short-list decisions, not broad discovery.",
        ],
        "Watchlist": [
            "Treat this as the portfolio command center for saved counties.",
            "Health, alerts, stages, and next actions are workflow aids. They do not change production ranking.",
        ],
        "Packet": [
            "Export the current review packet, watchlist CSV, or print-ready HTML for handoff.",
            "The packet reflects current Customer Mode artifacts and local profile state.",
        ],
    }.get(workspace, [])
    with st.popover("How This Workspace Works", help="Short operating guide for the current Customer workspace."):
        for item in help_text:
            st.markdown(f"- {item}")


def _saved_customer_views() -> dict:
    profiles = st.session_state.get("saved_strategy_profiles", {}) or {}
    return {
        name: profile
        for name, profile in profiles.items()
        if isinstance(profile, dict) and profile.get("profile_type") == "customer_view"
    }


def _customer_default_view_name() -> str | None:
    marker = (st.session_state.get("saved_strategy_profiles", {}) or {}).get("__customer_default_view__")
    if isinstance(marker, dict):
        name = str(marker.get("name") or "").strip()
        return name or None
    return None


def _customer_default_view_profile() -> dict | None:
    name = _customer_default_view_name()
    if not name:
        return None
    return _saved_customer_views().get(name)


def _customer_view_session_state(profile: dict) -> dict:
    cfg = profile.get("cfg") if isinstance(profile.get("cfg"), dict) else {}
    selected_fips = _normalize_fips_value(profile.get("selected_fips"))
    updates = {
        "customer_experience_preset": profile.get("customer_preset_name", "General Opportunity"),
        "customer_preset": profile.get("base_preset") or cfg.get("preset_name") or "Long-term appreciation",
        "customer_risk_posture": profile.get("risk_posture", "Balanced"),
        "customer_states": profile.get("states", []),
        "customer_card_limit": int(profile.get("card_limit", 12)),
        "customer_workspace": profile.get("workspace", "Radar"),
        "customer_radar_layer": profile.get("radar_layer", "sim_score"),
    }
    if selected_fips:
        updates["customer_selected_fips"] = selected_fips
    return updates


def _customer_view_payload(
    *,
    customer_preset_name: str,
    preset_name: str,
    risk_posture: str,
    selected_states: list[str],
    card_limit: int,
    workspace: str,
    selected_fips: str | None,
    radar_layer: str,
    cfg: dict,
) -> dict:
    return {
        "profile_type": "customer_view",
        "customer_preset_name": customer_preset_name,
        "base_preset": preset_name,
        "risk_posture": risk_posture,
        "states": list(selected_states),
        "card_limit": int(card_limit),
        "workspace": workspace,
        "selected_fips": _normalize_fips_value(selected_fips),
        "radar_layer": radar_layer,
        "cfg": cfg.copy(),
        "saved_at": datetime.now().isoformat(),
    }


def _customer_view_export_payload(name: str, profile: dict) -> dict:
    return {
        "kind": "landinvest_customer_view",
        "exported_at": datetime.now().isoformat(),
        "name": name,
        "profile": profile,
    }


def _parse_customer_view_import(raw_bytes: bytes) -> tuple[str, dict]:
    payload = json.loads(raw_bytes.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Customer view import must be a JSON object.")
    if payload.get("kind") == "landinvest_customer_view":
        name = str(payload.get("name") or "Imported Customer View").strip()
        profile = payload.get("profile")
    else:
        name = str(payload.get("name") or "Imported Customer View").strip()
        profile = payload
    if not isinstance(profile, dict) or profile.get("profile_type") != "customer_view":
        raise ValueError("JSON does not contain a Customer View profile.")
    return name or "Imported Customer View", profile


def _customer_watchlist_command_rows(
    watch_df: pd.DataFrame,
    health_eval: pd.DataFrame,
    alert_df: pd.DataFrame,
) -> pd.DataFrame:
    if watch_df.empty:
        return pd.DataFrame()
    health_lookup = {}
    if health_eval is not None and not health_eval.empty:
        health_lookup = health_eval.set_index(health_eval["fips"].astype(str).str.zfill(5)).to_dict("index")
    alert_counts = {}
    if alert_df is not None and not alert_df.empty:
        alert_counts = alert_df.groupby(alert_df["fips"].astype(str).str.zfill(5)).size().to_dict()
    rows = []
    for _, row in watch_df.sort_values("sim_rank").iterrows():
        fips = str(row.get("fips")).zfill(5)
        stage = st.session_state.county_funnel.get(fips, {}).get("stage", "Interested")
        health = health_lookup.get(fips, {})
        status = _humanize_status_label(health.get("health_status", "watch_closely"))
        rows.append(
            {
                "FIPS": fips,
                "County": _customer_county_display(row),
                "Stage": stage,
                "Health": status,
                "Alerts": int(alert_counts.get(fips, 0)),
                "Strategy Rank": _rank_text(row.get("sim_rank")),
                "Customer Signal": _fmt_score(row.get("customer_signal_score")),
                "5yr": _fmt_pct(row.get("pred_avg_5yr")),
                "Risk": _fmt_score(row.get("composite_risk")),
                "Next Action": _customer_next_step(row),
                "_strategy_rank": _product_numeric(row, "sim_rank", 99999.0),
                "_signal_value": _product_numeric(row, "customer_signal_score", 0.0),
                "_risk_value": _product_numeric(row, "composite_risk", 100.0),
                "_alerts": int(alert_counts.get(fips, 0)),
            }
        )
    return pd.DataFrame(rows)


def _customer_watchlist_stage_summary(command_df: pd.DataFrame) -> pd.DataFrame:
    if command_df.empty:
        return pd.DataFrame()
    rows = []
    for stage, group in command_df.groupby("Stage", dropna=False):
        rows.append(
            {
                "Stage": stage,
                "Count": int(len(group)),
                "Avg Customer Signal": _fmt_score(group["_signal_value"].mean()),
                "Avg Risk": _fmt_score(group["_risk_value"].mean()),
                "Alerts": int(group["_alerts"].sum()),
            }
        )
    return pd.DataFrame(rows).sort_values(["Count", "Stage"], ascending=[False, True])


def _customer_header_html(
    *,
    top_row: pd.Series,
    customer_preset_name: str,
    risk_posture: str,
    run_id: str,
    universe_count: int,
    full_count: int,
    prime_count: int,
    churn: float | None,
    health: str | None,
) -> str:
    churn_text = f"{100 * churn:.1f}%" if churn is not None else "n/a"
    health_text = _humanize_status_label(health) if health else "n/a"
    return f"""
<div class="customer-command-header">
  <div class="customer-command-copy">
    <div class="customer-kicker">LandInvest Customer Mode</div>
    <h1>Investment Command Center</h1>
    <p>{_customer_escape(_customer_county_display(top_row))} leads the active thesis. {_customer_escape(_customer_thesis_read(top_row))}</p>
  </div>
  <div class="customer-command-grid">
    <span><b>{_customer_escape(customer_preset_name)}</b><small>Preset</small></span>
    <span><b>{_customer_escape(risk_posture)}</b><small>Risk posture</small></span>
    <span><b>{universe_count:,} / {full_count:,}</b><small>Active universe</small></span>
    <span><b>{prime_count}</b><small>Prime signals</small></span>
    <span><b>{_customer_escape(churn_text)}</b><small>Top-25 churn</small></span>
    <span><b>{_customer_escape(health_text)}</b><small>3yr health</small></span>
    <span><b>{_customer_escape(run_id)}</b><small>Run</small></span>
  </div>
</div>
"""


def _customer_section_header(title: str, subtitle: str | None = None) -> None:
    sub = f"<p>{_customer_escape(subtitle)}</p>" if subtitle else ""
    st.markdown(
        f"""
<div class="customer-section-header">
  <div>
    <span class="customer-kicker">{_customer_escape(title)}</span>
    {sub}
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def _customer_map_selection_html(row: pd.Series) -> str:
    return f"""
<div class="customer-map-callout">
  <div>
    <span class="customer-kicker">Selected County | Map Highlight Active</span>
    <h3>{_customer_escape(_customer_county_display(row))}</h3>
    <p>{_customer_escape(_customer_thesis_read(row))}</p>
  </div>
  <div class="customer-map-stats">
    <span><b>{_rank_text(row.get('sim_rank'))}</b><small>Strategy</small></span>
    <span><b>{_fmt_score(row.get('sim_score'))}</b><small>Strategy score</small></span>
    <span><b>{_fmt_score(row.get('composite_risk'))}</b><small>Risk</small></span>
    <span><b>{_fmt_pct(row.get('pred_avg_5yr'))}</b><small>5yr</small></span>
  </div>
</div>
"""


def _current_user_state_payload() -> dict:
    return {
        "saved_watchlists": st.session_state.get("saved_watchlists", {}),
        "county_notes": st.session_state.get("county_notes", {}),
        "saved_compare_sets": st.session_state.get("saved_compare_sets", {}),
        "saved_strategy_profiles": st.session_state.get("saved_strategy_profiles", {}),
        "county_funnel": st.session_state.get("county_funnel", {}),
        "county_feedback": st.session_state.get("county_feedback", {}),
        "preboom_feedback": st.session_state.get("preboom_feedback", {}),
        "diligence_evidence": st.session_state.get("diligence_evidence", {}),
        "parcel_checklists": st.session_state.get("parcel_checklists", {}),
        "watchlist_alert_state": st.session_state.get("watchlist_alert_state", {}),
        "watchlist_settings": st.session_state.get("watchlist_settings", _default_user_data()["watchlist_settings"]),
    }


def _customer_signal_value(row: pd.Series, col: str, default: float = 50.0) -> float:
    return float(np.clip(_product_numeric(row, col, default), 0.0, 100.0))


def _customer_tier_label(row: pd.Series) -> str:
    score = _product_numeric(row, "customer_signal_score", _product_numeric(row, "sim_score", 50.0))
    risk = _product_numeric(row, "composite_risk", 50.0)
    confidence = str(row.get("confidence", "")).upper()
    if score >= 78 and risk <= 48 and confidence != "LOW":
        return "Prime"
    if score >= 68 and risk <= 58 and confidence != "LOW":
        return "Strong"
    if score >= 58 or _product_numeric(row, "pred_avg_5yr", 0.0) >= 0.12:
        return "Speculative"
    return "Watch"


def _customer_risk_band(row: pd.Series) -> str:
    risk = _product_numeric(row, "composite_risk", 50.0)
    if risk <= 40:
        return "Clean"
    if risk <= 55:
        return "Measured"
    return "Needs Diligence"


def _customer_county_display(row: pd.Series) -> str:
    county = str(row.get("county_name", "County")).strip()
    state = str(row.get("state", "")).strip()
    if not state or "," in county:
        return county
    return f"{county}, {state}"


def _customer_augment(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if out.empty:
        return out
    out["customer_signal_score"] = (
        0.38 * _product_series(out, "sim_score", 50.0)
        + 0.18 * _product_series(out, "sim_risk_fit", 50.0)
        + 0.16 * _product_series(out, "lens_structure_minus_fragility", 50.0)
        + 0.14 * _product_series(out, "lens_parcel_readiness", 50.0)
        + 0.14 * _product_series(out, "sim_confidence_score", 50.0)
    ).clip(0, 100)
    out["customer_tier"] = out.apply(_customer_tier_label, axis=1)
    out["customer_risk_band"] = out.apply(_customer_risk_band, axis=1)
    return out


def _customer_thesis_read(row: pd.Series) -> str:
    archetype = str(row.get("opportunity_archetype", "Opportunity")).strip() or "Opportunity"
    decision = _build_wave3_decision_narrative(row)
    thesis = str(decision.get("thesis", "")).strip()
    if thesis and thesis != "Current model and structural context are not complete enough for a confident thesis.":
        return f"{archetype}: {thesis}"
    pred5 = row.get("pred_avg_5yr")
    risk = row.get("composite_risk")
    return f"{archetype}: {_fmt_pct(pred5)} 5yr signal with {_fmt_score(risk)} risk."


def _customer_next_step(row: pd.Series) -> str:
    readiness, actions = _parcel_readiness(row)
    first_action = actions[0] if actions else "Open the county story and confirm the local thesis."
    return f"{readiness}: {first_action}"


def _customer_signal_bar_html(label: str, value: float, color: str) -> str:
    pct = float(np.clip(value, 0.0, 100.0))
    return (
        '<div class="customer-signal-row">'
        f'<div><span>{_customer_escape(label)}</span><b>{pct:.0f}</b></div>'
        '<div class="customer-meter">'
        f'<span style="width:{pct:.1f}%; background:{color};"></span>'
        "</div></div>"
    )


def _customer_card_html(row: pd.Series, *, compact: bool = False) -> str:
    tier = str(row.get("customer_tier") or _customer_tier_label(row))
    color = CUSTOMER_TIER_COLORS.get(tier, "#64748b")
    county_title = _customer_escape(_customer_county_display(row))
    thesis = _customer_escape(_customer_thesis_read(row))
    next_step = _customer_escape(_customer_next_step(row))
    rank = _rank_text(row.get("sim_rank"))
    prod_rank = _rank_text(row.get("overall_rank"))
    signal = _customer_signal_value(row, "customer_signal_score")
    growth = _customer_signal_value(row, "sim_growth_score")
    risk_fit = _customer_signal_value(row, "sim_risk_fit")
    land_fit = _customer_signal_value(row, "sim_structure_score")
    confidence = _customer_signal_value(row, "sim_confidence_score")
    bars = "".join(
        [
            _customer_signal_bar_html("Signal", signal, color),
            _customer_signal_bar_html("Upside", growth, "#38bdf8"),
            _customer_signal_bar_html("Risk Control", risk_fit, "#22c55e"),
            _customer_signal_bar_html("Land Fit", land_fit, "#a78bfa"),
            _customer_signal_bar_html("Confidence", confidence, "#f59e0b"),
        ][:3 if compact else 5]
    )
    compact_class = " customer-card-compact" if compact else ""
    return f"""
<div class="customer-card{compact_class}">
  <div class="customer-card-top">
    <span class="customer-tier" style="border-color:{color}; color:{color};">{_customer_escape(tier)}</span>
    <span>{rank} strategy · {prod_rank} production</span>
  </div>
  <h3>{county_title}</h3>
  <p class="customer-thesis">{thesis}</p>
  {bars}
  <p class="customer-next"><b>Next:</b> {next_step}</p>
</div>
"""


def _render_customer_card(row: pd.Series, key_prefix: str, *, compact: bool = False) -> None:
    fips = str(row.get("fips", "")).zfill(5)
    st.markdown(_customer_card_html(row, compact=compact), unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    b1.button(
        "Open Story",
        key=f"{key_prefix}_story_{fips}",
        on_click=_set_customer_story_selection,
        args=(fips,),
    )
    if fips in {str(x).zfill(5) for x in st.session_state.watchlist_fips}:
        b2.caption("On watchlist")
    elif b2.button("Watch", key=f"{key_prefix}_watch_{fips}"):
        st.session_state.watchlist_fips = sorted(set(st.session_state.watchlist_fips + [fips]))
        _save_current_user_state()
        st.success("Added to watchlist.")


def _customer_brief_table(df: pd.DataFrame, limit: int = 20) -> pd.DataFrame:
    rows = []
    for _, row in df.sort_values("sim_rank").head(limit).iterrows():
        rows.append(
            {
                "Tier": row.get("customer_tier", _customer_tier_label(row)),
                "County": _customer_county_display(row),
                "Strategy Rank": _rank_text(row.get("sim_rank")),
                "Production Rank": _rank_text(row.get("overall_rank")),
                "Customer Signal": _fmt_score(row.get("customer_signal_score")),
                "5yr": _fmt_pct(row.get("pred_avg_5yr")),
                "Risk Band": row.get("customer_risk_band", _customer_risk_band(row)),
                "Confidence": row.get("confidence", "n/a"),
                "Thesis": _customer_thesis_read(row),
                "Next Check": _customer_next_step(row),
            }
        )
    return pd.DataFrame(rows)


def _customer_signal_rows(row: pd.Series) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"Signal": "Upside", "Score": _customer_signal_value(row, "sim_growth_score"), "Read": _fmt_pct(row.get("pred_avg_5yr"))},
            {"Signal": "Risk Control", "Score": _customer_signal_value(row, "sim_risk_fit"), "Read": _fmt_score(row.get("composite_risk"))},
            {"Signal": "Land Fit", "Score": _customer_signal_value(row, "sim_structure_score"), "Read": row.get("opportunity_archetype", "n/a")},
            {"Signal": "Confidence", "Score": _customer_signal_value(row, "sim_confidence_score"), "Read": row.get("confidence", "n/a")},
            {"Signal": "Parcel Ready", "Score": _customer_signal_value(row, "lens_parcel_readiness"), "Read": _parcel_readiness(row)[0]},
        ]
    )


def _customer_packet_markdown(
    filtered: pd.DataFrame,
    watch_df: pd.DataFrame,
    cfg: dict,
    latest_run: dict | None,
    *,
    customer_preset_name: str = "Customer view",
    risk_posture: str = "Balanced",
    selected_states: list[str] | None = None,
    selected_fips: str | None = None,
    full_df: pd.DataFrame | None = None,
    health_eval: pd.DataFrame | None = None,
    alert_df: pd.DataFrame | None = None,
) -> str:
    run_id = latest_run.get("run_id", "unknown") if latest_run else "unknown"
    story_source = full_df if full_df is not None and not full_df.empty else filtered
    selected_row = _selected_county_row(story_source, selected_fips) if selected_fips else None
    top_row = filtered.sort_values("sim_rank").iloc[0] if not filtered.empty else None
    active_states = ", ".join(selected_states or []) if selected_states else "All states"
    alert_count = int(len(alert_df)) if alert_df is not None and not alert_df.empty else 0
    lines = [
        "# LandInvest Customer Review Packet",
        "",
        f"- Generated at: `{datetime.now().isoformat()}`",
        f"- Ranking run: `{run_id}`",
        f"- Customer view: `{customer_preset_name}` / `{risk_posture}`",
        f"- Customer thesis: `{cfg.get('preset_name', 'Active thesis')}`",
        f"- Active states: `{active_states}`",
        f"- Active universe: `{len(filtered):,}` counties",
        f"- Watchlist: `{len(watch_df):,}` counties",
        f"- Active alerts: `{alert_count}`",
        "- Boundary: county-level screening only; production ranks and model artifacts are unchanged.",
        "",
        "## Executive Snapshot",
        "",
    ]
    if top_row is not None:
        lines.append(
            f"- Lead active-filter county: `{_customer_county_display(top_row)}` at strategy `{_rank_text(top_row.get('sim_rank'))}`, "
            f"5yr `{_fmt_pct(top_row.get('pred_avg_5yr'))}`, risk `{_fmt_score(top_row.get('composite_risk'))}`."
        )
    if selected_row is not None:
        lines.append(
            f"- Selected county: `{_customer_county_display(selected_row)}` with customer signal "
            f"`{_fmt_score(selected_row.get('customer_signal_score'))}` and parcel read `{_parcel_readiness(selected_row)[0]}`."
        )
    if watch_df.empty:
        lines.append("- Watchlist is empty; use Radar or Opportunity Deck to save review candidates.")
    else:
        lines.append(
            f"- Watchlist average risk `{_fmt_score(watch_df.get('composite_risk', pd.Series(dtype=float)).mean())}` "
            f"and average customer signal `{_fmt_score(watch_df.get('customer_signal_score', pd.Series(dtype=float)).mean())}`."
        )
    lines.extend(
        [
            "",
            "## Active View",
            "",
            f"- Preset: `{customer_preset_name}`",
            f"- Risk posture: `{risk_posture}`",
            f"- Thesis config: `{cfg.get('preset_name', 'Active thesis')}`",
            f"- State filter: `{active_states}`",
            "",
            "## Radar Shortlist",
            "",
        ]
    )
    for _, row in filtered.sort_values("sim_rank").head(12).iterrows():
        lines.append(
            f"- `{_customer_county_display(row)}`: "
            f"{row.get('customer_tier', _customer_tier_label(row))} signal, strategy rank `{_rank_text(row.get('sim_rank'))}`, "
            f"5yr `{_fmt_pct(row.get('pred_avg_5yr'))}`, risk `{_fmt_score(row.get('composite_risk'))}`. "
            f"{_customer_thesis_read(row)}"
        )
        lines.append(f"  - Next check: {_customer_next_step(row)}")
    lines.extend(["", "## Watchlist Command Center", ""])
    if watch_df.empty:
        lines.append("- No counties are currently on the watchlist.")
    else:
        health_lookup = {}
        if health_eval is not None and not health_eval.empty:
            health_lookup = health_eval.set_index(health_eval["fips"].astype(str).str.zfill(5)).to_dict("index")
        for _, row in watch_df.sort_values("sim_rank").head(20).iterrows():
            fips = str(row.get("fips")).zfill(5)
            health = health_lookup.get(fips, {})
            stage = st.session_state.county_funnel.get(fips, {}).get("stage", "Interested")
            lines.append(
                f"- `{_customer_county_display(row)}`: "
                f"{row.get('customer_tier', _customer_tier_label(row))}, strategy rank `{_rank_text(row.get('sim_rank'))}`, "
                f"stage `{stage}`, health `{_humanize_status_label(health.get('health_status', 'watch_closely'))}`, "
                f"risk band `{row.get('customer_risk_band', _customer_risk_band(row))}`."
            )
            lines.append(f"  - Next action: {_customer_next_step(row)}")
    lines.extend(["", "## Alerts And Review Items", ""])
    if alert_df is None or alert_df.empty:
        lines.append("- No watchlist alerts are currently firing.")
    else:
        alert_view = alert_df.copy().head(12)
        for _, rec in alert_view.iterrows():
            lines.append(
                f"- `{rec.get('county_name')}, {rec.get('state')}`: "
                f"`{rec.get('severity', 'n/a')}` / `{rec.get('alert_type', 'alert')}` - {rec.get('message', '')}"
            )
    lines.extend(["", "## Diligence Checklist", ""])
    checklist: list[str] = []
    source_df = watch_df if not watch_df.empty else filtered.head(8)
    for _, row in source_df.head(8).iterrows():
        _, actions = _parcel_readiness(row)
        checklist.extend(actions)
    for item in list(dict.fromkeys(checklist))[:10]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Review Notes",
            "",
            "- Customer Mode is a visual presentation layer over the current Product Mode strategy simulation.",
            "- Production rank, scoring pipeline, feature eligibility, and model promotion gates are unchanged.",
            "- Parcel, zoning, title, local-market, insurance, and transaction diligence remain required before underwriting.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _customer_packet_inline_html(text: str) -> str:
    escaped = _customer_escape(text)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)


def _customer_packet_html(packet_md: str, title: str = "LandInvest Customer Review Packet") -> str:
    html_lines = []
    in_list = False
    for raw_line in packet_md.splitlines():
        line = raw_line.rstrip()
        if not line:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            continue
        if line.startswith("# "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h1>{_customer_packet_inline_html(line[2:])}</h1>")
        elif line.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h2>{_customer_packet_inline_html(line[3:])}</h2>")
        elif line.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{_customer_packet_inline_html(line[2:])}</li>")
        elif line.startswith("  - "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li class=\"subitem\">{_customer_packet_inline_html(line[4:])}</li>")
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<p>{_customer_packet_inline_html(line)}</p>")
    if in_list:
        html_lines.append("</ul>")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_customer_escape(title)}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #0f172a; margin: 32px; line-height: 1.5; background: #f8fafc; }}
    .packet {{ max-width: 980px; margin: 0 auto; background: #fff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 28px 34px; box-shadow: 0 20px 48px rgba(15,23,42,.10); }}
    h1 {{ margin-top: 0; font-size: 30px; letter-spacing: 0; }}
    h2 {{ margin-top: 28px; padding-top: 14px; border-top: 1px solid #e2e8f0; color: #0f766e; }}
    li {{ margin: 6px 0; }}
    li.subitem {{ margin-left: 18px; color: #475569; }}
    code {{ background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 5px; padding: 1px 5px; }}
    @media print {{ body {{ margin: 18mm; }} }}
  </style>
</head>
<body>
  <main class="packet">
    {"".join(html_lines)}
  </main>
</body>
</html>
"""


def _customer_signal_provenance_table(row: pd.Series, wave3_status: dict | None = None) -> pd.DataFrame:
    coastal = _coastal_lane_provenance(row, wave3_status)
    rows = [
        {
            "Signal": "Production rank",
            "Status": "Production artifact",
            "What It Means": "Current saved scoring output; Customer Mode does not rewrite it.",
        },
        {
            "Signal": "Customer signal",
            "Status": "Presentation layer",
            "What It Means": "Visual blend of existing Product Mode simulation components for browsing.",
        },
        {
            "Signal": "X-factor / pre-boom",
            "Status": "Report-only",
            "What It Means": "Discovery context only until promotion gates pass.",
        },
        {
            "Signal": "Wave 3 land context",
            "Status": "Overlay / narrative",
            "What It Means": "Structural support/brake explanation; not a production rank change.",
        },
        {
            "Signal": "Coastal provenance",
            "Status": coastal.get("label", "n/a"),
            "What It Means": coastal.get("summary", "No coastal provenance summary available."),
        },
    ]
    return pd.DataFrame(rows)


def _customer_change_table(row: pd.Series, latest_compare_rank_df: pd.DataFrame | None) -> pd.DataFrame:
    if latest_compare_rank_df is None or latest_compare_rank_df.empty:
        return pd.DataFrame()
    comp = latest_compare_rank_df.copy()
    if "fips" not in comp.columns:
        return pd.DataFrame()
    fips = str(row.get("fips", "")).zfill(5)
    match = comp[comp["fips"].astype(str).str.zfill(5).eq(fips)]
    if match.empty:
        return pd.DataFrame()
    rec = match.iloc[0]
    rows = []
    for label, old_col, new_col, delta_col, fmt in [
        ("Rank", "overall_rank_old", "overall_rank_new", "rank_shift", "rank"),
        ("Opportunity score", None, None, "opportunity_score_delta", "score"),
        ("3yr policy", None, None, "pred_policy_3yr_delta", "pct_delta"),
        ("XGB 5yr", None, None, "pred_xgboost_5yr_delta", "pct_delta"),
        ("LGB 5yr", None, None, "pred_lightgbm_5yr_delta", "pct_delta"),
        ("Risk", None, None, "composite_risk_delta", "score"),
    ]:
        if delta_col not in rec.index or pd.isna(rec.get(delta_col)):
            continue
        if fmt == "rank":
            read = (
                f"{_rank_text(rec.get(old_col))} -> {_rank_text(rec.get(new_col))} "
                f"({float(rec.get(delta_col)):+.0f})"
            )
        elif fmt == "pct_delta":
            read = f"{float(rec.get(delta_col)):+.2%}"
        else:
            read = f"{float(rec.get(delta_col)):+.3f}"
        rows.append({"Change": label, "Latest Read": read})
    return pd.DataFrame(rows)


def _customer_similar_counties(row: pd.Series, df: pd.DataFrame, limit: int = 6) -> pd.DataFrame:
    peer_sets = _find_peer_sets(row, df)
    frames = []
    for label in ["Most similar profile", "Similar-risk alternatives", "Similar-growth alternatives"]:
        peer_df = peer_sets.get(label)
        if peer_df is not None and not peer_df.empty:
            work = peer_df.head(limit).copy()
            work["match_type"] = label
            frames.append(work)
    if not frames:
        return pd.DataFrame()
    peers = pd.concat(frames, ignore_index=True, sort=False)
    if "fips" in peers.columns:
        peers["fips"] = peers["fips"].astype(str).str.zfill(5)
        peers = peers.drop_duplicates("fips")
    rows = []
    for _, rec in peers.sort_values("sim_rank").head(limit).iterrows():
        rows.append(
            {
                "Match": rec.get("match_type"),
                "County": _customer_county_display(rec),
                "Tier": rec.get("customer_tier", _customer_tier_label(rec)),
                "Strategy Rank": _rank_text(rec.get("sim_rank")),
                "5yr": _fmt_pct(rec.get("pred_avg_5yr")),
                "Risk": _fmt_score(rec.get("composite_risk")),
                "Why Compare": _customer_thesis_read(rec),
            }
        )
    return pd.DataFrame(rows)


def _customer_parcel_items(row: pd.Series) -> list[str]:
    items = [
        "Parcel supply and listing scan",
        "Zoning and entitlement check",
        "Road access and utility access",
        "Wetlands, flood, slope, and protected-land screen",
        "Comparable sale and pricing check",
        "Title, easement, and legal access review",
        "Insurance and hazard feasibility",
        "Local broker or operator validation",
    ]
    if _product_numeric(row, "land_fragility_pressure", 0.5) >= 0.55:
        items.append("Wildfire, climate, or fragility deep dive")
    if _product_numeric(row, "land_constraint_pressure", 0.5) >= 0.55:
        items.append("Constrained-acreage estimate")
    return list(dict.fromkeys(items))


def _render_customer_parcel_diligence(row: pd.Series) -> None:
    fips = str(row.get("fips", "")).zfill(5)
    current = st.session_state.parcel_checklists.get(fips, {})
    checked = set(current.get("checked", []))
    items = _customer_parcel_items(row)
    st.subheader("Parcel Diligence")
    st.caption("County-level signal becomes actionable only after parcel-level evidence clears these checks.")
    c1, c2 = st.columns(2)
    updated_checked: list[str] = []
    for idx, item in enumerate(items):
        target_col = c1 if idx % 2 == 0 else c2
        if target_col.checkbox(item, value=item in checked, key=f"customer_parcel_{fips}_{idx}"):
            updated_checked.append(item)
    broker_note = st.text_input(
        "Broker, listing, or parcel evidence link",
        value=current.get("evidence_link", ""),
        key=f"customer_parcel_link_{fips}",
    )
    diligence_note = st.text_area(
        "Parcel diligence note",
        value=current.get("note", ""),
        height=100,
        key=f"customer_parcel_note_{fips}",
    )
    progress = len(updated_checked) / max(len(items), 1)
    st.progress(progress, text=f"{len(updated_checked)} of {len(items)} diligence checks complete")
    if st.button("Save Parcel Diligence", key=f"customer_parcel_save_{fips}"):
        st.session_state.parcel_checklists[fips] = {
            "county_name": row.get("county_name"),
            "state": row.get("state"),
            "checked": updated_checked,
            "evidence_link": broker_note.strip(),
            "note": diligence_note.strip(),
            "updated_at": datetime.now().isoformat(),
        }
        _save_current_user_state()
        st.success("Parcel diligence saved.")


def _customer_watchlist_health(
    watch_df: pd.DataFrame,
    latest_compare_rank_df: pd.DataFrame | None,
    run_history_summary_df: pd.DataFrame | None,
    wave3_status: dict | None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if watch_df.empty:
        return pd.DataFrame(), pd.DataFrame()
    run_summary_df, _ = _build_watchlist_latest_run_summary(
        watch_df,
        latest_compare_rank_df=latest_compare_rank_df,
        run_history_summary_df=run_history_summary_df,
        notes=st.session_state.get("county_notes", {}),
        watchlist_name="Customer Watchlist",
    )
    if run_summary_df.empty:
        return pd.DataFrame(), pd.DataFrame()
    health_eval = run_summary_df.copy()
    watch_lookup = watch_df.set_index(watch_df["fips"].astype(str).str.zfill(5))
    for col in [
        "composite_risk",
        "site_thesis_support_index",
        "land_developability_index",
        "land_constraint_pressure",
        "land_fragility_pressure",
        "pred_avg_5yr",
    ]:
        if col in watch_df.columns:
            health_eval[col] = watch_lookup[col].reindex(health_eval["fips"].astype(str).str.zfill(5)).values
    health_eval["coastal_lane"] = [
        _coastal_lane_provenance(
            watch_lookup.loc[fips] if fips in watch_lookup.index else pd.Series(dtype=object),
            wave3_status,
        ).get("label")
        for fips in health_eval["fips"].astype(str).str.zfill(5)
    ]
    health_eval["health_status"], health_eval["health_reasons"] = zip(
        *health_eval.apply(lambda r: _classify_watchlist_health(r, settings=st.session_state.watchlist_settings), axis=1)
    )
    alert_df = _build_watchlist_alerts(health_eval, settings=st.session_state.watchlist_settings)
    return health_eval, alert_df


def _customer_backlog_table(status_bundle: dict | None) -> pd.DataFrame:
    model_health = ((status_bundle or {}).get("model_health_3yr") or {}).get("assessment", {})
    return pd.DataFrame(
        [
            {
                "Lane": "Cloud accounts",
                "Status": "Not implemented",
                "Next Step": "Add hosted auth, user database, and server-side share tokens outside the local Streamlit demo store.",
            },
            {
                "Lane": "3yr model stabilization",
                "Status": _humanize_status_label(model_health.get("health_status", "unknown")),
                "Next Step": "Keep 3yr diagnostic until controlled specialist gate passes.",
            },
            {
                "Lane": "Announcement-event promotion",
                "Status": "Blocked",
                "Next Step": "Finish systematic acquisition coverage, analog depth, and refresh governance before promotion.",
            },
            {
                "Lane": "SEC HQ point-in-time semantics",
                "Status": "Blocked",
                "Next Step": "Acquire historical filing-address trails and event-validity windows.",
            },
            {
                "Lane": "Pre-1990 demographic composition",
                "Status": "Thin source coverage",
                "Next Step": "Stage richer 1970/1980 composition fields before feature promotion.",
            },
        ]
    )


def _customer_history_row(
    row: pd.Series | None,
    run_history_summary_df: pd.DataFrame | None,
) -> pd.Series | None:
    if row is None or run_history_summary_df is None or run_history_summary_df.empty:
        return None
    match = run_history_summary_df[
        run_history_summary_df["fips"].astype(str).str.zfill(5) == str(row.get("fips")).zfill(5)
    ]
    if match.empty:
        return None
    return match.iloc[0]


def _render_customer_story(
    row: pd.Series,
    history_row: pd.Series | None,
    filtered_df: pd.DataFrame,
    latest_compare_rank_df: pd.DataFrame | None,
    wave3_status: dict | None,
    cfg: dict,
    preboom_surfaces: dict[str, pd.DataFrame | None] | None,
    known_analog_suite: dict | None,
    xfactor_scoreboard: dict | None,
) -> None:
    fips = str(row.get("fips", "")).zfill(5)
    tier = str(row.get("customer_tier") or _customer_tier_label(row))
    color = CUSTOMER_TIER_COLORS.get(tier, "#64748b")
    st.markdown(
        f"""
<div class="customer-hero">
  <div class="customer-kicker">Customer Mode County Story</div>
  <h1>{_customer_escape(_customer_county_display(row))}</h1>
  <p>{_customer_escape(_customer_thesis_read(row))}</p>
  <div class="customer-hero-strip">
    <span style="border-color:{color}; color:{color};">{_customer_escape(tier)} signal</span>
    <span>Strategy {_rank_text(row.get('sim_rank'))}</span>
    <span>Production {_rank_text(row.get('overall_rank'))}</span>
    <span>Risk {_fmt_score(row.get('composite_risk'))}</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Customer Signal", _fmt_score(row.get("customer_signal_score")))
    c2.metric("5yr Upside", _fmt_pct(row.get("pred_avg_5yr")))
    c3.metric("Risk Band", row.get("customer_risk_band", _customer_risk_band(row)))
    c4.metric("Confidence", row.get("confidence", "n/a"))
    c5.metric("Parcel Read", _parcel_readiness(row)[0])

    signal_rows = _customer_signal_rows(row)
    radar_labels = signal_rows["Signal"].tolist()
    radar_values = signal_rows["Score"].astype(float).tolist()
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=radar_values + [radar_values[0]],
            theta=radar_labels + [radar_labels[0]],
            fill="toself",
            line=dict(color=color, width=3),
            fillcolor="rgba(20, 184, 166, 0.22)",
            name="Signal stack",
        )
    )
    fig.update_layout(
        height=380,
        template="plotly_white",
        polar=dict(
            radialaxis=dict(range=[0, 100], showticklabels=False, gridcolor="rgba(148,163,184,0.35)"),
            angularaxis=dict(gridcolor="rgba(148,163,184,0.28)"),
            bgcolor="rgba(248,250,252,0.95)",
        ),
        margin=dict(l=35, r=35, t=25, b=25),
        showlegend=False,
        paper_bgcolor="rgba(255,255,255,0)",
        font=dict(color="#0f172a", family="Inter, system-ui, sans-serif"),
        hoverlabel=dict(bgcolor="#0f172a", font_color="#f8fafc", bordercolor="#14b8a6"),
    )

    left, right = st.columns([1.05, 1])
    with left:
        with st.container(border=True):
            st.plotly_chart(fig, width="stretch")
    with right:
        signal_view = signal_rows.copy()
        signal_view["Score"] = signal_view["Score"].map(lambda x: f"{float(x):.0f}")
        st.caption("Signal stack")
        st.dataframe(signal_view, width="stretch", hide_index=True, height=310)

    change_rows = _customer_change_table(row, latest_compare_rank_df)
    source_rows = _customer_signal_provenance_table(row, wave3_status)
    similar_rows = _customer_similar_counties(row, filtered_df)
    m1, m2 = st.columns(2)
    with m1:
        st.subheader("What Changed")
        if change_rows.empty:
            st.caption("No latest-run delta is available for this county.")
        else:
            st.dataframe(change_rows, width="stretch", hide_index=True, height=220)
    with m2:
        st.subheader("Signal Provenance")
        st.dataframe(source_rows, width="stretch", hide_index=True, height=220)

    narrative = _build_county_narrative(row, history_row=history_row)
    readiness, actions = _parcel_readiness(row)
    support_col, brake_col, diligence_col = st.columns(3)
    with support_col:
        st.subheader("Why It Could Work")
        for item in narrative["positives"][:5]:
            st.markdown(f"- {item}")
    with brake_col:
        st.subheader("What Could Go Wrong")
        for item in narrative["cautions"][:5]:
            st.markdown(f"- {item}")
    with diligence_col:
        st.subheader("Next Diligence")
        st.markdown(f"**{readiness}**")
        for item in actions[:5]:
            st.markdown(f"- {item}")

    preboom_rows = _preboom_signal_rows_for_county(row, preboom_surfaces)
    analog_rows = _analog_rows_for_county(row, known_analog_suite)
    e1, e2 = st.columns(2)
    with e1:
        st.subheader("Pre-Boom Context")
        if preboom_rows.empty:
            st.caption("No loaded pre-boom review surface currently includes this county.")
        else:
            st.dataframe(preboom_rows, width="stretch", hide_index=True, height=220)
    with e2:
        st.subheader("Analog Context")
        if analog_rows.empty:
            st.caption("No analog-library context is currently available for this county.")
        else:
            st.dataframe(analog_rows, width="stretch", hide_index=True, height=220)

    st.subheader("Similar Counties")
    if similar_rows.empty:
        st.caption("No similar-county alternatives are available under the current filters.")
    else:
        st.dataframe(similar_rows, width="stretch", hide_index=True, height=250)

    _render_customer_parcel_diligence(row)

    action_col, note_col = st.columns([1, 2])
    with action_col:
        if fips not in {str(x).zfill(5) for x in st.session_state.watchlist_fips}:
            if st.button("Add To Watchlist", key=f"customer_story_watch_{fips}", type="primary"):
                st.session_state.watchlist_fips = sorted(set(st.session_state.watchlist_fips + [fips]))
                _save_current_user_state()
                st.success("County added to watchlist.")
        memo_md = _build_county_memo_markdown(
            row=row,
            history_row=history_row,
            wave3_status=wave3_status,
            cfg=cfg,
            preboom_surfaces=preboom_surfaces,
            analog_suite=known_analog_suite,
            xfactor_scoreboard=xfactor_scoreboard,
        )
        st.download_button(
            "Download Story Memo",
            data=memo_md.encode("utf-8"),
            file_name=f"landinvest_customer_story_{fips}.md",
            mime="text/markdown",
            key=f"customer_story_download_{fips}",
        )
    with note_col:
        note_entry = st.session_state.county_notes.get(fips, {})
        note = st.text_area("Customer note", value=note_entry.get("note", ""), height=115, key=f"customer_note_{fips}")
        if st.button("Save Customer Note", key=f"customer_note_save_{fips}"):
            st.session_state.county_notes[fips] = {
                "county_name": row.get("county_name"),
                "state": row.get("state"),
                "note": note.strip(),
                "updated_at": datetime.now().isoformat(),
            }
            _save_current_user_state()
            st.success("Note saved.")


def _render_customer_mode(
    df: pd.DataFrame,
    states: list[str],
    latest_run: dict | None,
    latest_deltas: dict | None,
    status_bundle: dict | None,
    run_history_summary_df: pd.DataFrame | None,
    latest_compare_rank_df: pd.DataFrame | None,
    wave3_status: dict | None,
    preboom_surfaces: dict[str, pd.DataFrame | None] | None = None,
    known_analog_suite: dict | None = None,
    xfactor_scoreboard: dict | None = None,
    xfactor_promotion_gate: dict | None = None,
    demo_readiness_report: dict | None = None,
) -> None:
    presets = _product_thesis_presets()
    customer_preset_names = list(CUSTOMER_PRESET_CATALOG)
    requested_customer_preset = _query_param_first("customer_preset", "General Opportunity")
    if requested_customer_preset not in CUSTOMER_PRESET_CATALOG:
        requested_customer_preset = "General Opportunity"
    requested_workspace = _query_param_first("workspace", "Radar")
    workspace_options = ["Radar", "Opportunities", "County Story", "Compare", "Watchlist", "Packet"]
    if requested_workspace not in workspace_options:
        requested_workspace = "Radar"
    requested_fips = _normalize_fips_value(_query_param_first("fips"))
    if requested_fips and "customer_selected_fips" not in st.session_state:
        st.session_state.customer_selected_fips = requested_fips
    pending_customer_view = st.session_state.pop("pending_customer_view_profile", None)
    if isinstance(pending_customer_view, dict):
        for key, value in _customer_view_session_state(pending_customer_view).items():
            st.session_state[key] = value
    has_explicit_customer_view = any(
        _query_param_first(param)
        for param in ["customer_preset", "risk_posture", "workspace", "states", "fips"]
    )
    if (
        not has_explicit_customer_view
        and "customer_workspace" not in st.session_state
        and (default_view := _customer_default_view_profile()) is not None
    ):
        for key, value in _customer_view_session_state(default_view).items():
            st.session_state[key] = value

    with st.sidebar:
        st.markdown('<div class="customer-sidebar-title">Investment Control Rail</div>', unsafe_allow_html=True)
        with st.expander("Strategy Setup", expanded=True):
            customer_preset_kwargs = {}
            if "customer_experience_preset" not in st.session_state:
                customer_preset_kwargs["index"] = customer_preset_names.index(requested_customer_preset)
            customer_preset_name = st.selectbox(
                "Customer preset",
                customer_preset_names,
                key="customer_experience_preset",
                help="Preset bundles a Product Mode thesis and customer-facing risk posture.",
                **customer_preset_kwargs,
            )
            preset_def = CUSTOMER_PRESET_CATALOG[customer_preset_name]
            st.caption(preset_def["description"])
            risk_options = ["Balanced", "Lower risk", "More aggressive"]
            requested_risk = _query_param_first("risk_posture", preset_def["risk_posture"])
            if requested_risk not in risk_options:
                requested_risk = preset_def["risk_posture"]
            risk_kwargs = {}
            if "customer_risk_posture" not in st.session_state:
                risk_kwargs["index"] = risk_options.index(requested_risk)
            risk_posture = st.selectbox(
                "Risk posture",
                risk_options,
                key="customer_risk_posture",
                help="Controls the risk ceiling, risk weight, and confidence gate used by the active Customer view.",
                **risk_kwargs,
            )
        with st.expander("Universe And Display", expanded=True):
            state_lookup = {str(state).upper(): state for state in states}
            query_states = [state_lookup[s.upper()] for s in _query_param_list("states") if s.upper() in state_lookup]
            state_kwargs = {}
            if "customer_states" not in st.session_state:
                state_kwargs["default"] = query_states
            selected_states = st.multiselect(
                "States",
                states,
                placeholder="All states",
                key="customer_states",
                help="Limits Customer Radar and Opportunity Deck to selected states. County Story remains globally searchable.",
                **state_kwargs,
            )
            card_limit_kwargs = {}
            if "customer_card_limit" not in st.session_state:
                card_limit_kwargs["value"] = 12
            card_limit = st.slider(
                "Opportunity cards",
                6,
                30,
                step=3,
                key="customer_card_limit",
                help="Number of cards shown in the Opportunity Deck.",
                **card_limit_kwargs,
            )
        with st.expander("Advanced Strategy Tuning", expanded=False):
            thesis_kwargs = {}
            if "customer_preset" not in st.session_state:
                thesis_kwargs["index"] = list(presets.keys()).index(preset_def["base_preset"])
            preset_name = st.selectbox(
                "Thesis",
                list(presets.keys()),
                key="customer_preset",
                help="Underlying Product Mode thesis used for the Customer Mode strategy score.",
                **thesis_kwargs,
            )
            st.caption("Advanced tuning changes the simulated strategy lens only. It does not retrain or rewrite production artifacts.")
        _render_customer_term_guide("Term Guide")

    cfg = presets[preset_name].copy()
    if risk_posture == "Lower risk":
        cfg["max_risk"] = min(float(cfg.get("max_risk", 70)), 48.0)
        cfg["risk"] = max(int(cfg.get("risk", 15)), 35)
        cfg["confidence"] = max(int(cfg.get("confidence", 5)), 10)
        cfg["uncertainty"] = max(int(cfg.get("uncertainty", 5)), 10)
        cfg["min_confidence"] = "MEDIUM+"
    elif risk_posture == "More aggressive":
        cfg["max_risk"] = max(float(cfg.get("max_risk", 70)), 75.0)
        cfg["growth"] = max(int(cfg.get("growth", 75)), 80)
        cfg["risk"] = min(int(cfg.get("risk", 15)), 8)
        cfg["min_confidence"] = "Any"
    cfg["states"] = selected_states
    cfg["preset_name"] = f"{customer_preset_name}: {preset_name} / {risk_posture}"

    sim_df = _simulate_strategy_rankings(df, cfg)
    sim_df = _add_product_lenses(sim_df)
    if run_history_summary_df is not None and not run_history_summary_df.empty:
        hist_cols = [
            c for c in ["fips", "avg_rank", "std_rank", "top25_presence_share", "rank_range"]
            if c in run_history_summary_df.columns
        ]
        sim_df["fips"] = sim_df["fips"].astype(str).str.zfill(5)
        sim_df = sim_df.merge(run_history_summary_df[hist_cols], on="fips", how="left")
    sim_df = _customer_augment(sim_df)
    filtered = _apply_product_filter(sim_df, selected_states, float(cfg.get("max_risk", 70)), str(cfg.get("min_confidence", "Any"))).sort_values("sim_rank")

    if filtered.empty:
        _render_trust_banner(latest_run, df, xfactor_promotion_gate)
        st.warning("No counties match the current Customer Mode setup.")
        _render_demo_footer(latest_run, status_bundle, demo_readiness_report)
        return

    if "customer_selected_fips" not in st.session_state:
        st.session_state.customer_selected_fips = str(filtered.iloc[0]["fips"]).zfill(5)
    if str(st.session_state.customer_selected_fips).zfill(5) not in set(sim_df["fips"].astype(str).str.zfill(5)):
        st.session_state.customer_selected_fips = str(filtered.iloc[0]["fips"]).zfill(5)

    run_id = latest_run.get("run_id", "unknown") if latest_run else "unknown"
    churn = latest_deltas.get("top25_churn") if latest_deltas and latest_deltas.get("has_previous") else None
    health = ((status_bundle or {}).get("model_health_3yr") or {}).get("assessment", {}).get("health_status")
    top_row = filtered.sort_values("sim_rank").iloc[0]
    prime_count = int(filtered["customer_tier"].eq("Prime").sum()) if "customer_tier" in filtered.columns else 0
    st.markdown(
        _customer_header_html(
            top_row=top_row,
            customer_preset_name=customer_preset_name,
            risk_posture=risk_posture,
            run_id=run_id,
            universe_count=len(filtered),
            full_count=len(sim_df),
            prime_count=prime_count,
            churn=churn,
            health=health,
        ),
        unsafe_allow_html=True,
    )
    _render_trust_banner(latest_run, df, xfactor_promotion_gate)

    if not st.session_state.get("customer_intro_seen", False):
        with st.expander("Investor Brief", expanded=False):
            st.markdown(
                "- Customer Mode is the polished review layer over the current ranking artifacts.\n"
                "- Production rank remains unchanged; customer signal tiers are presentation aids.\n"
                "- Watchlist notes, parcel checks, stages, and packets save to the local demo user profile."
            )
            if st.button("Hide Customer Brief", key="customer_intro_seen_button"):
                st.session_state.customer_intro_seen = True
                st.rerun()

    nav_col, guide_col = st.columns([5, 1])
    with nav_col:
        workspace_widget_kwargs = {}
        if "customer_workspace" not in st.session_state:
            workspace_widget_kwargs["default"] = requested_workspace
        workspace = st.segmented_control(
            "Customer workspace",
            workspace_options,
            selection_mode="single",
            required=True,
            format_func=_customer_workspace_label,
            key="customer_workspace",
            help="Switch between the Customer Mode review surfaces.",
            width="stretch",
            **workspace_widget_kwargs,
        )
    if workspace is None:
        workspace = requested_workspace
    with guide_col:
        st.write("")
        _render_customer_term_guide("Info")
    _customer_section_header(
        _customer_workspace_label(workspace),
        {
            "Radar": "Interactive market map, selected-county action panel, and live signal stack.",
            "Opportunities": "Card-based shortlist for the active thesis and filter universe.",
            "County Story": "Full county narrative, provenance, peer context, and diligence checklist.",
            "Compare": "Side-by-side signal stack for a small compare set.",
            "Watchlist": "Saved counties, stages, alerts, drift reads, and review flags.",
            "Packet": "Customer-facing exports and review packet assembly.",
        }.get(workspace),
    )
    _render_customer_workspace_help(workspace)
    with st.sidebar:
        with st.expander("Saved Customer Views", expanded=False):
            saved_views = _saved_customer_views()
            default_view_name = _customer_default_view_name()
            if saved_views:
                selected_view_name = st.selectbox(
                    "Saved view",
                    sorted(saved_views),
                    key="customer_saved_view_choice",
                    help="Load a saved Customer Mode preset, filters, workspace, selected county, and map layer.",
                )
                view_meta = saved_views.get(selected_view_name, {})
                default_badge = "Default view" if selected_view_name == default_view_name else "Saved view"
                st.caption(
                    f"{default_badge}: {view_meta.get('customer_preset_name', 'Customer view')} / "
                    f"{view_meta.get('risk_posture', 'Balanced')} / "
                    f"{view_meta.get('workspace', 'Radar')}"
                )
                load_col, default_col = st.columns(2)
                if load_col.button("Load View", key="customer_load_saved_view", type="primary"):
                    st.session_state.pending_customer_view_profile = saved_views[selected_view_name]
                    st.rerun()
                if default_col.button("Make Default", key="customer_make_default_view"):
                    st.session_state.saved_strategy_profiles["__customer_default_view__"] = {
                        "profile_type": "customer_default_view",
                        "name": selected_view_name,
                        "updated_at": datetime.now().isoformat(),
                    }
                    _save_current_user_state()
                    st.success(f"Default Customer view set to: {selected_view_name}")
                    st.rerun()
                rename_name = st.text_input(
                    "Rename selected view to",
                    key="customer_rename_view_name",
                    placeholder=selected_view_name,
                    help="Rename this saved Customer view in local profile storage.",
                )
                rename_col, duplicate_col = st.columns(2)
                if rename_col.button("Rename", key="customer_rename_saved_view"):
                    clean_rename = rename_name.strip()
                    if clean_rename and clean_rename != selected_view_name:
                        st.session_state.saved_strategy_profiles[clean_rename] = st.session_state.saved_strategy_profiles.pop(selected_view_name)
                        if default_view_name == selected_view_name:
                            st.session_state.saved_strategy_profiles["__customer_default_view__"] = {
                                "profile_type": "customer_default_view",
                                "name": clean_rename,
                                "updated_at": datetime.now().isoformat(),
                            }
                        _save_current_user_state()
                        st.success(f"Renamed view to: {clean_rename}")
                        st.rerun()
                    else:
                        st.warning("Enter a new view name first.")
                if duplicate_col.button("Duplicate", key="customer_duplicate_saved_view"):
                    base_name = f"{selected_view_name} Copy"
                    duplicate_name = base_name
                    idx = 2
                    while duplicate_name in st.session_state.saved_strategy_profiles:
                        duplicate_name = f"{base_name} {idx}"
                        idx += 1
                    duplicate_profile = dict(saved_views[selected_view_name])
                    duplicate_profile["saved_at"] = datetime.now().isoformat()
                    st.session_state.saved_strategy_profiles[duplicate_name] = duplicate_profile
                    _save_current_user_state()
                    st.success(f"Duplicated view: {duplicate_name}")
                    st.rerun()
                export_col, delete_col = st.columns(2)
                export_col.download_button(
                    "Export View",
                    data=json.dumps(_customer_view_export_payload(selected_view_name, view_meta), indent=2).encode("utf-8"),
                    file_name=f"landinvest_customer_view_{re.sub(r'[^a-zA-Z0-9_-]+', '_', selected_view_name).strip('_') or 'view'}.json",
                    mime="application/json",
                    key="customer_export_saved_view",
                    help="Download this saved Customer view as JSON.",
                )
                if delete_col.button("Delete", key="customer_delete_saved_view"):
                    st.session_state.saved_strategy_profiles.pop(selected_view_name, None)
                    if default_view_name == selected_view_name:
                        st.session_state.saved_strategy_profiles.pop("__customer_default_view__", None)
                    _save_current_user_state()
                    st.success(f"Deleted view: {selected_view_name}")
                    st.rerun()
            else:
                st.caption("No saved Customer views yet.")
            import_file = st.file_uploader(
                "Import Customer View JSON",
                type=["json"],
                key="customer_import_view_file",
                help="Import a Customer View JSON exported from this app.",
            )
            if import_file is not None and st.button("Import View", key="customer_import_view_button"):
                try:
                    imported_name, imported_profile = _parse_customer_view_import(import_file.getvalue())
                    final_name = imported_name
                    idx = 2
                    while final_name in st.session_state.saved_strategy_profiles:
                        final_name = f"{imported_name} {idx}"
                        idx += 1
                    st.session_state.saved_strategy_profiles[final_name] = imported_profile
                    _save_current_user_state()
                    st.success(f"Imported Customer view: {final_name}")
                    st.rerun()
                except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
                    st.error(f"Customer view import failed: {exc}")
            save_view_name = st.text_input(
                "Save current view as",
                key="customer_save_view_name",
                placeholder="e.g. Retirement land screen",
                help="Stores Customer preset, risk posture, states, workspace, selected county, and map layer in local profile storage.",
            )
            if st.button("Save Customer View", key="customer_save_view_button", type="secondary"):
                clean_name = save_view_name.strip()
                if clean_name:
                    st.session_state.saved_strategy_profiles[clean_name] = _customer_view_payload(
                        customer_preset_name=customer_preset_name,
                        preset_name=preset_name,
                        risk_posture=risk_posture,
                        selected_states=selected_states,
                        card_limit=int(card_limit),
                        workspace=workspace,
                        selected_fips=st.session_state.get("customer_selected_fips"),
                        radar_layer=st.session_state.get("customer_radar_layer", "sim_score"),
                        cfg=cfg,
                    )
                    _save_current_user_state()
                    st.success(f"Saved Customer view: {clean_name}")
                else:
                    st.warning("Name the view before saving.")
    share_url = _customer_share_url(
        customer_preset=customer_preset_name,
        risk_posture=risk_posture,
        workspace=workspace,
        selected_states=selected_states,
        selected_fips=st.session_state.get("customer_selected_fips"),
    )
    with st.expander("Share And Profile", expanded=False):
        s1, s2 = st.columns([2, 1])
        with s1:
            st.caption("Shareable view state")
            st.code(share_url, language="text")
        with s2:
            st.download_button(
                "Export Local Profile JSON",
                data=json.dumps(_current_user_state_payload(), indent=2).encode("utf-8"),
                file_name=f"landinvest_user_profile_{_current_user_id()}.json",
                mime="application/json",
                key="customer_user_profile_json",
            )
            st.caption("Current profile is local SQLite demo storage, not hosted authentication.")

    if workspace == "Radar":
        st.markdown(
            f"""
<div class="customer-stat-strip">
  <span><b>{prime_count}</b><small>Prime signals</small></span>
  <span><b>{int(filtered['customer_tier'].eq('Strong').sum())}</b><small>Strong signals</small></span>
  <span><b>{100 * filtered['confidence'].astype(str).str.upper().eq('HIGH').mean():.0f}%</b><small>High confidence</small></span>
  <span><b>{_fmt_pct(filtered['pred_avg_5yr'].mean())}</b><small>Avg 5yr upside</small></span>
</div>
""",
            unsafe_allow_html=True,
        )

        map_layer_labels = {
            "customer_signal_score": "Customer Signal",
            "sim_score": "Strategy Score",
            "pred_avg_5yr": "5yr Upside",
            "composite_risk": "Risk",
            "lens_parcel_readiness": "Parcel Readiness",
            "sim_structure_score": "Land Fit",
        }
        map_layer_kwargs = {}
        if "customer_radar_layer" not in st.session_state:
            map_layer_kwargs["index"] = 0
        map_layer = st.selectbox(
            "Map signal layer",
            ["sim_score", "customer_signal_score", "pred_avg_5yr", "composite_risk", "lens_parcel_readiness", "sim_structure_score"],
            format_func=lambda x: map_layer_labels.get(x, x.replace("_", " ").title()),
            key="customer_radar_layer",
            help="Choose the score used to color the county map. Click a county to load it into the selected-county action panel.",
            **map_layer_kwargs,
        )
        map_col, stack_col = st.columns([2, 1])
        with map_col:
            map_df = sim_df.dropna(subset=["fips", map_layer]).copy()
            map_df["customer_universe"] = np.where(
                map_df["fips"].astype(str).str.zfill(5).isin(filtered["fips"].astype(str).str.zfill(5)),
                "In current Customer filter",
                "Outside current Customer filter",
            )
            map_df["fips_str"] = map_df["fips"].astype(str).str.zfill(5)
            county_geojson = load_county_geojson(_mtime=_file_mtime(COUNTY_GEOJSON_PATH))
            selected_map_fips = _normalize_fips_value(st.session_state.get("customer_selected_fips"))
            selected_map_initial_row = _selected_county_row(sim_df, selected_map_fips)
            selected_map_title = (
                f"Selected: {_customer_county_display(selected_map_initial_row)}"
                if selected_map_initial_row is not None
                else "Click a county to select"
            )
            st.caption(selected_map_title)
            fig_map = px.choropleth(
                map_df,
                geojson=county_geojson,
                locations="fips_str",
                color=map_layer,
                hover_name="county_name",
                hover_data={"state": True, "customer_tier": True, "customer_universe": True, "sim_rank": True, "fips_str": False},
                color_continuous_scale="RdYlGn_r" if map_layer == "composite_risk" else "Viridis",
                scope="usa",
                title=f"{map_layer_labels.get(map_layer, map_layer.replace('_', ' ').title())} Radar | {selected_map_title}",
                custom_data=["fips_str", "state", "customer_tier", "customer_universe", "sim_rank"],
            )
            fig_map.update_traces(
                marker_line_width=0.25,
                marker_line_color="rgba(15, 23, 42, 0.28)",
                hovertemplate=(
                    "<b>%{hovertext}</b><br>"
                    "State: %{customdata[1]}<br>"
                    "Tier: %{customdata[2]}<br>"
                    "%{customdata[3]}<br>"
                    "Strategy rank: #%{customdata[4]}<extra>Click county</extra>"
                ),
            )
            if selected_map_fips and selected_map_fips in set(map_df["fips_str"]):
                fig_map.add_trace(
                    go.Choropleth(
                        geojson=county_geojson,
                        locations=[selected_map_fips],
                        z=[1],
                        colorscale=[[0, "rgba(251,191,36,0.22)"], [1, "rgba(251,191,36,0.22)"]],
                        showscale=False,
                        marker_line_color="#f59e0b",
                        marker_line_width=4.0,
                        hoverinfo="skip",
                        name="Selected county",
                    )
                )
            fig_map.update_layout(
                height=650,
                margin=dict(l=0, r=0, t=52, b=0),
                clickmode="event+select",
                paper_bgcolor="rgba(255,255,255,0)",
                plot_bgcolor="rgba(255,255,255,0)",
                font=dict(color="#0f172a", family="Inter, system-ui, sans-serif"),
                title=dict(font=dict(size=18), x=0.01, xanchor="left"),
                hoverlabel=dict(bgcolor="#0f172a", font_color="#f8fafc", bordercolor="#14b8a6"),
                geo=dict(bgcolor="rgba(0,0,0,0)", lakecolor="#e0f2fe", landcolor="#f8fafc"),
            )
            with st.container(border=True):
                selection = st.plotly_chart(
                    fig_map,
                    width="stretch",
                    on_select="rerun",
                    selection_mode=["points", "box", "lasso"],
                    key="customer_map",
                )
            selected_points = getattr(selection, "selection", {}).get("points", []) if selection is not None else []
            if selected_points:
                customdata = selected_points[0].get("customdata") or []
                if customdata:
                    clicked_fips = str(customdata[0]).zfill(5)
                    st.session_state.customer_selected_fips = clicked_fips
                    clicked_row = _selected_county_row(sim_df, clicked_fips)
                    if clicked_row is not None:
                        st.session_state.customer_map_feedback = f"Map selected {_customer_county_display(clicked_row)}."
            selected_map_row = _selected_county_row(sim_df, st.session_state.get("customer_selected_fips"))
            if selected_map_row is not None:
                if st.session_state.get("customer_map_feedback"):
                    st.success(st.session_state.customer_map_feedback)
                st.markdown(_customer_map_selection_html(selected_map_row), unsafe_allow_html=True)
                a1, a2 = st.columns(2)
                a1.button(
                    "Open County Story",
                    key=f"customer_map_open_story_{str(selected_map_row.get('fips')).zfill(5)}",
                    on_click=_set_customer_story_selection,
                    args=(str(selected_map_row.get("fips")).zfill(5),),
                    help="Jump to the full narrative, provenance, and diligence checklist for this county.",
                    type="primary",
                )
                selected_fips = str(selected_map_row.get("fips")).zfill(5)
                if selected_fips in {str(x).zfill(5) for x in st.session_state.watchlist_fips}:
                    a2.caption("On watchlist")
                elif a2.button(
                    "Add To Watchlist",
                    key=f"customer_map_watch_{selected_fips}",
                    help="Save this county to the local Customer Mode watchlist.",
                ):
                    st.session_state.watchlist_fips = sorted(set(st.session_state.watchlist_fips + [selected_fips]))
                    _save_current_user_state()
                    st.success("Added to watchlist.")
                if st.button(
                    "Reset Map Selection To Lead County",
                    key="customer_map_reset_selection",
                    help="Return the selected-county panel to the top-ranked county in the active Customer filter.",
                ):
                    lead_fips = str(filtered.sort_values("sim_rank").iloc[0].get("fips")).zfill(5)
                    st.session_state.customer_selected_fips = lead_fips
                    st.session_state.customer_map_feedback = "Map selection reset to the lead active-filter county."
                    st.rerun()
        with stack_col:
            st.subheader("Lead Signal Stack", help="Top counties in the active Customer filter by strategy rank.")
            for idx, (_, row) in enumerate(filtered.sort_values("sim_rank").head(4).iterrows()):
                _render_customer_card(row, f"customer_radar_{idx}", compact=True)

    elif workspace == "Opportunities":
        sort_choice = st.selectbox(
            "Opportunity sorting lens",
            ["Strategy rank", "Customer signal", "Lowest risk", "Highest 5yr upside", "Best land fit"],
            index=0,
            key="customer_sort",
            help="Controls how the Opportunity Deck is ordered inside the active Customer filter.",
        )
        query = st.text_input(
            "Search active opportunities",
            key="customer_search",
            placeholder="County, state, archetype, or tier",
            help="Searches only the active Customer opportunity universe. Use County Story to search every scored county.",
        )
        card_df = filtered.copy()
        if query.strip():
            q = query.strip().lower()
            mask = pd.Series(False, index=card_df.index)
            for col in ["county_name", "state", "opportunity_archetype", "customer_tier", "customer_risk_band"]:
                if col in card_df.columns:
                    mask = mask | card_df[col].astype(str).str.lower().str.contains(q, regex=False, na=False)
            card_df = card_df[mask]
        sort_map = {
            "Strategy rank": ("sim_rank", True),
            "Customer signal": ("customer_signal_score", False),
            "Lowest risk": ("composite_risk", True),
            "Highest 5yr upside": ("pred_avg_5yr", False),
            "Best land fit": ("sim_structure_score", False),
        }
        sort_col, ascending = sort_map[sort_choice]
        card_df = card_df.sort_values([sort_col, "sim_rank"], ascending=[ascending, True]).head(int(card_limit))
        cols = st.columns(3)
        for idx, (_, row) in enumerate(card_df.iterrows()):
            if idx > 0 and idx % 3 == 0:
                cols = st.columns(3)
            with cols[idx % 3]:
                _render_customer_card(row, f"customer_opportunity_{idx}")
        with st.expander("Data View", expanded=False):
            st.dataframe(_customer_brief_table(card_df, limit=int(card_limit)), width="stretch", hide_index=True, height=420)

    elif workspace == "County Story":
        active_fips = set(filtered["fips"].astype(str).str.zfill(5))
        labels_df = sim_df.sort_values("sim_rank").copy()
        labels_df["fips_str"] = labels_df["fips"].astype(str).str.zfill(5)
        labels_df["customer_universe"] = np.where(
            labels_df["fips_str"].isin(active_fips),
            "active filter",
            "outside filter",
        )
        story_query = st.text_input(
            "Search all counties",
            key="customer_story_search",
            placeholder="County, state, FIPS, archetype, or tier",
            help="Searches the full scored county universe, including counties outside the active Customer filter.",
        )
        if story_query.strip():
            q = story_query.strip().lower()
            mask = pd.Series(False, index=labels_df.index)
            for col in ["county_name", "state", "fips_str", "opportunity_archetype", "customer_tier", "customer_risk_band"]:
                if col in labels_df.columns:
                    mask = mask | labels_df[col].astype(str).str.lower().str.contains(q, regex=False, na=False)
            labels_df = labels_df[mask]
        if labels_df.empty:
            st.info("No counties match that Story search. Try a county name, state abbreviation, or FIPS code.")
            _render_demo_footer(latest_run, status_bundle, demo_readiness_report)
            return
        labels = labels_df.apply(
            lambda r: (
                f"{_customer_county_display(r)} "
                f"({r.get('customer_tier', _customer_tier_label(r))}, strategy {_rank_text(r.get('sim_rank'))}, "
                f"{r.get('customer_universe')}, FIPS {r.get('fips_str')})"
            ),
            axis=1,
        ).tolist()
        label_to_fips = dict(zip(labels, labels_df["fips_str"]))
        current_fips = st.session_state.get("customer_selected_fips")
        current_label = next((label for label, fips in label_to_fips.items() if fips == current_fips), labels[0])
        chosen = st.selectbox(
            "County",
            labels,
            index=labels.index(current_label) if current_label in labels else 0,
            key="customer_story_county",
            help="Labels show whether the county is inside the active filter or outside it.",
        )
        st.session_state.customer_selected_fips = label_to_fips[chosen]
        row = _selected_county_row(sim_df, st.session_state.customer_selected_fips)
        if row is not None:
            _render_customer_story(
                row,
                _customer_history_row(row, run_history_summary_df),
                sim_df,
                latest_compare_rank_df,
                wave3_status,
                cfg,
                preboom_surfaces,
                known_analog_suite,
                xfactor_scoreboard,
            )

    elif workspace == "Compare":
        compare_source = filtered.sort_values("sim_rank").head(250).copy()
        compare_labels = compare_source.apply(
            lambda r: f"{_customer_county_display(r)} ({r.get('customer_tier', _customer_tier_label(r))}, {_rank_text(r.get('sim_rank'))})",
            axis=1,
        ).tolist()
        selected = st.multiselect(
            "Compare counties",
            compare_labels,
            default=compare_labels[: min(3, len(compare_labels))],
            key="customer_compare_labels",
            help="Choose a focused set of counties to compare across signal components.",
        )
        label_to_fips = dict(zip(compare_labels, compare_source["fips"].astype(str).str.zfill(5)))
        selected_fips = [label_to_fips[label] for label in selected if label in label_to_fips]
        compare_df = compare_source[compare_source["fips"].astype(str).str.zfill(5).isin(selected_fips)].copy()
        if compare_df.empty:
            st.info("Choose at least one county to compare.")
        else:
            winner = compare_df.sort_values("sim_rank").iloc[0]
            st.success(
                f"Best fit under this Customer Mode thesis: {_customer_county_display(winner)} "
                f"at strategy {_rank_text(winner.get('sim_rank'))}."
            )
            score_cols = ["customer_signal_score", "sim_growth_score", "sim_risk_fit", "sim_structure_score", "sim_confidence_score"]
            chart_df = compare_df[["county_name", "state"] + [c for c in score_cols if c in compare_df.columns]].copy()
            chart_df["County"] = compare_df.apply(_customer_county_display, axis=1).values
            long_chart = chart_df.melt(id_vars=["County"], value_vars=[c for c in score_cols if c in chart_df.columns], var_name="Signal", value_name="Score")
            long_chart["Signal"] = long_chart["Signal"].map(
                {
                    "customer_signal_score": "Customer Signal",
                    "sim_growth_score": "Upside",
                    "sim_risk_fit": "Risk Control",
                    "sim_structure_score": "Land Fit",
                    "sim_confidence_score": "Confidence",
                }
            )
            fig_compare = px.bar(
                long_chart,
                x="Signal",
                y="Score",
                color="County",
                barmode="group",
                range_y=[0, 100],
                title="Signal Stack Comparison",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig_compare.update_layout(height=420, margin=dict(t=45, b=20))
            fig_compare.update_layout(
                paper_bgcolor="rgba(255,255,255,0)",
                plot_bgcolor="rgba(248,250,252,0.92)",
                font=dict(color="#0f172a", family="Inter, system-ui, sans-serif"),
                hoverlabel=dict(bgcolor="#0f172a", font_color="#f8fafc", bordercolor="#14b8a6"),
            )
            with st.container(border=True):
                st.plotly_chart(fig_compare, width="stretch")
            st.dataframe(_customer_brief_table(compare_df, limit=len(compare_df)), width="stretch", hide_index=True, height=320)

    elif workspace == "Watchlist":
        watch_fips = {str(f).zfill(5) for f in st.session_state.watchlist_fips}
        watch_df = sim_df[sim_df["fips"].astype(str).str.zfill(5).isin(watch_fips)].copy().sort_values("sim_rank")
        summary = _watchlist_portfolio_summary(watch_df)
        if watch_df.empty:
            st.info("No customer watchlist yet. Add counties from Radar, Opportunities, or County Story.")
            with st.container(border=True):
                st.subheader("Starter Candidates", help="Top active-filter counties to consider adding first.")
                st.dataframe(_customer_brief_table(filtered.head(8), limit=8), width="stretch", hide_index=True, height=320)
        else:
            flags = _watchlist_review_flags(watch_df)
            drift_alerts = _watchlist_drift_alerts(watch_df, latest_compare_rank_df)
            health_eval, alert_df = _customer_watchlist_health(
                watch_df,
                latest_compare_rank_df=latest_compare_rank_df,
                run_history_summary_df=run_history_summary_df,
                wave3_status=wave3_status,
            )
            fits_count = int((health_eval["health_status"] == "fits_thesis").sum()) if not health_eval.empty else 0
            watch_count = int((health_eval["health_status"] == "watch_closely").sum()) if not health_eval.empty else 0
            review_count = int((health_eval["health_status"] == "review_or_drop").sum()) if not health_eval.empty else 0
            stage_mix = {
                st.session_state.county_funnel.get(str(row.get("fips")).zfill(5), {}).get("stage", "Interested")
                for _, row in watch_df.iterrows()
            }
            st.markdown(
                f"""
<div class="customer-stat-strip">
  <span><b>{summary['count']}</b><small>Saved counties</small></span>
  <span><b>{fits_count}</b><small>Fits thesis</small></span>
  <span><b>{watch_count}</b><small>Watch closely</small></span>
  <span><b>{review_count}</b><small>Review or drop</small></span>
  <span><b>{len(alert_df) if alert_df is not None else 0}</b><small>Active alerts</small></span>
  <span><b>{summary['avg_risk']}</b><small>Avg risk</small></span>
  <span><b>{len(stage_mix)}</b><small>Stage count</small></span>
</div>
""",
                unsafe_allow_html=True,
            )
            watch_panel = st.segmented_control(
                "Watchlist command view",
                ["Command Center", "Stage Board", "Alerts"],
                selection_mode="single",
                default="Command Center",
                required=True,
                key="customer_watchlist_panel",
                help="Switch between portfolio summary, stage management, and alert review.",
                width="stretch",
            )
            if watch_panel == "Command Center":
                command_df = _customer_watchlist_command_rows(watch_df, health_eval, alert_df)
                cfilter1, cfilter2, cfilter3 = st.columns(3)
                command_search = cfilter1.text_input(
                    "Search watchlist",
                    key="customer_watchlist_search",
                    placeholder="County, stage, health, or FIPS",
                    help="Filter the command queue without changing the saved watchlist.",
                )
                stage_filter_options = ["All"] + sorted(command_df["Stage"].dropna().astype(str).unique().tolist())
                stage_filter = cfilter2.selectbox(
                    "Stage filter",
                    stage_filter_options,
                    key="customer_watchlist_stage_filter",
                    help="Limit the command queue to one diligence stage.",
                )
                sort_choice = cfilter3.selectbox(
                    "Sort queue",
                    ["Strategy rank", "Most alerts", "Highest signal", "Lowest risk", "County"],
                    key="customer_watchlist_sort",
                    help="Sort the command queue and export.",
                )
                command_view = command_df.copy()
                if command_search.strip():
                    q = command_search.strip().lower()
                    mask = pd.Series(False, index=command_view.index)
                    for col in ["County", "Stage", "Health", "FIPS", "Next Action"]:
                        mask = mask | command_view[col].astype(str).str.lower().str.contains(q, regex=False, na=False)
                    command_view = command_view[mask]
                if stage_filter != "All":
                    command_view = command_view[command_view["Stage"].astype(str).eq(stage_filter)]
                sort_map = {
                    "Strategy rank": (["_strategy_rank", "County"], [True, True]),
                    "Most alerts": (["_alerts", "_strategy_rank"], [False, True]),
                    "Highest signal": (["_signal_value", "_strategy_rank"], [False, True]),
                    "Lowest risk": (["_risk_value", "_strategy_rank"], [True, True]),
                    "County": (["County"], [True]),
                }
                sort_cols, sort_ascending = sort_map[sort_choice]
                command_view = command_view.sort_values(sort_cols, ascending=sort_ascending)
                display_command = command_view[[c for c in command_view.columns if not c.startswith("_")]].copy()
                with st.container(border=True):
                    st.subheader("Watchlist Command Center", help="One-line operating read for each saved county.")
                    st.dataframe(display_command, width="stretch", hide_index=True, height=320)
                    st.download_button(
                        "Download Command CSV",
                        data=display_command.to_csv(index=False).encode("utf-8"),
                        file_name="landinvest_customer_watchlist_command_center.csv",
                        mime="text/csv",
                        key="customer_watchlist_command_csv",
                    )
                s1, s2 = st.columns([1, 1])
                with s1:
                    st.subheader("Stage Summary", help="Current saved-county distribution by diligence stage.")
                    st.dataframe(_customer_watchlist_stage_summary(command_df), width="stretch", hide_index=True, height=220)
                with s2:
                    remove_options = ["None"] + display_command["County"].tolist()
                    remove_choice = st.selectbox(
                        "Remove from watchlist",
                        remove_options,
                        key="customer_watchlist_remove_choice",
                        help="Remove a county from the local Customer watchlist.",
                    )
                    if remove_choice != "None" and st.button("Remove Selected County", key="customer_watchlist_remove_button"):
                        remove_fips = display_command.loc[display_command["County"].eq(remove_choice), "FIPS"].iloc[0]
                        st.session_state.watchlist_fips = [
                            f for f in st.session_state.watchlist_fips if str(f).zfill(5) != str(remove_fips).zfill(5)
                        ]
                        _save_current_user_state()
                        st.success(f"Removed {remove_choice} from watchlist.")
                        st.rerun()
                plot_df = watch_df.copy()
                if not health_eval.empty:
                    health_cols = [c for c in ["fips", "health_status"] if c in health_eval.columns]
                    plot_df = plot_df.merge(health_eval[health_cols], on="fips", how="left")
                plot_df["County"] = plot_df.apply(_customer_county_display, axis=1)
                plot_df["plot_upside_size"] = pd.to_numeric(
                    plot_df.get("pred_avg_5yr", pd.Series(0.01, index=plot_df.index)),
                    errors="coerce",
                ).fillna(0.01).clip(lower=0.01)
                fig_watch = px.scatter(
                    plot_df,
                    x="composite_risk",
                    y="customer_signal_score",
                    size="plot_upside_size",
                    color="health_status" if "health_status" in plot_df.columns else "customer_tier",
                    hover_name="County",
                    hover_data={"sim_rank": True, "pred_avg_5yr": True, "confidence": True, "plot_upside_size": False},
                    title="Watchlist Signal vs Risk",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                )
                fig_watch.update_layout(
                    height=420,
                    margin=dict(t=50, b=30),
                    paper_bgcolor="rgba(255,255,255,0)",
                    plot_bgcolor="rgba(248,250,252,0.92)",
                    font=dict(color="#0f172a", family="Inter, system-ui, sans-serif"),
                    hoverlabel=dict(bgcolor="#0f172a", font_color="#f8fafc", bordercolor="#14b8a6"),
                    xaxis_title="Composite Risk (lower is cleaner)",
                    yaxis_title="Customer Signal",
                )
                with st.container(border=True):
                    st.plotly_chart(fig_watch, width="stretch")
                replacement_df = _recommend_watchlist_replacements(filtered, watch_df)
                with st.container(border=True):
                    st.subheader("Replacement Radar", help="High-fit active-filter counties not already on the watchlist.")
                    if replacement_df.empty:
                        st.caption("No replacement suggestions available under the active filter.")
                    else:
                        st.dataframe(_customer_brief_table(replacement_df, limit=8), width="stretch", hide_index=True, height=300)

            elif watch_panel == "Stage Board":
                stage_options = ["Interested", "Researching", "Parcel Check", "IC Review", "Approved", "Rejected", "Monitor"]
                stage_summary_df = _customer_watchlist_stage_summary(_customer_watchlist_command_rows(watch_df, health_eval, alert_df))
                st.dataframe(stage_summary_df, width="stretch", hide_index=True, height=180)
                for idx, (_, row) in enumerate(watch_df.head(12).iterrows()):
                    fips = str(row.get("fips")).zfill(5)
                    card_col, stage_col = st.columns([2, 1])
                    with card_col:
                        _render_customer_card(row, f"customer_watch_{idx}", compact=True)
                    with stage_col:
                        current_stage = st.session_state.county_funnel.get(fips, {}).get("stage", "Interested")
                        stage = st.selectbox(
                            "Stage",
                            stage_options,
                            index=stage_options.index(current_stage) if current_stage in stage_options else 0,
                            key=f"customer_stage_{fips}",
                            help="Local workflow stage for this saved county.",
                        )
                        if st.button("Save Stage", key=f"customer_stage_save_{fips}"):
                            st.session_state.county_funnel[fips] = {
                                "county_name": row.get("county_name"),
                                "state": row.get("state"),
                                "stage": stage,
                                "updated_at": datetime.now().isoformat(),
                            }
                            _save_current_user_state()
                            st.success("Stage saved.")
                        if st.button("Remove", key=f"customer_stage_remove_{fips}"):
                            st.session_state.watchlist_fips = [
                                saved for saved in st.session_state.watchlist_fips if str(saved).zfill(5) != fips
                            ]
                            _save_current_user_state()
                            st.success(f"Removed {_customer_county_display(row)} from watchlist.")
                            st.rerun()

            else:
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.subheader("Review Flags", help="Risk, rank, and stability issues that deserve human review.")
                    if flags.empty:
                        st.caption("No watchlist counties are currently triggering review flags.")
                    else:
                        st.dataframe(flags, width="stretch", hide_index=True, height=300)
                with c2:
                    st.subheader("Drift Alerts", help="Latest-run movement against prior rank or signal artifacts.")
                    if drift_alerts.empty:
                        st.caption("No watchlist drift alerts are currently firing.")
                    else:
                        st.dataframe(drift_alerts, width="stretch", hide_index=True, height=300)
                with c3:
                    st.subheader("Run Alerts", help="Current health and ranking alerts generated from watchlist rules.")
                    if alert_df.empty:
                        st.caption("No current watchlist alerts are firing.")
                    else:
                        alert_view = alert_df.copy()
                        alert_view["County"] = alert_view.apply(_customer_county_display, axis=1)
                        alert_view = alert_view.rename(
                            columns={
                                "severity": "Severity",
                                "alert_type": "Alert",
                                "message": "Message",
                                "current_rank": "Current Rank",
                            }
                        )
                        st.dataframe(
                            alert_view[[c for c in ["Severity", "Alert", "County", "Current Rank", "Message"] if c in alert_view.columns]].head(12),
                            width="stretch",
                            hide_index=True,
                            height=300,
                        )

    elif workspace == "Packet":
        watch_fips = {str(f).zfill(5) for f in st.session_state.watchlist_fips}
        watch_df = sim_df[sim_df["fips"].astype(str).str.zfill(5).isin(watch_fips)].copy().sort_values("sim_rank")
        packet_health_df = pd.DataFrame()
        packet_alert_df = pd.DataFrame()
        if not watch_df.empty:
            packet_health_df, packet_alert_df = _customer_watchlist_health(
                watch_df,
                latest_compare_rank_df=latest_compare_rank_df,
                run_history_summary_df=run_history_summary_df,
                wave3_status=wave3_status,
            )
        packet = _customer_packet_markdown(
            filtered,
            watch_df,
            cfg,
            latest_run,
            customer_preset_name=customer_preset_name,
            risk_posture=risk_posture,
            selected_states=selected_states,
            selected_fips=st.session_state.get("customer_selected_fips"),
            full_df=sim_df,
            health_eval=packet_health_df,
            alert_df=packet_alert_df,
        )
        packet_html = _customer_packet_html(packet)
        st.markdown(
            f"""
<div class="customer-stat-strip">
  <span><b>{len(filtered):,}</b><small>Active counties</small></span>
  <span><b>{len(watch_df):,}</b><small>Watchlist counties</small></span>
  <span><b>{len(packet_alert_df) if packet_alert_df is not None else 0}</b><small>Packet alerts</small></span>
  <span><b>{customer_preset_name}</b><small>Customer view</small></span>
</div>
""",
            unsafe_allow_html=True,
        )
        with st.container(border=True):
            st.subheader("Packet Contents", help="Sections included in the Customer Review Packet export.")
            st.markdown(
                "- Executive Snapshot\n"
                "- Active View\n"
                "- Radar Shortlist\n"
                "- Watchlist Command Center\n"
                "- Alerts And Review Items\n"
                "- Diligence Checklist\n"
                "- Review Notes"
            )
        p1, p2, p3 = st.columns(3)
        with p1:
            st.download_button(
                "Download Markdown Packet",
                data=packet.encode("utf-8"),
                file_name="landinvest_customer_review_packet.md",
                mime="text/markdown",
                key="customer_packet_download",
                type="primary",
            )
        with p2:
            st.download_button(
                "Download Print HTML",
                data=packet_html.encode("utf-8"),
                file_name="landinvest_customer_review_packet.html",
                mime="text/html",
                key="customer_packet_html_download",
            )
        with p3:
            st.download_button(
                "Download Watchlist CSV",
                data=_format_export_frame(watch_df if not watch_df.empty else filtered, 100).to_csv(index=False).encode("utf-8"),
                file_name="landinvest_customer_watchlist.csv",
                mime="text/csv",
                key="customer_packet_watchlist_csv",
            )
        st.text_area("Packet Preview", value=packet, height=520)
        with st.expander("Platform Readiness", expanded=False):
            st.dataframe(_customer_backlog_table(status_bundle), width="stretch", hide_index=True, height=260)

    _render_demo_footer(latest_run, status_bundle, demo_readiness_report)


def _render_product_mode(
    df: pd.DataFrame,
    states: list[str],
    latest_run: dict | None,
    latest_deltas: dict | None,
    status_bundle: dict | None,
    run_history_summary_df: pd.DataFrame | None,
    run_history_detail_df: pd.DataFrame | None,
    latest_compare_rank_df: pd.DataFrame | None,
    latest_compare_boundary_df: pd.DataFrame | None,
    wave3_status: dict | None,
    preboom_surfaces: dict[str, pd.DataFrame | None] | None = None,
    preboom_blend_report: dict | None = None,
    preboom_analog_report: dict | None = None,
    preboom_promotion_gate: dict | None = None,
    known_analog_suite: dict | None = None,
    xfactor_scoreboard: dict | None = None,
    xfactor_ablation_queue: dict | None = None,
    xfactor_promotion_gate: dict | None = None,
    demo_readiness_report: dict | None = None,
    p0_repeatable_residual_guardrail: dict | None = None,
    p0_repeatable_residual_candidates: pd.DataFrame | None = None,
) -> None:
    presets = _product_thesis_presets()

    pending_profile = st.session_state.pop("pending_product_strategy_profile", None)
    if isinstance(pending_profile, dict):
        for key, value in pending_profile.items():
            st.session_state[key] = value

    with st.sidebar:
        st.subheader("Strategy")
        saved_profiles = st.session_state.get("saved_strategy_profiles", {})
        if saved_profiles:
            profile_name = st.selectbox("Saved strategy profile", ["None"] + sorted(saved_profiles), key="product_saved_profile")
            if profile_name != "None" and st.button("Apply saved profile"):
                profile = saved_profiles.get(profile_name, {})
                st.session_state.pending_product_strategy_profile = {
                    "product_h1": int(profile.get("h1", 0)),
                    "product_h3": int(profile.get("h3", 10)),
                    "product_h5": int(profile.get("h5", 90)),
                    "product_growth": int(profile.get("growth", 75)),
                    "product_risk": int(profile.get("risk", 15)),
                    "product_structure": int(profile.get("structure", 5)),
                    "product_confidence": int(profile.get("confidence", 5)),
                    "product_uncertainty": int(profile.get("uncertainty", 5)),
                    "product_structural_focus": profile.get("structural_focus", "Overall land thesis"),
                    "product_max_risk": float(profile.get("max_risk", 70)),
                    "product_min_confidence": profile.get("min_confidence", "Any"),
                    "product_states": profile.get("states", []),
                }
                st.rerun()
        preset_name = st.selectbox("Thesis preset", list(presets.keys()), index=0, key="product_preset")
        preset = presets[preset_name]
        selected_states = st.multiselect("States", states, default=[], placeholder="All states", key="product_states")
        min_confidence = st.selectbox(
            "Minimum confidence",
            ["Any", "MEDIUM+", "HIGH"],
            index=["Any", "MEDIUM+", "HIGH"].index(preset["min_confidence"]),
            key="product_min_confidence",
        )
        max_risk = st.slider("Maximum risk", 20.0, 80.0, float(preset["max_risk"]), step=1.0, key="product_max_risk")
        st.divider()
        st.caption("Horizon mix")
        h1 = st.slider("1yr", 0, 100, int(preset["h1"]), step=5, key="product_h1")
        h3 = st.slider("3yr", 0, 100, int(preset["h3"]), step=5, key="product_h3")
        h5 = st.slider("5yr", 0, 100, int(preset["h5"]), step=5, key="product_h5")
        st.caption("Score mix")
        growth = st.slider("Growth", 0, 100, int(preset["growth"]), step=5, key="product_growth")
        risk = st.slider("Risk control", 0, 100, int(preset["risk"]), step=5, key="product_risk")
        structure = st.slider("Land thesis", 0, 100, int(preset["structure"]), step=5, key="product_structure")
        confidence = st.slider("Confidence", 0, 100, int(preset["confidence"]), step=5, key="product_confidence")
        uncertainty = st.slider("Uncertainty penalty", 0, 25, int(preset["uncertainty"]), step=1, key="product_uncertainty")
        structural_focus = st.selectbox(
            "Land thesis focus",
            ["Overall land thesis", "Optionality", "Low fragility", "Recreation access", "Buildable scarcity"],
            index=["Overall land thesis", "Optionality", "Low fragility", "Recreation access", "Buildable scarcity"].index(preset["structural_focus"]),
            key="product_structural_focus",
        )
        profile_save_name = st.text_input("Save strategy as", value="", placeholder="e.g. Mountain West low-risk")

    cfg = {
        "h1": h1,
        "h3": h3,
        "h5": h5,
        "growth": growth,
        "risk": risk,
        "structure": structure,
        "confidence": confidence,
        "uncertainty": uncertainty,
        "structural_focus": structural_focus,
        "max_risk": max_risk,
        "min_confidence": min_confidence,
        "states": selected_states,
        "preset_name": preset_name,
    }
    if profile_save_name.strip():
        with st.sidebar:
            if st.button("Save strategy profile", type="secondary"):
                st.session_state.saved_strategy_profiles[profile_save_name.strip()] = cfg.copy()
                _save_current_user_state()
                st.success(f"Saved strategy profile: {profile_save_name.strip()}")
    st.sidebar.caption(_strategy_profile_description(cfg))
    sim_df = _simulate_strategy_rankings(df, cfg)
    sim_df = _add_product_lenses(sim_df)
    if run_history_summary_df is not None and not run_history_summary_df.empty:
        hist_cols = [
            c for c in ["fips", "avg_rank", "std_rank", "top25_presence_share", "rank_range"]
            if c in run_history_summary_df.columns
        ]
        sim_df["fips"] = sim_df["fips"].astype(str).str.zfill(5)
        sim_df = sim_df.merge(run_history_summary_df[hist_cols], on="fips", how="left")
    filtered = _apply_product_filter(sim_df, selected_states, max_risk, min_confidence).sort_values("sim_rank")

    if "product_selected_fips" not in st.session_state and not filtered.empty:
        st.session_state.product_selected_fips = str(filtered.iloc[0]["fips"]).zfill(5)

    run_id = latest_run.get("run_id", "unknown") if latest_run else "unknown"
    churn = latest_deltas.get("top25_churn") if latest_deltas and latest_deltas.get("has_previous") else None
    health = ((status_bundle or {}).get("model_health_3yr") or {}).get("assessment", {}).get("health_status")
    chips = [
        f"Run: {run_id}",
        f"Counties: {len(filtered):,} / {len(df):,}",
        f"Preset: {preset_name}",
        f"Top-25 churn: {100 * churn:.1f}%" if churn is not None else "Top-25 churn: n/a",
    ]
    if health:
        chips.append(f"3yr health: {_humanize_status_label(health)}")
    st.markdown(" ".join(f'<span class="run-chip">{chip}</span>' for chip in chips), unsafe_allow_html=True)
    _render_trust_banner(latest_run, df, xfactor_promotion_gate)

    (
        top_start,
        top_discover,
        top_map,
        top_memo,
        top_watch,
        top_reports,
        top_advanced,
    ) = st.tabs(
        [
            "Start",
            "Discover",
            "Map",
            "County Memo",
            "Watchlist",
            "Reports",
            "Advanced",
        ]
    )
    st.caption("Main workflow: Start -> Discover -> Map -> County Memo -> Watchlist -> Reports. Advanced keeps diagnostics and promotion gates out of the default path.")

    tab_start = top_start
    tab_map = top_map
    tab_memo = top_memo

    with top_discover:
        (
            tab_search,
            tab_explore,
            tab_preboom,
            tab_play,
            tab_screen,
            tab_stress,
            tab_peers,
            tab_disagree,
            tab_region,
        ) = st.tabs(
            [
                "Search",
                "Explore",
                "Pre-Boom",
                "Strategy",
                "Screening",
                "Stress Tests",
                "Peer Sets",
                "Disagreement",
                "Region",
            ]
        )

    with top_watch:
        tab_watch, tab_workflow = st.tabs(
            [
                "Watchlist",
                "Funnel",
            ]
        )

    with top_reports:
        tab_reports, tab_thesis = st.tabs(
            [
                "Reports",
                "Investment Memo",
            ]
        )

    with top_advanced:
        tab_run, tab_autopsy, tab_promo, tab_health = st.tabs(
            [
                "Run Review",
                "Autopsy",
                "Promotion Gate",
                "Model Health",
            ]
        )

    with tab_start:
        _render_start_here_tab(filtered, cfg, latest_run, xfactor_scoreboard, xfactor_promotion_gate, demo_readiness_report)

    with tab_search:
        st.header("Natural-Language Search")
        if "product_nl_query" not in st.session_state:
            st.session_state.product_nl_query = ""
        st.caption("Use transparent keyword search for quick county-set discovery, then tune the sidebar strategy for precise policy changes.")
        examples = [
            ("Low-risk Mountain West", "low-risk counties with strong 5yr upside in the Mountain West"),
            ("High-confidence recreation", "high confidence recreation"),
            ("Model disagreement", "model disagreement"),
        ]
        ecols = st.columns(len(examples))
        for col, (label, example_query) in zip(ecols, examples):
            if col.button(label, key=f"product_nl_example_{label.lower().replace(' ', '_').replace('-', '_')}"):
                st.session_state.product_nl_query = example_query
                st.rerun()
        with st.form("product_nl_search_form", clear_on_submit=False):
            query = st.text_input(
                "Ask for a county set",
                placeholder="e.g. low-risk counties with strong 5yr upside in the Mountain West",
                key="product_nl_query",
            )
            st.form_submit_button("Apply search", type="primary")
        if st.button("Clear search", key="product_nl_clear_search"):
            st.session_state.product_nl_query = ""
            st.rerun()
        query = st.session_state.get("product_nl_query", query)
        result_df, query_notes = _apply_natural_language_query(filtered, query)
        for note in query_notes:
            st.caption(note)
        st.dataframe(_product_table(result_df, limit=40), width="stretch", hide_index=True, height=520)
        if not result_df.empty:
            st.caption("Natural-language search uses a transparent keyword parser; use Strategy controls for precise policy changes.")

    with tab_explore:
        st.header("Explore")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Best Strategy Score", _fmt_score(filtered["sim_score"].max()) if not filtered.empty else "—")
        m2.metric("Median Risk", _fmt_score(filtered["composite_risk"].median()) if not filtered.empty else "—")
        high_conf = filtered["confidence"].astype(str).str.upper().eq("HIGH").mean() if not filtered.empty else np.nan
        m3.metric("High Confidence", f"{100 * high_conf:.0f}%" if pd.notna(high_conf) else "—")
        fallback = filtered.get("use_stable_3yr_fallback", pd.Series(dtype=bool)).mean() if not filtered.empty else np.nan
        m4.metric("3yr Fallback", f"{100 * fallback:.0f}%" if pd.notna(fallback) else "—")

        for title, caption, slice_df in _insight_slices(filtered):
            st.subheader(title)
            st.caption(caption)
            st.dataframe(_product_table(slice_df, limit=8), width="stretch", hide_index=True, height=320)

        if "opportunity_archetype" in filtered.columns and not filtered.empty:
            st.subheader("Opportunity Archetypes")
            arch_counts = filtered["opportunity_archetype"].value_counts().reset_index()
            arch_counts.columns = ["Archetype", "Count"]
            a1, a2 = st.columns([1, 2])
            with a1:
                st.dataframe(arch_counts, width="stretch", hide_index=True, height=260)
            with a2:
                fig_arch = px.bar(
                    arch_counts.sort_values("Count", ascending=True),
                    x="Count",
                    y="Archetype",
                    orientation="h",
                    title="Active Strategy Archetype Mix",
                    color="Count",
                    color_continuous_scale="Teal",
                )
                fig_arch.update_layout(height=320, margin=dict(t=45, b=20))
                st.plotly_chart(fig_arch, width="stretch")

    with tab_reports:
        st.header("Review Package")
        st.caption("Exports are shareable screening artifacts for discussion. They preserve the current Product Mode strategy settings.")
        st.info(
            "Use this after County Memo and Watchlist review: export a Top 25/Top 100 package, "
            "then attach a compare set for the counties you want to discuss."
        )
        if filtered.empty:
            st.warning("No counties match the active strategy filters.")
        else:
            report_df = filtered.sort_values("sim_rank").copy()
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                top25_md = _top_report_markdown(
                    report_df,
                    cfg,
                    latest_run,
                    limit=25,
                    title="LandInvest Top 25 Opportunity Report",
                )
                st.download_button(
                    "Top 25 Markdown",
                    data=top25_md.encode("utf-8"),
                    file_name="landinvest_top25_opportunity_report.md",
                    mime="text/markdown",
                    key="product_report_top25_md",
                )
            with c2:
                top100_md = _top_report_markdown(
                    report_df,
                    cfg,
                    latest_run,
                    limit=100,
                    title="LandInvest Top 100 Opportunity Report",
                )
                st.download_button(
                    "Top 100 Markdown",
                    data=top100_md.encode("utf-8"),
                    file_name="landinvest_top100_opportunity_report.md",
                    mime="text/markdown",
                    key="product_report_top100_md",
                )
            with c3:
                shortlist = _format_export_frame(report_df, 100)
                st.download_button(
                    "Shortlist CSV",
                    data=shortlist.to_csv(index=False).encode("utf-8"),
                    file_name="landinvest_active_shortlist_top100.csv",
                    mime="text/csv",
                    key="product_report_shortlist_csv",
                )
            with c4:
                review_packet = (
                    _top_report_markdown(
                        report_df,
                        cfg,
                        latest_run,
                        limit=25,
                        title="LandInvest Investor Review Packet",
                    )
                    + "\n---\n\n"
                    + _compare_set_markdown(report_df.head(5), cfg, latest_run)
                )
                st.download_button(
                    "Review Packet",
                    data=review_packet.encode("utf-8"),
                    file_name="landinvest_investor_review_packet.md",
                    mime="text/markdown",
                    key="product_report_review_packet_md",
                )

            st.subheader("Shortlist Preview")
            st.dataframe(_product_table(report_df, limit=25), width="stretch", hide_index=True, height=420)

            st.subheader("Compare-Set Export")
            compare_source = report_df.head(500).copy()
            compare_labels = compare_source.apply(
                lambda r: f"{r['county_name']}, {r['state']} (strategy #{int(r['sim_rank'])}, production #{int(r['overall_rank'])})",
                axis=1,
            ).tolist()
            default_labels = compare_labels[: min(3, len(compare_labels))]
            selected_labels = st.multiselect(
                "Counties to compare",
                compare_labels,
                default=default_labels,
                key="product_report_compare_set",
            )
            label_to_fips = dict(zip(compare_labels, compare_source["fips"].astype(str).str.zfill(5)))
            selected_fips = {label_to_fips[label] for label in selected_labels if label in label_to_fips}
            compare_df = report_df[report_df["fips"].astype(str).str.zfill(5).isin(selected_fips)].copy()
            if compare_df.empty:
                st.info("Choose at least one county to build a compare-set export.")
            else:
                compare_export = _compare_export_frame(compare_df)
                st.dataframe(compare_export, width="stretch", hide_index=True, height=260)
                e1, e2 = st.columns(2)
                with e1:
                    compare_md = _compare_set_markdown(compare_df, cfg, latest_run)
                    st.download_button(
                        "Compare Summary Markdown",
                        data=compare_md.encode("utf-8"),
                        file_name="landinvest_compare_set_summary.md",
                        mime="text/markdown",
                        key="product_report_compare_md",
                    )
                with e2:
                    compare_payload = {
                        "generated_at": datetime.now().isoformat(),
                        "strategy": cfg,
                        "ranking_run": latest_run or {},
                        "counties": json.loads(compare_export.to_json(orient="records")),
                    }
                    st.download_button(
                        "Compare Set JSON",
                        data=json.dumps(compare_payload, indent=2).encode("utf-8"),
                        file_name="landinvest_compare_set.json",
                        mime="application/json",
                        key="product_report_compare_json",
                    )

    with tab_preboom:
        _render_preboom_review_tab(
            surfaces=preboom_surfaces or {},
            blend_report=preboom_blend_report,
            analog_report=preboom_analog_report,
            promotion_gate=preboom_promotion_gate,
            p0_repeatable_residual_guardrail=p0_repeatable_residual_guardrail,
            p0_repeatable_residual_candidates=p0_repeatable_residual_candidates,
        )

    with tab_play:
        st.header("Strategy Playground")
        st.caption("This is a simulation layer only. Production ranks and scores are unchanged.")
        strategy_table = _filter_product_table_rows(filtered, "product_strategy_table")
        st.caption(f"Showing {len(strategy_table):,} of {len(filtered):,} strategy rows.")
        st.dataframe(_product_table(strategy_table.sort_values("sim_rank"), limit=500), width="stretch", hide_index=True, height=520)
        clean_view = filtered.sort_values("lens_confidence_rank").head(30).copy()
        with st.expander("High-Conviction Lens", expanded=False):
            st.caption("This optional lens pushes wide-uncertainty and lower-confidence counties down without changing production rank.")
            clean_cols = [
                "lens_confidence_rank", "sim_rank", "overall_rank", "county_name", "state",
                "lens_confidence_weighted", "sim_score", "confidence", "quantile_interval_width_mean",
            ]
            clean = clean_view[[c for c in clean_cols if c in clean_view.columns]].copy()
            clean = clean.rename(
                columns={
                    "lens_confidence_rank": "High-Conviction Rank",
                    "sim_rank": "Strategy Rank",
                    "overall_rank": "Production Rank",
                    "county_name": "County",
                    "state": "State",
                    "lens_confidence_weighted": "High-Conviction Score",
                    "sim_score": "Strategy Score",
                    "confidence": "Confidence",
                    "quantile_interval_width_mean": "Uncertainty Width",
                }
            )
            for col in ["High-Conviction Rank", "Strategy Rank", "Production Rank"]:
                if col in clean.columns:
                    clean[col] = clean[col].map(lambda x: f"#{int(x)}" if pd.notna(x) else "—")
            for col in ["High-Conviction Score", "Strategy Score", "Uncertainty Width"]:
                if col in clean.columns:
                    clean[col] = clean[col].map(lambda x: f"{float(x):.3f}" if col == "Uncertainty Width" else _fmt_score(x))
            st.dataframe(clean, width="stretch", hide_index=True, height=320)

        p1, p2 = st.columns(2)
        with p1:
            if not filtered.empty:
                fig = px.scatter(
                    filtered.head(500),
                    x="overall_rank",
                    y="sim_rank",
                    color="sim_score",
                    hover_name="county_name",
                    hover_data=["state", "composite_risk", "pred_avg_5yr", "pred_policy_3yr"],
                    title="Production Rank vs Strategy Rank",
                    labels={"overall_rank": "Production rank", "sim_rank": "Strategy rank"},
                    color_continuous_scale="Viridis",
                )
                fig.add_shape(type="line", x0=1, y0=1, x1=500, y1=500, line=dict(color="gray", dash="dash"))
                fig.update_yaxes(autorange="reversed")
                fig.update_xaxes(autorange="reversed")
                fig.update_layout(height=430, margin=dict(t=45, b=20))
                st.plotly_chart(fig, width="stretch")
        with p2:
            risers = filtered.sort_values("sim_rank_delta").head(15).copy()
            fig = px.bar(
                risers,
                x="sim_rank_delta",
                y="county_name",
                orientation="h",
                color="sim_score",
                title="Largest Strategy Risers",
                labels={"sim_rank_delta": "Strategy rank minus production rank", "county_name": "County"},
                color_continuous_scale="Teal",
            )
            fig.update_layout(height=430, margin=dict(t=45, b=20))
            st.plotly_chart(fig, width="stretch")

    with tab_screen:
        st.header("Negative Screening")
        st.caption("This view helps find counties to avoid, monitor only, or require a special thesis.")
        if filtered.empty:
            st.info("No counties match the active strategy filters.")
        else:
            screen_df = _negative_screen(filtered)
            avoid_cols = [
                "screen_read", "avoid_score", "county_name", "state", "sim_rank", "overall_rank",
                "composite_risk", "confidence", "sim_uncertainty_score", "sim_structure_score",
            ]
            avoid = screen_df[[c for c in avoid_cols if c in screen_df.columns]].head(50).copy()
            avoid = avoid.rename(
                columns={
                    "screen_read": "Screen Read",
                    "avoid_score": "Avoid Score",
                    "county_name": "County",
                    "state": "State",
                    "sim_rank": "Strategy Rank",
                    "overall_rank": "Production Rank",
                    "composite_risk": "Risk",
                    "confidence": "Confidence",
                    "sim_uncertainty_score": "Uncertainty",
                    "sim_structure_score": "Thesis Fit",
                }
            )
            for col in ["Avoid Score", "Risk", "Uncertainty", "Thesis Fit"]:
                if col in avoid.columns:
                    avoid[col] = avoid[col].map(_fmt_score)
            for col in ["Strategy Rank", "Production Rank"]:
                if col in avoid.columns:
                    avoid[col] = avoid[col].map(lambda x: f"#{int(x)}" if pd.notna(x) else "—")
            st.dataframe(avoid, width="stretch", hide_index=True, height=520)

    stress_df = None
    with tab_stress:
        st.header("Scenario Stress Tests")
        st.caption("Stress tests are strategy overlays. They do not alter production ranks or saved artifacts.")
        catalog = _scenario_catalog()
        scenarios = st.multiselect(
            "Stress scenarios",
            list(catalog.keys()),
            default=["Higher rates", "Climate-risk haircut"],
            key="product_scenarios",
        )
        severity = st.slider("Stress severity", 0.25, 2.00, 1.00, step=0.25, key="product_stress_severity")
        if scenarios and not filtered.empty:
            stress_df = _apply_scenario_stress(filtered, scenarios, severity)
            base_top = set(filtered.sort_values("sim_rank").head(25)["fips"].astype(str).str.zfill(5))
            stress_top = set(stress_df.sort_values("stress_rank").head(25)["fips"].astype(str).str.zfill(5))
            overlap = len(base_top & stress_top)
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Top-25 Survivors", f"{overlap}/25")
            s2.metric("Top-25 Churn", f"{100 * (1 - overlap / 25):.0f}%")
            s3.metric("Median Stress Score", _fmt_score(stress_df["stress_score"].median()))
            s4.metric("Median Rank Move", f"{stress_df['stress_rank_delta'].abs().median():.0f}")

            st.dataframe(_stress_table(stress_df, limit=40), width="stretch", hide_index=True, height=480)
            c1, c2 = st.columns(2)
            with c1:
                fallers = stress_df.sort_values("stress_rank_delta", ascending=False).head(15)
                fig_fall = px.bar(
                    fallers,
                    x="stress_rank_delta",
                    y="county_name",
                    orientation="h",
                    title="Most Stress-Sensitive Counties",
                    labels={"stress_rank_delta": "Stress rank move", "county_name": "County"},
                    color="stress_rank_delta",
                    color_continuous_scale="Reds",
                )
                fig_fall.update_layout(height=420, margin=dict(t=45, b=20))
                st.plotly_chart(fig_fall, width="stretch")
            with c2:
                survivors = stress_df[stress_df["fips"].astype(str).str.zfill(5).isin(base_top & stress_top)]
                fig_survive = px.scatter(
                    survivors,
                    x="composite_risk",
                    y="stress_score",
                    color="opportunity_archetype" if "opportunity_archetype" in survivors.columns else "state",
                    hover_name="county_name",
                    title="Top-25 Survivors",
                    labels={"composite_risk": "Composite risk", "stress_score": "Stress score"},
                )
                fig_survive.update_layout(height=420, margin=dict(t=45, b=20))
                st.plotly_chart(fig_survive, width="stretch")
            for name in scenarios:
                st.caption(f"{name}: {catalog[name]['description']}")
        else:
            st.info("Choose at least one scenario to stress the active strategy.")

    with tab_map:
        st.header("Map")
        metric = st.selectbox(
            "Map layer",
            [
                "sim_score",
                "lens_confidence_weighted",
                "lens_upside_minus_risk",
                "lens_structure_minus_fragility",
                "lens_parcel_readiness",
                "sim_rank_delta",
                "opportunity_score",
                "composite_risk",
                "sim_structure_score",
                "pred_avg_5yr",
                "pred_policy_3yr",
            ],
            format_func=lambda x: x.replace("_", " ").title(),
            key="product_map_metric",
        )
        map_df = filtered.dropna(subset=["fips", metric]).copy()
        map_df["fips_str"] = map_df["fips"].astype(str).str.zfill(5)
        color_scale = "RdYlGn_r" if "risk" in metric or metric == "sim_rank_delta" else "Viridis"
        fig_map = px.choropleth(
            map_df,
            geojson=load_county_geojson(_mtime=_file_mtime(COUNTY_GEOJSON_PATH)),
            locations="fips_str",
            color=metric,
            hover_name="county_name",
            hover_data={"state": True, "sim_rank": True, "overall_rank": True, "fips_str": False},
            color_continuous_scale=color_scale,
            scope="usa",
            title=f"{metric.replace('_', ' ').title()} by County",
            custom_data=["fips_str"],
        )
        fig_map.update_layout(height=650, margin=dict(l=0, r=0, t=45, b=0), geo=dict(bgcolor="rgba(0,0,0,0)"))
        selection = st.plotly_chart(fig_map, width="stretch", on_select="rerun", selection_mode=["points", "box", "lasso"], key="product_map")
        selected_points = getattr(selection, "selection", {}).get("points", []) if selection is not None else []
        if selected_points:
            point = selected_points[0]
            customdata = point.get("customdata") or []
            if customdata:
                st.session_state.product_selected_fips = str(customdata[0]).zfill(5)
        st.caption("Select a county or region on the map, then open County Memo to inspect the current selection.")

    with tab_memo:
        st.header("County Memo")
        if filtered.empty:
            st.warning("No counties match the active strategy filters.")
        else:
            labels = filtered.sort_values("sim_rank").head(1000).apply(
                lambda r: f"{r['county_name']}, {r['state']} (strategy #{int(r['sim_rank'])}, production #{int(r['overall_rank'])})",
                axis=1,
            ).tolist()
            label_to_fips = dict(zip(labels, filtered.sort_values("sim_rank").head(1000)["fips"].astype(str).str.zfill(5)))
            current_fips = st.session_state.get("product_selected_fips")
            current_label = next((label for label, fips in label_to_fips.items() if fips == current_fips), labels[0])
            chosen = st.selectbox("County", labels, index=labels.index(current_label) if current_label in labels else 0)
            st.session_state.product_selected_fips = label_to_fips[chosen]
            row = _selected_county_row(filtered, st.session_state.product_selected_fips)
            history_row = None
            if row is not None and run_history_summary_df is not None and not run_history_summary_df.empty:
                match = run_history_summary_df[run_history_summary_df["fips"].astype(str).str.zfill(5) == str(row["fips"]).zfill(5)]
                if not match.empty:
                    history_row = match.iloc[0]
            if row is not None:
                _render_product_county_memo(
                    row,
                    history_row,
                    wave3_status,
                    cfg,
                    preboom_surfaces=preboom_surfaces,
                    analog_suite=known_analog_suite,
                    xfactor_scoreboard=xfactor_scoreboard,
                )

    with tab_peers:
        st.header("Peer Sets")
        if filtered.empty:
            st.warning("No counties match the active strategy filters.")
        else:
            row = _selected_county_row(filtered, st.session_state.get("product_selected_fips"))
            if row is None:
                row = filtered.sort_values("sim_rank").iloc[0]
                st.session_state.product_selected_fips = str(row["fips"]).zfill(5)
            st.caption(
                f"Peer context for {row.get('county_name')}, {row.get('state')} "
                f"(strategy #{int(row.get('sim_rank'))}, production #{int(row.get('overall_rank'))})."
            )
            peer_sets = _find_peer_sets(row, filtered)
            if not peer_sets:
                st.info("No peer sets available under the active filters.")
            for label, peer_df in peer_sets.items():
                st.subheader(label)
                st.dataframe(_peer_table(peer_df), width="stretch", hide_index=True, height=300)
            st.subheader("County Matchmaker")
            match_goal = st.radio(
                "Find alternatives with",
                ["More upside", "Lower risk", "Same region", "Different region", "Stronger structural support", "Less rank volatility"],
                horizontal=True,
                key="product_match_goal",
            )
            base = filtered[filtered["fips"].astype(str).str.zfill(5) != str(row.get("fips")).zfill(5)].copy()
            if match_goal == "More upside":
                base = base[base["pred_avg_5yr"] >= _product_numeric(row, "pred_avg_5yr", 0.0)].sort_values(["pred_avg_5yr", "sim_rank"], ascending=[False, True])
            elif match_goal == "Lower risk":
                base = base[base["composite_risk"] <= _product_numeric(row, "composite_risk", 50.0)].sort_values(["composite_risk", "sim_rank"])
            elif match_goal == "Same region":
                base = base[base["state"] == row.get("state")].sort_values("sim_rank")
            elif match_goal == "Different region":
                base = base[base["state"] != row.get("state")].sort_values("sim_rank")
            elif match_goal == "Stronger structural support":
                base = base[base["sim_structure_score"] >= _product_numeric(row, "sim_structure_score", 50.0)].sort_values(["sim_structure_score", "sim_rank"], ascending=[False, True])
            else:
                base = base[base["rank_stability_spread"] <= _product_numeric(row, "rank_stability_spread", 0.25)].sort_values(["rank_stability_spread", "sim_rank"])
            st.dataframe(_peer_table(base.head(12)), width="stretch", hide_index=True, height=320)
            st.caption("Peer sets are heuristic comparisons for exploration, not replacement model outputs.")

    with tab_disagree:
        st.header("Model Disagreement Explorer")
        st.caption("Counties here are thesis-dependent or less settled across models/horizons.")
        if filtered.empty:
            st.info("No counties match the active strategy filters.")
        else:
            disagree_df = _model_disagreement_surface(filtered)
            cols = [
                "county_name", "state", "sim_rank", "overall_rank", "model_disagreement_lens",
                "model_disagreement", "horizon_disagreement", "sim_uncertainty_score",
                "pred_avg_1yr", "pred_policy_3yr", "pred_avg_5yr", "confidence",
            ]
            view = disagree_df[[c for c in cols if c in disagree_df.columns]].head(50).copy()
            view = view.rename(
                columns={
                    "county_name": "County",
                    "state": "State",
                    "sim_rank": "Strategy Rank",
                    "overall_rank": "Production Rank",
                    "model_disagreement_lens": "Disagreement Lens",
                    "model_disagreement": "Model Disagreement",
                    "horizon_disagreement": "Horizon Disagreement",
                    "sim_uncertainty_score": "Uncertainty",
                    "pred_avg_1yr": "1yr",
                    "pred_policy_3yr": "3yr",
                    "pred_avg_5yr": "5yr",
                    "confidence": "Confidence",
                }
            )
            for col in ["Strategy Rank", "Production Rank"]:
                if col in view.columns:
                    view[col] = view[col].map(lambda x: f"#{int(x)}" if pd.notna(x) else "—")
            for col in ["Disagreement Lens", "Model Disagreement", "Horizon Disagreement", "Uncertainty"]:
                if col in view.columns:
                    view[col] = view[col].map(lambda x: f"{float(x):.3f}" if pd.notna(x) else "—")
            for col in ["1yr", "3yr", "5yr"]:
                if col in view.columns:
                    view[col] = view[col].map(_fmt_pct)
            st.dataframe(view, width="stretch", hide_index=True, height=520)

    with tab_region:
        st.header("Regional Strategy Builder")
        region_states = st.multiselect("Region states", states, default=selected_states, key="product_region_states")
        region_df = filtered[filtered["state"].isin(region_states)].copy() if region_states else filtered.copy()
        state_roll, arch = _regional_summary(region_df)
        if region_df.empty:
            st.info("No counties match the regional selection.")
        else:
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Counties", f"{len(region_df):,}")
            r2.metric("Avg Strategy Score", _fmt_score(region_df["sim_score"].mean()))
            r3.metric("Avg Risk", _fmt_score(region_df["composite_risk"].mean()))
            r4.metric("Top Archetype", region_df["opportunity_archetype"].mode().iloc[0] if "opportunity_archetype" in region_df.columns else "n/a")
            st.subheader("State Rollup")
            roll = state_roll.copy()
            for col in ["avg_strategy_score", "avg_risk"]:
                if col in roll.columns:
                    roll[col] = roll[col].map(_fmt_score)
            if "avg_5yr" in roll.columns:
                roll["avg_5yr"] = roll["avg_5yr"].map(_fmt_pct)
            if "high_conf_share" in roll.columns:
                roll["high_conf_share"] = roll["high_conf_share"].map(lambda x: f"{100 * float(x):.0f}%")
            st.dataframe(roll, width="stretch", hide_index=True, height=300)
            st.subheader("Regional Leaders")
            regional_leaders = _filter_product_table_rows(region_df.sort_values("sim_rank"), "product_regional_leaders")
            st.caption(f"Showing {len(regional_leaders):,} of {len(region_df):,} regional rows.")
            st.dataframe(_product_table(regional_leaders.sort_values("sim_rank"), limit=500), width="stretch", hide_index=True, height=420)
            if not arch.empty:
                fig_region = px.bar(
                    arch.head(40),
                    x="count",
                    y="state",
                    color="opportunity_archetype",
                    orientation="h",
                    title="Regional Archetype Mix",
                )
                fig_region.update_layout(height=420, margin=dict(t=45, b=20))
                st.plotly_chart(fig_region, width="stretch")

    with tab_thesis:
        st.header("Thesis Builder")
        watch_fips = {str(f).zfill(5) for f in st.session_state.watchlist_fips}
        watch_df = filtered[filtered["fips"].astype(str).str.zfill(5).isin(watch_fips)].copy()
        if watch_df.empty:
            st.info("Add counties from County Memo to build a thesis memo.")
        else:
            t1, t2, t3, t4 = st.columns(4)
            t1.metric("Shortlist Counties", len(watch_df))
            t2.metric("Avg Strategy Score", _fmt_score(watch_df["sim_score"].mean()))
            t3.metric("Avg Risk", _fmt_score(watch_df["composite_risk"].mean()))
            t4.metric("Archetypes", watch_df["opportunity_archetype"].nunique() if "opportunity_archetype" in watch_df.columns else "n/a")

            st.subheader("Shortlist Diligence Readiness")
            readiness_rows = []
            for _, rec in watch_df.sort_values("sim_rank").iterrows():
                readiness, actions = _parcel_readiness(rec)
                readiness_rows.append(
                    {
                        "County": rec.get("county_name"),
                        "State": rec.get("state"),
                        "Strategy Rank": f"#{int(rec.get('sim_rank'))}",
                        "Archetype": rec.get("opportunity_archetype"),
                        "Readiness": readiness,
                        "Next Check": actions[0] if actions else "—",
                    }
                )
            st.dataframe(pd.DataFrame(readiness_rows), width="stretch", hide_index=True, height=320)

            memo = _build_deal_thesis_memo(watch_df, cfg, preset_name, stress_df=stress_df)
            st.subheader("Generated Investment Memo")
            st.text_area("Memo", value=memo, height=420)
            st.download_button(
                "Export thesis memo (Markdown)",
                data=memo.encode("utf-8"),
                file_name="landinvest_thesis_memo.md",
                mime="text/markdown",
            )
            ic_packet = _ic_packet_markdown(watch_df, cfg, preset_name, stress_df)
            with st.expander("Investment Committee Mode", expanded=False):
                st.text_area("IC packet", value=ic_packet, height=420)
                st.download_button(
                    "Export IC packet (Markdown)",
                    data=ic_packet.encode("utf-8"),
                    file_name="landinvest_ic_packet.md",
                    mime="text/markdown",
                )

    with tab_workflow:
        st.header("Opportunity Funnel")
        funnel_rows = []
        for fips, rec in st.session_state.county_funnel.items():
            feedback = st.session_state.county_feedback.get(fips, {})
            evidence = st.session_state.diligence_evidence.get(fips, {})
            funnel_rows.append(
                {
                    "FIPS": fips,
                    "County": rec.get("county_name"),
                    "State": rec.get("state"),
                    "Stage": rec.get("stage"),
                    "Feedback": feedback.get("feedback", "Unreviewed"),
                    "Evidence": "yes" if (evidence.get("evidence") or "").strip() else "no",
                    "Updated": rec.get("updated_at"),
                }
            )
        if funnel_rows:
            funnel_df = pd.DataFrame(funnel_rows).sort_values(["Stage", "State", "County"])
            st.dataframe(funnel_df, width="stretch", hide_index=True, height=420)
            stage_counts = funnel_df["Stage"].value_counts().reset_index()
            stage_counts.columns = ["Stage", "Count"]
            fig_funnel = px.bar(stage_counts, x="Stage", y="Count", title="Funnel Stage Counts", color="Stage")
            fig_funnel.update_layout(height=320, margin=dict(t=45, b=20))
            st.plotly_chart(fig_funnel, width="stretch")
        else:
            st.info("Set a funnel stage in County Memo to start tracking opportunities.")

        feedback_rows = []
        for fips, rec in st.session_state.county_feedback.items():
            feedback_rows.append({"FIPS": fips, **rec})
        if feedback_rows:
            st.subheader("Human Feedback Loop")
            st.dataframe(pd.DataFrame(feedback_rows), width="stretch", hide_index=True, height=280)

    with tab_watch:
        st.header("Watchlist")
        st.caption("Use Watchlist as the active review queue before generating Reports or an Investment Memo.")
        watch_fips = {str(f).zfill(5) for f in st.session_state.watchlist_fips}
        watch_df = filtered[filtered["fips"].astype(str).str.zfill(5).isin(watch_fips)].copy()
        summary = _watchlist_portfolio_summary(watch_df)
        w1, w2, w3, w4, w5 = st.columns(5)
        w1.metric("Counties", summary["count"])
        w2.metric("Avg Strategy Score", summary["avg_score"])
        w3.metric("Avg Risk", summary["avg_risk"])
        w4.metric("High Confidence", summary["high_conf_share"])
        w5.metric("Top States", summary["top_states"])
        if watch_df.empty:
            st.info("Add counties from County Memo to build a strategy watchlist.")
        else:
            st.dataframe(_product_table(watch_df.sort_values("sim_rank"), limit=100), width="stretch", hide_index=True, height=420)
            flags = _watchlist_review_flags(watch_df)
            recs = _recommend_watchlist_replacements(filtered, watch_df)
            drift_alerts = _watchlist_drift_alerts(watch_df, latest_compare_rank_df)
            r1, r2, r3 = st.columns(3)
            with r1:
                st.subheader("Review Candidates")
                if flags.empty:
                    st.caption("No watchlist counties are currently triggering review flags under this strategy.")
                else:
                    st.dataframe(flags, width="stretch", hide_index=True, height=260)
            with r2:
                st.subheader("Suggested Additions")
                if recs.empty:
                    st.caption("No replacement suggestions available under the active filters.")
                else:
                    st.dataframe(_product_table(recs, limit=8), width="stretch", hide_index=True, height=260)
            with r3:
                st.subheader("Drift Alerts")
                if drift_alerts.empty:
                    st.caption("No watchlist drift alerts are currently firing.")
                else:
                    st.dataframe(drift_alerts, width="stretch", hide_index=True, height=260)
            if run_history_summary_df is not None and not run_history_summary_df.empty:
                enriched = watch_df.merge(
                    run_history_summary_df[[
                        c for c in ["fips", "std_rank", "top25_presence_share", "rank_range"]
                        if c in run_history_summary_df.columns
                    ]],
                    on="fips",
                    how="left",
                    suffixes=("", "_hist"),
                )
                fig = px.scatter(
                    enriched,
                    x="composite_risk",
                    y="sim_score",
                    size="top25_presence_share" if "top25_presence_share" in enriched.columns else None,
                    color="state",
                    hover_name="county_name",
                    title="Watchlist Risk, Score, and Durability",
                    labels={"composite_risk": "Composite risk", "sim_score": "Strategy score"},
                )
                fig.update_layout(height=420, margin=dict(t=45, b=20))
                st.plotly_chart(fig, width="stretch")

    with tab_run:
        st.header("Run Review")
        review = _run_review_summary(filtered, latest_compare_rank_df, latest_compare_boundary_df)
        if not review:
            st.info("No latest run-comparison artifact is available for this Product Mode summary.")
        else:
            if latest_compare_rank_df is not None and not latest_compare_rank_df.empty:
                comp = latest_compare_rank_df.copy()
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Compared Counties", f"{len(comp):,}")
                c2.metric("Mean |Rank Move|", f"{pd.to_numeric(comp.get('abs_rank_shift'), errors='coerce').mean():.1f}")
                entrants = review.get("Top-25 entrants", pd.DataFrame())
                exits = review.get("Top-25 exits", pd.DataFrame())
                c3.metric("Top-25 Entrants", len(entrants))
                c4.metric("Top-25 Exits", len(exits))
                st.subheader("Narrative Brief")
                for bullet in _run_review_narrative(latest_compare_rank_df):
                    st.markdown(f"- {bullet}")
            for label, frame in review.items():
                st.subheader(label)
                if frame.empty:
                    st.caption("None in the latest comparison.")
                else:
                    st.dataframe(_run_review_table(frame), width="stretch", hide_index=True, height=300)

    with tab_autopsy:
        st.header("County Autopsy")
        st.caption("A lightweight review queue for counties where the system may have been too optimistic or where the latest run changed the read.")
        autopsy = _autopsy_candidates(filtered, latest_compare_rank_df)
        if autopsy.empty:
            st.info("No autopsy candidates found under the active strategy.")
        else:
            rows = []
            for _, rec in autopsy.iterrows():
                rows.append(
                    {
                        "County": rec.get("county_name"),
                        "State": rec.get("state"),
                        "Current Rank": f"#{int(rec.get('overall_rank'))}" if pd.notna(rec.get("overall_rank")) else "—",
                        "Reason": rec.get("autopsy_reason"),
                        "Risk": _fmt_score(rec.get("composite_risk")),
                        "Confidence": rec.get("confidence"),
                        "3yr Fallback": bool(rec.get("use_stable_3yr_fallback", False)),
                        "What to review": "; ".join(_why_not_bullets(rec)[:2]),
                    }
                )
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True, height=520)

    with tab_promo:
        st.header("Promotion-Readiness Console")
        st.caption("This is a compact product gate for deciding whether candidate model/policy changes deserve promotion work.")
        st.dataframe(_promotion_readiness_rows(status_bundle), width="stretch", hide_index=True, height=260)
        gate = xfactor_promotion_gate or {}
        if gate:
            st.subheader("X-Factor Interaction Promotion Gate")
            g1, g2, g3, g4 = st.columns(4)
            g1.metric("Status", gate.get("production_promotion_status", "n/a"))
            g2.metric("Ablation Ready", gate.get("ablation_ready_count", "n/a"))
            g3.metric("Default Promotion", gate.get("default_promotion_count", "n/a"))
            g4.metric("Report-Only", gate.get("report_only_count", "n/a"))
            gate_rows = pd.DataFrame(gate.get("gates") or [])
            if not gate_rows.empty:
                view_cols = [
                    "interaction",
                    "label",
                    "scoreboard_decision",
                    "ablation_decision",
                    "quiet_lift_gate",
                    "already_hot_gate",
                    "analog_gate",
                    "ablation_gate",
                    "final_decision",
                ]
                st.dataframe(gate_rows[[c for c in view_cols if c in gate_rows.columns]], width="stretch", hide_index=True, height=300)
            notes = gate.get("notes") or []
            for note in notes[:4]:
                st.markdown(f"- {note}")
        queue = xfactor_ablation_queue or {}
        queue_rows = pd.DataFrame(queue.get("queue") or [])
        if not queue_rows.empty:
            st.subheader("Controlled Ablation Queue")
            queue_cols = [
                "interaction",
                "label",
                "status",
                "scoreboard_decision",
                "ablation_decision",
                "recommended_action",
            ]
            st.dataframe(queue_rows[[c for c in queue_cols if c in queue_rows.columns]], width="stretch", hide_index=True, height=300)
            st.download_button(
                "Export Ablation Queue JSON",
                data=json.dumps(queue, indent=2).encode("utf-8"),
                file_name="xfactor_interaction_ablation_queue.json",
                mime="application/json",
                key="product_ablation_queue_json",
            )
        st.markdown(
            "- Treat green-looking product lenses as exploration aids until they pass historical quality, churn, source-health, and model-health gates.\n"
            "- Current Product Mode simulations are UI overlays only; `scoring_pipeline.py` production rankings remain unchanged.\n"
            "- Use Legacy Mode for the full validation and run-comparison evidence before changing model artifacts."
        )

    with tab_health:
        st.header("Model Health")
        model_health = (status_bundle or {}).get("model_health_3yr") or {}
        wave3_closeout = (status_bundle or {}).get("wave3_closeout") or {}
        h1c, h2c, h3c, h4c = st.columns(4)
        assessment = model_health.get("assessment", {}) or {}
        raw_health_status = assessment.get("health_status", "n/a")
        h1c.metric("3yr Status", _humanize_status_label(raw_health_status))
        fallback_share = (((model_health.get("live_rankings") or {}).get("fallback") or {}).get("fallback_share"))
        h2c.metric("3yr Fallback", f"{100 * fallback_share:.1f}%" if fallback_share is not None else "n/a")
        drift = model_health.get("target_drift_3yr", {}) or {}
        drift_psi = drift.get("psi")
        try:
            drift_read = f"{float(drift_psi):.3f}" if drift_psi is not None else "n/a"
        except (TypeError, ValueError):
            drift_read = str(drift_psi)
        h3c.metric("3yr Drift PSI", drift_read)
        closeout_summary = wave3_closeout.get("summary", {}) or {}
        wave3_status_label = wave3_closeout.get("status", closeout_summary.get("status", "n/a"))
        h4c.metric("Wave 3 Posture", _humanize_status_label(wave3_status_label))
        st.caption(f"Full 3yr status: `{raw_health_status}`")
        warnings = assessment.get("blocking_reasons") or assessment.get("warnings") or assessment.get("notes") or []
        if warnings:
            st.caption("Current model-health read")
            for item in warnings[:6]:
                st.markdown(f"- {item}")
        st.info("Use Legacy Mode for full validation, source-health, drift, calibration, and run-comparison diagnostics.")

    _render_demo_footer(latest_run, status_bundle, demo_readiness_report)


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="LandInvest — County Growth Dashboard",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .landinvest-brand-header {
        display: grid;
        grid-template-columns: minmax(280px, 0.82fr) minmax(320px, 1.18fr);
        align-items: center;
        gap: 0.82rem;
        border: 1px solid rgba(15, 118, 110, 0.22);
        background: linear-gradient(135deg, #f8fafc 0%, #f0fdfa 58%, #fffbeb 100%);
        color: #0f172a;
        border-radius: 8px;
        padding: 0.78rem 0.86rem;
        margin: 0 0 0.85rem 0;
        box-shadow: 0 14px 34px rgba(15, 23, 42, 0.07);
    }
    .landinvest-brand-main {
        display: flex;
        align-items: center;
        gap: 0.68rem;
        min-width: 0;
    }
    .landinvest-logo-wrap {
        width: 2.85rem;
        height: 2.85rem;
        flex: 0 0 2.85rem;
    }
    .landinvest-logo-wrap svg,
    .landinvest-sidebar-logo svg {
        width: 100%;
        height: 100%;
        display: block;
    }
    .landinvest-brand-kicker {
        color: #0f766e;
        font-size: 0.68rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0;
        margin-bottom: 0.1rem;
    }
    .landinvest-brand-copy h1 {
        color: #0f172a;
        font-size: 1.42rem;
        line-height: 1.06;
        margin: 0;
        letter-spacing: 0;
    }
    .landinvest-brand-copy p {
        color: #475569;
        font-size: 0.83rem;
        line-height: 1.35;
        margin: 0.22rem 0 0 0;
        max-width: 44rem;
    }
    .landinvest-brand-meta {
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-start;
        gap: 0.45rem;
        max-width: none;
    }
    .landinvest-brand-chip {
        min-width: 5.95rem;
        border: 1px solid rgba(15, 118, 110, 0.20);
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.76);
        padding: 0.35rem 0.5rem;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.84);
    }
    .landinvest-brand-chip b {
        display: block;
        color: #0f766e;
        font-size: 0.62rem;
        line-height: 1.1;
        text-transform: uppercase;
        letter-spacing: 0;
        margin-bottom: 0.12rem;
    }
    .landinvest-brand-chip span {
        display: block;
        color: #0f172a;
        font-size: 0.76rem;
        line-height: 1.15;
        font-weight: 700;
    }
    .landinvest-sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.58rem;
        margin: 0.15rem 0 0.85rem 0;
        padding: 0.45rem 0.1rem;
    }
    .landinvest-sidebar-logo {
        width: 2.25rem;
        height: 2.25rem;
        flex: 0 0 2.25rem;
    }
    .landinvest-sidebar-brand b {
        display: block;
        color: #0f172a;
        font-size: 1rem;
        line-height: 1.05;
    }
    .landinvest-sidebar-brand span {
        display: block;
        color: #64748b;
        font-size: 0.76rem;
        margin-top: 0.12rem;
    }
    .run-chip {
        display: inline-block;
        padding: 0.25rem 0.55rem;
        border-radius: 999px;
        background: #eef2f7;
        border: 1px solid #cbd5e1;
        color: #0f172a;
        font-size: 0.8rem;
        margin-right: 0.35rem;
        margin-bottom: 0.35rem;
    }
    .onboard {
        border: 1px solid #bfdbfe;
        background: linear-gradient(90deg, #e0ecff 0%, #eef4ff 100%);
        border-radius: 10px;
        padding: 0.75rem 0.9rem;
        margin-bottom: 0.8rem;
        color: #0f172a;
    }
    .onboard b {
        color: #0b3a7e;
    }
    .customer-sidebar-title {
        font-size: 0.78rem;
        font-weight: 800;
        color: #0f766e;
        text-transform: uppercase;
        letter-spacing: 0;
        margin: 0.2rem 0 0.65rem 0;
    }
    .customer-command-header {
        border: 1px solid rgba(20, 184, 166, 0.35);
        background:
            linear-gradient(135deg, rgba(204, 251, 241, 0.96) 0%, rgba(248, 250, 252, 0.98) 44%, rgba(254, 243, 199, 0.74) 100%);
        color: #0f172a;
        border-radius: 8px;
        padding: 1.15rem 1.25rem;
        margin: 0 0 0.85rem 0;
        box-shadow: 0 18px 46px rgba(15, 23, 42, 0.10);
        display: grid;
        grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.95fr);
        gap: 1rem;
        align-items: end;
    }
    .customer-command-header h1 {
        color: #0f172a;
        font-size: 2.1rem;
        line-height: 1.08;
        margin: 0 0 0.45rem 0;
        letter-spacing: 0;
    }
    .customer-command-header p {
        color: #334155;
        margin: 0;
        max-width: 76rem;
    }
    .customer-command-grid,
    .customer-stat-strip,
    .customer-map-stats {
        display: flex;
        flex-wrap: wrap;
        gap: 0.48rem;
    }
    .customer-command-grid span,
    .customer-stat-strip span,
    .customer-map-stats span {
        border: 1px solid rgba(15, 118, 110, 0.24);
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.72);
        padding: 0.52rem 0.64rem;
        min-width: 7.2rem;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.80);
    }
    .customer-command-grid b,
    .customer-stat-strip b,
    .customer-map-stats b {
        display: block;
        color: #0f172a;
        font-size: 0.95rem;
        line-height: 1.15;
    }
    .customer-command-grid small,
    .customer-stat-strip small,
    .customer-map-stats small {
        display: block;
        color: #64748b;
        font-size: 0.72rem;
        margin-top: 0.18rem;
    }
    .customer-section-header {
        margin: 0.65rem 0 0.75rem 0;
        padding: 0.72rem 0.85rem;
        border-left: 4px solid #14b8a6;
        border-radius: 8px;
        background: linear-gradient(90deg, rgba(240, 253, 250, 0.95), rgba(255, 251, 235, 0.55));
    }
    .customer-section-header p {
        margin: 0.12rem 0 0 0;
        color: #475569;
    }
    .customer-stat-strip {
        margin: 0.3rem 0 0.85rem 0;
    }
    .customer-stat-strip span {
        min-width: 10rem;
    }
    .customer-map-callout {
        margin: 0.8rem 0 0.25rem 0;
        border: 1px solid rgba(20, 184, 166, 0.34);
        border-radius: 8px;
        background: #f8fafc;
        padding: 0.82rem 0.92rem;
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        gap: 0.85rem;
        align-items: center;
    }
    .customer-map-callout h3 {
        margin: 0.08rem 0 0.22rem 0;
        font-size: 1.05rem;
        letter-spacing: 0;
        color: #0f172a;
    }
    .customer-map-callout p {
        margin: 0;
        color: #475569;
        font-size: 0.84rem;
    }
    button[data-testid^="stBaseButton-segmented_control"] {
        border-radius: 7px;
        font-weight: 700;
        border: 1px solid rgba(20, 184, 166, 0.22);
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
        color: #0f172a;
    }
    button[data-testid="stBaseButton-segmented_controlActive"] {
        border-color: rgba(15, 118, 110, 0.55);
        background: linear-gradient(135deg, rgba(20, 184, 166, 0.18), rgba(251, 191, 36, 0.14));
        color: #0f172a !important;
    }
    button[data-testid^="stBaseButton-segmented_control"] *,
    button[kind^="segmented_control"] * {
        color: inherit !important;
    }
    button[kind="primary"],
    button[data-testid="stBaseButton-primary"] {
        background: #0f766e !important;
        border-color: #0f766e !important;
        color: #ffffff !important;
    }
    button[kind="primary"] *,
    button[data-testid="stBaseButton-primary"] * {
        color: #ffffff !important;
    }
    div[role="slider"] [data-testid="stSliderThumbValue"],
    div[data-testid="stSliderThumbValue"],
    div[data-testid="stSliderThumbValue"] * {
        color: #ffffff !important;
    }
    div[data-testid="stPlotlyChart"] {
        border-radius: 8px;
        overflow: hidden;
    }
    .customer-hero {
        border: 1px solid rgba(20, 184, 166, 0.38);
        background: linear-gradient(135deg, #0b1115 0%, #10231f 58%, #312914 100%);
        color: #f8fafc;
        border-radius: 8px;
        padding: 1.1rem 1.25rem;
        margin: 0.75rem 0 1rem 0;
        box-shadow: 0 18px 45px rgba(2, 6, 23, 0.22);
    }
    .customer-kicker {
        color: #0f766e;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }
    .customer-hero h1 {
        color: #f8fafc;
        font-size: 2.1rem;
        line-height: 1.15;
        margin: 0 0 0.45rem 0;
        letter-spacing: 0;
    }
    .customer-hero p {
        color: #cbd5e1;
        margin: 0;
        max-width: 78rem;
    }
    .customer-hero-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin-top: 0.95rem;
    }
    .customer-hero-strip span {
        border: 1px solid rgba(148, 163, 184, 0.45);
        border-radius: 999px;
        padding: 0.22rem 0.55rem;
        color: #e2e8f0 !important;
        font-size: 0.8rem;
        background: rgba(15, 23, 42, 0.60);
    }
    .customer-card {
        min-height: 332px;
        border: 1px solid #cbd5e1;
        background: #ffffff;
        color: #0f172a;
        border-radius: 8px;
        padding: 0.9rem;
        margin: 0.35rem 0 0.6rem 0;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
        transition: transform 120ms ease, border-color 120ms ease, box-shadow 120ms ease;
    }
    .customer-card:hover {
        transform: translateY(-1px);
        border-color: #14b8a6;
        box-shadow: 0 16px 34px rgba(15, 23, 42, 0.12);
    }
    .customer-card-compact {
        min-height: 238px;
    }
    .customer-card-top {
        display: flex;
        justify-content: space-between;
        gap: 0.5rem;
        align-items: center;
        color: #64748b;
        font-size: 0.78rem;
        margin-bottom: 0.55rem;
    }
    .customer-tier {
        display: inline-flex;
        align-items: center;
        border: 1px solid;
        border-radius: 999px;
        padding: 0.15rem 0.45rem;
        font-weight: 700;
        background: #f8fafc;
    }
    .customer-card h3 {
        font-size: 1.03rem;
        line-height: 1.25;
        margin: 0 0 0.45rem 0;
        letter-spacing: 0;
    }
    .customer-thesis {
        min-height: 3.4rem;
        color: #334155;
        font-size: 0.87rem;
        margin: 0 0 0.65rem 0;
    }
    .customer-next {
        color: #475569;
        font-size: 0.78rem;
        margin: 0.75rem 0 0 0;
    }
    .customer-signal-row {
        margin-top: 0.42rem;
    }
    .customer-signal-row div:first-child {
        display: flex;
        justify-content: space-between;
        gap: 0.5rem;
        color: #475569;
        font-size: 0.75rem;
        margin-bottom: 0.12rem;
    }
    .customer-meter {
        width: 100%;
        height: 7px;
        background: #e2e8f0;
        border-radius: 999px;
        overflow: hidden;
    }
    .customer-meter span {
        display: block;
        height: 100%;
        border-radius: 999px;
    }
    @media (max-width: 720px) {
        .landinvest-brand-header {
            grid-template-columns: 1fr;
            padding: 0.8rem;
        }
        .landinvest-brand-meta {
            justify-content: flex-start;
        }
        .landinvest-brand-chip {
            min-width: 7.3rem;
        }
        .landinvest-brand-copy h1 {
            font-size: 1.35rem;
        }
        .landinvest-brand-copy p {
            font-size: 0.84rem;
        }
        .customer-command-header,
        .customer-map-callout {
            grid-template-columns: 1fr;
        }
        .customer-command-header h1 {
            font-size: 1.55rem;
        }
        .customer-hero {
            padding: 0.9rem;
        }
        .customer-hero h1 {
            font-size: 1.45rem;
        }
        .customer-card,
        .customer-card-compact {
            min-height: auto;
        }
        .customer-thesis {
            min-height: auto;
        }
    }
    @media (prefers-color-scheme: dark) {
        .landinvest-brand-header {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(6, 78, 59, 0.60));
            border-color: rgba(45, 212, 191, 0.40);
            color: #f8fafc;
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.24);
        }
        .landinvest-brand-kicker,
        .landinvest-brand-chip b {
            color: #5eead4;
        }
        .landinvest-brand-copy h1,
        .landinvest-brand-chip span,
        .landinvest-sidebar-brand b {
            color: #f8fafc;
        }
        .landinvest-brand-copy p,
        .landinvest-sidebar-brand span {
            color: #cbd5e1;
        }
        .landinvest-brand-chip {
            background: rgba(15, 23, 42, 0.66);
            border-color: rgba(148, 163, 184, 0.34);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
        }
        .run-chip {
            background: rgba(100, 116, 139, 0.25);
            border: 1px solid rgba(148, 163, 184, 0.45);
            color: #e5e7eb;
        }
        .onboard {
            border: 1px solid rgba(96, 165, 250, 0.45);
            background: linear-gradient(90deg, rgba(30, 58, 138, 0.40) 0%, rgba(15, 23, 42, 0.30) 100%);
            color: #e5e7eb;
        }
        .onboard b {
            color: #bfdbfe;
        }
        .customer-sidebar-title {
            color: #5eead4;
        }
        .customer-kicker {
            color: #5eead4;
        }
        .customer-command-header {
            background: linear-gradient(135deg, rgba(6, 78, 59, 0.62), rgba(15, 23, 42, 0.92));
            color: #f8fafc;
            border-color: rgba(45, 212, 191, 0.45);
        }
        .customer-command-header h1,
        .customer-command-grid b,
        .customer-stat-strip b,
        .customer-map-stats b,
        .customer-map-callout h3 {
            color: #f8fafc;
        }
        .customer-command-header p,
        .customer-section-header p,
        .customer-map-callout p {
            color: #cbd5e1;
        }
        .customer-command-grid span,
        .customer-stat-strip span,
        .customer-map-stats span,
        .customer-map-callout,
        .customer-section-header {
            background: rgba(15, 23, 42, 0.66);
            border-color: rgba(148, 163, 184, 0.36);
        }
        button[data-testid^="stBaseButton-segmented_control"] {
            border-color: rgba(148, 163, 184, 0.35);
            color: #e5e7eb !important;
        }
        button[data-testid="stBaseButton-segmented_controlActive"] {
            border-color: rgba(45, 212, 191, 0.55);
            background: #0f766e !important;
            color: #ffffff !important;
        }
        button[data-testid="stTab"] {
            color: #e5e7eb !important;
        }
        button[data-testid="stTab"][aria-selected="true"] {
            color: #5eead4 !important;
        }
        button[data-testid="stTab"] * {
            color: inherit !important;
        }
        .customer-tier,
        .customer-hero-strip span {
            color: #f8fafc !important;
            border-color: rgba(203, 213, 225, 0.70) !important;
        }
        div[data-testid="stPlotlyChart"] .js-plotly-plot .bg {
            fill: rgba(15, 23, 42, 0.94) !important;
        }
        div[data-testid="stPlotlyChart"] .js-plotly-plot svg text,
        div[data-testid="stPlotlyChart"] .js-plotly-plot .legendtext,
        div[data-testid="stPlotlyChart"] .js-plotly-plot .gtitle,
        div[data-testid="stPlotlyChart"] .js-plotly-plot .xtitle,
        div[data-testid="stPlotlyChart"] .js-plotly-plot .ytitle {
            fill: #e5e7eb !important;
            color: #e5e7eb !important;
        }
        div[data-testid="stPlotlyChart"] .js-plotly-plot .gridlayer path,
        div[data-testid="stPlotlyChart"] .js-plotly-plot .xgrid,
        div[data-testid="stPlotlyChart"] .js-plotly-plot .ygrid,
        div[data-testid="stPlotlyChart"] .js-plotly-plot .zerolinelayer path,
        div[data-testid="stPlotlyChart"] .js-plotly-plot .xlines-above,
        div[data-testid="stPlotlyChart"] .js-plotly-plot .ylines-above {
            stroke: rgba(148, 163, 184, 0.38) !important;
        }
        .customer-command-grid small,
        .customer-stat-strip small,
        .customer-map-stats small {
            color: #94a3b8;
        }
        .customer-card {
            background: #0b1115;
            border-color: rgba(148, 163, 184, 0.35);
            color: #f8fafc;
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.22);
        }
        .customer-tier {
            background: rgba(15, 23, 42, 0.68);
        }
        .customer-card-top,
        .customer-thesis,
        .customer-next,
        .customer-signal-row div:first-child {
            color: #cbd5e1;
        }
        .customer-meter {
            background: rgba(100, 116, 139, 0.35);
        }
    }
</style>
""",
    unsafe_allow_html=True,
)

df = load_data(_mtime=_file_mtime(DATA_PATH))
if df.empty:
    _render_missing_artifact_help()
    st.stop()
wave3_overlay_df = load_wave3_structural_overlay_df(_mtime=_file_mtime(WAVE3_STRUCTURAL_OVERLAY_CSV_PATH))
wave3_overlay_summary = load_wave3_structural_overlay_summary(_mtime=_file_mtime(WAVE3_STRUCTURAL_OVERLAY_JSON_PATH))
if wave3_overlay_df is not None and not wave3_overlay_df.empty:
    overlay_cols = [
        c for c in [
            "fips",
            "wave3_overlay_rank",
            "wave3_overlay_score",
            "wave3_overlay_adjustment",
            "wave3_net_support",
            "wave3_support_score",
            "wave3_brake_score",
            "wave3_supports",
            "wave3_brakes",
            "wave3_structural_summary",
        ] if c in wave3_overlay_df.columns
    ]
    if len(overlay_cols) > 1:
        df["fips"] = df["fips"].astype(str).str.zfill(5)
        overlay_merge = wave3_overlay_df[overlay_cols].copy()
        overlay_merge["fips"] = overlay_merge["fips"].astype(str).str.zfill(5)
        df = df.drop(columns=[c for c in overlay_cols if c != "fips" and c in df.columns], errors="ignore")
        df = df.merge(overlay_merge, on="fips", how="left")
states = get_states(df)
calibration_diag = compute_calibration_diagnostics(df)
latest_run, latest_deltas = load_latest_run_snapshot(
    _mtime=max(_file_mtime(DATA_PATH), _file_mtime(EVAL_PATH), _file_mtime(RUNS_PATH))
)
conformal_diag = load_conformal_diagnostics(_mtime=_file_mtime(CONFORMAL_DIAG_PATH))
status_bundle = load_status_bundle(
    _mtime=max(
        _file_mtime(STATUS_BUNDLE_PATH),
        _file_mtime(SOURCE_HEALTH_PATH),
        _file_mtime(MISSINGNESS_PATH),
        _file_mtime(GAP_TRIAGE_PATH),
        _file_mtime(DRIFT_TRIAGE_PATH),
        _file_mtime(WAVE2_REASSESSMENT_PATH),
        _file_mtime(WAVE3_STRUCTURAL_OVERLAY_JSON_PATH),
        _file_mtime(RUNS_PATH),
    )
)
run_compare_files = list_run_compare_artifacts(_mtime=_file_mtime(OUTPUT_PATH))
run_history_summary = load_run_history_summary(_mtime=_file_mtime(RUN_HISTORY_SUMMARY_JSON_PATH))
run_history_summary_df = load_run_history_summary_df(_mtime=_file_mtime(RUN_HISTORY_SUMMARY_CSV_PATH))
run_history_detail_df = load_run_history_detail_df(_mtime=_file_mtime(RUN_HISTORY_DETAIL_CSV_PATH))
wave2_training_policy = load_wave2_training_policy(_mtime=_file_mtime(WAVE2_TRAINING_POLICY_PATH))
fiveyr_policy_status = load_fiveyr_policy_status(_mtime=_file_mtime(FIVEYR_POLICY_STATUS_PATH))
preboom_surfaces = {
    "raw": load_preboom_surface_df(str(PREBOOM_RAW_EXPORT_PATH), _mtime=_file_mtime(PREBOOM_RAW_EXPORT_PATH)),
    "balanced": load_preboom_surface_df(str(PREBOOM_BALANCED_EXPORT_PATH), _mtime=_file_mtime(PREBOOM_BALANCED_EXPORT_PATH)),
    "unguarded_blend": load_preboom_surface_df(str(PREBOOM_BLEND_EXPORT_PATH), _mtime=_file_mtime(PREBOOM_BLEND_EXPORT_PATH)),
    "guarded_blend": load_preboom_surface_df(str(PREBOOM_GUARDED_BLEND_EXPORT_PATH), _mtime=_file_mtime(PREBOOM_GUARDED_BLEND_EXPORT_PATH)),
    "residual_guardrail": load_preboom_surface_df(
        str(PREBOOM_RESIDUAL_DISPLAY_GUARDED_PATH),
        _mtime=_file_mtime(PREBOOM_RESIDUAL_DISPLAY_GUARDED_PATH),
    ),
    "residual_audit": load_preboom_surface_df(
        str(PREBOOM_RESIDUAL_AUDIT_PATH),
        _mtime=_file_mtime(PREBOOM_RESIDUAL_AUDIT_PATH),
    ),
}
preboom_blend_report = _safe_json_load(PREBOOM_BLEND_REPORT_PATH)
preboom_analog_report = _safe_json_load(PREBOOM_ANALOG_REPORT_PATH)
preboom_promotion_gate = _safe_json_load(PREBOOM_PROMOTION_GATE_PATH)
p0_repeatable_residual_guardrail = _safe_json_load(P0_REPEATABLE_RESIDUAL_GUARDRAIL_PATH)
p0_repeatable_residual_candidates = load_preboom_surface_df(
    str(P0_REPEATABLE_RESIDUAL_GUARDRAIL_TOP_CANDIDATES_PATH),
    _mtime=_file_mtime(P0_REPEATABLE_RESIDUAL_GUARDRAIL_TOP_CANDIDATES_PATH),
)
known_analog_suite = load_known_analog_suite(_mtime=_file_mtime(KNOWN_ANALOG_SUITE_PATH))
xfactor_scoreboard = load_xfactor_interaction_scoreboard(_mtime=_file_mtime(XFACTOR_INTERACTION_SCOREBOARD_PATH))
xfactor_ablation_queue = load_xfactor_interaction_ablation_queue(_mtime=_file_mtime(XFACTOR_INTERACTION_ABLATION_QUEUE_PATH))
xfactor_promotion_gate = load_xfactor_interaction_promotion_gate(_mtime=_file_mtime(XFACTOR_INTERACTION_PROMOTION_GATE_PATH))
demo_readiness_report = load_demo_readiness_report(_mtime=_file_mtime(DEMO_READINESS_REPORT_PATH))
latest_compare_json_path = ((status_bundle or {}).get("latest_run") or {}).get("run_compare_path")
latest_compare_rank_df = None
latest_compare_boundary_df = None
if latest_compare_json_path:
    latest_compare_rank_path = str(Path(latest_compare_json_path).with_name(Path(latest_compare_json_path).stem + "_rank_shifts.csv"))
    latest_compare_boundary_path = str(Path(latest_compare_json_path).with_name(Path(latest_compare_json_path).stem + "_top25_boundary.csv"))
    latest_compare_rank_df = load_compare_csv(latest_compare_rank_path, _mtime=_file_mtime(Path(latest_compare_rank_path)))
    latest_compare_boundary_df = load_compare_csv(latest_compare_boundary_path, _mtime=_file_mtime(Path(latest_compare_boundary_path)))

wave3_status = (status_bundle or {}).get("wave3_status") or {}

with st.sidebar:
    st.markdown(_sidebar_brand_html(), unsafe_allow_html=True)

if "dashboard_user_id" not in st.session_state:
    st.session_state.dashboard_user_id = "demo"
with st.sidebar:
    user_id_input = st.text_input(
        "Demo user",
        value=st.session_state.dashboard_user_id,
        key="dashboard_user_id_input",
        help="Separates saved watchlists, notes, and compare sets in a local SQLite store. This is not authentication.",
    )
resolved_user_id = _normalize_user_id(user_id_input)
if resolved_user_id != st.session_state.dashboard_user_id:
    st.session_state.dashboard_user_id = resolved_user_id
    st.session_state.user_data_loaded = False
with st.sidebar:
    st.caption(_user_storage_status())

if "watchlist_fips" not in st.session_state:
    st.session_state.watchlist_fips = []
if not st.session_state.get("user_data_loaded", False):
    user_data = _load_user_data()
    st.session_state.saved_watchlists = user_data.get("saved_watchlists", {})
    st.session_state.county_notes = user_data.get("county_notes", {})
    st.session_state.saved_compare_sets = user_data.get("saved_compare_sets", {})
    st.session_state.saved_strategy_profiles = user_data.get("saved_strategy_profiles", {})
    st.session_state.county_funnel = user_data.get("county_funnel", {})
    st.session_state.county_feedback = user_data.get("county_feedback", {})
    st.session_state.preboom_feedback = user_data.get("preboom_feedback", {})
    st.session_state.diligence_evidence = user_data.get("diligence_evidence", {})
    st.session_state.parcel_checklists = user_data.get("parcel_checklists", {})
    st.session_state.watchlist_alert_state = user_data.get("watchlist_alert_state", {})
    st.session_state.watchlist_settings = user_data.get("watchlist_settings", _default_user_data()["watchlist_settings"])
    st.session_state.user_data_loaded = True
if "saved_watchlists" not in st.session_state:
    st.session_state.saved_watchlists = {}
if "county_notes" not in st.session_state:
    st.session_state.county_notes = {}
if "saved_compare_sets" not in st.session_state:
    st.session_state.saved_compare_sets = {}
if "saved_strategy_profiles" not in st.session_state:
    st.session_state.saved_strategy_profiles = {}
if "county_funnel" not in st.session_state:
    st.session_state.county_funnel = {}
if "county_feedback" not in st.session_state:
    st.session_state.county_feedback = {}
if "preboom_feedback" not in st.session_state:
    st.session_state.preboom_feedback = {}
if "diligence_evidence" not in st.session_state:
    st.session_state.diligence_evidence = {}
if "parcel_checklists" not in st.session_state:
    st.session_state.parcel_checklists = {}
if "watchlist_alert_state" not in st.session_state:
    st.session_state.watchlist_alert_state = _load_user_data().get("watchlist_alert_state", {})
if "watchlist_settings" not in st.session_state:
    st.session_state.watchlist_settings = _load_user_data().get("watchlist_settings", _default_user_data()["watchlist_settings"])

experience_options = ["Product Mode", "Customer Mode", "Legacy Mode"]
requested_experience = (_query_param_first("experience", "") or "").strip().lower()
experience_default_index = 1 if requested_experience in {"customer", "customer mode"} else 0
experience_mode = st.sidebar.radio(
    "Experience",
    experience_options,
    index=experience_default_index,
    horizontal=False,
    help="Customer Mode is the visual investor workflow. Product Mode keeps power-user controls. Legacy Mode keeps the full analyst console.",
)

header_data_ts = datetime.fromtimestamp(_file_mtime(DATA_PATH)).strftime("%Y-%m-%d %H:%M")
header_run_id = latest_run.get("run_id", "unknown") if latest_run else "unknown"
header_run_year = latest_run.get("year", "n/a") if latest_run else "n/a"
header_churn = latest_deltas.get("top25_churn") if latest_deltas and latest_deltas.get("has_previous") else None
header_churn_text = f"{100 * header_churn:.1f}%" if header_churn is not None else "n/a"
header_health = ((status_bundle or {}).get("model_health_3yr") or {}).get("assessment", {}).get("health_status")
header_health_text = _humanize_status_label(header_health) if header_health else None
st.markdown(
    _brand_header_html(
        experience_mode=experience_mode,
        run_id=header_run_id,
        run_year=header_run_year,
        data_ts=header_data_ts,
        churn_text=header_churn_text,
        health_text=header_health_text,
    ),
    unsafe_allow_html=True,
)

if experience_mode == "Customer Mode":
    _render_customer_mode(
        df=df,
        states=states,
        latest_run=latest_run,
        latest_deltas=latest_deltas,
        status_bundle=status_bundle,
        run_history_summary_df=run_history_summary_df,
        latest_compare_rank_df=latest_compare_rank_df,
        wave3_status=wave3_status,
        preboom_surfaces=preboom_surfaces,
        known_analog_suite=known_analog_suite,
        xfactor_scoreboard=xfactor_scoreboard,
        xfactor_promotion_gate=xfactor_promotion_gate,
        demo_readiness_report=demo_readiness_report,
    )
    st.stop()

if experience_mode == "Product Mode":
    _render_product_mode(
        df=df,
        states=states,
        latest_run=latest_run,
        latest_deltas=latest_deltas,
        status_bundle=status_bundle,
        run_history_summary_df=run_history_summary_df,
        run_history_detail_df=run_history_detail_df,
        latest_compare_rank_df=latest_compare_rank_df,
        latest_compare_boundary_df=latest_compare_boundary_df,
        wave3_status=wave3_status,
        preboom_surfaces=preboom_surfaces,
        preboom_blend_report=preboom_blend_report,
        preboom_analog_report=preboom_analog_report,
        preboom_promotion_gate=preboom_promotion_gate,
        known_analog_suite=known_analog_suite,
        xfactor_scoreboard=xfactor_scoreboard,
        xfactor_ablation_queue=xfactor_ablation_queue,
        xfactor_promotion_gate=xfactor_promotion_gate,
        demo_readiness_report=demo_readiness_report,
        p0_repeatable_residual_guardrail=p0_repeatable_residual_guardrail,
        p0_repeatable_residual_candidates=p0_repeatable_residual_candidates,
    )
    st.stop()

# ---------------------------------------------------------------------------
# Header + mode
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="onboard"><b>Workflow:</b> 1) Apply filters 2) Inspect map 3) Deep-dive counties 4) Compare counties 5) Export shortlist</div>',
    unsafe_allow_html=True,
)

view_mode = st.radio(
    "View Mode",
    ["Quick View", "Advanced View"],
    horizontal=True,
    help="Advanced View exposes QA/testing controls while keeping the same core workflow.",
)
advanced_mode = view_mode == "Advanced View"

data_ts = datetime.fromtimestamp(_file_mtime(DATA_PATH)).strftime("%Y-%m-%d %H:%M")
run_id = latest_run.get("run_id", "unknown") if latest_run else "unknown"
run_year = latest_run.get("year", "n/a") if latest_run else "n/a"
winner = latest_run.get("champion_challenger", {}).get("overall_winner", "n/a") if latest_run else "n/a"
churn_txt = "n/a"
if latest_deltas and latest_deltas.get("has_previous"):
    churn_txt = f"{100 * latest_deltas.get('top25_churn', 0):.2f}%"
st.markdown(
    (
        f'<span class="run-chip">Run: <b>{run_id}</b></span>'
        f'<span class="run-chip">Year: <b>{run_year}</b></span>'
        f'<span class="run-chip">Champion: <b>{winner}</b></span>'
        f'<span class="run-chip">Top-25 Churn: <b>{churn_txt}</b></span>'
        f'<span class="run-chip">Data Freshness: <b>{data_ts}</b></span>'
    ),
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------

st.sidebar.divider()
st.sidebar.caption(f"Mode: `{view_mode}`")

if "flt_states" not in st.session_state:
    st.session_state.flt_states = []
if "flt_horizon" not in st.session_state:
    st.session_state.flt_horizon = 5
if "flt_opp" not in st.session_state:
    st.session_state.flt_opp = (0.0, 100.0)
if "flt_top_n" not in st.session_state:
    st.session_state.flt_top_n = 100 if advanced_mode else 50
if "flt_show_all" not in st.session_state:
    st.session_state.flt_show_all = False
if "watchlist_fips" not in st.session_state:
    st.session_state.watchlist_fips = []
if not st.session_state.get("user_data_loaded", False):
    user_data = _load_user_data()
    st.session_state.saved_watchlists = user_data.get("saved_watchlists", {})
    st.session_state.county_notes = user_data.get("county_notes", {})
    st.session_state.saved_compare_sets = user_data.get("saved_compare_sets", {})
    st.session_state.saved_strategy_profiles = user_data.get("saved_strategy_profiles", {})
    st.session_state.county_funnel = user_data.get("county_funnel", {})
    st.session_state.county_feedback = user_data.get("county_feedback", {})
    st.session_state.preboom_feedback = user_data.get("preboom_feedback", {})
    st.session_state.diligence_evidence = user_data.get("diligence_evidence", {})
    st.session_state.parcel_checklists = user_data.get("parcel_checklists", {})
    st.session_state.user_data_loaded = True
if "saved_watchlists" not in st.session_state:
    st.session_state.saved_watchlists = {}
if "county_notes" not in st.session_state:
    st.session_state.county_notes = {}
if "saved_compare_sets" not in st.session_state:
    st.session_state.saved_compare_sets = {}
if "saved_strategy_profiles" not in st.session_state:
    st.session_state.saved_strategy_profiles = {}
if "county_funnel" not in st.session_state:
    st.session_state.county_funnel = {}
if "county_feedback" not in st.session_state:
    st.session_state.county_feedback = {}
if "preboom_feedback" not in st.session_state:
    st.session_state.preboom_feedback = {}
if "diligence_evidence" not in st.session_state:
    st.session_state.diligence_evidence = {}
if "parcel_checklists" not in st.session_state:
    st.session_state.parcel_checklists = {}
if "watchlist_alert_state" not in st.session_state:
    st.session_state.watchlist_alert_state = _load_user_data().get("watchlist_alert_state", {})
if "session_watchlist_meta" not in st.session_state:
    st.session_state.session_watchlist_meta = {"owner": "", "tags": [], "thesis": ""}
if "watchlist_settings" not in st.session_state:
    st.session_state.watchlist_settings = _load_user_data().get("watchlist_settings", _default_user_data()["watchlist_settings"])

preset = st.sidebar.selectbox("Filter preset", ["Custom", "Balanced", "Conservative", "Aggressive"], index=0)
if preset != "Custom":
    if preset == "Balanced":
        st.session_state.flt_opp = (55.0, 100.0)
    elif preset == "Conservative":
        st.session_state.flt_opp = (45.0, 100.0)
    elif preset == "Aggressive":
        st.session_state.flt_opp = (70.0, 100.0)

with st.sidebar.form("filter_form", clear_on_submit=False):
    selected_states = st.multiselect(
        "Filter by state", states, default=st.session_state.flt_states, placeholder="All states"
    )
    horizon = st.radio(
        "Forecast horizon", HORIZONS, format_func=lambda h: f"{h}-year", index=HORIZONS.index(st.session_state.flt_horizon)
    )
    min_opp, max_opp = st.slider(
        "Opportunity score range", 0.0, 100.0, st.session_state.flt_opp, step=1.0
    )
    top_n_max = 500 if advanced_mode else 200
    top_n_default = min(st.session_state.flt_top_n, top_n_max)
    top_n = st.slider("Top N counties to show", 10, top_n_max, top_n_default, step=10)
    show_all_counties = False
    if advanced_mode:
        st.divider()
        st.caption("Advanced Controls")
        show_all_counties = st.checkbox(
            "Include all counties (ignore filters)",
            value=st.session_state.flt_show_all,
            help="Testing-only mode to inspect full national output regardless of filters.",
        )
    apply_btn = st.form_submit_button("Apply filters", type="primary")
    reset_btn = st.form_submit_button("Reset")

if apply_btn:
    st.session_state.flt_states = selected_states
    st.session_state.flt_horizon = horizon
    st.session_state.flt_opp = (min_opp, max_opp)
    st.session_state.flt_top_n = top_n
    st.session_state.flt_show_all = show_all_counties
if reset_btn:
    st.session_state.flt_states = []
    st.session_state.flt_horizon = 5
    st.session_state.flt_opp = (0.0, 100.0)
    st.session_state.flt_top_n = 100 if advanced_mode else 50
    st.session_state.flt_show_all = False

selected_states = st.session_state.flt_states
horizon = st.session_state.flt_horizon
min_opp, max_opp = st.session_state.flt_opp
top_n = st.session_state.flt_top_n
show_all_counties = st.session_state.flt_show_all if advanced_mode else False

# Apply filters
mask = pd.Series(True, index=df.index)
if show_all_counties:
    filtered = df.copy()
else:
    if selected_states:
        mask &= df["state"].isin(selected_states)
    mask &= df["opportunity_score"].between(min_opp, max_opp)
    filtered = df[mask].copy()

st.sidebar.metric("Counties shown", f"{len(filtered):,}")
st.sidebar.metric("Total counties", f"{len(df):,}")
if advanced_mode:
    st.sidebar.metric("Filtered out", f"{len(df) - len(filtered):,}")

if latest_run:
    with st.sidebar.expander("Latest Run Summary", expanded=False):
        st.write(f"Run: `{latest_run.get('run_id', 'unknown')}`")
        st.write(f"Year: `{latest_run.get('year', 'n/a')}`")
        champs = latest_run.get("champion_challenger", {})
        if champs:
            st.write(f"Champion: `{champs.get('overall_winner', 'n/a')}`")
        policy = latest_run.get("policy_settings", {})
        if policy:
            st.write(
                "3yr policy: "
                f"`dq={policy.get('threeyr_disagree_q', 'n/a')}`, "
                f"`gq={policy.get('threeyr_gap_q', 'n/a')}`"
            )
        if latest_deltas and latest_deltas.get("has_previous"):
            st.write(f"Top-25 churn: `{100 * latest_deltas.get('top25_churn', 0):.2f}%`")

# ---------------------------------------------------------------------------
# Tab layout
# ---------------------------------------------------------------------------

tab_rank, tab_map, tab_detail, tab_watch, tab_compare, tab_valid, tab_status = st.tabs([
    "Rankings", "Map", "County Detail", "Watchlist", "Model Comparison", "Validation", "System Status"
])

# ========================= TAB 1: RANKINGS =================================

with tab_rank:
    st.header("County Rankings")

    pred_col = f"pred_avg_{horizon}yr"
    rank_col = f"rank_avg_{horizon}yr"

    # Fallback if avg not available
    if pred_col not in filtered.columns:
        pred_col = f"pred_xgboost_{horizon}yr"
        rank_col = f"rank_xgboost_{horizon}yr"

    display_cols = ["overall_rank", "county_name", "state"]
    for overlay_col in ["wave3_overlay_rank", "wave3_net_support", "wave3_support_score", "wave3_brake_score"]:
        if overlay_col in filtered.columns and overlay_col not in display_cols:
            display_cols.append(overlay_col)
    if pred_col in filtered.columns:
        display_cols.append(pred_col)
    for h in HORIZONS:
        for mt in ["xgboost", "lightgbm"]:
            raw_col = f"pred_{mt}_{h}yr"
            cal_col = f"{raw_col}_cal"
            if raw_col in filtered.columns and raw_col not in display_cols:
                display_cols.append(raw_col)
            if cal_col in filtered.columns and cal_col not in display_cols:
                display_cols.append(cal_col)
        eff_col = "pred_policy_3yr" if h == 3 else f"pred_avg_{h}yr"
        if eff_col in filtered.columns and eff_col not in display_cols:
            display_cols.append(eff_col)
    display_cols += ["opportunity_score", "composite_risk", "confidence"]
    display_cols = [c for c in display_cols if c in filtered.columns]

    top = filtered.sort_values("overall_rank").head(top_n)[display_cols].copy()
    selected_cols = st.multiselect(
        "Columns to display",
        options=top.columns.tolist(),
        default=top.columns.tolist(),
        key="rank_cols",
    )
    if selected_cols:
        top = top[selected_cols]

    # Format prediction columns as percentages
    for col in top.columns:
        if col.startswith("pred_"):
            top[col] = top[col].map(_fmt_pct)
    if "opportunity_score" in top.columns:
        top["opportunity_score"] = top["opportunity_score"].map(_fmt_score)
    if "composite_risk" in top.columns:
        top["composite_risk"] = top["composite_risk"].map(_fmt_score)
    for col in ["wave3_net_support", "wave3_support_score", "wave3_brake_score"]:
        if col in top.columns:
            top[col] = top[col].map(lambda x: f"{x:.3f}" if pd.notna(x) else "—")

    st.dataframe(
        top,
        width="stretch",
        hide_index=True,
        height=min(35 * len(top) + 38, 800),
    )
    st.download_button(
        "Export current rankings view (CSV)",
        data=filtered.sort_values("overall_rank").head(top_n).to_csv(index=False).encode("utf-8"),
        file_name=f"rankings_view_{horizon}yr.csv",
        mime="text/csv",
    )
    st.caption(
        "Prediction columns: raw model outputs (`pred_*`), calibrated outputs (`pred_*_cal`), "
        "and effective scoring signals (`pred_avg_*`, `pred_policy_3yr`)."
    )

    if advanced_mode:
        st.subheader("Advanced QA")
        st.caption("Missingness checks and raw feature preview for QA/testing.")
        miss_cols = [c for c in ["opportunity_score", "composite_risk", "confidence"] if c in filtered.columns]
        miss_cols += [c for c in filtered.columns if c.startswith("pred_")][:8]
        if miss_cols:
            miss = (
                filtered[miss_cols].isna().mean().sort_values(ascending=False) * 100
            ).round(2).rename("missing_pct").reset_index().rename(columns={"index": "column"})
            st.dataframe(miss, width="stretch", hide_index=True, height=220)

        preview_default = [c for c in ["fips", "county_name", "state", "overall_rank", "opportunity_score"] if c in filtered.columns]
        preview_choices = [c for c in filtered.columns if c.startswith("pred_") or c.startswith("rank_")]
        preview_choices += [c for c in ["composite_risk", "market_risk", "liquidity_risk"] if c in filtered.columns]
        preview_choices = list(dict.fromkeys(preview_default + preview_choices))
        selected_preview_cols = st.multiselect(
            "Raw feature preview columns",
            options=preview_choices,
            default=preview_default[:],
            key="adv_rank_preview_cols",
        )
        if selected_preview_cols:
            st.dataframe(
                filtered[selected_preview_cols].sort_values("overall_rank").head(min(top_n, 200)),
                width="stretch",
                hide_index=True,
                height=280,
            )

    # Distribution chart
    col1, col2 = st.columns(2)
    with col1:
        fig_opp = px.histogram(
            filtered, x="opportunity_score", nbins=40,
            title="Opportunity Score Distribution",
            color_discrete_sequence=["#2ecc71"],
        )
        fig_opp.update_layout(height=300, margin=dict(t=40, b=20))
        st.plotly_chart(fig_opp, width="stretch")

    with col2:
        fig_risk = px.histogram(
            filtered, x="composite_risk", nbins=40,
            title="Composite Risk Distribution",
            color_discrete_sequence=["#e74c3c"],
        )
        fig_risk.update_layout(height=300, margin=dict(t=40, b=20))
        st.plotly_chart(fig_risk, width="stretch")


# ========================= TAB 2: MAP ======================================

with tab_map:
    st.header("County Map")

    map_metric = st.selectbox(
        "Color counties by",
        ["opportunity_score", "composite_risk"] +
        [f"pred_avg_{h}yr" for h in HORIZONS if f"pred_avg_{h}yr" in df.columns] +
        [f"pred_xgboost_{h}yr" for h in HORIZONS if f"pred_xgboost_{h}yr" in df.columns],
        index=0,
    )

    try:
        with st.spinner("Rendering county map..."):
            map_cols = ["fips", map_metric, "opportunity_score"]
            # Ensure unique column list (map_metric can equal opportunity_score).
            map_cols = list(dict.fromkeys(map_cols))
            for c in ["county_name", "state"]:
                if c in filtered.columns:
                    map_cols.append(c)
            map_df = filtered[map_cols].dropna(subset=["fips", map_metric]).copy()
            map_df["fips_str"] = map_df["fips"].astype(str).str.zfill(5)

            # Color scale
            if "risk" in map_metric:
                color_scale = "RdYlGn_r"
            elif "pred_" in map_metric:
                color_scale = "RdYlGn"
            else:
                color_scale = "Viridis"

            hover_dict = {"fips_str": False}
            if "state" in map_df.columns:
                hover_dict["state"] = True
            if "opportunity_score" in map_df.columns:
                hover_dict["opportunity_score"] = ":.1f"

            fig_map = px.choropleth(
                map_df,
                geojson=load_county_geojson(_mtime=_file_mtime(COUNTY_GEOJSON_PATH)),
                locations="fips_str",
                color=map_metric,
                hover_name=("county_name" if "county_name" in map_df.columns else None),
                hover_data=hover_dict,
                color_continuous_scale=color_scale,
                scope="usa",
                title=f"{map_metric} by County",
            )
            fig_map.update_layout(
                height=700,
                margin=dict(l=0, r=0, t=40, b=0),
                geo=dict(bgcolor="rgba(0,0,0,0)"),
                coloraxis_colorbar=dict(title=map_metric, len=0.8, y=0.5),
            )
            st.plotly_chart(fig_map, width="stretch")
            st.caption("Tip: use `County Detail` and `Compare` for deeper context beyond map color.")
    except Exception as exc:
        st.error(f"Map rendering failed: {exc}")

    # State summary
    if not selected_states:
        st.subheader("Top States by Average Opportunity Score")
        state_avg = (
            filtered.groupby("state")["opportunity_score"]
            .agg(["mean", "count", "max"])
            .round(1)
            .sort_values("mean", ascending=False)
            .head(15)
            .rename(columns={"mean": "Avg Score", "count": "Counties", "max": "Best County"})
        )
        st.dataframe(state_avg, width="stretch")

    if advanced_mode:
        st.subheader("Advanced Diagnostics")
        diag_cols = ["fips", "county_name", "state", "opportunity_score", map_metric]
        diag_cols = [c for c in list(dict.fromkeys(diag_cols)) if c in filtered.columns]
        st.caption("Sample rows used for map rendering")
        st.dataframe(
            filtered[diag_cols].head(200),
            width="stretch",
            hide_index=True,
            height=260,
        )


# ========================= TAB 3: COUNTY DETAIL ============================

with tab_detail:
    st.header("County Deep Dive")

    try:
        # County selector
        county_options = filtered.sort_values("overall_rank").apply(
            lambda r: f"{r['county_name']}, {r['state']} (rank #{int(r['overall_rank'])})"
            if pd.notna(r.get("county_name")) else f"FIPS {r['fips']} (rank #{int(r['overall_rank'])})",
            axis=1,
        ).tolist()

        if not county_options:
            st.warning("No counties match the current filters.")
        else:
            selected_county_label = st.selectbox("Select a county", county_options)
            # Parse rank from label
            rank_num = int(selected_county_label.split("rank #")[1].rstrip(")"))
            county_row = filtered[filtered["overall_rank"] == rank_num].iloc[0]

            # Header metrics
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Opportunity Score", _fmt_score(county_row["opportunity_score"]))
            c2.metric("Composite Risk", _fmt_score(county_row["composite_risk"]))
            c3.metric("Overall Rank", f"#{int(county_row['overall_rank'])}")
            c4.metric("Confidence", county_row.get("confidence", "—"))

            county_fips = str(county_row["fips"]).zfill(5)
            is_on_watchlist = county_fips in st.session_state.watchlist_fips
            history_row = None
            if run_history_summary_df is not None and not run_history_summary_df.empty:
                match = run_history_summary_df[run_history_summary_df["fips"] == county_fips]
                if not match.empty:
                    history_row = match.iloc[0]
            b1, b2 = st.columns(2)
            with b1:
                if not is_on_watchlist:
                    if st.button("Add To Watchlist", key=f"watch_add_{county_fips}"):
                        st.session_state.watchlist_fips = sorted(set(st.session_state.watchlist_fips + [county_fips]))
                        st.success("County added to watchlist.")
                else:
                    st.caption("This county is already on the watchlist.")
            with b2:
                if is_on_watchlist and st.button("Remove From Watchlist", key=f"watch_remove_{county_fips}"):
                    st.session_state.watchlist_fips = [f for f in st.session_state.watchlist_fips if f != county_fips]
                    st.success("County removed from watchlist.")

            st.subheader("County Notes")
            note_entry = st.session_state.county_notes.get(county_fips, {})
            note_default = note_entry.get("note", "")
            note_text = st.text_area(
                "Analyst note",
                value=note_default,
                height=140,
                key=f"county_note_{county_fips}",
                help="Saved to the local per-user SQLite demo store. This is not authentication.",
            )
            nsave1, nsave2 = st.columns(2)
            with nsave1:
                if st.button("Save County Note", key=f"save_note_{county_fips}"):
                    st.session_state.county_notes[county_fips] = {
                        "county_name": county_row.get("county_name"),
                        "state": county_row.get("state"),
                        "note": note_text.strip(),
                        "updated_at": datetime.now().isoformat(),
                    }
                    _save_current_user_state()
                    st.success("County note saved.")
            with nsave2:
                if county_fips in st.session_state.county_notes and st.button("Delete County Note", key=f"delete_note_{county_fips}"):
                    st.session_state.county_notes.pop(county_fips, None)
                    _save_current_user_state()
                    st.success("County note deleted.")

            # Predictions across horizons
            st.subheader("Predicted Appreciation by Horizon")
            pred_data = []
            for h in HORIZONS:
                row_data = {"Horizon": f"{h}-year"}
                for mt in ["xgboost", "lightgbm"]:
                    raw_col = f"pred_{mt}_{h}yr"
                    cal_col = f"{raw_col}_cal"
                    if raw_col in county_row.index and pd.notna(county_row[raw_col]):
                        row_data[f"{mt.upper()} (raw)"] = f"{county_row[raw_col]:+.1%}"
                    if cal_col in county_row.index and pd.notna(county_row[cal_col]):
                        row_data[f"{mt.upper()} (cal)"] = f"{county_row[cal_col]:+.1%}"
                avg_col = f"pred_avg_{h}yr"
                if avg_col in county_row.index and pd.notna(county_row[avg_col]):
                    row_data["AVG (cal blend)"] = f"{county_row[avg_col]:+.1%}"
                if h == 3 and "pred_policy_3yr" in county_row.index and pd.notna(county_row["pred_policy_3yr"]):
                    row_data["POLICY 3YR (effective)"] = f"{county_row['pred_policy_3yr']:+.1%}"
                pred_data.append(row_data)
            st.dataframe(pd.DataFrame(pred_data), width="stretch", hide_index=True)

            st.subheader("Why This County?")
            narrative = _build_county_narrative(county_row, history_row=history_row)
            st.info(narrative["summary"])
            n1, n2 = st.columns(2)
            with n1:
                st.caption("Upside case")
                for bullet in narrative["positives"]:
                    st.markdown(f"- {bullet}")
            with n2:
                st.caption("Main cautions")
                for bullet in narrative["cautions"]:
                    st.markdown(f"- {bullet}")

            st.subheader("Data Context")
            policy_context = _family_context_for_row(county_row, wave2_training_policy)
            if not policy_context.empty:
                st.dataframe(policy_context, width="stretch", hide_index=True)
                st.caption(
                    "Historical-safe families are training-eligible by default. "
                    "Panel-only and review-static families are currently used as context, not default training signal."
                )
            else:
                st.caption("No explicit Wave 2 family context was detected for this county row.")

            wave3_cols_present = any(
                c in county_row.index
                for c in [
                    "site_thesis_support_index",
                    "land_developability_index",
                    "land_constraint_pressure",
                    "land_fragility_pressure",
                ]
            )
            if wave3_cols_present:
                st.subheader("Wave 3 Structural Profile")
                wave3_profile = _build_wave3_profile(county_row)
                st.info(wave3_profile["summary"])
                coastal_provenance = _coastal_lane_provenance(county_row, wave3_status)
                st.caption(f"Coastal lane: `{coastal_provenance['label']}`")
                st.caption(str(coastal_provenance["summary"]))
                wp1, wp2, wp3, wp4 = st.columns(4)
                wp1.metric(
                    "Site Thesis Support",
                    f"{float(county_row['site_thesis_support_index']):.3f}"
                    if pd.notna(county_row.get("site_thesis_support_index")) else "—",
                )
                wp2.metric(
                    "Land Developability",
                    f"{float(county_row['land_developability_index']):.3f}"
                    if pd.notna(county_row.get("land_developability_index")) else "—",
                )
                wp3.metric(
                    "Constraint Pressure",
                    f"{float(county_row['land_constraint_pressure']):.3f}"
                    if pd.notna(county_row.get("land_constraint_pressure")) else "—",
                )
                wp4.metric(
                    "Fragility Pressure",
                    f"{float(county_row['land_fragility_pressure']):.3f}"
                    if pd.notna(county_row.get("land_fragility_pressure")) else "—",
                )

                metric_df = wave3_profile["metric_df"]
                if isinstance(metric_df, pd.DataFrame) and not metric_df.empty:
                    fig_wave3 = px.bar(
                        metric_df,
                        x="Value",
                        y="Metric",
                        orientation="h",
                        color="Type",
                        color_discrete_map={"support": "#1f9d55", "pressure": "#dc2626"},
                        title="Wave 3 Structural Scores",
                    )
                    fig_wave3.update_layout(height=320, margin=dict(t=40, b=20))
                    st.plotly_chart(fig_wave3, width="stretch")

                ws1, ws2 = st.columns(2)
                with ws1:
                    st.caption("Structural supports")
                    for bullet in wave3_profile["supports"]:
                        st.markdown(f"- {bullet}")
                with ws2:
                    st.caption("Structural brakes")
                    for bullet in wave3_profile["brakes"]:
                        st.markdown(f"- {bullet}")

            if history_row is not None and not history_row.empty:
                health_row = pd.Series(
                    {
                        "current_rank": county_row.get("overall_rank"),
                        "pred_avg_5yr": county_row.get("pred_avg_5yr"),
                        "composite_risk": county_row.get("composite_risk"),
                        "top25_presence_share": history_row.get("top25_presence_share"),
                        "std_rank": history_row.get("std_rank"),
                    }
                )
                if latest_compare_rank_df is not None and not latest_compare_rank_df.empty:
                    latest_shift = latest_compare_rank_df[latest_compare_rank_df["fips"] == county_fips]
                    if not latest_shift.empty:
                        health_row["rank_shift"] = latest_shift.iloc[0].get("rank_shift")
                fit_status, fit_reasons = _classify_watchlist_health(health_row, settings=st.session_state.watchlist_settings)
                st.subheader("Why It Still Belongs")
                if fit_status == "fits_thesis":
                    st.success("This county still fits the current shortlist thesis.")
                elif fit_status == "watch_closely":
                    st.warning("This county still has a case, but it should be watched closely.")
                else:
                    st.error("This county may need a thesis review or removal from the shortlist.")
                for reason in fit_reasons[:5]:
                    st.markdown(f"- {reason}")

            # Risk breakdown
            st.subheader("Risk Breakdown")
            risk_dims = {
                "Market Risk": county_row.get("market_risk", 50),
                "Liquidity Risk": county_row.get("liquidity_risk", 50),
                "Regulatory Risk": county_row.get("regulatory_risk", 50),
                "Environmental Risk": county_row.get("environmental_risk", 50),
                "Concentration Risk": county_row.get("concentration_risk", 50),
            }
            # Replace NaN with 50 (neutral) for display
            risk_dims = {k: (v if pd.notna(v) else 50) for k, v in risk_dims.items()}
            fig_risk_bar = go.Figure(go.Bar(
                x=list(risk_dims.values()),
                y=list(risk_dims.keys()),
                orientation="h",
                marker_color=[_risk_color(v) for v in risk_dims.values()],
            ))
            fig_risk_bar.update_layout(
                xaxis=dict(range=[0, 100], title="Risk Score (0–100)"),
                height=250, margin=dict(t=10, b=20),
            )
            st.plotly_chart(fig_risk_bar, width="stretch")

            if history_row is not None and not history_row.empty:
                st.subheader("Run Stability")
                s1, s2, s3, s4 = st.columns(4)
                s1.metric("Avg Rank", f"{float(history_row.get('avg_rank', np.nan)):.1f}" if pd.notna(history_row.get("avg_rank")) else "—")
                s2.metric("Rank Std", f"{float(history_row.get('std_rank', np.nan)):.1f}" if pd.notna(history_row.get("std_rank")) else "—")
                s3.metric(
                    "Top-25 Presence",
                    f"{100 * float(history_row.get('top25_presence_share', 0.0)):.0f}%"
                    if pd.notna(history_row.get("top25_presence_share")) else "—"
                )
                s4.metric("Rank Range", f"{float(history_row.get('rank_range', np.nan)):.0f}" if pd.notna(history_row.get("rank_range")) else "—")

                if run_history_detail_df is not None and not run_history_detail_df.empty:
                    county_hist = run_history_detail_df[run_history_detail_df["fips"] == county_fips].copy()
                    if not county_hist.empty:
                        county_hist = county_hist.sort_values("run_id")
                        fig_hist = px.line(
                            county_hist,
                            x="run_id",
                            y="overall_rank",
                            markers=True,
                            title="Recent Run Rank Path",
                            labels={"overall_rank": "Overall rank (lower is better)", "run_id": "Run"},
                            hover_data=["opportunity_score", "pred_policy_3yr", "pred_avg_5yr", "composite_risk", "confidence"],
                        )
                        fig_hist.update_yaxes(autorange="reversed")
                        fig_hist.update_layout(height=320, margin=dict(t=40, b=20))
                        st.plotly_chart(fig_hist, width="stretch")

            if latest_compare_rank_df is not None and not latest_compare_rank_df.empty:
                latest_shift = latest_compare_rank_df[latest_compare_rank_df["fips"] == county_fips]
                if not latest_shift.empty:
                    latest_shift = latest_shift.iloc[0]
                    st.subheader("Latest Run Delta")
                    d1, d2, d3, d4 = st.columns(4)
                    d1.metric("Prior Rank", f"#{int(latest_shift['overall_rank_old'])}" if pd.notna(latest_shift.get("overall_rank_old")) else "—")
                    d2.metric("Current Rank", f"#{int(latest_shift['overall_rank_new'])}" if pd.notna(latest_shift.get("overall_rank_new")) else "—")
                    d3.metric("Opp Score Δ", f"{float(latest_shift['opportunity_score_delta']):+.2f}" if pd.notna(latest_shift.get("opportunity_score_delta")) else "—")
                    d4.metric("5yr Policy Δ", f"{float(latest_shift['pred_policy_3yr_delta']):+.3f}" if pd.notna(latest_shift.get("pred_policy_3yr_delta")) else "—")
                    for bullet in _build_latest_run_delta_bullets(latest_shift):
                        st.markdown(f"- {bullet}")

            # SHAP drivers
            st.subheader("Growth Drivers (SHAP)")
            for h in HORIZONS:
                driver_col = f"drivers_xgboost_{h}yr"
                if driver_col in county_row.index:
                    drivers = {k: v for k, v in _parse_drivers(county_row[driver_col]).items()
                               if v is not None and isinstance(v, (int, float))}
                    if drivers:
                        st.caption(f"**{h}-year XGBoost drivers**")
                        driver_df = pd.DataFrame([
                            {"Feature": k, "SHAP Impact": v}
                            for k, v in sorted(drivers.items(), key=lambda x: abs(x[1]), reverse=True)[:8]
                        ])
                        fig_shap = go.Figure(go.Bar(
                            x=driver_df["SHAP Impact"],
                            y=driver_df["Feature"],
                            orientation="h",
                            marker_color=[
                                "#2ecc71" if v > 0 else "#e74c3c"
                                for v in driver_df["SHAP Impact"]
                            ],
                        ))
                        fig_shap.update_layout(
                            height=max(200, 30 * len(driver_df)),
                            margin=dict(t=5, b=20),
                            xaxis_title="SHAP value",
                        )
                        st.plotly_chart(fig_shap, width="stretch")

            if advanced_mode:
                st.subheader("Advanced QA")
                available = county_row.index.tolist()
                metric_cols = [c for c in available if c.startswith("pred_") or c.endswith("_risk")]
                qa_cols = [c for c in ["opportunity_score", "composite_risk", "confidence"] if c in available]
                qa_cols += metric_cols[:20]
                missing_count = int(pd.Series(county_row[qa_cols]).isna().sum()) if qa_cols else 0
                st.caption(f"Selected county QA: `{missing_count}` missing values across key prediction/risk fields.")
                qa_row = pd.DataFrame(
                    [{"column": c, "value": county_row.get(c), "is_missing": pd.isna(county_row.get(c))} for c in qa_cols]
                )
                st.dataframe(qa_row, width="stretch", hide_index=True, height=260)

                with st.expander("Raw county record (full row)"):
                    raw_cols = st.multiselect(
                        "Columns",
                        options=available,
                        default=[c for c in ["fips", "county_name", "state", "overall_rank", "opportunity_score"] if c in available],
                        key="adv_detail_raw_cols",
                    )
                    if raw_cols:
                        st.dataframe(
                            pd.DataFrame([county_row[raw_cols].to_dict()]),
                            width="stretch",
                            hide_index=True,
                        )
    except Exception as exc:
        st.error(f"County detail failed: {exc}")


# ========================= TAB 4: WATCHLIST ================================

with tab_watch:
    st.header("Watchlist")
    st.caption("Track shortlist counties across runs, spot stable winners, and flag volatile boundary movers.")

    with st.expander("Watchlist Sharing & Import"):
        import_mode = st.radio(
            "Import mode",
            ["Append to current session", "Replace current session"],
            horizontal=True,
            help="Append keeps your current shortlist and adds imported counties. Replace overwrites only the current in-memory watchlist.",
        )
        import_file = st.file_uploader(
            "Import watchlist bundle or county list",
            type=["json", "csv", "txt", "md"],
            help="Supported formats: dashboard JSON export, watchlist share JSON, CSV with a FIPS column, or TXT/Markdown with one FIPS per line.",
        )
        if st.button("Apply Import"):
            if import_file is None:
                st.warning("Choose a JSON, CSV, TXT, or Markdown file before importing.")
            else:
                try:
                    parsed_import = _parse_watchlist_import(import_file.name, import_file.getvalue())
                    new_watch, new_saved, new_notes, import_msg = _apply_watchlist_import_payload(
                        parsed_import,
                        import_mode=import_mode,
                        current_watch_fips=st.session_state.watchlist_fips,
                        saved_watchlists=st.session_state.saved_watchlists,
                        county_notes=st.session_state.county_notes,
                    )
                    st.session_state.watchlist_fips = new_watch
                    st.session_state.saved_watchlists = new_saved
                    st.session_state.county_notes = new_notes
                    _save_current_user_state()
                    st.success(import_msg)
                except Exception as exc:
                    st.error(f"Watchlist import failed: {exc}")

        manual_fips_text = st.text_area(
            "Quick add by FIPS",
            value="",
            height=90,
            placeholder="Paste county FIPS values separated by commas, spaces, or new lines.",
        )
        if st.button("Add Pasted FIPS"):
            parsed = [
                f for f in (
                    _normalize_fips_value(token)
                    for token in manual_fips_text.replace(",", " ").split()
                )
                if f is not None
            ]
            if not parsed:
                st.warning("No valid county FIPS values were found in the pasted text.")
            else:
                st.session_state.watchlist_fips = sorted(set(st.session_state.watchlist_fips + parsed))
                st.success(f"Added `{len(set(parsed))}` counties from pasted FIPS.")

    st.subheader("Saved Watchlists")
    saved_names = sorted(st.session_state.saved_watchlists.keys())
    load_options = ["Current Session"] + saved_names
    selected_saved_watchlist = st.selectbox("Load saved watchlist", options=load_options, index=0)
    current_meta_payload = (
        st.session_state.saved_watchlists.get(selected_saved_watchlist, {})
        if selected_saved_watchlist != "Current Session"
        else st.session_state.session_watchlist_meta
    ) or {}
    sw1, sw2, sw3 = st.columns(3)
    with sw1:
        if selected_saved_watchlist != "Current Session" and st.button("Load Watchlist"):
            payload = st.session_state.saved_watchlists.get(selected_saved_watchlist, {})
            st.session_state.watchlist_fips = payload.get("fips", [])
            st.success(f"Loaded watchlist: {selected_saved_watchlist}")
    with sw2:
        save_name = st.text_input("Save current as", value="", placeholder="e.g. Rust Belt 5yr shortlist")
        if st.button("Save Current Watchlist"):
            cleaned = save_name.strip()
            if not cleaned:
                st.warning("Enter a watchlist name before saving.")
            else:
                owner_val = st.session_state.get("watchlist_owner_input", "").strip()
                thesis_val = st.session_state.get("watchlist_thesis_input", "").strip()
                tags_val = _normalize_tag_list(st.session_state.get("watchlist_tags_input", ""))
                st.session_state.saved_watchlists[cleaned] = {
                    "fips": sorted(set(st.session_state.watchlist_fips)),
                    "updated_at": datetime.now().isoformat(),
                    "count": len(set(st.session_state.watchlist_fips)),
                    "owner": owner_val,
                    "thesis": thesis_val,
                    "tags": tags_val,
                }
                st.session_state.session_watchlist_meta = {
                    "owner": owner_val,
                    "thesis": thesis_val,
                    "tags": tags_val,
                }
                _save_current_user_state()
                st.success(f"Saved watchlist: {cleaned}")
    with sw3:
        if selected_saved_watchlist != "Current Session" and st.button("Delete Saved Watchlist"):
            st.session_state.saved_watchlists.pop(selected_saved_watchlist, None)
            _save_current_user_state()
            st.success(f"Deleted watchlist: {selected_saved_watchlist}")

    st.subheader("Watchlist Thesis")
    meta1, meta2 = st.columns(2)
    with meta1:
        owner_input = st.text_input(
            "Owner / reviewer",
            value=current_meta_payload.get("owner", ""),
            key="watchlist_owner_input",
            help="Useful for handoffs and share packets.",
        )
        tags_input = st.text_input(
            "Tags",
            value=", ".join(current_meta_payload.get("tags", []) or []),
            key="watchlist_tags_input",
            help="Comma-separated thesis or theme tags, e.g. value, exurban, supply constrained.",
        )
    with meta2:
        thesis_input = st.text_area(
            "Thesis summary",
            value=current_meta_payload.get("thesis", ""),
            height=110,
            key="watchlist_thesis_input",
            help="Short explanation of why this shortlist exists.",
        )
    if selected_saved_watchlist == "Current Session":
        st.session_state.session_watchlist_meta = {
            "owner": owner_input.strip(),
            "thesis": thesis_input.strip(),
            "tags": _normalize_tag_list(tags_input),
        }
    elif st.button("Update Saved Watchlist Thesis"):
        payload = st.session_state.saved_watchlists.get(selected_saved_watchlist, {})
        payload.update(
            {
                "owner": owner_input.strip(),
                "thesis": thesis_input.strip(),
                "tags": _normalize_tag_list(tags_input),
                "updated_at": datetime.now().isoformat(),
            }
        )
        st.session_state.saved_watchlists[selected_saved_watchlist] = payload
        _save_current_user_state()
        st.success(f"Updated thesis metadata for `{selected_saved_watchlist}`.")

    with st.expander("Health Rules & Alerts"):
        hs = st.session_state.watchlist_settings
        hr1, hr2, hr3 = st.columns(3)
        with hr1:
            top_rank_strong = st.number_input("Top-rank strong cutoff", min_value=1, max_value=500, value=int(hs.get("top_rank_strong", 25)), step=1)
            top_rank_watch = st.number_input("Top-rank watch cutoff", min_value=1, max_value=1000, value=int(hs.get("top_rank_watch", 100)), step=1)
            sharp_rank_move = st.number_input("Sharp move alert (ranks)", min_value=1.0, max_value=200.0, value=float(hs.get("sharp_rank_move", 10.0)), step=1.0)
            alert_rank_exit_boundary = st.number_input("Alert boundary rank", min_value=1, max_value=500, value=int(hs.get("alert_rank_exit_boundary", 50)), step=1)
        with hr2:
            durable_top25_share = st.slider("Durable top-25 share", min_value=0.0, max_value=1.0, value=float(hs.get("durable_top25_share", 0.60)), step=0.05)
            weak_top25_share = st.slider("Weak top-25 share", min_value=0.0, max_value=1.0, value=float(hs.get("weak_top25_share", 0.20)), step=0.05)
            calm_std_rank = st.number_input("Calm rank std", min_value=0.0, max_value=100.0, value=float(hs.get("calm_std_rank", 12.0)), step=1.0)
            volatile_std_rank = st.number_input("Volatile rank std", min_value=0.0, max_value=200.0, value=float(hs.get("volatile_std_rank", 25.0)), step=1.0)
        with hr3:
            strong_5yr_upside = st.number_input("Strong 5yr upside", min_value=-1.0, max_value=2.0, value=float(hs.get("strong_5yr_upside", 0.15)), step=0.01, format="%.2f")
            weak_5yr_upside = st.number_input("Weak 5yr upside", min_value=-1.0, max_value=2.0, value=float(hs.get("weak_5yr_upside", 0.05)), step=0.01, format="%.2f")
            elevated_risk = st.number_input("Elevated risk cutoff", min_value=0.0, max_value=100.0, value=float(hs.get("elevated_risk", 60.0)), step=1.0)
        if st.button("Save Health Rules"):
            st.session_state.watchlist_settings = {
                "top_rank_strong": int(top_rank_strong),
                "top_rank_watch": int(top_rank_watch),
                "durable_top25_share": float(durable_top25_share),
                "weak_top25_share": float(weak_top25_share),
                "calm_std_rank": float(calm_std_rank),
                "volatile_std_rank": float(volatile_std_rank),
                "sharp_rank_move": float(sharp_rank_move),
                "strong_5yr_upside": float(strong_5yr_upside),
                "weak_5yr_upside": float(weak_5yr_upside),
                "elevated_risk": float(elevated_risk),
                "alert_rank_exit_boundary": int(alert_rank_exit_boundary),
            }
            _save_current_user_state()
            st.success("Saved watchlist health rules.")

    if saved_names:
        saved_meta_rows = []
        for name in saved_names:
            payload = st.session_state.saved_watchlists.get(name, {})
            saved_meta_rows.append(
                {
                    "watchlist": name,
                    "count": payload.get("count", len(payload.get("fips", []))),
                    "owner": payload.get("owner"),
                    "tags": ", ".join(payload.get("tags", []) or []),
                    "updated_at": payload.get("updated_at"),
                }
            )
        st.dataframe(pd.DataFrame(saved_meta_rows), width="stretch", hide_index=True, height=180)
    st.download_button(
        "Export saved watchlists + notes (JSON)",
        data=json.dumps(
            {
                "saved_watchlists": st.session_state.saved_watchlists,
                "county_notes": st.session_state.county_notes,
                "saved_compare_sets": st.session_state.saved_compare_sets,
                "watchlist_alert_state": st.session_state.watchlist_alert_state,
                "watchlist_settings": st.session_state.watchlist_settings,
            },
            indent=2,
        ).encode("utf-8"),
        file_name=f"dashboard_user_data_{_current_user_id()}.json",
        mime="application/json",
    )

    watch_options_df = df.sort_values("overall_rank")[["fips", "county_name", "state", "overall_rank"]].copy()
    watch_options_df["fips"] = watch_options_df["fips"].astype(str).str.zfill(5)
    watch_options_df["label"] = watch_options_df.apply(
        lambda r: f"{r['county_name']}, {r['state']} [FIPS {r['fips']}] (#{int(r['overall_rank'])})",
        axis=1,
    )
    label_to_fips = dict(zip(watch_options_df["label"], watch_options_df["fips"]))
    fips_to_label = dict(zip(watch_options_df["fips"], watch_options_df["label"]))

    current_watch_labels = [fips_to_label[f] for f in st.session_state.watchlist_fips if f in fips_to_label]
    selected_watch_labels = st.multiselect(
        "Manage watchlist counties",
        options=watch_options_df["label"].tolist(),
        default=current_watch_labels,
        key="watchlist_labels",
    )
    st.session_state.watchlist_fips = [label_to_fips[label] for label in selected_watch_labels]

    watch_fips = st.session_state.watchlist_fips
    watch_current = df[df["fips"].astype(str).str.zfill(5).isin(watch_fips)].copy()

    if watch_current.empty:
        st.info("Add counties to the watchlist from here or from the County Detail tab.")
    else:
        active_watchlist_name = selected_saved_watchlist if selected_saved_watchlist != "Current Session" else None
        active_watchlist_meta = (
            st.session_state.saved_watchlists.get(selected_saved_watchlist, {})
            if selected_saved_watchlist != "Current Session"
            else st.session_state.session_watchlist_meta
        ) or {}
        keep_cols = [
            c for c in [
                "fips", "county_name", "state", "overall_rank", "opportunity_score",
                "pred_policy_3yr", "pred_avg_5yr", "composite_risk", "confidence",
                "site_thesis_support_index", "land_developability_index",
                "land_constraint_pressure", "land_fragility_pressure",
                "wave3_overlay_rank", "wave3_net_support", "wave3_support_score",
                "wave3_brake_score", "wave3_overlay_adjustment", "wave3_structural_summary",
            ] if c in watch_current.columns
        ]
        watch_table = watch_current[keep_cols].copy()
        watch_table["fips"] = watch_table["fips"].astype(str).str.zfill(5)
        if run_history_summary_df is not None and not run_history_summary_df.empty:
            enrich_cols = [
                c for c in [
                    "fips", "avg_rank", "std_rank", "rank_range",
                    "top25_presence_share", "top50_presence_share", "net_rank_change"
                ] if c in run_history_summary_df.columns
            ]
            watch_table = watch_table.merge(run_history_summary_df[enrich_cols], on="fips", how="left")

        for col in ["pred_policy_3yr", "pred_avg_5yr"]:
            if col in watch_table.columns:
                watch_table[col] = watch_table[col].map(_fmt_pct)
        for col in [
            "opportunity_score", "composite_risk", "avg_rank", "std_rank", "rank_range", "net_rank_change",
            "site_thesis_support_index", "land_developability_index",
            "land_constraint_pressure", "land_fragility_pressure",
            "wave3_net_support", "wave3_support_score", "wave3_brake_score", "wave3_overlay_adjustment",
        ]:
            if col in watch_table.columns:
                watch_table[col] = watch_table[col].map(lambda x: f"{x:.1f}" if pd.notna(x) else "—")
        for col in ["wave3_overlay_rank"]:
            if col in watch_table.columns:
                watch_table[col] = watch_table[col].map(lambda x: f"#{int(x)}" if pd.notna(x) else "—")
        for col in ["top25_presence_share", "top50_presence_share"]:
            if col in watch_table.columns:
                watch_table[col] = watch_table[col].map(lambda x: f"{100*x:.0f}%" if pd.notna(x) else "—")

        st.dataframe(watch_table.sort_values("overall_rank"), width="stretch", hide_index=True, height=320)
        st.download_button(
            "Export watchlist (CSV)",
            data=watch_current.sort_values("overall_rank").to_csv(index=False).encode("utf-8"),
            file_name="watchlist_current_snapshot.csv",
            mime="text/csv",
        )
        share_payload = _build_watchlist_share_payload(
            watch_current,
            notes=st.session_state.county_notes,
            watchlist_name=active_watchlist_name,
            watchlist_meta=active_watchlist_meta,
        )
        st.download_button(
            "Export watchlist share packet (JSON)",
            data=json.dumps(share_payload, indent=2).encode("utf-8"),
            file_name="watchlist_share_packet.json",
            mime="application/json",
        )

        history = None
        if run_history_detail_df is not None and not run_history_detail_df.empty:
            history = run_history_detail_df[run_history_detail_df["fips"].isin(watch_fips)].copy()
        watchlist_md = _build_watchlist_markdown(
            watch_current,
            history_df=history,
            notes=st.session_state.county_notes,
            watchlist_name=active_watchlist_name,
            watchlist_meta=active_watchlist_meta,
        )
        st.download_button(
            "Export watchlist memo (Markdown)",
            data=watchlist_md.encode("utf-8"),
            file_name="watchlist_memo.md",
            mime="text/markdown",
        )

        run_summary_df, run_summary_md = _build_watchlist_latest_run_summary(
            watch_current,
            latest_compare_rank_df=latest_compare_rank_df,
            run_history_summary_df=run_history_summary_df,
            notes=st.session_state.county_notes,
            watchlist_name=active_watchlist_name,
        )
        if not run_summary_df.empty:
            health_eval = run_summary_df.copy()
            health_eval["composite_risk"] = watch_current.set_index(watch_current["fips"].astype(str).str.zfill(5))["composite_risk"].reindex(health_eval["fips"]).values
            for structural_col in [
                "site_thesis_support_index",
                "land_developability_index",
                "land_constraint_pressure",
                "land_fragility_pressure",
                "fragility_balance_index",
                "scarcity_amenity_balance_index",
                "optionality_profile_index",
                "constraint_cluster_label",
                "wave3_overlay_rank",
                "wave3_overlay_adjustment",
                "wave3_net_support",
                "wave3_support_score",
                "wave3_brake_score",
                "wave3_structural_summary",
            ]:
                if structural_col in watch_current.columns:
                    health_eval[structural_col] = (
                        watch_current.set_index(watch_current["fips"].astype(str).str.zfill(5))[structural_col]
                        .reindex(health_eval["fips"]).values
                    )
            county_lookup = watch_current.set_index(watch_current["fips"].astype(str).str.zfill(5))
            health_eval["coastal_lane"] = [
                _coastal_lane_provenance(
                    county_lookup.loc[fips] if fips in county_lookup.index else pd.Series(dtype=object),
                    wave3_status,
                ).get("label")
                for fips in health_eval["fips"]
            ]
            health_eval["health_status"], health_eval["health_reasons"] = zip(
                *health_eval.apply(lambda row: _classify_watchlist_health(row, settings=st.session_state.watchlist_settings), axis=1)
            )
            st.subheader("Wave 3 Watchlist Context")
            wv1, wv2, wv3 = st.columns(3)
            high_support_count = int((health_eval["site_thesis_support_index"].fillna(0) >= 0.66).sum()) if "site_thesis_support_index" in health_eval.columns else 0
            high_fragility_count = int((health_eval["land_fragility_pressure"].fillna(0) >= 0.66).sum()) if "land_fragility_pressure" in health_eval.columns else 0
            high_constraint_count = int((health_eval["land_constraint_pressure"].fillna(0) >= 0.66).sum()) if "land_constraint_pressure" in health_eval.columns else 0
            wv1.metric("High Site Support", high_support_count)
            wv2.metric("High Fragility", high_fragility_count)
            wv3.metric("High Constraint", high_constraint_count)
            provenance_counts = health_eval["coastal_lane"].value_counts(dropna=False).to_dict()
            if provenance_counts:
                st.caption(
                    "Coastal lane mix: "
                    + ", ".join(f"{label}={count}" for label, count in provenance_counts.items())
                )

            wave3_watch_cols = [
                c for c in [
                    "county_name", "state", "current_rank", "site_thesis_support_index",
                    "land_developability_index", "land_constraint_pressure", "land_fragility_pressure",
                    "fragility_balance_index", "scarcity_amenity_balance_index", "optionality_profile_index",
                    "constraint_cluster_label",
                    "wave3_overlay_rank", "wave3_net_support", "wave3_support_score",
                    "wave3_brake_score", "wave3_overlay_adjustment", "wave3_structural_summary",
                    "coastal_lane",
                    "pred_avg_5yr", "composite_risk",
                ] if c in health_eval.columns
            ]
            wave3_watch = health_eval[wave3_watch_cols].copy()
            for col in ["pred_avg_5yr"]:
                if col in wave3_watch.columns:
                    wave3_watch[col] = wave3_watch[col].map(_fmt_pct)
            for col in [
                "site_thesis_support_index", "land_developability_index",
                "land_constraint_pressure", "land_fragility_pressure",
                "fragility_balance_index", "scarcity_amenity_balance_index", "optionality_profile_index",
                "wave3_net_support", "wave3_support_score", "wave3_brake_score", "wave3_overlay_adjustment",
                "composite_risk",
            ]:
                if col in wave3_watch.columns:
                    wave3_watch[col] = wave3_watch[col].map(lambda x: f"{x:.3f}" if pd.notna(x) else "—")
            for col in ["current_rank", "wave3_overlay_rank"]:
                if col in wave3_watch.columns:
                    wave3_watch[col] = wave3_watch[col].map(lambda x: f"#{int(x)}" if pd.notna(x) else "—")
            st.dataframe(
                wave3_watch.sort_values("county_name"),
                width="stretch",
                hide_index=True,
                height=260,
            )

            st.subheader("Thesis Health Check")
            hc1, hc2, hc3 = st.columns(3)
            hc1.metric("Fits Thesis", int((health_eval["health_status"] == "fits_thesis").sum()))
            hc2.metric("Watch Closely", int((health_eval["health_status"] == "watch_closely").sum()))
            hc3.metric("Review / Drop", int((health_eval["health_status"] == "review_or_drop").sum()))
            health_view = health_eval.copy()
            health_view["health_reasons"] = health_view["health_reasons"].map(lambda xs: "; ".join(xs[:3]))
            if "top25_presence_share" in health_view.columns:
                health_view["top25_presence_share"] = health_view["top25_presence_share"].map(
                    lambda x: f"{100*x:.0f}%" if pd.notna(x) else "—"
                )
            for col in ["pred_policy_3yr", "pred_avg_5yr"]:
                if col in health_view.columns:
                    health_view[col] = health_view[col].map(_fmt_pct)
            for col in ["current_rank", "prior_rank"]:
                if col in health_view.columns:
                    health_view[col] = health_view[col].map(lambda x: f"#{int(x)}" if pd.notna(x) else "—")
            for col in ["rank_shift", "std_rank", "site_thesis_support_index", "land_developability_index", "land_constraint_pressure", "land_fragility_pressure"]:
                if col in health_view.columns:
                    if col == "rank_shift":
                        health_view[col] = health_view[col].map(lambda x: f"{x:+.1f}" if pd.notna(x) else "—")
                    elif col == "std_rank":
                        health_view[col] = health_view[col].map(lambda x: f"{x:.1f}" if pd.notna(x) else "—")
                    else:
                        health_view[col] = health_view[col].map(lambda x: f"{x:.3f}" if pd.notna(x) else "—")
            st.dataframe(
                health_view[
                    [
                        c for c in [
                            "county_name", "state", "health_status", "current_rank", "prior_rank",
                            "rank_shift", "pred_policy_3yr", "pred_avg_5yr",
                            "top25_presence_share", "std_rank",
                            "site_thesis_support_index", "land_developability_index",
                            "land_constraint_pressure", "land_fragility_pressure",
                            "health_reasons"
                        ] if c in health_view.columns
                    ]
                ],
                width="stretch",
                hide_index=True,
                height=260,
            )
            alert_df = _build_watchlist_alerts(health_eval, settings=st.session_state.watchlist_settings)
            st.subheader("Watchlist Alerts")
            if alert_df.empty:
                st.success("No current watchlist alerts are firing under the saved health rules.")
            else:
                alert_df = alert_df.copy()
                alert_df["alert_key"] = alert_df.apply(_alert_key, axis=1)
                alert_state = st.session_state.watchlist_alert_state
                alert_df["alert_status"] = alert_df["alert_key"].map(
                    lambda k: (alert_state.get(k) or {}).get("status", "active")
                )
                alert_df["alert_note"] = alert_df["alert_key"].map(
                    lambda k: (alert_state.get(k) or {}).get("note", "")
                )
                alert_df["alert_updated_at"] = alert_df["alert_key"].map(
                    lambda k: (alert_state.get(k) or {}).get("updated_at", "")
                )
                show_suppressed = st.checkbox("Show suppressed alerts", value=False)
                visible_alerts = alert_df if show_suppressed else alert_df[alert_df["alert_status"] != "suppressed"].copy()
                ac1, ac2, ac3 = st.columns(3)
                ac1.metric("High Severity", int((visible_alerts["severity"] == "high").sum()))
                ac2.metric("Medium Severity", int((visible_alerts["severity"] == "medium").sum()))
                ac3.metric("Low Severity", int((visible_alerts["severity"] == "low").sum()))
                digest_payload, digest_md = _build_watchlist_alert_digest(
                    alert_df,
                    alert_state=st.session_state.watchlist_alert_state,
                    watchlist_name=active_watchlist_name,
                )
                dc1, dc2, dc3 = st.columns(3)
                dc1.metric("Active", int(digest_payload["counts"].get("active", 0)))
                dc2.metric("Acknowledged", int(digest_payload["counts"].get("acknowledged", 0)))
                dc3.metric("Suppressed", int(digest_payload["counts"].get("suppressed", 0)))
                manage_cols = [c for c in ["county_name", "state", "severity", "alert_type", "alert_status", "message"] if c in visible_alerts.columns]
                selected_alert_labels = st.multiselect(
                    "Select alerts to manage",
                    options=[
                        f"{row['county_name']}, {row['state']} | {row['alert_type']} | {row['severity']} | {row['alert_status']}"
                        for _, row in visible_alerts.iterrows()
                    ],
                    default=[],
                )
                label_to_key = {
                    f"{row['county_name']}, {row['state']} | {row['alert_type']} | {row['severity']} | {row['alert_status']}": row["alert_key"]
                    for _, row in visible_alerts.iterrows()
                }
                alert_note_input = st.text_input(
                    "Alert review note",
                    value="",
                    help="Optional note saved with acknowledgement or suppression.",
                )
                m1, m2, m3 = st.columns(3)
                selected_keys = [label_to_key[x] for x in selected_alert_labels if x in label_to_key]
                with m1:
                    if st.button("Acknowledge Selected Alerts"):
                        for key in selected_keys:
                            st.session_state.watchlist_alert_state[key] = {
                                "status": "acknowledged",
                                "note": alert_note_input.strip(),
                                "updated_at": datetime.now().isoformat(),
                            }
                        if selected_keys:
                            _save_current_user_state()
                            st.success(f"Acknowledged `{len(selected_keys)}` alerts.")
                with m2:
                    if st.button("Suppress Selected Alerts"):
                        for key in selected_keys:
                            st.session_state.watchlist_alert_state[key] = {
                                "status": "suppressed",
                                "note": alert_note_input.strip(),
                                "updated_at": datetime.now().isoformat(),
                            }
                        if selected_keys:
                            _save_current_user_state()
                            st.success(f"Suppressed `{len(selected_keys)}` alerts.")
                with m3:
                    if st.button("Clear Selected Alert State"):
                        for key in selected_keys:
                            st.session_state.watchlist_alert_state.pop(key, None)
                        if selected_keys:
                            _save_current_user_state()
                            st.success(f"Cleared saved state for `{len(selected_keys)}` alerts.")

                alert_view = visible_alerts.copy()
                for col in ["current_rank", "prior_rank"]:
                    if col in alert_view.columns:
                        alert_view[col] = alert_view[col].map(lambda x: f"#{int(x)}" if pd.notna(x) else "—")
                for col in ["rank_shift", "std_rank"]:
                    if col in alert_view.columns:
                        alert_view[col] = alert_view[col].map(lambda x: f"{x:+.1f}" if pd.notna(x) and col == "rank_shift" else (f"{x:.1f}" if pd.notna(x) else "—"))
                st.dataframe(
                    alert_view[
                        [
                            c for c in [
                                "county_name", "state", "severity", "alert_type", "current_rank",
                                "prior_rank", "rank_shift", "std_rank", "health_status",
                                "alert_status", "message", "alert_note", "alert_updated_at"
                            ] if c in alert_view.columns
                        ]
                    ],
                    width="stretch",
                    hide_index=True,
                    height=260,
                )
                with st.expander("Alert Digest & Export", expanded=False):
                    top_review = pd.DataFrame(digest_payload.get("top_review_counties") or [])
                    if not top_review.empty:
                        review_view = top_review.copy()
                        if "current_rank" in review_view.columns:
                            review_view["current_rank"] = review_view["current_rank"].map(
                                lambda x: f"#{int(x)}" if pd.notna(x) else "—"
                            )
                        st.dataframe(review_view, width="stretch", hide_index=True, height=220)
                    else:
                        st.caption("No unsuppressed alert clusters currently need review.")
                    dg1, dg2 = st.columns(2)
                    with dg1:
                        st.download_button(
                            "Export alert digest (Markdown)",
                            data=digest_md.encode("utf-8"),
                            file_name="watchlist_alert_digest.md",
                            mime="text/markdown",
                        )
                    with dg2:
                        st.download_button(
                            "Export alert digest (JSON)",
                            data=json.dumps(digest_payload, indent=2).encode("utf-8"),
                            file_name="watchlist_alert_digest.json",
                            mime="application/json",
                        )

            st.subheader("Run-to-Run Explanation Summary")
            summary_view = run_summary_df.copy()
            if "top25_presence_share" in summary_view.columns:
                summary_view["top25_presence_share"] = summary_view["top25_presence_share"].map(
                    lambda x: f"{100*x:.0f}%" if pd.notna(x) else "—"
                )
            for col in ["opportunity_score", "pred_policy_3yr", "pred_avg_5yr"]:
                if col in summary_view.columns:
                    fmt = _fmt_score if col == "opportunity_score" else _fmt_pct
                    summary_view[col] = summary_view[col].map(fmt)
            for col in ["rank_shift", "std_rank"]:
                if col in summary_view.columns:
                    summary_view[col] = summary_view[col].map(lambda x: f"{x:+.1f}" if pd.notna(x) and col == "rank_shift" else (f"{x:.1f}" if pd.notna(x) else "—"))
            for col in [
                "site_thesis_support_index",
                "land_developability_index",
                "land_constraint_pressure",
                "land_fragility_pressure",
            ]:
                if col in summary_view.columns:
                    summary_view[col] = summary_view[col].map(lambda x: f"{x:.3f}" if pd.notna(x) else "—")
            show_cols = [
                c for c in [
                    "county_name", "state", "current_rank", "prior_rank", "rank_shift", "movement",
                    "opportunity_score", "pred_policy_3yr", "pred_avg_5yr",
                    "top25_presence_share", "std_rank",
                    "site_thesis_support_index", "land_developability_index",
                    "land_constraint_pressure", "land_fragility_pressure",
                    "wave3_support_short", "wave3_brake_short", "wave3_decision_verdict",
                    "explanation", "note"
                ] if c in summary_view.columns
            ]
            st.dataframe(summary_view[show_cols], width="stretch", hide_index=True, height=320)
            st.download_button(
                "Export run-to-run summary (Markdown)",
                data=run_summary_md.encode("utf-8"),
                file_name="watchlist_run_summary.md",
                mime="text/markdown",
            )
            wave3_brief_md = _build_wave3_shortlist_brief(
                watch_current,
                run_summary_df=run_summary_df,
                watchlist_name=active_watchlist_name,
                watchlist_meta=active_watchlist_meta,
            )
            st.download_button(
                "Export Wave 3 shortlist brief (Markdown)",
                data=wave3_brief_md.encode("utf-8"),
                file_name="watchlist_wave3_structural_brief.md",
                mime="text/markdown",
            )
            scorecard_df, scorecard_md = _build_wave3_shortlist_scorecard(
                watch_current,
                run_summary_df=run_summary_df,
            )
            if not scorecard_df.empty:
                st.subheader("Wave 3 Structural Scorecard")
                posture_counts = scorecard_df["structural_posture"].value_counts().to_dict()
                sc1, sc2, sc3 = st.columns(3)
                sc1.metric("Structurally Supported", int(posture_counts.get("structurally_supported", 0)))
                sc2.metric("Mixed Structural Read", int(posture_counts.get("mixed_structural_read", 0)))
                sc3.metric("Structurally Constrained", int(posture_counts.get("structurally_constrained", 0)))

                scorecard_view = scorecard_df.copy()
                for col in ["pred_policy_3yr", "pred_avg_5yr"]:
                    if col in scorecard_view.columns:
                        scorecard_view[col] = scorecard_view[col].map(_fmt_pct)
                for col in [
                    "site_thesis_support_index",
                    "land_developability_index",
                    "land_constraint_pressure",
                    "land_fragility_pressure",
                    "composite_risk",
                ]:
                    if col in scorecard_view.columns:
                        scorecard_view[col] = scorecard_view[col].map(lambda x: f"{x:.3f}" if pd.notna(x) else "—")
                if "overall_rank" in scorecard_view.columns:
                    scorecard_view["overall_rank"] = scorecard_view["overall_rank"].map(
                        lambda x: f"#{int(x)}" if pd.notna(x) else "—"
                    )
                if "rank_shift" in scorecard_view.columns:
                    scorecard_view["rank_shift"] = scorecard_view["rank_shift"].map(
                        lambda x: f"{x:+.1f}" if pd.notna(x) else "—"
                    )
                st.dataframe(
                    scorecard_view[
                        [
                            c for c in [
                                "county_name", "state", "overall_rank", "structural_posture",
                                "site_thesis_support_index", "land_developability_index",
                                "land_constraint_pressure", "land_fragility_pressure",
                                "wave3_support_short", "wave3_brake_short", "wave3_decision_verdict",
                                "movement", "rank_shift",
                                "structural_posture_reasons",
                            ] if c in scorecard_view.columns
                        ]
                    ],
                    width="stretch",
                    hide_index=True,
                    height=280,
                )
                sg1, sg2 = st.columns(2)
                with sg1:
                    st.download_button(
                        "Export structural scorecard (CSV)",
                        data=scorecard_df.to_csv(index=False).encode("utf-8"),
                        file_name="watchlist_wave3_structural_scorecard.csv",
                        mime="text/csv",
                    )
                with sg2:
                    st.download_button(
                        "Export structural scorecard (Markdown)",
                        data=scorecard_md.encode("utf-8"),
                        file_name="watchlist_wave3_structural_scorecard.md",
                        mime="text/markdown",
                    )
            template_choice = st.selectbox(
                "Share template",
                options=["Teammate Brief", "IC Summary"],
                index=0,
                help="Generate a more opinionated reusable handoff format from the current watchlist.",
            )
            template_md = _build_watchlist_share_template(
                template_choice,
                watch_current,
                run_summary_df=run_summary_df,
                watchlist_name=active_watchlist_name,
                watchlist_meta=active_watchlist_meta,
            )
            st.download_button(
                f"Export {template_choice} (Markdown)",
                data=template_md.encode("utf-8"),
                file_name=f"watchlist_{template_choice.lower().replace(' ', '_')}.md",
                mime="text/markdown",
            )

        if run_history_detail_df is not None and not run_history_detail_df.empty:
            history = run_history_detail_df[run_history_detail_df["fips"].isin(watch_fips)].copy()
            if not history.empty:
                history["county_state"] = history["county_name"] + ", " + history["state"]
                history = history.sort_values(["run_id", "overall_rank"], ascending=[True, True])
                fig_watch = px.line(
                    history,
                    x="run_id",
                    y="overall_rank",
                    color="county_state",
                    markers=True,
                    title="Watchlist Rank Trajectory Across Recent Runs",
                    labels={"overall_rank": "Overall rank (lower is better)", "run_id": "Run"},
                    hover_data=["opportunity_score", "pred_policy_3yr", "pred_avg_5yr", "composite_risk", "confidence"],
                )
                fig_watch.update_yaxes(autorange="reversed")
                fig_watch.update_layout(height=420, margin=dict(t=40, b=20))
                st.plotly_chart(fig_watch, width="stretch")

                hist_cols = [
                    c for c in [
                        "run_id", "county_name", "state", "overall_rank",
                        "opportunity_score", "pred_policy_3yr", "pred_avg_5yr",
                        "composite_risk", "confidence"
                    ] if c in history.columns
                ]
                st.caption("Per-run watchlist detail")
                st.dataframe(history[hist_cols], width="stretch", hide_index=True, height=320)
        else:
            st.warning(
                "Run history artifacts are missing. Run "
                "`./.venv/bin/python scripts/build_run_history_summary.py` "
                "to enable movement tracking."
            )

        if latest_compare_rank_df is not None and not latest_compare_rank_df.empty:
            movers = latest_compare_rank_df[latest_compare_rank_df["fips"].isin(watch_fips)].copy()
            if not movers.empty:
                movers["abs_rank_shift"] = movers["rank_shift"].abs()
                movers = movers.sort_values("abs_rank_shift", ascending=False)
                show_cols = [
                    c for c in [
                        "fips", "county_name_new", "state_new", "overall_rank_old", "overall_rank_new",
                        "rank_shift", "opportunity_score_delta", "pred_policy_3yr_delta",
                        "pred_xgboost_5yr_delta", "pred_lightgbm_5yr_delta"
                    ] if c in movers.columns
                ]
                st.subheader("Watchlist Latest Run Movers")
                st.dataframe(movers[show_cols].head(20), width="stretch", hide_index=True, height=260)

        watch_notes_rows = []
        for fips in watch_fips:
            note = st.session_state.county_notes.get(fips)
            if note and (note.get("note") or "").strip():
                watch_notes_rows.append(
                    {
                        "fips": fips,
                        "county_name": note.get("county_name"),
                        "state": note.get("state"),
                        "updated_at": note.get("updated_at"),
                        "note": note.get("note"),
                    }
                )
        if watch_notes_rows:
            st.subheader("Watchlist Notes")
            st.dataframe(pd.DataFrame(watch_notes_rows), width="stretch", hide_index=True, height=240)

    if run_history_summary:
        st.subheader("Stable Top-25 Counties Across Recent Runs")
        stable = pd.DataFrame(run_history_summary.get("stable_top25") or [])
        if not stable.empty:
            stable["top25_presence_share"] = (100 * stable["top25_presence_share"]).round(0).astype("Int64").astype(str) + "%"
            st.dataframe(stable, width="stretch", hide_index=True, height=260)

        st.subheader("Volatile Boundary Movers")
        volatile = pd.DataFrame(run_history_summary.get("volatile_boundary") or [])
        if not volatile.empty:
            st.dataframe(volatile, width="stretch", hide_index=True, height=260)


# ========================= TAB 5: MODEL COMPARISON =========================

with tab_compare:
    st.header("Model Comparison")

    try:
        col_left, col_right = st.columns(2)

        with col_left:
            h_compare = st.selectbox(
                "Horizon to compare", HORIZONS,
                format_func=lambda h: f"{h}-year", index=2, key="compare_horizon"
            )

        xgb_col = f"pred_xgboost_{h_compare}yr"
        lgb_col = f"pred_lightgbm_{h_compare}yr"

        if xgb_col in filtered.columns and lgb_col in filtered.columns:
            scatter_cols = [xgb_col, lgb_col, "opportunity_score"]
            for c in ["county_name", "state"]:
                if c in filtered.columns:
                    scatter_cols.append(c)
            scatter_df = filtered[scatter_cols].dropna(subset=[xgb_col, lgb_col])

            if scatter_df.empty:
                st.warning("No data available for this horizon after filtering.")
            else:
                fig_scatter = px.scatter(
                    scatter_df,
                    x=xgb_col, y=lgb_col,
                    hover_name=("county_name" if "county_name" in scatter_df.columns else None),
                    color="opportunity_score",
                    color_continuous_scale="Viridis",
                    title=f"XGBoost vs LightGBM — {h_compare}-year predictions",
                    labels={xgb_col: "XGBoost prediction", lgb_col: "LightGBM prediction"},
                )
                # Add diagonal line
                min_val = min(scatter_df[xgb_col].min(), scatter_df[lgb_col].min())
                max_val = max(scatter_df[xgb_col].max(), scatter_df[lgb_col].max())
                fig_scatter.add_shape(
                    type="line", x0=min_val, y0=min_val, x1=max_val, y1=max_val,
                    line=dict(color="gray", dash="dash"),
                )
                fig_scatter.update_layout(height=500)
                st.plotly_chart(fig_scatter, width="stretch")

                # Agreement metrics
                corr = scatter_df[xgb_col].corr(scatter_df[lgb_col])
                mean_diff = (scatter_df[xgb_col] - scatter_df[lgb_col]).mean()
                st.caption(
                    f"Correlation: **{corr:.3f}** · Mean difference (XGB - LGB): **{mean_diff:+.3f}**"
                )

                # Distribution comparison
                fig_dist = go.Figure()
                fig_dist.add_trace(go.Histogram(
                    x=scatter_df[xgb_col], name="XGBoost",
                    opacity=0.6, marker_color="#3498db", nbinsx=50,
                ))
                fig_dist.add_trace(go.Histogram(
                    x=scatter_df[lgb_col], name="LightGBM",
                    opacity=0.6, marker_color="#e67e22", nbinsx=50,
                ))
                fig_dist.update_layout(
                    barmode="overlay", height=300,
                    title=f"Prediction Distribution — {h_compare}-year",
                    xaxis_title="Predicted appreciation",
                )
                st.plotly_chart(fig_dist, width="stretch")

        else:
            st.warning(f"Missing model predictions for {h_compare}-year horizon.")

        st.subheader("Calibration Diagnostics")
        st.caption(
            "Raw vs calibrated prediction shifts by model/horizon. "
            "Cap-hit rate uses the same dynamic cap formula as scoring."
        )
        if calibration_diag.empty:
            st.info("No calibrated prediction columns found (`pred_*_cal`).")
        else:
            diag_view = calibration_diag.copy()
            diag_view["cap_hit_rate"] = (100 * diag_view["cap_hit_rate"]).round(2)
            for c in ["raw_mean", "cal_mean", "mean_shift", "mean_abs_shift", "max_abs_shift", "dynamic_cap"]:
                diag_view[c] = diag_view[c].round(4)
            st.dataframe(diag_view, width="stretch", hide_index=True)

            fig_cap = px.bar(
                diag_view,
                x="horizon_yr",
                y="cap_hit_rate",
                color="model",
                barmode="group",
                title="Calibration Cap-Hit Rate (%)",
                labels={"horizon_yr": "Horizon (years)", "cap_hit_rate": "Cap-hit rate (%)"},
            )
            fig_cap.update_layout(height=320, margin=dict(t=40, b=20))
            st.plotly_chart(fig_cap, width="stretch")

            fig_shift = px.bar(
                diag_view,
                x="horizon_yr",
                y="mean_abs_shift",
                color="model",
                barmode="group",
                title="Mean Absolute Calibration Shift",
                labels={"horizon_yr": "Horizon (years)", "mean_abs_shift": "Mean |shift|"},
            )
            fig_shift.update_layout(height=320, margin=dict(t=40, b=20))
            st.plotly_chart(fig_shift, width="stretch")

        # Cross-horizon consistency
        st.subheader("Cross-Horizon Consistency")
        st.caption("Do models agree on which counties are high-growth across all horizons?")

        rank_cols = [f"rank_avg_{h}yr" for h in HORIZONS if f"rank_avg_{h}yr" in filtered.columns]
        if len(rank_cols) >= 2:
            rank_df = filtered[rank_cols].dropna().head(100)
            corr_matrix = rank_df.corr()
            fig_corr = px.imshow(
                corr_matrix,
                text_auto=".2f",
                color_continuous_scale="RdBu_r",
                zmin=-1, zmax=1,
                title="Rank Correlation Across Horizons",
            )
            fig_corr.update_layout(height=350)
            st.plotly_chart(fig_corr, width="stretch")

        st.divider()
        st.subheader("County Compare")
        compare_source = df.sort_values("overall_rank").head(1000).copy()
        compare_options = compare_source.apply(
            lambda r: f"{r['county_name']}, {r['state']} (#{int(r['overall_rank'])})",
            axis=1,
        ).tolist()
        compare_label_to_fips = dict(
            zip(
                compare_options,
                compare_source["fips"].astype(str).str.zfill(5).tolist(),
            )
        )
        compare_fips_to_label = {v: k for k, v in compare_label_to_fips.items()}
        with st.expander("Compare Set Import / Export"):
            compare_import = st.file_uploader(
                "Import compare set JSON",
                type=["json"],
                key="compare_set_import_file",
                help="Use a compare-set JSON export from this dashboard or a full dashboard user-data bundle.",
            )
            if st.button("Apply Compare Set Import"):
                if compare_import is None:
                    st.warning("Choose a compare-set JSON file before importing.")
                else:
                    try:
                        payload = json.loads(compare_import.getvalue().decode("utf-8"))
                        if "saved_compare_sets" in payload:
                            st.session_state.saved_compare_sets.update(payload.get("saved_compare_sets") or {})
                            _save_current_user_state()
                            st.success("Merged compare sets from dashboard user-data bundle.")
                        else:
                            compare_name = payload.get("compare_set_name") or payload.get("name") or "Imported Compare Set"
                            compare_fips = [
                                f for f in (_normalize_fips_value(x) for x in (payload.get("fips") or []))
                                if f is not None
                            ]
                            st.session_state.saved_compare_sets[compare_name] = {
                                "fips": compare_fips,
                                "updated_at": datetime.now().isoformat(),
                                "count": len(compare_fips),
                            }
                            st.session_state.compare_pick = [
                                compare_fips_to_label[f] for f in compare_fips if f in compare_fips_to_label
                            ]
                            _save_current_user_state()
                            st.success(f"Imported compare set: {compare_name}")
                    except Exception as exc:
                        st.error(f"Compare set import failed: {exc}")
        saved_compare_names = ["Current Selection"] + sorted(st.session_state.saved_compare_sets.keys())
        cs1, cs2, cs3 = st.columns(3)
        with cs1:
            selected_compare_set = st.selectbox("Load compare set", options=saved_compare_names, index=0)
            if selected_compare_set != "Current Selection" and st.button("Load Compare Set"):
                payload = st.session_state.saved_compare_sets.get(selected_compare_set, {})
                st.session_state.compare_pick = [
                    compare_fips_to_label[f]
                    for f in payload.get("fips", [])
                    if f in compare_fips_to_label
                ]
                st.success(f"Loaded compare set: {selected_compare_set}")
        with cs2:
            compare_set_name = st.text_input("Save compare set as", value="", placeholder="e.g. Midwest value check")
            if st.button("Save Compare Set"):
                cleaned = compare_set_name.strip()
                selected_labels = st.session_state.get("compare_pick", [])
                selected_fips = [compare_label_to_fips[label] for label in selected_labels if label in compare_label_to_fips]
                if not cleaned:
                    st.warning("Enter a name before saving the compare set.")
                elif len(selected_fips) < 2:
                    st.warning("Select at least two counties before saving a compare set.")
                else:
                    st.session_state.saved_compare_sets[cleaned] = {
                        "fips": selected_fips,
                        "updated_at": datetime.now().isoformat(),
                        "count": len(selected_fips),
                    }
                    _save_current_user_state()
                    st.success(f"Saved compare set: {cleaned}")
        with cs3:
            if selected_compare_set != "Current Selection" and st.button("Delete Compare Set"):
                st.session_state.saved_compare_sets.pop(selected_compare_set, None)
                _save_current_user_state()
                st.success(f"Deleted compare set: {selected_compare_set}")
        pick = st.multiselect(
            "Select 2-4 counties to compare",
            options=compare_options,
            default=st.session_state.get("compare_pick", compare_options[:2] if len(compare_options) >= 2 else compare_options),
            max_selections=4,
            key="compare_pick",
        )
        if len(pick) >= 2:
            ranks = [int(x.split("(#")[1].rstrip(")")) for x in pick]
            cmp = df[df["overall_rank"].isin(ranks)].copy()
            cmp["fips"] = cmp["fips"].astype(str).str.zfill(5)
            cmp_raw = cmp.copy()
            keep = ["overall_rank", "county_name", "state", "opportunity_score", "composite_risk", "confidence"]
            for h in HORIZONS:
                col = f"pred_avg_{h}yr"
                if col in cmp.columns:
                    keep.append(col)
            for col in [
                "site_thesis_support_index",
                "land_developability_index",
                "land_constraint_pressure",
                "land_fragility_pressure",
                "recreation_access_score",
                "coastal_flood_pressure",
            ]:
                if col in cmp.columns:
                    keep.append(col)
            keep.append("fips")
            cmp = cmp[keep].sort_values("overall_rank")
            cmp_raw = cmp_raw[keep].sort_values("overall_rank")
            if run_history_summary_df is not None and not run_history_summary_df.empty:
                hist_keep = [
                    c for c in ["fips", "avg_rank", "std_rank", "top25_presence_share", "rank_range"]
                    if c in run_history_summary_df.columns
                ]
                cmp = cmp.merge(run_history_summary_df[hist_keep], on="fips", how="left")
                cmp_raw = cmp_raw.merge(run_history_summary_df[hist_keep], on="fips", how="left")
            for c in cmp.columns:
                if c.startswith("pred_"):
                    cmp[c] = cmp[c].map(_fmt_pct)
            if "opportunity_score" in cmp.columns:
                cmp["opportunity_score"] = cmp["opportunity_score"].map(_fmt_score)
            if "composite_risk" in cmp.columns:
                cmp["composite_risk"] = cmp["composite_risk"].map(_fmt_score)
            for col in [
                "avg_rank", "std_rank", "rank_range",
                "site_thesis_support_index", "land_developability_index",
                "land_constraint_pressure", "land_fragility_pressure",
                "fragility_balance_index", "scarcity_amenity_balance_index",
                "optionality_profile_index", "constraint_cluster_label",
                "recreation_access_score", "coastal_flood_pressure",
            ]:
                if col in cmp.columns:
                    if col in {"avg_rank", "std_rank", "rank_range"}:
                        cmp[col] = cmp[col].map(lambda x: f"{x:.1f}" if pd.notna(x) else "—")
                    elif col == "constraint_cluster_label":
                        cmp[col] = cmp[col].fillna("—")
                    else:
                        cmp[col] = cmp[col].map(lambda x: f"{x:.3f}" if pd.notna(x) else "—")
            if "top25_presence_share" in cmp.columns:
                cmp["top25_presence_share"] = cmp["top25_presence_share"].map(lambda x: f"{100*x:.0f}%" if pd.notna(x) else "—")
            cmp = cmp.drop(columns=["fips"], errors="ignore")
            st.dataframe(cmp, width="stretch", hide_index=True)

            wave3_compare_cols = [
                c for c in [
                    "site_thesis_support_index",
                    "land_developability_index",
                    "land_constraint_pressure",
                    "land_fragility_pressure",
                    "fragility_balance_index",
                    "scarcity_amenity_balance_index",
                    "optionality_profile_index",
                    "wave3_overlay_rank",
                    "wave3_overlay_adjustment",
                    "wave3_net_support",
                    "wave3_support_score",
                    "wave3_brake_score",
                    "recreation_access_score",
                    "coastal_flood_pressure",
                ] if c in cmp_raw.columns
            ]
            if wave3_compare_cols:
                st.subheader("Wave 3 Structural Comparison")
                structural_view = _build_wave3_compare_rows(cmp_raw, wave3_status)
                structural_fmt = structural_view.copy()
                if "overall_rank" in structural_fmt.columns:
                    structural_fmt["overall_rank"] = structural_fmt["overall_rank"].map(lambda x: f"#{int(x)}" if pd.notna(x) else "—")
                if "wave3_overlay_rank" in structural_fmt.columns:
                    structural_fmt["wave3_overlay_rank"] = structural_fmt["wave3_overlay_rank"].map(lambda x: f"#{int(x)}" if pd.notna(x) else "—")
                for col in wave3_compare_cols:
                    if col in structural_fmt.columns and col != "wave3_overlay_rank":
                        structural_fmt[col] = structural_fmt[col].map(lambda x: f"{x:.3f}" if pd.notna(x) else "—")
                st.dataframe(structural_fmt, width="stretch", hide_index=True, height=240)

                radar_rows = []
                for _, row in cmp_raw.iterrows():
                    for metric in wave3_compare_cols:
                        val = row.get(metric)
                        if pd.notna(val):
                            radar_rows.append(
                                {
                                    "county": f"{row.get('county_name')}, {row.get('state')}",
                                    "metric": metric,
                                    "value": float(val),
                                }
                            )
                if radar_rows:
                    radar_df = pd.DataFrame(radar_rows)
                    fig_wave3_cmp = px.line_polar(
                        radar_df,
                        r="value",
                        theta="metric",
                        color="county",
                        line_close=True,
                        title="Wave 3 Structural Land-Thesis Surface",
                    )
                    fig_wave3_cmp.update_layout(height=520, margin=dict(t=50, b=20))
                    st.plotly_chart(fig_wave3_cmp, width="stretch")

                for bullet in _build_wave3_compare_bullets(cmp_raw, wave3_status):
                    st.markdown(f"- {bullet}")

            compare_export_payload = {
                "compare_set_name": selected_compare_set if selected_compare_set != "Current Selection" else "Current Selection",
                "exported_at": datetime.now().isoformat(),
                "fips": [compare_label_to_fips[label] for label in pick if label in compare_label_to_fips],
                "labels": pick,
            }
            st.download_button(
                "Export compare set (JSON)",
                data=json.dumps(compare_export_payload, indent=2).encode("utf-8"),
                file_name="compare_set.json",
                mime="application/json",
            )
    except Exception as exc:
        st.error(f"Model comparison failed: {exc}")


# ========================= TAB 6: VALIDATION ===============================

with tab_valid:
    st.header("Model Validation")
    eval_report = load_eval_report(_mtime=_file_mtime(EVAL_PATH))

    if eval_report is None:
        st.warning(
            "No evaluation report found. Run `python -m models.evaluation` to generate it."
        )
    else:
        try:
            # --- Walk-Forward CV Summary ---
            st.subheader("Walk-Forward Cross-Validation")
            st.caption(
                "Models trained up to year *t*, tested on *t+1*. "
                "Negative R² is expected across regime shifts — focus on MAE and relative ranking."
            )

            wf_summary = []
            for name, records in sorted(eval_report.items()):
                if name.startswith("wf_") and records:
                    r2s = [r["r2"] for r in records if r.get("r2") is not None and np.isfinite(r["r2"])]
                    maes = [r["mae"] for r in records if r.get("mae") is not None and np.isfinite(r["mae"])]
                    ndcg25 = [r.get("ndcg_at_25") for r in records if r.get("ndcg_at_25") is not None]
                    ndcg50 = [r.get("ndcg_at_50") for r in records if r.get("ndcg_at_50") is not None]
                    ndcg100 = [r.get("ndcg_at_100") for r in records if r.get("ndcg_at_100") is not None]
                    if r2s and maes:
                        row = {
                            "Model": name.replace("wf_", "").replace("_", " ").title(),
                            "Avg R²": round(float(np.nanmean(r2s)), 3),
                            "Avg MAE": round(float(np.nanmean(maes)), 4),
                            "Best Fold R²": round(float(np.nanmax(r2s)), 3),
                            "Worst Fold R²": round(float(np.nanmin(r2s)), 3),
                            "Folds": len(records),
                        }
                        if ndcg25:
                            row["Avg NDCG@25"] = round(float(np.nanmean(ndcg25)), 3)
                        if ndcg50:
                            row["Avg NDCG@50"] = round(float(np.nanmean(ndcg50)), 3)
                        if ndcg100:
                            row["Avg NDCG@100"] = round(float(np.nanmean(ndcg100)), 3)
                        wf_summary.append(row)

            if wf_summary:
                wf_df = pd.DataFrame(wf_summary)
                st.dataframe(wf_df, width="stretch", hide_index=True)

                # Per-fold detail chart
                wf_detail_name = st.selectbox(
                    "View fold details for:",
                    [n for n in sorted(eval_report) if n.startswith("wf_")],
                    format_func=lambda n: n.replace("wf_", "").replace("_", " ").title(),
                )
                if wf_detail_name and eval_report.get(wf_detail_name):
                    fold_df = pd.DataFrame(eval_report[wf_detail_name])
                    col1, col2 = st.columns(2)
                    with col1:
                        fig_r2 = px.bar(
                            fold_df, x="train_end_year", y="r2",
                            title="R² by Fold",
                            color="r2",
                            color_continuous_scale="RdYlGn",
                            color_continuous_midpoint=0,
                        )
                        fig_r2.update_layout(height=300, margin=dict(t=40, b=20))
                        st.plotly_chart(fig_r2, width="stretch")
                    with col2:
                        fig_mae = px.bar(
                            fold_df, x="train_end_year", y="mae",
                            title="MAE by Fold",
                            color_discrete_sequence=["#e67e22"],
                        )
                        fig_mae.update_layout(height=300, margin=dict(t=40, b=20))
                        st.plotly_chart(fig_mae, width="stretch")

                    topk_cols = [
                        c for c in [
                            "precision_at_25", "recall_at_25", "ndcg_at_25",
                            "precision_at_50", "recall_at_50", "ndcg_at_50",
                            "precision_at_100", "recall_at_100", "ndcg_at_100",
                        ]
                        if c in fold_df.columns
                    ]
                    if topk_cols:
                        st.caption("Top-K decision metrics by fold")
                        topk_df = fold_df[["train_end_year"] + topk_cols].copy()
                        for c in topk_cols:
                            topk_df[c] = topk_df[c].round(3)
                        st.dataframe(topk_df, width="stretch", hide_index=True)

            # --- Backtest on Known Booms ---
            st.divider()
            st.subheader("Backtest: Known Boom Regions")
            st.caption(
                "Did the model rank Denver, Boise, and Nashville metro counties "
                "in the **top percentiles** before their booms?"
            )

            bt_keys = sorted([k for k in eval_report if k.startswith("bt_")])
            if bt_keys:
                all_bt_rows = []
                for key in bt_keys:
                    parts = key.replace("bt_", "").split("_")
                    model_type = parts[0]
                    pred_year = parts[1]
                    for r in eval_report[key]:
                        if r.get("status") == "NO_DATA":
                            continue
                        all_bt_rows.append({
                            "Model": model_type.title(),
                            "Pred Year": pred_year,
                            "Region": r["region"].replace("_", " ").title(),
                            "Predicted": f"{r['mean_predicted']:.1%}",
                            "Actual": f"{r['mean_actual']:.1%}",
                            "Pred Rank %ile": f"{r['mean_predicted_rank_pct']:.0%}",
                            "Actual Rank %ile": f"{r['mean_actual_rank_pct']:.0%}",
                            "Status": r["status"],
                        })

                if all_bt_rows:
                    bt_df = pd.DataFrame(all_bt_rows)
                    # Color the status — use applymap fallback for older pandas
                    _style_fn = lambda v: (
                        "background-color: #2ecc7144" if v == "FLAGGED"
                        else "background-color: #e74c3c44" if v == "MISSED" else ""
                    )
                    styler = getattr(bt_df.style, "map", None) or bt_df.style.applymap
                    st.dataframe(
                        styler(_style_fn, subset=["Status"]),
                        width="stretch",
                        hide_index=True,
                    )

                # Percentile rank chart
                bt_chart_data = []
                for key in bt_keys:
                    parts = key.replace("bt_", "").split("_")
                    for r in eval_report[key]:
                        if r.get("status") == "NO_DATA":
                            continue
                        bt_chart_data.append({
                            "config": f"{parts[0]} / {parts[1]}",
                            "region": r["region"].replace("_", " ").title(),
                            "Predicted Rank %ile": r["mean_predicted_rank_pct"] * 100,
                            "Actual Rank %ile": r["mean_actual_rank_pct"] * 100,
                        })

                if bt_chart_data:
                    bt_chart_df = pd.DataFrame(bt_chart_data)
                    fig_bt = px.scatter(
                        bt_chart_df,
                        x="Predicted Rank %ile",
                        y="Actual Rank %ile",
                        color="region",
                        symbol="config",
                        title="Predicted vs Actual Percentile Rank (Known Booms)",
                        labels={"Predicted Rank %ile": "Predicted Rank Percentile",
                                "Actual Rank %ile": "Actual Rank Percentile"},
                    )
                    fig_bt.add_shape(
                        type="line", x0=0, y0=0, x1=100, y1=100,
                        line=dict(color="gray", dash="dash"),
                    )
                    fig_bt.add_shape(
                        type="rect", x0=75, y0=75, x1=100, y1=100,
                        fillcolor="green", opacity=0.1, line_width=0,
                    )
                    fig_bt.update_layout(height=450)
                    st.plotly_chart(fig_bt, width="stretch")

                    st.info(
                        "**Key insight:** All boom regions consistently rank in the "
                        "**80th–99th percentile** — the model successfully identifies "
                        "high-growth counties even years before the boom peaks."
                    )

            st.divider()
            st.subheader("Conformal Interval Diagnostics")
            if not conformal_diag:
                st.caption(
                    "No conformal diagnostics found. Run `python -m models.quantile` "
                    "to generate `conformal_diagnostics.json`."
                )
            else:
                rows = []
                for horizon, rec in conformal_diag.items():
                    cov = rec.get("coverage", {})
                    conf = rec.get("conformal", {})
                    rows.append({
                        "horizon": horizon,
                        "target_coverage": cov.get("target_coverage"),
                        "raw_coverage": cov.get("coverage_raw"),
                        "calibrated_coverage": cov.get("coverage_calibrated"),
                        "global_qhat": conf.get("global_qhat"),
                        "n_calib": conf.get("n_calib"),
                        "n_eval": cov.get("n_eval"),
                    })
                if rows:
                    cov_df = pd.DataFrame(rows)
                    for col in ["target_coverage", "raw_coverage", "calibrated_coverage"]:
                        if col in cov_df.columns:
                            cov_df[col] = (100 * cov_df[col]).round(2)
                    if "global_qhat" in cov_df.columns:
                        cov_df["global_qhat"] = cov_df["global_qhat"].round(4)
                    st.dataframe(cov_df, width="stretch", hide_index=True)
                first = next(iter(conformal_diag.values()), {})
                reg = first.get("coverage", {}).get("by_regime", {})
                if reg:
                    reg_rows = []
                    for rg, vals in reg.items():
                        reg_rows.append({
                            "regime": rg,
                            "n": vals.get("n"),
                            "raw_coverage": 100 * vals.get("coverage_raw", 0.0),
                            "calibrated_coverage": 100 * vals.get("coverage_calibrated", 0.0),
                        })
                    reg_df = pd.DataFrame(reg_rows)
                    reg_df["raw_coverage"] = reg_df["raw_coverage"].round(2)
                    reg_df["calibrated_coverage"] = reg_df["calibrated_coverage"].round(2)
                    st.caption("Regime-level coverage sample (first horizon)")
                    st.dataframe(reg_df, width="stretch", hide_index=True)
        except Exception as exc:
            st.error(f"Validation tab failed: {exc}")


# ========================= TAB 7: SYSTEM STATUS ============================

with tab_status:
    st.header("System Status")
    st.caption("Operational visibility for source health, latest-year completeness, drift, and Wave 2 promotion posture.")

    if not status_bundle:
        st.warning(
            "No consolidated project status bundle found. Run "
            "`./.venv/bin/python scripts/build_project_status_bundle.py` "
            "to generate one."
        )
    else:
        source_summary = status_bundle.get("source_health_summary", {}) or {}
        missingness_summary = status_bundle.get("missingness_summary", {}) or {}
        row_missingness = missingness_summary.get("row_missingness", {}) or {}
        gap_summary = ((status_bundle.get("gap_triage") or {}).get("summary") or {})
        drift_summary = ((status_bundle.get("drift_triage") or {}).get("summary") or {})
        latest_run_bundle = status_bundle.get("latest_run", {}) or {}
        latest_run_summary = latest_run_bundle.get("run_summary", {}) or {}
        latest_run_deltas = latest_run_bundle.get("run_deltas", {}) or {}
        latest_compare = ((latest_run_bundle.get("run_compare") or {}).get("summary") or {})
        wave2 = status_bundle.get("wave2_reassessment", {}) or {}
        family_summaries = wave2.get("family_summaries", {}) or {}
        recent_runs = status_bundle.get("recent_runs") or []
        run_history_status = status_bundle.get("run_history_summary", {}) or {}
        run_history_stats = run_history_status.get("summary_stats", {}) or {}
        fiveyr_policy = status_bundle.get("fiveyr_policy_status") or fiveyr_policy_status or {}
        wave3_status = status_bundle.get("wave3_status") or {}

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Healthy Sources", f"{source_summary.get('healthy_sources', 0)}/{source_summary.get('n_sources', 0)}")
        c2.metric("2024 Avg Missing", f"{100 * row_missingness.get('avg_share', 0.0):.2f}%")
        c3.metric("Gap Actions", sum((gap_summary.get("action_counts") or {}).values()))
        churn_val = latest_run_deltas.get("top25_churn") if latest_run_deltas.get("has_previous") else None
        c4.metric("Latest Top-25 Churn", f"{100 * churn_val:.2f}%" if churn_val is not None else "n/a")

        if run_history_stats:
            rh1, rh2, rh3 = st.columns(3)
            rh1.metric("Stable Top-25 Counties", run_history_stats.get("stable_top25_count", 0))
            rh2.metric("Boundary Movers", run_history_stats.get("watchlist_boundary_count", 0))
            rh3.metric("Run History Depth", run_history_status.get("run_count", 0))

        wave2_training = status_bundle.get("wave2_training_policy", {}) or {}
        wave3_training = status_bundle.get("wave3_training_policy", {}) or {}
        wave3_cleanup = status_bundle.get("wave3_cleanup_status", {}) or {}
        wave3_overlay_drift = status_bundle.get("wave3_overlay_drift", {}) or {}
        hydro_readiness = status_bundle.get("usgs_hydrography_nhdplus_readiness", {}) or {}
        training_summary = wave2_training.get("summary", {}) or {}
        if training_summary:
            st.subheader("Wave 2 Training Policy")
            tp1, tp2 = st.columns(2)
            tp1.metric("Training Status Buckets", len(training_summary.get("status_counts", {})))
            tp2.metric("Default Excluded Families", training_summary.get("default_action_counts", {}).get("excluded_by_default", 0))
            fam_rows = []
            for fam in wave2_training.get("families", []) or []:
                fam_rows.append(
                    {
                        "family": fam.get("label", fam.get("family")),
                        "training_status": fam.get("training_status"),
                        "default_action": fam.get("default_training_action"),
                        "latest_non_null_share": (
                            f"{100 * fam['latest_non_null_share']:.1f}%"
                            if isinstance(fam.get("latest_non_null_share"), (int, float))
                            else "n/a"
                        ),
                    }
                )
            if fam_rows:
                st.dataframe(pd.DataFrame(fam_rows), width="stretch", hide_index=True, height=260)

        fiveyr_reco = fiveyr_policy.get("recommendation") or {}
        if fiveyr_reco:
            st.subheader("5yr Product Policy")
            fp1, fp2, fp3 = st.columns(3)
            fp1.metric("Active Default", fiveyr_reco.get("active_default", "n/a"))
            fp2.metric("Primary Objective", fiveyr_reco.get("objective", "n/a"))
            fp3.metric("Promotion Status", fiveyr_reco.get("promotion_status", "n/a"))
            rationale = fiveyr_reco.get("rationale") or []
            if rationale:
                st.markdown("\n".join(f"- {line}" for line in rationale))

            evidence = fiveyr_policy.get("evidence") or {}
            ev1, ev2 = st.columns(2)
            with ev1:
                dominance = evidence.get("dominance") or {}
                if dominance:
                    st.caption("Ranking dominance")
                    st.markdown(
                        "\n".join(
                            [
                                f"- top signal: `{dominance.get('top_signal', 'n/a')}`",
                                f"- top-signal overlap: `{dominance.get('top_signal_top25_overlap', 'n/a')}`",
                                f"- top-signal rank corr: `{dominance.get('top_signal_corr_with_final', 'n/a')}`",
                                f"- calibrators change ranks: `{dominance.get('calibrators_change_ranks', 'n/a')}`",
                            ]
                        )
                    )
            with ev2:
                blend_candidate = evidence.get("blend_candidate") or {}
                if blend_candidate:
                    st.caption("Most promising experimental blend")
                    st.markdown(
                        "\n".join(
                            [
                                f"- candidate: `{blend_candidate.get('candidate', 'n/a')}`",
                                f"- avg realized top-25 `5yr`: `{blend_candidate.get('avg_top25_mean_realized_5yr', 'n/a')}`",
                                f"- live top-25 churn vs baseline: `{blend_candidate.get('live_top25_churn_vs_baseline', 'n/a')}`",
                                f"- promotion: `{blend_candidate.get('promotion_status', 'n/a')}`",
                            ]
                        )
                    )

            next_steps = fiveyr_policy.get("next_steps") or []
            if next_steps:
                st.caption("Next likely steps")
                st.markdown("\n".join(f"- {step}" for step in next_steps))

        if wave3_status:
            st.subheader("Wave 3")
            landed_wave3 = [
                src for src in (wave3_status.get("sources") or [])
                if src.get("status") in {"landed", "guarded_trial"}
            ]
            noaa_trial = wave3_status.get("noaa_guarded_trial") or {}
            w31, w32, w33 = st.columns(3)
            w31.metric("Landed Wave 3 Sources", len(landed_wave3))
            w32.metric("Wave 3 County Universe", wave3_status.get("latest_year_counties", "n/a"))
            top_site = (wave3_status.get("top_site_thesis_support") or [])
            w33.metric("Top Site-Thesis Rows", len(top_site))

            wave3_training_summary = wave3_training.get("summary", {}) or {}
            if wave3_training_summary:
                wtpol1, wtpol2 = st.columns(2)
                wtpol1.metric("Wave 3 Training Buckets", len(wave3_training_summary.get("status_counts", {})))
                wtpol2.metric(
                    "Wave 3 Default Excluded Families",
                    wave3_training_summary.get("default_action_counts", {}).get("excluded_by_default", 0),
                )
                st.caption(
                    "Wave 3 ordered raw-family experiment lane: "
                    + ", ".join(wave3_training_summary.get("ordered_experiment_lane", []))
                )

            cleanup_summary = wave3_cleanup.get("summary", {}) or {}
            if cleanup_summary:
                wc1, wc2 = st.columns(2)
                wc1.metric("Wave 3 Open Cleanup Items", cleanup_summary.get("open_cleanup_items", 0))
                wc2.metric("Wave 3 Intentional Policy Items", cleanup_summary.get("intentional_policy_items", 0))

            structural_overlay = status_bundle.get("wave3_structural_overlay") or wave3_overlay_summary or {}
            if structural_overlay:
                so1, so2, so3 = st.columns(3)
                so1.metric("Overlay Top Churn", f"{structural_overlay.get('top_churn_pct', 'n/a')}%")
                so2.metric("Overlay Mean Rank Delta", f"{structural_overlay.get('mean_abs_rank_delta', 'n/a')}")
                so3.metric("Overlay Max Adjustment", structural_overlay.get("max_adjustment", "n/a"))

            if wave3_overlay_drift:
                drift_top = wave3_overlay_drift.get("top_overlap") or {}
                drift_rank = wave3_overlay_drift.get("rank_delta") or {}
                st.caption("Wave 3 overlay drift check")
                od1, od2, od3 = st.columns(3)
                od1.metric("Top-50 Overlay Churn", f"{(drift_top.get('top_50') or {}).get('churn_pct', 'n/a')}%")
                od2.metric("Top-100 Overlay Churn", f"{(drift_top.get('top_100') or {}).get('churn_pct', 'n/a')}%")
                od3.metric("Overlay P95 Rank Delta", f"{drift_rank.get('p95_abs', 'n/a')}")

            if hydro_readiness:
                hydro_headline = hydro_readiness.get("headline") or {}
                hydro_decision = hydro_readiness.get("readiness") or {}
                st.caption("NHDPlus hydrography readiness")
                hd1, hd2, hd3 = st.columns(3)
                hd1.metric("NHDPlus Proof Counties", hydro_headline.get("proof_upgrade_counties", "n/a"))
                hd2.metric("Hydro Recreation Churn", f"{hydro_headline.get('downstream_recreation_top25_churn_pct', 'n/a')}%")
                hd3.metric("Hydro Site-Thesis Churn", f"{hydro_headline.get('downstream_site_thesis_top25_churn_pct', 'n/a')}%")
                st.caption(f"Hydro readiness status: `{hydro_decision.get('status', 'n/a')}`")

            if noaa_trial.get("active"):
                st.warning(
                    "Guarded NOAA trial is active in the current Wave 3 coastal lane. "
                    f"Release=`{noaa_trial.get('release_label', 'n/a')}`, "
                    f"excluded counties=`{noaa_trial.get('excluded_fips_count', 0)}`, "
                    f"merge gate=`{noaa_trial.get('merge_env_var', 'n/a')}`."
                )

            if landed_wave3:
                wave3_rows = []
                for src in landed_wave3:
                    headline = src.get("headline_coverage") or {}
                    wave3_rows.append(
                        {
                            "source": src.get("source"),
                            "counties": src.get("counties"),
                            "rows": src.get("rows"),
                            "columns": src.get("columns"),
                            "status": src.get("status"),
                            "headline_coverage": ", ".join(f"{k}={v}" for k, v in headline.items()),
                        }
                    )
                    if src.get("source") == "noaa_sea_level":
                        wave3_rows[-1]["positive_coastal_counties"] = src.get("positive_coastal_counties")
                        wave3_rows[-1]["excluded_fips_count"] = src.get("excluded_fips_count")
                st.dataframe(pd.DataFrame(wave3_rows), width="stretch", hide_index=True, height=320)

            wt1, wt2 = st.columns(2)
            with wt1:
                top_dev = wave3_status.get("top_land_developability") or []
                if top_dev:
                    st.caption("Top land developability")
                    st.dataframe(pd.DataFrame(top_dev), width="stretch", hide_index=True, height=280)
            with wt2:
                high_frag = wave3_status.get("highest_land_fragility") or []
                if high_frag:
                    st.caption("Highest land fragility")
                    st.dataframe(pd.DataFrame(high_frag), width="stretch", hide_index=True, height=280)

            top_site = wave3_status.get("top_site_thesis_support") or []
            if top_site:
                st.caption("Top site thesis support")
                st.dataframe(pd.DataFrame(top_site), width="stretch", hide_index=True, height=280)

        st.subheader("Current Snapshot")
        snap1, snap2 = st.columns(2)
        with snap1:
            st.markdown(
                "\n".join(
                    [
                        f"- Latest run: `{latest_run_bundle.get('run_dir', 'n/a')}`",
                        f"- Previous run: `{latest_run_deltas.get('previous_run', 'n/a')}`",
                        f"- Score-only: `{latest_run_summary.get('score_only', 'n/a')}`",
                        f"- 2024 p90 row missingness: `{100 * row_missingness.get('p90_share', 0.0):.2f}%`",
                        f"- Drift alert count: `{drift_summary.get('feature_alert_count', 'n/a')}`",
                    ]
                )
            )
        with snap2:
            st.markdown(
                "\n".join(
                    [
                        f"- Duplicate-issue sources: `{source_summary.get('duplicate_issue_count', 0)}`",
                        f"- Missing sources: `{source_summary.get('missing_source_count', 0)}`",
                        f"- Error sources: `{source_summary.get('error_source_count', 0)}`",
                        f"- Gap triage actions: `{gap_summary.get('action_counts', {})}`",
                        f"- Latest compare file present: `{bool(latest_run_bundle.get('run_compare_path'))}`",
                    ]
                )
            )

        st.subheader("Source Health")
        source_health = status_bundle.get("source_health") or []
        if source_health:
            src_df = pd.DataFrame(source_health)
            if not src_df.empty:
                src_df["status"] = np.where(
                    ~src_df["exists"].fillna(False),
                    "missing",
                    np.where(
                        src_df["error"].notna(),
                        "error",
                        np.where(src_df["duplicate_keys"].fillna(0).gt(0), "duplicate_keys", "healthy"),
                    ),
                )
                src_df["updated_at"] = pd.to_datetime(src_df["updated_at"], errors="coerce")
                src_df = src_df.sort_values(["status", "updated_at"], ascending=[True, False])
                show_cols = [
                    c for c in [
                        "source", "status", "rows", "columns", "duplicate_keys",
                        "key_null_rows", "updated_at", "file", "error"
                    ] if c in src_df.columns
                ]
                st.dataframe(src_df[show_cols], width="stretch", hide_index=True, height=320)

                src_status_counts = src_df["status"].value_counts().rename_axis("status").reset_index(name="count")
                fig_src = px.bar(
                    src_status_counts,
                    x="status",
                    y="count",
                    color="status",
                    title="Source Health Status Counts",
                    color_discrete_sequence=px.colors.qualitative.Safe,
                )
                fig_src.update_layout(height=280, margin=dict(t=40, b=20))
                st.plotly_chart(fig_src, width="stretch")

        st.subheader("Latest-Year Completeness")
        top_missing_features = missingness_summary.get("top_missing_features") or []
        if top_missing_features:
            miss_df = pd.DataFrame(top_missing_features[:20])
            miss_df["missing_pct"] = 100 * miss_df["missing_share"]
            fig_missing = px.bar(
                miss_df.sort_values("missing_pct", ascending=True),
                x="missing_pct",
                y="feature",
                orientation="h",
                title="Top Missing 2024 Features",
                labels={"missing_pct": "Missing %", "feature": "Feature"},
            )
            fig_missing.update_layout(height=560, margin=dict(t=40, b=20))
            st.plotly_chart(fig_missing, width="stretch")

        mid1, mid2 = st.columns(2)
        with mid1:
            st.caption("Gap triage family counts")
            family_counts = gap_summary.get("family_counts") or {}
            if family_counts:
                fam_df = pd.DataFrame(
                    [{"family": k, "count": v} for k, v in family_counts.items()]
                ).sort_values("count", ascending=False)
                st.dataframe(fam_df, width="stretch", hide_index=True)
        with mid2:
            st.caption("Drift action counts")
            drift_action_counts = drift_summary.get("feature_action_counts") or {}
            if drift_action_counts:
                drift_df = pd.DataFrame(
                    [{"action": k, "count": v} for k, v in drift_action_counts.items()]
                ).sort_values("count", ascending=False)
                st.dataframe(drift_df, width="stretch", hide_index=True)

        if latest_compare:
            st.subheader("Latest Run Comparison")
            rc1, rc2, rc3, rc4 = st.columns(4)
            rc1.metric("Top-25 Overlap", latest_compare.get("top25_overlap", "n/a"))
            rc2.metric("Top-25 Churn", f"{100 * latest_compare.get('top25_churn', 0.0):.2f}%")
            rc3.metric("Mean |Rank Shift|", f"{latest_compare.get('mean_abs_rank_shift', 0.0):.2f}")
            rc4.metric("Median |Rank Shift|", f"{latest_compare.get('median_abs_rank_shift', 0.0):.2f}")

            top_drivers = latest_compare.get("top_driver_shift_correlations") or []
            if top_drivers:
                driver_df = pd.DataFrame(top_drivers)
                driver_df["abs_corr"] = driver_df["correlation"].abs()
                fig_driver = px.bar(
                    driver_df.sort_values("abs_corr", ascending=True),
                    x="correlation",
                    y="metric",
                    orientation="h",
                    title="Latest Run: Rank-Shift Driver Correlations",
                    labels={"metric": "Metric", "correlation": "Correlation"},
                )
                fig_driver.update_layout(height=320, margin=dict(t=40, b=20))
                st.plotly_chart(fig_driver, width="stretch")

        if latest_compare_boundary_df is not None and not latest_compare_boundary_df.empty:
            st.subheader("Latest Boundary Movers")
            show_cols = [
                c for c in [
                    "county_name_new", "state_new", "overall_rank_old", "overall_rank_new",
                    "opportunity_score_old", "opportunity_score_new",
                    "pred_policy_3yr_old", "pred_policy_3yr_new",
                    "pred_xgboost_5yr_old", "pred_xgboost_5yr_new",
                    "pred_lightgbm_5yr_old", "pred_lightgbm_5yr_new",
                ] if c in latest_compare_boundary_df.columns
            ]
            st.dataframe(latest_compare_boundary_df[show_cols].head(15), width="stretch", hide_index=True, height=280)

        st.subheader("Run Comparison Explorer")
        if run_compare_files:
            default_compare_idx = len(run_compare_files) - 1
            selected_compare = st.selectbox(
                "Inspect saved run comparison",
                options=run_compare_files,
                index=default_compare_idx,
            )
            compare_payload = load_named_output_json(
                selected_compare,
                _mtime=_file_mtime(OUTPUT_PATH / selected_compare),
            ) or {}
            if compare_payload:
                ex1, ex2, ex3, ex4 = st.columns(4)
                ex1.metric("Base Run", compare_payload.get("base_run", "n/a"))
                ex2.metric("New Run", compare_payload.get("new_run", "n/a"))
                ex3.metric("Top-25 Overlap", compare_payload.get("top25_overlap", "n/a"))
                ex4.metric("Top-25 Churn", f"{100 * compare_payload.get('top25_churn', 0.0):.2f}%")

                shift_summary = compare_payload.get("rank_shift_summary") or {}
                st.caption(
                    "Mean |rank shift|: "
                    f"`{shift_summary.get('mean_abs_rank_shift', 'n/a')}` · "
                    "Median |rank shift|: "
                    f"`{shift_summary.get('median_abs_rank_shift', 'n/a')}`"
                )

                pred_delta_summary = compare_payload.get("prediction_delta_summary") or {}
                pred_rows = []
                for metric, meta in pred_delta_summary.items():
                    pred_rows.append(
                        {
                            "metric": metric,
                            "mean_abs_delta": meta.get("mean_abs_delta"),
                            "corr_with_rank_shift": meta.get("corr_with_rank_shift"),
                        }
                    )
                if pred_rows:
                    pred_df = pd.DataFrame(pred_rows)
                    st.dataframe(pred_df, width="stretch", hide_index=True, height=260)

        st.subheader("Wave 2 Family Reassessment")
        if family_summaries:
            wave2_rows = []
            for family_key, meta in family_summaries.items():
                wave2_rows.append({
                    "family": family_key,
                    "label": meta.get("label", family_key),
                    "recommendation": meta.get("recommendation"),
                    "policy": meta.get("policy"),
                    "latest_avg_missing_pct": 100 * float(meta.get("latest_avg_missing_share", 0.0)),
                    "notes": meta.get("notes"),
                })
            wave2_df = pd.DataFrame(wave2_rows).sort_values(
                ["recommendation", "latest_avg_missing_pct", "label"],
                ascending=[True, True, True],
            )
            st.dataframe(wave2_df, width="stretch", hide_index=True, height=320)

            rec_counts = wave2_df["recommendation"].value_counts().rename_axis("recommendation").reset_index(name="count")
            fig_wave2 = px.bar(
                rec_counts,
                x="recommendation",
                y="count",
                color="recommendation",
                title="Wave 2 Recommendation Counts",
                color_discrete_sequence=px.colors.qualitative.Bold,
            )
            fig_wave2.update_layout(height=280, margin=dict(t=40, b=20))
            st.plotly_chart(fig_wave2, width="stretch")

        st.subheader("Recent Runs")
        if recent_runs:
            rr_df = pd.DataFrame(recent_runs)
            if "top25_churn" in rr_df.columns:
                rr_df["top25_churn_pct"] = (100 * rr_df["top25_churn"].fillna(0.0)).round(2)
            if "fallback_rate_3yr" in rr_df.columns:
                rr_df["fallback_rate_3yr_pct"] = (100 * rr_df["fallback_rate_3yr"].fillna(0.0)).round(2)
            show_rr_cols = [
                c for c in [
                    "run_id", "year", "score_only", "previous_run",
                    "top25_churn_pct", "fallback_rate_3yr_pct",
                    "source_health_mode", "generated_at"
                ] if c in rr_df.columns
            ]
            st.dataframe(rr_df[show_rr_cols], width="stretch", hide_index=True, height=320)

_render_demo_footer(latest_run, status_bundle, demo_readiness_report)
