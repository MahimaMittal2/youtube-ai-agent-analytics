# AI Agent Performance & Optimization in Creator Support

### Independent analytics case study using synthetic data

> [!IMPORTANT]
> **Synthetic Data & Independence Disclosure**: This is an independent portfolio project using synthetic data. It does not use or represent Google/YouTube internal data, systems, metrics, methodologies, or confidential information.

---

## The Business Problem

Customer support organizations increasingly deploy AI agents to handle incoming user volume. On the surface, these AI systems often look highly effective because they achieve high "containment"—meaning the conversation never reaches a human support agent.

However, containment alone does not answer the fundamental question:

> **"Did the creator actually get their problem solved?"**

When an AI agent prematurely closes a conversation without resolving the underlying issue, or provides inaccurate guidance, the user experiences frustration and inevitably returns to support. This case study evaluates whether upgrading an AI agent truly improves resolution and customer experience, or simply pushes failure demand further downstream.

---

## What I Measured

To evaluate true resolution rather than superficial deflection, this project established a primary North-Star metric:

### **Successful AI Resolution Rate (SARR)**

In plain English, a conversation counts as a **successful resolution** only when all four conditions are met:
1. The AI agent handles the conversation.
2. The conversation is contained without needing human escalation.
3. The creator's underlying issue is marked resolved.
4. The creator does not contact support again about the same issue within 7 days.

In addition to SARR, the measurement framework tracked:
- **Creator Satisfaction (CSAT)**: Post-interaction sentiment and rating distributions.
- **7-Day Repeat Contact Rate**: Measuring downstream failure demand.
- **AI Error Rate**: Factual inaccuracies, policy misinterpretations, and hallucinations.
- **Human Escalation Rate**: Cases routed to specialist support teams.
- **Response Time & Latency**: System turnaround speed.

---

## What I Did

The project followed four core analytical steps:

1. **Controlled Experimentation**: Compared AI Agent V1 (baseline) against AI Agent V2 (upgraded) using a simulated 60-day randomized controlled trial ($N = 19,404$ conversations).
2. **Subgroup Segmentation**: Evaluated how performance varied across low-, medium-, and high-complexity creator workflows.
3. **AI Quality & Behavioral Analysis**: Examined how AI errors and hallucinations correlated with creator sentiment and repeat contact demand.
4. **Capacity & Scenario Modeling**: Modeled the downstream impact on human support queue volume, monthly labor hours, and operational trade-offs across different containment thresholds.

---

## What I Found

AI Agent V2 demonstrated significant overall improvements over V1 across core resolution and quality metrics:

| Metric | Baseline (V1) | Treatment (V2) | Impact |
| :--- | :---: | :---: | :---: |
| **Successful AI Resolution (SARR)** | **54.26%** | **64.11%** | **+9.85 percentage points** (+18.16% rel, $p < 10^{-40}$) |
| **Headline Containment Rate** | 68.37% | 79.12% | +10.75 percentage points |
| **Human Escalation Rate** | 31.63% | 20.88% | -10.75 percentage points (-33.99% rel) |
| **AI Error Rate** | 4.38% | 3.06% | -1.32 percentage points (-30.20% rel) |
| **Low-Complexity SARR** | 71.0% | 86.6% | **+15.63 percentage points** |
| **Medium-Complexity SARR** | 54.6% | 62.8% | **+8.25 percentage points** |
| **High-Complexity SARR** | 26.1% | 29.3% | **+3.16 percentage points** |

### The Core Analytical Insight

While AI Agent V2 performed strongly overall, the gains were highly uneven across issue types:

- **Low- and medium-complexity workflows accounted for approximately 94% of the incremental SARR gain observed in the simulated experiment.**
- **High-complexity workflows** (such as policy strikes, monetization disputes, and copyright claims) showed much weaker resolution gains (+3.16 pp) and suffered from an expanded **false-containment gap** (widening from 20.2 pp in V1 to 26.2 pp in V2).

---

## Why AI Quality Matters

An AI system should never be evaluated solely on volume deflection. In the simulated analysis:

- **AI factual and policy errors were associated with 4.5× higher repeat-contact odds** within 7 days, creating substantial downstream rework for human agents.
- **Creator satisfaction collapsed** when AI errors occurred, with mean CSAT declining by -56.0% (from 4.52 stars down to 1.99 stars).
- **High-complexity inquiries** produced the largest wedge between reported containment and true resolution, proving that aggressive deflection in nuanced topics directly damages user trust.

---

## The Operational Trade-off

Pushing AI containment targets higher is not automatically beneficial for operations.

In the sensitivity scenario analysis:
- Increasing containment targets from 60% up to 80% steadily reduced human queue volume.
- However, pushing containment targets beyond **~80%** triggered a **+55.1% surge in repeat failure demand**.
- This influx of returning creators reversed previous labor savings, increasing total modeled human support hours from **2,071 to 2,111 hours per month**.

*(Note: These figures represent illustrative scenario modeling based on synthetic parameters, not observed YouTube internal financials).*

---

## Recommendation

### **Selective Rollout (Option B)**

Rather than a blanket 100% rollout, the data strongly supports a tiered operational strategy:

1. **Broad Deployment for Low & Medium Complexity**: Deploy AI Agent V2 widely across standard inquiries (creator tools, channel settings, standard analytics, memberships) where resolution rates are high and error risks are minimal.
2. **Early Human Routing for High Complexity**: Implement early triage on complex policy, copyright, and revenue disputes, routing them directly to specialized human specialists to avoid false-containment failure loops.
3. **Balanced Governance**: Replace isolated containment targets with SARR and Quality-Adjusted Containment (QAC) launch gates across all AI product scorecards.

---

## Why It Matters

This project demonstrates a disciplined, end-to-end framework for evaluating AI applications in real-world business environments:

- **Defining Business-Aligned Metrics**: Moving beyond superficial vanity numbers to measure true customer outcomes.
- **Causal Experimentation**: Using randomized A/B testing to separate genuine product improvements from random noise.
- **Subgroup Diagnostics**: Identifying where AI excels and where it fails to optimize deployment strategies.
- **Capacity & Financial Translation**: Bridging technical model metrics to operational queue dynamics, labor capacity, and business decision-making.

---

## Explore the Full Project

- **[Recruiter Case Study](recruiter_case_study.md)**: 5-minute executive summary and visual story.
- **[Full Technical Case Study](case_study.md)**: Comprehensive deep dive including data architecture, SQL queries, Python modeling, and statistical outputs.
- **[GitHub Repository](https://github.com/MahimaMittal2/youtube-ai-agent-analytics)**: Complete open-source codebase, SQL scripts, and reproducible data pipeline.
- **[Live Portfolio Website](https://mahimamittal2.github.io/youtube-ai-agent-analytics/)**: Interactive web portfolio and case study presentation.
