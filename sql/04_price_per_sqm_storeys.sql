-- 04_price_per_sqm_storeys.sql: Price-per-sqm Normalization & Vertical Storey Premium

-- Raw lump-sum resale price is misleading across eras because flat floor areas
-- have shrunk over time (e.g., 1990s 4-room ~105 sqm vs 2020s 4-room ~92 sqm).
-- Normalizing to Price-per-sqm reveals the true market valuation and allows
-- quantifying the exact vertical price premium across building storey heights.

-- PART 1: The Raw Price vs Size Shrinkage Paradox (Eras Comparison)
WITH era_flat_size_comparison AS (
    SELECT
        decade,
        flat_type,
        COUNT(*) AS transaction_volume,
        ROUND(AVG(floor_area_sqm)::numeric, 1) AS avg_floor_area_sqm,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY resale_price)::numeric, 0) AS median_raw_price,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_per_sqm)::numeric, 2) AS median_price_per_sqm
    FROM resale_prices
    WHERE flat_type IN ('3 ROOM', '4 ROOM', '5 ROOM')
    GROUP BY decade, flat_type
)
SELECT
    decade,
    flat_type,
    transaction_volume,
    avg_floor_area_sqm,
    median_raw_price,
    median_price_per_sqm,
    -- Calculate % change in unit size relative to the 1990s
    ROUND(
        ((avg_floor_area_sqm - FIRST_VALUE(avg_floor_area_sqm) OVER (PARTITION BY flat_type ORDER BY decade))
        / FIRST_VALUE(avg_floor_area_sqm) OVER (PARTITION BY flat_type ORDER BY decade)) * 100.0, 1
    ) AS size_change_vs_1990s_pct
FROM era_flat_size_comparison
ORDER BY flat_type, decade;


-- PART 2: Vertical Storey Height Premium Analysis (Controlling for Flat Type)
WITH storey_categorization AS (
    SELECT
        flat_type,
        CASE
            WHEN storey_midpoint <= 6 THEN '1. Low Floor (Storey 1-6)'
            WHEN storey_midpoint <= 12 THEN '2. Mid Floor (Storey 7-12)'
            WHEN storey_midpoint <= 20 THEN '3. High Floor (Storey 13-20)'
            ELSE '4. Sky Tier (Storey 21+)'
        END AS floor_tier,
        resale_price,
        floor_area_sqm,
        price_per_sqm
    FROM resale_prices
    WHERE transaction_year >= 2020 -- Focus on current market pricing dynamics
      AND flat_type IN ('3 ROOM', '4 ROOM', '5 ROOM')
      AND storey_midpoint IS NOT NULL
),
tier_stats AS (
    SELECT
        flat_type,
        floor_tier,
        COUNT(*) AS transaction_count,
        ROUND(AVG(floor_area_sqm)::numeric, 1) AS avg_sqm,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY resale_price)::numeric, 0) AS median_raw_price,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_per_sqm)::numeric, 2) AS median_psm
    FROM storey_categorization
    GROUP BY flat_type, floor_tier
)
SELECT
    flat_type,
    floor_tier,
    transaction_count,
    avg_sqm,
    median_raw_price,
    median_psm,
    -- Compare every floor tier against the Low Floor base
    ROUND(
        ((median_psm - FIRST_VALUE(median_psm) OVER (PARTITION BY flat_type ORDER BY floor_tier))
        / FIRST_VALUE(median_psm) OVER (PARTITION BY flat_type ORDER BY floor_tier)) * 100.0, 2
    ) AS storey_premium_vs_low_floor_pct,
    -- Step-by-step marginal gain from previous tier
    ROUND(
        median_psm - LAG(median_psm) OVER (PARTITION BY flat_type ORDER BY floor_tier), 2
    ) AS marginal_step_psm_gain
FROM tier_stats
ORDER BY flat_type, floor_tier;
