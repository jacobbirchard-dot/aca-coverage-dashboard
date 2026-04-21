"""
ACA Coverage Dashboard — National
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from data_loader import (
    load_nhis_national,
    national_marketplace_totals,
    national_medicaid_monthly,
)
from layout import render_sidebar, render_footer

st.set_page_config(
    page_title="ACA Coverage Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

COLORS = {
    "marketplace": "#2563EB",
    "medicaid": "#059669",
    "uninsured": "#DC2626",
    "accent": "#F59E0B",
    "text_muted": "#64748B",
}

PLOT_LAYOUT = dict(
    font=dict(family="DM Sans, sans-serif", size=13, color="#1E293B"),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=40, r=20, t=40, b=40),
    hoverlabel=dict(bgcolor="white", font_size=13),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)


def fmt_millions(n):
    if pd.isna(n):
        return "N/A"
    return f"{n / 1e6:.1f}M"


def fmt_pct(n):
    if pd.isna(n):
        return "N/A"
    return f"{n:.1f}%"


render_sidebar()

# ══════════════════════════════════════════════════════════════════════════════
# NATIONAL VIEW
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("# The National Coverage Story")
st.markdown(
    "From 2020 to 2025, U.S. health coverage shifted dramatically — driven by "
    "pandemic-era Medicaid protections, expanded ACA subsidies, and the largest "
    "Marketplace enrollment surge in history."
)

# ── Load data ────────────────────────────────────────────────────────────────
nhis = load_nhis_national()
nhis_all = nhis[nhis["age_group"] == "All ages"].sort_values("year")
mkt = national_marketplace_totals()
med = national_medicaid_monthly()

# ── Key metrics ──────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    latest_mp = mkt[mkt["year"] == 2025]["total_selections"].values[0]
    first_mp = mkt[mkt["year"] == 2020]["total_selections"].values[0]
    st.metric(
        "Marketplace Enrollment (2025)",
        fmt_millions(latest_mp),
        delta=f"+{fmt_millions(latest_mp - first_mp)} since 2020",
    )

with col2:
    peak_med = med["total_enrollment"].max()
    latest_med = med.iloc[-1]["total_enrollment"]
    st.metric(
        "Medicaid/CHIP Peak (Apr 2023)",
        fmt_millions(peak_med),
        delta=f"{fmt_millions(latest_med - peak_med)} since peak",
        delta_color="inverse",
    )

with col3:
    low_unins = nhis_all["uninsured_pct"].min()
    low_year = nhis_all.loc[nhis_all["uninsured_pct"].idxmin(), "year"]
    latest_unins = nhis_all.iloc[-1]["uninsured_pct"]
    st.metric(
        f"Uninsured Rate Low ({int(low_year)})",
        fmt_pct(low_unins),
        delta=f"+{latest_unins - low_unins:.1f}pp by 2024",
        delta_color="inverse",
    )

with col4:
    lte10 = mkt[mkt["year"] == 2025]["premium_lte_10"].values[0]
    st.metric(
        "Paying ≤$10/mo (2025)",
        fmt_millions(lte10),
        delta="42% of enrollees",
    )


# ── Chart 1: Uninsured rate ─────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Uninsured Rate, 2020–2024")
st.markdown(
    "The uninsured rate fell to a historic low of 7.6% in 2023, then ticked back up "
    "in 2024 as Medicaid's pandemic-era continuous enrollment protections ended "
    "and states began redetermining eligibility."
)

fig_unins = go.Figure()
fig_unins.add_trace(go.Scatter(
    x=nhis_all["year"],
    y=nhis_all["uninsured_pct"],
    mode="lines+markers+text",
    text=[f"{v}%" for v in nhis_all["uninsured_pct"]],
    textposition="top center",
    textfont=dict(size=14, color=COLORS["uninsured"]),
    line=dict(color=COLORS["uninsured"], width=3),
    marker=dict(size=10),
    name="Uninsured rate",
    hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
))

fig_unins.add_annotation(
    x=2024, y=8.2,
    text="Medicaid unwinding<br>begins",
    showarrow=True, arrowhead=2,
    ax=60, ay=-40,
    font=dict(size=11, color=COLORS["text_muted"]),
    arrowcolor=COLORS["text_muted"],
)
fig_unins.add_annotation(
    x=2021, y=9.2,
    text="ARP enhanced<br>subsidies begin",
    showarrow=True, arrowhead=2,
    ax=-60, ay=-40,
    font=dict(size=11, color=COLORS["text_muted"]),
    arrowcolor=COLORS["text_muted"],
)

fig_unins.update_layout(
    **PLOT_LAYOUT,
    yaxis=dict(
        title="% uninsured (all ages)",
        range=[5, 11],
        gridcolor="#E2E8F0",
        ticksuffix="%",
    ),
    xaxis=dict(dtick=1, gridcolor="#E2E8F0"),
    height=380,
    showlegend=False,
)
st.plotly_chart(fig_unins, use_container_width=True)


# ── Chart 2: Marketplace enrollment surge ────────────────────────────────────
st.markdown("### Marketplace Enrollment Surge")
st.markdown(
    "ACA Marketplace plan selections more than doubled from 2020 to 2025, driven by "
    "enhanced premium subsidies under the American Rescue Plan (2021) and Inflation "
    "Reduction Act (2022). The 2026 figure reflects early OE data."
)

fig_mp = go.Figure()
fig_mp.add_trace(go.Bar(
    x=mkt["year"],
    y=mkt["total_selections"],
    marker_color=[
        COLORS["marketplace"] if y <= 2025 else "#93C5FD" for y in mkt["year"]
    ],
    text=[fmt_millions(v) for v in mkt["total_selections"]],
    textposition="outside",
    textfont=dict(size=13, color=COLORS["marketplace"]),
    hovertemplate="%{x}: %{text}<extra></extra>",
))

fig_mp.add_vrect(
    x0=2020.5, x1=2025.5,
    fillcolor=COLORS["marketplace"], opacity=0.04,
    layer="below", line_width=0,
)
fig_mp.add_annotation(
    x=2023, y=mkt[mkt["year"] == 2025]["total_selections"].values[0] * 0.95,
    text="Enhanced ACA subsidies in effect (ARP / IRA)",
    showarrow=False,
    font=dict(size=11, color=COLORS["text_muted"]),
)

fig_mp.update_layout(
    **PLOT_LAYOUT,
    yaxis=dict(title="Plan selections", gridcolor="#E2E8F0", showticklabels=False),
    xaxis=dict(dtick=1),
    height=400,
    showlegend=False,
)
st.plotly_chart(fig_mp, use_container_width=True)


# ── Chart 3: Medicaid Down, Marketplace Up (dual-axis) ──────────────────────
st.markdown("### Medicaid Down, Marketplace Up")
st.markdown(
    "As states unwound pandemic Medicaid protections, Marketplace enrollment surged "
    "to absorb many of those losing coverage. But the timing didn't perfectly align — "
    "gaps in coverage are reflected in the 2024 uninsured rate increase."
)

fig_seesaw = go.Figure()

# Medicaid monthly on left axis
fig_seesaw.add_trace(go.Scatter(
    x=med["date"],
    y=med["total_enrollment"],
    mode="lines",
    name="Medicaid/CHIP (monthly)",
    fill="tozeroy",
    line=dict(color=COLORS["medicaid"], width=2),
    fillcolor="rgba(5, 150, 105, 0.1)",
    yaxis="y",
    hovertemplate="%{x|%b %Y}: %{customdata}<extra>Medicaid/CHIP</extra>",
    customdata=[fmt_millions(v) for v in med["total_enrollment"]],
))

# Marketplace annual on right axis
fig_seesaw.add_trace(go.Bar(
    x=[pd.Timestamp(f"{y}-01-15") for y in mkt["year"]],
    y=mkt["total_selections"],
    name="Marketplace selections (annual)",
    marker_color=COLORS["marketplace"],
    opacity=0.7,
    width=86400000 * 120,
    yaxis="y2",
    hovertemplate="%{customdata}<extra>Marketplace</extra>",
    customdata=[f"{y}: {fmt_millions(v)}" for y, v in zip(mkt["year"], mkt["total_selections"])],
))

fig_seesaw.add_vline(
    x=pd.Timestamp("2023-04-01").timestamp() * 1000,
    line_dash="dash", line_color=COLORS["text_muted"], line_width=1,
)
fig_seesaw.add_annotation(
    x="2023-04-01",
    y=med["total_enrollment"].max() * 1.02,
    text="Unwinding begins →",
    showarrow=False,
    font=dict(size=11, color=COLORS["text_muted"]),
)

med_max = med["total_enrollment"].max()
mkt_max = mkt["total_selections"].max()

fig_seesaw.update_layout(
    **PLOT_LAYOUT,
    height=450,
    yaxis=dict(
        title=dict(text="Medicaid/CHIP enrollment", font=dict(color=COLORS["medicaid"])),
        gridcolor="#E2E8F0",
        tickformat=",.0s",
        range=[0, med_max * 1.15],
    ),
    yaxis2=dict(
        title=dict(text="Marketplace plan selections", font=dict(color=COLORS["marketplace"])),
        overlaying="y",
        side="right",
        tickformat=",.0s",
        range=[0, mkt_max * 1.4],
        showgrid=False,
    ),
    xaxis=dict(gridcolor="#E2E8F0"),
)
st.plotly_chart(fig_seesaw, use_container_width=True)


# ── Footer ────────────────────────────────────────────────────────────────────
render_footer()
