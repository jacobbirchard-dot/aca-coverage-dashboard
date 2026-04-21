"""
Affordability
Premiums, subsidies, and what people actually pay.
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from data_loader import (
    load_benchmark_premiums,
    national_marketplace_totals,
)
from layout import render_sidebar, render_footer

st.set_page_config(page_title="Affordability | ACA Dashboard", page_icon="🏥", layout="wide")

render_sidebar()

COLORS = {
    "marketplace": "#2563EB",
    "medicaid": "#059669",
    "uninsured": "#DC2626",
    "accent": "#F59E0B",
    "text_muted": "#64748B",
    "subsidy": "#7C3AED",
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


# ── Data ─────────────────────────────────────────────────────────────────────
mkt = national_marketplace_totals()
bench = load_benchmark_premiums()

st.markdown("# Affordability")
st.markdown(
    "Enhanced subsidies have dramatically reduced what most Marketplace enrollees "
    "actually pay — even as sticker-price premiums have risen. But these subsidies "
    "are set to expire, and the 2026 numbers already show what could happen."
)

# ── Key metrics ──────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    aptc_2025 = mkt[mkt["year"] == 2025]["pct_with_aptc"].values[0]
    st.metric("% Receiving Subsidies (2025)", f"{aptc_2025:.0f}%")

with col2:
    after_2025 = mkt[mkt["year"] == 2025]["avg_premium_after_aptc"].values[0]
    st.metric("Avg. After-Subsidy Premium (2025)", f"${after_2025:.0f}/mo")

with col3:
    lte10_2025 = mkt[mkt["year"] == 2025]["premium_lte_10"].values[0]
    lte10_pct = lte10_2025 / mkt[mkt["year"] == 2025]["total_selections"].values[0] * 100
    st.metric("Enrollees Paying ≤$10/mo", f"{fmt_millions(lte10_2025)}", delta=f"{lte10_pct:.0f}% of total")


# ── Chart 1: Subsidy gap ────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### The Subsidy Gap")
st.markdown(
    "The gap between full premiums and what subsidized enrollees pay has widened "
    "since enhanced subsidies began. Watch the 2026 number — it shows a sharp "
    "increase in after-subsidy costs as enhanced subsidies face expiration."
)

fig_gap = go.Figure()

fig_gap.add_trace(go.Scatter(
    x=mkt["year"], y=mkt["avg_premium"],
    name="Avg. full premium",
    mode="lines+markers",
    line=dict(color=COLORS["text_muted"], width=2),
    marker=dict(size=8),
))

fig_gap.add_trace(go.Scatter(
    x=mkt["year"], y=mkt["avg_premium_after_aptc"],
    name="Avg. after subsidies",
    mode="lines+markers",
    line=dict(color=COLORS["marketplace"], width=3),
    marker=dict(size=10),
    fill="tonexty",
    fillcolor="rgba(124, 58, 237, 0.08)",
))

fig_gap.update_layout(
    **PLOT_LAYOUT,
    height=400,
    yaxis=dict(title="Avg. monthly premium", gridcolor="#E2E8F0", tickprefix="$"),
    xaxis=dict(dtick=1),
)
st.plotly_chart(fig_gap, use_container_width=True)


# ── Chart 2: $10-or-less enrollees ───────────────────────────────────────────
st.markdown("### The $10-or-Less Club")
st.markdown(
    "The number of people paying $10 or less per month exploded after enhanced "
    "subsidies took effect — then dropped sharply in 2026 projections."
)

lte10_data = mkt[mkt["year"] >= 2022].copy()

fig_10 = go.Figure()
fig_10.add_trace(go.Bar(
    x=lte10_data["year"],
    y=lte10_data["premium_lte_10"],
    marker_color=[
        COLORS["accent"] if y <= 2025 else COLORS["uninsured"] for y in lte10_data["year"]
    ],
    text=[fmt_millions(v) for v in lte10_data["premium_lte_10"]],
    textposition="outside",
    textfont=dict(size=13),
    hovertemplate="%{x}: %{customdata}<extra></extra>",
    customdata=[fmt_millions(v) for v in lte10_data["premium_lte_10"]],
))

fig_10.update_layout(
    **PLOT_LAYOUT,
    height=380,
    yaxis=dict(title="Enrollees paying ≤$10/mo", gridcolor="#E2E8F0", showticklabels=False),
    xaxis=dict(dtick=1),
    showlegend=False,
)
st.plotly_chart(fig_10, use_container_width=True)


# ── Chart 3: Benchmark premiums by state ─────────────────────────────────────
st.markdown("---")
st.markdown("### Benchmark Premium Trends")
st.markdown(
    "The benchmark (second-lowest silver plan) premium determines subsidy amounts. "
    "Compare how benchmark costs have changed nationally or in specific states."
)

# Build state selection options: National first, then alphabetical states
all_bench_states = sorted(bench[bench["state"] != "United States"]["state"].unique())
state_options = ["United States (National)"] + all_bench_states

selected_bench_states = st.multiselect(
    "Select states to compare",
    options=state_options,
    default=["United States (National)"],
    max_selections=6,
)

# Map display names back to data values
selected_mapped = [
    "United States" if s == "United States (National)" else s
    for s in selected_bench_states
]

if selected_mapped:
    bench_filtered = bench[bench["state"].isin(selected_mapped)].sort_values("year")

    fig_bench = go.Figure()

    for state_name in selected_mapped:
        state_data = bench_filtered[bench_filtered["state"] == state_name]
        display_name = "National" if state_name == "United States" else state_name

        # Make national line bolder
        is_national = state_name == "United States"
        fig_bench.add_trace(go.Scatter(
            x=state_data["year"],
            y=state_data["avg_benchmark_premium"],
            mode="lines+markers" + ("+text" if len(selected_mapped) == 1 else ""),
            name=display_name,
            text=[f"${int(v)}" for v in state_data["avg_benchmark_premium"]] if len(selected_mapped) == 1 else None,
            textposition="top center" if len(selected_mapped) == 1 else None,
            textfont=dict(size=12, color=COLORS["subsidy"]) if len(selected_mapped) == 1 else None,
            line=dict(
                width=3 if is_national else 2,
                dash=None if is_national else None,
            ),
            marker=dict(size=10 if is_national else 7),
            hovertemplate=f"{display_name}<br>%{{x}}: $%{{y:.0f}}/mo<extra></extra>",
        ))

    fig_bench.update_layout(
        **PLOT_LAYOUT,
        height=420,
        yaxis=dict(title="Avg. benchmark premium", gridcolor="#E2E8F0", tickprefix="$"),
        xaxis=dict(dtick=1),
    )
    st.plotly_chart(fig_bench, use_container_width=True)
else:
    st.info("Select at least one state or 'United States (National)' to see benchmark trends.")


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "*Methodology note: Premium data from CMS Open Enrollment Public Use Files. Benchmark premiums are "
    "the second-lowest cost silver plan, which determines subsidy eligibility. "
    "2026 figures reflect plans filed for the upcoming year; actual subsidies depend "
    "on Congressional action to extend enhanced premium tax credits.*"
)
render_footer()
