"""
Shared layout components: sidebar and footer with proper data citations.
"""
import streamlit as st


def render_sidebar():
    with st.sidebar:
        st.markdown("## 🏥 ACA Coverage Dashboard")
        st.markdown(
            "Exploring U.S. health insurance coverage trends from 2020 to 2025 — "
            "across ACA Marketplace enrollment, Medicaid, and the uninsured population."
        )

        st.markdown("---")
        st.markdown("#### Data Sources")
        st.markdown(
            "**Marketplace enrollment:** Centers for Medicare & Medicaid Services (CMS), "
            "[Open Enrollment Public Use Files](https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products), "
            "2020–2026."
        )
        st.markdown(
            "**Medicaid/CHIP enrollment:** CMS, "
            "[Data.Medicaid.gov](https://data.medicaid.gov/dataset/6jey-9bgk), "
            "monthly enrollment reports."
        )
        st.markdown(
            "**National coverage estimates:** National Center for Health Statistics, "
            "[National Health Interview Survey](https://www.cdc.gov/nchs/nhis/) (NHIS), "
            "Early Release Program."
        )
        st.markdown(
            "**State & county coverage:** U.S. Census Bureau, "
            "[American Community Survey](https://data.census.gov/table/ACSST1Y2023.S2701), "
            "Table S2701, 1-Year and 5-Year Estimates."
        )
        st.markdown(
            "**Additional state-level data:** "
            "[KFF](https://www.kff.org/state-health-facts/), State Health Facts."
        )

        st.markdown("---")
        st.caption(
            "Built with [Streamlit](https://streamlit.io) · "
            "[View on GitHub](https://github.com/jacobbirchard-dot/aca-coverage-dashboard)"
        )


def render_footer():
    st.markdown("---")
    st.caption(
        "**Sources:** Marketplace enrollment from Centers for Medicare & Medicaid Services (CMS), "
        "Open Enrollment Public Use Files, 2020–2026. Medicaid/CHIP enrollment from CMS, Data.Medicaid.gov. "
        "National uninsured rates and coverage shares from National Center for Health Statistics, "
        "National Health Interview Survey. State and county coverage from U.S. Census Bureau, "
        "American Community Survey, Table S2701. Additional state data from KFF, State Health Facts."
    )
    st.caption(
        "*Analysis, visualizations, and conclusions are the author's own and do not represent "
        "the views of CMS, CDC/NCHS, the U.S. Census Bureau, or KFF.*"
    )
