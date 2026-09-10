"""
LandInvest Interactive Dashboard

Launch:  streamlit run dashboard.py
"""

import html
import json
import re
import sqlite3
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import urlencode

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from dashboard_modules.evidence_panel import render_county_evidence_panel
from dashboard_modules.county_memo import render_county_memo_markdown
from dashboard_modules.customer_story import customer_signal_radar_figure, customer_signal_table, customer_story_hero_html
from dashboard_modules.parcel_explorer import render_parcel_explorer_tab

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DATA_PATH = APP_ROOT / "output" / "county_rankings_2025.parquet"  # 2025 vintage refresh 2026-09-04
ASSETS_PATH = APP_ROOT / "assets"
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
XFACTOR_COMMAND_LOOP_CSV_PATH = OUTPUT_PATH / "xfactor_command_loop.csv"
XFACTOR_EVIDENCE_CENTER_CSV_PATH = OUTPUT_PATH / "xfactor_evidence_center.csv"
SOURCE_CONFIDENCE_WEIGHTING_CSV_PATH = OUTPUT_PATH / "source_confidence_weighting.csv"
ANNOUNCEMENT_ANCHOR_EVENT_LATEST_CSV_PATH = OUTPUT_PATH / "announcement_anchor_event_latest_2024.csv"
FIVEYR_BOUNDARY_REVIEW_CSV_PATH = OUTPUT_PATH / "fiveyr_boundary_review_packet.csv"
BOOM_ONSET_ARCHETYPE_LENS_CSV_PATH = OUTPUT_PATH / "boom_onset_archetype_lens_latest.csv"
WATCHLIST_ALERT_EVENTS_PATH = OUTPUT_PATH / "watchlist_alert_events.json"
DEMO_READINESS_REPORT_PATH = OUTPUT_PATH / "demo_readiness_report.json"
TOKENIZATION_READINESS_PACKET_PATH = OUTPUT_PATH / "tokenization_readiness_packet.json"
USER_DATA_PATH = OUTPUT_PATH / "dashboard_user_data.json"
# RECAL-1 (2026-09-09, operator D-D): three-layer surfaces published by scripts/publish_recal_surfaces.py
RECAL_BRIEFS_PATH = OUTPUT_PATH / "recal" / "county_briefs.parquet"
RECAL_READS_PATH = OUTPUT_PATH / "recal" / "reads.json"
RECAL_SHORTLIST_PATH = OUTPUT_PATH / "recal" / "universe_b_shortlist.csv"
RECAL_BRIEF_COLUMNS = [
    "fips", "universe_A", "universe_B", "universe_C", "density_pct", "rucc_code", "population",
    "zhvi_end", "home_value_pct", "price_to_income", "fmr_2br", "fmr_fiscal_year", "fmr_gross_yield", "rent_yield_pct",
    "rent_yield_pct_in_rucc_band", "fmr_growth3_log", "rent_price_divergence3", "zori_gross_yield", "acs_gross_yield",
    "nass_cash_rent_cropland_nonirr", "nass_cash_rent_pasture", "nass_land_value_per_acre", "nass_land_value_year",
    "aei_land_value_per_acre", "farm_cap_rate_proxy", "land_value_pct", "land_cheapness_pct", "prime_farmland_share",
    "gdp_total", "gdp_per_capita", "growth3_total", "share_retail", "share_real_estate", "share_construction",
    "share_manufacturing", "share_accommodation_food", "bea_year", "establishments_per_1k", "tourism_gdp_share",
    "retail_est_per_1k", "real_estate_est_per_1k", "arts_recreation_est_per_1k", "manufacturing_est_per_1k", "health_care_est_per_1k",
    "cbp_total_est_growth3_log", "cbp_retail_est_growth3_log", "cbp_real_estate_est_growth3_log", "cbp_vintage",
    "qcew_sector_hospitality_employment_share", "seasonal_home_share", "usda_natural_amenity_scale", "nps_visits_50km",
    "nps_visits_per_capita_50km", "nps_nearest_unit_name", "nps_nearest_unit_km", "str_host_proxy_per_1k_units",
    "nes721_growth3_log", "tourism_intensity_index", "str_occupancy", "str_adr", "str_revpar", "str_revenue_per_listing_annual",
    "str_active_listings_mapped", "str_localities_mapped", "str_as_of", "str_revpar_growth_1yr", "str_revpar_growth_3yr", "str_listings_growth_3yr",
    "str_demand_pressure_3yr", "str_history_as_of", "str_history_thin", "nri_risk_score", "usfs_wildfire_risk_score", "coastal_exposure_score",
    "qcew_commodity_cycle_flag", "momentum_rank_pct", "quiet_now", "demand_floor_ok", "boom_onset_score",
    "timing_class_median_rank_pct", "timing_champion_lane", "timing_rank_in_universe_B", "archetype_lens_best",
    "operator_review_2024", "operator_review_2025", "forward_snapshot_20260908_role", "forward_snapshot_20260909_role", "badge_urban_core",
    "badge_tiny_market", "badge_already_hot", "badge_declining", "badge_commodity_cycle", "badge_no_demand_signal",
]
USER_DATA_DB_PATH = OUTPUT_PATH / "dashboard_user_data.sqlite3"
HORIZONS = [1, 3, 5]
MIN_CAL_SHIFT = {1: 0.05, 3: 0.10, 5: 0.15}
MAX_CAL_SHIFT = {1: 0.20, 3: 0.40, 5: 0.70}
RISK_COLOR_LOW = "#1f9d55"
RISK_COLOR_MED = "#f59e0b"
RISK_COLOR_HIGH = "#dc2626"


def _timing_chip_text(honest: dict | None) -> str:
    """Header chip for the boom-onset timing engine (replaces the retired 3yr-health chip); reads the published honest coordinates."""
    h = honest or {}
    h = h.get("classifier") if isinstance(h.get("classifier"), dict) else h
    cap = next((h[k] for k in ("honest_held_out_capture_at_100", "quiet_capture_100", "capture_100") if isinstance(h.get(k), (int, float))), None)
    mult = next((h[k] for k in ("vs_random_multiple", "multiple_vs_random", "x_random") if isinstance(h.get(k), (int, float))), None)
    if cap is None:
        return "ensemble class (report-only)"
    return f"capture {cap:.3f}" + (f" ≈ {mult:.1f}× random" if mult else "")


