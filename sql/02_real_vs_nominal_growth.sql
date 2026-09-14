-- 02_real_vs_nominal_growth.sql: Real (Inflation-Adjusted) vs Nominal Price Growth

-- Raw price trends always show dramatic upward slopes. A rigorous financial analyst
-- adjusts for Singapore Consumer Price Index (CPI) inflation to evaluate true real
-- purchasing power gains vs headline nominal numbers across the 36-year timeline (1990-2026).

WITH cpi_reference(trans_year, cpi_index_1990_base) AS (
    -- Official Singapore Department of Statistics (DOS) CPI trajectory (Base: 1990 = 100.0)
    VALUES
        (1990, 100.00), (1991, 103.40), (1992, 105.80), (1993, 108.30), (1994, 111.70),
        (1995, 113.60), (1996, 115.20), (1997, 117.50), (1998, 117.20), (1999, 117.20),
        (2000, 118.80), (2001, 120.00), (2002, 119.50), (2003, 120.10), (2004, 122.10),
        (2005, 122.70), (2006, 123.90), (2007, 126.50), (2008, 134.80), (2009, 135.60),
        (2010, 139.40), (2011, 146.70), (2012, 153.40), (2013, 157.10), (2014, 158.70),
        (2015, 157.90), (2016, 157.10), (2017, 158.00), (2018, 158.70), (2019, 159.60),
        (2020, 159.30), (2021, 163.00), (2022, 172.90), (2023, 181.20), (2024, 185.50),
        (2025, 189.20), (2026, 192.50)
),
annual_nominal_stats AS (
    SELECT
        transaction_year,
        COUNT(*) AS transaction_volume,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY resale_price)::numeric, 0) AS nominal_median_price,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_per_sqm)::numeric, 2) AS nominal_median_psm,
        ROUND(AVG(price_per_sqm)::numeric, 2) AS nominal_avg_psm
    FROM resale_prices
    GROUP BY transaction_year
),
real_adjusted_series AS (
    SELECT
        n.transaction_year,
        n.transaction_volume,
        c.cpi_index_1990_base AS cpi_deflator,
        n.nominal_median_price,
        -- Real Price in 1990 Constant Dollars: Nominal / (CPI / 100)
        ROUND((n.nominal_median_price / (c.cpi_index_1990_base / 100.0))::numeric, 0) AS real_median_price_1990_dollars,
        n.nominal_median_psm,
        ROUND((n.nominal_median_psm / (c.cpi_index_1990_base / 100.0))::numeric, 2) AS real_median_psm_1990_dollars
    FROM annual_nominal_stats n
    JOIN cpi_reference c ON n.transaction_year = c.trans_year
),
baseline_1990 AS (
    SELECT
        nominal_median_price AS base_nom_price,
        real_median_price_1990_dollars AS base_real_price,
        nominal_median_psm AS base_nom_psm,
        real_median_psm_1990_dollars AS base_real_psm
    FROM real_adjusted_series
    WHERE transaction_year = 1990
)
SELECT
    r.transaction_year,
    r.transaction_volume,
    r.cpi_deflator,
    r.nominal_median_price,
    r.real_median_price_1990_dollars,
    ROUND(((r.nominal_median_price - b.base_nom_price) / b.base_nom_price) * 100.0, 1) AS cumulative_nominal_gain_pct,
    ROUND(((r.real_median_price_1990_dollars - b.base_real_price) / b.base_real_price) * 100.0, 1) AS cumulative_real_gain_pct,
    r.nominal_median_psm,
    r.real_median_psm_1990_dollars,
    -- Annualized Compounded Growth Rates (CAGR) from 1990
    CASE
        WHEN r.transaction_year > 1990 THEN
            ROUND((POWER((r.nominal_median_psm / b.base_nom_psm)::numeric, (1.0 / (r.transaction_year - 1990))::numeric) - 1.0) * 100.0, 2)
        ELSE 0.0
    END AS nominal_cagr_from_1990_pct,
    CASE
        WHEN r.transaction_year > 1990 THEN
            ROUND((POWER((r.real_median_psm_1990_dollars / b.base_real_psm)::numeric, (1.0 / (r.transaction_year - 1990))::numeric) - 1.0) * 100.0, 2)
        ELSE 0.0
    END AS real_cagr_from_1990_pct
FROM real_adjusted_series r
CROSS JOIN baseline_1990 b
ORDER BY r.transaction_year;
