"""Reusable report-only county evidence panel for Product and Customer modes."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import streamlit as st


def _fmt_score(value: Any) -> str:
    try:
        val = float(value)
    except (TypeError, ValueError):
        return "-"
    if not np.isfinite(val):
        return "-"
    return f"{val:.1f}"


def _fmt_pct(value: Any) -> str:
    try:
        val = float(value)
    except (TypeError, ValueError):
        return "-"
    if not np.isfinite(val):
        return "-"
    return f"{val * 100:.1f}%"


def _fmt_money_m(value: Any) -> str:
    try:
        val = float(value)
    except (TypeError, ValueError):
        return "-"
    if not np.isfinite(val):
        return "-"
    return f"${val:,.0f}M"


def _fips(row: pd.Series) -> str:
    return str(row.get("fips", "")).replace(".0", "").zfill(5)


def _county_filter(df: pd.DataFrame | None, row: pd.Series) -> pd.DataFrame:
    if df is None or df.empty or "fips" not in df.columns:
        return pd.DataFrame()
    work = df.copy()
    work["fips"] = work["fips"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)
    return work[work["fips"].eq(_fips(row))].copy()


def _source_confidence_rows(row: pd.Series, source_confidence_df: pd.DataFrame | None) -> pd.DataFrame:
    match = _county_filter(source_confidence_df, row)
    if match.empty:
        return pd.DataFrame()
    rec = match.iloc[0]
    rows = [
        {
            "Family": "Overall",
            "Score": _fmt_score(rec.get("source_confidence_score")),
            "Band": rec.get("source_confidence_band", "-"),
        }
    ]
    for col in sorted(c for c in match.columns if c.startswith("source_confidence_")):
        if col in {"source_confidence_score", "source_confidence_band"}:
            continue
        family = col.replace("source_confidence_", "").replace("_", " ").title()
        rows.append({"Family": family, "Score": _fmt_score(rec.get(col)), "Band": ""})
    return pd.DataFrame(rows)


def _announcement_rows(row: pd.Series, announcement_df: pd.DataFrame | None) -> pd.DataFrame:
    match = _county_filter(announcement_df, row)
    if match.empty:
        return pd.DataFrame()
    rows = []
    for _, rec in match.sort_values("year", ascending=False).head(5).iterrows():
        rows.append(
            {
                "Year": rec.get("year", "-"),
                "Events": rec.get("announcement_anchor_event_count", "-"),
                "Score": _fmt_score(rec.get("announcement_anchor_event_score")),
                "Capex": _fmt_money_m(rec.get("announcement_anchor_capex_usd_millions")),
                "Jobs": _fmt_score(rec.get("announcement_anchor_jobs_announced")),
                "Families": rec.get("announcement_anchor_event_families", "-"),
                "Names": rec.get("announcement_anchor_event_names", "-"),
            }
        )
    return pd.DataFrame(rows)


def _command_loop_rows(command_loop_df: pd.DataFrame | None, limit: int = 6) -> pd.DataFrame:
    if command_loop_df is None or command_loop_df.empty:
        return pd.DataFrame()
    keep = [
        "command_priority_rank",
        "label",
        "family",
        "product_readiness",
        "recommended_action",
        "decision",
    ]
    rows = command_loop_df[[c for c in keep if c in command_loop_df.columns]].head(limit).copy()
    rename = {
        "command_priority_rank": "Rank",
        "label": "Surface",
        "family": "Family",
        "product_readiness": "Readiness",
        "recommended_action": "Action",
        "decision": "Decision",
    }
    return rows.rename(columns=rename)


def _boundary_rows(row: pd.Series, boundary_df: pd.DataFrame | None) -> pd.DataFrame:
    match = _county_filter(boundary_df, row)
    if match.empty:
        return pd.DataFrame()
    keep = [
        "boundary_name",
        "boundary_side",
        "boundary_review_label",
        "boundary_risk_points",
        "primary_issue",
        "review_action",
        "operator_summary",
    ]
    out = match[[c for c in keep if c in match.columns]].copy()
    rename = {
        "boundary_name": "Boundary",
        "boundary_side": "Side",
        "boundary_review_label": "Label",
        "boundary_risk_points": "Risk Points",
        "primary_issue": "Primary Issue",
        "review_action": "Review Action",
        "operator_summary": "Operator Summary",
    }
    return out.rename(columns=rename)


def _archetype_lens_rows(row: pd.Series, archetype_df: pd.DataFrame | None) -> pd.DataFrame:
    match = _county_filter(archetype_df, row)
    if match.empty:
        return pd.DataFrame()
    rec = match.iloc[0]
    lenses = (
        ("Anchor", "anchor", "Employer/institution-led setups: anchor announcements, industry composition, college scale, federal construction."),
        ("Amenity", "amenity", "Amenity/migration-led setups: inflows from high-cost counties, seasonal-home demand, hot-metro spillover."),
        ("Adoption", "adoption", "Early-adoption setups: business formation and broadband take-up."),
    )
    rows = []
    for label, key, reads in lenses:
        rank = rec.get(f"{key}_lens_rank")
        if pd.isna(rank):
            continue
        rows.append({"Lens": label, "National Rank": int(float(rank)), "What This Lens Reads": reads})
    return pd.DataFrame(rows)


# Standalone structural "experts" surfaced as directly interpretable national
# percentiles (not model lenses). Each maps to a land-type archetype. The
# economic-dynamism and farmland-cash-rent reads are framed by the Round-24
# land-value follow-up: dynamism is the strongest *home*-value boom signal but
# does NOT predict land-rent booms, whereas farmland cash rent is the one lane
# that does. Report-only context; never affects rank.
_STRUCTURAL_READS = (
    ("Natural amenity", "natural_amenity_pct", "Recreation / second-home",
     "USDA climate/topography/water desirability (national percentile). The recreation/amenity land-type setup."),
    ("Supply constraint", "supply_constraint_pct", "Supply-constrained",
     "WRLURI land-use regulatory restrictiveness (national percentile; survey covers ~1/3 of counties). Amplifies any demand shock."),
    ("Economic dynamism", "dynamism_pct", "Economic dynamism",
     "BEA GDP growth + Census BDS firm dynamism (national percentile). A strong home-value boom signal, but it does not predict land-rent booms."),
    ("Farmland cash rent", "farmland_cash_rent_pct", "Farmland income",
     "USDA NASS cropland cash-rent level (national percentile). The direct land-income signal and the strongest predictor of land-rent booms."),
    ("Renewable build-out", "renewable_buildout_pct", "Renewable ground-lease",
     "EIA-860 utility-scale solar+wind capacity (national percentile). The renewable ground-lease land type; most counties have little/none, so the high end is the signal."),
)


def _structural_reads_rows(row: pd.Series, archetype_df: pd.DataFrame | None) -> pd.DataFrame:
    """Directly interpretable structural percentiles from supplied data —
    natural-amenity desirability (USDA), regulatory supply constraint (WRLURI),
    economic dynamism (BEA GDP + Census BDS), and farmland cash rent (NASS) —
    each a standalone "expert" surfaced as a per-county national percentile.
    Report-only context; does not affect rank."""
    match = _county_filter(archetype_df, row)
    if match.empty:
        return pd.DataFrame()
    rec = match.iloc[0]
    rows = []
    for label, key, _archetype, reads_text in _STRUCTURAL_READS:
        pct = rec.get(key)
        if pd.isna(pct):
            continue
        rows.append({"Structural read": label, "Percentile": int(float(pct)), "What it means": reads_text})
    return pd.DataFrame(rows)


def _structural_archetype_read(row: pd.Series, archetype_df: pd.DataFrame | None,
                               high_pct: int = 75) -> str | None:
    """Synthesize the structural percentiles into a one-line per-county read:
    which standalone expert this county ranks highest on (its land-type fit),
    with any other high-percentile lenses as context. The productization of the
    saturated-blend finding — value is per-county evidence, not a global rank."""
    match = _county_filter(archetype_df, row)
    if match.empty:
        return None
    rec = match.iloc[0]
    scored = []
    for label, key, archetype, _text in _STRUCTURAL_READS:
        pct = rec.get(key)
        if pd.isna(pct):
            continue
        scored.append((archetype, int(float(pct))))
    if not scored:
        return None
    scored.sort(key=lambda t: t[1], reverse=True)
    top_archetype, top_pct = scored[0]
    if top_pct < high_pct:
        return (f"No structural lens stands out (strongest is {top_archetype} at the "
                f"{top_pct}th pct, below the {high_pct}th-pct threshold).")
    others = [f"{a} ({p}th)" for a, p in scored[1:] if p >= high_pct]
    tail = f" Also elevated: {', '.join(others)}." if others else ""
    return f"Strongest structural lens: **{top_archetype}** ({top_pct}th pct).{tail}"


def _brake_rows(row: pd.Series) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    risk = row.get("composite_risk")
    if pd.notna(risk) and float(risk) >= 55:
        rows.append({"Brake": "Risk", "Read": f"Composite risk is {_fmt_score(risk)}.", "Next Check": "Separate hazard, crime, credit, and affordability contributors."})
    interval = row.get("quantile_interval_width_mean", row.get("interval_width_5yr", row.get("pred_std")))
    if pd.notna(interval) and float(interval) >= 0.35:
        rows.append({"Brake": "Uncertainty", "Read": f"Prediction interval is wide ({float(interval):.3f}).", "Next Check": "Compare model disagreement and run-history stability."})
    fallback = row.get("use_stable_3yr_fallback")
    if bool(fallback):
        rows.append({"Brake": "3yr Fallback", "Read": "Medium-term signal uses the stable fallback.", "Next Check": "Treat near-term timing as conditional."})
    source_score = row.get("source_confidence_score")
    if pd.notna(source_score) and float(source_score) < 55:
        rows.append({"Brake": "Source Confidence", "Read": f"Source confidence is {_fmt_score(source_score)}.", "Next Check": "Review missing families before diligence spend."})
    live_rank = row.get("overall_rank")
    sim_rank = row.get("sim_rank")
    if pd.notna(live_rank) and pd.notna(sim_rank) and abs(float(live_rank) - float(sim_rank)) >= 100:
        rows.append({"Brake": "Strategy Spread", "Read": f"Strategy rank differs from production by {abs(float(live_rank) - float(sim_rank)):.0f}.", "Next Check": "Confirm the active strategy matches the user thesis."})
    if not rows:
        rows.append({"Brake": "No Major Brake Flagged", "Read": "No high-level brake crossed the display threshold.", "Next Check": "Continue parcel, listing, zoning, and local-market diligence."})
    return pd.DataFrame(rows)


def render_county_evidence_panel(
    row: pd.Series,
    *,
    preboom_rows: pd.DataFrame | None = None,
    analog_rows: pd.DataFrame | None = None,
    command_loop_df: pd.DataFrame | None = None,
    source_confidence_df: pd.DataFrame | None = None,
    announcement_df: pd.DataFrame | None = None,
    boundary_df: pd.DataFrame | None = None,
    archetype_df: pd.DataFrame | None = None,
    expanded: bool = False,
    key_prefix: str = "county_evidence",
) -> None:
    """Render a shared county evidence panel.

    All content is report-only context. Callers decide where the opt-in panel
    appears; this function only renders evidence already loaded by dashboard.py.
    """

    county = row.get("county_name", row.get("county", "County"))
    state = row.get("state", row.get("state_abbr", ""))
    with st.expander(f"Evidence Panel: {county}, {state}", expanded=expanded):
        st.caption("Report-only evidence; default production rank and score are unchanged.")
        tab_x, tab_lens, tab_events, tab_source, tab_boundary, tab_analogs, tab_brakes = st.tabs(
            ["X-Factors", "Archetype Lens", "Events", "Source", "5yr Boundary", "Analogs", "Brakes"]
        )
        with tab_x:
            if preboom_rows is not None and not preboom_rows.empty:
                st.dataframe(preboom_rows, width="stretch", hide_index=True, height=220)
            else:
                st.caption("No loaded pre-boom surface currently includes this county.")
            command_rows = _command_loop_rows(command_loop_df)
            if not command_rows.empty:
                st.caption("Command-loop priorities")
                st.dataframe(command_rows, width="stretch", hide_index=True, height=220)
        with tab_lens:
            lens_rows = _archetype_lens_rows(row, archetype_df)
            if lens_rows.empty:
                st.caption("No archetype-lens reads are loaded for this county.")
            else:
                st.dataframe(lens_rows, width="stretch", hide_index=True, height=160)
                st.caption(
                    "Each lens is a research model trained on one boom mechanism; a low national "
                    "rank means this county resembles that archetype's pre-boom setup. Lens reads "
                    "are report-only context and never change production rank."
                )
            structural_rows = _structural_reads_rows(row, archetype_df)
            if not structural_rows.empty:
                archetype_read = _structural_archetype_read(row, archetype_df)
                if archetype_read:
                    st.markdown(f"**Structural archetype fit:** {archetype_read}")
                st.caption("Structural reads (supplied data) — standalone expert percentiles")
                st.dataframe(structural_rows, width="stretch", hide_index=True, height=170)
                st.caption(
                    "Each read is a standalone signal surfaced as a national percentile (not a "
                    "rank prediction). High amenity + supply constraint is the classic amenity-boom "
                    "setup; high farmland cash rent is the land-income / farmland setup. Economic "
                    "dynamism tracks home-value booms while farmland cash rent tracks land-value "
                    "booms — distinct land-type theses."
                )
        with tab_events:
            events = _announcement_rows(row, announcement_df)
            if events.empty:
                st.caption("No announcement-event evidence is loaded for this county.")
            else:
                st.dataframe(events, width="stretch", hide_index=True, height=240)
        with tab_source:
            sources = _source_confidence_rows(row, source_confidence_df)
            if sources.empty:
                st.caption("No source-confidence row is loaded for this county.")
            else:
                st.dataframe(sources, width="stretch", hide_index=True, height=280)
        with tab_boundary:
            boundary = _boundary_rows(row, boundary_df)
            if boundary.empty:
                st.caption("This county is not in the current top-25/top-50/top-100 5yr boundary review packet.")
            else:
                st.dataframe(boundary, width="stretch", hide_index=True, height=240)
                st.caption("Boundary labels are operator-review context only; they do not promote or demote production ranks.")
        with tab_analogs:
            if analog_rows is not None and not analog_rows.empty:
                st.dataframe(analog_rows, width="stretch", hide_index=True, height=260)
            else:
                st.caption("No analog-library context is currently available for this county.")
        with tab_brakes:
            st.dataframe(_brake_rows(row), width="stretch", hide_index=True, height=220)
