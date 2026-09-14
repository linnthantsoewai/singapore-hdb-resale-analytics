# Singapore HDB Resale Analytics (1990–2026)

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Dataset](https://img.shields.io/badge/Dataset-986%2C548%20Transactions-blue)](#)
[![Coverage](https://img.shields.io/badge/Coverage-36%20Years%20(1990--2026)-green)](#)
[![Pytest](https://img.shields.io/badge/Pytest-8%2F8%20Passing-brightgreen?logo=pytest&logoColor=white)](https://docs.pytest.org/)

An empirical real estate data analytics project analyzing the complete **36-year history of Singapore public housing (986,548 transactions from 1990 through 2026)**. 

Using **PostgreSQL 16** as the analytical engine and **Streamlit** for interactive presentation, this study answers 5 foundational questions about how property value, lease depreciation, inflation, and government policy interact in Singapore.

---

## 🔍 The 5 Core Analytical Discoveries

### 1. The Lease Decay Cliff (The 60-Year Financing Shock)
* **The Question:** Does an HDB flat's value decline smoothly as its 99-year lease ticks down, or does it hit an abrupt cliff?
* **The Finding:** Value does **not** decay smoothly. In Singapore, commercial banks cap mortgage tenures and CPF usage limits tighten once a flat has fewer than 60 years remaining on its lease. This creates a severe financing cliff:
  - In **Queenstown (4-Room)**, flats with 60–64 years remaining averaged **$8,147/sqm** ($730k). The moment they crossed into 55–59 years, prices dropped by **-26.4%** to **$5,994/sqm** ($445k).
  - In **Ang Mo Kio (4-Room)**, prices plunged by **-28.5%** approaching the threshold.
  - In **Queenstown (3-Room)**, median prices dropped by **-49.6%** ($10k/sqm down to $5k/sqm).
* **Takeaway:** Regulatory loan and CPF restrictions create sharp pricing drops that overpower gradual theoretical depreciation models.

### 2. Real vs. Nominal Price Growth (Inflation Drag)
* **The Question:** Resale prices grew from $52,500 in 1990 to $630,000 in 2026 (+1,100%). How much of that was genuine purchasing power gain vs. inflation?
* **The Finding:** Over 36 years, cumulative consumer inflation was **92.5%** ($1.00 in 1990 equals $1.925 in 2026).
  - **Nominal Growth:** Grew at a **6.4% CAGR** (+1,100% headline gain).
  - **Real Purchasing Power:** Grew at a **4.4% CAGR** (+523% real gain in constant 1990 dollars).
* **Takeaway:** Public housing delivered a solid **+4.4% real annualized return above inflation**, generating **+$274,773** in genuine purchasing power per median home.

### 3. Town Capital Appreciation, Decade by Decade
* **The Question:** Are prime central towns (Queenstown, Bishan, Bukit Timah) always the best investments, or does leadership shift across market eras?
* **The Finding:** Town leadership is **cyclical across decades**, not permanent:
  - **1990s (Central Mature Surge):** City-fringe mature estates led all growth—**Bukit Timah (+338.8%)**, **Queenstown (+311.3%)**, and **Toa Payoh (+308.5%)**.
  - **2000s (New Town Expansion):** Newly built towns surged as infrastructure matured—**Sengkang jumped from #19 to #1 (+91.7%)**, while Queenstown held #2 (+86.7%).
  - **2010s (Suburban Hangover):** Massive new flat supply caused suburban towns to stagnate (**Sembawang -5.4%**, **Bukit Batok -5.3%**), while Central Area (+24.8%) grew.
  - **2020s (Suburban Revival):** Post-pandemic demand for larger, affordable spaces reversed the trend—suburban towns led appreciation: **Toa Payoh (+63.0%)**, **Sembawang (+61.5%)**, and **Bukit Batok (+54.2%)** outperformed Central Area (+21.7%).
* **Takeaway:** Today's lagging town is frequently the next decade's top performer once infrastructure and affordability rebalance.

### 4. Flat Size Shrinkage & Vertical Storey Height Premiums
* **The Question:** Are newer flats really getting smaller, and how much does floor height add to property value?
* **The Finding:** 
  - **Flats Are Shrinking:** 5-Room flats built in the 2020s are **-5.3% smaller** than in the 1990s (down from 124.2 sqm to 117.6 sqm). Normalizing to **price-per-sqm** is necessary to prevent older, larger flats from appearing artificially expensive in lump-sum comparisons.
  - **Vertical Sky Premium:** Higher floors command compounding premiums over lower levels:
    - **Storey 1–6 (Low Floor):** Baseline ($5,355/sqm, $510k median)
    - **Storey 7–12 (Mid Floor):** **+7.3% premium** ($5,747/sqm)
    - **Storey 13–20 (High Floor):** **+22.2% premium** ($6,543/sqm)
    - **Storey 21+ (Sky Tier / Pinnacle):** **+80.9% premium** ($9,688/sqm, $875k median)
* **Takeaway:** Floor height has become a primary driver of million-dollar resale transactions, with sky-tier units commanding nearly double the $/sqm of lower-floor equivalents.

### 5. Macro Policy Cooling Measures & Market Impact
* **The Question:** When the government introduces cooling measures (loan caps, stamp duties), does the resale market actually cool down?
* **The Finding:** We tracked the **12-month pre- vs. 12-month post-event** volume and pricing shifts across 5 major policy interventions:
  - **2013 TDSR (Debt Ratio Cap):** **Effective.** Resale volume plunged **-21.6%** and prices softened by **-1.5%**.
  - **2018 ABSD & LTV Tightening:** **Effective.** Transaction prices cooled by **-1.8%**.
  - **2020 COVID-19 Circuit Breaker:** **Resilient Demand.** Volumes rebounded **+7.5%** and prices rose **+7.4%** in 12 months.
  - **2021 & 2022 Cooling Packages:** **Constrained Supply.** While transaction volumes dropped (-8%), prices continued rising (**+7.4% to +9.3%**) because pandemic construction bottlenecks created severe physical supply shortages that cooling taxes could not offset.
* **Takeaway:** Cooling measures effectively rein in speculative demand during normal times, but supply deficits overpower fiscal restrictions during crisis periods.

---

## 🛠️ Data Engineering: Multi-File Schema Reconciliation

A major technical challenge of this dataset was reconciling **36 years of data across 5 separate CSV releases** into a single cohesive PostgreSQL 16 schema. Over the decades, Singapore's data format changed substantially:

| Dataset Era | Transaction Count | Key Schema Challenge & Harmonization Solution |
| :--- | :--- | :--- |
| **1990–1999** | 287,196 | No remaining lease recorded. Reconstructed mathematically from transaction date and lease commence year ($99 - [\text{trans\_year} - \text{commence}]$). |
| **2000–Feb 2012** | 369,651 | Approval-date based records with 10 standard columns. |
| **Mar 2012–Dec 2014** | 52,203 | Shifted from approval date to registration date; synchronized date format. |
| **Jan 2015–Dec 2016** | 37,153 | Added `remaining_lease` as raw integer years (e.g., `70`). Cast to decimal float. |
| **Jan 2017–Sep 2026** | 240,345 | Changed `remaining_lease` to text strings (e.g. `"61 years 04 months"`). Normalized via regex into continuous float years ($61 + 4/12 = 61.33$). |

### ETL Pipeline Highlights ([`src/load_data.py`](src/load_data.py)):
* **Storey Range Midpoints:** Converted categorical text ranges (`"07 TO 09"`, `"01 TO 03"`) to numeric midpoints (`8.0`, `2.0`) to allow mathematical floor tier analysis.
* **Unit Normalization:** Pre-computed `price_per_sqm` and `price_per_sqft` during ingestion.
* **High-Speed Streaming:** Utilized PostgreSQL's native `COPY` protocol via `psycopg`, ingesting all **986,548 rows with 4 composite B-tree indexes in ~11.4 seconds**.

---

## 💡 Practical Takeaways for Buyers & Homeowners

1. **Beware the 60-Year Boundary:** Buyers considering older flats in mature estates (e.g. Queenstown, Toa Payoh) should avoid units with 60 to 65 years remaining unless they intend to stay for life, because crossing below 60 years triggers a 20%–26% price drop due to bank loan restrictions and CPF withdrawal limits.
2. **Older Flats Offer More Space:** Families wanting maximum living space should look at 1990s 4-room and 5-room flats—which average 5% to 6% more floor area than modern flats—while avoiding top-tier high floors (21st floor and above) which command up to an 80.9% $/sqm premium over lower floors.
3. **Plan Exit Strategies Before 55 Years:** While public housing has delivered a consistent 4.4% real annual gain above inflation, capital appreciation slows and secondary-market liquidity falls sharply once remaining tenure drops below 55 years; owners should time upgrades before this phase.

---

## 📁 Repository Structure

```
ResaleFlatPrices/
├── app.py                               # Interactive Streamlit Web Dashboard (Universal Light & Dark Mode)
├── data/                                # The 5 Official Public HDB Resale CSVs (1990–2026)
│   ├── Resale Flat Prices (Based on Approval Date), 1990 - 1999.csv
│   ├── Resale Flat Prices (Based on Approval Date), 2000 - Feb 2012.csv
│   ├── Resale Flat Prices (Based on Registration Date), From Mar 2012 to Dec 2014.csv
│   ├── Resale Flat Prices (Based on Registration Date), From Jan 2015 to Dec 2016.csv
│   └── Resale flat prices based on registration date from Jan-2017 onwards.csv
├── sql/
│   ├── 00_schema_and_load.sql           # PostgreSQL table schema & composite index definitions
│   ├── 01_lease_decay_cliff.sql         # 1. Lease decay cliff & 60-year financing threshold
│   ├── 02_real_vs_nominal_growth.sql    # 2. Real CPI-adjusted vs. nominal growth (1990-2026)
│   ├── 03_town_ranking_by_decade.sql    # 3. Decade town ranking rotations (RANK, LAG)
│   ├── 04_price_per_sqm_storeys.sql     # 4. Size shrinkage & vertical storey height premiums
│   ├── 05_policy_event_impact.sql       # 5. Macro cooling measures 12M pre/post event impact
│   └── run_all_analyses.sql             # Master SQL runner script (runnable via psql)
├── src/
│   ├── __init__.py
│   └── load_data.py                     # Schema reconciliation ETL: streams CSVs into PostgreSQL
├── docs/
│   ├── data_dictionary.md               # PostgreSQL schema documentation & column definitions
│   └── executive_summary.md             # In-depth executive memo of analytical findings
├── tests/
│   ├── __init__.py
│   └── test_sql_analyses.py             # Pytest suite validating data integrity & SQL queries (8/8 passing)
├── requirements.txt                     # Dependencies (pandas, psycopg, streamlit, plotly, pytest)
├── project_plan.md                      # Original project plan & analytical scope
└── README.md                            # Comprehensive project overview
```

---

## 🚀 Quick-Start Guide

### 1. Prerequisites
Ensure PostgreSQL is running locally on port 5433:
```bash
brew services start postgresql@16
```

### 2. Environment Setup
```bash
source .venv/bin/activate
# Or install dependencies afresh:
# pip install -r requirements.txt
```

### 3. Load Data into PostgreSQL
Reconciles the 5 CSVs and streams all 986,548 transactions into PostgreSQL table `resale_prices` in ~12 seconds:
```bash
python -m src.load_data
```

### 4. Launch Interactive Web Dashboard
```bash
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser. Seamlessly supports both **Light and Dark mode** via Streamlit's upper-right three-dot menu.

### 5. Run Pure SQL Scripts via Terminal
```bash
psql -p 5433 -d hdb_resale -f sql/run_all_analyses.sql
```

### 6. Run Automated Tests
```bash
pytest tests/
```

---

## 📜 Data Lineage & Attribution
All data originates exclusively from official public HDB resale transaction records on [Data.gov.sg](https://data.gov.sg/) provided under the Singapore Open Data Licence.
