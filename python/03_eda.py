"""
03_eda.py
Exploratory Data Analysis & Visualizations for YouTube Creator Support AI Agent.

Generates high-resolution diagnostic charts saved to visuals/ directory.
"""

import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(str(Path(__file__).resolve().parent))
import config

# Set styling
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    "font.sans-serif": "Arial",
    "font.family": "sans-serif",
    "figure.titlesize": 16,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 11,
    "figure.dpi": 300,
})

def load_data():
    """Load cleaned facts and dimensions."""
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
    
    df_creator = pd.read_csv(data_dir / "dim_creator.csv", keep_default_na=False, na_values=[""])
    df_issue = pd.read_csv(data_dir / "dim_issue_type.csv", keep_default_na=False, na_values=[""])
    df_date = pd.read_csv(data_dir / "dim_date.csv", keep_default_na=False, na_values=[""])
    
    # Merge date attributes
    df_fact = df_fact.merge(df_date[["date", "month", "month_name", "quarter"]], left_on="conversation_date", right_on="date", how="left")
    
    # Calculate SARR indicator
    df_fact["is_sarr"] = (
        df_fact["ai_used"] &
        df_fact["ai_contained"] &
        (df_fact["resolution_type"] == "AI_Resolved") &
        (~df_fact["repeat_contact_7d"])
    )
    return df_fact, df_creator, df_issue, df_date

def generate_figure1_time_trends(df_fact):
    """Figure 1: Monthly SARR, Containment, and CSAT Longitudinal Trends."""
    ai_df = df_fact[df_fact["ai_used"]].copy()
    monthly = ai_df.groupby("month").agg(
        containment=("ai_contained", "mean"),
        sarr=("is_sarr", "mean"),
        positive_csat=("csat_score", lambda x: np.mean(x >= 4)),
        repeat_rate=("repeat_contact_7d", "mean"),
        error_rate=("ai_error_flag", "mean"),
        total_vol=("conversation_id", "count")
    ).reset_index()
    
    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    
    months = ["Jan", "Feb", "Mar", "Apr", "May (RCT)", "Jun (RCT)", "Jul", "Aug"]
    x = np.arange(len(months))
    
    ax1.plot(x, monthly["containment"] * 100, marker="o", color="#1f77b4", linewidth=2.5, label="AI Containment Rate (%)")
    ax1.plot(x, monthly["sarr"] * 100, marker="s", color="#2ca02c", linewidth=2.5, label="Successful AI Resolution Rate (SARR %)")
    ax1.plot(x, monthly["positive_csat"] * 100, marker="^", color="#ff7f0e", linewidth=2.0, linestyle="--", label="Positive CSAT (Top-2 Box %)")
    ax1.plot(x, monthly["repeat_rate"] * 100, marker="d", color="#d62728", linewidth=2.0, linestyle=":", label="7-Day Repeat Contact Rate (%)")
    
    # Fill the wedge between Containment and SARR
    ax1.fill_between(x, monthly["sarr"] * 100, monthly["containment"] * 100, color="#1f77b4", alpha=0.12, label="False Containment Wedge")
    
    # Add vertical shading for experiment period (May-June)
    ax1.axvspan(3.5, 5.5, color="#f0f0f0", alpha=0.7, label="May-June A/B Experiment")
    
    ax1.set_title("Monthly AI Agent Performance & The Operational Wedge Gap (Jan-Aug 2026)", pad=15)
    ax1.set_xlabel("Calendar Month (2026)")
    ax1.set_ylabel("Metric Rate (%)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(months)
    ax1.set_ylim(0, 100)
    ax1.legend(loc="lower left", frameon=True, facecolor="white", edgecolor="#cccccc")
    
    plt.tight_layout()
    output_path = config.VISUALS_DIR / "fig1_kpi_time_trends.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[OK] Saved: {output_path.name}")

