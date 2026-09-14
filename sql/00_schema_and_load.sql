-- PostgreSQL Schema Definition for 1990-2026 HDB Resale

DROP TABLE IF EXISTS resale_prices;

CREATE TABLE resale_prices (
    id                      SERIAL PRIMARY KEY,
    month                   VARCHAR(7) NOT NULL,
    transaction_year        INTEGER NOT NULL,
    transaction_month       INTEGER NOT NULL,
    decade                  VARCHAR(10) NOT NULL,
    town                    VARCHAR(50) NOT NULL,
    flat_type               VARCHAR(50) NOT NULL,
    flat_model              VARCHAR(50) NOT NULL,
    block                   VARCHAR(10) NOT NULL,
    street_name             VARCHAR(100) NOT NULL,
    storey_range            VARCHAR(20) NOT NULL,
    storey_midpoint         NUMERIC(4, 1),
    floor_area_sqm          NUMERIC(6, 2) NOT NULL,
    lease_commence_date     INTEGER NOT NULL,
    remaining_lease_years   NUMERIC(5, 2) NOT NULL,
    resale_price            NUMERIC(12, 2) NOT NULL,
    price_per_sqm           NUMERIC(10, 2) NOT NULL,
    price_per_sqft          NUMERIC(10, 2) NOT NULL
);

-- Production Indexes for High-Speed Analytical Window Queries
CREATE INDEX idx_resale_town_type ON resale_prices(town, flat_type);
CREATE INDEX idx_resale_year_decade ON resale_prices(transaction_year, decade);
CREATE INDEX idx_resale_lease ON resale_prices(remaining_lease_years);
CREATE INDEX idx_resale_psm ON resale_prices(price_per_sqm);
