"""The "why is this an investment" number stack (plan P1.1, 2026-09-16).

Seven numbers per county, each an observed, vintage-stamped fact or a labelled read, each with
what it beats. Pure function on the county row and the stamped S2 band table
(output/recal/s2_band_table.json) so the stack can be golden-tested without Streamlit.
"""

from __future__ import annotations

import pandas as pd

from dashboard_modules.property_math import breakeven_annual_growth


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


def band_read(band_table: dict | None, quintile: int | None, era: str = "zhvi") -> dict | None:
    """The stamped historical read for one S2 band in one era, or None."""
    if not band_table or quintile is None:
        return None
    try:
        bands = band_table["eras"][era]["bands"]
    except (KeyError, TypeError):
        return None
    for b in bands:
        if int(b.get("band", 0)) == int(quintile):
            ex = b.get("excess_3yr_pp") or {}
            td = b.get("top_decile_share") or {}
            return {"band": int(quintile), "label": b.get("label"), "excess_pp": ex.get("value"),
                    "ci90": ex.get("ci90"), "n_anchors": ex.get("n_units"),
                    "top_decile_share": td.get("value"),
                    "top_decile_null": next((n.get("value") for n in (td.get("nulls") or []) if n.get("preferred")), None),
                    "net_of_cost_3yr_pct": b.get("net_of_cost_3yr_pct")}
    return None


def investment_number_items(row, band_table: dict | None = None) -> list[dict]:
    """Ordered list of {label, value, note} — the stack the Guided story and the memo show."""
    items: list[dict] = []

    q = _num(row, "s2_quintile_quiet_B")
    eligible = _flag(row, "s2_eligible")
    if q is not None and eligible:
        br = band_read(band_table, int(q))
        note = "regional screen S2 among quiet universe-B counties"
        if br and br.get("excess_pp") is not None:
            ci = br.get("ci90") or [None, None]
            note = (f"band {int(q)} earned {br['excess_pp']:+.1f}pp 3-yr vs a random quiet county, 2008–22"
                    + (f" [{ci[0]:+.1f}, {ci[1]:+.1f}]" if ci[0] is not None else "") + "; regional, home prices, not a forecast")
        items.append({"label": "Regional tide", "value": f"S2 quintile {int(q)} of 5", "note": note})
    else:
        why = "outside universe B" if not _flag(row, "universe_B") else ("already moving" if not _flag(row, "quiet_now") else "not served")
        items.append({"label": "Regional tide", "value": "not in the quiet pool", "note": f"S2 applies to quiet universe-B counties ({why})"})

    y = _num(row, "fmr_gross_yield")
    band = _num(row, "rent_yield_pct_in_rucc_band")
    fy = _num(row, "fmr_fiscal_year")
    items.append({"label": "Gross rent yield", "value": f"{y:.1%}" if y is not None else "—",
                  "note": (f"top {100 * (1 - band):.0f}% of its rural–urban band" if band is not None else "no band read")
                          + (f" · HUD FMR FY{int(fy)}" if fy else " · HUD FMR")})

    nass = _num(row, "nass_land_value_per_acre")
    cheap = _num(row, "land_cheapness_pct")
    ly = _num(row, "nass_land_value_year")
    items.append({"label": "Farm land $/acre", "value": f"${nass:,.0f}" if nass is not None else "—",
                  "note": (f"cheaper than {cheap:.0%} of counties" if cheap is not None else "no cheapness read")
                          + (f" · NASS {int(ly)}" if ly else " · NASS")})

    aei = _num(row, "aei_land_value_per_acre")
    items.append({"label": "Residential land $/acre", "value": f"${aei:,.0f}" if aei is not None else "—",
                  "note": "AEI Housing Center land price, 2024 · observed"})

    pti = _num(row, "price_to_income")
    zhvi = _num(row, "zhvi_end")
    items.append({"label": "Price / income", "value": f"{pti:.1f}" if pti is not None else "—",
                  "note": (f"ZHVI ${zhvi:,.0f} (Zillow, 2025)" if zhvi is not None else "Zillow ZHVI") + " · observed"})

    cap = _num(row, "farm_cap_rate_proxy")
    g3 = breakeven_annual_growth(3, income_yield_per_year=cap or 0.0)
    items.append({"label": "Breakeven growth / yr", "value": f"{g3:+.1%}",
                  "note": "3-yr hold, 8% round trip + 1%/yr carry" + (f", farm cap-rate proxy {cap:.1%} as income" if cap else ", no income")
                          + " · arithmetic on stated assumptions"})

    risk = _num(row, "composite_risk")
    nri = _num(row, "nri_risk_score")
    items.append({"label": "Risk", "value": f"{risk:.0f}" if risk is not None else "—",
                  "note": (f"FEMA NRI {nri:.1f}" if nri is not None else "FEMA NRI —") + " · composite risk score, observed hazards"})

    bos = _num(row, "boom_onset_score")
    items.append({"label": "Classifier (research)", "value": f"{bos:.2f}" if bos is not None else "—",
                  "note": "resemblance score; 1.1× a random quiet county under live conditions — no live skill, never a headline"})
    return items


def investment_numbers_markdown(items: list[dict]) -> list[str]:
    return [f"- {it['label']}: `{it['value']}` — {it['note']}" for it in items]
