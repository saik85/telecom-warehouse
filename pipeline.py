"""Build the telecom warehouse with DuckDB: load star schema, then run the
ARPU / churn / retention analytics SQL, and print the marts."""
import os
import duckdb

DB = "telecom.duckdb"


def run_sql_file(con, path):
    with open(path) as f:
        con.execute(f.read())


def main():
    if os.path.exists(DB):
        os.remove(DB)
    con = duckdb.connect(DB)

    print("Building star schema...")
    run_sql_file(con, os.path.join("sql", "01_star_schema.sql"))
    for t in ["dim_subscriber", "dim_date", "fact_billing"]:
        n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  ✓ {t}: {n:,} rows")

    print("\nBuilding analytics marts...")
    run_sql_file(con, os.path.join("sql", "02_analytics.sql"))
    for t in ["mart_arpu", "mart_churn", "mart_retention"]:
        n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  ✓ {t}: {n:,} rows")

    print("\n  Monthly churn:")
    print(con.execute(
        "SELECT month_key, base, churned, churn_rate_pct FROM mart_churn ORDER BY month_key"
    ).df().to_string(index=False))

    print("\n  ARPU by plan (latest month):")
    print(con.execute("""
        SELECT plan, SUM(active_subs) AS active_subs, ROUND(SUM(revenue),2) AS revenue,
               ROUND(SUM(revenue)/NULLIF(SUM(active_subs),0),2) AS arpu
        FROM mart_arpu
        WHERE month_key = (SELECT MAX(month_key) FROM mart_arpu)
        GROUP BY plan ORDER BY arpu DESC
    """).df().to_string(index=False))

    con.close()
    print("\nDone. Warehouse in telecom.duckdb (marts: arpu, churn, retention)")


if __name__ == "__main__":
    main()
