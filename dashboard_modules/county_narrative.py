"""Facts-based county narrative (plan P0.2, 2026-09-16).

Replaces the SHAP-driver bullets that opened every Guided "Why It Could Work" list with raw
feature names and attributions from the retired 5-yr / 3-yr regressions. Every sentence here
is an observed, vintage-stamped fact (HUD FMR, NASS, AEI, BEA, ACS, FEMA NRI) or an explicitly
labelled research read. No model attribution, no multi-year horizon, and the 1-yr model appears
only as an ordinal position (embargoed median Spearman +0.35; top-of-list precision unproven).

Pure functions on a county row so the text can be golden-tested without Streamlit.
"""

from __future__ import annotations

import pandas as pd

S2_EDGE_SENTENCE = (
    "Historically the screen's top picks earned about +3.9pp more over three years than a random "
    "quiet county (regional, home prices only, 61% of the edge retained out of era) — context, not a "
    "forecast for this county."
)
NO_FORECAST_SENTENCE = (
    "No multi-year appreciation forecast is claimed; the classifier's resemblance score is a research "
    "column with no live skill (1.1× a random quiet county)."
)


def _get(row, key):
    try:
        return row.get(key)
    except AttributeError:
        return None


def _num(row, key) -> float | None:
    v = _get(row, key)
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if pd.isna(f) else f


def _flag(row, key) -> bool:
    v = _get(row, key)
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return False
    return bool(v)


def _year(row, key) -> str:
    v = _num(row, key)
    return f"{int(v)}" if v is not None else "?"


def ordinal_position(pct: float | None) -> str:
    """A within-year percentile (0–1, higher = better) as an ordinal position, never a magnitude."""
    return f"top {100 * (1 - pct):.0f}%" if pct is not None else "—"


def build_county_narrative(row, history_row=None) -> dict[str, list[str] | str]:
    """Positives, cautions and a summary built only from observed facts and labelled research reads."""
    name = _get(row, "county_name") or "This county"
    positives: list[str] = []
    cautions: list[str] = []

    y = _num(row, "fmr_gross_yield")
    band = _num(row, "rent_yield_pct_in_rucc_band")
    fy = _year(row, "fmr_fiscal_year")
    if y is not None:
        where = (f" — in the {ordinal_position(band)} of its rural–urban band" if band is not None else "")
        line = f"Gross rent yield {y:.1%} (HUD FMR FY{fy}){where}; an observed yield, not a forecast."
        (positives if band is None or band >= 0.5 else cautions).append(line)

    nass = _num(row, "nass_land_value_per_acre")
    cheap = _num(row, "land_cheapness_pct")
    if nass is not None:
        ly = _year(row, "nass_land_value_year")
        if cheap is None or cheap >= 0.5:
            positives.append(f"Farm land ${nass:,.0f}/acre (NASS {ly})"
                             + (f" — cheaper than {cheap:.0%} of counties." if cheap is not None else "."))
        else:
            cautions.append(f"Farm land is not cheap here: ${nass:,.0f}/acre (NASS {ly}), pricier than "
                            f"{1 - cheap:.0%} of counties.")

    mom = _num(row, "momentum_rank_pct")
    quiet = _flag(row, "quiet_now")
    in_universe = _flag(row, "universe_B")
    if quiet:
        positives.append("Quiet band: prior 3-year momentum rank "
                         + (f"{mom:.2f}" if mom is not None else "—")
                         + " — prices are not already running"
                         + ("; inside the investable universe (density ≤ 95th percentile, population < 1M)." if in_universe else "."))
    elif mom is not None:
        cautions.append(f"Prices are already moving (momentum rank {mom:.2f}) — not a quiet-band setup.")

    q = _num(row, "s2_quintile_quiet_B")
    tide = ""
    if q is not None:
        qi = int(q)
        tide = f"Regional tide: S2 quintile {qi} of 5 among quiet counties (state momentum + own warming)."
        if qi <= 2:
            positives.append(tide + " " + S2_EDGE_SENTENCE)
        elif qi >= 4:
            cautions.append(f"Regional tide is weak: S2 quintile {qi} of 5 among quiet counties.")

    p1 = _num(row, "pred_1yr_pct")
    if p1 is not None and p1 >= 0.75:
        positives.append(f"The 1-year model places it in the {ordinal_position(p1)} of counties — an ordering "
                         "read only; top-of-list precision is unproven and no return is implied.")

    seasonal = _num(row, "seasonal_home_share")
    if seasonal is not None and seasonal >= 0.15:
        positives.append(f"Seasonal-home share {seasonal:.0%} (ACS) — a second-home / amenity market.")

    risk = _num(row, "composite_risk")
    if risk is not None and risk >= 60:
        cautions.append(f"Composite risk score {risk:.1f} is elevated (market, liquidity, regulatory, "
                        "environmental and concentration sub-scores).")
    elif risk is not None and risk >= 45:
        cautions.append(f"Composite risk score {risk:.1f} is middling, so this is not a clean low-risk setup.")
    nri = _num(row, "nri_risk_score")
    if nri is not None and nri >= 20:
        cautions.append(f"FEMA National Risk Index {nri:.1f} — elevated natural-hazard exposure.")
    wildfire = _num(row, "usfs_wildfire_risk_score")
    if wildfire is not None and wildfire >= 0.66:
        cautions.append(f"Wildfire risk score {wildfire:.2f} is high (USFS).")
    coastal = _num(row, "coastal_exposure_score")
    if coastal is not None and coastal >= 0.5:
        cautions.append(f"Coastal exposure {coastal:.2f} — add flood and insurance diligence.")
    if _flag(row, "qcew_commodity_cycle_flag"):
        cautions.append("The local economy is exposed to a commodity cycle (QCEW sector mix).")
    pti = _num(row, "price_to_income")
    if pti is not None and pti >= 5:
        cautions.append(f"Price-to-income {pti:.1f} — affordability is already stretched.")
    div = _num(row, "rent_price_divergence3")
    if div is not None and div <= -0.05:
        cautions.append(f"Prices have outrun rents over three years ({div:+.1%} rent–price divergence).")
    cov = _num(row, "facts_coverage")
    if cov is not None and cov < 0.6:
        cautions.append(f"Only {cov:.0%} of the facts columns are populated — treat every read as thin.")

    if history_row is not None and not getattr(history_row, "empty", False):
        share = _num(history_row, "top25_presence_share")
        std_rank = _num(history_row, "std_rank")
        latest_rank = _num(history_row, "latest_rank")
        if share is not None and share >= 0.75:
            positives.append(f"This county has stayed in the top 25 for {100 * share:.0f}% of recent runs, "
                             "which supports shortlist durability.")
        if std_rank is not None and std_rank >= 20:
            cautions.append(f"Run-to-run rank volatility is still meaningful (rank std {std_rank:.1f}), "
                            "so placement is not fully settled.")
        if latest_rank is not None:
            positives.append(f"Current live rank is #{int(latest_rank)}.")

    yield_txt = f"{y:.1%}" if y is not None else "n/a"
    land_txt = f"${nass:,.0f}/acre" if nass is not None else "n/a"
    risk_txt = f"{risk:.1f}" if risk is not None else "n/a"
    summary = (f"{name}: {'quiet-band' if quiet else 'already-moving'} county with gross rent yield {yield_txt} "
               f"and farm land at {land_txt}; composite risk {risk_txt}. "
               + (tide + " " if tide else "") + NO_FORECAST_SENTENCE)
    # The Guided story shows five of each; the memo export shows all of them.
    return {"summary": summary, "positives": positives[:8], "cautions": cautions[:8]}
