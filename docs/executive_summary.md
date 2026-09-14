# Executive Summary: 36-Year HDB Resale Analysis (1990–2026)

**Dataset Coverage:** 986,548 Resale Transactions (Jan 1990 – Sep 2026)  
**Database Engine:** PostgreSQL 16  
**Source Data:** 5 Official HDB Public Datasets (Data.gov.sg)  

---

## 1. The "Lease Decay Cliff" Analysis (60-Year Boundary)
* **Hypothesis:** Does resale price exhibit a structural cliff when remaining lease tenure drops below 60 years, where commercial banks restrict mortgage tenures and CPF usage limits tighten?
* **SQL Findings:**
  - **Location Controls Matter:** When analyzing national averages, flats with 50–59 years lease appear to trade higher than 65–69 year flats. This is a classic Simpson's paradox: the oldest flats are situated in prime central heritage estates (Queenstown, Bukit Merah, Toa Payoh), while 65-year flats are located in outer non-mature suburbs.
  - **Within-Town Cliffs:** Controlling for town and flat size, we observe pronounced discontinuities:
    - **Queenstown 4-Room:** Drops from **$8,147/sqm** (60–64 yrs) down to **$5,994/sqm** (55–59 yrs), representing an immediate **-26.4% cliff drop** across the 60-year boundary.
    - **Ang Mo Kio 4-Room:** Drops by **-28.5%** between 65–69 and 60–64 years ($6,029 $\rightarrow$ $4,312/sqm).
    - **Bedok 4-Room:** Drops by **-26.6%** ($6,000 $\rightarrow$ $4,405/sqm).
  - **Interview Takeaway:** Lease decay is non-linear and governed by regulatory financing thresholds rather than smooth mechanical depreciation.

---

## 2. Real vs. Nominal Price Growth (1990–2026)
* **Headline Numbers vs. Real Purchasing Power:**
  - **Nominal Resale Price:** Grew from **$52,500** in 1990 to **$630,000** in 2026 — an **11.0x increase (+1,100% nominal gain)**, translating to a **6.4% nominal CAGR**.
  - **CPI Inflation Adjustment:** Factoring in Singapore's Department of Statistics historical CPI (compounding by 92.5% from 1990 to 2026), the real median price in constant 1990 dollars rose from **$52,500** to **$327,273** — a **5.2x increase (+523% real gain)**.
  - **Real Annualized Return:** Compounded at **4.38% real CAGR**.
  - **Interview Takeaway:** While headline media reports tout 10x gains, inflation accounts for nearly half of total nominal appreciation; public housing provided a reliable inflation hedge plus ~4.4% real annual growth.

---

## 3. Town Appreciation Ranking, Decade by Decade
* **Is Town Performance Consistent or Cyclical?**
  Using SQL window functions (`DENSE_RANK()`, `LAG()`) across decade boundaries:
  - **1990s Bull Run:** Driven by city-fringe mature estates: **Bukit Timah (+338.8%)**, **Queenstown (+311.3%)**, **Toa Payoh (+308.5%)**.
  - **2000s New Town Emergence:** Newly completed towns took the lead: **Sengkang jumped from Rank 19 to Rank 1 (+91.7%)**, while Queenstown remained stable at Rank 2 (+86.7%).
  - **2010s Mature Divergence vs Suburban Stagnation:** Central Area (+24.8%) and Queenstown (+22.7%) posted moderate gains, but suburban non-mature towns experienced negative growth (**Sembawang -5.4%**, **Bukit Batok -5.3%**, **Choa Chu Kang -4.3%**) due to aggressive BTO supply ramp-ups.
  - **2020s Suburban Renaissance:** Complete cyclical reversal post-COVID! **Toa Payoh (+63.0%)**, **Sembawang (+61.5%)**, and **Bukit Batok (+54.2%)** outperformed Central Area (+21.7%) and Marine Parade (+26.3%) as remote work favored larger, suburban units.
  - **Interview Takeaway:** Real estate leadership is inherently cyclical; suburban towns underperform during supply surges but offer the strongest upside during post-crisis catch-up cycles.

---

## 4. Price-per-sqm Normalization & Vertical Storey Height Premium
* **The Shrinking Unit Phenomenon:**
  - Between 1990 and 2026, 5-Room flats shrank from an average of **124.2 sqm down to 117.6 sqm (-5.3%)**, and 4-Room flats shrank from **96.6 sqm to 94.8 sqm (-1.9%)**. Looking solely at raw lump-sum prices understates how expensive modern flats have become per unit of living area.
* **Vertical Storey Height Premium (2020–2026):**
  - **Storey 1–6 (Low Floor Baseline):** Median $5,355/sqm (4-Room).
  - **Storey 7–12 (Mid Floor):** **+7.3% premium** ($5,747/sqm).
  - **Storey 13–20 (High Floor):** **+22.2% premium** ($6,543/sqm).
  - **Storey 21+ (Sky Tier / Pinnacle):** **+80.9% premium** ($9,688/sqm).
  - **Interview Takeaway:** Height is heavily monetized in Singapore public housing; living on a 21st+ floor commands an 80%+ premium over low-floor equivalents.

---

## 5. Policy Cooling Measures & Macro Event Causality
* **Quantifying 12-Month Pre vs Post Impact:**
  1. **2013 TDSR / MSR Mortgage Cap:** Transactions plummeted by **-21.6%**, and median price/sqm fell by **-1.47%** (`COOLING EFFECTIVE`).
  2. **2018 ABSD Hike & LTV Tightening:** Price/sqm softened by **-1.79%** over the subsequent 12 months (`COOLING EFFECTIVE`).
  3. **2020 COVID-19 Circuit Breaker:** Despite initial lockdowns, transaction volume rose **+7.5%**, and price/sqm surged **+7.38%** over the next 12 months, initiating the pandemic housing boom (`RESILIENT DEMAND`).
  4. **2021 Cooling Measures Package:** Transactions fell by **-8.1%**, but prices rose **+9.3%** due to severe supply chain construction delays (`RESILIENT DEMAND`).
  5. **2022 15-Month Wait-Out Rule:** Volume contracted by **-7.6%**, yet price/sqm rose **+7.36%** (`RESILIENT DEMAND`).
  - **Interview Takeaway:** Financing restrictions (TDSR) immediately chilled transaction velocity, whereas macro supply constraints and pandemic space demand overpowered subsequent stamp-duty interventions.
