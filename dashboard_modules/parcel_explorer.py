"""Parcel Explorer tab (Operator/Advanced): surfaces the parcel-layer artifacts.

Reads (all optional; the tab degrades gracefully when a file is absent):
  data/processed/parcels/parcel_tokenization_readiness.parquet  (per-parcel gates/tiers)
  output/tk2_offering_simulation.json                            (TK2 scenario table)
  output/parcel_score_repeat_sales_validation.json               (P5 validation read)

Report-only sourcing surface: parcel scores are calibrated value/quality reads
(P4 operator labels; P5 sales validation), never investability or an offering.
Production county ranks are untouched by everything shown here.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

APP_ROOT = Path(__file__).resolve().parent.parent
READINESS_PATH = APP_ROOT / "data" / "processed" / "parcels" / "parcel_tokenization_readiness.parquet"
TK2_PATH = APP_ROOT / "output" / "tk2_offering_simulation.json"
P5_PATH = APP_ROOT / "output" / "parcel_score_repeat_sales_validation.json"


def _mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


@st.cache_data(show_spinner=False)
def _load_readiness(_mtime_key: float) -> pd.DataFrame | None:
    if not READINESS_PATH.exists():
        return None
    return pd.read_parquet(READINESS_PATH)


@st.cache_data(show_spinner=False)
def _load_json(path_str: str, _mtime_key: float) -> dict | None:
    path = Path(path_str)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _county_2x2_figure(df: pd.DataFrame) -> go.Figure:
    per = (df.groupby("county")
             .agg(thesis=("g1_county_thesis", "first"),
                  tier_a=("readiness_tier", lambda s: int((s == "A").sum())),
                  p90_score=("parcel_score", lambda s: float(s.quantile(0.90)))))
    fig = go.Figure(go.Scatter(
        x=per["p90_score"], y=per["thesis"], mode="markers+text",
        text=per.index, textposition="top center",
        marker=dict(size=(per["tier_a"].clip(lower=1) ** 0.5) * 1.8 + 8),
        hovertemplate="%{text}<br>county thesis %{y:.2f} · P90 parcel score %{x:.1f}<extra></extra>",
    ))
    fig.update_layout(
        height=340, margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title="P90 parcel score (within-county)",
        yaxis_title="County boom-onset thesis",
        title="The 2×2: quality of the market × quality of the dirt (bubble = Tier-A count)",
    )
    return fig


def render_parcel_explorer_tab() -> None:
    st.header("Parcel Explorer (Pilot Counties)")
    st.caption(
        "Report-only sourcing surface over the four pilot counties (Phases 0–5 of the "
        "parcel proposal). Scores are within-county value/quality reads — calibrated to "
        "operator labels (P4) and validated against recorded sales as a *level* signal "
        "(P5); they do not forecast parcel-level appreciation, and nothing here is "
        "investability. Production county ranks are untouched."
    )

    df = _load_readiness(_mtime(READINESS_PATH))
    if df is None or df.empty:
        st.info(
            "Parcel artifacts are not staged in this environment. Generate them with the "
            "Phase 0–3 pipeline (see `documentation/PARCEL_VALUE_SCORING_PROPOSAL.md`):\n\n"
            "`fetch_pilot_county_parcels.py` → `fetch_parcel_overlay_layers.py` → "
            "`build_parcel_intrinsics.py` → `fetch_ssurgo_county_soils.py` → "
            "`build_parcel_farm_income.py` → `build_parcel_score.py` → "
            "`build_parcel_tokenization_readiness.py`"
        )
        return

    n_labeled = int((df["operator_verdict"] != "").sum()) if "operator_verdict" in df else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Parcels scored", f"{len(df):,}")
    c2.metric("Pilot counties", f"{df['county'].nunique()}")
    c3.metric("Tier A (sourcing-ready)", f"{int((df['readiness_tier'] == 'A').sum()):,}")
    c4.metric("Operator-labeled (P4)", f"{n_labeled}")

    st.plotly_chart(_county_2x2_figure(df), use_container_width=True)

    st.subheader("Browse parcels")
    f1, f2, f3, f4 = st.columns([2, 1, 1, 1])
    county = f1.selectbox("County", ["All"] + sorted(df["county"].unique().tolist()),
                          key="parcel_explorer_county")
    tier = f2.selectbox("Readiness tier", ["A", "A+B", "All"], key="parcel_explorer_tier")
    min_acres = f3.number_input("Min acres", min_value=0.0, value=2.0, step=1.0,
                                key="parcel_explorer_min_acres")
    frontage_only = f4.checkbox("Road frontage only", value=False,
                                key="parcel_explorer_frontage")

    view = df.copy()
    if county != "All":
        view = view[view["county"] == county]
    if tier == "A":
        view = view[view["readiness_tier"] == "A"]
    elif tier == "A+B":
        view = view[view["readiness_tier"].isin(["A", "B"])]
    view = view[view["acres_geom"] >= min_acres]
    if frontage_only and "g2_parcel" in view:
        view = view[view["g2_parcel"]]

    cols = [c for c in ["county", "parcel_key", "owner", "acres_geom", "usable_acres",
                        "parcel_score", "readiness_tier", "g4_strategy",
                        "farm_income_ceiling_yr", "g5_income_yield_proxy",
                        "operator_verdict"] if c in view.columns]
    top = view.sort_values("parcel_score", ascending=False).head(200)[cols]
    st.caption(f"{len(view):,} parcels match; showing top 200 by parcel score.")
    st.dataframe(top, use_container_width=True, hide_index=True)
    st.download_button(
        "Export filtered parcels (CSV)",
        view.sort_values("parcel_score", ascending=False)[cols].to_csv(index=False),
        file_name="parcel_explorer_export.csv",
        mime="text/csv",
        key="parcel_explorer_export",
    )

    tk2 = _load_json(str(TK2_PATH), _mtime(TK2_PATH))
    with st.expander("TK2 offering simulator (report-only scenario model)"):
        if not tk2:
            st.info("Run `scripts/build_tk2_offering_simulator.py` to generate scenarios.")
        else:
            st.caption(
                "Reg CF scenario model over real Tier-A Jefferson parcels. Every cost "
                "constant is a pre-counsel assumption ([A1]–[A14] in the script); "
                "acquisition multiples are relative to Arkansas USE-VALUE assessments, "
                "so higher columns are the realistic ones. Not an offering."
            )
            rows = [s for s in tk2.get("scenarios", []) if s.get("feasible")]
            if rows:
                tbl = pd.DataFrame([{
                    "Raise": f"${s['raise']:,}",
                    "Acq ×": s["acq_multiple"],
                    "Parcels": s["parcels_bought"],
                    "Acres": s["acres"],
                    "Fixed %": s["fixed_cost_pct_of_raise"],
                    "Yr-1 yield %": s["year1_net_yield_pct"],
                    "IRR flat %": s["irr_7yr"]["flat"],
                    "IRR 3%/yr %": s["irr_7yr"]["steady_3pct"],
                    "IRR boom %": s["irr_7yr"]["boom_thesis"],
                    "IRR downside %": s["irr_downside_pct"],
                } for s in rows])
                st.dataframe(tbl, use_container_width=True, hide_index=True)

    p5 = _load_json(str(P5_PATH), _mtime(P5_PATH))
    with st.expander("How much to trust these scores (P4/P5 evidence)"):
        st.markdown(
            "- **P4 (operator calibration):** 85 hand labels; pursue-vs-pass separation "
            "0.88 in Lamoille after the v3 archetype-conditional alpha; Sussex/Jefferson "
            "discriminators are known feature gaps. Labels: "
            "`data/operator_labels/parcel_review_verdicts_20260714.csv`."
        )
        if p5:
            cx = p5.get("cross_section_spearman_vs_price_per_ac", {})
            st.markdown(
                f"- **P5 (sales validation, Lamoille):** score components track realized "
                f"land $/ac (alpha ρ={cx.get('alpha_score', {}).get('rho', '—')}, "
                f"income ρ={cx.get('income_score', {}).get('rho', '—')}, "
                f"n={p5.get('cross_section_n', '—')}); within-county appreciation "
                f"prediction is **null** — the appreciation thesis lives in the county "
                f"tide, by design."
            )
        st.markdown(
            "- Full reads: `output/parcel_score_calibration_read.md`, "
            "`output/parcel_score_repeat_sales_validation.md`."
        )
