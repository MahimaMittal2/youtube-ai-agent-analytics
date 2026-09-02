# Optimizing AI Agent Performance in Creator Support: A Data-Driven Decision Framework

**Author**: Mahima Mittal — Independent Analytics Case Study  
**Audience**: Hypothetical Creator Support Leadership  
**Context**: This independent case study models a hypothetical YouTube creator-support environment using synthetic data.

> [!IMPORTANT]
> **Synthetic Data & Independence Disclosure**: This project is an independent analytics portfolio study based on a simulated creator support environment (120,000 synthetic conversation records). It does not use or represent internal Google or YouTube data, metrics, systems, methodologies, or confidential roadmaps.

---

## 1. Business Problem

In high-volume creator platforms, support operations must balance rapid automated assistance with high-touch issue resolution. When creators reach out regarding monetization holds, copyright counter-notifications, channel access recovery, or creator tools, resolution delays directly impact creator sentiment, platform trust, and downstream operational workload.

To scale support efficiently, conversational AI agents handle incoming inquiries. As operations leadership evaluates whether to deploy **AI Agent V2** to replace **Baseline V1**, executive stakeholders face four strategic choices:

1. **Option A (Scale Broadly)**: Deploy V2 universally across 100% of creator support traffic.
2. **Option B (Scale Selectively)**: Deploy V2 across specific issue categories and complexity tiers while routing high-friction workflows directly to human specialists.
3. **Option C (Improve Before Rollout)**: Pause release until high-complexity reasoning and policy accuracy reach higher resolution thresholds.
4. **Option D (Rollback)**: Maintain Baseline V1 across the entire support operation.

The core analytical objective is to determine whether AI Agent V2 delivers genuine problem resolution that benefits both creators and support operations, or whether headline efficiency metrics mask underlying operational friction.

---

## 2. Measurement Framework

Traditional contact center analytics often over-index on **AI Containment Rate** (the proportion of conversations closed without a live human transfer) as the primary metric of automation success. However, high containment can create an optical illusion of efficiency: an AI agent can achieve high containment by offering generic guidance that causes creators to abandon sessions in frustration without resolving their root problem.

To resolve this measurement blind spot, we establish the **Successful AI Resolution Rate (SARR)** as the primary North-Star metric, defined strictly among creators who engage with the AI agent:

$$\text{SARR} = \frac{\text{AI Used} \land \text{AI Contained} \land \text{Resolved} \land \neg\text{Repeat Contact in 7 Days}}{\text{AI Used Conversations}}$$

The operational gap between headline containment and true durable resolution is defined as the **False Containment Wedge**:

$$\text{False Containment Wedge (pp)} = \text{AI Containment Rate} - \text{SARR}$$

When this wedge expands, it indicates that creators are being contained without resolution, generating silent friction and downstream failure demand.

