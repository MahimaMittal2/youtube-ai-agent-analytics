"""
Data Quality and Validation Suite for YouTube Creator Support AI Agent Analytics.

Executes schema integrity checks, foreign key validations, distribution sanity tests,
and experimental covariate balance checks (SMD and absolute proportion differences).

Supports:
- python python/02_data_quality.py --pilot (validates pilot dataset)
- python python/02_data_quality.py (validates full dataset)
"""

import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

# Import configuration
sys.path.append(str(Path(__file__).resolve().parent))
import config

def calculate_smd_categorical(df, col, group_col, group_a, group_b):
    """
    Calculate Standardized Mean Difference (SMD) and absolute proportion differences
    for categorical variables between two groups.
    """
    df_a = df[df[group_col] == group_a]
    df_b = df[df[group_col] == group_b]
    
    n_a = len(df_a)
    n_b = len(df_b)
    
    cats = df[col].dropna().unique()
    smd_list = []
    diff_p_list = []
    
    for cat in cats:
        p_a = np.mean(df_a[col] == cat)
        p_b = np.mean(df_b[col] == cat)
        diff_p = abs(p_a - p_b)
        diff_p_list.append(diff_p)
        
        # Pooled variance for binary indicator
        var_a = p_a * (1 - p_a)
        var_b = p_b * (1 - p_b)
        pooled_sd = np.sqrt((var_a + var_b) / 2.0)
        
        if pooled_sd > 0:
            smd = diff_p / pooled_sd
        else:
            smd = 0.0
        smd_list.append(smd)
        
    return {
        "max_smd": np.max(smd_list),
        "mean_smd": np.mean(smd_list),
        "max_diff_p": np.max(diff_p_list),
        "categories": dict(zip(cats, smd_list))
    }

