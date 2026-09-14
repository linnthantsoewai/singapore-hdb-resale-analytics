-- 01_lease_decay_cliff.sql: The "Lease Decay Cliff" Analysis

-- In Singapore, banks restrict mortgage tenure and CPF housing usage once
-- remaining lease tenure drops below 60 years.
-- This query tests whether resale prices exhibit a measurable structural cliff / 
-- drop-off near that 60-year boundary, controlling for Town and Flat Size.

WITH lease_tranches AS (
    SELECT
        town,
        flat_type,
        CASE
            WHEN remaining_lease_years >= 80 THEN '1. 80+ Years (Post-MOP/Prime)'
            WHEN remaining_lease_years >= 70 THEN '2. 70-79 Years (Pre-Decay Stage)'
            WHEN remaining_lease_years >= 65 THEN '3. 65-69 Years (Approaching Boundary)'
            WHEN remaining_lease_years >= 60 THEN '4. 60-64 Years (Pre-Cliff Edge)'
            WHEN remaining_lease_years >= 55 THEN '5. 55-59 Years (Post-60 Cliff)'
            WHEN remaining_lease_years >= 50 THEN '6. 50-54 Years (Deep Decay)'
            ELSE '7. < 50 Years (Terminal Phase)'
        END AS lease_bracket,
        CASE
            WHEN remaining_lease_years >= 80 THEN 1
            WHEN remaining_lease_years >= 70 THEN 2
            WHEN remaining_lease_years >= 65 THEN 3
            WHEN remaining_lease_years >= 60 THEN 4
            WHEN remaining_lease_years >= 55 THEN 5
            WHEN remaining_lease_years >= 50 THEN 6
            ELSE 7
        END AS bracket_order,
        price_per_sqm,
        resale_price,
        floor_area_sqm
    FROM resale_prices
    WHERE flat_type IN ('3 ROOM', '4 ROOM')
      AND transaction_year >= 2018 -- Focus on modern era under active CPF age-95 rules
),
town_aggregates AS (
    SELECT
        town,
        flat_type,
        lease_bracket,
        bracket_order,
        COUNT(*) AS sales_count,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_per_sqm)::numeric, 2) AS median_psm,
        ROUND(AVG(price_per_sqm)::numeric, 2) AS avg_psm,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY resale_price)::numeric, 0) AS median_price
    FROM lease_tranches
    GROUP BY town, flat_type, lease_bracket, bracket_order
    HAVING COUNT(*) >= 15 -- Filter for statistical significance / liquidity
),
decay_steps AS (
    SELECT
        town,
        flat_type,
        lease_bracket,
        bracket_order,
        sales_count,
        median_psm,
        median_price,
        LAG(median_psm) OVER (
            PARTITION BY town, flat_type
            ORDER BY bracket_order
        ) AS previous_bracket_psm
    FROM town_aggregates
)
SELECT
    town,
    flat_type,
    lease_bracket,
    sales_count,
    median_psm,
    median_price,
    previous_bracket_psm,
    ROUND(median_psm - previous_bracket_psm, 2) AS absolute_psm_drop,
    ROUND(
        ((median_psm - previous_bracket_psm) / previous_bracket_psm) * 100.0, 2
    ) AS step_change_pct,
    -- Flag whether the drop at the 60-year boundary is an accelerated cliff (> 10% step drop)
    CASE
        WHEN bracket_order = 5 AND ((median_psm - previous_bracket_psm) / previous_bracket_psm) <= -0.10
        THEN 'CONFIRMED CLIFF'
        WHEN bracket_order = 5
        THEN 'MODERATE IMPACT'
        ELSE 'BASELINE'
    END AS cliff_indicator
FROM decay_steps
ORDER BY town, flat_type, bracket_order;
