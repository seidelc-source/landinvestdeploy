"""Customer Story rendering helpers shared by the Streamlit dashboard."""

from __future__ import annotations

import html

import pandas as pd
import plotly.graph_objects as go


def customer_story_hero_html(
    *,
    county_display: str,
    thesis_read: str,
    tier: str,
    tier_color: str,
    strategy_rank: str,
    production_rank: str,
    risk_score: str,
) -> str:
    return f"""
<div class="customer-hero">
  <div class="customer-kicker">Customer Mode County Story</div>
  <h1>{html.escape(str(county_display))}</h1>
  <p>{html.escape(str(thesis_read))}</p>
  <div class="customer-hero-strip">
    <span style="border-color:{html.escape(str(tier_color))}; color:{html.escape(str(tier_color))};">{html.escape(str(tier))} signal</span>
    <span>Strategy {html.escape(str(strategy_rank))}</span>
    <span>Production {html.escape(str(production_rank))}</span>
    <span>Risk {html.escape(str(risk_score))}</span>
  </div>
</div>
"""


def customer_signal_radar_figure(signal_rows: pd.DataFrame, *, color: str) -> go.Figure:
    labels = signal_rows["Signal"].tolist()
    values = signal_rows["Score"].astype(float).tolist()
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values + [values[0]],
            theta=labels + [labels[0]],
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
    return fig


def customer_signal_table(signal_rows: pd.DataFrame) -> pd.DataFrame:
    view = signal_rows.copy()
    view["Score"] = view["Score"].map(lambda x: f"{float(x):.0f}")
    return view
