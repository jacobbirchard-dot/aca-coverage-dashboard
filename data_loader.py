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
def load_medicaid_monthly():
    df = pd.read_csv(DATA_DIR / "medicaid_enrollment.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df


@st.cache_data
def load_marketplace():
    return pd.read_csv(DATA_DIR / "marketplace_enrollment.csv")


@st.cache_data
def load_effectuated():
    df = pd.read_csv(DATA_DIR / "effectuated_enrollment.csv")
    return df.dropna(subset=["effectuated_enrollment"])


@st.cache_data
def load_benchmark_premiums():
    return pd.read_csv(DATA_DIR / "benchmark_premiums.csv")


@st.cache_data
def load_state_attributes():
    return pd.read_csv(DATA_DIR / "reference_state_attributes.csv")


# ── National aggregates ──────────────────────────────────────────────────────

@st.cache_data
def national_marketplace_totals():
    mp = load_marketplace()

    def weighted(group, col, weight_col="total_plan_selections"):
        mask = group[col].notna() & group[weight_col].notna()
        weights = group.loc[mask, weight_col]
        if weights.sum() == 0:
            return pd.NA
        return (group.loc[mask, col] * weights).sum() / weights.sum()

    def subsidized_full_premium(group):
        # For APTC recipients: full premium = APTC amount + after-APTC premium.
        # Weight each state's contribution by its aptc_consumers.
        mask = (
            group["aptc_avg_amount"].notna()
            & group["aptc_avg_premium_after"].notna()
            & group["aptc_consumers"].notna()
        )
        if mask.sum() == 0 or group.loc[mask, "aptc_consumers"].sum() == 0:
            return pd.NA
        full = group.loc[mask, "aptc_avg_amount"] + group.loc[mask, "aptc_avg_premium_after"]
        weights = group.loc[mask, "aptc_consumers"]
        return (full * weights).sum() / weights.sum()

    agg = mp.groupby("year").apply(
        lambda g: pd.Series({
            "total_selections": g["total_plan_selections"].sum(),
            "avg_premium": weighted(g, "avg_monthly_premium"),
            "avg_premium_after_aptc": weighted(g, "avg_premium_after_aptc"),
            "pct_with_aptc": weighted(g, "pct_with_aptc"),
            "premium_lte_10": g["premium_lte_10"].sum(),
            "subsidized_full_premium": subsidized_full_premium(g),
            "subsidized_after_aptc": weighted(g, "aptc_avg_premium_after", "aptc_consumers"),
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