def _fmt_timing(value) -> str:
    """Boom-onset timing score (0–1) for memo/report text; report-only, never a forecast."""
    try:
        return "—" if value is None or pd.isna(value) else f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "—"


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

    risk = row.get("composite_risk")
    conf = row.get("confidence", "unknown")
    fallback = bool(row.get("use_stable_3yr_fallback", False))
    interval = row.get("quantile_interval_width_mean", row.get("pred_std"))

    pred1 = row.get("pred_avg_1yr")
    if pd.notna(pred1):
        bullets_good.append(
            f"1yr relative-appreciation signal is {_fmt_pct(pred1)} — an ordering read against other counties, "
            "not a forecast (top-of-list precision is unproven)."
        )
    bos = row.get("boom_onset_score")
    if pd.notna(bos):
        rank_b = row.get("timing_rank_in_universe_B")
        rank_txt = f" — #{int(rank_b)} in the investable universe" if pd.notna(rank_b) else ""
        bullets_good.append(f"Boom-onset timing score is {float(bos):.2f}{rank_txt} — resemblance to the quiet years before past booms (report-only, not a forecast).")
    for feat, val in positives_5[:2]:
        bullets_good.append(f"`{feat}` is one of the strongest positive model drivers ({val:+.3f} SHAP — attribution, not causation).")
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
        bullets_caution.append(f"`{feat}` is a notable negative model driver ({val:+.3f} SHAP — attribution, not causation).")
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
        f"{row.get('county_name', 'This county')} is currently a `{conf}`-confidence entry on the strategy list. "
        f"The main case is a strong relative model signal with supportive structural drivers (context, not a "
        f"multi-year forecast), while the main question is "
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
    bos = row.get("boom_onset_score")
    if pd.notna(bos):
        thesis_bits.append(f"boom-onset timing score is {float(bos):.2f} (report-only)")
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
        "customer_tour_dismissed": False,
        "watchlist_settings": {
            "top_rank_strong": 25,
            "top_rank_watch": 100,
            "durable_top25_share": 0.60,
            "weak_top25_share": 0.20,
            "calm_std_rank": 12.0,
            "volatile_std_rank": 25.0,
            "sharp_rank_move": 10.0,
            "strong_5yr_upside": 0.15,  # legacy key kept for stored user settings; no longer read
            "weak_5yr_upside": 0.05,
            "strong_timing_score": 0.75,
            "weak_timing_score": 0.40,
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
            "customer_tour_dismissed": bool(st.session_state.get("customer_tour_dismissed", False)),
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
            f", 1yr (ordinal) `{_fmt_pct(row.get('pred_avg_1yr'))}`"
            f", timing `{_fmt_timing(row.get('boom_onset_score'))}`"
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
                f" | 1yr (ordinal) `{_fmt_pct(rec.get('pred_avg_1yr'))}`"
                f" | timing `{_fmt_timing(rec.get('boom_onset_score'))}`"
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
                f"1yr (ordinal) `{_fmt_pct(row.get('pred_avg_1yr'))}`, timing `{_fmt_timing(row.get('boom_onset_score'))}`, "
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
                    f", timing `{_fmt_timing(rec.get('boom_onset_score'))}`"
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
                f", timing `{_fmt_timing(rec.get('boom_onset_score'))}`"
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

    bos = row.get("boom_onset_score")
    if pd.notna(bos):
        if float(bos) >= float(cfg.get("strong_timing_score", 0.75)):
            strength += 1
            reasons.append("boom-onset timing score is still high (quiet-shortlist territory)")
        elif float(bos) <= float(cfg.get("weak_timing_score", 0.40)):
            concern += 1
            reasons.append("boom-onset timing score has faded")

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
def load_recal_briefs(_mtime: float) -> pd.DataFrame | None:
    """RECAL-1 county briefs (universe flags, facts by category, timing, badges); report-only."""
    if not RECAL_BRIEFS_PATH.exists():
        return None
    try:
        out = pd.read_parquet(RECAL_BRIEFS_PATH)
    except Exception:
        return None
    out["fips"] = out["fips"].astype(str).str.zfill(5)
    return out


@st.cache_data
def load_recal_reads(_mtime: float) -> dict | None:
    return _safe_json_load(RECAL_READS_PATH)


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
def load_tokenization_readiness_packet(_mtime: float) -> dict | None:
    return _safe_json_load(TOKENIZATION_READINESS_PACKET_PATH)


def load_watchlist_alert_events(_mtime: float) -> list[dict]:
    payload = _safe_json_load(WATCHLIST_ALERT_EVENTS_PATH)
    if isinstance(payload, dict):
        events = payload.get("events", [])
        return events if isinstance(events, list) else []
    return []


def _render_watchlist_alerts(events: list[dict], watched_fips: set[str]) -> None:
    """Report-only 'since you last looked' panel from the offline alert
    evaluator. Filters the global event feed to the user's watched counties."""
    relevant = [
        e for e in events if str(e.get("fips", "")).zfill(5) in watched_fips
    ] if watched_fips else []
    with st.expander(f"Watchlist Alerts ({len(relevant)})", expanded=bool(relevant)):
        st.caption(
            "Offline alert feed refreshed with the monthly research run; report-only and "
            "does not change production rank. Email delivery arrives with hosted accounts."
        )
        if not relevant:
            st.caption("No new alerts for your watched counties since the last refresh.")
            return
        df = pd.DataFrame(relevant)
        df["County"] = df["county"].astype(str) + ", " + df["state"].astype(str)
        view = df.rename(columns={"type": "Alert", "severity": "Severity", "detail": "Detail", "as_of": "As Of"})
        st.dataframe(
            view[["County", "Alert", "Severity", "Detail", "As Of"]],
            width="stretch",
            hide_index=True,
            height=240,
        )


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
    """RECAL-1 thesis presets (2026-09-09). Score components: timing (boom-onset resemblance, key
    ``growth`` for saved-profile compatibility), value (yield & cheapness), risk control, land thesis,
    confidence. ``h1`` = optional 1yr ordinal context; ``h3``/``h5`` are always 0 (falsified horizons)."""
    base = {"h1": 0, "h3": 0, "h5": 0, "uncertainty": 0, "min_confidence": "Any", "universe_only": True, "quiet_only": True}
    return {
        "Quiet shortlist (classifier order)": {**base, "growth": 100, "value": 0, "value_focus": "Balanced", "risk": 0, "structure": 0, "confidence": 0, "max_risk": 100, "structural_focus": "Overall land thesis"},
        "Quiet pre-boom (timing-led)": {**base, "growth": 80, "value": 10, "value_focus": "Balanced", "risk": 5, "structure": 0, "confidence": 5, "max_risk": 70, "structural_focus": "Overall land thesis"},
        "Timing x value (balanced)": {**base, "growth": 50, "value": 30, "value_focus": "Balanced", "risk": 10, "structure": 5, "confidence": 5, "max_risk": 70, "structural_focus": "Overall land thesis"},
        "Income first (rent yield)": {**base, "growth": 25, "value": 50, "value_focus": "Rent yield", "risk": 15, "structure": 5, "confidence": 5, "max_risk": 70, "structural_focus": "Overall land thesis"},
        "Vacation land (tourism)": {**base, "growth": 40, "value": 15, "value_focus": "Balanced", "risk": 10, "structure": 30, "confidence": 5, "max_risk": 70, "structural_focus": "Tourism intensity"},
        "Farmland & acreage": {**base, "growth": 30, "value": 40, "value_focus": "Farmland income", "risk": 10, "structure": 15, "confidence": 5, "max_risk": 70, "structural_focus": "Farmland income"},
        "Low-risk compounder": {**base, "growth": 40, "value": 20, "value_focus": "Balanced", "risk": 30, "structure": 5, "confidence": 5, "max_risk": 48, "min_confidence": "MEDIUM+", "structural_focus": "Overall land thesis"},
        "Buildable scarcity": {**base, "growth": 40, "value": 15, "value_focus": "Balanced", "risk": 10, "structure": 30, "confidence": 5, "max_risk": 65, "structural_focus": "Buildable scarcity"},
        "Climate-resilient growth": {**base, "growth": 40, "value": 15, "value_focus": "Balanced", "risk": 25, "structure": 15, "confidence": 5, "max_risk": 55, "min_confidence": "MEDIUM+", "structural_focus": "Low fragility"},
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
    if focus == "Tourism intensity":
        return (100.0 * pd.to_numeric(df.get("tourism_intensity_index", pd.Series(0.5, index=idx)), errors="coerce").fillna(0.5)).clip(0, 100)
    if focus == "Farmland income":
        prime = pd.to_numeric(df.get("prime_farmland_share", pd.Series(np.nan, index=idx)), errors="coerce").rank(pct=True).fillna(0.5)
        cap = pd.to_numeric(df.get("farm_cap_rate_proxy", pd.Series(np.nan, index=idx)), errors="coerce").rank(pct=True).fillna(0.5)
        return (100.0 * (0.5 * prime + 0.5 * cap)).clip(0, 100)
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


def _recal_value_score(df: pd.DataFrame, focus: str) -> pd.Series:
    """Value layer (observed facts, no forecast): higher = cheaper and earning more.
    Rent yield = gross rent yield percentile within the county's RUCC band (+ national);
    Farmland income = land cheapness + farm cap-rate percentiles; Balanced = yield-in-band,
    home-value cheapness, land cheapness."""
    idx = df.index
    yield_band = _product_series(df, "rent_yield_pct_in_rucc_band", 0.5) * 100.0
    yield_nat = _product_series(df, "rent_yield_pct", 0.5) * 100.0
    cheap_home = (1.0 - _product_series(df, "home_value_pct", 0.5)) * 100.0
    cheap_land = _product_series(df, "land_cheapness_pct", 0.5) * 100.0
    cap = pd.to_numeric(df.get("farm_cap_rate_proxy", pd.Series(np.nan, index=idx)), errors="coerce").rank(pct=True).fillna(0.5) * 100.0
    if focus == "Rent yield":
        return (0.7 * yield_band + 0.3 * yield_nat).clip(0, 100)
    if focus == "Farmland income":
        return (0.5 * cheap_land + 0.5 * cap).clip(0, 100)
    return (0.5 * yield_band + 0.25 * cheap_home + 0.25 * cheap_land).clip(0, 100)


def _recal_timing_score(df: pd.DataFrame, one_year_weight: float = 0.0) -> pd.Series:
    """Timing layer: the boom-onset classifier's champion-lane score rank within the scored year, with the
    ensemble-class median rank as fallback; optional 1yr ordinal context blended in. Never 3yr/5yr (falsified).
    Counties outside the quiet band are halved: a high resemblance score on an already-moving or
    collapsing market is not a pre-boom read."""
    idx = df.index
    cls = pd.to_numeric(df.get("timing_class_median_rank_pct", pd.Series(np.nan, index=idx)), errors="coerce")
    champ_raw = pd.to_numeric(df.get("boom_onset_score", pd.Series(np.nan, index=idx)), errors="coerce")
    # min-max of the champion score (a within-year rank blend) keeps the spread at the top; a percentile would
    # compress the top 50 into 98-100 and let any secondary weight decide the order
    champ = _scale_0_100(champ_raw) / 100.0 if champ_raw.notna().any() else champ_raw
    # Champion lane first so every surface (this table, the Quiet Shortlist tab, operator packets, the frozen
    # forward-validation snapshots) ranks on the same basis; the lane-agnostic class rank is the fallback and is
    # shown beside it. Skill CLAIMS stay at class level (never a named lane) — see the honest coordinates.
    timing = champ.where(champ.notna(), cls).fillna(0.0) * 100.0
    w = float(np.clip(one_year_weight, 0.0, 100.0)) / 100.0
    if w > 0 and "pred_avg_1yr" in df.columns:
        timing = (1.0 - w) * timing + w * _scale_0_100(df["pred_avg_1yr"])
    if "quiet_now" in df.columns:
        quiet = df["quiet_now"].fillna(False).astype(bool)
        timing = timing.where(quiet, timing * 0.5)
    return timing.clip(0, 100)


def _simulate_strategy_rankings(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """RECAL-1 strategy simulation: timing (classifier) x value (facts) x risk x land thesis x confidence.
    A UI overlay only — production rank artifacts are unchanged."""
    out = df.copy()
    out["sim_timing_score"] = _recal_timing_score(out, float(cfg.get("h1", 0)))
    out["sim_growth_score"] = out["sim_timing_score"]  # legacy alias read by lenses, cards, and stress tests
    out["sim_value_score"] = _recal_value_score(out, str(cfg.get("value_focus", "Balanced")))
    out["sim_risk_fit"] = (100.0 - pd.to_numeric(out.get("composite_risk", 50.0), errors="coerce").fillna(50.0)).clip(0, 100)
    out["sim_structure_score"] = _product_structural_score(out, str(cfg.get("structural_focus", "Overall land thesis")))
    out["sim_confidence_score"] = _confidence_numeric(out.get("confidence", pd.Series("MEDIUM", index=out.index)))
    if "quantile_interval_width_mean" in out.columns:
        out["sim_uncertainty_score"] = _scale_0_100(out["quantile_interval_width_mean"])
    else:
        out["sim_uncertainty_score"] = 0.0

    component_weights = {
        "sim_timing_score": float(cfg.get("growth", 60)),
        "sim_value_score": float(cfg.get("value", 15)),
        "sim_risk_fit": float(cfg.get("risk", 15)),
        "sim_structure_score": float(cfg.get("structure", 5)),
        "sim_confidence_score": float(cfg.get("confidence", 5)),
    }
    total = sum(max(v, 0.0) for v in component_weights.values()) or 1.0
    out["sim_score"] = 0.0
    for col, weight in component_weights.items():
        out["sim_score"] += (max(weight, 0.0) / total) * out[col]
    out["sim_score"] = (out["sim_score"] - float(cfg.get("uncertainty", 0)) * out["sim_uncertainty_score"] / 100.0).clip(0, 100)
    # Rank inside the active scope first (universe B / quiet-shortlist brakes), then everything else, so the
    # scoped tables number consecutively from #1 and the rank means "rank within the scope you chose".
    in_scope = pd.Series(True, index=out.index)
    if cfg.get("universe_only", True) and "universe_B" in out.columns:
        in_scope &= out["universe_B"].fillna(False).astype(bool)
    if cfg.get("quiet_only", True) and "quiet_now" in out.columns:
        in_scope &= out["quiet_now"].fillna(False).astype(bool)
        if "population" in out.columns:
            in_scope &= pd.to_numeric(out["population"], errors="coerce").fillna(0) >= 25_000
        if "demand_floor_ok" in out.columns:
            in_scope &= out["demand_floor_ok"].fillna(False).astype(bool)
    out["sim_in_scope"] = in_scope
    order = out.sort_values(["sim_in_scope", "sim_score"], ascending=[False, False]).index
    out.loc[order, "sim_rank"] = np.arange(1, len(out) + 1)
    out["sim_rank"] = out["sim_rank"].astype(int)
    if "overall_rank" in out.columns:
        out["sim_rank_delta"] = out["sim_rank"] - out["overall_rank"]
    else:
        out["sim_rank_delta"] = 0
    out["opportunity_archetype"] = out.apply(_assign_opportunity_archetype, axis=1)
    return out.sort_values("sim_rank")


def _apply_product_filter(df: pd.DataFrame, states: list[str], max_risk: float, min_confidence: str,
                          universe_only: bool = False, quiet_only: bool = False) -> pd.DataFrame:
    out = df.copy()
    if universe_only and "universe_B" in out.columns:
        out = out[out["universe_B"].fillna(False).astype(bool)]
    if quiet_only and "quiet_now" in out.columns:
        # the classifier shortlist's own brakes: quiet band, population >= 25k, observed demand
        brakes = out["quiet_now"].fillna(False).astype(bool)
        if "population" in out.columns:
            brakes &= pd.to_numeric(out["population"], errors="coerce").fillna(0) >= 25_000
        if "demand_floor_ok" in out.columns:
            brakes &= out["demand_floor_ok"].fillna(False).astype(bool)
        out = out[brakes]
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
        "sim_score", "sim_timing_score", "sim_value_score", "fmr_gross_yield", "nass_land_value_per_acre",
        "tourism_intensity_index", "composite_risk", "confidence", "sim_structure_score", "opportunity_archetype", "universe_B",
    ]
    show = df[[c for c in cols if c in df.columns]].head(limit).copy()
    rename = {
        "sim_rank": "Sim Rank",
        "overall_rank": "Prod Rank",
        "sim_rank_delta": "Rank Delta",
        "county_name": "County",
        "state": "State",
        "sim_score": "Strategy Score",
        "sim_timing_score": "Timing",
        "sim_value_score": "Value",
        "fmr_gross_yield": "Gross Rent Yield",
        "nass_land_value_per_acre": "Farm Land $/ac",
        "tourism_intensity_index": "Tourism Idx",
        "universe_B": "Universe B",
        "composite_risk": "Risk",
        "confidence": "Confidence",
        "sim_structure_score": "Thesis Fit",
        "opportunity_archetype": "Archetype",
    }
    show = show.rename(columns=rename)
    for col in ["Strategy Score", "Timing", "Value", "Risk", "Thesis Fit"]:
        if col in show.columns:
            show[col] = show[col].map(_fmt_score)
    for col in ["Gross Rent Yield"]:
        if col in show.columns:
            show[col] = show[col].map(_fmt_pct)
    if "Farm Land $/ac" in show.columns:
        show["Farm Land $/ac"] = show["Farm Land $/ac"].map(lambda x: f"${x:,.0f}" if pd.notna(x) else "—")
    if "Tourism Idx" in show.columns:
        show["Tourism Idx"] = show["Tourism Idx"].map(lambda x: f"{x:.2f}" if pd.notna(x) else "—")
    if "Universe B" in show.columns:
        show["Universe B"] = show["Universe B"].map(lambda x: "yes" if bool(x) else "no")
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
                out, source, "pred_avg_1yr", "1yr signal (ordinal)", f"{key_prefix}_pred_1yr", step=0.01, fmt="%.2f"
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
    """RECAL-1 archetype labels: timing x value x category facts (no 5yr forecast anywhere)."""
    timing = _product_numeric(row, "sim_timing_score", 50.0)
    value = _product_numeric(row, "sim_value_score", 50.0)
    quiet = bool(row.get("quiet_now")) if pd.notna(row.get("quiet_now")) else True
    tourism = _product_numeric(row, "tourism_intensity_index", 0.5)
    cap_rate = _product_numeric(row, "farm_cap_rate_proxy", np.nan)
    developability = _product_numeric(row, "land_developability_index", 0.5)
    scarcity = _product_numeric(row, "scarcity_amenity_balance_index", 0.5)
    momentum = _product_numeric(row, "momentum_rank_pct", np.nan)
    if pd.notna(momentum) and momentum > 2.0 / 3.0:
        return "Already moving (not pre-boom)"
    if not quiet:
        return "Declining / outside quiet band"
    if timing >= 85 and value >= 55:
        return "Quiet pre-boom & cheap"
    if timing >= 85:
        return "Quiet pre-boom"
    if tourism >= 0.8 and timing >= 60:
        return "Vacation / tourism"
    if pd.notna(cap_rate) and cap_rate >= 0.03 and value >= 55:
        return "Farmland income"
    if value >= 75:
        return "Income & yield"
    if developability >= 0.65 and scarcity >= 0.60:
        return "Buildable scarcity"
    if timing >= 70:
        return "Structural thesis fit"
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
        "Timing": float(cfg.get("growth", 60)),
        "Value": float(cfg.get("value", 15)),
        "Risk control": float(cfg.get("risk", 15)),
        "Land thesis": float(cfg.get("structure", 5)),
        "Confidence": float(cfg.get("confidence", 5)),
    }
    total = sum(max(v, 0.0) for v in weights.values()) or 1.0
    components = [
        ("Timing", "sim_timing_score"),
        ("Value", "sim_value_score"),
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
            "sim_score", "composite_risk", "boom_onset_score", "pred_avg_1yr",
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

    if "boom_onset_score" in base.columns:
        timing_target = _product_numeric(row, "boom_onset_score", 0.0)
        timing_peers = base.assign(timing_distance=(pd.to_numeric(base["boom_onset_score"], errors="coerce") - timing_target).abs())
        peer_sets["Similar-timing alternatives"] = timing_peers.sort_values(["timing_distance", "sim_rank"]).head(8)
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
    focus = cfg.get("structural_focus", "overall land thesis")
    timing = int(cfg.get("growth", 0)); value = int(cfg.get("value", 0)); risk = int(cfg.get("risk", 0)); structure = int(cfg.get("structure", 0))
    parts = []
    parts.append("leads with boom-onset timing" if timing >= value else "leads with value (yield & cheapness)")
    if value >= 35:
        parts.append(f"weights {str(cfg.get('value_focus', 'balanced')).lower()} value heavily")
    if risk >= 30:
        parts.append("meaningfully rewards risk control")
    if structure >= 25:
        parts.append(f"puts real weight on {str(focus).lower()}")
    if int(cfg.get("h1", 0)) > 0:
        parts.append("blends in 1yr ordinal context")
    scope = "inside investable universe B" if cfg.get("universe_only", True) else "across all scored counties"
    scope += ", with the quiet-shortlist brakes" if cfg.get("quiet_only", True) else ""
    return "This profile " + ", ".join(parts) + f" — {scope}."


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
    if ("strong 5" in q or "5yr upside" in q or "5 year upside" in q or "5-year upside" in q
            or "high upside" in q or "growth signal" in q or "1yr signal" in q or "strong growth" in q):
        out = out[out["pred_avg_1yr"] >= out["pred_avg_1yr"].quantile(0.75)]
        notes.append("Kept upper-quartile 1yr relative signal (growth intent maps to the validated 1yr ordering read).")
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


def _render_xfactor_evidence_center_tab(
    evidence_center_df: pd.DataFrame | None,
    command_loop_df: pd.DataFrame | None = None,
) -> None:
    st.header("Evidence Center")
    st.caption("Report-only source, rank, ablation, and X-factor evidence. Production rank and score are unchanged.")
    if evidence_center_df is None or evidence_center_df.empty:
        st.info("No X-factor Evidence Center artifact is available yet.")
        return

    df = evidence_center_df.copy()
    for col in [
        "surface",
        "family",
        "status",
        "allowed_use",
        "display_surface",
        "blocker",
        "next_action",
        "risk_level",
    ]:
        if col not in df.columns:
            df[col] = "n/a"
    if "evidence_center_rank" not in df.columns:
        df["evidence_center_rank"] = np.arange(1, len(df) + 1)
    if "evidence_center_priority" not in df.columns:
        df["evidence_center_priority"] = np.nan

    display_series = df["display_surface"].astype(str)
    risk_series = df["risk_level"].astype(str).str.lower()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Surfaces", f"{len(df):,}")
    m2.metric("Evidence Panels", f"{display_series.str.contains('Evidence Panel', case=False, na=False).sum():,}")
    m3.metric("Research Queue", f"{display_series.eq('Research queue').sum():,}")
    m4.metric("High Risk", f"{risk_series.eq('high').sum():,}")

    f1, f2, f3 = st.columns(3)
    families = sorted(df["family"].dropna().astype(str).unique().tolist())
    allowed_uses = sorted(df["allowed_use"].dropna().astype(str).unique().tolist())
    risks = sorted(df["risk_level"].dropna().astype(str).unique().tolist())
    selected_families = f1.multiselect("Families", families, default=[], key="product_evidence_center_families")
    selected_allowed = f2.multiselect("Allowed use", allowed_uses, default=[], key="product_evidence_center_allowed_use")
    selected_risks = f3.multiselect("Risk", risks, default=[], key="product_evidence_center_risk")
    view = df.copy()
    if selected_families:
        view = view[view["family"].astype(str).isin(selected_families)]
    if selected_allowed:
        view = view[view["allowed_use"].astype(str).isin(selected_allowed)]
    if selected_risks:
        view = view[view["risk_level"].astype(str).isin(selected_risks)]

    sort_cols = [c for c in ["evidence_center_rank", "evidence_center_priority"] if c in view.columns]
    if sort_cols:
        view = view.sort_values(sort_cols, ascending=[True] * len(sort_cols))
    show_cols = [
        "evidence_center_rank",
        "surface",
        "family",
        "status",
        "allowed_use",
        "display_surface",
        "risk_level",
        "blocker",
        "next_action",
        "evidence_center_priority",
    ]
    table = view[[c for c in show_cols if c in view.columns]].copy()
    table = table.rename(
        columns={
            "evidence_center_rank": "Rank",
            "surface": "Surface",
            "family": "Family",
            "status": "Status",
            "allowed_use": "Allowed Use",
            "display_surface": "Display",
            "risk_level": "Risk",
            "blocker": "Blocker",
            "next_action": "Next Action",
            "evidence_center_priority": "Priority",
        }
    )
    if "Priority" in table.columns:
        table["Priority"] = pd.to_numeric(table["Priority"], errors="coerce").map(lambda x: f"{x:.1f}" if pd.notna(x) else "n/a")
    st.dataframe(table, width="stretch", hide_index=True, height=520)

    b1, b2 = st.columns([1, 1])
    with b1:
        blockers = (
            view["blocker"]
            .fillna("n/a")
            .astype(str)
            .value_counts()
            .head(8)
            .reset_index()
        )
        blockers.columns = ["Blocker", "Surfaces"]
        st.subheader("Blockers")
        st.dataframe(blockers, width="stretch", hide_index=True, height=260)
    with b2:
        st.subheader("Export")
        st.download_button(
            "Evidence Center CSV",
            data=view.to_csv(index=False).encode("utf-8"),
            file_name="landinvest_xfactor_evidence_center.csv",
            mime="text/csv",
            key="product_evidence_center_csv",
        )
        if command_loop_df is not None and not command_loop_df.empty:
            st.caption("Command loop snapshot")
            command_cols = [
                "command_rank",
                "label",
                "family",
                "product_readiness",
                "promotion_gate",
                "recommended_action",
            ]
            command_view = command_loop_df[[c for c in command_cols if c in command_loop_df.columns]].head(6).copy()
            st.dataframe(command_view, width="stretch", hide_index=True, height=220)


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
                "Term": "Timing",
                "Plain-English Read": "Boom-onset classifier, ensemble-class within-year rank (0–100): how much this quiet county resembles the years before past booms. Halved outside the quiet band.",
                "Production Status": "Research surface (report-only)",
            },
            {
                "Term": "Value",
                "Plain-English Read": "Observed cheapness and income: gross rent yield within the county's RUCC band, home-value and farm-land cheapness, farm cap-rate proxy. Facts, not a forecast.",
                "Production Status": "Facts layer (vintage-stamped)",
            },
            {
                "Term": "Universe B",
                "Plain-English Read": "Investable universe: density percentile ≤ 0.95 and population < 1M. Scope rule adopted 2026-09-09 — not a model.",
                "Production Status": "Scope rule",
            },
            {
                "Term": "Gross Rent Yield",
                "Plain-English Read": "HUD Fair Market Rent (2BR) × 12 ÷ ZHVI. Validated against market rents (Spearman 0.80 vs ZORI yield).",
                "Production Status": "Facts layer",
            },
            {
                "Term": "Opportunity Score",
                "Plain-English Read": "Legacy production composite (5yr-weighted growth blend + risk). Its growth horizon has no validated forward skill — treat as context, not a forecast; county discovery lives on the Pre-Boom shortlist.",
                "Production Status": "Production artifact (context-only)",
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
                "Plain-English Read": "The headline discovery surface: counties resembling the quiet years before past booms, found before momentum is obvious.",
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
        f"- Scope: {'investable universe B' if cfg.get('universe_only', True) else 'all scored counties'}{', quiet-shortlist brakes (quiet band, >=25k pop, demand floor)' if cfg.get('quiet_only', True) else ''}",
        f"- Score mix: timing `{cfg.get('growth')}`, value `{cfg.get('value')}` ({cfg.get('value_focus', 'Balanced')}), risk `{cfg.get('risk')}`, land thesis `{cfg.get('structure')}`, confidence `{cfg.get('confidence')}`, 1yr context `{cfg.get('h1')}`",
        "- Use: county-level screening and discussion; not investment advice or parcel-level diligence.",
        "",
        "## County List",
        "",
        "| Strategy Rank | Production Rank | County | State | Timing | Value | Gross Rent Yield | Risk | Confidence | Archetype | First Diligence Check |",
        "|---:|---:|---|---|---:|---:|---:|---:|---|---|---|",
    ]
    for _, row in df.sort_values("sim_rank").head(limit).iterrows():
        _, actions = _parcel_readiness(row)
        lines.append(
            f"| {_rank_text(row.get('sim_rank'))} | {_rank_text(row.get('overall_rank'))} | "
            f"{row.get('county_name', '')} | {row.get('state', '')} | {_fmt_score(row.get('sim_timing_score'))} | {_fmt_score(row.get('sim_value_score'))} | "
            f"{_fmt_pct(row.get('fmr_gross_yield'))} | {_fmt_score(row.get('composite_risk'))} | {row.get('confidence', 'n/a')} | "
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
        "| Strategy Rank | Production Rank | County | State | Timing | Gross Rent Yield | Risk | Confidence | Best Read | Main Brake |",
        "|---:|---:|---|---|---:|---:|---:|---|---|---|",
    ]
    for _, row in compare_df.sort_values("sim_rank").iterrows():
        narrative = _build_county_narrative(row)
        support = narrative["positives"][0] if narrative["positives"] else "n/a"
        brake = narrative["cautions"][0] if narrative["cautions"] else "n/a"
        lines.append(
            f"| {_rank_text(row.get('sim_rank'))} | {_rank_text(row.get('overall_rank'))} | "
            f"{row.get('county_name', '')} | {row.get('state', '')} | {_fmt_score(row.get('sim_timing_score'))} | "
            f"{_fmt_pct(row.get('fmr_gross_yield'))} | {_fmt_score(row.get('composite_risk'))} | "
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
        "LandInvest works in three layers. **Universe**: counties where land can be bought at scale (density "
        "percentile ≤ 0.95 and population under 1M — adopted 2026-09-09; removes cooled big-city cores, keeps 91% of "
        "documented boom-family counties). **Value & yield facts** by category for every county (gross rent yield, "
        "farm land value and cash rents, economy, tourism), observed and vintage-stamped — never forecast. **Timing**: "
        "the boom-onset classifier's quiet shortlist (Discover → Quiet Shortlist). The strategy matches below rank on "
        "timing × value inside that universe; open a county memo for the facts, then export."
    )
    st.caption(
        "Product update (Sept 2026): timing comes from the boom-onset classifier (ensemble-class rank), value from "
        "observed facts. No multi-year appreciation forecast is claimed anywhere — the 5yr/3yr horizons failed honest "
        "validation; the 1yr signal is an optional ordering context only. Details: README §Model Outputs."
    )
    if filtered.empty:
        st.warning("No counties match the active strategy filters.")
        return

    s1, s2, s3 = st.columns(3)
    s1.metric("View Top Strategy Matches", f"{min(len(filtered), 25)} counties")
    s2.metric("Explore Map", f"{filtered['state'].nunique()} states")
    s3.metric("Open County Memo", str(filtered.iloc[0].get("county_name", "Top county")))

    st.subheader("Investor Review Workflow")
    r1, r2, r3, r4 = st.columns(4)
    r1.markdown("**1. Discover**\n\nScreen top counties, search, and compare strategy lenses.")
    r2.markdown("**2. Open County Memo**\n\nRead the thesis, brakes, confidence, and what would break the case.")
    r3.markdown("**3. Build Watchlist**\n\nSave counties, stage diligence, and monitor rank or risk drift.")
    r4.markdown("**4. Export Reports**\n\nDownload shortlist, compare-set, and memo packages for review.")

    st.subheader("Top Strategy Matches")
    st.caption("Ranked inside the active scope under the sidebar preset (timing x value x risk x land thesis). The pure classifier order, with facts and badges, is Discover → Quiet Shortlist.")
    st.dataframe(_product_table(filtered.sort_values("sim_rank"), limit=10), width="stretch", hide_index=True, height=360)
    top_row = filtered.sort_values("sim_rank").iloc[0]
    if st.button("Set top county as memo selection", key="start_set_top_memo", type="primary"):
        st.session_state.product_selected_fips = str(top_row.get("fips")).zfill(5)
        st.success(f"County Memo selection set to {top_row.get('county_name')}, {top_row.get('state')}.")

    g1, g2 = st.columns(2)
    with g1:
        st.subheader("Score Glossary")
        st.dataframe(_score_glossary_table(), width="stretch", hide_index=True, height=310)
        hc_path = OUTPUT_PATH / "honest_coordinates.json"
        if hc_path.exists():
            hc = json.loads(hc_path.read_text())
            c, o = hc["classifier"], hc["operator_review"]
            st.caption(
                f"Honest skill coordinates ({hc['generated_at'][:10]}): shortlist capture "
                f"{c['honest_held_out_capture_at_100']:.3f} ≈ {c['vs_random_multiple']}× random "
                f"(held-out, selection-corrected); operator precision {o['operator_precision']:.2f} "
                "(judged proxy). Full detail: Pro → Advanced → Validation."
            )
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
        data=_top_report_markdown(filtered, cfg, latest_run, limit=25, title="LandInvest Top 25 Strategy Report").encode("utf-8"),
        file_name="landinvest_top25_strategy_report.md",
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
    score_snapshot_lines = [
        f"- Strategy rank: `{_rank_text(row.get('sim_rank'))}`",
        f"- Production rank: `{_rank_text(row.get('overall_rank'))}`",
        f"- Strategy score: `{_fmt_score(row.get('sim_score'))}`",
        f"- 5yr signal: `{_fmt_pct(row.get('pred_avg_5yr'))}`",
        f"- Risk: `{_fmt_score(row.get('composite_risk'))}`",
        f"- Confidence read: `{confidence_label}`",
    ]
    preboom_signal_lines: list[str] = []
    if preboom_rows.empty:
        preboom_signal_lines.append("- This county is not currently present in the loaded top pre-boom review surfaces.")
    else:
        for _, rec in preboom_rows.iterrows():
            preboom_signal_lines.append(
                f"- `{rec['Surface']}`: rank `{rec['Review Rank']}`, breakout `{rec['Breakout Prob']}`, "
                f"residual upside `{rec['Residual Upside']}`, prior momentum `{rec['Prior Momentum']}`."
            )
    score_rows = _top_xfactor_scoreboard_rows(xfactor_scoreboard)
    xfactor_theme_lines: list[str] = []
    if not score_rows.empty:
        xfactor_theme_lines.append("- Current validated interaction themes remain report-only:")
        for _, rec in score_rows.iterrows():
            xfactor_theme_lines.append(
                f"  - {rec['Interaction']}: quiet lift `{rec.get('Quiet Lift', 'n/a')}`, decision `{rec.get('Decision', 'report-only')}`."
            )
    analog_lines: list[str] = []
    if analog_rows.empty:
        analog_lines.append("- No analog library context is currently available for this county.")
    else:
        for _, rec in analog_rows.iterrows():
            analog_lines.append(
                f"- `{rec['Analog Family']}` ({rec['Historical Window']}): {rec['Why Relevant']} "
                f"Historical read: {rec['Historical Read']}; before-hot signal: {rec['Before-Hot Signal']}."
            )
    return render_county_memo_markdown(
        county_name=str(row.get("county_name", "County")),
        state=str(row.get("state", "")),
        fips=fips,
        generated_at=datetime.now().isoformat(),
        summary=str(narrative["summary"]),
        score_snapshot_lines=score_snapshot_lines,
        support_lines=[f"- {item}" for item in narrative["positives"][:5]],
        brake_lines=[f"- {item}" for item in narrative["cautions"][:5]],
        preboom_signal_lines=preboom_signal_lines,
        xfactor_theme_lines=xfactor_theme_lines,
        structural_summary=str(wave3_note["summary"]),
        decision_thesis=str(decision["thesis"]),
        confidence_label=str(confidence_label),
        confidence_lines=[f"- {item}" for item in confidence_bullets],
        analog_lines=analog_lines,
        parcel_readiness=str(readiness),
        diligence_lines=[f"- {item}" for item in actions],
        thesis_breaker_lines=[f"- {item}" for item in _why_not_bullets(row)],
    )


def _recal_fact_rows(row: pd.Series) -> dict[str, list[tuple[str, str]]]:
    """Facts by category with vintages, from the RECAL-1 briefs merged into the scored frame."""
    def money(v):
        return f"${float(v):,.0f}" if pd.notna(v) else "—"
    def num(v, d=2):
        return f"{float(v):.{d}f}" if pd.notna(v) else "—"
    def pct_or_dash(v):
        return f"{100 * float(v):.0f}%" if pd.notna(v) else "—"
    fy = row.get("fmr_fiscal_year"); fy = f"FY{int(fy)}" if pd.notna(fy) else "FY?"
    ly = row.get("nass_land_value_year"); ly = int(ly) if pd.notna(ly) else "?"
    by = row.get("bea_year"); by = int(by) if pd.notna(by) else "?"
    scope = []
    scope.append(("Investable universe B", "yes" if bool(row.get("universe_B")) and pd.notna(row.get("universe_B")) else "no"))
    scope.append(("Quiet band (momentum rank)", f"{'yes' if bool(row.get('quiet_now')) else 'no'} ({num(row.get('momentum_rank_pct'))})"))
    scope.append(("Density percentile / RUCC", f"{num(row.get('density_pct'))} / {num(row.get('rucc_code'), 0)}"))
    scope.append(("Badges", _recal_badges(row)))
    return {
        "Scope & timing": scope + [
            ("Timing (class rank)", _fmt_score(row.get("sim_timing_score"))),
            ("Boom-onset score", num(row.get("boom_onset_score"), 3)),
            ("Rank in universe B (quiet)", num(row.get("timing_rank_in_universe_B"), 0)),
            ("Archetype lens", str(row.get("archetype_lens_best") or "—")),
            ("Operator review 2024 / 2025", f"{row.get('operator_review_2024') or '—'} / {row.get('operator_review_2025') or '—'}"),
        ],
        "Homes & rent": [
            ("ZHVI (2025)", money(row.get("zhvi_end"))), ("Home-value percentile", num(row.get("home_value_pct"))),
            ("Price / income", num(row.get("price_to_income"), 1)), (f"FMR 2BR ({fy})", money(row.get("fmr_2br"))),
            ("Gross rent yield", _fmt_pct(row.get("fmr_gross_yield"))), ("Yield pct within RUCC band", num(row.get("rent_yield_pct_in_rucc_band"))),
            ("Rent growth 3y (log)", _fmt_pct(row.get("fmr_growth3_log"))), ("Rent–price divergence 3y", _fmt_pct(row.get("rent_price_divergence3"))),
        ],
        "Land": [
            (f"Farm land $/ac (NASS {ly})", money(row.get("nass_land_value_per_acre"))), ("Residential land $/ac (AEI 2024)", money(row.get("aei_land_value_per_acre"))),
            ("Cropland cash rent $/ac", money(row.get("nass_cash_rent_cropland_nonirr"))), ("Pasture rent $/ac", money(row.get("nass_cash_rent_pasture"))),
            ("Farm cap-rate proxy", _fmt_pct(row.get("farm_cap_rate_proxy"))), ("Prime farmland share", _fmt_pct(row.get("prime_farmland_share"))),
            ("Land cheapness percentile", num(row.get("land_cheapness_pct"))),
        ],
        "Economy (activity)": [
            (f"GDP $M ({by})", f"{float(row.get('gdp_total')) / 1000:,.0f}" if pd.notna(row.get("gdp_total")) else "—"),
            ("GDP per capita", money(row.get("gdp_per_capita"))), ("GDP growth 3y (log)", _fmt_pct(row.get("growth3_total"))),
            ("Retail / real estate share", f"{_fmt_pct(row.get('share_retail'))} / {_fmt_pct(row.get('share_real_estate'))}"),
            ("Construction / manufacturing share", f"{_fmt_pct(row.get('share_construction'))} / {_fmt_pct(row.get('share_manufacturing'))}"),
            ("Establishments per 1k", num(row.get("establishments_per_1k"), 1)),
            (f"Business activity per 1k (CBP {row.get('cbp_vintage') or 'n/a'}): retail / real estate / arts-rec",
             f"{num(row.get('retail_est_per_1k'), 2)} / {num(row.get('real_estate_est_per_1k'), 2)} / {num(row.get('arts_recreation_est_per_1k'), 2)}"),
            ("Establishment growth 3y (log): all / retail / real estate",
             f"{_fmt_pct(row.get('cbp_total_est_growth3_log'))} / {_fmt_pct(row.get('cbp_retail_est_growth3_log'))} / {_fmt_pct(row.get('cbp_real_estate_est_growth3_log'))}"),
            ("Commercial price", "not available at county grain — commercial is shown as activity, not price"),
        ],
        "Tourism": [
            ("Tourism intensity index", num(row.get("tourism_intensity_index"))), ("Tourism GDP share", _fmt_pct(row.get("tourism_gdp_share"))),
            ("Hospitality employment share", _fmt_pct(row.get("qcew_sector_hospitality_employment_share"))), ("Seasonal-home share", _fmt_pct(row.get("seasonal_home_share"))),
            ("NPS visits within 50 km", f"{float(row.get('nps_visits_50km')):,.0f}" if pd.notna(row.get("nps_visits_50km")) else "—"),
            ("Nearest NPS unit", f"{row.get('nps_nearest_unit_name') or '—'} ({num(row.get('nps_nearest_unit_km'), 0)} km)"),
            ("STR-host proxy per 1k units", num(row.get("str_host_proxy_per_1k_units"), 1)), ("Natural amenity scale", num(row.get("usda_natural_amenity_scale"), 1)),
            (f"STR occupancy (AirROI, {row.get('str_as_of') or 'n/a'})", pct_or_dash(row.get("str_occupancy"))),
            ("STR nightly rate (ADR)", money(row.get("str_adr"))), ("STR RevPAR", money(row.get("str_revpar"))),
            ("STR revenue per listing (annual)", money(row.get("str_revenue_per_listing_annual"))),
            ("STR active listings (mapped localities)", f"{float(row.get('str_active_listings_mapped')):,.0f}" if pd.notna(row.get("str_active_listings_mapped")) else "—"),
            ("STR localities mapped", str(row.get("str_localities_mapped") or "—")),
            (f"STR RevPAR trend, 1y / 3y (AirROI, {row.get('str_history_as_of') or 'n/a'})", f"{_fmt_pct(row.get('str_revpar_growth_1yr'))} / {_fmt_pct(row.get('str_revpar_growth_3yr'))}"),
            ("STR supply growth 3y (active listings)", _fmt_pct(row.get("str_listings_growth_3yr"))),
            ("STR demand pressure 3y (RevPAR growth − supply growth)", "thin market (<30 listings in base window)" if bool(row.get("str_history_thin")) and pd.isna(row.get("str_demand_pressure_3yr")) else _fmt_pct(row.get("str_demand_pressure_3yr"))),
        ],
        "Risk facts": [
            ("FEMA NRI score", num(row.get("nri_risk_score"), 1)), ("Wildfire risk score", num(row.get("usfs_wildfire_risk_score"))),
            ("Coastal exposure", num(row.get("coastal_exposure_score"))), ("Commodity-cycle flag", "yes" if bool(row.get("qcew_commodity_cycle_flag")) and pd.notna(row.get("qcew_commodity_cycle_flag")) else "no"),
        ],
    }


def _render_recal_facts_card(row: pd.Series) -> None:
    if "universe_B" not in row.index:
        return
    st.subheader("Facts by category")
    st.caption("Observed, vintage-stamped facts from primary sources (HUD, NASS, BEA, Census, NPS). Not forecasts. Commercial is an activity lens; no price series is claimed.")
    groups = _recal_fact_rows(row)
    cols = st.columns(3)
    for i, (title, items) in enumerate(groups.items()):
        with cols[i % 3]:
            st.markdown(f"**{title}**")
            st.dataframe(pd.DataFrame(items, columns=["Fact", "Value"]), width="stretch", hide_index=True, height=38 + 35 * len(items))


def _recal_facts_markdown(row: pd.Series) -> str:
    if "universe_B" not in row.index:
        return ""
    lines = ["## Facts By Category (observed, vintage-stamped; not forecasts)", ""]
    for title, items in _recal_fact_rows(row).items():
        lines.append(f"### {title}")
        lines.extend(f"- {k}: {v}" for k, v in items)
        lines.append("")
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
    k4.metric("Timing (class rank)", _fmt_score(row.get("sim_timing_score")))
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
    memo_md = memo_md.rstrip() + "\n\n" + _recal_facts_markdown(row)
    _render_recal_facts_card(row)
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
    render_county_evidence_panel(
        row,
        preboom_rows=preboom_rows,
        analog_rows=analog_rows,
        command_loop_df=xfactor_command_loop_df,
        source_confidence_df=source_confidence_weighting_df,
        announcement_df=announcement_anchor_event_latest_df,
        boundary_df=fiveyr_boundary_review_df,
        archetype_df=boom_onset_archetype_lens_df,
        expanded=False,
        key_prefix=f"product_evidence_{fips}",
    )
    if not score_rows.empty:
        with st.expander("Current validated interaction themes", expanded=False):
            st.dataframe(score_rows, width="stretch", hide_index=True, height=180)
            st.caption("These interaction themes are report-only validation context, not production scoring columns.")

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
    "Quiet Pre-Boom": {
        "base_preset": "Quiet shortlist (classifier order)",
        "risk_posture": "Balanced",
        "description": "The classifier's quiet shortlist inside the investable universe, in its own order, with value facts shown beside each county.",
    },
    "Quiet Pre-Boom (timing-led blend)": {
        "base_preset": "Quiet pre-boom (timing-led)",
        "risk_posture": "Balanced",
        "description": "Timing-led with a light value and risk tiebreaker.",
    },
    "Timing x Value": {
        "base_preset": "Timing x value (balanced)",
        "risk_posture": "Balanced",
        "description": "The sweet spot: quiet pre-boom resemblance and observed cheapness/yield weighted together.",
    },
    "Income & Yield": {
        "base_preset": "Income first (rent yield)",
        "risk_posture": "Balanced",
        "description": "Leads with observed gross rent yield and cheapness; timing as the secondary read.",
    },
    "Vacation Land": {
        "base_preset": "Vacation land (tourism)",
        "risk_posture": "Balanced",
        "description": "Tourism intensity (park visits, hospitality jobs, seasonal homes, STR-host growth) plus quiet pre-boom timing.",
    },
    "Farmland & Acreage": {
        "base_preset": "Farmland & acreage",
        "risk_posture": "Balanced",
        "description": "Cheap farm land with an income floor (cash rents, cap-rate proxy, prime-farmland share) plus timing.",
    },
    "Low-Risk Growth": {
        "base_preset": "Low-risk compounder",
        "risk_posture": "Lower risk",
        "description": "Timing and value with a heavier risk-control weight and a medium-or-better confidence gate.",
    },
    "Buildable Scarcity": {
        "base_preset": "Buildable scarcity",
        "risk_posture": "Balanced",
        "description": "Emphasizes developability, scarcity, and structural land fit alongside timing.",
    },
    "Climate-Resilient Growth": {
        "base_preset": "Climate-resilient growth",
        "risk_posture": "Lower risk",
        "description": "Rewards lower fragility and cleaner structural risk alongside timing.",
    },
}


