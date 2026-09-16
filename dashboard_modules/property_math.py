"""Property Analyzer arithmetic (plan P1.2, 2026-09-16) — closed-form, unit-tested, no model.

Every number the analyzer shows is either an observed county fact multiplied by the user's
acreage, or arithmetic on stated cost assumptions. The assumptions mirror the repo's own
underwriting conventions: an 8% round trip and 1%/yr carry (`scripts/screen_returns.py`) and
the TK2 cost stack (`scripts/build_tk2_offering_simulator.py`: closing, property tax, management,
vacancy, exit). Nothing here projects appreciation; the user supplies a growth path and the
functions report what that path would have to be to break even.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Defaults are the repo's stated conventions, exposed so the UI can show and let the user edit them.
ROUND_TRIP_COST = 0.08      # buy + sell friction as a share of price (screen_returns.py)
CARRY_PER_YEAR = 0.01       # taxes, insurance, upkeep as a share of price per year (screen_returns.py)
CLOSING_COST_EACH = 2_500.0  # title search/insurance + closing per parcel (TK2 A7)
PROPERTY_TAX_RATE = 0.010   # share of price per year (TK2 A12, AR-style; user-editable)
MANAGEMENT_PCT_RENT = 0.08  # share of gross rent (TK2 A10)
VACANCY_HAIRCUT = 0.10      # rent collection / vacancy (TK2 A11)
EXIT_COST_PCT = 0.06        # disposition costs at exit (TK2 A13)


def breakeven_annual_growth(hold_years: int, *, round_trip: float = ROUND_TRIP_COST,
                            carry_per_year: float = CARRY_PER_YEAR, income_yield_per_year: float = 0.0) -> float:
    """The constant annual price growth g that just clears costs over the hold, undiscounted:
    (1+g)^H - 1 + H*(income - carry) = round_trip  =>  g = (1 + round_trip + H*(carry - income))^(1/H) - 1.
    Negative means income alone already covers the friction (no appreciation needed)."""
    if hold_years <= 0:
        raise ValueError("hold_years must be positive")
    base = 1.0 + round_trip + hold_years * (carry_per_year - income_yield_per_year)
    if base <= 0:
        return -1.0
    return base ** (1.0 / hold_years) - 1.0


def income_ceiling_per_year(acres: float, cash_rent_per_acre: float | None, *, usable_share: float = 1.0,
                            management_pct: float = MANAGEMENT_PCT_RENT, vacancy: float = VACANCY_HAIRCUT) -> dict:
    """Gross and net income capacity from the county's cash rent (NASS, $/acre/yr) on the usable acres."""
    if cash_rent_per_acre is None or acres <= 0:
        return {"gross": None, "net": None, "usable_acres": max(acres, 0.0) * usable_share}
    usable = max(acres, 0.0) * max(min(usable_share, 1.0), 0.0)
    gross = usable * cash_rent_per_acre
    net = gross * (1.0 - management_pct) * (1.0 - vacancy)
    return {"gross": gross, "net": net, "usable_acres": usable}


def value_anchors(acres: float, *, farm_value_per_acre: float | None, residential_value_per_acre: float | None,
                  asking_price: float | None = None) -> dict:
    """County-level $/acre anchors multiplied by acreage — anchors, never an appraisal."""
    out = {"farm": None, "residential": None, "asking_per_acre": None}
    if acres > 0:
        if farm_value_per_acre is not None:
            out["farm"] = {"per_acre": farm_value_per_acre, "total": farm_value_per_acre * acres}
        if residential_value_per_acre is not None:
            out["residential"] = {"per_acre": residential_value_per_acre, "total": residential_value_per_acre * acres}
        if asking_price is not None:
            out["asking_per_acre"] = asking_price / acres
    return out


def irr(cashflows: list[float], *, lo: float = -0.99, hi: float = 5.0, tol: float = 1e-7) -> float | None:
    """Internal rate of return by bisection; None if the sign pattern gives no root."""
    def npv(rate: float) -> float:
        return sum(cf / (1.0 + rate) ** t for t, cf in enumerate(cashflows))
    f_lo, f_hi = npv(lo), npv(hi)
    if f_lo * f_hi > 0:
        return None
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        f_mid = npv(mid)
        if abs(f_mid) < tol:
            return mid
        if f_lo * f_mid < 0:
            hi, f_hi = mid, f_mid
        else:
            lo, f_lo = mid, f_mid
    return 0.5 * (lo + hi)


@dataclass
class VehicleEconomics:
    """Cash-flow arithmetic for one parcel held H years under a user-supplied growth path."""
    price: float
    hold_years: int
    annual_net_income: float = 0.0
    growth_path: list[float] = field(default_factory=list)   # per-year price growth, len >= hold_years (padded with last)
    closing_cost: float = CLOSING_COST_EACH
    tax_rate: float = PROPERTY_TAX_RATE
    exit_cost_pct: float = EXIT_COST_PCT
    other_carry_per_year: float = 0.0

    def run(self) -> dict:
        if self.price <= 0 or self.hold_years <= 0:
            raise ValueError("price and hold_years must be positive")
        path = list(self.growth_path) or [0.0]
        path = path + [path[-1]] * (self.hold_years - len(path))
        value = self.price
        flows = [-(self.price + self.closing_cost)]
        carry = self.price * self.tax_rate + self.other_carry_per_year
        for year in range(self.hold_years):
            value *= 1.0 + path[year]
            cf = self.annual_net_income - carry
            if year == self.hold_years - 1:
                cf += value * (1.0 - self.exit_cost_pct)
            flows.append(cf)
        total_in = self.price + self.closing_cost
        net_proceeds = value * (1.0 - self.exit_cost_pct)
        profit = sum(flows)
        return {
            "year1_net_yield": (self.annual_net_income - carry) / self.price,
            "fixed_cost_share_of_price": (self.closing_cost + self.price * self.exit_cost_pct) / self.price,
            "exit_value": value,
            "net_proceeds": net_proceeds,
            "total_profit": profit,
            "multiple_on_cost": (profit + total_in) / total_in,
            "irr": irr(flows),
            "breakeven_growth": breakeven_annual_growth(
                self.hold_years,
                round_trip=(self.closing_cost / self.price) + self.exit_cost_pct,
                carry_per_year=self.tax_rate + self.other_carry_per_year / self.price,
                income_yield_per_year=self.annual_net_income / self.price),
            "cashflows": flows,
        }
