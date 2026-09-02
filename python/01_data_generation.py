"""
Synthetic Data Generation Engine for YouTube Creator Support AI Agent Analytics.

Generates 5-table star schema:
1. fact_conversations
2. dim_creator
3. dim_issue_type
4. dim_ai_version
5. dim_date

Supports:
- Pilot dataset generation (--pilot, 5,000 rows)
- Full dataset generation (exactly 120,000 rows)
"""

import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Import configuration
sys.path.append(str(Path(__file__).resolve().parent))
import config

def generate_dim_date(start_date_str, end_date_str):
    """Generate calendar dimension table."""
    dates = pd.date_range(start=start_date_str, end=end_date_str, freq="D")
    df_date = pd.DataFrame({
        "date": dates.strftime("%Y-%m-%d"),
        "year": dates.year,
        "quarter": "Q" + dates.quarter.astype(str),
        "month": dates.month,
        "month_name": dates.strftime("%B"),
        "week": dates.isocalendar().week.astype(int),
        "day_of_week": dates.strftime("%A"),
    })
    return df_date

def generate_dim_issue_type():
    """Generate canonical issue type dimension table."""
    records = []
    for issue, category in config.ISSUE_CATEGORIES.items():
        # Derive default complexity
        priors = config.ISSUE_COMPLEXITY_PRIORS[issue]
        default_comp = ["Low", "Medium", "High"][int(np.argmax(priors))]
        records.append({
            "issue_type": issue,
            "issue_category": category,
            "default_complexity": default_comp,
        })
    return pd.DataFrame(records)

def generate_dim_ai_version():
    """Generate AI agent engine version dimension table."""
    records = [
        {
            "ai_version": "V1",
            "version_name": "Baseline Creator Agent",
            "launch_date": "2025-10-01",
            "experiment_group": "Control / Baseline",
            "description": "First-generation conversational support model with standard RAG retrieval.",
        },
        {
            "ai_version": "V2",
            "version_name": "Enhanced LLM Reasoning Agent",
            "launch_date": "2026-05-01",
            "experiment_group": "Treatment / Improved Agent",
            "description": "Second-generation model with multi-step policy reasoning and reduced latency.",
        },
        {
            "ai_version": "None",
            "version_name": "Direct Human Routing",
            "launch_date": "2024-01-01",
            "experiment_group": "Non-AI Route",
            "description": "Inbound tickets routed directly to human support queues without AI intervention.",
        },
    ]
    return pd.DataFrame(records)

def generate_dim_creator(num_creators, rng):
    """Generate creator universe with realistic demographic distributions."""
    creator_ids = [f"CRT-{i:05d}" for i in range(1, num_creators + 1)]
    
    # Sample segment
    segments = list(config.CREATOR_SEGMENT_DISTRIBUTION.keys())
    seg_probs = list(config.CREATOR_SEGMENT_DISTRIBUTION.values())
    creator_segments = rng.choice(segments, size=num_creators, p=seg_probs)
    
    # Sample region
    regions = list(config.REGION_DISTRIBUTION.keys())
    reg_probs = list(config.REGION_DISTRIBUTION.values())
    creator_regions = rng.choice(regions, size=num_creators, p=reg_probs)
    
    # Sample subscriber channel size conditioned on segment
    channel_sizes = np.zeros(num_creators, dtype=int)
    for i, seg in enumerate(creator_segments):
        if seg == "Emerging":
            # 100 to 9,999
            channel_sizes[i] = int(np.clip(rng.lognormal(mean=7.2, sigma=0.8), 100, 9_999))
        elif seg == "Growth":
            # 10,000 to 99,999
            channel_sizes[i] = int(np.clip(rng.lognormal(mean=10.2, sigma=0.5), 10_000, 99_999))
        elif seg == "Established":
            # 100,000 to 999,999
            channel_sizes[i] = int(np.clip(rng.lognormal(mean=12.2, sigma=0.6), 100_000, 999_999))
        else:  # Large
            # 1,000,000 to 25,000,000
            channel_sizes[i] = int(np.clip(rng.lognormal(mean=14.5, sigma=0.7), 1_000_000, 25_000_000))
            
    # Sample creator tenure in months (1 to 120)
    tenure_months = rng.integers(low=1, high=121, size=num_creators)
    
    df_creator = pd.DataFrame({
        "creator_id": creator_ids,
        "creator_segment": creator_segments,
        "region": creator_regions,
        "channel_size": channel_sizes,
        "creator_tenure_months": tenure_months,
    })
    return df_creator

