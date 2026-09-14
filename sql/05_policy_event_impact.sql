-- 05_policy_event_impact.sql: Macro Policy & Cooling Measure Impact Analysis

-- Tie price movement to real-world regulatory causality reasoning.
-- Marks known Singapore policy cooling measures and macro shocks:
--   1. Jun 2013: Total Debt Servicing Ratio (TDSR) & Mortgage Servicing Ratio (MSR)
--   2. Jul 2018: ABSD Rate Hikes & LTV Cap Tightening
--   3. Apr 2020: COVID-19 Circuit Breaker & Remote Work Demand Shock
--   4. Dec 2021: ABSD Increases & TDSR Ceiling Tightening
--   5. Sep 2022: 15-Month Wait-Out Period for Private Property Downgraders
-- Quantifies 12-month pre-event vs 12-month post-event price and volume shifts.

WITH policy_events(event_id, event_name, event_month, pre_window_start, pre_window_end, post_window_start, post_window_end) AS (
    VALUES
        (1, '2013 TDSR / MSR Mortgage Cap',       '2013-06', '2012-07', '2013-06', '2013-07', '2014-06'),
        (2, '2018 ABSD Hike & LTV Tightening',     '2018-07', '2017-07', '2018-06', '2018-07', '2019-06'),
        (3, '2020 COVID-19 Circuit Breaker',      '2020-04', '2019-04', '2020-03', '2020-04', '2021-03'),
        (4, '2021 Cooling Measures Package',      '2021-12', '2021-01', '2021-12', '2022-01', '2022-12'),
        (5, '2022 15-Month Wait-Out Period Rule', '2022-09', '2021-10', '2022-09', '2022-10', '2023-09')
),
event_window_transactions AS (
    SELECT
        e.event_id,
        e.event_name,
        e.event_month,
        CASE
            WHEN r.month BETWEEN e.pre_window_start AND e.pre_window_end THEN 'PRE-EVENT (12M)'
            WHEN r.month BETWEEN e.post_window_start AND e.post_window_end THEN 'POST-EVENT (12M)'
            ELSE NULL
        END AS period_tag,
        r.resale_price,
        r.price_per_sqm
    FROM resale_prices r
    CROSS JOIN policy_events e
    WHERE (r.month BETWEEN e.pre_window_start AND e.pre_window_end)
       OR (r.month BETWEEN e.post_window_start AND e.post_window_end)
),
aggregated_impact AS (
    SELECT
        event_id,
        event_name,
        event_month,
        period_tag,
        COUNT(*) AS transaction_volume,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY resale_price)::numeric, 0) AS median_price,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_per_sqm)::numeric, 2) AS median_psm,
        ROUND(AVG(price_per_sqm)::numeric, 2) AS avg_psm
    FROM event_window_transactions
    WHERE period_tag IS NOT NULL
    GROUP BY event_id, event_name, event_month, period_tag
),
pivoted AS (
    SELECT
        event_id,
        event_name,
        event_month,
        MAX(CASE WHEN period_tag = 'PRE-EVENT (12M)' THEN transaction_volume END) AS pre_volume_12m,
        MAX(CASE WHEN period_tag = 'POST-EVENT (12M)' THEN transaction_volume END) AS post_volume_12m,
        MAX(CASE WHEN period_tag = 'PRE-EVENT (12M)' THEN median_psm END) AS pre_median_psm,
        MAX(CASE WHEN period_tag = 'POST-EVENT (12M)' THEN median_psm END) AS post_median_psm,
        MAX(CASE WHEN period_tag = 'PRE-EVENT (12M)' THEN median_price END) AS pre_median_price,
        MAX(CASE WHEN period_tag = 'POST-EVENT (12M)' THEN median_price END) AS post_median_price
    FROM aggregated_impact
    GROUP BY event_id, event_name, event_month
)
SELECT
    event_id,
    event_name,
    event_month,
    pre_volume_12m,
    post_volume_12m,
    -- Volume elasticity (% change in transaction liquidity)
    ROUND(((post_volume_12m - pre_volume_12m)::numeric / pre_volume_12m) * 100.0, 1) AS volume_change_pct,
    pre_median_psm,
    post_median_psm,
    -- Price per sqm percentage movement
    ROUND(((post_median_psm - pre_median_psm) / pre_median_psm) * 100.0, 2) AS psm_change_pct,
    -- Core causal conclusion
    CASE
        WHEN ((post_median_psm - pre_median_psm) / pre_median_psm) < 0 THEN 'COOLING EFFECTIVE (Prices Softened)'
        WHEN ((post_volume_12m - pre_volume_12m)::numeric / pre_volume_12m) < -15 THEN 'VOLUME CHILLED (Transactions Froze)'
        ELSE 'RESILIENT DEMAND (Growth Continued)'
    END AS market_response
FROM pivoted
ORDER BY event_id;
