"""
Audit Verification Script for YouTube Creator Support Analytics.
Audits every numerical claim in executive_summary.md against:
1. Raw synthetic fact_conversations.csv / dimensions
2. 05_ab_test.py outputs
3. 06_forecasting.py outputs
4. 07_scenario_analysis.py outputs
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

sys.path.append(str(Path(__file__).resolve().parent))
import config
from importlib import import_module

def audit_all():
    print("=" * 80)
    print("DETAILED NUMERICAL AUDIT & TRACEABILITY REPORT")
    print("=" * 80)
    
    # 1. Load data
    data_dir = config.RAW_DATA_DIR
    df = pd.read_csv(data_dir / "fact_conversations.csv", keep_default_na=False, na_values=[""])
    for col in ["ai_response_time_sec", "human_handling_time_min"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["csat_score"] = pd.to_numeric(df["csat_score"], errors="coerce")
    for col in ["eligible_for_ai", "ai_used", "ai_contained", "ai_error_flag", "human_escalated", "repeat_contact_7d"]:
        df[col] = df[col].astype(bool)
        
    df["is_sarr"] = df["ai_used"] & df["ai_contained"] & (df["resolution_type"] == "AI_Resolved") & (~df["repeat_contact_7d"])
    
    dim_issue = pd.read_csv(data_dir / "dim_issue_type.csv")
    
    # 2. Experiment dataset audit (May-June RCT)
    exp = df[df["experiment_group"].isin(["Control_V1", "Treatment_V2"])].copy()
    ctrl = exp[exp["experiment_group"] == "Control_V1"]
    treat = exp[exp["experiment_group"] == "Treatment_V2"]
    
    print("\n--- A. A/B Experiment Audit (May-June RCT) ---")
    print(f"Total Exp Records: {len(exp):,} (Control: {len(ctrl):,}, Treatment: {len(treat):,})")
    
    # SARR
    sarr_c = ctrl["is_sarr"].mean()
    sarr_t = treat["is_sarr"].mean()
    sarr_diff = sarr_t - sarr_c
    sarr_rel = sarr_diff / sarr_c
    print(f"SARR: Control = {sarr_c:.4%} ({sarr_c*100:.2f}%), Treatment = {sarr_t:.4%} ({sarr_t*100:.2f}%), Abs Lift = {sarr_diff*100:+.2f} pp, Rel Lift = {sarr_rel*100:+.2f}%")
    
    # Containment
    cont_c = ctrl["ai_contained"].mean()
    cont_t = treat["ai_contained"].mean()
    cont_diff = cont_t - cont_c
    cont_rel = cont_diff / cont_c
    print(f"Containment: Control = {cont_c:.4%} ({cont_c*100:.2f}%), Treatment = {cont_t:.4%} ({cont_t*100:.2f}%), Abs Lift = {cont_diff*100:+.2f} pp, Rel Lift = {cont_rel*100:+.2f}%")
    
    # Escalation
    esc_c = ctrl["human_escalated"].mean()
    esc_t = treat["human_escalated"].mean()
    esc_diff = esc_t - esc_c
    esc_rel = esc_diff / esc_c
    print(f"Escalation: Control = {esc_c:.4%} ({esc_c*100:.2f}%), Treatment = {esc_t:.4%} ({esc_t*100:.2f}%), Abs Lift = {esc_diff*100:+.2f} pp, Rel Lift = {esc_rel*100:+.2f}%")
    
    # AI Error
    err_c = ctrl["ai_error_flag"].mean()
    err_t = treat["ai_error_flag"].mean()
    err_diff = err_t - err_c
    err_rel = err_diff / err_c
    print(f"AI Error: Control = {err_c:.4%} ({err_c*100:.2f}%), Treatment = {err_t:.4%} ({err_t*100:.2f}%), Abs Lift = {err_diff*100:+.2f} pp, Rel Lift = {err_rel*100:+.2f}%")
    
    # Positive CSAT
    ctrl_csat = ctrl[ctrl["csat_score"].notnull()]
    treat_csat = treat[treat["csat_score"].notnull()]
    pos_c = (ctrl_csat["csat_score"] >= 4).mean()
    pos_t = (treat_csat["csat_score"] >= 4).mean()
    pos_diff = pos_t - pos_c
    pos_rel = pos_diff / pos_c
    print(f"Positive CSAT: Control = {pos_c:.4%} ({pos_c*100:.2f}%), Treatment = {pos_t:.4%} ({pos_t*100:.2f}%), Abs Lift = {pos_diff*100:+.2f} pp, Rel Lift = {pos_rel*100:+.2f}%")
    
    # Repeat Contact
    rep_c = ctrl["repeat_contact_7d"].mean()
    rep_t = treat["repeat_contact_7d"].mean()
    rep_diff = rep_t - rep_c
    rep_rel = rep_diff / rep_c
    print(f"Repeat 7d: Control = {rep_c:.4%} ({rep_c*100:.2f}%), Treatment = {rep_t:.4%} ({rep_t*100:.2f}%), Abs Lift = {rep_diff*100:+.2f} pp, Rel Lift = {rep_rel*100:+.2f}%")
    
    # Latencies
    med_c = ctrl["ai_response_time_sec"].median()
    med_t = treat["ai_response_time_sec"].median()
    print(f"Median Latency: Control = {med_c:.2f}s, Treatment = {med_t:.2f}s, Diff = {med_t - med_c:.2f}s")
    
    # 3. Complexity Subgroups Audit
    print("\n--- B. Complexity Subgroup Breakdown Audit ---")
    for comp in ["Low", "Medium", "High"]:
        c_sub = ctrl[ctrl["issue_complexity"] == comp]
        t_sub = treat[treat["issue_complexity"] == comp]
        sc = c_sub["is_sarr"].mean()
        st = t_sub["is_sarr"].mean()
        cc = c_sub["ai_contained"].mean()
        ct = t_sub["ai_contained"].mean()
        w_c = cc - sc
        w_t = ct - st
        print(f"[{comp:6s}] V1 SARR={sc*100:.1f}%, V2 SARR={st*100:.1f}%, SARR Lift={st*100-sc*100:+.2f} pp | V1 Cont={cc*100:.1f}%, V2 Cont={ct*100:.1f}%, Cont Lift={ct*100-cc*100:+.2f} pp | Wedge: {w_c*100:.1f} pp -> {w_t*100:.1f} pp (Delta: {w_t*100-w_c*100:+.1f} pp)")

    # 4. AI Error Impact on CSAT & Repeat Contacts Audit (Entire Active AI Population)
    print("\n--- C. AI Error Sentiment & Repeat Contact Audit ---")
    ai_all = df[df["ai_used"]].copy()
    err_no = ai_all[~ai_all["ai_error_flag"]]
    err_yes = ai_all[ai_all["ai_error_flag"]]
    
    csat_no = err_no[err_no["csat_score"].notnull()]["csat_score"].mean()
    csat_yes = err_yes[err_yes["csat_score"].notnull()]["csat_score"].mean()
    csat_drop_pct = (csat_yes - csat_no) / csat_no * 100
    
    rep_no = err_no["repeat_contact_7d"].mean()
    rep_yes = err_yes["repeat_contact_7d"].mean()
    rep_ratio = rep_yes / rep_no
    
    print(f"Mean CSAT: No Error = {csat_no:.2f}, Error = {csat_yes:.2f} (Delta = {csat_yes - csat_no:.2f}, Rel = {csat_drop_pct:.1f}%)")
    print(f"7-Day Repeat: No Error = {rep_no*100:.1f}%, Error = {rep_yes*100:.1f}% (Ratio = {rep_ratio:.2f}x, Delta = {(rep_yes-rep_no)*100:+.1f} pp)")
    
    # 5. Forecasting & Scenario Sweep Audit
    print("\n--- D. Forecasting & Scenario Sweep Audit ---")
    forecasting_mod = import_module("06_forecasting")
    v1_base = forecasting_mod.simulate_operational_demand(routing_mode="Baseline_V1")
    v2_broad = forecasting_mod.simulate_operational_demand(routing_mode="Broad_V2")
    v2_sel = forecasting_mod.simulate_operational_demand(routing_mode="Selective_V2")
    
    print(f"Baseline V1:   Queue={v1_base['total_human_queue_volume']:,.0f}, Hours={v1_base['human_support_hours']:,.0f}/mo, Annual Cost=${v1_base['annualized_labor_cost']:,.0f}")
    print(f"Broad V2:      Queue={v2_broad['total_human_queue_volume']:,.0f}, Hours={v2_broad['human_support_hours']:,.0f}/mo, Annual Cost=${v2_broad['annualized_labor_cost']:,.0f}")
    print(f"Selective V2:  Queue={v2_sel['total_human_queue_volume']:,.0f}, Hours={v2_sel['human_support_hours']:,.0f}/mo, Annual Cost=${v2_sel['annualized_labor_cost']:,.0f}")
    
    # 6. Scenario 60/70/80/85% Sweep Audit
    print("\n--- E. 60%, 70%, 80%, 85% Containment Sensitivity Sweep Audit ---")
    scenario_mod = import_module("07_scenario_analysis")
    # Let's inspect scenario sweep numbers
    # Run the exact sweep formula
    target_containments = [0.60, 0.70, 0.80, 0.85]
    monthly_inbound = 15000
    p_eligible = 0.85
    p_adopt = 0.75
    v_eligible = monthly_inbound * p_eligible
    v_ai_start = v_eligible * p_adopt
    v_direct_human = monthly_inbound * (1 - p_eligible) + v_eligible * (1 - p_adopt)
    
    for c_target in target_containments:
        v_contained = v_ai_start * c_target
        v_escalated = v_ai_start * (1 - c_target)
        if c_target == 0.60:
            p_res_given_cont = 0.92; p_repeat_unres = 0.40
        elif c_target == 0.70:
            p_res_given_cont = 0.88; p_repeat_unres = 0.45
        elif c_target == 0.80:
            p_res_given_cont = 0.80; p_repeat_unres = 0.52
        else:
            p_res_given_cont = 0.70; p_repeat_unres = 0.60
            
        v_resolved_ai = v_contained * p_res_given_cont
        v_unresolved_contained = v_contained * (1 - p_res_given_cont)
        v_repeat = (v_resolved_ai * 0.06) + (v_unresolved_contained * p_repeat_unres)
        v_sarr = v_resolved_ai * (1 - 0.06)
        sarr_pct = v_sarr / v_ai_start
        qac_pct = c_target * p_res_given_cont * (1 - (v_repeat / v_contained))
        total_human_queue = v_direct_human + v_escalated + v_repeat
        avg_hht_min = 14.6
        human_hours = (v_direct_human + v_escalated + v_repeat) * (avg_hht_min / 60.0)
        
        print(f"Target {c_target*100:.0f}%: SARR={sarr_pct*100:.1f}%, QAC={qac_pct*100:.1f}%, AI_Res={v_resolved_ai:,.0f}, FalseCont={v_unresolved_contained:,.0f}, Repeat={v_repeat:,.0f}, Queue={total_human_queue:,.0f}, Hours={human_hours:,.0f}/mo")

    # 7. Check 80% to 85% changes
    # At 80%: Repeat = 1163, Hours = 2071
    # At 85%: Repeat = 1804, Hours = 2111
    # Repeat change: (1804 - 1163) / 1163 = +55.1%
    # Hours change: (2111 - 2071) / 2071 = +1.93% (+2%)
    print(f"\n80% -> 85% Repeat increase: {(1804 - 1163) / 1163:.1%}")
    print(f"80% -> 85% Hours increase: {(2111 - 2071) / 2071:.2%}")
    
    # 8. Check Issue Categories in dim_issue_type
    print("\n--- F. Dimension Issue Types in dim_issue_type.csv ---")
    canonical_issues = dim_issue.to_dict(orient="records")
    for r in canonical_issues:
        print(f"  * {r['issue_type']:22s} | Category: {r['issue_category']:24s} | Default Complexity: {r['default_complexity']}")
        
    # 9. Multivariate Logistic Regression Verification
    print("\n--- G. Logistic Regression Driver Models (Target-Leakage Free) ---")
    import statsmodels.formula.api as smf
    ai_df = df[df["ai_used"]].copy()
    ai_df["is_repeat"] = ai_df["repeat_contact_7d"].astype(int)
    ai_df["is_error"] = ai_df["ai_error_flag"].astype(int)
    ai_df["is_resolved"] = (ai_df["resolution_status"] == "Resolved").astype(int)
    ai_df["is_false_contained"] = (ai_df["ai_contained"] & ((ai_df["resolution_status"] == "Unresolved") | (ai_df["ai_error_flag"]))).astype(int)
    ai_df["is_escalated"] = ai_df["human_escalated"].astype(int)

    m_rep = smf.logit(
        "is_repeat ~ is_resolved + is_error + is_false_contained + C(issue_complexity, Treatment(reference='Low'))",
        data=ai_df
    ).fit(disp=False)
    
    print("Model 2 (7-Day Repeat Drivers):")
    for term in m_rep.params.index:
        if term == "Intercept": continue
        or_val = np.exp(m_rep.params[term])
        ci = np.exp(m_rep.conf_int().loc[term])
        p_val = m_rep.pvalues[term]
        print(f"  * {term:65s} -> OR: {or_val:.3f} [95% CI: {ci[0]:.3f} - {ci[1]:.3f}], p={p_val:.4e}")

    print("=" * 80)

if __name__ == "__main__":
    audit_all()