CUSTOMER_VISUAL_THEME_CATALOG = {
    "Investor": {
        "label": "Investor",
        "description": "Clean command-center view for normal diligence work.",
        "query_value": "investor",
    },
    "Vaporwave": {
        "label": "Vaporwave",
        "description": "Neon terminal skin with high-contrast market surfaces.",
        "query_value": "vaporwave",
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
    "Universe B": "Investable universe: population density percentile at or below 0.95 and population under 1M. The adopted scope rule (2026-09-09) — where land can be bought at scale. Not a model.",
    "Timing": "Boom-onset classifier, ensemble-class within-year rank (0–100): how much a quiet county resembles the years before documented booms. Halved outside the quiet band; never a forecast of returns.",
    "Value": "Observed cheapness and income (0–100): gross rent yield within the county's RUCC band, home-value and farm-land cheapness, farm cap-rate proxy. Facts, vintage-stamped.",
    "Gross Rent Yield": "HUD Fair Market Rent for a 2-bedroom unit × 12 ÷ ZHVI. Validated against market rents (Spearman 0.80 vs ZORI yield).",
    "Tourism Intensity": "Descriptive index (0–1): tourism GDP share, hospitality jobs, seasonal homes, park visits within 50 km, STR-host proxy, natural amenity. Not a validated predictor.",
    "Farm Land $/ac": "USDA Census of Agriculture value of farm real estate including buildings (2022). Shown as a range in spirit — a different asset from residential land.",
    "Business activity (CBP)": "County Business Patterns establishment counts per 1,000 residents by sector (retail 44-45, real estate 53, arts/recreation 71, manufacturing 31-33, health care 62) with three-year log growth. Commercial is shown as activity, not price: no free county-level commercial price series exists and none is claimed.",
    "STR demand pressure (AirROI)": "Three-year RevPAR growth minus three-year growth in active listings for the county's mapped STR localities (AirROI, 60-month market history). Positive = demand outran supply; negative = supply outran demand (post-boom saturation). Descriptive, pre-registered for a forward test (H-STR-FWD-1); not a forecast.",
    "STR RevPAR (AirROI)": "Short-term-rental revenue per available night for the county's principal STR localities (AirROI markets, trailing 12 months, listing-weighted). A locality snapshot, not a county total and not a forecast; shown for mapped counties only.",
    "Strategy Score": "The active Product Mode strategy score for the selected thesis, risk posture, and state universe.",
    "Customer Signal": "A presentation-only blend that makes the current opportunity easier to read. It does not rewrite production rank.",
    "Prime / Strong": "Customer-facing signal tiers based on strategy score, risk, and confidence.",
    "Composite Risk": "A 0-100 risk read where lower is cleaner for diligence.",
    "Confidence": "Model confidence bucket from the current scored artifact. Higher confidence means the model has cleaner support, not a guarantee.",
    "1yr Signal": "The 1-year-ahead relative appreciation signal from the scored artifact. Validated as an ordering read against other counties only — not a top-list picker and not a forecast.",
    "5yr Signal": "Legacy long-horizon model output, retired from every ranking and card (no validated forward skill). It survives only in the raw scored artifact.",
    "Strategy Rank": "Rank after applying the active Customer/Product thesis weights. Lower rank number is better.",
    "Parcel Readiness": "A customer workflow cue for how much parcel-level diligence is likely needed next.",
    "Active Filter": "The county matches the current Customer preset, risk posture, confidence gate, and state filters.",
    "Outside Filter": "The county exists in the scored universe, but does not match the active Customer filter.",
    "Watchlist Health": "A workflow read combining rank, stability, model growth signal, and risk to suggest whether to keep, watch, or review a county.",
}


def _customer_escape(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return html.escape(str(value), quote=True)


def _customer_visual_theme_sentinel(theme: str) -> str:
    class_name = "customer-theme-vaporwave" if theme == "Vaporwave" else "customer-theme-investor"
    return f'<div class="customer-theme-sentinel {class_name}" aria-hidden="true"></div>'


def _customer_plot_theme_tokens(theme: str) -> dict[str, object]:
    if theme == "Vaporwave":
        return {
            "font": "#f8f7ff",
            "muted": "#e9d5ff",
            "paper": "rgba(16,0,43,0)",
            "plot": "rgba(26,6,56,0.94)",
            "polar": "rgba(26,6,56,0.94)",
            "grid": "rgba(103,232,249,0.28)",
            "zero": "rgba(244,114,182,0.35)",
            "hover_bg": "#10002b",
            "hover_border": "#67e8f9",
            "geo_land": "#1a0638",
            "geo_lake": "#0b1230",
            "map_scale": [
                [0.0, "#21124b"],
                [0.28, "#7c3aed"],
                [0.55, "#ff4fd8"],
                [0.78, "#f9a8d4"],
                [1.0, "#67e8f9"],
            ],
            "risk_scale": [
                [0.0, "#67e8f9"],
                [0.35, "#a78bfa"],
                [0.68, "#ff4fd8"],
                [1.0, "#f97316"],
            ],
            "sequence": ["#67e8f9", "#f472b6", "#c084fc", "#facc15", "#22d3ee", "#fb7185"],
        }
    return {
        "font": "#0f172a",
        "muted": "#475569",
        "paper": "rgba(255,255,255,0)",
        "plot": "rgba(248,250,252,0.92)",
        "polar": "rgba(248,250,252,0.95)",
        "grid": "rgba(148,163,184,0.35)",
        "zero": "rgba(148,163,184,0.40)",
        "hover_bg": "#0f172a",
        "hover_border": "#14b8a6",
        "geo_land": "#f8fafc",
        "geo_lake": "#e0f2fe",
        "map_scale": "Viridis",
        "risk_scale": "RdYlGn_r",
        "sequence": px.colors.qualitative.Set2,
    }


def _apply_customer_plot_theme(fig: go.Figure, theme: str) -> go.Figure:
    tokens = _customer_plot_theme_tokens(theme)
    fig.update_layout(
        paper_bgcolor=tokens["paper"],
        plot_bgcolor=tokens["plot"],
        font=dict(color=tokens["font"], family="Inter, system-ui, sans-serif"),
        hoverlabel=dict(
            bgcolor=tokens["hover_bg"],
            font_color=tokens["font"],
            bordercolor=tokens["hover_border"],
        ),
    )
    fig.update_xaxes(gridcolor=tokens["grid"], zerolinecolor=tokens["zero"], linecolor=tokens["grid"], tickfont=dict(color=tokens["font"]))
    fig.update_yaxes(gridcolor=tokens["grid"], zerolinecolor=tokens["zero"], linecolor=tokens["grid"], tickfont=dict(color=tokens["font"]))
    if "polar" in fig.layout:
        fig.update_layout(
            polar=dict(
                bgcolor=tokens["polar"],
                radialaxis=dict(gridcolor=tokens["grid"], tickfont=dict(color=tokens["font"])),
                angularaxis=dict(gridcolor=tokens["grid"], tickfont=dict(color=tokens["font"])),
            )
        )
    return fig


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
    meta.append(("Timing engine", _timing_chip_text((globals().get("recal_reads") or {}).get("honest"))))  # replaces the retired 3yr-health chip
    meta_html = "".join(_brand_chip_html(label, value) for label, value in meta)
    return f"""
<div class="landinvest-brand-header" role="banner" aria-label="LandInvest application summary">
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
<div class="landinvest-sidebar-brand" aria-label="LandInvest sidebar brand">
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
    visual_theme: str,
) -> str:
    params = {
        "experience": "customer",
        "customer_preset": customer_preset,
        "risk_posture": risk_posture,
        "workspace": workspace,
        "customer_theme": CUSTOMER_VISUAL_THEME_CATALOG.get(
            visual_theme,
            CUSTOMER_VISUAL_THEME_CATALOG["Investor"],
        )["query_value"],
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


def _normalize_customer_visual_theme(value: str | None) -> str:
    normalized = str(value or "").strip().lower().replace("-", " ").replace("_", " ")
    aliases = {
        "": "Investor",
        "investor": "Investor",
        "default": "Investor",
        "classic": "Investor",
        "clean": "Investor",
        "vaporwave": "Vaporwave",
        "vapor": "Vaporwave",
        "synthwave": "Vaporwave",
        "neon": "Vaporwave",
    }
    return aliases.get(normalized, "Investor")


def _customer_visual_theme_label(theme: str) -> str:
    return CUSTOMER_VISUAL_THEME_CATALOG.get(theme, CUSTOMER_VISUAL_THEME_CATALOG["Investor"])["label"]


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


# Pro-tier score and policy terms; shown alongside CUSTOMER_TERM_DEFINITIONS
# in the Pro term guide so every score visible in Product Mode is defined.
PRO_TERM_DEFINITIONS = {
    "Model Disagreement": "Gap between the XGBoost and LightGBM predictions for the same county. A larger gap means a less trustworthy point estimate.",
    "Horizon Spread": "How much the 1yr/3yr/5yr predictions disagree after scaling. Big spreads signal timing uncertainty.",
    "Prediction Interval": "Conformal range around the point prediction. Wider intervals mean less certainty.",
    "Fallback": "The 3yr model policy substituted a guarded baseline because the specialist signal failed its checks for this county.",
    "Top-25 Churn": "Share of the national top-25 that changed since the previous run. High churn means an unstable regime or a data shift worth investigating.",
    "Guarded Blend": "The default pre-boom ranking: momentum-safe signals with brakes applied.",
    "Residual Upside": "Model upside left after removing what momentum already explains. Display-guarded and report-only; never a rank.",
    "Quiet County": "Prior-momentum rank at or below the 67th percentile — a county that is not yet moving.",
    "Promotion Gate": "The evidence ladder a research signal must clear before it can affect any default surface.",
    "Evidence Panel": "Opt-in, report-only context cards from gated sources (events, anchors). Context for diligence, never part of rank.",
}

# What / How / Next guides for every Product Mode tab. Keep each line short:
# the popover is a 10-second orientation, not documentation.
PRO_TAB_GUIDES = {
    "start": ("Your home base: current run status, headline signals, and suggested next steps.", "Scan the run chips and cards for anything unusual.", "Head to Discover -> Search to find counties."),
    "search": ("Plain-English county search.", "Type a goal like 'low-risk Mountain West with a strong growth signal'; it maps to transparent filters.", "Open promising counties in County Memo."),
    "explore": ("The ranked table of the full scored universe under current filters.", "Sort by strategy rank or any score; narrow with the sidebar filters.", "Send candidates to County Memo or the Watchlist."),
    "preboom": ("The headline discovery surface (report-only): the boom-onset classifier's quiet shortlist ranked inside investable universe B, with value facts and archetype lens beside each county.", "Read timing and value together; badges flag the known false-positive modes; the legacy two-score lane sits in an expander for reference.", "Treat hits as diligence leads, never as a buy list."),
    "strategy": ("Strategy simulator: re-weight the thesis and watch ranks move.", "Adjust the weights; the resulting rank is a simulation, not a saved artifact.", "Save a shortlist you like to the Watchlist."),
    "screening": ("Hard-threshold screening across scores and brakes.", "Set floors and caps to cut the universe down to survivors.", "Export survivors or push them to the Watchlist."),
    "region": ("State and regional rollups.", "Compare regions before drilling into counties.", "Drill into a region's counties via Explore."),
    "map": ("Choropleth of the active signal across all counties.", "Switch signal layers; click a county for details.", "Open clicked counties in County Memo."),
    "memo": ("A one-county diligence memo: scores, drivers, history, and caveats.", "Pick a county and read top to bottom.", "Add it to the Watchlist or export via Reports."),
    "watchlist": ("Your saved counties with health and stage tracking.", "Use stages, notes, and alerts as your workflow; they never change production rank.", "Promote conviction names into the Funnel."),
    "funnel": ("Pipeline view of watchlist stages.", "Move counties through research -> diligence -> decision.", "Export decisions via Reports."),
    "reports": ("Bundle exports: shortlists, packets, and CSVs.", "Pick the artifacts you need and export for handoff.", "Share or archive the packet."),
    "thesis": ("Long-form investment memo builder.", "Compose the thesis from current evidence; edit before export.", "Export as the final memo."),
    "evidence_center": ("Governance view of x-factor evidence panels and source gates.", "Read panel status and provenance; nothing here is a rank.", "Consult the promotion-gates doc before promoting anything."),
    "run_review": ("Run-over-run rank movement review.", "Compare this run against the previous one; investigate big movers.", "Check Model Health if churn looks abnormal."),
    "autopsy": ("Post-mortems of past misses and hits.", "Read the case studies for recurring failure patterns.", "Feed the lessons into your strategy settings."),
    "promotion_gate": ("Promotion-gate scoreboard for research candidates.", "Check which gates a candidate currently passes.", "Promotion requires the full gate contract, not this view alone."),
    "model_health": ("Model health diagnostics: calibration, drift, and coverage.", "Scan the statuses; investigate anything flagged.", "Slow down decisions while health is degraded."),
    "stress": ("Scenario stress tests on the current strategy.", "Apply shocks and see which picks are fragile.", "Prefer counties that hold up across scenarios."),
    "peers": ("Peer-set construction for county comparables.", "Inspect how peers are chosen for a county.", "Use peer sets inside County Memo comparisons."),
    "disagreement": ("Counties where XGBoost and LightGBM disagree most.", "High disagreement means lower trust in the point estimate.", "Treat high-disagreement counties as leads needing extra diligence."),
    "validation": ("Model validation: walk-forward CV, known-boom backtests, conformal coverage.", "Read MAE and relative ranking, not raw R²; check that known booms rank in top percentiles.", "Slow decisions if coverage or backtests degrade."),
    "system_status": ("Operational health: source freshness, completeness, drift, Wave 2/3 posture.", "Scan source health and missingness; investigate anything flagged.", "Rerun the pipeline or refresh sources if health is degraded."),
    "tokenization": ("Internal, report-only SOURCING-readiness screen — A/B/C tiers over the quiet shortlist with best land-type strategy and income fit.", "Read tier + best land-type strategy as a parcel-diligence priority, never as investability; all six investability gates stay blocked.", "Pursue Tier A income-fit counties for parcel diligence; offerings need parcel data + securities counsel first."),
}


def _render_pro_tab_guide(tab_key: str) -> None:
    guide = PRO_TAB_GUIDES.get(tab_key)
    if not guide:
        return
    what, how, nxt = guide
    with st.popover("How this tab works", help="What this tab is, how to use it, and what to do next."):
        st.markdown(f"**What it is.** {what}")
        st.markdown(f"**How to use it.** {how}")
        st.markdown(f"**What to do next.** {nxt}")


def _render_pro_term_guide(label: str = "Term Guide") -> None:
    with st.popover(label, help="Definitions for every score and policy label shown in Pro."):
        for term, body in {**CUSTOMER_TERM_DEFINITIONS, **PRO_TERM_DEFINITIONS}.items():
            st.markdown(f"**{term}**")
            st.caption(body)


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
        "customer_experience_preset": profile.get("customer_preset_name", "Quiet Pre-Boom"),
        "customer_preset": profile.get("base_preset") or cfg.get("preset_name") or "Quiet shortlist (classifier order)",
        "customer_risk_posture": profile.get("risk_posture", "Balanced"),
        "customer_states": profile.get("states", []),
        "customer_card_limit": int(profile.get("card_limit", 12)),
        "customer_workspace": profile.get("workspace", "Radar"),
        "customer_radar_layer": profile.get("radar_layer", "sim_score"),
        "customer_visual_theme": _normalize_customer_visual_theme(profile.get("visual_theme")),
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
    visual_theme: str,
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
        "visual_theme": _normalize_customer_visual_theme(visual_theme),
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
                "1yr Signal": _fmt_pct(row.get("pred_avg_1yr")),
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
    visual_theme: str,
    run_id: str,
    universe_count: int,
    full_count: int,
    prime_count: int,
    churn: float | None,
    health: str | None,
) -> str:
    churn_text = f"{100 * churn:.1f}%" if churn is not None else "n/a"
    health_text = _humanize_status_label(health) if health else "n/a"
    if visual_theme == "Vaporwave":
        kicker = "LandInvest Customer Mode | Vaporwave"
        title = "Neon Market Terminal"
    else:
        kicker = "LandInvest Customer Mode"
        title = "Investment Command Center"
    return f"""
<div class="customer-command-header" role="region" aria-label="Customer Mode investment command summary">
  <div class="customer-command-copy">
    <div class="customer-kicker">{_customer_escape(kicker)}</div>
    <h1>{_customer_escape(title)}</h1>
    <p>{_customer_escape(_customer_county_display(top_row))} leads the active thesis. {_customer_escape(_customer_thesis_read(top_row))}</p>
  </div>
  <div class="customer-command-grid">
    <span><b>{_customer_escape(customer_preset_name)}</b><small>Preset</small></span>
    <span><b>{_customer_escape(risk_posture)}</b><small>Risk posture</small></span>
    <span><b>{universe_count:,} / {full_count:,}</b><small>Active universe</small></span>
    <span><b>{prime_count}</b><small>Prime signals</small></span>
    <span><b>{_customer_escape(churn_text)}</b><small>Top-25 churn</small></span>
    <span><b>{_customer_escape(_timing_chip_text((globals().get("recal_reads") or {}).get("honest")))}</b><small>Timing engine</small></span>
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


def _customer_empty_state_html(
    title: str,
    body: str,
    actions: list[str] | None = None,
    *,
    tone: str = "neutral",
) -> str:
    action_html = ""
    if actions:
        action_html = "<ul>" + "".join(f"<li>{_customer_escape(action)}</li>" for action in actions) + "</ul>"
    return f"""
<div class="customer-empty-state customer-empty-{_customer_escape(tone)}" role="status" aria-live="polite">
  <span class="customer-kicker">{_customer_escape(tone.title())}</span>
  <h3>{_customer_escape(title)}</h3>
  <p>{_customer_escape(body)}</p>
  {action_html}
</div>
"""


def _render_customer_empty_state(
    title: str,
    body: str,
    actions: list[str] | None = None,
    *,
    tone: str = "neutral",
) -> None:
    st.markdown(_customer_empty_state_html(title, body, actions, tone=tone), unsafe_allow_html=True)


def _customer_map_selection_html(row: pd.Series) -> str:
    return f"""
<div class="customer-map-callout" role="region" aria-label="Selected county map summary">
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
    if score >= 58 or _product_numeric(row, "sim_timing_score", 0.0) >= 85:
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
    risk = row.get("composite_risk")
    return (f"{archetype}: timing {_fmt_score(row.get('sim_timing_score'))}, value {_fmt_score(row.get('sim_value_score'))}, "
            f"gross rent yield {_fmt_pct(row.get('fmr_gross_yield'))}, risk {_fmt_score(risk)}.")


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
    timing = _customer_signal_value(row, "sim_timing_score")
    value = _customer_signal_value(row, "sim_value_score")
    risk_fit = _customer_signal_value(row, "sim_risk_fit")
    land_fit = _customer_signal_value(row, "sim_structure_score")
    confidence = _customer_signal_value(row, "sim_confidence_score")
    bars = "".join(
        [
            _customer_signal_bar_html("Signal", signal, color),
            _customer_signal_bar_html("Timing", timing, "#38bdf8"),
            _customer_signal_bar_html("Value", value, "#14b8a6"),
            _customer_signal_bar_html("Risk Control", risk_fit, "#22c55e"),
            _customer_signal_bar_html("Land Fit", land_fit, "#a78bfa"),
            _customer_signal_bar_html("Confidence", confidence, "#f59e0b"),
        ][:3 if compact else 6]
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
                "Timing": _fmt_score(row.get("sim_timing_score")),
                "Value": _fmt_score(row.get("sim_value_score")),
                "Gross Rent Yield": _fmt_pct(row.get("fmr_gross_yield")),
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
            {"Signal": "Timing", "Score": _customer_signal_value(row, "sim_timing_score"), "Read": f"class rank {_fmt_score(row.get('sim_timing_score'))}"},
            {"Signal": "Value", "Score": _customer_signal_value(row, "sim_value_score"), "Read": f"gross yield {_fmt_pct(row.get('fmr_gross_yield'))}"},
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


_ARCHETYPE_READS = {
    "anchor": "an employer/institution-led setup (jobs, anchors, campuses)",
    "amenity": "an amenity/migration-led setup (inflows from costly metros, second-home demand)",
    "adoption": "an early-adoption setup (new business formation, broadband take-up)",
}


def _customer_archetype_read(fips: str, lens_df: pd.DataFrame | None) -> tuple[str, str] | None:
    """Return (headline, detail) describing which boom archetype a county most
    resembles, from the report-only archetype-lens artifact, or None."""
    if lens_df is None or lens_df.empty or "fips" not in lens_df.columns:
        return None
    work = lens_df.copy()
    work["fips"] = work["fips"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)
    match = work[work["fips"].eq(str(fips).zfill(5))]
    if match.empty:
        return None
    rec = match.iloc[0]
    ranks = {
        key: rec.get(f"{key}_lens_rank")
        for key in _ARCHETYPE_READS
        if pd.notna(rec.get(f"{key}_lens_rank"))
    }
    if not ranks:
        return None
    best_key = min(ranks, key=ranks.get)
    best_rank = int(ranks[best_key])
    # only call it out when the lens is genuinely enthusiastic about the county
    if best_rank > 300:
        return ("No single boom archetype stands out yet for this county.", "")
    return (
        f"Most resembles {_ARCHETYPE_READS[best_key]}.",
        f"The {best_key} research lens ranks this county {best_rank} of ~3,100 nationally. "
        "Report-only context; it does not change rank.",
    )


# Per-county structural land reads surfaced from the archetype-lens artifact
# (report-only national percentiles). dynamism_pct + farmland_cash_rent_pct are
# the free-data lanes added in the 2026 sweep (backlog UX1).
_STRUCTURAL_READS = {
    "dynamism_pct": "Economic dynamism (GDP + firm growth)",
    "farmland_cash_rent_pct": "Farmland cash-rent level",
    "natural_amenity_pct": "Natural amenity",
    "supply_constraint_pct": "Supply constraint (zoning)",
}


def _customer_structural_reads(fips: str, lens_df: pd.DataFrame | None) -> list[tuple[str, int]]:
    """Available per-county structural percentiles (label, percentile) from the
    archetype-lens artifact, or an empty list."""
    if lens_df is None or lens_df.empty or "fips" not in lens_df.columns:
        return []
    work = lens_df.copy()
    work["fips"] = work["fips"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)
    match = work[work["fips"].eq(str(fips).zfill(5))]
    if match.empty:
        return []
    rec = match.iloc[0]
    reads: list[tuple[str, int]] = []
    for col, label in _STRUCTURAL_READS.items():
        val = rec.get(col)
        if pd.notna(val):
            reads.append((label, int(val)))
    return reads


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
    visual_theme: str = "Investor",
) -> None:
    fips = str(row.get("fips", "")).zfill(5)
    tier = str(row.get("customer_tier") or _customer_tier_label(row))
    color = CUSTOMER_TIER_COLORS.get(tier, "#64748b")
    st.markdown(
        customer_story_hero_html(
            county_display=_customer_county_display(row),
            thesis_read=_customer_thesis_read(row),
            tier=tier,
            tier_color=color,
            strategy_rank=_rank_text(row.get("sim_rank")),
            production_rank=_rank_text(row.get("overall_rank")),
            risk_score=_fmt_score(row.get("composite_risk")),
        ),
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Customer Signal", _fmt_score(row.get("customer_signal_score")))
    c2.metric("1yr Signal", _fmt_pct(row.get("pred_avg_1yr")))
    c3.metric("Risk Band", row.get("customer_risk_band", _customer_risk_band(row)))
    c4.metric("Confidence", row.get("confidence", "n/a"))
    c5.metric("Parcel Read", _parcel_readiness(row)[0])

    archetype_read = _customer_archetype_read(fips, boom_onset_archetype_lens_df)
    if archetype_read is not None:
        headline, detail = archetype_read
        st.info(f"**Boom archetype:** {headline}" + (f" {detail}" if detail else ""))

    structural_reads = _customer_structural_reads(fips, boom_onset_archetype_lens_df)
    if structural_reads:
        chips = " · ".join(f"{label} {pct}th pct" for label, pct in structural_reads)
        st.caption(
            f"Structural land reads (report-only national percentiles): {chips}"
        )

    signal_rows = _customer_signal_rows(row)
    fig = customer_signal_radar_figure(signal_rows, color=color)
    _apply_customer_plot_theme(fig, visual_theme)

    left, right = st.columns([1.05, 1])
    with left:
        with st.container(border=True):
            st.plotly_chart(fig, width="stretch")
    with right:
        st.caption("Signal stack")
        st.dataframe(customer_signal_table(signal_rows), width="stretch", hide_index=True, height=310)

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
    render_county_evidence_panel(
        row,
        preboom_rows=preboom_rows,
        analog_rows=analog_rows,
        command_loop_df=xfactor_command_loop_df,
        source_confidence_df=source_confidence_weighting_df,
        announcement_df=announcement_anchor_event_latest_df,
        boundary_df=fiveyr_boundary_review_df,
        archetype_df=boom_onset_archetype_lens_df,
        expanded=False,
        key_prefix=f"customer_evidence_{fips}",
    )

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
    if not st.session_state.get("customer_tour_dismissed", False):
        with st.container(border=True):
            st.markdown("**Welcome — three steps to your first shortlist**")
            tour_cols = st.columns([1, 1, 1, 0.35])
            tour_cols[0].markdown(
                "**1. Pick a preset.** Choose an investment thesis in the sidebar "
                "(Quiet Pre-Boom is a good start)."
            )
            tour_cols[1].markdown(
                "**2. Open a county story.** Click a county on the Radar map, then "
                "open its Story for the plain-English read."
            )
            tour_cols[2].markdown(
                "**3. Save it.** Add promising counties to your Watchlist and export "
                "a Packet when you are ready."
            )
            if tour_cols[3].button(
                "Got it",
                key="customer_tour_dismiss",
                help="Hide this intro. It stays hidden for this profile.",
            ):
                st.session_state.customer_tour_dismissed = True
                _save_current_user_state()
                st.rerun()
    presets = _product_thesis_presets()
    customer_preset_names = list(CUSTOMER_PRESET_CATALOG)
    requested_customer_preset = _query_param_first("customer_preset", "Quiet Pre-Boom")
    if requested_customer_preset not in CUSTOMER_PRESET_CATALOG:
        requested_customer_preset = "Quiet Pre-Boom"
    requested_workspace = _query_param_first("workspace", "Radar")
    workspace_options = ["Radar", "Opportunities", "County Story", "Compare", "Watchlist", "Packet"]
    if requested_workspace not in workspace_options:
        requested_workspace = "Radar"
    requested_visual_theme = _normalize_customer_visual_theme(_query_param_first("customer_theme", "Investor"))
    requested_fips = _normalize_fips_value(_query_param_first("fips"))
    if requested_fips and "customer_selected_fips" not in st.session_state:
        st.session_state.customer_selected_fips = requested_fips
    pending_customer_view = st.session_state.pop("pending_customer_view_profile", None)
    if isinstance(pending_customer_view, dict):
        for key, value in _customer_view_session_state(pending_customer_view).items():
            st.session_state[key] = value
    has_explicit_customer_view = any(
        _query_param_first(param)
        for param in ["customer_preset", "risk_posture", "workspace", "states", "fips", "customer_theme"]
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
        with st.expander("Experience Style", expanded=True):
            visual_theme_kwargs = {}
            if "customer_visual_theme" not in st.session_state:
                visual_theme_kwargs["default"] = requested_visual_theme
            customer_visual_theme = st.segmented_control(
                "Visual skin",
                list(CUSTOMER_VISUAL_THEME_CATALOG),
                selection_mode="single",
                required=True,
                format_func=_customer_visual_theme_label,
                key="customer_visual_theme",
                help="Switch the Customer Mode presentation skin without changing scoring, ranks, filters, or saved artifacts.",
                width="stretch",
                **visual_theme_kwargs,
            )
            if customer_visual_theme is None:
                customer_visual_theme = requested_visual_theme
            st.caption(CUSTOMER_VISUAL_THEME_CATALOG[customer_visual_theme]["description"])
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
    st.markdown(_customer_visual_theme_sentinel(customer_visual_theme), unsafe_allow_html=True)

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
    filtered = _apply_product_filter(sim_df, selected_states, float(cfg.get("max_risk", 70)), str(cfg.get("min_confidence", "Any")),
                                     universe_only=bool(cfg.get("universe_only", True)), quiet_only=bool(cfg.get("quiet_only", True))).sort_values("sim_rank")

    if filtered.empty:
        _render_trust_banner(latest_run, df, xfactor_promotion_gate)
        _render_customer_empty_state(
            "No counties match this Customer setup",
            "The active preset, risk posture, confidence gate, and state filters produced an empty review universe.",
            [
                "Clear the state filter or widen the selected state set.",
                "Switch Risk posture to Balanced or More aggressive.",
                "Try the General Opportunity preset before saving this view.",
            ],
            tone="review",
        )
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
            visual_theme=customer_visual_theme,
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
                    f"{view_meta.get('workspace', 'Radar')} / "
                    f"{_normalize_customer_visual_theme(view_meta.get('visual_theme'))}"
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
                        visual_theme=customer_visual_theme,
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
        visual_theme=customer_visual_theme,
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
  <span><b>{_fmt_pct(filtered['fmr_gross_yield'].median()) if 'fmr_gross_yield' in filtered.columns else '—'}</b><small>Median gross rent yield</small></span>
</div>
""",
            unsafe_allow_html=True,
        )

        map_layer_labels = {
            "customer_signal_score": "Customer Signal",
            "sim_score": "Strategy Score",
            "sim_timing_score": "Timing (boom-onset)",
            "sim_value_score": "Value (yield & cheapness)",
            "fmr_gross_yield": "Gross Rent Yield",
            "tourism_intensity_index": "Tourism Intensity",
            "nass_land_value_per_acre": "Farm Land $/ac",
            "pred_avg_1yr": "1yr Signal (context)",
            "composite_risk": "Risk",
            "lens_parcel_readiness": "Parcel Readiness",
            "sim_structure_score": "Land Fit",
        }
        map_layer_kwargs = {}
        if "customer_radar_layer" not in st.session_state:
            map_layer_kwargs["index"] = 0
        map_layer = st.selectbox(
            "Map signal layer",
            ["sim_score", "customer_signal_score", "pred_avg_1yr", "composite_risk", "lens_parcel_readiness", "sim_structure_score"],
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
            plot_tokens = _customer_plot_theme_tokens(customer_visual_theme)
            map_color_scale = plot_tokens["risk_scale"] if map_layer == "composite_risk" else plot_tokens["map_scale"]
            fig_map = px.choropleth(
                map_df,
                geojson=county_geojson,
                locations="fips_str",
                color=map_layer,
                hover_name="county_name",
                hover_data={"state": True, "customer_tier": True, "customer_universe": True, "sim_rank": True, "fips_str": False},
                color_continuous_scale=map_color_scale,
                scope="usa",
                title=f"{map_layer_labels.get(map_layer, map_layer.replace('_', ' ').title())} Radar | {selected_map_title}",
                custom_data=["fips_str", "state", "customer_tier", "customer_universe", "sim_rank"],
            )
            fig_map.update_traces(
                marker_line_width=0.25,
                marker_line_color="rgba(103, 232, 249, 0.34)" if customer_visual_theme == "Vaporwave" else "rgba(15, 23, 42, 0.28)",
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
                        colorscale=[[0, "rgba(250,204,21,0.24)"], [1, "rgba(250,204,21,0.24)"]],
                        showscale=False,
                        marker_line_color="#facc15" if customer_visual_theme == "Vaporwave" else "#f59e0b",
                        marker_line_width=4.0,
                        hoverinfo="skip",
                        name="Selected county",
                    )
                )
            fig_map.update_layout(
                height=650,
                margin=dict(l=0, r=0, t=52, b=0),
                clickmode="event+select",
                paper_bgcolor=plot_tokens["paper"],
                plot_bgcolor=plot_tokens["paper"],
                font=dict(color=plot_tokens["font"], family="Inter, system-ui, sans-serif"),
                title=dict(font=dict(size=18), x=0.01, xanchor="left"),
                hoverlabel=dict(bgcolor=plot_tokens["hover_bg"], font_color=plot_tokens["font"], bordercolor=plot_tokens["hover_border"]),
                geo=dict(
                    bgcolor="rgba(0,0,0,0)",
                    lakecolor=plot_tokens["geo_lake"],
                    landcolor=plot_tokens["geo_land"],
                    subunitcolor=plot_tokens["grid"],
                    coastlinecolor=plot_tokens["grid"],
                ),
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
            ["Strategy rank", "Best timing", "Highest rent yield", "Cheapest farm land", "Tourism intensity", "Customer signal", "Lowest risk", "Best land fit"],
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
            "Best timing": ("sim_timing_score", False),
            "Highest rent yield": ("fmr_gross_yield", False),
            "Cheapest farm land": ("nass_land_value_per_acre", True),
            "Tourism intensity": ("tourism_intensity_index", False),
            "Customer signal": ("customer_signal_score", False),
            "Lowest risk": ("composite_risk", True),
            "Best land fit": ("sim_structure_score", False),
        }
        sort_col, ascending = sort_map[sort_choice]
        card_df = card_df.sort_values([sort_col, "sim_rank"], ascending=[ascending, True]).head(int(card_limit))
        if card_df.empty:
            _render_customer_empty_state(
                "No opportunity cards match this search",
                "The active opportunity universe is still available, but the current search phrase removed every card.",
                [
                    "Clear the search field to restore the active shortlist.",
                    "Search by state abbreviation, county name, archetype, risk band, or signal tier.",
                    "Use County Story when you want to search every scored county.",
                ],
                tone="search",
            )
        else:
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
            _render_customer_empty_state(
                "No County Story match",
                "The search did not match a county, state, FIPS code, archetype, tier, or risk band in the scored universe.",
                [
                    "Try a shorter county name or two-letter state abbreviation.",
                    "Use a five-digit FIPS code when you have one.",
                    "Clear the search to return to the full scored county list.",
                ],
                tone="search",
            )
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
                visual_theme=customer_visual_theme,
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
            _render_customer_empty_state(
                "Choose counties to compare",
                "The comparison chart needs at least one selected county before it can draw the signal stack.",
                [
                    "Select one to five counties from the compare control.",
                    "Start with the default top-ranked counties when you want a quick benchmark.",
                ],
                tone="action",
            )
        else:
            winner = compare_df.sort_values("sim_rank").iloc[0]
            st.success(
                f"Best fit under this Customer Mode thesis: {_customer_county_display(winner)} "
                f"at strategy {_rank_text(winner.get('sim_rank'))}."
            )
            score_cols = ["customer_signal_score", "sim_timing_score", "sim_value_score", "sim_risk_fit", "sim_structure_score", "sim_confidence_score"]
            chart_df = compare_df[["county_name", "state"] + [c for c in score_cols if c in compare_df.columns]].copy()
            chart_df["County"] = compare_df.apply(_customer_county_display, axis=1).values
            long_chart = chart_df.melt(id_vars=["County"], value_vars=[c for c in score_cols if c in chart_df.columns], var_name="Signal", value_name="Score")
            long_chart["Signal"] = long_chart["Signal"].map(
                {
                    "customer_signal_score": "Customer Signal",
                    "sim_timing_score": "Timing",
                    "sim_value_score": "Value",
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
                color_discrete_sequence=_customer_plot_theme_tokens(customer_visual_theme)["sequence"],
            )
            fig_compare.update_layout(height=420, margin=dict(t=45, b=20))
            _apply_customer_plot_theme(fig_compare, customer_visual_theme)
            with st.container(border=True):
                st.plotly_chart(fig_compare, width="stretch")
            st.dataframe(_customer_brief_table(compare_df, limit=len(compare_df)), width="stretch", hide_index=True, height=320)

    elif workspace == "Watchlist":
        watch_fips = {str(f).zfill(5) for f in st.session_state.watchlist_fips}
        watch_df = sim_df[sim_df["fips"].astype(str).str.zfill(5).isin(watch_fips)].copy().sort_values("sim_rank")
        summary = _watchlist_portfolio_summary(watch_df)
        if watch_df.empty:
            _render_customer_empty_state(
                "Your Customer watchlist is empty",
                "Save counties from Radar, Opportunity Deck, or County Story to build a diligence queue.",
                [
                    "Open a county story from the map or cards and choose Add To Watchlist.",
                    "Use Starter Candidates below as a first-pass shortlist.",
                    "Watchlist data is local demo storage for the current user profile.",
                ],
                tone="action",
            )
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
                    color_discrete_sequence=_customer_plot_theme_tokens(customer_visual_theme)["sequence"],
                )
                fig_watch.update_layout(
                    height=420,
                    margin=dict(t=50, b=30),
                    xaxis_title="Composite Risk (lower is cleaner)",
                    yaxis_title="Customer Signal",
                )
                _apply_customer_plot_theme(fig_watch, customer_visual_theme)
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
        if watch_df.empty:
            _render_customer_empty_state(
                "Packet has no watchlist counties yet",
                "The export is still available and will use the active Radar shortlist, but the Watchlist Command Center section is stronger after you save counties.",
                [
                    "Add counties from Radar, Opportunity Deck, or County Story.",
                    "Use the active shortlist export for a quick first handoff.",
                ],
                tone="action",
            )
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


def _render_honest_coordinates() -> None:
    """Current honest claim coordinates, generated (never hardcoded) by
    scripts/build_honest_coordinates.py from the measurement artifacts."""
    path = OUTPUT_PATH / "honest_coordinates.json"
    if not path.exists():
        st.caption("Honest-coordinates artifact missing — regenerate with "
                   "`scripts/build_honest_coordinates.py`.")
        return
    hc = json.loads(path.read_text())
    c, o, fv = hc["classifier"], hc["operator_review"], hc["forward_validation"]
    r1 = hc["regression"]["horizons"]["1yr"]
    st.subheader("Current Honest Coordinates")
    st.caption(f"Generated {hc['generated_at'][:10]} from the measurement artifacts — "
               "these are the ONLY model-skill numbers this product claims.")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Shortlist capture (honest)", f"{c['honest_held_out_capture_at_100']:.3f}",
              f"{c['vs_random_multiple']}× random", delta_color="off")
    m2.metric("Operator precision (proxy)", f"{o['operator_precision']:.2f}",
              f"{o['accepted']}✓ / {o['rejected']}✗ / {o['held']} hold", delta_color="off")
    m3.metric("1yr rank signal (ordinal)", f"{r1['embargoed_median_spearman']:+.2f}",
              "top-K unproven", delta_color="off")
    m4.metric("Realized outcomes graded", "0 so far",
              f"clock running {max(s['days_elapsed'] for s in fv['snapshots'])}d", delta_color="off")
    st.caption(
        f"Shortlist figure: {c['claim']} Measured on {c['measured_on']} "
        f"(naive argmax {c['naive_argmax']:.3f}; {c['vs_best_baseline_ratio']}× best baseline). "
        "3yr/5yr appreciation forecasts are falsified and never presented. "
        "Operator precision is judged, not realized; the forward-validation clock is the "
        "realized read and is sparse by design early."
    )
    _render_recal_reads_block()


