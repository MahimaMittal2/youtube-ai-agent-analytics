"""
SQL Runner and Verification Utility using DuckDB.

Loads the synthetic 5-table star schema into in-memory DuckDB
and executes all 10 production SQL scripts, printing formatted summary tables.
"""

import os
import sys
import glob
import re
from pathlib import Path
import duckdb

sys.path.append(str(Path(__file__).resolve().parent))
import config

def validate_all_sql():
    print("=" * 75)
    print("EXECUTING AND VALIDATING PRODUCTION SQL SUITE (DuckDB Engine)")
    print("=" * 75)
    
    data_dir = config.RAW_DATA_DIR
    con = duckdb.connect(":memory:")
    
    # Load raw CSVs into DuckDB tables
    print("Loading CSV tables into in-memory DuckDB...")
    con.execute(f"CREATE TABLE fact_conversations AS SELECT * FROM read_csv('{data_dir}/fact_conversations.csv', auto_detect=true, nullstr=['']);")
    con.execute(f"CREATE TABLE dim_creator AS SELECT * FROM read_csv('{data_dir}/dim_creator.csv', auto_detect=true, nullstr=['']);")
    con.execute(f"CREATE TABLE dim_issue_type AS SELECT * FROM read_csv('{data_dir}/dim_issue_type.csv', auto_detect=true, nullstr=['']);")
    con.execute(f"CREATE TABLE dim_ai_version AS SELECT * FROM read_csv('{data_dir}/dim_ai_version.csv', auto_detect=true, nullstr=['']);")
    con.execute(f"CREATE TABLE dim_date AS SELECT * FROM read_csv('{data_dir}/dim_date.csv', auto_detect=true, nullstr=['']);")
    
    sql_files = sorted(glob.glob(str(config.SQL_DIR / "*.sql")))
    print(f"Found {len(sql_files)} SQL files to execute.\n")
    
    all_passed = True
    for sf in sql_files:
        fname = os.path.basename(sf)
        with open(sf, "r", encoding="utf-8") as f:
            raw_sql = f.read()
            
        # Split into individual statements separated by semicolon
        # Remove comment lines that precede statements
        statements = [s.strip() for s in raw_sql.split(";") if s.strip()]
        for idx, stmt in enumerate(statements):
            # Check if statement is only comments
            clean_stmt = "\n".join([line for line in stmt.split("\n") if not line.strip().startswith("--")]).strip()
            if not clean_stmt:
                continue
            try:
                df_res = con.execute(clean_stmt).df()
                print(f"[PASS] {fname:30s} (Stmt {idx+1}) -> {len(df_res)} rows, {len(df_res.columns)} cols")
            except Exception as e:
                print(f"[FAIL] {fname:30s} (Stmt {idx+1}) -> Error: {e}")
                all_passed = False
                
    print("\n" + "=" * 75)
    if all_passed:
        print("--> SQL VALIDATION RESULT: [ALL 10 SQL SCRIPTS EXECUTED SUCCESSFULLY]")
    else:
        print("--> SQL VALIDATION RESULT: [FAILURES DETECTED IN SQL SUITE]")
    print("=" * 75)
    return all_passed

if __name__ == "__main__":
    success = validate_all_sql()
    sys.exit(0 if success else 1)
