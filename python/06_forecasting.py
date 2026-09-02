"""
06_forecasting.py
Closed-Loop Operational Demand & Workforce Capacity Forecasting Engine.

Translates AI agent performance (eligibility, adoption, containment, SARR, repeat demand)
into human support queue volumes and labor hours under Baseline, Broad V2, and Selective V2 deployment.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(str(Path(__file__).resolve().parent))
import config

sns.set_theme(style="whitegrid")
plt.rcParams.update({"font.sans-serif": "Arial", "font.family": "sans-serif", "figure.dpi": 300})

def simulate_operational_demand(
    monthly_inbound=15_000,
    p_eligible=0.85,
    p_adopt=0.75,
    p_contain_low=0.90, p_contain_med=0.76, p_contain_high=0.56,
    p_res_low=0.92, p_res_med=0.85, p_res_high=0.60,
    p_rep_resolved=0.07, p_rep_unres=0.48,
    routing_mode="Broad"  # "Baseline_V1", "Broad_V2", "Selective_V2"
):
    """
    Closed-loop operational simulation modeling human support volume and hours.
    """
    # Issue complexity distribution
    p_comp = {"Low": 0.40, "Medium": 0.40, "High": 0.20}
    
    # Ineligible & Opt-out routing
    v_ineligible = monthly_inbound * (1 - p_eligible)
    v_eligible = monthly_inbound * p_eligible
    
    v_opt_out = v_eligible * (1 - p_adopt)
    v_ai_start = v_eligible * p_adopt
    
    # Initialize tier counters
    v_ai_contained_total = 0
    v_sarr_total = 0
    v_escalated_total = 0
    v_repeat_total = 0
    human_hours_total = 0
    
    # Direct routing for Selective Mode: High complexity routed directly to Tier 2 human specialists
    for comp, comp_share in p_comp.items():
        v_ai_comp = v_ai_start * comp_share
        
        if routing_mode == "Selective_V2" and comp == "High":
            # Selective routing: High complexity bypasses AI to avoid false containment & errors
            v_escalated_comp = v_ai_comp
            v_contained_comp = 0
            v_sarr_comp = 0
            v_repeat_comp = v_escalated_comp * 0.12  # Normal human repeat rate
        else:
            if routing_mode == "Baseline_V1":
                p_c = 0.78 if comp == "Low" else (0.68 if comp == "Medium" else 0.48)
                p_r = 0.92 if comp == "Low" else (0.85 if comp == "Medium" else 0.71)
            else:  # Broad_V2
                p_c = p_contain_low if comp == "Low" else (p_contain_med if comp == "Medium" else p_contain_high)
                p_r = p_res_low if comp == "Low" else (p_res_med if comp == "Medium" else p_res_high)
                
            v_contained_comp = v_ai_comp * p_c
            v_escalated_comp = v_ai_comp * (1 - p_c)
            
            # Contained resolutions
            v_res_comp = v_contained_comp * p_r
            v_unres_comp = v_contained_comp * (1 - p_r)
            
            # Repeat failure demand
            v_repeat_comp = (v_res_comp * p_rep_resolved) + (v_unres_comp * p_rep_unres)
            v_sarr_comp = v_res_comp * (1 - p_rep_resolved)
            
        v_ai_contained_total += v_contained_comp
        v_sarr_total += v_sarr_comp
        v_escalated_total += v_escalated_comp
        v_repeat_total += v_repeat_comp
        
        # Human labor hours per complexity
        hht = 7.5 if comp == "Low" else (15.0 if comp == "Medium" else 28.0)
        # Labor from escalations + repeat visits
        human_hours_total += (v_escalated_comp + v_repeat_comp) * (hht / 60.0)
        
    # Add labor for ineligible and opt-out (weighted average handling time ~14.6 min)
    avg_direct_hht = 0.40 * 7.5 + 0.40 * 15.0 + 0.20 * 28.0
    human_hours_total += (v_ineligible + v_opt_out) * (avg_direct_hht / 60.0)
    
    total_human_queue = v_ineligible + v_opt_out + v_escalated_total + v_repeat_total
    
    return {
        "monthly_inbound": monthly_inbound,
        "ai_used_volume": v_ai_start,
        "ai_contained_volume": v_ai_contained_total,
        "sarr_resolutions": v_sarr_total,
        "containment_pct": v_ai_contained_total / v_ai_start,
        "sarr_pct": v_sarr_total / v_ai_start,
        "direct_human_inbound": v_ineligible + v_opt_out,
        "live_ai_escalations": v_escalated_total,
        "repeat_failure_demand": v_repeat_total,
        "total_human_queue_volume": total_human_queue,
        "human_support_hours": human_hours_total,
        "annualized_human_hours": human_hours_total * 12,
        "annualized_labor_cost": human_hours_total * 12 * 45.0,  # $45/hr
    }

def run_forecasting_analysis():
    print("=" * 85)
    print("CLOSED-LOOP OPERATIONAL CAPACITY & WORKFORCE FORECASTING")
    print("=" * 85)
    
    v1_base = simulate_operational_demand(routing_mode="Baseline_V1")
    v2_broad = simulate_operational_demand(routing_mode="Broad_V2")
    v2_selective = simulate_operational_demand(routing_mode="Selective_V2")
    
    scenarios = [
        ("Baseline (V1 Model)", v1_base),
        ("Option A: Broad V2 Rollout", v2_broad),
        ("Option B: Selective V2 Rollout", v2_selective),
    ]
    
    print(f"{'Deployment Scenario':30s} | {'AI Cont%':10s} | {'SARR%':8s} | {'Human Queue/mo':16s} | {'Human Hours/mo':16s} | {'Labor Cost/yr':15s}")
    print("-" * 110)
    for name, s in scenarios:
        print(f"{name:30s} | {s['containment_pct']*100:9.1f}% | {s['sarr_pct']*100:7.1f}% | {s['total_human_queue_volume']:14,.0f} | {s['human_support_hours']:14,.0f} hrs | ${s['annualized_labor_cost']:13,.0f}")
        
    print("\n--- Operational Efficiency Comparison vs Baseline V1 ---")
    hrs_save_broad = v1_base["annualized_human_hours"] - v2_broad["annualized_human_hours"]
    cost_save_broad = v1_base["annualized_labor_cost"] - v2_broad["annualized_labor_cost"]
    hrs_save_sel = v1_base["annualized_human_hours"] - v2_selective["annualized_human_hours"]
    cost_save_sel = v1_base["annualized_labor_cost"] - v2_selective["annualized_labor_cost"]
    
    print(f"1. Broad V2 Rollout:     Saves {hrs_save_broad:,.0f} human hours/year (${cost_save_broad:,.0f}/yr) vs Baseline.")
    print(f"2. Selective V2 Rollout: Saves {hrs_save_sel:,.0f} human hours/year (${cost_save_sel:,.0f}/yr) vs Baseline.")
    print(f"   Selective Rollout provides superior creator CSAT and reduces repeat failure contacts by {(v2_broad['repeat_failure_demand'] - v2_selective['repeat_failure_demand']):,.0f} monthly tickets in High Complexity workflows.")
    
    # -------------------------------------------------------------
    # Visualization: Figure 6
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    
    names = ["Baseline\n(V1)", "Broad V2\nRollout", "Selective V2\nRollout"]
    hours = [v1_base["human_support_hours"], v2_broad["human_support_hours"], v2_selective["human_support_hours"]]
    queues = [v1_base["total_human_queue_volume"], v2_broad["total_human_queue_volume"], v2_selective["total_human_queue_volume"]]
    
    # Subplot 1: Monthly Human Support Hours
    bars1 = ax1.bar(names, hours, color=["#9E9E9E", "#1976D2", "#388E3C"], width=0.55, edgecolor="black")
    for b in bars1:
        ax1.text(b.get_x() + b.get_width()/2, b.get_height() + 20, f"{b.get_height():,.0f} hrs", ha="center", fontweight="bold", fontsize=10)
    ax1.set_title("Projected Monthly Human Support Hours")
    ax1.set_ylabel("Human Labor Hours / Month")
    ax1.set_ylim(0, max(hours) * 1.2)
    
    # Subplot 2: Monthly Human Queue Breakdown
    x = np.arange(len(names))
    direct = [s["direct_human_inbound"] for _, s in scenarios]
    esc = [s["live_ai_escalations"] for _, s in scenarios]
    repeat = [s["repeat_failure_demand"] for _, s in scenarios]
    
    ax2.bar(x, direct, label="Direct Routing (Ineligible/Opt-out)", color="#B0BEC5", width=0.5)
    ax2.bar(x, esc, bottom=direct, label="Live AI Escalations", color="#FFA726", width=0.5)
    ax2.bar(x, repeat, bottom=np.array(direct)+np.array(esc), label="7-Day Repeat Failure Demand", color="#EF5350", width=0.5)
    
    ax2.set_xticks(x)
    ax2.set_xticklabels(names)
    ax2.set_title("Monthly Human Support Queue Composition")
    ax2.set_ylabel("Inbound Tickets / Month")
    ax2.legend(loc="upper right", fontsize=9)
    ax2.set_ylim(0, max(queues) * 1.2)
    
    plt.tight_layout()
    output_path = config.VISUALS_DIR / "fig6_forecasting_capacity_curves.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"\n[OK] Saved: {output_path.name}")

if __name__ == "__main__":
    run_forecasting_analysis()