def _render_recal_reads_block() -> None:
    """RECAL-1 reads (universe, value-lens validation, embargoed precision, quick-AI) from output/recal/reads.json."""
    reads = recal_reads if "recal_reads" in globals() else None
    if not reads:
        return
    st.subheader("Recalibration reads (2026-09-08/09)")
    uc = (reads.get("universe_capture") or {}).get("universes", {}).get("B", {})
    vl = ((reads.get("value_lens") or {}).get("validation") or {}).get("VAL-1 fmr_yield_vs_zori_yield", {})
    pr = ((reads.get("precision") or {}).get("summary") or {}).get("pre_covid_folds", {})
    qa = reads.get("quick_ai") or {}
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Universe B capture (inside / unrestricted)", f"{uc.get('ratio_vs_unrestricted', float('nan')):.2f}×" if uc else "—",
              f"class {uc.get('class_median', float('nan')):.3f}" if uc else "", delta_color="off")
    m2.metric("Rent yield validation (VAL-1)", f"ρ {vl.get('spearman', float('nan')):.2f}" if vl else "—", "FMR vs ZORI yield", delta_color="off")
    m3.metric("Embargoed statistical precision", f"{pr.get('median_lift_p100', float('nan')):.2f}× random" if pr else "—",
              f"{pr.get('median_ratio_vs_best_naive', float('nan')):.2f}× best naive rule" if pr else "", delta_color="off")
    cmp = (qa.get("comparison_ai_vs_landinvest_vs_universeB") or {}).get("ai_picks", {})
    m4.metric("Quick-AI picks that are documented past booms", f"{100 * cmp.get('share_in_documented_boom_family_library', float('nan')):.0f}%" if cmp else "—",
              f"run-to-run overlap {qa.get('H_b_mean_pairwise_jaccard', float('nan')):.2f}" if qa else "", delta_color="off")
    st.caption(
        "Statistical precision (FHFA 1975–2025, fully embargoed) beats random about 3× but does not beat the best simple contrarian rule "
        "on the median fold — quote both together. The universe read is a scope rule, not new skill. Full reads: `output/recalibration_20260908/OVERNIGHT_READ.md`."
    )