def run_data_quality_suite(data_dir, is_pilot=False):
    """Execute complete suite of data quality checks."""
    print("=" * 75)
    print(f"RUNNING DATA QUALITY ASSURANCE SUITE [{'PILOT' if is_pilot else 'FULL DATASET'}]")
    print("=" * 75)
    print(f"Reading tables from: {data_dir}")
    
    # 1. Load tables with explicit na handling so literal "None" is preserved
    try:
        df_fact = pd.read_csv(data_dir / "fact_conversations.csv", keep_default_na=False, na_values=[""])
        # Convert empty strings back to NaN/None for optional columns
        for num_col in ["ai_response_time_sec", "human_handling_time_min"]:
            df_fact[num_col] = pd.to_numeric(df_fact[num_col], errors="coerce")
        df_fact["csat_score"] = pd.to_numeric(df_fact["csat_score"], errors="coerce").astype("Int64")
        df_fact["eligible_for_ai"] = df_fact["eligible_for_ai"].astype(bool)
        df_fact["ai_used"] = df_fact["ai_used"].astype(bool)
        df_fact["ai_contained"] = df_fact["ai_contained"].astype(bool)
        df_fact["ai_error_flag"] = df_fact["ai_error_flag"].astype(bool)
        df_fact["human_escalated"] = df_fact["human_escalated"].astype(bool)
        df_fact["repeat_contact_7d"] = df_fact["repeat_contact_7d"].astype(bool)
        
        df_creator = pd.read_csv(data_dir / "dim_creator.csv", keep_default_na=False, na_values=[""])
        df_issue = pd.read_csv(data_dir / "dim_issue_type.csv", keep_default_na=False, na_values=[""])
        df_version = pd.read_csv(data_dir / "dim_ai_version.csv", keep_default_na=False, na_values=[""])
        df_date = pd.read_csv(data_dir / "dim_date.csv", keep_default_na=False, na_values=[""])
    except Exception as e:
        print(f"[FATAL] Failed to load CSV files: {e}")
        return False
        
    passed_all = True
    
    # -------------------------------------------------------------
    # Check 1: Primary Key Uniqueness & Non-Nullability
    # -------------------------------------------------------------
    print("\n--- Check 1: Primary Key Uniqueness & Table Volumes ---")
    print(f"fact_conversations rows: {len(df_fact):,} (Unique IDs: {df_fact['conversation_id'].nunique():,})")
    print(f"dim_creator rows:        {len(df_creator):,} (Unique IDs: {df_creator['creator_id'].nunique():,})")
    print(f"dim_issue_type rows:     {len(df_issue):,} (Unique Types: {df_issue['issue_type'].nunique():,})")
    print(f"dim_ai_version rows:     {len(df_version):,} (Unique Versions: {df_version['ai_version'].nunique():,})")
    print(f"dim_date rows:           {len(df_date):,} (Unique Dates: {df_date['date'].nunique():,})")
    
    pk_checks = [
        ("fact_conversations.conversation_id", len(df_fact) == df_fact["conversation_id"].nunique()),
        ("dim_creator.creator_id", len(df_creator) == df_creator["creator_id"].nunique()),
        ("dim_issue_type.issue_type", len(df_issue) == df_issue["issue_type"].nunique()),
        ("dim_ai_version.ai_version", len(df_version) == df_version["ai_version"].nunique()),
        ("dim_date.date", len(df_date) == df_date["date"].nunique()),
    ]
    for name, res in pk_checks:
        status = "[PASS]" if res else "[FAIL]"
        if not res: passed_all = False
        print(f"  {status} {name} is strictly unique and non-null.")
        
    # -------------------------------------------------------------
    # Check 2: Foreign Key Referential Integrity
    # -------------------------------------------------------------
    print("\n--- Check 2: Foreign Key Referential Integrity ---")
    fk_checks = [
        ("fact_conversations -> dim_creator", df_fact["creator_id"].isin(df_creator["creator_id"]).all()),
        ("fact_conversations -> dim_issue_type", df_fact["issue_type"].isin(df_issue["issue_type"]).all()),
        ("fact_conversations -> dim_ai_version", df_fact["ai_version"].isin(df_version["ai_version"]).all()),
        ("fact_conversations -> dim_date", df_fact["conversation_date"].isin(df_date["date"]).all()),
    ]
    for name, res in fk_checks:
        status = "[PASS]" if res else "[FAIL]"
        if not res: passed_all = False
        print(f"  {status} 100% valid referential integrity for {name}")

    # -------------------------------------------------------------
    # Check 3: Logical Consistency & Domain Constraints
    # -------------------------------------------------------------
    print("\n--- Check 3: State Constraints & Mutex Rules ---")
    
    # Non-AI routing consistency
    non_ai_rows = df_fact[~df_fact["ai_used"]]
    non_ai_valid = ((non_ai_rows["ai_version"] == "None") & (~non_ai_rows["ai_contained"]) & (non_ai_rows["human_escalated"])).all()
    # Containment vs escalation mutex for AI conversations
    ai_convs = df_fact[df_fact["ai_used"]]
    mutex_valid = (ai_convs["ai_contained"] != ai_convs["human_escalated"]).all()
    # Duration / Handling time sanity
    handling_time_valid = (df_fact["human_handling_time_min"] >= 0).all() and ((df_fact["human_escalated"]) == (df_fact["human_handling_time_min"] > 0)).all()
    # CSAT domain
    valid_csat = df_fact["csat_score"].dropna().isin([1, 2, 3, 4, 5]).all()
    
    logic_checks = [
        ("Non-AI interactions route directly to human with ai_version='None'", non_ai_valid),
        ("AI interactions: ai_contained and human_escalated are strictly mutually exclusive", mutex_valid),
        ("Human handling time is positive iff human_escalated is True", handling_time_valid),
        ("CSAT scores strictly within range [1, 5] (or null for non-responses)", valid_csat),
    ]
    for name, res in logic_checks:
        status = "[PASS]" if res else "[FAIL]"
        if not res: passed_all = False
        print(f"  {status} {name}")
        
    # -------------------------------------------------------------
    # Check 4: Empirical Relationship Validations
    # -------------------------------------------------------------
    print("\n--- Check 4: Empirical Relationship & Sanity Checks ---")
    
    # 4A. Complexity vs Resolution Monotonicity
    ai_data = df_fact[df_fact["ai_used"]].copy()
    ai_data["is_sarr"] = (
        ai_data["ai_contained"] &
        (ai_data["resolution_type"] == "AI_Resolved") &
        (~ai_data["repeat_contact_7d"])
    )
    sarr_by_comp = ai_data.groupby("issue_complexity")["is_sarr"].mean()
    comp_monotonic = sarr_by_comp["Low"] > sarr_by_comp["Medium"] > sarr_by_comp["High"]
    status = "[PASS]" if comp_monotonic else "[FAIL]"
    if not comp_monotonic: passed_all = False
    print(f"  {status} Complexity vs SARR Monotonicity:")
    print(f"         Low Complexity SARR:    {sarr_by_comp['Low']:.1%}")
    print(f"         Medium Complexity SARR: {sarr_by_comp['Medium']:.1%}")
    print(f"         High Complexity SARR:   {sarr_by_comp['High']:.1%}")
    
    # 4B. AI Error vs CSAT and Repeat Contact
    err_csat_drop = ai_data.groupby("ai_error_flag")["csat_score"].mean()
    err_repeat_jump = ai_data.groupby("ai_error_flag")["repeat_contact_7d"].mean()
    error_valid = (err_csat_drop[True] < err_csat_drop[False]) and (err_repeat_jump[True] > err_repeat_jump[False])
    status = "[PASS]" if error_valid else "[FAIL]"
    if not error_valid: passed_all = False
    print(f"  {status} AI Error Impact on CSAT & Repeat Contacts:")
    print(f"         Mean CSAT (No Error):   {err_csat_drop[False]:.2f} / 5.0")
    print(f"         Mean CSAT (AI Error):   {err_csat_drop[True]:.2f} / 5.0 (Delta: {err_csat_drop[True] - err_csat_drop[False]:.2f})")
    print(f"         Repeat Rate (No Error): {err_repeat_jump[False]:.1%}")
    print(f"         Repeat Rate (AI Error): {err_repeat_jump[True]:.1%}")

    # 4C. Containment vs SARR (False Containment Gap)
    cont_rate = ai_data["ai_contained"].mean()
    sarr_rate = ai_data["is_sarr"].mean()
    wedge_valid = cont_rate > sarr_rate
    status = "[PASS]" if wedge_valid else "[FAIL]"
    if not wedge_valid: passed_all = False
    print(f"  {status} Containment vs SARR Gap (Demonstrating False Containment):")
    print(f"         Headline Containment:   {cont_rate:.1%}")
    print(f"         Successful SARR:        {sarr_rate:.1%}")
    print(f"         Operational Wedge Gap:  {(cont_rate - sarr_rate):.1%}")

    # -------------------------------------------------------------
    # Check 5: A/B Experiment Covariate Balance Diagnostics
    # -------------------------------------------------------------
    print("\n--- Check 5: A/B Experiment Covariate Balance (May-June RCT) ---")
    exp_data = df_fact[df_fact["experiment_group"].isin(["Control_V1", "Treatment_V2"])].copy()
    
    if len(exp_data) > 0:
        print(f"Experiment records: {len(exp_data):,} (Control_V1: {np.sum(exp_data['experiment_group'] == 'Control_V1'):,}, Treatment_V2: {np.sum(exp_data['experiment_group'] == 'Treatment_V2'):,})")
        
        balance_results = {}
        smd_threshold = 0.10 if is_pilot else 0.05
        diff_p_threshold = 0.03 if is_pilot else 0.015
        
        for covariate in ["issue_type", "issue_complexity", "region", "creator_segment"]:
            res = calculate_smd_categorical(exp_data, covariate, "experiment_group", "Control_V1", "Treatment_V2")
            balance_results[covariate] = res
            
            # Chi-square diagnostic
            contingency = pd.crosstab(exp_data[covariate], exp_data["experiment_group"])
            chi2, p_val, _, _ = stats.chi2_contingency(contingency)
            
            smd_pass = res["max_smd"] < smd_threshold and res["max_diff_p"] < diff_p_threshold
            status = "[PASS]" if smd_pass else "[WARN]"
            if not smd_pass: passed_all = False
            
            print(f"  {status} {covariate:16s} -> Max SMD: {res['max_smd']:.4f} (Mean: {res['mean_smd']:.4f}) | Max |diff_p|: {res['max_diff_p']:.2%} | Chi2 p-val: {p_val:.3f}")
            
    print("\n" + "=" * 75)
    if passed_all:
        print("--> OVERALL QUALITY SUITE STATUS: [ALL CHECKS PASSED 100%]")
    else:
        print("--> OVERALL QUALITY SUITE STATUS: [ISSUES DETECTED - PLEASE REVIEW]")
    print("=" * 75)
    
    return passed_all

def main():
    parser = argparse.ArgumentParser(description="Validate data quality for YouTube AI Agent simulation.")
    parser.add_argument("--pilot", action="store_true", help="Validate the pilot dataset.")
    args = parser.parse_args()
    
    data_dir = config.DATA_DIR / "pilot" if args.pilot else config.RAW_DATA_DIR
    success = run_data_quality_suite(data_dir, is_pilot=args.pilot)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
