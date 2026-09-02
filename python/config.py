"""
Configuration and Simulation Parameters for YouTube Creator Support AI Agent Analytics.

Independent simulated case study using synthetic data.
"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DOCS_DIR = BASE_DIR / "docs"
SQL_DIR = BASE_DIR / "sql"
PYTHON_DIR = BASE_DIR / "python"
VISUALS_DIR = BASE_DIR / "visuals"
CASE_STUDY_DIR = BASE_DIR / "case-study"
DASHBOARD_DIR = BASE_DIR / "dashboard" / "powerbi"

# Ensure directories exist
for p in [RAW_DATA_DIR, PROCESSED_DATA_DIR, VISUALS_DIR, DASHBOARD_DIR, CASE_STUDY_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# Random Seed for 100% Reproducibility
RANDOM_SEED = 42

# Dataset Scale
TOTAL_CONVERSATIONS = 120_000
TOTAL_CREATORS = 25_000
START_DATE = "2026-01-01"
END_DATE = "2026-08-31"

# Lifecycle Phases
EXPERIMENT_START = "2026-05-01"
EXPERIMENT_END = "2026-06-30"

# Issue Type Distribution (sums to 1.0)
ISSUE_TYPE_DISTRIBUTION = {
    "Monetization": 0.18,
    "Copyright": 0.14,
    "Revenue & Payments": 0.12,
    "Creator Tools": 0.12,
    "Policy": 0.10,
    "Channel Access": 0.08,
    "Memberships": 0.08,
    "Analytics": 0.07,
    "Shorts": 0.06,
    "Other": 0.05,
}

# Issue Categories
ISSUE_CATEGORIES = {
    "Monetization": "Monetization & Rights",
    "Copyright": "Monetization & Rights",
    "Revenue & Payments": "Monetization & Rights",
    "Memberships": "Monetization & Rights",
    "Creator Tools": "Channel & Tools",
    "Channel Access": "Channel & Tools",
    "Analytics": "Channel & Tools",
    "Policy": "Policy & Safety",
    "Shorts": "Content & Discovery",
    "Other": "Content & Discovery",
}

# Complexity Conditional Priors per Issue Type [Low, Medium, High]
ISSUE_COMPLEXITY_PRIORS = {
    "Creator Tools": [0.65, 0.30, 0.05],
    "Analytics": [0.60, 0.32, 0.08],
    "Shorts": [0.55, 0.35, 0.10],
    "Memberships": [0.45, 0.40, 0.15],
    "Other": [0.45, 0.40, 0.15],
    "Monetization": [0.35, 0.45, 0.20],
    "Revenue & Payments": [0.30, 0.50, 0.20],
    "Channel Access": [0.20, 0.45, 0.35],
    "Copyright": [0.15, 0.45, 0.40],
    "Policy": [0.15, 0.45, 0.40],
}

# Region Mix (sums to 1.0)
REGION_DISTRIBUTION = {
    "US": 0.30,
    "India": 0.20,
    "Southeast Asia": 0.12,
    "UK": 0.10,
    "Canada": 0.08,
    "Other": 0.20,
}

# Creator Segment Distribution (sums to 1.0)
CREATOR_SEGMENT_DISTRIBUTION = {
    "Emerging": 0.45,       # < 10K
    "Growth": 0.32,         # 10K - 100K
    "Established": 0.18,    # 100K - 1M
    "Large": 0.05,          # > 1M
}

# AI Adoption Propensities by Segment
AI_ADOPTION_BY_SEGMENT = {
    "Emerging": 0.80,
    "Growth": 0.77,
    "Established": 0.72,
    "Large": 0.68,
}

# Overall Baseline AI Eligibility Rate
BASE_AI_ELIGIBILITY_RATE = 0.85

# Entry Channels
ENTRY_CHANNELS = {
    "Creator_Studio": 0.55,
    "Help_Center": 0.25,
    "Mobile_App": 0.15,
    "Email_Form": 0.05,
}

# AI Agent Baseline Latency Parameters (LogNormal mu, sigma)
LATENCY_PARAMS = {
    "V1": {"mu": 1.35, "sigma": 0.45},  # Median ~3.85s, P90 ~8.9s
    "V2": {"mu": 0.88, "sigma": 0.38},  # Median ~2.41s, P90 ~5.7s
}

# Human Handling Time Parameters (Gamma shape k, scale theta in minutes)
HUMAN_HANDLING_PARAMS = {
    "Low": {"shape": 5.0, "scale": 1.5},     # Mean ~7.5 min
    "Medium": {"shape": 6.0, "scale": 2.5},  # Mean ~15.0 min
    "High": {"shape": 7.0, "scale": 4.0},    # Mean ~28.0 min
}

# Operational Economics Assumptions
COST_PER_HUMAN_MINUTE = 0.75  # $45/hour
COST_PER_AI_INTERACTION = 0.05  # $0.05 compute/inference
CSAT_SURVEY_RESPONSE_RATE = 0.40  # 40% response rate