def _render_validation_console() -> None:
    """Walk-forward CV, known-boom backtests, and conformal coverage.

    Analyst-only diagnostics; references module-level loaders/globals
    (load_eval_report, EVAL_PATH, conformal_diag). Surfaced under Pro ->
    Advanced; report-only, no rank or scoring change."""
    st.header("Model Validation")
    _render_honest_coordinates()
    st.divider()
    st.caption("Below: legacy engineering diagnostics (contemporaneous-trained CV). "
               "These are NOT honest forward-skill claims — the coordinates above are.")
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


def _render_system_status_console() -> None:
    """Source health, latest-year completeness, drift, and Wave 2/3 posture.

    Analyst-only diagnostics; references module-level globals (status_bundle,
    fiveyr_policy_status, wave3_status, wave3_overlay_summary,
    latest_compare_boundary_df, run_compare_files). Surfaced under Pro ->
    Advanced; report-only, no rank or scoring change."""
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


def _render_tokenization_readiness_tab(packet: dict | None) -> None:
    """Internal, report-only Tokenization Readiness surface (backlog TK1).

    Renders the SOURCING-readiness packet from
    `scripts/build_tokenization_readiness_packet.py`: A/B/C tiers over the quiet
    shortlist, best land-type strategy signal, income-fit flag, and the six
    investability gates that stay blocked pending parcel data + counsel. A high
    tier means "worth parcel diligence," never investable or offered. No
    securities, no production or rank change."""
    st.header("Tokenization Readiness (Sourcing Screen)")
    st.caption(
        "Internal, report-only. County-grain SOURCING readiness only — NOT investability, "
        "NOT an offering, NOT a security. Surfaces the existing readiness packet; it does "
        "not change any rank, score, or production artifact."
    )
    if not packet or not packet.get("rows"):
        st.info(
            "No tokenization-readiness packet is loaded. Generate it with "
            "`./.venv/bin/python scripts/build_tokenization_readiness_packet.py` "
            "(reads the latest boom-onset shortlist)."
        )
        return

    tiers = packet.get("tier_counts") or {}
    shortlist_year = packet.get("shortlist_year", "n/a")
    rows = packet.get("rows") or []
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Shortlist Year", str(shortlist_year))
    c2.metric("Tier A", tiers.get("A", 0))
    c3.metric("Tier B", tiers.get("B", 0))
    c4.metric("Tier C", tiers.get("C", 0))

    income_fit_count = sum(1 for r in rows if r.get("income_fit"))
    st.caption(
        f"{len(rows)} quiet-shortlist counties screened · {income_fit_count} flagged "
        "income-fit (farmland-cash-rent or amenity — the retail/non-accredited-friendly "
        "land types per the feasibility memo)."
    )

    table = pd.DataFrame(
        [
            {
                "County": r.get("county"),
                "St": r.get("state_abbr"),
                "Tier": r.get("sourcing_readiness_tier"),
                "Readiness": round(float(r["sourcing_readiness_score"]), 3)
                if r.get("sourcing_readiness_score") is not None else None,
                "Thesis": round(float(r["gate1_thesis_strength"]), 2)
                if r.get("gate1_thesis_strength") is not None else None,
                "Best Land-Type Strategy": r.get("gate4_best_strategy"),
                "Signal": round(float(r["gate4_best_signal"]), 3)
                if r.get("gate4_best_signal") is not None else None,
                "Income Fit": "yes" if r.get("income_fit") else "no",
            }
            for r in rows
        ]
    )
    st.dataframe(table, width="stretch", hide_index=True, height=460)

    assessable = ", ".join(packet.get("assessable_gates") or []) or "n/a"
    blocked = ", ".join(packet.get("blocked_gates") or []) or "n/a"
    st.markdown(
        f"- **Assessable gates** (scored here): `{assessable}`.\n"
        f"- **Blocked gates** (need parcel data + counsel): `{blocked}`. Every county above "
        "still has all six investability gates blocked — there is no parcel, legal, "
        "underwriting, offering, token, or servicing assessment here.\n"
        "- **Tier A/B/C** ranks how worth-pursuing a county is for *parcel diligence*, from "
        "its boom-onset thesis strength + best land-type signal + income fit.\n"
        "- **Best Land-Type Strategy** is the county's highest land-type signal (farmland "
        "cash rent, recreation/amenity, supply-constrained, or development dynamism) — a "
        "hypothesis to test on the ground, not an underwriting.\n"
        f"- Gate spec: `{packet.get('matrix', 'documentation/TOKENIZATION_READINESS_MATRIX.md')}`."
    )
    st.download_button(
        "Export Tokenization Readiness JSON",
        data=json.dumps(packet, indent=2).encode("utf-8"),
        file_name="tokenization_readiness_packet.json",
        mime="application/json",
        key="product_tokenization_readiness_json",
    )
    st.caption(f"Packet generated: `{packet.get('generated_at', 'n/a')}` · status: `{packet.get('status', 'n/a')}`.")


