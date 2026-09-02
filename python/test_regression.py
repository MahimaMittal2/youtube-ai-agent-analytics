import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

df = pd.read_csv("c:/Users/mahim/Desktop/Google project/youtube-ai-agent-analytics/data/raw/fact_conversations.csv")
for col in ["eligible_for_ai", "ai_used", "ai_contained", "ai_error_flag", "human_escalated", "repeat_contact_7d"]:
    df[col] = df[col].astype(bool)

ai_df = df[df["ai_used"]].copy()
ai_df["is_repeat"] = ai_df["repeat_contact_7d"].astype(int)
ai_df["is_error"] = ai_df["ai_error_flag"].astype(int)
ai_df["is_resolved"] = (ai_df["resolution_status"] == "Resolved").astype(int)

# Independent definition of premature/false containment without repeat_contact_7d:
ai_df["is_false_contained"] = (ai_df["ai_contained"] & ((ai_df["resolution_status"] == "Unresolved") | (ai_df["ai_error_flag"]))).astype(int)

print("--- Model 1: is_repeat ~ is_resolved + is_error + is_false_contained + C(issue_complexity) ---")
m = smf.logit(
    "is_repeat ~ is_resolved + is_error + is_false_contained + C(issue_complexity, Treatment(reference='Low'))",
    data=ai_df
).fit(disp=False)

or_df = pd.DataFrame({
    "OR": np.exp(m.params),
    "CI_lower": np.exp(m.conf_int()[0]),
    "CI_upper": np.exp(m.conf_int()[1]),
    "p_value": m.pvalues
})
for idx, row in or_df.iterrows():
    print(f"{idx:60s} | OR: {row['OR']:.3f} | 95% CI: [{row['CI_lower']:.3f}, {row['CI_upper']:.3f}] | p: {row['p_value']:.4e}")

