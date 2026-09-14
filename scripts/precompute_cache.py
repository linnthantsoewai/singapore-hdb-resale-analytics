"""
precompute_cache.py
Run this script ONCE locally before deploying to Streamlit Community Cloud.
It queries PostgreSQL and saves all analysis results as Parquet/JSON files so
the cloud-hosted app can function without a live database connection.

Usage:
    python scripts/precompute_cache.py
"""

import json
import os
import pandas as pd
import psycopg

CONN_STR = "dbname=hdb_resale port=5433"
CACHE_DIR = "data/cached"
SQL_DIR = "sql"


def _df_from_cursor(cur) -> pd.DataFrame:
    cols = [d[0] for d in cur.description]
    df = pd.DataFrame(cur.fetchall(), columns=cols)
    for col in df.columns:
        if df[col].dtype == object:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass
    return df


def _run_sql_file(cur, path: str) -> pd.DataFrame:
    with open(path, "r") as f:
        cur.execute(f.read())
    return _df_from_cursor(cur)


def main():
    os.makedirs(CACHE_DIR, exist_ok=True)
    print(f"Connecting to PostgreSQL ({CONN_STR})...")

    with psycopg.connect(CONN_STR) as conn:
        with conn.cursor() as cur:

            # Overview KPIs
            print("Computing overview KPIs...")
            cur.execute("SELECT COUNT(*), MIN(transaction_year), MAX(transaction_year), COUNT(DISTINCT town) FROM resale_prices;")
            total_rows, min_year, max_year, total_towns = cur.fetchone()

            cur.execute("SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY resale_price) FROM resale_prices WHERE transaction_year = (SELECT MAX(transaction_year) FROM resale_prices);")
            latest_median_price = float(cur.fetchone()[0])

            cur.execute("SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY resale_price) FROM resale_prices WHERE transaction_year = (SELECT MIN(transaction_year) FROM resale_prices);")
            earliest_median_price = float(cur.fetchone()[0])

            kpis = {"total_rows": int(total_rows), "min_year": int(min_year), "max_year": int(max_year),
                    "total_towns": int(total_towns), "latest_median_price": latest_median_price,
                    "earliest_median_price": earliest_median_price}
            with open(os.path.join(CACHE_DIR, "overview_kpis.json"), "w") as f:
                json.dump(kpis, f, indent=2)
            print(f"  saved overview_kpis.json")

            # Analysis 01
            print("Running 01_lease_decay_cliff.sql...")
            df = _run_sql_file(cur, os.path.join(SQL_DIR, "01_lease_decay_cliff.sql"))
            df.to_parquet(os.path.join(CACHE_DIR, "lease_decay.parquet"), index=False)
            print(f"  saved lease_decay.parquet  ({len(df):,} rows)")

            # Analysis 02
            print("Running 02_real_vs_nominal_growth.sql...")
            df = _run_sql_file(cur, os.path.join(SQL_DIR, "02_real_vs_nominal_growth.sql"))
            df.to_parquet(os.path.join(CACHE_DIR, "real_growth.parquet"), index=False)
            print(f"  saved real_growth.parquet  ({len(df):,} rows)")

            # Analysis 03
            print("Running 03_town_ranking_by_decade.sql...")
            df = _run_sql_file(cur, os.path.join(SQL_DIR, "03_town_ranking_by_decade.sql"))
            df.to_parquet(os.path.join(CACHE_DIR, "town_ranking.parquet"), index=False)
            print(f"  saved town_ranking.parquet  ({len(df):,} rows)")

            # Analysis 04 (two result sets)
            print("Running 04_price_per_sqm_storeys.sql...")
            with open(os.path.join(SQL_DIR, "04_price_per_sqm_storeys.sql"), "r") as f:
                stmts = [s.strip() for s in f.read().split(";") if s.strip()]
            cur.execute(stmts[0])
            _df_from_cursor(cur).to_parquet(os.path.join(CACHE_DIR, "size_eras.parquet"), index=False)
            cur.execute(stmts[1])
            _df_from_cursor(cur).to_parquet(os.path.join(CACHE_DIR, "storeys.parquet"), index=False)
            print(f"  saved size_eras.parquet + storeys.parquet")

            # Analysis 05
            print("Running 05_policy_event_impact.sql...")
            df = _run_sql_file(cur, os.path.join(SQL_DIR, "05_policy_event_impact.sql"))
            df.to_parquet(os.path.join(CACHE_DIR, "policy_impact.parquet"), index=False)
            print(f"  saved policy_impact.parquet  ({len(df):,} rows)")

    print("\nAll cache files written to data/cached/")
    print("Next steps:")
    print("  git add data/cached/")
    print("  git commit -m 'cache: precomputed analysis results for cloud deployment'")
    print("  git push origin main")
    print("  Then in Streamlit Cloud: Reboot app")


if __name__ == "__main__":
    main()