def generate_figure2_wedge(df_fact):
    """Figure 2: The Containment vs. SARR Wedge Breakdown by Issue Category."""
    ai_df = df_fact[df_fact["ai_used"]].copy()
    issue_grp = ai_df.groupby("issue_type").agg(
        containment=("ai_contained", "mean"),
        sarr=("is_sarr", "mean"),
        volume=("conversation_id", "count")
    ).reset_index()
    issue_grp["wedge"] = issue_grp["containment"] - issue_grp["sarr"]
    issue_grp = issue_grp.sort_values("sarr", ascending=True)
    
    fig, ax = plt.subplots(figsize=(11, 6))
    y = np.arange(len(issue_grp))
    height = 0.38
    
    ax.barh(y - height/2, issue_grp["containment"] * 100, height, label="AI Containment Rate", color="#4285F4", alpha=0.9)
    ax.barh(y + height/2, issue_grp["sarr"] * 100, height, label="Successful AI Resolution Rate (SARR)", color="#34A853", alpha=0.9)
    
    # Annotate the wedge gap
    for idx, row in issue_grp.reset_index().iterrows():
        wedge_val = (row["containment"] - row["sarr"]) * 100
        ax.text(row["containment"] * 100 + 1.0, idx - height/2, f"Gap: {wedge_val:.1f} pp", 
                va="center", fontsize=9, color="#EA4335", fontweight="bold")
        
    ax.set_yticks(y)
    ax.set_yticklabels(issue_grp["issue_type"])
    ax.set_xlabel("Rate (%)")
    ax.set_title("AI Containment vs. True SARR Resolution Across Issue Types", pad=15)
    ax.set_xlim(0, 116)
    ax.set_ylim(-0.85, len(issue_grp) - 0.15)
    ax.legend(loc="lower right", bbox_to_anchor=(0.99, 0.03), frameon=True, facecolor="white", framealpha=0.95, fontsize=9.5)
    
    plt.tight_layout()
    output_path = config.VISUALS_DIR / "fig2_containment_vs_sarr_wedge.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[OK] Saved: {output_path.name}")

def generate_figure3_complexity(df_fact):
    """Figure 3: Interaction between Complexity and Agent Version."""
    exp_df = df_fact[df_fact["experiment_group"].isin(["Control_V1", "Treatment_V2"])].copy()
    comp_v = exp_df.groupby(["issue_complexity", "ai_version"]).agg(
        containment=("ai_contained", "mean"),
        sarr=("is_sarr", "mean"),
        csat=("csat_score", "mean"),
        error_rate=("ai_error_flag", "mean")
    ).reset_index()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.5))
    
    # Subplot 1: Containment vs SARR
    comp_order = ["Low", "Medium", "High"]
    x = np.arange(len(comp_order))
    width = 0.20
    
    v1_cont = [comp_v[(comp_v["issue_complexity"] == c) & (comp_v["ai_version"] == "V1")]["containment"].values[0] * 100 for c in comp_order]
    v2_cont = [comp_v[(comp_v["issue_complexity"] == c) & (comp_v["ai_version"] == "V2")]["containment"].values[0] * 100 for c in comp_order]
    v1_sarr = [comp_v[(comp_v["issue_complexity"] == c) & (comp_v["ai_version"] == "V1")]["sarr"].values[0] * 100 for c in comp_order]
    v2_sarr = [comp_v[(comp_v["issue_complexity"] == c) & (comp_v["ai_version"] == "V2")]["sarr"].values[0] * 100 for c in comp_order]
    
    b1 = ax1.bar(x - 1.5*width, v1_cont, width, label="V1 Containment", color="#90CAF9")
    b2 = ax1.bar(x - 0.5*width, v2_cont, width, label="V2 Containment", color="#1E88E5")
    b3 = ax1.bar(x + 0.5*width, v1_sarr, width, label="V1 SARR", color="#A5D6A7")
    b4 = ax1.bar(x + 1.5*width, v2_sarr, width, label="V2 SARR", color="#2E7D32")
    
    # Restrained direct value callouts above each bar
    for bars in [b1, b2, b3, b4]:
        for bar in bars:
            height_val = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height_val + 1.0,
                     f"{height_val:.1f}%", ha="center", va="bottom", fontsize=8, color="#333333", fontweight="semibold")
    
    ax1.set_xticks(x)
    ax1.set_xticklabels(comp_order)
    ax1.set_ylabel("Rate (%)")
    ax1.set_title("Containment & SARR by Complexity (May-June RCT)")
    ax1.set_ylim(0, 108)
    ax1.legend(loc="upper right", fontsize=9)
    
    # Subplot 2: Mean CSAT
    v1_csat = [comp_v[(comp_v["issue_complexity"] == c) & (comp_v["ai_version"] == "V1")]["csat"].values[0] for c in comp_order]
    v2_csat = [comp_v[(comp_v["issue_complexity"] == c) & (comp_v["ai_version"] == "V2")]["csat"].values[0] for c in comp_order]
    
    ax2.plot(comp_order, v1_csat, marker="o", linewidth=2.5, color="#FB8C00", label="V1 Baseline CSAT")
    ax2.plot(comp_order, v2_csat, marker="s", linewidth=2.5, color="#E53935", label="V2 Treatment CSAT")
    ax2.set_title("Mean CSAT Score by Complexity (May-June RCT)")
    ax2.set_ylabel("Mean CSAT (1-5 Scale)")
    ax2.set_ylim(2.5, 5.0)
    ax2.legend(loc="lower left")
    
    plt.tight_layout()
    output_path = config.VISUALS_DIR / "fig3_complexity_interaction.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[OK] Saved: {output_path.name}")

