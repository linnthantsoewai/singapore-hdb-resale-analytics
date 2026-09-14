"""
PostgreSQL ETL Pipeline for Singapore HDB Resale Transactions (1990-2026).

Directly ingests the 5 raw HDB CSV files, harmonizes schemas, calculates
remaining lease tenure and price-per-sqm, and streams into PostgreSQL via
high-performance native COPY protocol.
"""

import io
import os
import re
import sys
import time
import pandas as pd
import psycopg

YEAR_MONTH_PATTERN = re.compile(
    r"^(?:(?P<years>\d+)\s*years?)?\s*(?:(?P<months>\d+)\s*months?)?$",
    re.IGNORECASE,
)
STOREY_PATTERN = re.compile(r"^(\d+)\s*TO\s*(\d+)$", re.IGNORECASE)


def parse_lease(val, trans_year, commence_year):
    """
    Convert string/integer/missing remaining lease to continuous float years.
    """
    if pd.notna(val):
        val_str = str(val).strip()
        try:
            return round(float(val_str), 2)
        except ValueError:
            pass

        m = YEAR_MONTH_PATTERN.match(val_str)
        if m:
            years = int(m.group("years")) if m.group("years") else 0
            months = int(m.group("months")) if m.group("months") else 0
            if years > 0 or months > 0:
                return round(years + (months / 12.0), 2)

    # Pre-2015 formula: 99 - (transaction_year - lease_commence_date)
    if pd.notna(trans_year) and pd.notna(commence_year):
        try:
            calc = 99.0 - (float(trans_year) - float(commence_year))
            return round(max(0.0, calc), 2)
        except (ValueError, TypeError):
            pass

    return 0.0


def parse_storey(val):
    if not val or pd.isna(val):
        return None
    m = STOREY_PATTERN.match(str(val).strip())
    if m:
        return (int(m.group(1)) + int(m.group(2))) / 2.0
    try:
        return float(val)
    except ValueError:
        return None


def load_raw_csvs(data_dir: str = "data") -> pd.DataFrame:
    files = [
        "Resale Flat Prices (Based on Approval Date), 1990 - 1999.csv",
        "Resale Flat Prices (Based on Approval Date), 2000 - Feb 2012.csv",
        "Resale Flat Prices (Based on Registration Date), From Mar 2012 to Dec 2014.csv",
        "Resale Flat Prices (Based on Registration Date), From Jan 2015 to Dec 2016.csv",
        "Resale flat prices based on registration date from Jan-2017 onwards.csv",
    ]
    dfs = []
    search_dirs = [data_dir, ".", "data/raw"]
    for fname in files:
        fpath = None
        for d in search_dirs:
            candidate = os.path.join(d, fname)
            if os.path.exists(candidate):
                fpath = candidate
                break
        if not fpath:
            raise FileNotFoundError(f"Could not locate {fname} in any of {search_dirs}")
        print(f"Reading {fpath}...")
        df = pd.read_csv(fpath)
        print(f"  -> {len(df):,} rows")
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    print(f"Total rows to process: {len(combined):,}\n")
    return combined


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    print("Normalizing schemas and deriving analytics fields...")
    df = df.copy()

    df["town"] = df["town"].str.strip().str.upper()
    df["flat_type"] = df["flat_type"].str.strip().str.upper()
    df["flat_model"] = df["flat_model"].str.strip().str.title()
    df["block"] = df["block"].astype(str).str.strip().str.upper()
    df["street_name"] = df["street_name"].astype(str).str.strip().str.upper()

    df["transaction_year"] = df["month"].str.slice(0, 4).astype(int)
    df["transaction_month"] = df["month"].str.slice(5, 7).astype(int)

    def assign_decade(yr):
        if yr < 2000:
            return "1990s"
        elif yr < 2010:
            return "2000s"
        elif yr < 2020:
            return "2010s"
        else:
            return "2020s"

    df["decade"] = df["transaction_year"].apply(assign_decade)

    df["resale_price"] = df["resale_price"].astype(float)
    df["floor_area_sqm"] = df["floor_area_sqm"].astype(float)
    df["lease_commence_date"] = df["lease_commence_date"].astype(int)

    df["storey_midpoint"] = df["storey_range"].apply(parse_storey)
    df["price_per_sqm"] = (df["resale_price"] / df["floor_area_sqm"]).round(2)
    df["price_per_sqft"] = (df["resale_price"] / (df["floor_area_sqm"] * 10.7639)).round(2)

    if "remaining_lease" not in df.columns:
        df["remaining_lease"] = ""

    df["remaining_lease_years"] = [
        parse_lease(val, y, c)
        for val, y, c in zip(df["remaining_lease"], df["transaction_year"], df["lease_commence_date"])
    ]

    cols = [
        "month",
        "transaction_year",
        "transaction_month",
        "decade",
        "town",
        "flat_type",
        "flat_model",
        "block",
        "street_name",
        "storey_range",
        "storey_midpoint",
        "floor_area_sqm",
        "lease_commence_date",
        "remaining_lease_years",
        "resale_price",
        "price_per_sqm",
        "price_per_sqft",
    ]
    return df[cols]


def load_into_postgresql(df: pd.DataFrame, conn_str: str = "dbname=hdb_resale port=5433"):
    print(f"Connecting to PostgreSQL ({conn_str})...")
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            # Recreate schema
            schema_file = "sql/00_schema_and_load.sql"
            if os.path.exists(schema_file):
                print(f"Executing {schema_file}...")
                with open(schema_file, "r") as f:
                    cur.execute(f.read())
                conn.commit()

            print("Streaming 986k records into PostgreSQL table 'resale_prices'...")
            t0 = time.time()
            # Fast COPY stream via TSV in memory
            buffer = io.StringIO()
            df.to_csv(buffer, sep="\t", index=False, header=False, na_rep="\\N")
            buffer.seek(0)

            copy_sql = """
                COPY resale_prices (
                    month, transaction_year, transaction_month, decade,
                    town, flat_type, flat_model, block, street_name,
                    storey_range, storey_midpoint, floor_area_sqm,
                    lease_commence_date, remaining_lease_years,
                    resale_price, price_per_sqm, price_per_sqft
                ) FROM STDIN WITH (FORMAT text, NULL '\\N');
            """
            with cur.copy(copy_sql) as copy:
                while data := buffer.read(1024 * 1024):
                    copy.write(data)

            conn.commit()
            elapsed = time.time() - t0
            print(f"COPY finished in {elapsed:.2f} seconds!")

            # Verify count
            cur.execute("SELECT COUNT(*) FROM resale_prices;")
            total_loaded = cur.fetchone()[0]
            cur.execute("SELECT MIN(transaction_year), MAX(transaction_year) FROM resale_prices;")
            min_y, max_y = cur.fetchone()

            print("\n" + "=" * 55)
            print("POSTGRESQL INGESTION VERIFICATION")
            print("=" * 55)
            print(f"Total Transactions in PostgreSQL: {total_loaded:,}")
            print(f"Historical Coverage:             {min_y} to {max_y} (36 Years)")
            print("=" * 55)


if __name__ == "__main__":
    t_start = time.time()
    raw_df = load_raw_csvs(".")
    clean_df = transform_data(raw_df)
    load_into_postgresql(clean_df)
    print(f"Total ETL runtime: {time.time() - t_start:.2f} seconds")
