"""
Automated Validation Suite for PostgreSQL HDB Resale Data Warehouse.
"""

import os
import pytest
import psycopg

CONN_STR = "dbname=hdb_resale port=5433"


@pytest.fixture(scope="module")
def pg_conn():
    try:
        conn = psycopg.connect(CONN_STR)
        yield conn
        conn.close()
    except Exception as e:
        pytest.fail(f"Could not connect to PostgreSQL on port 5433: {e}")


def test_table_row_count(pg_conn):
    with pg_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM resale_prices;")
        count = cur.fetchone()[0]
        assert count == 986548, f"Expected 986,548 rows, got {count}"


def test_data_quality_no_nulls(pg_conn):
    with pg_conn.cursor() as cur:
        cur.execute("""
            SELECT
                COUNT(*) FILTER (WHERE remaining_lease_years IS NULL),
                COUNT(*) FILTER (WHERE price_per_sqm IS NULL),
                COUNT(*) FILTER (WHERE floor_area_sqm <= 0),
                COUNT(*) FILTER (WHERE resale_price <= 0)
            FROM resale_prices;
        """)
        null_leases, null_psm, zero_area, zero_price = cur.fetchone()
        assert null_leases == 0, f"Found {null_leases} null leases"
        assert null_psm == 0, f"Found {null_psm} null psm"
        assert zero_area == 0, f"Found {zero_area} non-positive floor areas"
        assert zero_price == 0, f"Found {zero_price} non-positive prices"


def test_decade_distribution(pg_conn):
    with pg_conn.cursor() as cur:
        cur.execute("SELECT decade, COUNT(*) FROM resale_prices GROUP BY decade ORDER BY decade;")
        rows = dict(cur.fetchall())
        assert "1990s" in rows and rows["1990s"] > 200000
        assert "2000s" in rows and rows["2000s"] > 300000
        assert "2010s" in rows and rows["2010s"] > 200000
        assert "2020s" in rows and rows["2020s"] > 100000


@pytest.mark.parametrize(
    "sql_file",
    [
        "sql/01_lease_decay_cliff.sql",
        "sql/02_real_vs_nominal_growth.sql",
        "sql/03_town_ranking_by_decade.sql",
        "sql/04_price_per_sqm_storeys.sql",
        "sql/05_policy_event_impact.sql",
    ],
)
def test_sql_analyses_execute(pg_conn, sql_file):
    assert os.path.exists(sql_file), f"File {sql_file} does not exist"
    with open(sql_file, "r") as f:
        content = f.read()

    statements = [s.strip() for s in content.split(";") if s.strip()]
    with pg_conn.cursor() as cur:
        for stmt in statements:
            cur.execute(stmt)
            if cur.description:
                rows = cur.fetchall()
                assert len(rows) > 0, f"Query in {sql_file} returned 0 rows"
