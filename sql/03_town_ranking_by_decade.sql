-- 03_town_ranking_by_decade.sql: Decade-by-Decade Town Appreciation Ranking

-- Are today's "hot" towns (Queenstown, Bishan, Bukit Merah) consistent winners,
-- or is estate capital growth cyclical across market regimes?
-- Uses RANK() and LAG() over decade partitions (1990s, 2000s, 2010s, 2020s).

WITH decade_endpoints AS (
    SELECT
        decade,
        town,
        -- Start of decade median PSM (e.g. 1990-1991, 2000-2001, 2010-2011, 2020-2021)
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (
            ORDER BY CASE WHEN transaction_year IN (1990, 1991, 2000, 2001, 2010, 2011, 2020, 2021) THEN price_per_sqm END
        )::numeric, 2) AS decade_start_psm,
        -- End of decade median PSM (e.g. 1998-1999, 2008-2009, 2018-2019, 2025-2026)
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (
            ORDER BY CASE WHEN transaction_year IN (1998, 1999, 2008, 2009, 2018, 2019, 2025, 2026) THEN price_per_sqm END
        )::numeric, 2) AS decade_end_psm,
        COUNT(*) AS total_decade_transactions
    FROM resale_prices
    GROUP BY decade, town
),
decade_growth AS (
    SELECT
        decade,
        town,
        decade_start_psm,
        decade_end_psm,
        total_decade_transactions,
        ROUND(((decade_end_psm - decade_start_psm) / decade_start_psm) * 100.0, 2) AS decade_growth_pct
    FROM decade_endpoints
    WHERE decade_start_psm IS NOT NULL
      AND decade_end_psm IS NOT NULL
      AND total_decade_transactions >= 50
),
ranked_decades AS (
    SELECT
        decade,
        town,
        decade_start_psm,
        decade_end_psm,
        decade_growth_pct,
        total_decade_transactions,
        DENSE_RANK() OVER (
            PARTITION BY decade
            ORDER BY decade_growth_pct DESC
        ) AS rank_in_decade
    FROM decade_growth
)
SELECT
    decade,
    rank_in_decade,
    town,
    decade_start_psm,
    decade_end_psm,
    decade_growth_pct,
    total_decade_transactions,
    -- Check previous decade rank to demonstrate cyclical rotation
    LAG(rank_in_decade) OVER (
        PARTITION BY town
        ORDER BY decade
    ) AS prev_decade_rank,
    CASE
        WHEN LAG(rank_in_decade) OVER (PARTITION BY town ORDER BY decade) IS NULL THEN 'NEW/BASELINE'
        WHEN rank_in_decade < LAG(rank_in_decade) OVER (PARTITION BY town ORDER BY decade) THEN 'RISING LEADER'
        WHEN rank_in_decade > LAG(rank_in_decade) OVER (PARTITION BY town ORDER BY decade) THEN 'FALLING BEHIND'
        ELSE 'STABLE'
    END AS trajectory
FROM ranked_decades
ORDER BY decade, rank_in_decade;