![Figure 2: False Containment Wedge across Issue Types](file:///c:/Users/mahim/Desktop/Google%20project/youtube-ai-agent-analytics/visuals/fig2_containment_vs_sarr_wedge.png)
*Figure 1 (fig2): The False Containment Wedge across issue types. While headline containment remains elevated across all categories, true SARR resolution reveals substantial friction in complex domains like Copyright and Channel Access.*

---

## 3. What the Experiment Found

To evaluate AI Agent V2 without selection bias, a 60-day randomized controlled trial was conducted ($N = 19,404$ active AI conversations, split 50/50 into Control V1 and Treatment V2). Randomization was stratified across issue types, complexity tiers, creator tiers, and regions, achieving near-perfect covariate balance (all Standardized Mean Differences $\le 0.0038$).

### Controlled Experiment Scorecard (May 1 – June 30, 2026)

| Metric | Control (V1) | Treatment (V2) | Absolute Lift (95% CI) | Relative Lift | Statistical Significance |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **SARR (North Star)** | **54.26%** | **64.11%** | **+9.85 pp [+8.48, +11.23]** | **+18.16%** | **$p < 10^{-40}$ (Stat. Sig. \*\*\*)** |
| **AI Containment Rate** | 68.37% | 79.12% | +10.75 pp [+9.52, +11.98] | +15.73% | $p < 10^{-40}$ (Stat. Sig. \*\*\*) |
| **Human Escalation Rate** | 31.63% | 20.88% | -10.75 pp [-11.98, -9.52] | -33.99% | $p < 10^{-40}$ (Stat. Sig. \*\*\*) |
| **AI Error Rate (Guardrail)** | 4.38% | 3.06% | -1.32 pp [-1.86, -0.79] | -30.20% | $p = 1.11 \times 10^{-6}$ (Stat. Sig. \*\*\*) |
| **Positive CSAT (Top-2 Box)**| 84.86% | 85.80% | +0.95 pp [-0.63, +2.52] | +1.12% | $p = 0.2381$ (Directional gain) |
| **7-Day Repeat Contact Rate** | 14.86% | 14.35% | -0.51 pp [-1.51, +0.48] | -3.45% | $p = 0.3118$ (Directional gain) |
| **Median Response Latency** | 3.89 sec | 2.39 sec | -1.50 sec | -38.56% | Nonparametric Bootstrap |
| **P90 Response Latency** | 6.90 sec | 3.92 sec | -2.98 sec | -43.19% | $p < 10^{-300}$ (Stat. Sig. \*\*\*) |

The headline results demonstrate that AI Agent V2 significantly outperforms V1 on core resolution metrics: SARR increased by **$+9.85\text{ pp}$** ($18.16\%$ relative improvement), AI error rates dropped by **$30.20\%$**, and response latencies decreased substantially.

![Figure 5: A/B Experiment Headline Lift & Scorecard](file:///c:/Users/mahim/Desktop/Google%20project/youtube-ai-agent-analytics/visuals/fig5_ab_experiment_comparison.png)
*Figure 2 (fig5): Randomized A/B experiment evaluation. AI Agent V2 delivers statistically significant uplifts in SARR across major issue categories while reducing response latency and hallucination rates.*

---

## 4. Where V2 Worked / Struggled

Evaluating Heterogeneous Treatment Effects (HTE) across complexity tiers reveals crucial operational divergence:

```
+---------------------------------------------------------------------------------------------------------+
| Complexity Tier | Vol Share | V1 SARR | V2 SARR | SARR Lift (pp) | V1 Cont | V2 Cont | False Containment Gap|
+-----------------+-----------+---------+---------+----------------+---------+---------+----------------------+
| Low Complexity  | 40.2%     | 71.0%   | 86.6%   | +15.63 pp ***  | 80.7%   | 94.2%   | 9.7 pp -> 7.6 pp (-2.1 pp)
| Medium Complex. | 39.8%     | 54.6%   | 62.8%   |  +8.25 pp ***  | 69.3%   | 78.4%   | 14.7 pp -> 15.6 pp (+0.8 pp)
| High Complexity | 20.0%     | 26.1%   | 29.3%   |  +3.16 pp *    | 46.3%   | 55.5%   | 20.2 pp -> 26.2 pp (+6.1 pp)
+---------------------------------------------------------------------------------------------------------+
```

### 1. Low Complexity: High Efficiency & True Resolution
In straightforward inquiries (Creator Tools, basic Analytics, Shorts publishing), V2 performs strongly. SARR surged by **$+15.63\text{ pp}$** ($71.0\% \rightarrow 86.6\%$), and the false containment wedge contracted from $9.7\text{ pp}$ to $7.6\text{ pp}$. The agent successfully resolves queries on the first turn without generating repeat contacts.

### 2. Medium Complexity: Dependable Performance Lift
In standard inquiries (Memberships, Monetization setup, standard Payments), V2 achieved a solid **$+8.25\text{ pp}$** SARR lift ($54.6\% \rightarrow 62.8\%$) while maintaining a stable false containment gap.

### 3. High Complexity: The Over-Containment Trap
In complex, policy-intensive workflows (Copyright disputes, Policy strike appeals, Channel Access restoration), V2 exhibited a notable divergence:
- Containment surged by **$+9.22\text{ pp}$** ($46.3\% \rightarrow 55.5\%$).
- SARR only gained **$+3.16\text{ pp}$** ($26.1\% \rightarrow 29.3\%$).
- The false containment wedge **expanded by $+6.1\text{ pp}$ to $26.2\text{ pp}$**.

In high-complexity scenarios, V2 aggressively deflected inquiries without genuinely solving the creator's underlying problem, locking creators into unproductive conversational loops.

![Figure 3: Complexity Interactions with SARR and Containment](file:///c:/Users/mahim/Desktop/Google%20project/youtube-ai-agent-analytics/visuals/fig3_complexity_interaction.png)
*Figure 3 (fig3): Complexity interaction curves. As query complexity increases, SARR drops sharply and the wedge gap between containment and resolution expands, highlighting severe over-containment in high-complexity workflows.*

---

## 5. Why AI Quality Matters

To quantify the downstream consequences of AI errors and unassisted closures, we modeled creator sentiment and 7-day repeat contact behavior using multivariate logistic regression.

To prevent target leakage, the regression predictors were constructed independently of the downstream outcome (`repeat_contact_7d`):
- **`is_resolved`**: Immediate resolution status recorded during the primary interaction.
- **`is_false_contained`**: Defined independently as $\mathbf{1}\big(\text{ai\_contained} = \text{True} \land (\text{resolution\_status} = \text{'Unresolved'} \lor \text{ai\_error\_flag} = \text{True})\big)$.

### Multivariate Regression: Drivers of 7-Day Repeat Contact Failure Demand

| Predictor | Odds Ratio (OR) | 95% Confidence Interval | $p$-value | Operational Takeaway |
| :--- | :---: | :---: | :---: | :--- |
| **True Problem Resolution** (`is_resolved`) | **$0.112$** | $[0.105, 0.120]$ | $< 10^{-300}$ | Resolving the root problem reduces repeat contact odds by **$88.8\%$**. |
| **AI Error / Hallucination** (`is_error`) | **$4.455$** | $[4.072, 4.875]$ | $1.19 \times 10^{-232}$ | Errors multiply repeat failure demand odds by **$4.46\times$**. |
| **False Containment** (`is_false_contained`) | **$1.477$** | $[1.362, 1.602]$ | $5.31 \times 10^{-21}$ | Premature deflection elevates repeat contact odds by **$47.7\%$**. |
| **High Complexity Query** | **$2.716$** | $[2.553, 2.891]$ | $1.76 \times 10^{-217}$ | High complexity elevates repeat contact odds by **$2.72\times$**. |

### Empirical Impact on Creator Sentiment
When an AI agent commits a factual or policy error:
- **Mean CSAT collapses** from **$4.52$ to $1.99$ stars** (a $-56.0\%$ reduction).
- **Positive CSAT drops** from **$86.8\%$ to $18.2\%$** (a $-68.6\text{ pp}$ drop).
- **7-Day Repeat Contact Rate spikes** from **$12.9\%$ to $54.9\%$** ($4.26\times$ baseline).

AI errors directly erode creator trust and immediately rebound into support queues as expensive, escalated repeat conversations.

![Figure 4: Impact of AI Errors on Creator CSAT and Repeat Contacts](file:///c:/Users/mahim/Desktop/Google%20project/youtube-ai-agent-analytics/visuals/fig4_ai_error_csat_impact.png)
*Figure 4 (fig4): The penalty of AI errors. Committing factual or policy errors causes an immediate collapse in CSAT and drives a 4.26x surge in 7-day repeat contact failure demand.*

---

## 6. Operational Trade-off

To understand how containment targets impact overall workforce capacity, we modeled a closed-loop operational demand forecast spanning 15,000 monthly inbound conversations ($\approx 180,000$ annually).

### Containment Sensitivity Sweep (60%, 70%, 80%, 85%)

| Target Containment | SARR % | Quality-Adjusted Containment (QAC) | Monthly True Resolved | Monthly False Contained | Monthly Repeat Demand | Total Human Queue / Mo | Monthly Human Labor Hours |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **60%** | **51.9%** | **50.4%** | 5,278 | 459 | 500 | 9,763 | **2,376 hrs** |
| **70%** | **57.9%** | **55.0%** | 5,890 | 803 | 715 | 9,021 | **2,195 hrs** |
| **80%** | **60.2%** | **54.3%** | 6,120 | 1,530 | 1,163 | 8,513 | **2,071 hrs** |
| **85%** | **55.9%** | **46.3%** | 5,690 | 2,438 (+59%) | 1,804 (+55%) | 8,676 | **2,111 hrs** |

*\*Note: Labor hours and costs are illustrative modeled outputs under the simulation's standard $45.00/hour loaded labor assumption and 15,000 monthly volume, not observed internal YouTube financial figures.*

### The Diminishing Returns Inflection Point
- Moving containment from **$60\% \rightarrow 80\%$** produces genuine productivity gains, reducing human labor requirements from $2,376$ to $2,071\text{ hrs/month}$.
- Pushing containment from **$80\% \rightarrow 85\%$** creates adverse and diminishing operational returns: false containment jumps by $+59\%$, triggering a $+55.1\%$ spike in repeat failure demand that **increases total human support hours** from $2,071$ to $2,111\text{ hrs/month}$.

Forcing containment beyond the $\approx 80\%$ threshold converts live queues into delayed, high-friction repeat queues, increasing total labor burden while frustrating creators.

![Figure 7: Containment Sensitivity Curves and Operational Trade-offs](file:///c:/Users/mahim/Desktop/Google%20project/youtube-ai-agent-analytics/visuals/fig7_containment_sensitivity_scenarios.png)
*Figure 5 (fig7): Containment sensitivity curves. Pushing containment beyond 80% causes false containment and repeat failure demand to spike, reversing workforce labor savings.*

---

## 7. Recommendation

Based on the empirical findings, we recommend **Selective Rollout (Option B)**.

```
+---------------------------------------------------------------------------------------------------+
| Deployment Strategy       | Containment | SARR  | Monthly Human Queue       | Monthly Hours | Modeled Annual Cost*|
+---------------------------+-------------+-------+---------------------------+---------------+--------------------+
| Baseline (V1 Model)       | 68.0%       | 54.5% | 9,320 conversations       | 2,403 hrs     | $1,297,719         |
| Option A: Broad V2        | 77.6%       | 61.1% | 8,566 conversations       | 2,250 hrs     | $1,214,943         |
| Option B: Selective V2    | 66.4%       | 54.8% | 9,616 conversations       | 2,740 hrs     | $1,479,514         |
+---------------------------------------------------------------------------------------------------+
```
*\*Note: Modeled labor costs represent illustrative simulation projections at $45/hour, not actual YouTube financial records.*

### The Strategic Case for Option B

1. **Deploy V2 Universally for Low and Medium Complexity**:
   Low and Medium complexity issues represent **$80.0\%$** of total creator support volume. Low- and medium-complexity workflows account for approximately 94% of the incremental SARR gain observed in the simulated experiment. Deploying V2 across these categories captures substantial resolution gains while maintaining high creator satisfaction.

2. **Implement Intelligent Early Triage for High Complexity**:
   For complex workflows (Copyright disputes, Policy strike appeals, Channel Access restoration), implement a rapid 1-turn triage agent that verifies creator credentials and immediately routes inquiries directly to specialized human queues. This bypasses the $26.2\text{ pp}$ false containment trap and substantially reduces downstream repeat contacts.

3. **Modernize Support KPI Governance**:
   - **Deprecate raw Containment Rate** as an isolated success metric.
   - Mandate **SARR (Successful AI Resolution Rate)** and **Quality-Adjusted Containment (QAC)** as the primary launch gates for future model iterations.
   - Establish automated anomaly detection for any issue category where the 7-day repeat contact rate exceeds $15\%$.

---

**Tools**: SQL · Python · Power BI  
**Dataset**: 120,000 synthetic conversations  
**Links**: [Dashboard Guide](file:///c:/Users/mahim/Desktop/Google%20project/youtube-ai-agent-analytics/dashboard/powerbi/dashboard_guide.md) · [GitHub Repository](https://github.com/) · [Technical Methodology](file:///c:/Users/mahim/Desktop/Google%20project/youtube-ai-agent-analytics/docs/methodology.md)