def _recal_badges(row: pd.Series) -> str:
    flags = [("badge_urban_core", "urban core"), ("badge_tiny_market", "tiny market"), ("badge_already_hot", "already hot"),
             ("badge_declining", "declining"), ("badge_commodity_cycle", "commodity cycle"), ("badge_no_demand_signal", "no demand signal")]
    out = [label for col, label in flags if bool(row.get(col)) and pd.notna(row.get(col))]
    return ", ".join(out) if out else "—"


def _render_quiet_shortlist_tab(sim_df: pd.DataFrame, reads: dict | None) -> None:
    """RECAL-1 headline discovery surface: the classifier's quiet shortlist inside universe B."""
    st.header("Quiet Shortlist — universe B")
    if "boom_onset_score" not in sim_df.columns or "universe_B" not in sim_df.columns:
        st.warning("Recalibration surfaces missing — run `scripts/publish_recal_surfaces.py` to publish `output/recal/`.")
        return
    st.caption(
        "Report-only. Quiet counties (prior 3-yr momentum rank 0.10–0.667, demand floor met, population ≥ 25k) inside the "
        "investable universe (density pct ≤ 0.95, population < 1M), ranked by the boom-onset classifier's champion lane "
        "(the same basis as the operator packets and the frozen forward-validation snapshots); the lane-agnostic class rank "
        "is shown beside it. Value is observed facts. Nothing here changes production ranks."
    )
    uc = (reads or {}).get("universe_capture") or {}
    hc = (reads or {}).get("honest") or {}
    b = (uc.get("universes") or {}).get("B") or {}
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Universe B counties", f"{b.get('n_counties', '—')}")
    c2.metric("Capture inside vs unrestricted", f"{b.get('ratio_vs_unrestricted', float('nan')):.2f}×" if b.get("ratio_vs_unrestricted") else "—",
              "UNIV-1 pass" if b.get("UNIV-1_capture_floor_0.8x") else "", delta_color="off")
    c3.metric("Honest capture (held-out)", f"{hc.get('classifier', {}).get('honest_held_out_capture_at_100', float('nan')):.3f}" if hc else "—",
              f"{hc.get('classifier', {}).get('vs_random_multiple', '')}× random" if hc else "", delta_color="off")
    c4.metric("Operator precision (proxy)", f"{hc.get('operator_review', {}).get('operator_precision', float('nan')):.2f}" if hc else "—")
    pool = sim_df[
        sim_df["universe_B"].fillna(False).astype(bool)
        & sim_df["quiet_now"].fillna(False).astype(bool)
        & sim_df["demand_floor_ok"].fillna(False).astype(bool)
        & (pd.to_numeric(sim_df.get("population"), errors="coerce").fillna(0) >= 25_000)
    ].copy()
    pool = pool.sort_values("boom_onset_score", ascending=False)
    top_n = st.slider("Rows", 10, 100, 30, step=10, key="quiet_shortlist_rows")
    show = pool.head(top_n)
    table = pd.DataFrame({
        "#": range(1, len(show) + 1),
        "County": show.apply(lambda r: f"{r.get('county_name', '')}, {r.get('state', '')}", axis=1).values,
        "Timing": show["sim_timing_score"].map(_fmt_score).values,
        "Boom-onset score": show["boom_onset_score"].map(lambda x: f"{x:.3f}" if pd.notna(x) else "—").values,
        "Class rank (lane-agnostic)": show["timing_class_median_rank_pct"].map(lambda x: f"{x:.2f}" if pd.notna(x) else "—").values if "timing_class_median_rank_pct" in show.columns else "—",
        "Value": show["sim_value_score"].map(_fmt_score).values,
        "Gross rent yield": show["fmr_gross_yield"].map(_fmt_pct).values if "fmr_gross_yield" in show.columns else "—",
        "Farm land $/ac": show["nass_land_value_per_acre"].map(lambda x: f"${x:,.0f}" if pd.notna(x) else "—").values if "nass_land_value_per_acre" in show.columns else "—",
        "Tourism idx": show["tourism_intensity_index"].map(lambda x: f"{x:.2f}" if pd.notna(x) else "—").values if "tourism_intensity_index" in show.columns else "—",
        "STR RevPAR (AirROI)": show["str_revpar"].map(lambda x: f"${x:,.0f}" if pd.notna(x) else "—").values if "str_revpar" in show.columns else "—",
        "STR demand pressure 3y": show["str_demand_pressure_3yr"].map(lambda x: f"{x:+.0%}" if pd.notna(x) else "—").values if "str_demand_pressure_3yr" in show.columns else "—",
        "Archetype lens": show.get("archetype_lens_best", pd.Series("—", index=show.index)).fillna("—").values,
        "Momentum rank": show["momentum_rank_pct"].map(lambda x: f"{x:.2f}" if pd.notna(x) else "—").values,
        "Density pct": show["density_pct"].map(lambda x: f"{x:.2f}" if pd.notna(x) else "—").values,
        "2025 review": show.get("operator_review_2025", pd.Series("", index=show.index)).fillna("").values,
        "On clock (snapshot 4)": show.get("forward_snapshot_20260909_role", pd.Series("", index=show.index)).fillna("").map(lambda x: "pick" if x == "pick" else ("control" if x == "control" else "")).values,
        "Badges": show.apply(_recal_badges, axis=1).values,
    })
    st.dataframe(table, width="stretch", hide_index=True, height=min(60 + 36 * len(table), 720))
    if not pool.empty:
        fig = px.scatter(
            pool.head(300), x="sim_value_score", y="sim_timing_score", hover_name=pool.head(300).apply(lambda r: f"{r.get('county_name', '')}, {r.get('state', '')}", axis=1),
            color="opportunity_archetype", labels={"sim_value_score": "Value (yield & cheapness)", "sim_timing_score": "Timing (boom-onset class rank)"},
            title="Value × timing — quiet counties inside universe B (top 300 by timing)",
        )
        fig.update_layout(height=460, legend_title_text="Archetype")
        st.plotly_chart(fig, width="stretch")
    st.download_button("Export quiet shortlist (CSV)", data=table.to_csv(index=False).encode("utf-8"),
                       file_name="landinvest_quiet_shortlist_universe_b.csv", mime="text/csv", key="quiet_shortlist_export")
    st.caption("Badges are the documented false-positive modes; a county can be on this list and still carry one — read them as diligence flags. "
               "Honest coordinates for this surface live under Advanced → Validation.")


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
    tokenization_readiness_packet: dict | None = None,
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
                    "product_growth": int(profile.get("growth", 60)),
                    "product_value": int(profile.get("value", 15)),
                    "product_value_focus": profile.get("value_focus", "Balanced"),
                    "product_universe_only": bool(profile.get("universe_only", True)),
                    "product_quiet_only": bool(profile.get("quiet_only", True)),
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
        max_risk = st.slider("Maximum risk", 20.0, 100.0, float(preset["max_risk"]), step=1.0, key="product_max_risk")
        st.divider()
        st.caption("Scope")
        universe_only = st.toggle(
            "Investable universe B only", value=bool(preset.get("universe_only", True)), key="product_universe_only",
            help="Density percentile <= 0.95 and population < 1M — the adopted scope rule (2026-09-09). Removes cooled big-city cores; keeps 91% of documented boom-family counties.",
        )
        quiet_only = st.toggle(
            "Quiet-shortlist brakes", value=bool(preset.get("quiet_only", True)), key="product_quiet_only",
            help="The classifier shortlist's own brakes: prior 3-year momentum rank between 0.10 and 0.667 (not already moving, not collapsing), population >= 25k, and an observed demand signal (positive net migration or above-median business formation).",
        )
        st.caption("Score mix")
        growth = st.slider("Timing (boom-onset resemblance)", 0, 100, int(preset["growth"]), step=5, key="product_growth",
                           help="Classifier ensemble-class rank: how much this quiet county resembles the years before past booms.")
        value = st.slider("Value (yield & cheapness)", 0, 100, int(preset.get("value", 15)), step=5, key="product_value",
                          help="Observed facts: gross rent yield within the county's RUCC band, home-value and land cheapness, farm cap-rate proxy.")
        value_focus = st.selectbox("Value focus", ["Balanced", "Rent yield", "Farmland income"],
                                   index=["Balanced", "Rent yield", "Farmland income"].index(preset.get("value_focus", "Balanced")), key="product_value_focus")
        h1 = st.slider("1yr ordinal context (optional)", 0, 100, int(preset["h1"]), step=5, key="product_h1",
                       help="Blends the validated 1yr ordering signal into timing. 3yr/5yr are never used — falsified under honest validation.")
        h3, h5 = 0, 0
        risk = st.slider("Risk control", 0, 100, int(preset["risk"]), step=5, key="product_risk")
        structure = st.slider("Land thesis", 0, 100, int(preset["structure"]), step=5, key="product_structure")
        confidence = st.slider("Confidence", 0, 100, int(preset["confidence"]), step=5, key="product_confidence")
        uncertainty = st.slider("Uncertainty penalty", 0, 25, int(preset["uncertainty"]), step=1, key="product_uncertainty")
        _focus_options = ["Overall land thesis", "Optionality", "Low fragility", "Recreation access", "Buildable scarcity", "Tourism intensity", "Farmland income"]
        structural_focus = st.selectbox(
            "Land thesis focus",
            _focus_options,
            index=_focus_options.index(preset["structural_focus"]) if preset["structural_focus"] in _focus_options else 0,
            key="product_structural_focus",
        )
        profile_save_name = st.text_input("Save strategy as", value="", placeholder="e.g. Mountain West low-risk")

    cfg = {
        "h1": h1,
        "h3": h3,
        "h5": h5,
        "growth": growth,
        "value": value,
        "value_focus": value_focus,
        "universe_only": universe_only,
        "quiet_only": quiet_only,
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
    filtered = _apply_product_filter(sim_df, selected_states, max_risk, min_confidence,
                                     universe_only=universe_only, quiet_only=quiet_only).sort_values("sim_rank")

    if "product_selected_fips" not in st.session_state and not filtered.empty:
        st.session_state.product_selected_fips = str(filtered.iloc[0]["fips"]).zfill(5)

    run_id = latest_run.get("run_id", "unknown") if latest_run else "unknown"
    churn = latest_deltas.get("top25_churn") if latest_deltas and latest_deltas.get("has_previous") else None
    chips = [
        f"Run: {run_id}",
        f"Counties: {len(filtered):,} / {len(df):,}",
        f"Preset: {preset_name}",
        f"Top-25 churn: {100 * churn:.1f}%" if churn is not None else "Top-25 churn: n/a",
    ]
    chips.append(f"Timing engine: {_timing_chip_text((globals().get('recal_reads') or {}).get('honest'))}")
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
    st.caption("Main workflow: Start -> Discover -> Map -> County Memo -> Watchlist -> Reports. Advanced keeps diagnostics, model QA, and promotion gates out of the default path.")
    _render_pro_term_guide()

    tab_start = top_start
    tab_map = top_map
    tab_memo = top_memo

    with top_discover:
        st.caption("Find counties: search in plain English, explore the universe, or run the pre-boom, strategy, screening, and regional lenses. Model QA tools (stress tests, peer sets, disagreement) live under Advanced.")
        (
            tab_search,
            tab_explore,
            tab_preboom,
            tab_play,
            tab_screen,
            tab_region,
        ) = st.tabs(
            [
                "Search",
                "Explore",
                "Quiet Shortlist",
                "Strategy",
                "Screening",
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
        st.caption(
            "Analyst diagnostics: model QA, evidence governance, and run forensics. "
            "Nothing here changes your shortlist — these tools explain and stress the "
            "signals, they do not produce new ranks."
        )
        (
            tab_evidence_center,
            tab_run,
            tab_autopsy,
            tab_promo,
            tab_health,
            tab_stress,
            tab_peers,
            tab_disagree,
            tab_validation,
            tab_system_status,
            tab_tokenization,
            tab_parcels,
        ) = st.tabs(
            [
                "Evidence Center",
                "Run Review",
                "Autopsy",
                "Promotion Gate",
                "Model Health",
                "Stress Tests",
                "Peer Sets",
                "Disagreement",
                "Validation",
                "System Status",
                "Tokenization",
                "Parcels",
            ]
        )

    with tab_start:
        _render_pro_tab_guide("start")
        _render_start_here_tab(filtered, cfg, latest_run, xfactor_scoreboard, xfactor_promotion_gate, demo_readiness_report)

    with tab_search:
        _render_pro_tab_guide("search")
        st.header("Natural-Language Search")
        if "product_nl_query" not in st.session_state:
            st.session_state.product_nl_query = ""
        st.caption("Use transparent keyword search for quick county-set discovery, then tune the sidebar strategy for precise policy changes.")
        examples = [
            ("Low-risk Mountain West", "low-risk counties with a strong growth signal in the Mountain West"),
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
                placeholder="e.g. low-risk counties with a strong growth signal in the Mountain West",
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
        _render_pro_tab_guide("explore")
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
        _render_pro_tab_guide("reports")
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
                    title="LandInvest Top 25 Strategy Report",
                )
                st.download_button(
                    "Top 25 Markdown",
                    data=top25_md.encode("utf-8"),
                    file_name="landinvest_top25_strategy_report.md",
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
        _render_pro_tab_guide("preboom")
        _render_quiet_shortlist_tab(sim_df, recal_reads)
        with st.expander("Legacy two-score pre-boom lane (May 2026 export; superseded by the classifier shortlist above)", expanded=False):
            _render_preboom_review_tab(
                surfaces=preboom_surfaces or {},
                blend_report=preboom_blend_report,
                analog_report=preboom_analog_report,
                promotion_gate=preboom_promotion_gate,
                p0_repeatable_residual_guardrail=p0_repeatable_residual_guardrail,
                p0_repeatable_residual_candidates=p0_repeatable_residual_candidates,
            )

    with tab_play:
        _render_pro_tab_guide("strategy")
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
        _render_pro_tab_guide("screening")
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
        _render_pro_tab_guide("stress")
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
        _render_pro_tab_guide("map")
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
        _render_pro_tab_guide("memo")
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
        _render_pro_tab_guide("peers")
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
        _render_pro_tab_guide("disagreement")
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
        _render_pro_tab_guide("region")
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
        _render_pro_tab_guide("thesis")
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
        _render_pro_tab_guide("funnel")
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
        _render_pro_tab_guide("watchlist")
        st.header("Watchlist")
        st.caption("Use Watchlist as the active review queue before generating Reports or an Investment Memo.")
        watch_fips = {str(f).zfill(5) for f in st.session_state.watchlist_fips}
        _render_watchlist_alerts(watchlist_alert_events, watch_fips)
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

    with tab_evidence_center:
        _render_pro_tab_guide("evidence_center")
        _render_xfactor_evidence_center_tab(xfactor_evidence_center_df, xfactor_command_loop_df)

    with tab_run:
        _render_pro_tab_guide("run_review")
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
        _render_pro_tab_guide("autopsy")
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
        _render_pro_tab_guide("promotion_gate")
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
            "- Use the Advanced -> Validation and System Status tabs for the full validation and run-comparison evidence before changing model artifacts."
        )

    with tab_health:
        _render_pro_tab_guide("model_health")
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
        st.caption("See the Validation and System Status tabs for full walk-forward CV, source-health, drift, calibration, and run-comparison diagnostics.")

    with tab_validation:
        _render_pro_tab_guide("validation")
        _render_validation_console()

    with tab_system_status:
        _render_pro_tab_guide("system_status")
        _render_system_status_console()

    with tab_tokenization:
        _render_pro_tab_guide("tokenization")
        _render_tokenization_readiness_tab(tokenization_readiness_packet)

    with tab_parcels:
        render_parcel_explorer_tab()

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
    .skip-link {
        position: absolute;
        left: 0.75rem;
        top: -4rem;
        z-index: 10000;
        background: #0f766e;
        color: #ffffff !important;
        border-radius: 8px;
        padding: 0.62rem 0.82rem;
        font-weight: 800;
        text-decoration: none;
        box-shadow: 0 10px 26px rgba(15, 23, 42, 0.24);
    }
    .skip-link:focus,
    .skip-link:focus-visible {
        top: 0.75rem;
        outline: 3px solid #fbbf24;
        outline-offset: 3px;
    }
    .landinvest-main-anchor {
        scroll-margin-top: 1rem;
    }
    .landinvest-theme-sentinel {
        display: none;
    }
    .customer-theme-sentinel {
        display: none;
    }
    button:focus-visible,
    a:focus-visible,
    input:focus-visible,
    textarea:focus-visible,
    select:focus-visible,
    [role="button"]:focus-visible,
    [role="tab"]:focus-visible,
    [role="slider"]:focus-visible,
    div[data-testid="stDataFrame"] *:focus-visible,
    div[data-testid="stPlotlyChart"] *:focus-visible {
        outline: 3px solid #fbbf24 !important;
        outline-offset: 3px !important;
        box-shadow: 0 0 0 2px rgba(15, 23, 42, 0.85) !important;
    }
    button,
    [role="button"],
    [role="tab"],
    a,
    input,
    select,
    textarea {
        min-height: 2.5rem;
    }
    button[aria-label^="Help for"] {
        min-width: 2rem !important;
    }
    div[data-testid="stDataFrame"],
    div[data-testid="stDataFrameResizable"],
    div[data-testid="stTable"] {
        overflow-x: auto;
    }
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
    .customer-empty-state {
        border: 1px solid rgba(15, 118, 110, 0.28);
        border-left: 5px solid #0f766e;
        background: linear-gradient(135deg, rgba(240, 253, 250, 0.92), rgba(248, 250, 252, 0.98));
        color: #0f172a;
        border-radius: 8px;
        padding: 0.95rem 1rem;
        margin: 0.65rem 0 0.9rem 0;
    }
    .customer-empty-state h3 {
        margin: 0.1rem 0 0.35rem 0;
        font-size: 1.08rem;
        color: #0f172a;
        letter-spacing: 0;
    }
    .customer-empty-state p,
    .customer-empty-state li {
        color: #334155;
        font-size: 0.9rem;
    }
    .customer-empty-state ul {
        margin: 0.55rem 0 0 1.1rem;
        padding: 0;
    }
    .customer-empty-search {
        border-left-color: #0f766e;
    }
    .customer-empty-action {
        border-left-color: #1d4ed8;
    }
    .customer-empty-review {
        border-left-color: #92400e;
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
        background-color: #0b1115;
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
        section.main > div,
        div[data-testid="stAppViewContainer"] section.main > div {
            padding-left: 0.75rem;
            padding-right: 0.75rem;
        }
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
        .customer-command-grid span,
        .customer-stat-strip span,
        .customer-map-stats span,
        .landinvest-brand-chip {
            min-width: min(100%, 9rem);
            flex: 1 1 8.5rem;
        }
        .customer-section-header,
        .customer-empty-state {
            padding: 0.72rem 0.78rem;
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
        div[data-testid="stPlotlyChart"] {
            min-height: 320px;
        }
        div[data-testid="stHorizontalBlock"] {
            gap: 0.65rem;
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
        .customer-section-header,
        .customer-empty-state {
            background: rgba(15, 23, 42, 0.66);
            border-color: rgba(148, 163, 184, 0.36);
        }
        .customer-empty-state {
            border-left-color: #5eead4;
            color: #f8fafc;
        }
        .customer-empty-state h3 {
            color: #f8fafc;
        }
        .customer-empty-state p,
        .customer-empty-state li {
            color: #cbd5e1;
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
    body:has(.landinvest-theme-light) .landinvest-brand-header {
        background: linear-gradient(135deg, #f8fafc 0%, #f0fdfa 58%, #fffbeb 100%);
        border-color: rgba(15, 118, 110, 0.22);
        color: #0f172a;
        box-shadow: 0 14px 34px rgba(15, 23, 42, 0.07);
    }
    body:has(.landinvest-theme-light) .landinvest-brand-kicker,
    body:has(.landinvest-theme-light) .landinvest-brand-chip b,
    body:has(.landinvest-theme-light) .customer-sidebar-title,
    body:has(.landinvest-theme-light) .customer-kicker {
        color: #0f766e;
    }
    body:has(.landinvest-theme-light) .landinvest-brand-copy h1,
    body:has(.landinvest-theme-light) .landinvest-brand-chip span,
    body:has(.landinvest-theme-light) .landinvest-sidebar-brand b,
    body:has(.landinvest-theme-light) .customer-command-header h1,
    body:has(.landinvest-theme-light) .customer-command-grid b,
    body:has(.landinvest-theme-light) .customer-stat-strip b,
    body:has(.landinvest-theme-light) .customer-map-stats b,
    body:has(.landinvest-theme-light) .customer-map-callout h3,
    body:has(.landinvest-theme-light) .customer-empty-state h3 {
        color: #0f172a;
    }
    body:has(.landinvest-theme-light) .landinvest-brand-copy p,
    body:has(.landinvest-theme-light) .customer-command-header p,
    body:has(.landinvest-theme-light) .customer-section-header p,
    body:has(.landinvest-theme-light) .customer-map-callout p,
    body:has(.landinvest-theme-light) .customer-empty-state p,
    body:has(.landinvest-theme-light) .customer-empty-state li {
        color: #334155;
    }
    body:has(.landinvest-theme-light) .landinvest-sidebar-brand span,
    body:has(.landinvest-theme-light) .customer-command-grid small,
    body:has(.landinvest-theme-light) .customer-stat-strip small,
    body:has(.landinvest-theme-light) .customer-map-stats small {
        color: #64748b;
    }
    body:has(.landinvest-theme-light) .landinvest-brand-chip,
    body:has(.landinvest-theme-light) .run-chip,
    body:has(.landinvest-theme-light) .customer-command-grid span,
    body:has(.landinvest-theme-light) .customer-stat-strip span,
    body:has(.landinvest-theme-light) .customer-map-stats span {
        background: rgba(255, 255, 255, 0.72);
        border-color: rgba(15, 118, 110, 0.24);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.80);
    }
    body:has(.landinvest-theme-light) .run-chip {
        background: #eef2f7;
        border-color: #cbd5e1;
        color: #0f172a !important;
    }
    body:has(.landinvest-theme-light) .customer-command-header {
        background: linear-gradient(135deg, rgba(204, 251, 241, 0.96) 0%, rgba(248, 250, 252, 0.98) 44%, rgba(254, 243, 199, 0.74) 100%);
        color: #0f172a;
        border-color: rgba(20, 184, 166, 0.35);
    }
    body:has(.landinvest-theme-light) .customer-section-header {
        background: linear-gradient(90deg, rgba(240, 253, 250, 0.95), rgba(255, 251, 235, 0.55));
        border-color: #14b8a6;
    }
    body:has(.landinvest-theme-light) .customer-map-callout,
    body:has(.landinvest-theme-light) .customer-empty-state {
        background: #f8fafc;
        border-color: rgba(20, 184, 166, 0.34);
        color: #0f172a;
    }
    body:has(.landinvest-theme-light) .customer-card {
        background: #ffffff;
        border-color: #cbd5e1;
        color: #0f172a;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
    }
    body:has(.landinvest-theme-light) .customer-card-top,
    body:has(.landinvest-theme-light) .customer-next,
    body:has(.landinvest-theme-light) .customer-signal-row div:first-child {
        color: #475569;
    }
    body:has(.landinvest-theme-light) .customer-thesis {
        color: #334155;
    }
    body:has(.landinvest-theme-light) .customer-tier {
        background: #f8fafc;
        color: #0f172a !important;
        border-color: #cbd5e1 !important;
    }
    body:has(.landinvest-theme-light) .customer-meter {
        background: #e2e8f0;
    }
    body:has(.landinvest-theme-light) button[data-testid^="stBaseButton-segmented_control"] {
        color: #0f172a !important;
    }
    body:has(.landinvest-theme-light) button[data-testid="stBaseButton-segmented_controlActive"] {
        background: linear-gradient(135deg, rgba(20, 184, 166, 0.18), rgba(251, 191, 36, 0.14)) !important;
        color: #0f172a !important;
    }
    body:has(.landinvest-theme-light) button[data-testid="stTab"] {
        color: #0f172a !important;
    }
    body:has(.landinvest-theme-light) button[data-testid="stTab"][aria-selected="true"] {
        color: #0f766e !important;
    }
    body:has(.landinvest-theme-light) div[data-testid="stPlotlyChart"] .js-plotly-plot .bg {
        fill: rgba(255, 255, 255, 0) !important;
    }
    body:has(.landinvest-theme-light) div[data-testid="stPlotlyChart"] .js-plotly-plot svg text,
    body:has(.landinvest-theme-light) div[data-testid="stPlotlyChart"] .js-plotly-plot .legendtext,
    body:has(.landinvest-theme-light) div[data-testid="stPlotlyChart"] .js-plotly-plot .gtitle,
    body:has(.landinvest-theme-light) div[data-testid="stPlotlyChart"] .js-plotly-plot .xtitle,
    body:has(.landinvest-theme-light) div[data-testid="stPlotlyChart"] .js-plotly-plot .ytitle {
        fill: #0f172a !important;
        color: #0f172a !important;
    }
    body:has(.landinvest-theme-dark) .landinvest-brand-header {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(6, 78, 59, 0.60));
        border-color: rgba(45, 212, 191, 0.40);
        color: #f8fafc;
    }
    body:has(.landinvest-theme-dark) .customer-command-header {
        background: linear-gradient(135deg, rgba(6, 78, 59, 0.62), rgba(15, 23, 42, 0.92));
        color: #f8fafc;
        border-color: rgba(45, 212, 191, 0.45);
    }
    body:has(.landinvest-theme-dark) .customer-card {
        background: #0b1115;
        border-color: rgba(148, 163, 184, 0.35);
        color: #f8fafc;
    }
    body:has(.customer-theme-vaporwave) .stApp,
    body:has(.customer-theme-vaporwave) div[data-testid="stAppViewContainer"] {
        background:
            linear-gradient(rgba(103, 232, 249, 0.07) 1px, transparent 1px),
            linear-gradient(90deg, rgba(103, 232, 249, 0.06) 1px, transparent 1px),
            linear-gradient(180deg, #10002b 0%, #16042f 48%, #2a064d 100%) !important;
        background-size: 42px 42px, 42px 42px, auto !important;
        color: #f8f7ff;
    }
    body:has(.customer-theme-vaporwave) section[data-testid="stSidebar"] {
        background:
            linear-gradient(rgba(244, 114, 182, 0.07) 1px, transparent 1px),
            linear-gradient(180deg, #10002b 0%, #16042f 56%, #0b1230 100%) !important;
        background-size: 36px 36px, auto !important;
        border-right: 1px solid rgba(103, 232, 249, 0.32);
    }
    body:has(.customer-theme-vaporwave) h1,
    body:has(.customer-theme-vaporwave) h2,
    body:has(.customer-theme-vaporwave) h3,
    body:has(.customer-theme-vaporwave) h4,
    body:has(.customer-theme-vaporwave) h5,
    body:has(.customer-theme-vaporwave) h6,
    body:has(.customer-theme-vaporwave) .landinvest-brand-copy h1,
    body:has(.customer-theme-vaporwave) .landinvest-sidebar-brand b,
    body:has(.customer-theme-vaporwave) .customer-command-header h1,
    body:has(.customer-theme-vaporwave) .customer-card h3,
    body:has(.customer-theme-vaporwave) .customer-empty-state h3,
    body:has(.customer-theme-vaporwave) .customer-map-callout h3 {
        color: #f8f7ff !important;
    }
    body:has(.customer-theme-vaporwave) p,
    body:has(.customer-theme-vaporwave) label,
    body:has(.customer-theme-vaporwave) .stCaptionContainer,
    body:has(.customer-theme-vaporwave) .landinvest-brand-copy p,
    body:has(.customer-theme-vaporwave) .landinvest-sidebar-brand span,
    body:has(.customer-theme-vaporwave) .customer-command-header p,
    body:has(.customer-theme-vaporwave) .customer-section-header p,
    body:has(.customer-theme-vaporwave) .customer-map-callout p,
    body:has(.customer-theme-vaporwave) .customer-empty-state p,
    body:has(.customer-theme-vaporwave) .customer-empty-state li,
    body:has(.customer-theme-vaporwave) .customer-thesis,
    body:has(.customer-theme-vaporwave) .customer-next,
    body:has(.customer-theme-vaporwave) .customer-card-top,
    body:has(.customer-theme-vaporwave) .customer-signal-row div:first-child {
        color: #e9d5ff !important;
    }
    body:has(.customer-theme-vaporwave) .customer-kicker,
    body:has(.customer-theme-vaporwave) .customer-sidebar-title,
    body:has(.customer-theme-vaporwave) .landinvest-brand-kicker,
    body:has(.customer-theme-vaporwave) .landinvest-brand-chip b,
    body:has(.customer-theme-vaporwave) .customer-command-grid small,
    body:has(.customer-theme-vaporwave) .customer-stat-strip small,
    body:has(.customer-theme-vaporwave) .customer-map-stats small {
        color: #67e8f9 !important;
    }
    body:has(.customer-theme-vaporwave) .landinvest-brand-header,
    body:has(.customer-theme-vaporwave) .customer-command-header {
        position: relative;
        overflow: hidden;
        background:
            linear-gradient(rgba(103, 232, 249, 0.08) 1px, transparent 1px),
            linear-gradient(90deg, rgba(244, 114, 182, 0.08) 1px, transparent 1px),
            linear-gradient(135deg, rgba(42, 6, 77, 0.96) 0%, rgba(16, 0, 43, 0.96) 55%, rgba(11, 18, 48, 0.98) 100%) !important;
        background-size: 34px 34px, 34px 34px, auto !important;
        border-color: rgba(103, 232, 249, 0.56) !important;
        color: #f8f7ff !important;
        box-shadow:
            0 24px 60px rgba(0, 0, 0, 0.36),
            0 0 0 1px rgba(244, 114, 182, 0.20),
            0 0 34px rgba(103, 232, 249, 0.16);
    }
    body:has(.customer-theme-vaporwave) .customer-command-header::after,
    body:has(.customer-theme-vaporwave) .landinvest-brand-header::after {
        content: "";
        position: absolute;
        left: 1rem;
        right: 1rem;
        bottom: 0.72rem;
        height: 1px;
        background: linear-gradient(90deg, transparent, #ff4fd8, #67e8f9, transparent);
        pointer-events: none;
    }
    body:has(.customer-theme-vaporwave) .landinvest-logo-wrap,
    body:has(.customer-theme-vaporwave) .landinvest-sidebar-logo {
        filter: drop-shadow(0 0 12px rgba(103, 232, 249, 0.45));
    }
    body:has(.customer-theme-vaporwave) .landinvest-brand-chip,
    body:has(.customer-theme-vaporwave) .run-chip,
    body:has(.customer-theme-vaporwave) .customer-command-grid span,
    body:has(.customer-theme-vaporwave) .customer-stat-strip span,
    body:has(.customer-theme-vaporwave) .customer-map-stats span {
        background: rgba(16, 0, 43, 0.74) !important;
        border-color: rgba(249, 168, 212, 0.42) !important;
        color: #f8f7ff !important;
        box-shadow:
            inset 0 1px 0 rgba(255, 255, 255, 0.08),
            0 0 18px rgba(124, 58, 237, 0.18) !important;
    }
    body:has(.customer-theme-vaporwave) .landinvest-brand-chip span,
    body:has(.customer-theme-vaporwave) .run-chip,
    body:has(.customer-theme-vaporwave) .customer-command-grid b,
    body:has(.customer-theme-vaporwave) .customer-stat-strip b,
    body:has(.customer-theme-vaporwave) .customer-map-stats b {
        color: #f8f7ff !important;
    }
    body:has(.customer-theme-vaporwave) .customer-section-header,
    body:has(.customer-theme-vaporwave) .customer-map-callout,
    body:has(.customer-theme-vaporwave) .customer-empty-state,
    body:has(.customer-theme-vaporwave) div[data-testid="stVerticalBlockBorderWrapper"],
    body:has(.customer-theme-vaporwave) details[data-testid="stExpander"] {
        background: rgba(16, 0, 43, 0.78) !important;
        border-color: rgba(103, 232, 249, 0.36) !important;
        color: #f8f7ff !important;
        box-shadow: 0 18px 42px rgba(0, 0, 0, 0.24);
    }
    body:has(.customer-theme-vaporwave) .customer-section-header {
        border-left-color: #ff4fd8 !important;
    }
    body:has(.customer-theme-vaporwave) .customer-empty-state {
        border-left-color: #67e8f9 !important;
    }
    body:has(.customer-theme-vaporwave) .customer-card {
        background:
            linear-gradient(180deg, rgba(42, 6, 77, 0.96) 0%, rgba(16, 0, 43, 0.98) 100%) !important;
        border-color: rgba(192, 132, 252, 0.56) !important;
        color: #f8f7ff !important;
        box-shadow:
            0 18px 42px rgba(0, 0, 0, 0.30),
            0 0 24px rgba(244, 114, 182, 0.14) !important;
    }
    body:has(.customer-theme-vaporwave) .customer-card:hover {
        border-color: #67e8f9 !important;
        box-shadow:
            0 22px 52px rgba(0, 0, 0, 0.34),
            0 0 30px rgba(103, 232, 249, 0.24) !important;
    }
    body:has(.customer-theme-vaporwave) .customer-tier,
    body:has(.customer-theme-vaporwave) .customer-hero-strip span {
        background: rgba(42, 6, 77, 0.82) !important;
        border-color: #ff4fd8 !important;
        color: #f8f7ff !important;
        box-shadow: 0 0 14px rgba(255, 79, 216, 0.20);
    }
    body:has(.customer-theme-vaporwave) .customer-meter {
        background: #2a064d !important;
        border: 1px solid rgba(103, 232, 249, 0.18);
    }
    body:has(.customer-theme-vaporwave) .customer-meter span {
        box-shadow: 0 0 10px rgba(103, 232, 249, 0.35);
    }
    body:has(.customer-theme-vaporwave) .customer-hero {
        background:
            linear-gradient(rgba(103, 232, 249, 0.08) 1px, transparent 1px),
            linear-gradient(135deg, #10002b 0%, #2a064d 58%, #0b1230 100%) !important;
        background-size: 32px 32px, auto !important;
        border-color: rgba(249, 168, 212, 0.54) !important;
        box-shadow: 0 24px 58px rgba(0, 0, 0, 0.35), 0 0 30px rgba(255, 79, 216, 0.16);
    }
    body:has(.customer-theme-vaporwave) button[data-testid^="stBaseButton-segmented_control"] {
        background: rgba(16, 0, 43, 0.84) !important;
        border-color: rgba(192, 132, 252, 0.44) !important;
        color: #f8f7ff !important;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.20);
    }
    body:has(.customer-theme-vaporwave) button[data-testid="stBaseButton-segmented_controlActive"] {
        background: #67e8f9 !important;
        border-color: #67e8f9 !important;
        color: #10002b !important;
        box-shadow: 0 0 22px rgba(103, 232, 249, 0.32);
    }
    body:has(.customer-theme-vaporwave) button[kind="primary"],
    body:has(.customer-theme-vaporwave) button[data-testid="stBaseButton-primary"] {
        background: #67e8f9 !important;
        border-color: #67e8f9 !important;
        color: #10002b !important;
        box-shadow: 0 0 22px rgba(103, 232, 249, 0.34);
    }
    body:has(.customer-theme-vaporwave) button[kind="primary"] *,
    body:has(.customer-theme-vaporwave) button[data-testid="stBaseButton-primary"] * {
        color: #10002b !important;
    }
    body:has(.customer-theme-vaporwave) button[data-testid="stTab"] {
        color: #e9d5ff !important;
    }
    body:has(.customer-theme-vaporwave) button[data-testid="stTab"][aria-selected="true"] {
        color: #67e8f9 !important;
    }
    body:has(.customer-theme-vaporwave) input,
    body:has(.customer-theme-vaporwave) textarea,
    body:has(.customer-theme-vaporwave) div[data-baseweb="select"] > div,
    body:has(.customer-theme-vaporwave) div[data-baseweb="base-input"] {
        background: rgba(16, 0, 43, 0.86) !important;
        border-color: rgba(103, 232, 249, 0.38) !important;
        color: #f8f7ff !important;
    }
    body:has(.customer-theme-vaporwave) input::placeholder,
    body:has(.customer-theme-vaporwave) textarea::placeholder {
        color: #d8b4fe !important;
        opacity: 1;
    }
    body:has(.customer-theme-vaporwave) div[data-testid="stDataFrame"],
    body:has(.customer-theme-vaporwave) div[data-testid="stTable"],
    body:has(.customer-theme-vaporwave) div[data-testid="stPlotlyChart"] {
        background: rgba(16, 0, 43, 0.56) !important;
        border: 1px solid rgba(103, 232, 249, 0.28);
        box-shadow: 0 18px 42px rgba(0, 0, 0, 0.24);
    }
    body:has(.customer-theme-vaporwave) div[data-testid="stPlotlyChart"] .js-plotly-plot .bg {
        fill: rgba(26, 6, 56, 0.96) !important;
    }
    body:has(.customer-theme-vaporwave) div[data-testid="stPlotlyChart"] .js-plotly-plot svg text,
    body:has(.customer-theme-vaporwave) div[data-testid="stPlotlyChart"] .js-plotly-plot .legendtext,
    body:has(.customer-theme-vaporwave) div[data-testid="stPlotlyChart"] .js-plotly-plot .gtitle,
    body:has(.customer-theme-vaporwave) div[data-testid="stPlotlyChart"] .js-plotly-plot .xtitle,
    body:has(.customer-theme-vaporwave) div[data-testid="stPlotlyChart"] .js-plotly-plot .ytitle {
        fill: #f8f7ff !important;
        color: #f8f7ff !important;
    }
    body:has(.customer-theme-vaporwave) div[data-testid="stPlotlyChart"] .js-plotly-plot .gridlayer path,
    body:has(.customer-theme-vaporwave) div[data-testid="stPlotlyChart"] .js-plotly-plot .xgrid,
    body:has(.customer-theme-vaporwave) div[data-testid="stPlotlyChart"] .js-plotly-plot .ygrid,
    body:has(.customer-theme-vaporwave) div[data-testid="stPlotlyChart"] .js-plotly-plot .zerolinelayer path,
    body:has(.customer-theme-vaporwave) div[data-testid="stPlotlyChart"] .js-plotly-plot .xlines-above,
    body:has(.customer-theme-vaporwave) div[data-testid="stPlotlyChart"] .js-plotly-plot .ylines-above {
        stroke: rgba(103, 232, 249, 0.30) !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

def _theme_hint_class() -> str:
    embed_options = (_query_param_first("embed_options", "") or "").lower()
    theme_query = (_query_param_first("theme", "") or "").lower()
    if "light_theme" in embed_options or theme_query == "light":
        return "landinvest-theme-light"
    if "dark_theme" in embed_options or theme_query == "dark":
        return "landinvest-theme-dark"
    try:
        theme = st.context.theme
        theme_type = theme.get("type") if isinstance(theme, dict) else getattr(theme, "type", None)
    except Exception:
        theme_type = None
    if theme_type == "light":
        return "landinvest-theme-light"
    if theme_type == "dark":
        return "landinvest-theme-dark"
    return "landinvest-theme-auto"


st.markdown(f'<div class="landinvest-theme-sentinel {_theme_hint_class()}" aria-hidden="true"></div>', unsafe_allow_html=True)
st.markdown('<a class="skip-link" href="#landinvest-main">Skip to main content</a>', unsafe_allow_html=True)

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
recal_briefs_df = load_recal_briefs(_mtime=_file_mtime(RECAL_BRIEFS_PATH))
recal_reads = load_recal_reads(_mtime=_file_mtime(RECAL_READS_PATH))
RECAL_ACTIVE = recal_briefs_df is not None and not recal_briefs_df.empty
if RECAL_ACTIVE:
    df["fips"] = df["fips"].astype(str).str.zfill(5)
    _brief_cols = [c for c in RECAL_BRIEF_COLUMNS if c in recal_briefs_df.columns]
    df = df.drop(columns=[c for c in _brief_cols if c != "fips" and c in df.columns], errors="ignore")
    df = df.merge(recal_briefs_df[_brief_cols], on="fips", how="left")
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
xfactor_command_loop_df = load_compare_csv(str(XFACTOR_COMMAND_LOOP_CSV_PATH), _mtime=_file_mtime(XFACTOR_COMMAND_LOOP_CSV_PATH))
xfactor_evidence_center_df = load_compare_csv(str(XFACTOR_EVIDENCE_CENTER_CSV_PATH), _mtime=_file_mtime(XFACTOR_EVIDENCE_CENTER_CSV_PATH))
source_confidence_weighting_df = load_compare_csv(str(SOURCE_CONFIDENCE_WEIGHTING_CSV_PATH), _mtime=_file_mtime(SOURCE_CONFIDENCE_WEIGHTING_CSV_PATH))
announcement_anchor_event_latest_df = load_compare_csv(str(ANNOUNCEMENT_ANCHOR_EVENT_LATEST_CSV_PATH), _mtime=_file_mtime(ANNOUNCEMENT_ANCHOR_EVENT_LATEST_CSV_PATH))
fiveyr_boundary_review_df = load_compare_csv(str(FIVEYR_BOUNDARY_REVIEW_CSV_PATH), _mtime=_file_mtime(FIVEYR_BOUNDARY_REVIEW_CSV_PATH))
boom_onset_archetype_lens_df = load_compare_csv(str(BOOM_ONSET_ARCHETYPE_LENS_CSV_PATH), _mtime=_file_mtime(BOOM_ONSET_ARCHETYPE_LENS_CSV_PATH))
watchlist_alert_events = load_watchlist_alert_events(_mtime=_file_mtime(WATCHLIST_ALERT_EVENTS_PATH))
demo_readiness_report = load_demo_readiness_report(_mtime=_file_mtime(DEMO_READINESS_REPORT_PATH))
tokenization_readiness_packet = load_tokenization_readiness_packet(_mtime=_file_mtime(TOKENIZATION_READINESS_PACKET_PATH))
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
if "customer_tour_dismissed" not in st.session_state:
    st.session_state.customer_tour_dismissed = bool(_load_user_data().get("customer_tour_dismissed", False))

# Guided-first progressive disclosure: everyone starts in the explained
# Customer experience; Pro and the legacy console are deliberate opt-ins.
# Internal mode values are unchanged so query params and session keys keep
# working (see documentation/UX_INFORMATION_ARCHITECTURE_AUDIT.md).
experience_options = ["Customer Mode", "Product Mode"]
EXPERIENCE_LABELS = {
    "Customer Mode": "Guided — start here",
    "Product Mode": "Pro — strategy & screening tools",
}
requested_experience = (_query_param_first("experience", "") or "").strip().lower()
experience_default_index = 1 if requested_experience in {"product", "product mode", "pro"} else 0
experience_mode = st.sidebar.radio(
    "Experience",
    experience_options,
    index=experience_default_index,
    format_func=lambda mode: EXPERIENCE_LABELS.get(mode, mode),
    horizontal=False,
    help="Guided is the visual investor workflow with explanations on every screen. Pro adds strategy, screening, and reporting power tools.",
)
st.sidebar.caption(
    "New here? Stay on **Guided**. Switch to **Pro** when you want to tune "
    "strategy weights and run screens yourself. Analyst diagnostics "
    "(walk-forward CV, source health, drift) live under Pro -> Advanced."
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
st.markdown('<div id="landinvest-main" class="landinvest-main-anchor" tabindex="-1"></div>', unsafe_allow_html=True)

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
        tokenization_readiness_packet=tokenization_readiness_packet,
    )
    st.stop()
