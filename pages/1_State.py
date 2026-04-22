"""
State
Interactive state-level comparisons for marketplace, medicaid, and uninsured data.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from data_loader import (
    load_effectuated,
    load_master_panel,
    load_state_attributes,
)
from layout import render_sidebar, render_footer

st.set_page_config(page_title="State | ACA Dashboard", page_icon="🏥", layout="wide")

render_sidebar()

COLORS = {
    "marketplace": "#2563EB",
    "medicaid": "#059669",
    "uninsured": "#DC2626",
    "private": "#7C3AED",
    "accent": "#F59E0B",
    "text_muted": "#64748B",
    "expanded": "#059669",
    "not_expanded": "#DC2626",
}

PLOT_LAYOUT = dict(
    font=dict(family="DM Sans, sans-serif", size=13, color="#1E293B"),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=40, r=20, t=40, b=40),
    hoverlabel=dict(bgcolor="white", font_size=13),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)

# ── Load data ────────────────────────────────────────────────────────────────
panel = load_master_panel()
attrs = load_state_attributes()

st.markdown("# State")
st.markdown(
    "Compare coverage trends across states. Select states below or filter by "
    "Medicaid expansion status to see how policy choices shaped outcomes."
)

# ── Filters ──────────────────────────────────────────────────────────────────
col_filter1, col_filter2 = st.columns([3, 1])

with col_filter1:
    all_states = sorted(panel["state"].unique())
    default_states = ["California", "Texas", "Florida", "New York", "Ohio"]
    selected_states = st.multiselect(
        "Select states to compare",
        options=all_states,
        default=[s for s in default_states if s in all_states],
        max_selections=8,
    )

with col_filter2:
    expansion_filter = st.radio(
        "Medicaid expansion",
        ["All", "Expanded", "Not expanded"],
        horizontal=True,
    )

# Apply expansion filter
if expansion_filter == "Expanded":
    filtered = panel[panel["expanded_medicaid"] == True]
elif expansion_filter == "Not expanded":
    filtered = panel[panel["expanded_medicaid"] == False]
else:
    filtered = panel.copy()

# Narrow to selected states if any
if selected_states:
    state_data = filtered[filtered["state"].isin(selected_states)]
else:
    state_data = filtered.copy()
    selected_states = list(filtered["state"].unique())


# ── Chart 1: Marketplace enrollment by state ──────────────────────────────────
st.markdown("---")
st.markdown("### Marketplace Plan Selections by State")

if len(selected_states) <= 8:
    fig_mp = px.line(
        state_data.sort_values("year"),
        x="year", y="total_plan_selections",
        color="state",
        markers=True,
        hover_data={"total_plan_selections": ":,.0f"},
        labels={"total_plan_selections": "Plan selections", "year": "Year", "state": "State"},
    )
    fig_mp.update_layout(**PLOT_LAYOUT, height=420,
        yaxis=dict(gridcolor="#E2E8F0", tickformat=",.0s"),
        xaxis=dict(dtick=1),
    )
    st.plotly_chart(fig_mp, use_container_width=True)
else:
    st.info("Select up to 8 states to see the line chart, or use the expansion filter.")


# ── Chart 2: Uninsured rate by state ──────────────────────────────────────────
st.markdown("### Uninsured Rate by State")

unins_data = state_data.dropna(subset=["uninsured_rate"])
if not unins_data.empty and len(selected_states) <= 8:
    fig_ur = px.line(
        unins_data.sort_values("year"),
        x="year", y="uninsured_rate",
        color="state",
        markers=True,
        labels={"uninsured_rate": "Uninsured rate (%)", "year": "Year", "state": "State"},
    )
    fig_ur.update_layout(**PLOT_LAYOUT, height=420,
        yaxis=dict(gridcolor="#E2E8F0", ticksuffix="%"),
        xaxis=dict(dtick=1),
    )
    st.plotly_chart(fig_ur, use_container_width=True)
    st.caption(
        "Source: U.S. Census Bureau, American Community Survey (ACS), Table S2701. "
        "State-level uninsured rates use ACS methodology, which differs from the NHIS "
        "figures shown on the National page — figures are not directly comparable."
    )
elif unins_data.empty:
    st.info("Uninsured rate data is available for 2021–2024.")
else:
    st.info("Select up to 8 states to see the line chart.")


# ── Chart 3: Expansion vs. non-expansion scatter ─────────────────────────────
st.markdown("---")
st.markdown("### Medicaid Expansion and the Uninsured Rate")

_intro_2023 = panel[panel["year"] == 2023].dropna(subset=["uninsured_rate"])
_exp_mean = _intro_2023[_intro_2023["expanded_medicaid"]]["uninsured_rate"].mean()
_nonexp_mean = _intro_2023[~_intro_2023["expanded_medicaid"]]["uninsured_rate"].mean()
st.markdown(
    f"States that expanded Medicaid under the ACA consistently have lower uninsured rates. "
    f"In 2023, expansion states averaged a {_exp_mean:.1f}% uninsured rate vs. "
    f"{_nonexp_mean:.1f}% in non-expansion states."
)

scatter_year = st.select_slider(
    "Year", options=[2021, 2022, 2023, 2024], value=2023
)

scatter_data = panel[panel["year"] == scatter_year].dropna(subset=["uninsured_rate"])
scatter_data["expansion_label"] = scatter_data["expanded_medicaid"].map(
    {True: "Expanded Medicaid", False: "Did not expand"}
)

fig_scatter = px.strip(
    scatter_data,
    x="expansion_label",
    y="uninsured_rate",
    color="expansion_label",
    hover_name="state",
    hover_data={"uninsured_rate": ":.1f", "expansion_label": False},
    color_discrete_map={
        "Expanded Medicaid": COLORS["expanded"],
        "Did not expand": COLORS["not_expanded"],
    },
    labels={"uninsured_rate": "Uninsured rate (%)", "expansion_label": ""},
    stripmode="overlay",
)

# Add mean lines
for expand_val, label, color in [
    (True, "Expanded Medicaid", COLORS["expanded"]),
    (False, "Did not expand", COLORS["not_expanded"]),
]:
    mean_val = scatter_data[scatter_data["expanded_medicaid"] == expand_val]["uninsured_rate"].mean()
    fig_scatter.add_shape(
        type="line",
        x0=-0.3 if expand_val else 0.7,
        x1=0.3 if expand_val else 1.3,
        y0=mean_val, y1=mean_val,
        xref="x", yref="y",
        line=dict(color=color, width=2, dash="dash"),
    )
    fig_scatter.add_annotation(
        x=label,
        y=mean_val + 0.5,
        text=f"Mean: {mean_val:.1f}%",
        showarrow=False,
        font=dict(size=12, color=color),
    )

fig_scatter.update_traces(marker=dict(size=10, opacity=0.7))
fig_scatter.update_layout(
    **PLOT_LAYOUT,
    height=450,
    showlegend=False,
    yaxis=dict(title="Uninsured rate (%)", gridcolor="#E2E8F0", ticksuffix="%"),
)
st.plotly_chart(fig_scatter, use_container_width=True)
st.caption(
    "Source: U.S. Census Bureau, American Community Survey (ACS), Table S2701. "
    "ACS state-level uninsured rates differ from NHIS national estimates in methodology "
    "and reference period."
)


# ── Chart 4: Marketplace growth ranking ───────────────────────────────────────
st.markdown("---")
st.markdown("### Marketplace Growth Since 2020")
st.markdown("Which states saw the biggest surge in ACA enrollment?")

growth = panel[panel["year"] == 2025].dropna(subset=["growth_since_2020_pct"])
growth = growth.nlargest(20, "growth_since_2020_pct").sort_values("growth_since_2020_pct")

eff = load_effectuated()[["state", "effectuated_enrollment"]]
growth = growth.merge(eff, on="state", how="left")


def fmt_eff(v):
    if pd.isna(v):
        return "N/A"
    if v >= 1e6:
        return f"{v / 1e6:.1f}M"
    return f"{v / 1e3:.0f}K"


fig_growth = make_subplots(
    rows=1, cols=2,
    column_widths=[0.8, 0.2],
    shared_yaxes=True,
    horizontal_spacing=0.02,
)

fig_growth.add_trace(go.Bar(
    y=growth["state"],
    x=growth["growth_since_2020_pct"],
    orientation="h",
    marker_color=[
        COLORS["expanded"] if exp else COLORS["not_expanded"]
        for exp in growth["expanded_medicaid"]
    ],
    text=[f"{v:.0f}%" for v in growth["growth_since_2020_pct"]],
    textposition="outside",
    textfont=dict(size=11),
    hovertemplate="%{y}: %{x:.1f}% growth<extra></extra>",
), row=1, col=1)

fig_growth.add_trace(go.Scatter(
    y=growth["state"],
    x=[0] * len(growth),
    mode="text",
    text=[fmt_eff(v) for v in growth["effectuated_enrollment"]],
    textfont=dict(size=12, color="#1E293B"),
    textposition="middle right",
    hoverinfo="skip",
    showlegend=False,
), row=1, col=2)

fig_growth.update_layout(
    **PLOT_LAYOUT,
    height=550,
    showlegend=False,
)
fig_growth.update_xaxes(
    title_text="% growth in plan selections (2020→2025)",
    gridcolor="#E2E8F0", ticksuffix="%",
    row=1, col=1,
)
fig_growth.update_xaxes(
    title_text="2025 Effectuated",
    showticklabels=False, showgrid=False, zeroline=False,
    range=[-0.5, 1],
    row=1, col=2,
)
fig_growth.update_yaxes(tickfont=dict(size=11), row=1, col=1)
st.plotly_chart(fig_growth, use_container_width=True)
st.caption("🟢 Expanded Medicaid  🔴 Did not expand · Effectuated column shows 2025 (latest available).")


# ── Data table ────────────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("📊 View raw state data"):
    display_cols = [
        "state", "year", "total_plan_selections", "medicaid_chip_enrollment",
        "uninsured_rate", "avg_monthly_premium", "avg_premium_after_aptc",
        "pct_with_aptc", "expanded_medicaid",
    ]
    display_data = state_data[display_cols].sort_values(["state", "year"])
    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "total_plan_selections": st.column_config.NumberColumn("Marketplace", format="%d"),
            "medicaid_chip_enrollment": st.column_config.NumberColumn("Medicaid/CHIP", format="%d"),
            "uninsured_rate": st.column_config.NumberColumn("Uninsured %", format="%.1f%%"),
            "avg_monthly_premium": st.column_config.NumberColumn("Avg Premium", format="$%d"),
            "avg_premium_after_aptc": st.column_config.NumberColumn("After Subsidy", format="$%d"),
            "pct_with_aptc": st.column_config.NumberColumn("% w/ APTC", format="%.1f%%"),
        },
    )

render_footer()
