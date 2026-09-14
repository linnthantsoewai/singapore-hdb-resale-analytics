# PostgreSQL Data Warehouse: HDB Resale Data Dictionary

## Table: `resale_prices`
- **Database Engine:** PostgreSQL 16
- **Grain:** One record per individual completed resale transaction
- **Total Records:** 986,548 rows (Covering Jan 1990 to Sep 2026)
- **Source:** Combined 5 official HDB transaction CSV releases (Data.gov.sg)

| Column Name | Data Type | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `SERIAL PRIMARY KEY` | NO | Auto-incrementing unique identifier | `1` |
| `month` | `VARCHAR(7)` | NO | Registration/Approval period (`YYYY-MM`) | `1990-01` |
| `transaction_year` | `INTEGER` | NO | 4-digit calendar transaction year | `1990` |
| `transaction_month`| `INTEGER` | NO | 1- or 2-digit transaction month (1 to 12) | `1` |
| `decade` | `VARCHAR(10)` | NO | Market regime decade (`1990s`, `2000s`, `2010s`, `2020s`) | `1990s` |
| `town` | `VARCHAR(50)` | NO | Standardized HDB Town / Planning Area | `ANG MO KIO` |
| `flat_type` | `VARCHAR(50)` | NO | Room configuration (`1 ROOM` to `MULTI-GENERATION`) | `3 ROOM` |
| `flat_model` | `VARCHAR(50)` | NO | Architectural flat model design | `Improved` |
| `block` | `VARCHAR(10)` | NO | HDB residential block number | `309` |
| `street_name` | `VARCHAR(100)`| NO | Standardized Singapore street name | `ANG MO KIO AVE 1` |
| `storey_range` | `VARCHAR(20)` | NO | Original storey height bracket | `10 TO 12` |
| `storey_midpoint` | `NUMERIC(4, 1)`| YES | Continuous numerical midpoint of storey bracket | `11.0` |
| `floor_area_sqm` | `NUMERIC(6, 2)`| NO | Interior floor area in square metres | `31.00` |
| `lease_commence_date`| `INTEGER` | NO | Year the 99-year state lease commenced | `1977` |
| `remaining_lease_years`| `NUMERIC(5, 2)`| NO | Continuous remaining lease tenure in years | `86.00` |
| `resale_price` | `NUMERIC(12, 2)`| NO | Agreed transaction price (SGD) | `9000.00` |
| `price_per_sqm` | `NUMERIC(10, 2)`| NO | `resale_price / floor_area_sqm` ($/sqm) | `290.32` |
| `price_per_sqft` | `NUMERIC(10, 2)`| NO | `resale_price / (floor_area_sqm * 10.7639)` ($ PSF) | `26.97` |

---

## Derived Field Formulas & Logic

1. **`remaining_lease_years` Standardization:**
   - For post-2017 text strings (e.g. `"61 years 04 months"`):
     $$\text{years} + \frac{\text{months}}{12.0}$$
   - For 2015–2016 integers (e.g. `70`):
     $$\text{float}(70.0)$$
   - For pre-2015 legacy records:
     $$99.0 - (\text{transaction\_year} - \text{lease\_commence\_date})$$

2. **`price_per_sqm` (PSM) & `price_per_sqft` (PSF):**
   $$\text{PSM} = \frac{\text{resale\_price}}{\text{floor\_area\_sqm}}$$
   $$\text{PSF} = \frac{\text{resale\_price}}{\text{floor\_area\_sqm} \times 10.7639}$$

3. **`decade` Segmentation:**
   $$\text{decade} = \begin{cases} 
   \text{'1990s'} & 1990 \le \text{year} < 2000 \\
   \text{'2000s'} & 2000 \le \text{year} < 2010 \\
   \text{'2010s'} & 2010 \le \text{year} < 2020 \\
   \text{'2020s'} & \text{year} \ge 2020 
   \end{cases}$$
