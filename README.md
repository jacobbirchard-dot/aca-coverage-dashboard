# ACA Coverage Dashboard

An interactive Streamlit dashboard exploring U.S. health insurance coverage trends from 2020 to 2025 — across ACA Marketplace enrollment, Medicaid/CHIP, and the uninsured population.

## Pages

1. **National — The National Coverage Story**: Key metrics, uninsured rate trends, coverage by type, marketplace enrollment surge, Medicaid monthly enrollment, and premium affordability.
2. **State**: Interactive state comparisons with filters for Medicaid expansion status. Includes marketplace enrollment, uninsured rates, expansion vs. non-expansion scatter, and growth rankings.
3. **Coverage Seesaw**: Visualizes the Medicaid-to-Marketplace transition during the 2023–2024 unwinding. Dual-axis time series, state-level scatter showing who caught the falloff, and per-state Medicaid drilldown.
4. **Affordability**: Premium trends, the subsidy gap, the "$10 or less" phenomenon, state-level premium comparisons, and benchmark premium trends showing the 2026 cliff.

## Data Sources

- **CMS** Open Enrollment Public Use Files (plan selections, premiums, demographics)
- **Data.Medicaid.gov** monthly Medicaid/CHIP enrollment
- **Census Bureau ACS** state and county uninsured rates and coverage by type
- **CDC/NHIS** national coverage estimates by age group

## Run Locally

```bash
pip install -r requirements.txt
streamlit run National.py
```

## Deploy to Streamlit Community Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set the main file to `National.py`
5. Deploy

## Project Structure

```
aca-dashboard/
├── National.py                # Main page: national coverage story
├── data_loader.py             # Centralized data loading & caching
├── requirements.txt
├── .streamlit/
│   └── config.toml            # Theme & server config
├── data/                      # All cleaned CSV data files
│   ├── master_state_year_panel.csv
│   ├── marketplace_enrollment.csv
│   ├── medicaid_enrollment.csv
│   ├── nhis_national_coverage.csv
│   ├── benchmark_premiums.csv
│   ├── effectuated_enrollment.csv
│   └── reference_state_attributes.csv
└── pages/
    ├── 1_State.py
    ├── 2_Coverage_Seesaw.py
    └── 3_Affordability.py
```
