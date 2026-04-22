"""
Data loader for ACA Coverage Dashboard.
Loads all CSV files and computes national aggregations used across pages.
"""
import pandas as pd
import streamlit as st
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


@st.cache_data
def load_master_panel():
    df = pd.read_csv(DATA_DIR / "master_state_year_panel.csv")
    df["expanded_medicaid"] = df["expanded_medicaid"].astype(bool)
    df["trump_2024"] = df["trump_2024"].astype(bool)
    return df


@st.cache_data
def load_nhis_national():
    return pd.read_csv(DATA_DIR / "nhis_national_coverage.csv")


@st.cache_data
def load_nhis_exchange():
    return pd.read_csv(DATA_DIR / "nhis_exchange_coverage.csv")


@st.cache_data
def load_medicaid_monthly():
    df = pd.read_csv(DATA_DIR / "medicaid_enrollment.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df


@st.cache_data
def load_marketplace():
    return pd.read_csv(DATA_DIR / "marketplace_enrollment.csv")


@st.cache_data
def load_effectuated():
    return pd.read_csv(DATA_DIR / "effectuated_enrollment.csv")


@st.cache_data
def load_benchmark_premiums():
    return pd.read_csv(DATA_DIR / "benchmark_premiums.csv")


@st.cache_data
def load_census_state():
    return pd.read_csv(DATA_DIR / "census_state_coverage.csv")


@st.cache_data
def load_census_county():
    return pd.read_csv(DATA_DIR / "census_county_coverage.csv")


@st.cache_data
def load_state_attributes():
    return pd.read_csv(DATA_DIR / "reference_state_attributes.csv")


@st.cache_data
def load_oe_2026():
    return pd.read_csv(DATA_DIR / "oe_2026_selections.csv")


@st.cache_data
def load_fpl_thresholds():
    return pd.read_csv(DATA_DIR / "reference_fpl_thresholds.csv")


# ── National aggregates ──────────────────────────────────────────────────────

@st.cache_data
def national_marketplace_totals():
    mp = load_marketplace()

    def weighted(group, col):
        mask = group[col].notna() & group["total_plan_selections"].notna()
        weights = group.loc[mask, "total_plan_selections"]
        if weights.sum() == 0:
            return pd.NA
        return (group.loc[mask, col] * weights).sum() / weights.sum()

    agg = mp.groupby("year").apply(
        lambda g: pd.Series({
            "total_selections": g["total_plan_selections"].sum(),
            "avg_premium": weighted(g, "avg_monthly_premium"),
            "avg_premium_after_aptc": weighted(g, "avg_premium_after_aptc"),
            "pct_with_aptc": weighted(g, "pct_with_aptc"),
            "premium_lte_10": g["premium_lte_10"].sum(),
        }),
        include_groups=False,
    ).round(1).reset_index()
    return agg


@st.cache_data
def national_medicaid_monthly():
    med = load_medicaid_monthly()
    med = med[med["state"] != "United States"]
    agg = med.groupby(["date", "year", "month"]).agg(
        total_enrollment=("total_enrollment", "sum"),
        medicaid_enrollment=("medicaid_enrollment", "sum"),
        chip_enrollment=("chip_enrollment", "sum"),
    ).reset_index().sort_values("date")
    return agg