def generate_fact_conversations(total_conversations, df_creator, df_date, rng):
    """Generate fact_conversations with high-fidelity probabilistic dependency graph."""
    num_creators = len(df_creator)
    
    # 1. Select creator for each conversation
    # Weight ticket propensity: Emerging & Growth submit slightly more inquiries
    seg_weights = {"Emerging": 1.25, "Growth": 1.10, "Established": 0.85, "Large": 0.60}
    creator_weights = df_creator["creator_segment"].map(seg_weights).values
    creator_weights = creator_weights / creator_weights.sum()
    
    chosen_creator_indices = rng.choice(num_creators, size=total_conversations, p=creator_weights)
    creator_ids = df_creator["creator_id"].values[chosen_creator_indices]
    creator_segments = df_creator["creator_segment"].values[chosen_creator_indices]
    creator_regions = df_creator["region"].values[chosen_creator_indices]
    
    # 2. Conversation Date
    all_dates = df_date["date"].values
    num_days = len(all_dates)
    # Day-of-week seasonality (slightly higher weekday volume)
    day_weights = np.ones(num_days)
    for i, d in enumerate(all_dates):
        dow = df_date.loc[df_date["date"] == d, "day_of_week"].values[0]
        if dow in ["Saturday", "Sunday"]:
            day_weights[i] = 0.75
    day_weights /= day_weights.sum()
    
    conversation_dates = rng.choice(all_dates, size=total_conversations, p=day_weights)
    
    # Sort by date for chronological consistency
    sort_idx = np.argsort(conversation_dates)
    creator_ids = creator_ids[sort_idx]
    creator_segments = creator_segments[sort_idx]
    creator_regions = creator_regions[sort_idx]
    conversation_dates = conversation_dates[sort_idx]
    
    conversation_ids = [f"CNV-2026-{i:07d}" for i in range(1, total_conversations + 1)]
    
    # 3. Issue Type
    issue_types_list = list(config.ISSUE_TYPE_DISTRIBUTION.keys())
    issue_probs = list(config.ISSUE_TYPE_DISTRIBUTION.values())
    issue_types = rng.choice(issue_types_list, size=total_conversations, p=issue_probs)
    
    # 4. Complexity conditioned on Issue Type
    complexities = []
    complexity_choices = ["Low", "Medium", "High"]
    for it in issue_types:
        priors = config.ISSUE_COMPLEXITY_PRIORS[it]
        complexities.append(rng.choice(complexity_choices, p=priors))
    complexities = np.array(complexities)
    
    # 5. Entry Channel
    channels = list(config.ENTRY_CHANNELS.keys())
    chan_probs = list(config.ENTRY_CHANNELS.values())
    entry_channels = rng.choice(channels, size=total_conversations, p=chan_probs)
    
    # 6. AI Eligibility (~85% overall, modulated by issue/channel)
    elig_probs = np.full(total_conversations, config.BASE_AI_ELIGIBILITY_RATE)
    # Adjust: Channel Access & Policy slightly lower eligibility for high complexity
    elig_probs[(complexities == "High") & np.isin(issue_types, ["Channel Access", "Policy"])] -= 0.10
    elig_probs[entry_channels == "Email_Form"] -= 0.15
    elig_probs = np.clip(elig_probs, 0.50, 0.98)
    eligible_for_ai = rng.random(total_conversations) < elig_probs
    
    # 7. AI Used (Adoption conditioned on segment and eligibility)
    ai_used = np.zeros(total_conversations, dtype=bool)
    for seg, p_adopt in config.AI_ADOPTION_BY_SEGMENT.items():
        mask = (creator_segments == seg) & eligible_for_ai
        ai_used[mask] = rng.random(np.sum(mask)) < p_adopt
        
    # 8. Experiment Group & AI Version Assignment
    experiment_group = np.full(total_conversations, "Non_Experiment", dtype=object)
    ai_version = np.full(total_conversations, "None", dtype=object)
    
    # Convert dates for range checking
    exp_start = config.EXPERIMENT_START
    exp_end = config.EXPERIMENT_END
    
    pre_mask = (conversation_dates < exp_start) & ai_used
    exp_mask = (conversation_dates >= exp_start) & (conversation_dates <= exp_end) & ai_used
    post_mask = (conversation_dates > exp_end) & ai_used
    
    # Pre-experiment: 100% V1
    experiment_group[pre_mask] = "Pre_Experiment"
    ai_version[pre_mask] = "V1"
    
    # Controlled Experiment: 50% Control (V1), 50% Treatment (V2) Stratified
    # Stratification block: (issue_type, complexity, creator_segment, region)
    exp_indices = np.where(exp_mask)[0]
    if len(exp_indices) > 0:
        df_exp = pd.DataFrame({
            "idx": exp_indices,
            "stratum": [
                f"{it}|{comp}|{seg}|{reg}"
                for it, comp, seg, reg in zip(
                    issue_types[exp_indices],
                    complexities[exp_indices],
                    creator_segments[exp_indices],
                    creator_regions[exp_indices],
                )
            ],
        })
        
        # For each stratum, perform balanced block permutation
        treatment_flags = np.zeros(len(exp_indices), dtype=bool)
        for _, group in df_exp.groupby("stratum"):
            grp_locs = group.index.values
            n_grp = len(grp_locs)
            if n_grp == 1:
                treatment_flags[grp_locs] = rng.random() < 0.50
            else:
                n_treat = n_grp // 2 + (1 if (n_grp % 2 == 1 and rng.random() < 0.50) else 0)
                assign = np.zeros(n_grp, dtype=bool)
                assign[:n_treat] = True
                rng.shuffle(assign)
                treatment_flags[grp_locs] = assign
            
        ai_version[exp_indices] = np.where(treatment_flags, "V2", "V1")
        experiment_group[exp_indices] = np.where(treatment_flags, "Treatment_V2", "Control_V1")
        
    # Post-experiment: 80% V2, 20% V1 observational
    post_indices = np.where(post_mask)[0]
    if len(post_indices) > 0:
        post_v2 = rng.random(len(post_indices)) < 0.80
        ai_version[post_indices] = np.where(post_v2, "V2", "V1")
        experiment_group[post_indices] = "Post_Experiment"
        
    # Non-AI conversations keep ai_version = "None"
    non_ai_mask = ~ai_used
    ai_version[non_ai_mask] = "None"
    experiment_group[non_ai_mask] = "Non_Experiment"
    
    # 9. AI Latency
    ai_response_time_sec = np.full(total_conversations, np.nan)
    v1_ai_mask = (ai_version == "V1")
    v2_ai_mask = (ai_version == "V2")
    
    p_v1 = config.LATENCY_PARAMS["V1"]
    p_v2 = config.LATENCY_PARAMS["V2"]
    
    ai_response_time_sec[v1_ai_mask] = np.round(rng.lognormal(mean=p_v1["mu"], sigma=p_v1["sigma"], size=np.sum(v1_ai_mask)), 2)
    ai_response_time_sec[v2_ai_mask] = np.round(rng.lognormal(mean=p_v2["mu"], sigma=p_v2["sigma"], size=np.sum(v2_ai_mask)), 2)
    
    # 10. AI Error / Hallucination Flag
    # Conditional probability: base(version) + complexity + issue effect
    ai_error_flag = np.zeros(total_conversations, dtype=bool)
    
    # Error priors: V1 vs V2 by complexity
    # Low: V1 2.5%, V2 1.4%
    # Med: V1 4.0%, V2 2.7%
    # High: V1 7.0%, V2 5.5%
    err_probs = np.zeros(total_conversations)
    err_probs[(ai_version == "V1") & (complexities == "Low")] = 0.025
    err_probs[(ai_version == "V1") & (complexities == "Medium")] = 0.040
    err_probs[(ai_version == "V1") & (complexities == "High")] = 0.070
    
    err_probs[(ai_version == "V2") & (complexities == "Low")] = 0.014
    err_probs[(ai_version == "V2") & (complexities == "Medium")] = 0.027
    err_probs[(ai_version == "V2") & (complexities == "High")] = 0.055
    
    # Policy / Copyright extra risk factor (+1.0% error)
    err_probs[ai_used & np.isin(issue_types, ["Policy", "Copyright"])] += 0.010
    
    ai_error_flag[ai_used] = rng.random(np.sum(ai_used)) < err_probs[ai_used]
    
    # 11. AI Response Quality ('High', 'Medium', 'Low')
    ai_response_quality = np.full(total_conversations, None, dtype=object)
    for i in np.where(ai_used)[0]:
        ver = ai_version[i]
        comp = complexities[i]
        err = ai_error_flag[i]
        
        if err:
            # Errors heavily penalize quality
            q_choice = rng.choice(["High", "Medium", "Low"], p=[0.05, 0.20, 0.75])
        else:
            if ver == "V2":
                if comp == "Low":
                    q_choice = rng.choice(["High", "Medium", "Low"], p=[0.88, 0.10, 0.02])
                elif comp == "Medium":
                    q_choice = rng.choice(["High", "Medium", "Low"], p=[0.72, 0.23, 0.05])
                else:
                    q_choice = rng.choice(["High", "Medium", "Low"], p=[0.48, 0.38, 0.14])
            else:  # V1
                if comp == "Low":
                    q_choice = rng.choice(["High", "Medium", "Low"], p=[0.78, 0.18, 0.04])
                elif comp == "Medium":
                    q_choice = rng.choice(["High", "Medium", "Low"], p=[0.60, 0.30, 0.10])
                else:
                    q_choice = rng.choice(["High", "Medium", "Low"], p=[0.38, 0.42, 0.20])
        ai_response_quality[i] = q_choice
        
    # 12. Containment Logic
    # Containment priors:
    # Low: V1 78%, V2 90%
    # Med: V1 68%, V2 76%
    # High: V1 48%, V2 56%
    cont_probs = np.zeros(total_conversations)
    cont_probs[(ai_version == "V1") & (complexities == "Low")] = 0.78
    cont_probs[(ai_version == "V1") & (complexities == "Medium")] = 0.68
    cont_probs[(ai_version == "V1") & (complexities == "High")] = 0.48
    
    cont_probs[(ai_version == "V2") & (complexities == "Low")] = 0.90
    cont_probs[(ai_version == "V2") & (complexities == "Medium")] = 0.76
    cont_probs[(ai_version == "V2") & (complexities == "High")] = 0.56
    
    # Quality modulation on containment
    cont_probs[ai_response_quality == "Low"] -= 0.15
    cont_probs[ai_response_quality == "High"] += 0.05
    cont_probs = np.clip(cont_probs, 0.15, 0.96)
    
    ai_contained = np.zeros(total_conversations, dtype=bool)
    ai_contained[ai_used] = rng.random(np.sum(ai_used)) < cont_probs[ai_used]
    
    # 13. Human Escalation (Mutually exclusive with containment for AI interactions)
    human_escalated = np.zeros(total_conversations, dtype=bool)
    # Non-AI routed interactions are directly handled by humans
    human_escalated[~ai_used] = True
    # AI interactions not contained escalate to human
    human_escalated[ai_used & ~ai_contained] = True
    
    # 14. Resolution Logic & Types
    # If contained: Can be AI_Resolved, Unresolved_Contained (false containment), or Abandoned
    # SARR resolution probability among contained:
    # Low: V1 ~92% -> SARR ~72%; V2 ~92% -> SARR ~83%
    # Med: V1 ~85% -> SARR ~58%; V2 ~86% -> SARR ~65%
    # High: V1 ~71% -> SARR ~34%; V2 ~63% -> SARR ~35% (Notice high complexity V2 has lower resolution among contained!)
    res_status = np.full(total_conversations, "Unresolved", dtype=object)
    res_type = np.full(total_conversations, "Unresolved_Escalated", dtype=object)
    
    for i in range(total_conversations):
        if not ai_used[i]:
            # Direct human handled: 92% resolved, 8% unresolved
            if rng.random() < 0.92:
                res_status[i] = "Resolved"
                res_type[i] = "Human_Resolved"
            else:
                res_status[i] = "Unresolved"
                res_type[i] = "Unresolved_Escalated"
        else:
            if ai_contained[i]:
                ver = ai_version[i]
                comp = complexities[i]
                err = ai_error_flag[i]
                qual = ai_response_quality[i]
                
                # Base resolution probability for contained
                if comp == "Low":
                    p_res = 0.93 if ver == "V2" else 0.92
                elif comp == "Medium":
                    p_res = 0.86 if ver == "V2" else 0.85
                else:  # High
                    p_res = 0.63 if ver == "V2" else 0.71  # Over-containment dynamic
                    
                if err:
                    p_res -= 0.40
                if qual == "Low":
                    p_res -= 0.25
                elif qual == "High":
                    p_res += 0.05
                p_res = np.clip(p_res, 0.10, 0.98)
                
                if rng.random() < p_res:
                    res_status[i] = "Resolved"
                    res_type[i] = "AI_Resolved"
                else:
                    # 70% unres contained, 30% abandoned
                    if rng.random() < 0.70:
                        res_status[i] = "Unresolved"
                        res_type[i] = "Unresolved_Contained"
                    else:
                        res_status[i] = "Abandoned"
                        res_type[i] = "Abandoned"
            else:
                # Escalated to human: 91% resolved by human
                if rng.random() < 0.91:
                    res_status[i] = "Resolved"
                    res_type[i] = "Human_Resolved"
                else:
                    res_status[i] = "Unresolved"
                    res_type[i] = "Unresolved_Escalated"
                    
    # 15. Repeat Contact 7-Day Logic
    # Repeat rate depends on resolution status, errors, and complexity
    repeat_probs = np.zeros(total_conversations)
    for i in range(total_conversations):
        if res_status[i] == "Resolved":
            p_rep = 0.05 if complexities[i] == "Low" else (0.08 if complexities[i] == "Medium" else 0.14)
        else:
            p_rep = 0.38 if complexities[i] == "Low" else (0.45 if complexities[i] == "Medium" else 0.55)
            
        if ai_error_flag[i]:
            p_rep += 0.25
        if res_type[i] == "Unresolved_Contained":
            p_rep += 0.10
        repeat_probs[i] = np.clip(p_rep, 0.02, 0.85)
        
    repeat_contact_7d = rng.random(total_conversations) < repeat_probs
    
    # 16. CSAT Score Generation (1 to 5, ~40% response rate)
    csat_score = np.full(total_conversations, np.nan)
    survey_responded = rng.random(total_conversations) < config.CSAT_SURVEY_RESPONSE_RATE
    
    for i in np.where(survey_responded)[0]:
        # Latent satisfaction score
        latent = 3.6
        if res_status[i] == "Resolved":
            latent += 1.1
        else:
            latent -= 1.4
            
        if ai_response_quality[i] == "High":
            latent += 0.4
        elif ai_response_quality[i] == "Low":
            latent -= 0.6
            
        if ai_error_flag[i]:
            latent -= 1.3
        if repeat_contact_7d[i]:
            latent -= 0.8
        if human_escalated[i]:
            latent += 0.1  # Creators appreciate human transfer when needed
            
        # Add random noise
        latent += rng.normal(0, 0.45)
        
        # Cutpoints to map to 1-5
        if latent < 1.8:
            score = 1
        elif latent < 2.6:
            score = 2
        elif latent < 3.4:
            score = 3
        elif latent < 4.2:
            score = 4
        else:
            score = 5
        csat_score[i] = score
        
    # 17. Human Handling Time & Total Conversation Duration
    human_handling_time_min = np.zeros(total_conversations)
    for i in np.where(human_escalated)[0]:
        comp = complexities[i]
        hp = config.HUMAN_HANDLING_PARAMS[comp]
        hht = rng.gamma(shape=hp["shape"], scale=hp["scale"])
        human_handling_time_min[i] = np.round(np.clip(hht, 1.0, 90.0), 2)
        
    # Total conversation duration (AI time + Human handling time + waiting)
    conv_duration_min = np.zeros(total_conversations)
    for i in range(total_conversations):
        ai_sec = ai_response_time_sec[i] if not np.isnan(ai_response_time_sec[i]) else 0.0
        h_min = human_handling_time_min[i]
        base_dur = (ai_sec / 60.0) + h_min + rng.uniform(0.5, 3.0)
        conv_duration_min[i] = np.round(np.clip(base_dur, 0.5, 120.0), 2)
        
    # Assemble fact dataframe
    df_fact = pd.DataFrame({
        "conversation_id": conversation_ids,
        "creator_id": creator_ids,
        "conversation_date": conversation_dates,
        "ai_version": ai_version,
        "issue_type": issue_types,
        "issue_complexity": complexities,
        "region": creator_regions,
        "creator_segment": creator_segments,
        "entry_channel": entry_channels,
        "eligible_for_ai": eligible_for_ai,
        "ai_used": ai_used,
        "experiment_group": experiment_group,
        "ai_response_time_sec": ai_response_time_sec,
        "ai_contained": ai_contained,
        "ai_response_quality": ai_response_quality,
        "ai_error_flag": ai_error_flag,
        "resolution_status": res_status,
        "resolution_type": res_type,
        "human_escalated": human_escalated,
        "human_handling_time_min": human_handling_time_min,
        "csat_score": pd.Series(csat_score, dtype="Int64"),
        "repeat_contact_7d": repeat_contact_7d,
        "conversation_duration_min": conv_duration_min,
    })
    
    return df_fact

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic YouTube creator support dataset.")
    parser.add_argument("--pilot", action="store_true", help="Generate a 5,000-row pilot dataset for pre-flight validation.")
    args = parser.parse_args()
    
    rng = np.random.default_rng(config.RANDOM_SEED)
    
    if args.pilot:
        total_convs = 5_000
        total_creators = 1_500
        output_dir = config.DATA_DIR / "pilot"
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"--> Generating 5,000-row PILOT dataset (Seed: {config.RANDOM_SEED})...")
    else:
        total_convs = config.TOTAL_CONVERSATIONS  # Exactly 120,000
        total_creators = config.TOTAL_CREATORS    # Exactly 25,000
        output_dir = config.RAW_DATA_DIR
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"--> Generating exactly 120,000-row FULL dataset (Seed: {config.RANDOM_SEED})...")
        
    df_date = generate_dim_date(config.START_DATE, config.END_DATE)
    df_issue = generate_dim_issue_type()
    df_version = generate_dim_ai_version()
    df_creator = generate_dim_creator(total_creators, rng)
    df_fact = generate_fact_conversations(total_convs, df_creator, df_date, rng)
    
    # Save CSVs
    df_fact.to_csv(output_dir / "fact_conversations.csv", index=False)
    df_creator.to_csv(output_dir / "dim_creator.csv", index=False)
    df_issue.to_csv(output_dir / "dim_issue_type.csv", index=False)
    df_version.to_csv(output_dir / "dim_ai_version.csv", index=False)
    df_date.to_csv(output_dir / "dim_date.csv", index=False)
    
    print(f"[OK] Generated {len(df_fact):,} conversations and {len(df_creator):,} creators.")
    print(f"[OK] Saved all 5 tables to {output_dir}")

if __name__ == "__main__":
    main()
