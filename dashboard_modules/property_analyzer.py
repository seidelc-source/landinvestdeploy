"""Property Analyzer — national lite (plan P1.2, 2026-09-16).

The user enters a location (county, or a ZIP mapped through the Census ZCTA–county crosswalk),
acreage, land use, an optional asking price and a hold. Every number returned is either an
observed, vintage-stamped county fact multiplied by the acreage (HUD FMR yield, NASS land value
and cash rent, AEI residential land price, FEMA NRI) or closed-form arithmetic on stated cost
assumptions (dashboard_modules/property_math.py). The only forward-looking input is the user's
own growth assumption, and the analyzer reports what growth would be needed to break even.

It never estimates a parcel's appreciation: the parcel-level appreciation test was null (P5).
The county tide is shown as the regional screen S2 quintile with its historical band, and the
classifier's resemblance score only as a research column.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from dashboard_modules.property_math import (
    CARRY_PER_YEAR, CLOSING_COST_EACH, EXIT_COST_PCT, MANAGEMENT_PCT_RENT, PROPERTY_TAX_RATE, ROUND_TRIP_COST,
    VACANCY_HAIRCUT, VehicleEconomics, breakeven_annual_growth, income_ceiling_per_year, value_anchors)

LAND_USES = ("Cropland", "Pasture / grazing", "Recreation / timber", "Residential lot")
NO_PARCEL_APPRECIATION = ("No parcel-level appreciation estimate: the parcel appreciation test was null (P5). "
                          "County tide and observed facts only.")
PILOT_COUNTIES = {"50015": "Lamoille VT", "47155": "Sevier TN", "10005": "Sussex DE", "05069": "Jefferson AR"}
DEFAULT_ASSUMPTIONS = {
    "round_trip": ROUND_TRIP_COST, "carry_per_year": CARRY_PER_YEAR, "closing_cost": CLOSING_COST_EACH,
    "tax_rate": PROPERTY_TAX_RATE, "management_pct": MANAGEMENT_PCT_RENT, "vacancy": VACANCY_HAIRCUT,
    "exit_cost_pct": EXIT_COST_PCT,
}


def _num(row, key):
    try:
        v = row.get(key)
    except AttributeError:
        return None
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if pd.isna(f) else f


def _flag(row, key) -> bool:
    try:
        v = row.get(key)
    except AttributeError:
        return False
    return bool(v) and not (isinstance(v, float) and pd.isna(v))


def load_crosswalk(path: Path) -> pd.DataFrame | None:
    try:
        cw = pd.read_parquet(path)
    except (OSError, ValueError):
        return None
    cw["zcta"] = cw["zcta"].astype(str).str.zfill(5)
    cw["fips"] = cw["fips"].astype(str).str.zfill(5)
    return cw


def zip_to_counties(zip5: str, crosswalk: pd.DataFrame | None) -> pd.DataFrame:
    """Counties a ZIP (as a 2020 ZCTA) overlaps, by land-area share; the largest share is `primary`."""
    if crosswalk is None or not zip5:
        return pd.DataFrame(columns=["fips", "share", "primary"])
    z = str(zip5).strip().zfill(5)
    hit = crosswalk[crosswalk["zcta"] == z].sort_values("share", ascending=False)
    return hit[["fips", "share", "primary"]].reset_index(drop=True)


def rent_for_land_use(row, land_use: str) -> tuple[float | None, str]:
    crop = _num(row, "nass_cash_rent_cropland_nonirr")
    pasture = _num(row, "nass_cash_rent_pasture")
    if land_use == "Cropland":
        return crop, "NASS non-irrigated cropland cash rent"
    if land_use == "Pasture / grazing":
        return pasture, "NASS pasture cash rent"
    if land_use == "Recreation / timber":
        return (0.5 * pasture if pasture is not None else None), "proxy: half the NASS pasture rent (no county recreation-lease series on disk)"
    return None, "no county rent series for residential lots (enter your own rent if you have one)"


def analyze_property(row, *, acres: float, land_use: str, asking_price: float | None, hold_years: int,
                     growth_assumption: float = 0.0, usable_share: float = 1.0, user_rent_per_acre: float | None = None,
                     assumptions: dict | None = None) -> dict:
    """All analyzer numbers for one county row and one property description. Pure; unit-tested."""
    a = {**DEFAULT_ASSUMPTIONS, **(assumptions or {})}
    acres = max(float(acres), 0.0)
    asking = float(asking_price) if asking_price else None

    rent, rent_source = rent_for_land_use(row, land_use)
    if user_rent_per_acre:
        rent, rent_source = float(user_rent_per_acre), "your rent assumption"
    income = income_ceiling_per_year(acres, rent, usable_share=usable_share,
                                     management_pct=a["management_pct"], vacancy=a["vacancy"])

    anchors = value_anchors(acres, farm_value_per_acre=_num(row, "nass_land_value_per_acre"),
                            residential_value_per_acre=_num(row, "aei_land_value_per_acre"), asking_price=asking)
    anchor_key = "residential" if land_use == "Residential lot" else "farm"
    basis = asking if asking else ((anchors.get(anchor_key) or {}).get("total"))
    net_income = income["net"] or 0.0
    income_yield = (net_income / basis) if basis else None
    breakeven = (breakeven_annual_growth(hold_years, round_trip=a["round_trip"], carry_per_year=a["carry_per_year"],
                                         income_yield_per_year=income_yield or 0.0) if hold_years > 0 else None)
    vehicle = None
    if basis:
        vehicle = VehicleEconomics(price=basis, hold_years=hold_years, annual_net_income=net_income,
                                   growth_path=[growth_assumption], closing_cost=a["closing_cost"], tax_rate=a["tax_rate"],
                                   exit_cost_pct=a["exit_cost_pct"]).run()

    q = _num(row, "s2_quintile_quiet_B")
    fips = str(row.get("fips", "")).zfill(5) if hasattr(row, "get") else ""
    return {
        "county": {"fips": fips, "name": row.get("county_name"), "state": row.get("state"),
                   "universe_B": _flag(row, "universe_B"), "quiet_now": _flag(row, "quiet_now"),
                   "facts_coverage": _num(row, "facts_coverage")},
        "inputs": {"acres": acres, "land_use": land_use, "asking_price": asking, "hold_years": hold_years,
                   "growth_assumption": growth_assumption, "usable_share": usable_share},
        "anchors": anchors, "anchor_basis": basis, "anchor_basis_kind": "asking price" if asking else f"{anchor_key} anchor",
        "income": {**income, "rent_per_acre": rent, "rent_source": rent_source, "net_yield_on_basis": income_yield,
                   "county_gross_rent_yield": _num(row, "fmr_gross_yield"), "farm_cap_rate_proxy": _num(row, "farm_cap_rate_proxy")},
        "breakeven_growth": breakeven, "vehicle": vehicle,
        "tide": {"s2_quintile": int(q) if q is not None else None, "s2_rank_quiet_B": _num(row, "s2_rank_quiet_B"),
                 "s2_score": _num(row, "s2_score"), "state_rank_pct": _num(row, "s2_state_rank_pct"),
                 "own_momentum_rank_pct": _num(row, "s2_mom_rank_pct"), "momentum_rank_pct": _num(row, "momentum_rank_pct"),
                 "classifier_score_research": _num(row, "boom_onset_score"), "pred_1yr_pct": _num(row, "pred_1yr_pct")},
        "risk": {"composite_risk": _num(row, "composite_risk"), "nri": _num(row, "nri_risk_score"),
                 "wildfire": _num(row, "usfs_wildfire_risk_score"), "coastal": _num(row, "coastal_exposure_score"),
                 "commodity_cycle": _flag(row, "qcew_commodity_cycle_flag")},
        "pilot": PILOT_COUNTIES.get(fips),
        "disclaimers": [NO_PARCEL_APPRECIATION,
                        "Value anchors are county-level $/acre facts (NASS farm land, AEI residential land) times your acreage — "
                        "anchors, not an appraisal.",
                        "Breakeven and vehicle economics are arithmetic on the stated cost assumptions; the growth path is your own assumption."],
    }


def load_band_table(path: Path) -> dict | None:
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return None


# ----------------------------------------------------------------------------------------- Streamlit
def render_property_analyzer(df: pd.DataFrame, *, key_prefix: str, crosswalk_path: Path,
                             band_table_path: Path | None = None) -> None:
    import streamlit as st

    st.subheader("Property Analyzer — national lite")
    st.caption("Describe a property; every number is an observed county fact times your acreage, or arithmetic on the "
               "cost assumptions below. " + NO_PARCEL_APPRECIATION)
    if df.empty or "fips" not in df.columns:
        st.info("No county frame is loaded.")
        return
    frame = df.copy()
    frame["fips"] = frame["fips"].astype(str).str.zfill(5)
    crosswalk = load_crosswalk(crosswalk_path)

    left, right = st.columns([1, 1])
    with left:
        mode = st.radio("Locate by", ["County", "ZIP"], horizontal=True, key=f"{key_prefix}_mode")
        row = None
        if mode == "ZIP":
            zip5 = st.text_input("ZIP code", value="", max_chars=5, key=f"{key_prefix}_zip")
            hits = zip_to_counties(zip5, crosswalk) if len(zip5.strip()) == 5 else pd.DataFrame()
            if crosswalk is None:
                st.info("ZIP lookup needs data/reference/zcta_county_crosswalk.parquet (run scripts/fetch_zcta_county_crosswalk.py); use County.")
            elif len(zip5.strip()) == 5 and hits.empty:
                st.warning("That ZIP is not in the 2020 ZCTA–county crosswalk (PO-box ZIPs have no ZCTA).")
            elif not hits.empty:
                hits = hits.merge(frame[["fips", "county_name", "state"]], on="fips", how="left")
                labels = [f"{r.county_name}, {r.state} ({r.share:.0%} of the ZIP's land)" for r in hits.itertuples()]
                pick = st.selectbox("County for this ZIP", labels, index=0, key=f"{key_prefix}_zip_county")
                fips = hits.iloc[labels.index(pick)]["fips"]
                sel = frame[frame["fips"] == fips]
                row = sel.iloc[0] if not sel.empty else None
        else:
            states = sorted(frame["state"].dropna().astype(str).unique().tolist())
            state = st.selectbox("State", states, key=f"{key_prefix}_state")
            counties = frame[frame["state"] == state].sort_values("county_name")
            names = counties["county_name"].astype(str).tolist()
            name = st.selectbox("County", names, key=f"{key_prefix}_county")
            sel = counties[counties["county_name"].astype(str) == name]
            row = sel.iloc[0] if not sel.empty else None
    with right:
        acres = st.number_input("Acres", min_value=0.1, max_value=100_000.0, value=20.0, step=1.0, key=f"{key_prefix}_acres")
        land_use = st.selectbox("Land use", list(LAND_USES), key=f"{key_prefix}_use")
        asking = st.number_input("Asking price ($, 0 = unknown)", min_value=0.0, value=0.0, step=1_000.0, key=f"{key_prefix}_price")
        hold = st.slider("Hold (years)", 1, 10, 5, key=f"{key_prefix}_hold")
        growth = st.slider("Your price-growth assumption (%/yr) — we do not forecast", -5.0, 10.0, 0.0, 0.5,
                           key=f"{key_prefix}_growth") / 100.0
    with st.expander("Cost assumptions (editable)", expanded=False):
        c1, c2, c3 = st.columns(3)
        a = dict(DEFAULT_ASSUMPTIONS)
        a["round_trip"] = c1.number_input("Round-trip cost (share of price)", 0.0, 0.3, a["round_trip"], 0.01, key=f"{key_prefix}_rt")
        a["carry_per_year"] = c1.number_input("Carry per year (share of price)", 0.0, 0.1, a["carry_per_year"], 0.005, key=f"{key_prefix}_carry")
        a["closing_cost"] = c2.number_input("Closing cost ($)", 0.0, 50_000.0, a["closing_cost"], 500.0, key=f"{key_prefix}_close")
        a["tax_rate"] = c2.number_input("Property tax (share of price / yr)", 0.0, 0.05, a["tax_rate"], 0.001, format="%.3f", key=f"{key_prefix}_tax")
        a["management_pct"] = c3.number_input("Management (share of rent)", 0.0, 0.5, a["management_pct"], 0.01, key=f"{key_prefix}_mgmt")
        a["vacancy"] = c3.number_input("Vacancy haircut (share of rent)", 0.0, 0.5, a["vacancy"], 0.01, key=f"{key_prefix}_vac")
        a["exit_cost_pct"] = c3.number_input("Exit cost (share of sale)", 0.0, 0.2, a["exit_cost_pct"], 0.01, key=f"{key_prefix}_exit")
        usable = st.slider("Usable share of the acreage (after wetlands / flood / slope, if known)", 0.1, 1.0, 1.0, 0.05, key=f"{key_prefix}_usable")
        user_rent = st.number_input("Your own rent assumption ($/acre/yr, 0 = use the county series)", 0.0, 5_000.0, 0.0, 5.0, key=f"{key_prefix}_rent")

    if row is None:
        st.info("Pick a county (or a ZIP that maps to one) to run the analyzer.")
        return
    res = analyze_property(row, acres=acres, land_use=land_use, asking_price=asking or None, hold_years=int(hold),
                           growth_assumption=growth, usable_share=usable, user_rent_per_acre=user_rent or None, assumptions=a)
    _render_result(st, res, band_table_path)


def _money(v) -> str:
    return f"${v:,.0f}" if v is not None and not pd.isna(v) else "—"


def _pct(v, d=1) -> str:
    return f"{v:+.{d}%}" if v is not None and not pd.isna(v) else "—"


def _render_result(st, res: dict, band_table_path: Path | None) -> None:
    c = res["county"]
    badges = [("universe B" if c["universe_B"] else "outside universe B"), ("quiet band" if c["quiet_now"] else "already moving")]
    if res["pilot"]:
        badges.append(f"pilot county ({res['pilot']}) — parcel-deep read under Advanced → Parcels")
    st.markdown(f"### {c['name']}, {c['state']}  ·  " + " · ".join(badges))

    anchors, inc, tide, risk = res["anchors"], res["income"], res["tide"], res["risk"]
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    farm = anchors.get("farm") or {}
    resid = anchors.get("residential") or {}
    m1.metric("Farm land anchor", _money(farm.get("total")), f"{_money(farm.get('per_acre'))}/ac NASS", delta_color="off")
    m2.metric("Residential land anchor", _money(resid.get("total")), f"{_money(resid.get('per_acre'))}/ac AEI", delta_color="off")
    m3.metric("Asking $/acre", _money(anchors.get("asking_per_acre")), "vs the anchors above", delta_color="off")
    m4.metric("Net income capacity / yr", _money(inc.get("net")), f"{_money(inc.get('rent_per_acre'))}/ac rent", delta_color="off")
    m5.metric("Breakeven growth / yr", _pct(res["breakeven_growth"]), f"over {res['inputs']['hold_years']} yrs, net of costs", delta_color="off")
    m6.metric("Regional tide (S2)", f"quintile {tide['s2_quintile']}" if tide["s2_quintile"] else "not served yet",
              "among quiet counties", delta_color="off")

    st.markdown("**Value anchors** — county-level $/acre facts × your acreage (anchors, not an appraisal)")
    st.dataframe(pd.DataFrame([
        {"Anchor": "NASS farm land value", "$/acre": _money(farm.get("per_acre")), "× acres": _money(farm.get("total"))},
        {"Anchor": "AEI residential land price", "$/acre": _money(resid.get("per_acre")), "× acres": _money(resid.get("total"))},
        {"Anchor": "Your asking price", "$/acre": _money(anchors.get("asking_per_acre")), "× acres": _money(res["inputs"]["asking_price"])},
    ]), width="stretch", hide_index=True, height=150)

    st.markdown("**Income capacity** — " + str(inc["rent_source"]))
    st.dataframe(pd.DataFrame([
        {"Item": "Usable acres", "Value": f"{inc['usable_acres']:,.1f}"},
        {"Item": "Gross rent / yr", "Value": _money(inc.get("gross"))},
        {"Item": "Net after management + vacancy / yr", "Value": _money(inc.get("net"))},
        {"Item": f"Net yield on {res['anchor_basis_kind']}", "Value": _pct(inc.get("net_yield_on_basis"))},
        {"Item": "County gross rent yield (HUD FMR, homes)", "Value": _pct(inc.get("county_gross_rent_yield"))},
        {"Item": "County farm cap-rate proxy", "Value": _pct(inc.get("farm_cap_rate_proxy"))},
    ]), width="stretch", hide_index=True, height=250)

    v = res["vehicle"]
    if v:
        st.markdown(f"**Vehicle economics** — on a basis of {_money(res['anchor_basis'])} ({res['anchor_basis_kind']}), "
                    f"your growth assumption {res['inputs']['growth_assumption']:+.1%}/yr")
        st.dataframe(pd.DataFrame([
            {"Item": "Year-1 net yield (income − tax − carry)", "Value": _pct(v["year1_net_yield"])},
            {"Item": "Fixed costs as share of price (closing + exit)", "Value": _pct(v["fixed_cost_share_of_price"])},
            {"Item": "Breakeven growth / yr (clears all costs)", "Value": _pct(v["breakeven_growth"])},
            {"Item": f"Exit value after {res['inputs']['hold_years']} yrs under your assumption", "Value": _money(v["exit_value"])},
            {"Item": "Net proceeds after exit cost", "Value": _money(v["net_proceeds"])},
            {"Item": "Total profit (undiscounted)", "Value": _money(v["total_profit"])},
            {"Item": "IRR under your assumption", "Value": _pct(v["irr"]) if v["irr"] is not None else "—"},
        ]), width="stretch", hide_index=True, height=290)

    st.markdown("**Regional tide and timing** — the only return signal with an out-of-era edge is regional")
    tide_rows = [
        {"Read": "S2 quintile among quiet counties (1 = strongest)", "Value": tide["s2_quintile"] or "not served yet"},
        {"Read": "State home-price momentum rank (S2 input)", "Value": f"{tide['state_rank_pct']:.2f}" if tide["state_rank_pct"] is not None else "—"},
        {"Read": "Own prior 3-yr momentum rank (quiet ≤ 0.667)", "Value": f"{tide['momentum_rank_pct']:.2f}" if tide["momentum_rank_pct"] is not None else "—"},
        {"Read": "1yr model position (ordinal only)", "Value": f"top {100 * (1 - tide['pred_1yr_pct']):.0f}%" if tide["pred_1yr_pct"] is not None else "—"},
        {"Read": "Classifier resemblance score (research column, no live skill)", "Value": f"{tide['classifier_score_research']:.2f}" if tide["classifier_score_research"] is not None else "—"},
    ]
    st.dataframe(pd.DataFrame(tide_rows), width="stretch", hide_index=True, height=220)
    band = load_band_table(band_table_path) if band_table_path else None
    if band:
        with st.expander("What an S2 band has been worth historically (stamped; regional; home prices; not a forecast)", expanded=False):
            st.json(band, expanded=False)
    else:
        st.caption("Historical band table not on disk yet (published by scripts/build_s2_band_table.py). RF-1 / SCR-B3: the "
                   "screen's top picks earned ≈ +3.9pp more over 3 years than a random quiet county (2008–22), 61% retained out of era.")

    st.markdown("**Risk facts**")
    st.dataframe(pd.DataFrame([
        {"Fact": "Composite risk score", "Value": f"{risk['composite_risk']:.1f}" if risk["composite_risk"] is not None else "—"},
        {"Fact": "FEMA National Risk Index", "Value": f"{risk['nri']:.1f}" if risk["nri"] is not None else "—"},
        {"Fact": "Wildfire risk (USFS)", "Value": f"{risk['wildfire']:.2f}" if risk["wildfire"] is not None else "—"},
        {"Fact": "Coastal exposure", "Value": f"{risk['coastal']:.2f}" if risk["coastal"] is not None else "—"},
        {"Fact": "Commodity-cycle exposure (QCEW)", "Value": "yes" if risk["commodity_cycle"] else "no"},
        {"Fact": "Facts coverage", "Value": f"{c['facts_coverage']:.0%}" if c["facts_coverage"] is not None else "—"},
    ]), width="stretch", hide_index=True, height=250)
    for line in res["disclaimers"]:
        st.caption(line)
