-- Master Runner for all 5 Core Analytical Inquiries
\pset pager off

\echo '------------------------------------------------------------------------'
\echo 'ANALYSIS 1: THE LEASE DECAY CLIFF (60-YEAR FINANCING BOUNDARY)'
\echo '------------------------------------------------------------------------'
\i sql/01_lease_decay_cliff.sql

\echo '------------------------------------------------------------------------'
\echo 'ANALYSIS 2: REAL (CPI-ADJUSTED) VS NOMINAL CAPITAL GROWTH (1990-2026)'
\echo '------------------------------------------------------------------------'
\i sql/02_real_vs_nominal_growth.sql

\echo '------------------------------------------------------------------------'
\echo 'ANALYSIS 3: TOWN APPRECIATION RANKING, DECADE BY DECADE'
\echo '------------------------------------------------------------------------'
\i sql/03_town_ranking_by_decade.sql

\echo '------------------------------------------------------------------------'
\echo 'ANALYSIS 4: PRICE-PER-SQM NORMALIZATION & VERTICAL STOREY PREMIUM'
\echo '------------------------------------------------------------------------'
\i sql/04_price_per_sqm_storeys.sql

\echo '------------------------------------------------------------------------'
\echo 'ANALYSIS 5: POLICY COOLING MEASURES & MACRO EVENT IMPACT'
\echo '------------------------------------------------------------------------'
\i sql/05_policy_event_impact.sql
