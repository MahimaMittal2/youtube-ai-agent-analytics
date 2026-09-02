"""
05_ab_test.py
Randomized Controlled Trial (A/B Test) Analysis Engine (May 1 - June 30, 2026).

Evaluates V1 (Control) vs. V2 (Treatment) with statistical hypothesis testing,
Wilson score and bootstrap confidence intervals, guardrail evaluation,
and heterogeneous subgroup treatment-effect estimation.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(str(Path(__file__).resolve().parent))
import config

# Styling
sns.set_theme(style="whitegrid")
plt.rcParams.update({"font.sans-serif": "Arial", "font.family": "sans-serif", "figure.dpi": 300})

def load_experiment_data():
    """Filter May-June randomized experiment records."""
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
    
    # SARR
    df_fact["is_sarr"] = (
        df_fact["ai_used"] &
        df_fact["ai_contained"] &
        (df_fact["resolution_type"] == "AI_Resolved") &
        (~df_fact["repeat_contact_7d"])
    )
    
    exp_df = df_fact[df_fact["experiment_group"].isin(["Control_V1", "Treatment_V2"])].copy()
    return exp_df

def two_proportion_z_test(count_c, nobs_c, count_t, nobs_t, alternative="two-sided"):
    """Two-sample z-test for difference in proportions."""
    p_c = count_c / nobs_c
    p_t = count_t / nobs_t
    p_pool = (count_c + count_t) / (nobs_c + nobs_t)
    se_pool = np.sqrt(p_pool * (1 - p_pool) * (1/nobs_c + 1/nobs_t))
    
    if se_pool == 0:
        return 0.0, 1.0, (0.0, 0.0)
        
    z_stat = (p_t - p_c) / se_pool
    
    if alternative == "two-sided":
        p_val = 2 * (1 - stats.norm.cdf(abs(z_stat)))
    elif alternative == "smaller":  # H1: p_t < p_c
        p_val = stats.norm.cdf(z_stat)
    else:  # H1: p_t > p_c
        p_val = 1 - stats.norm.cdf(z_stat)
        
    # Unpooled standard error for confidence interval
    se_diff = np.sqrt((p_c * (1 - p_c) / nobs_c) + (p_t * (1 - p_t) / nobs_t))
    ci_low = (p_t - p_c) - 1.96 * se_diff
    ci_high = (p_t - p_c) + 1.96 * se_diff
    
    return z_stat, p_val, (ci_low, ci_high)

def bootstrap_median_diff(series_c, series_t, n_boot=1000, rng_seed=42):
    """Bootstrap 95% confidence interval for difference in medians."""
    rng = np.random.default_rng(rng_seed)
    med_c = np.median(series_c)
    med_t = np.median(series_t)
    point_diff = med_t - med_c
    
    boot_diffs = []
    for _ in range(n_boot):
        sample_c = rng.choice(series_c, size=len(series_c), replace=True)
        sample_t = rng.choice(series_t, size=len(series_t), replace=True)
        boot_diffs.append(np.median(sample_t) - np.median(sample_c))
        
    ci_low, ci_high = np.percentile(boot_diffs, [2.5, 97.5])
    return point_diff, (ci_low, ci_high)

def analyze_experiment(exp_df):
    print("=" * 85)
    print("RANDOMIZED A/B EXPERIMENT EVALUATION (MAY 1 - JUNE 30, 2026)")
    print("=" * 85)
    
    ctrl = exp_df[exp_df["experiment_group"] == "Control_V1"]
    treat = exp_df[exp_df["experiment_group"] == "Treatment_V2"]
    
    n_c = len(ctrl)
    n_t = len(treat)
    
    print(f"\nSample Sizes: Control (V1) = {n_c:,} conversations | Treatment (V2) = {n_t:,} conversations")
    print(f"Randomization Allocation Split: {n_c / (n_c + n_t):.1%} Control / {n_t / (n_c + n_t):.1%} Treatment\n")
    
    # -----------------------------------------------------------------
    # Primary & Secondary Metrics Table
    # -----------------------------------------------------------------
    metrics = [
        ("SARR (North Star)", "is_sarr", "prop", "higher"),
        ("Containment Rate", "ai_contained", "prop", "higher"),
        ("Positive CSAT (Top-2)", "pos_csat", "prop", "higher"),
        ("Repeat Contact Rate (7d)", "repeat_contact_7d", "prop", "lower"),
        ("Human Escalation Rate", "human_escalated", "prop", "lower"),
        ("AI Error Rate (Guardrail)", "ai_error_flag", "prop", "lower"),
    ]
    
    # Create pos_csat indicator
    ctrl_csat = ctrl[ctrl["csat_score"].notnull()]
    treat_csat = treat[treat["csat_score"].notnull()]
    
    results = []
    
    print(f"{'Metric Name':30s} | {'Control (V1)':12s} | {'Treatment (V2)':14s} | {'Abs Diff (95% CI)':26s} | {'Rel Lift':10s} | {'p-value':10s} | {'Significance'}")
    print("-" * 125)
    
    for name, col, mtype, direction in metrics:
        if name == "Positive CSAT (Top-2)":
            c_pos = np.sum(ctrl_csat["csat_score"] >= 4)
            c_n = len(ctrl_csat)
            t_pos = np.sum(treat_csat["csat_score"] >= 4)
            t_n = len(treat_csat)
        else:
            c_pos = np.sum(ctrl[col])
            c_n = n_c
            t_pos = np.sum(treat[col])
            t_n = n_t
            
        p_c = c_pos / c_n
        p_t = t_pos / t_n
        abs_diff = p_t - p_c
        rel_lift = (p_t - p_c) / p_c * 100
        
        alt = "larger" if direction == "higher" else "smaller"
        z_stat, p_val, (ci_low, ci_high) = two_proportion_z_test(c_pos, c_n, t_pos, t_n, alternative="two-sided")
        
        sig = "***" if p_val < 0.001 else ("**" if p_val < 0.01 else ("*" if p_val < 0.05 else "n.s."))
        
        ci_str = f"{abs_diff*100:+.2f} pp [{ci_low*100:+.2f}, {ci_high*100:+.2f}]"
        print(f"{name:30s} | {p_c*100:10.2f}% | {p_t*100:12.2f}% | {ci_str:26s} | {rel_lift:+8.2f}% | {p_val:8.4e} | {sig}")
        
        results.append({
            "metric": name, "control": p_c, "treatment": p_t, 
            "abs_diff": abs_diff, "rel_lift_pct": rel_lift, "ci_low": ci_low, "ci_high": ci_high,
            "p_val": p_val, "sig": sig
        })

    # Continuous Metrics (Mean CSAT & Latency)
    print("\n--- Continuous Metrics (Welch's t-test & Bootstrap Medians) ---")
    
    # 1. Mean CSAT
    t_stat, p_val_csat = stats.ttest_ind(treat_csat["csat_score"], ctrl_csat["csat_score"], equal_var=False)
    mean_c_csat = np.mean(ctrl_csat["csat_score"])
    mean_t_csat = np.mean(treat_csat["csat_score"])
    print(f"Mean CSAT Score:   Control = {mean_c_csat:.3f} | Treatment = {mean_t_csat:.3f} | Delta = {mean_t_csat - mean_c_csat:+.3f} (t={t_stat:.2f}, p={p_val_csat:.4e})")
    
    # 2. Latency
    t_stat_lat, p_val_lat = stats.ttest_ind(treat["ai_response_time_sec"], ctrl["ai_response_time_sec"], equal_var=False)
    med_c_lat = np.median(ctrl["ai_response_time_sec"])
    med_t_lat = np.median(treat["ai_response_time_sec"])
    p90_c_lat = np.percentile(ctrl["ai_response_time_sec"], 90)
    p90_t_lat = np.percentile(treat["ai_response_time_sec"], 90)
    print(f"Median Latency:    Control = {med_c_lat:.2f}s | Treatment = {med_t_lat:.2f}s | Delta = {med_t_lat - med_c_lat:+.2f}s")
    print(f"P90 Latency:       Control = {p90_c_lat:.2f}s | Treatment = {p90_t_lat:.2f}s | Delta = {p90_t_lat - p90_c_lat:+.2f}s (t={t_stat_lat:.2f}, p={p_val_lat:.4e})")

    # -----------------------------------------------------------------
    # Heterogeneous Treatment Effects (HTE) by Complexity
    # -----------------------------------------------------------------
    print("\n" + "=" * 85)
    print("HETEROGENEOUS TREATMENT EFFECTS (HTE) BY COMPLEXITY TIER")
    print("=" * 85)
    print(f"{'Complexity Tier':18s} | {'V1 SARR':10s} | {'V2 SARR':10s} | {'SARR Lift (pp)':15s} | {'V1 Cont':10s} | {'V2 Cont':10s} | {'Cont Lift (pp)':15s} | {'Wedge Gap Change'}")
    print("-" * 115)
    
    for comp in ["Low", "Medium", "High"]:
        c_sub = ctrl[ctrl["issue_complexity"] == comp]
        t_sub = treat[treat["issue_complexity"] == comp]
        
        v1_sarr = np.mean(c_sub["is_sarr"])
        v2_sarr = np.mean(t_sub["is_sarr"])
        sarr_lift = (v2_sarr - v1_sarr) * 100
        
        v1_cont = np.mean(c_sub["ai_contained"])
        v2_cont = np.mean(t_sub["ai_contained"])
        cont_lift = (v2_cont - v1_cont) * 100
        
        w1 = (v1_cont - v1_sarr) * 100
        w2 = (v2_cont - v2_sarr) * 100
        w_delta = w2 - w1
        
        print(f"{comp:18s} | {v1_sarr*100:9.1f}% | {v2_sarr*100:9.1f}% | {sarr_lift:+14.2f} pp | {v1_cont*100:9.1f}% | {v2_cont*100:9.1f}% | {cont_lift:+14.2f} pp | {w1:.1f} pp -> {w2:.1f} pp ({w_delta:+.1f} pp)")

    # -----------------------------------------------------------------
    # Visualizations
    # -----------------------------------------------------------------
    generate_ab_charts(exp_df)

def generate_ab_charts(exp_df):
    """Generate high-resolution A/B test summary chart."""
    ctrl = exp_df[exp_df["experiment_group"] == "Control_V1"]
    treat = exp_df[exp_df["experiment_group"] == "Treatment_V2"]
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    
    # Chart 1: Core Headline Comparison
    kpis = ["SARR\n(North Star)", "Containment\nRate", "Positive\nCSAT", "Repeat\nContact (7d)", "AI Error\nRate"]
    v1_vals = [
        np.mean(ctrl["is_sarr"]) * 100,
        np.mean(ctrl["ai_contained"]) * 100,
        np.mean(ctrl.loc[ctrl["csat_score"].notnull(), "csat_score"] >= 4) * 100,
        np.mean(ctrl["repeat_contact_7d"]) * 100,
        np.mean(ctrl["ai_error_flag"]) * 100,
    ]
    v2_vals = [
        np.mean(treat["is_sarr"]) * 100,
        np.mean(treat["ai_contained"]) * 100,
        np.mean(treat.loc[treat["csat_score"].notnull(), "csat_score"] >= 4) * 100,
        np.mean(treat["repeat_contact_7d"]) * 100,
        np.mean(treat["ai_error_flag"]) * 100,
    ]
    
    x = np.arange(len(kpis))
    width = 0.35
    
    axes[0].bar(x - width/2, v1_vals, width, label="Control (V1 Baseline)", color="#757575", alpha=0.9)
    axes[0].bar(x + width/2, v2_vals, width, label="Treatment (V2 Agent)", color="#1976D2", alpha=0.9)
    
    for i in range(len(kpis)):
        diff = v2_vals[i] - v1_vals[i]
        axes[0].text(x[i], max(v1_vals[i], v2_vals[i]) + 2.0, f"{diff:+.1f} pp", ha="center", fontsize=9, fontweight="bold")
        
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(kpis)
    axes[0].set_ylabel("Rate (%)")
    axes[0].set_title("A/B Experiment KPI Comparison (May-June RCT)")
    axes[0].set_ylim(0, 100)
    axes[0].legend(loc="upper right", frameon=True)
    
    # Chart 2: HTE SARR Lift by Issue Type
    issue_hte = exp_df.groupby(["issue_type", "ai_version"])["is_sarr"].mean().unstack() * 100
    issue_hte["lift"] = issue_hte["V2"] - issue_hte["V1"]
    issue_hte = issue_hte.sort_values("lift", ascending=True)
    
    colors = ["#2E7D32" if l > 0 else "#C62828" for l in issue_hte["lift"]]
    axes[1].barh(issue_hte.index, issue_hte["lift"], color=colors, alpha=0.85, edgecolor="black")
    axes[1].axvline(0, color="black", linewidth=1.0, linestyle="--")
    
    for idx, (issue, row) in enumerate(issue_hte.iterrows()):
        axes[1].text(row["lift"] + (0.3 if row["lift"] >= 0 else -0.8), idx, f"{row['lift']:+.1f} pp", va="center", fontsize=9, fontweight="bold")
        
    axes[1].set_xlabel("SARR Absolute Difference (V2 - V1 in pp)")
    axes[1].set_title("V2 Treatment Effect on SARR by Issue Type")
    axes[1].set_xlim(min(issue_hte["lift"]) - 2, max(issue_hte["lift"]) + 4)
    
    plt.tight_layout()
    output_path = config.VISUALS_DIR / "fig5_ab_experiment_comparison.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[OK] Saved: {output_path.name}")

if __name__ == "__main__":
    exp_df = load_experiment_data()
    analyze_experiment(exp_df)
