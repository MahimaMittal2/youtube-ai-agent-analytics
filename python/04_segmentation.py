"""
04_segmentation.py
Root-Cause Segmentation & Multivariate Driver Analysis for YouTube Creator Support.

Uses statistical modeling (Logistic Regression Odds Ratios) to isolate drivers of
human escalations and 7-day repeat contact failure demand.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

sys.path.append(str(Path(__file__).resolve().parent))
import config

def load_data():
    data_dir = config.RAW_DATA_DIR
    df_fact = pd.read_csv(data_dir / "fact_conversations.csv", keep_default_na=False, na_values=[""])
    for num_col in ["ai_response_time_sec", "human_handling_time_min"]:
        df_fact[num_col] = pd.to_numeric(df_fact[num_col], errors="coerce")
    df_fact["csat_score"] = pd.to_numeric(df_fact["csat_score"], errors="coerce").astype("Int64")
    df_fact["eligible_for_ai"] = df_fact["eligible_for_ai"].astype(bool)
    df_fact["ai_used"] = df_fact["ai_used"].astype(bool)
    df_fact["ai_contained"] = df_fact["ai_contained"].astype(bool)
    df_fact["ai_error_flag"] = df_fact["ai_error_flag"].astype(bool)
    df_fact["human_escalated"] = df_fact["human_escalated"].astype(bool)
    df_fact["repeat_contact_7d"] = df_fact["repeat_contact_7d"].astype(bool)
    
    df_fact["is_sarr"] = (
        df_fact["ai_used"] &
        df_fact["ai_contained"] &
        (df_fact["resolution_type"] == "AI_Resolved") &
        (~df_fact["repeat_contact_7d"])
    )
    return df_fact

def run_segmentation_analysis(df_fact):
    print("=" * 75)
    print("ROOT-CAUSE SEGMENTATION & MULTIVARIATE DRIVER ANALYSIS")
    print("=" * 75)
    
    ai_df = df_fact[df_fact["ai_used"]].copy()
    
    # -------------------------------------------------------------
    # 1. High-Risk Segment Identification (Complexity x Issue Type)
    # -------------------------------------------------------------
    print("\n--- 1. Multi-Dimensional Performance Matrix (Issue x Complexity) ---")
    matrix = ai_df.groupby(["issue_type", "issue_complexity"]).agg(
        volume=("conversation_id", "count"),
        containment=("ai_contained", "mean"),
        sarr=("is_sarr", "mean"),
        repeat_rate=("repeat_contact_7d", "mean"),
        error_rate=("ai_error_flag", "mean"),
        mean_csat=("csat_score", "mean")
    ).reset_index()
    matrix["wedge_pp"] = (matrix["containment"] - matrix["sarr"]) * 100
    matrix = matrix.sort_values("wedge_pp", ascending=False)
    
    print("\nTop 5 Highest Operational Wedge (False Containment) Segments:")
    for _, r in matrix.head(5).iterrows():
        print(f"  * {r['issue_type']:20s} [{r['issue_complexity']:6s}] -> Containment: {r['containment']:.1%}, SARR: {r['sarr']:.1%}, Wedge: {r['wedge_pp']:.1f} pp, Repeat Rate: {r['repeat_rate']:.1%}")

    # -------------------------------------------------------------
    # 2. Logistic Regression: Drivers of Human Escalation
    # -------------------------------------------------------------
    print("\n--- 2. Multivariate Driver Model: Human Escalation Propensity ---")
    # Model: P(Human Escalation) = f(Complexity, Issue Type, AI Error, AI Version, Creator Segment)
    ai_df["is_escalated"] = ai_df["human_escalated"].astype(int)
    ai_df["is_error"] = ai_df["ai_error_flag"].astype(int)
    
    model_esc = smf.logit(
        "is_escalated ~ C(issue_complexity, Treatment(reference='Low')) + "
        "is_error + C(ai_version, Treatment(reference='V1')) + "
        "C(creator_segment, Treatment(reference='Emerging'))",
        data=ai_df
    ).fit(disp=False)
    
    esc_or = np.exp(model_esc.params)
    esc_ci = np.exp(model_esc.conf_int())
    esc_p = model_esc.pvalues
    
    print("\nOdds Ratios for Human Escalation:")
    for term in esc_or.index:
        if term == "Intercept": continue
        print(f"  * {term:65s} -> OR: {esc_or[term]:.3f} [95% CI: {esc_ci.loc[term, 0]:.3f} - {esc_ci.loc[term, 1]:.3f}], p={esc_p[term]:.4e}")

    # -------------------------------------------------------------
    # 3. Logistic Regression: Drivers of 7-Day Repeat Contact (Failure Demand)
    # -------------------------------------------------------------
    print("\n--- 3. Multivariate Driver Model: 7-Day Repeat Contact (Failure Demand) ---")
    ai_df["is_repeat"] = ai_df["repeat_contact_7d"].astype(int)
    ai_df["is_resolved"] = (ai_df["resolution_status"] == "Resolved").astype(int)
    # Define false/premature containment independently of repeat_contact_7d:
    ai_df["is_false_contained"] = (ai_df["ai_contained"] & ((ai_df["resolution_status"] == "Unresolved") | (ai_df["ai_error_flag"]))).astype(int)
    
    model_rep = smf.logit(
        "is_repeat ~ is_resolved + is_error + is_false_contained + "
        "C(issue_complexity, Treatment(reference='Low'))",
        data=ai_df
    ).fit(disp=False)
    
    rep_or = np.exp(model_rep.params)
    rep_ci = np.exp(model_rep.conf_int())
    rep_p = model_rep.pvalues
    
    print("\nOdds Ratios for 7-Day Repeat Contact:")
    for term in rep_or.index:
        if term == "Intercept": continue
        print(f"  * {term:65s} -> OR: {rep_or[term]:.3f} [95% CI: {rep_ci.loc[term, 0]:.3f} - {rep_ci.loc[term, 1]:.3f}], p={rep_p[term]:.4e}")

    high_comp_key = [k for k in esc_or.index if "T.High" in k][0]
    high_comp_or = esc_or[high_comp_key]
    resolved_or = rep_or["is_resolved"]
    error_or = rep_or["is_error"]
    fc_or = rep_or["is_false_contained"]
    
    print("\n" + "=" * 75)
    print("--> KEY DRIVER SUMMARY:")
    print(f"  1. High Complexity issues increase escalation odds by {high_comp_or:.2f}x compared to Low Complexity.")
    print(f"  2. True Problem Resolution reduces repeat contact odds by {(1 - resolved_or):.1%} (OR: {resolved_or:.3f}).")
    print(f"  3. AI Errors multiply repeat contact failure demand odds by {error_or:.2f}x.")
    print(f"  4. False Containment (unresolved deflection) increases repeat contact odds by {fc_or:.2f}x.")
    print("=" * 75)

if __name__ == "__main__":
    df_fact = load_data()
    run_segmentation_analysis(df_fact)