def generate_figure4_error_csat(df_fact):
    """Figure 4: AI Error Impact on CSAT Distribution and Repeat Inbound."""
    ai_df = df_fact[df_fact["ai_used"] & df_fact["csat_score"].notnull()].copy()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Consistent color mapping: No Error = Slate Blue (#546E7A), AI Error = Coral Red (#E53935)
    palette = ["#546E7A", "#E53935"]
    
    # Left: CSAT score distribution
    csat_err = pd.crosstab(ai_df["csat_score"], ai_df["ai_error_flag"], normalize="columns") * 100
    csat_err.columns = ["No Error", "AI Error"]
    csat_err.plot(kind="bar", ax=ax1, color=palette, alpha=0.90, edgecolor="black", width=0.7)
    ax1.set_title("CSAT Score Distribution: Error vs. No Error")
    ax1.set_xlabel("CSAT Rating (1 to 5 Stars)")
    ax1.set_ylabel("Proportion of Responses (%)")
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=0)
    ax1.legend(title="AI Error State")
    
    # Right: 7-Day Repeat Contact Rate by Quality Tier & Error
    qual_df = df_fact[df_fact["ai_used"]].groupby(["ai_response_quality", "ai_error_flag"])["repeat_contact_7d"].mean().unstack() * 100
    qual_df.columns = ["No Error", "AI Error"]
    qual_df = qual_df.reindex(["High", "Medium", "Low"])
    qual_df.plot(kind="bar", ax=ax2, color=palette, alpha=0.90, edgecolor="black", width=0.6)
    ax2.set_title("7-Day Repeat Contact Rate by AI Response Quality")
    ax2.set_xlabel("AI Response Quality Assessment")
    ax2.set_ylabel("Repeat Contact Rate (%)")
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=0)
    ax2.legend(title="AI Error State")
    
    plt.tight_layout()
    output_path = config.VISUALS_DIR / "fig4_ai_error_csat_impact.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[OK] Saved: {output_path.name}")

def main():
    print("=" * 75)
    print("RUNNING EXPLORATORY DATA ANALYSIS & VISUALIZATION ENGINE")
    print("=" * 75)
    df_fact, df_creator, df_issue, df_date = load_data()
    print(f"Loaded {len(df_fact):,} conversations across {len(df_creator):,} creators.")
    
    generate_figure1_time_trends(df_fact)
    generate_figure2_wedge(df_fact)
    generate_figure3_complexity(df_fact)
    generate_figure4_error_csat(df_fact)
    
    print("\n[OK] All exploratory visuals successfully rendered to visuals/")

if __name__ == "__main__":
    main()
