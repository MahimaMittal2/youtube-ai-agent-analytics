# Simulation Assumptions & Modeling Parameters

> [!IMPORTANT]
> **Synthetic Data Disclosure**: All parameters, probability distributions, costs, and operational baselines documented here are synthetic assumptions constructed specifically for this simulation study. They do not represent proprietary YouTube or Google operational metrics.

---

## 1. Volume & Time Distribution

| Phase | Calendar Period | Month Numbers | Share of Total | Approximate Volume | AI Version Mix |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Phase 1: Baseline** | Jan 1, 2026 – Apr 30, 2026 | 1, 2, 3, 4 | 50% | ~60,000 | 100% V1 (Control baseline) |
| **Phase 2: A/B Experiment**| May 1, 2026 – Jun 30, 2026 | 5, 6 | 25% | ~30,000 | 50% V1 Control, 50% V2 Treatment |
| **Phase 3: Post-Experiment**| Jul 1, 2026 – Aug 31, 2026 | 7, 8 | 25% | ~30,000 | 80% V2, 20% V1 (Observational cohort) |

- **Total Conversations**: ~120,000
- **Unique Creators**: ~25,000 (Average ~4.8 conversations/creator across 8 months, modeled via Poisson distribution)

---

## 2. Issue Mix & Complexity Priors

### Issue Type Distribution

```
Monetization:        18%
Copyright:           14%
Revenue & Payments:  12%
Creator Tools:       12%
Policy:              10%
Channel Access:       8%
Memberships:          8%
Analytics:            7%
Shorts:               6%
Other:                5%
Total:              100%
```

### Conditional Complexity Distribution

Complexity is conditioned on issue type to reflect real-world problem domains:

| Issue Type | Low Complexity | Medium Complexity | High Complexity | Weighted Complexity |
| :--- | :---: | :---: | :---: | :--- |
| **Creator Tools** | 65% | 30% | 5% | Low |
| **Analytics** | 60% | 32% | 8% | Low |
| **Shorts** | 55% | 35% | 10% | Low |
| **Memberships** | 45% | 40% | 15% | Medium |
| **Other** | 45% | 40% | 15% | Medium |
| **Monetization** | 35% | 45% | 20% | Medium |
| **Revenue & Payments**| 30% | 50% | 20% | Medium |
| **Channel Access** | 20% | 45% | 35% | High |
| **Copyright** | 15% | 45% | 40% | High |
| **Policy** | 15% | 45% | 40% | High |
| **Portfolio Aggregate** | **~40%** | **~40%** | **~20%** | **Balanced** |

---

## 3. Geographic & Creator Demographic Priors

### Region Distribution
- **US**: 30%
- **India**: 20%
- **Southeast Asia**: 12%
- **UK**: 10%
- **Canada**: 8%
- **Other**: 20%

### Creator Segment & Adoption Matrix

| Creator Segment | Subscriber Range | Share of Creators | AI Eligibility | AI Adoption Rate |
| :--- | :--- | :---: | :---: | :---: |
| **Emerging** | < 10,000 | 45% | 88% | 80% |
| **Growth** | 10,000 – 100,000 | 32% | 85% | 77% |
| **Established** | 100,000 – 1,000,000 | 18% | 82% | 72% |
| **Large** | > 1,000,000 | 5% | 75% | 68% |
| **Overall Weighted** | — | **100%** | **~85%** | **~75%** |

---

## 4. Agent Performance & Heterogeneous Effects

### Baseline Priors (V1 vs V2 Overall)

| Metric | V1 Baseline | V2 Starting Prior | Directional Target |
| :--- | :---: | :---: | :--- |
| **AI Containment** | ~68.0% | ~77.0% | +9.0 pp |
| **SARR (North Star)** | ~58.5% | ~65.0% | +6.5 pp |
| **Positive CSAT** | ~81.0% | ~82.5% | +1.5 pp |
| **Repeat Contact (7d)** | ~13.0% | ~10.8% | -2.2 pp |
| **AI Error Rate** | ~4.0% | ~2.9% | -1.1 pp |
| **Median Response Latency** | 4.0 sec | 2.5 sec | -1.5 sec |
| **P90 Response Latency** | 9.0 sec | 5.8 sec | -3.2 sec |

### Heterogeneous Treatment Effects by Complexity

| Metric / Attribute | Low Complexity | Medium Complexity | High Complexity |
| :--- | :---: | :---: | :---: |
| **V1 Containment** | 78% | 68% | 48% |
| **V2 Containment** | 90% (+12%) | 76% (+8%) | 56% (+8%) |
| **V1 SARR (Resolution)** | 72% | 58% | 34% |
| **V2 SARR (Resolution)** | 83% (+11%) | 65% (+7%) | 35% (+1%) |
| **V1 AI Error Rate** | 2.5% | 4.0% | 7.0% |
| **V2 AI Error Rate** | 1.4% (-1.1%) | 2.7% (-1.3%) | 5.5% (-1.5%) |
| **V1 Repeat Contact** | 8% | 13% | 23% |
| **V2 Repeat Contact** | 5% (-3%) | 10% (-3%) | 21% (-2%) |
| **V1 Positive CSAT** | 87% | 81% | 68% |
| **V2 Positive CSAT** | 92% (+5%) | 83% (+2%) | 67% (-1%) |

> [!NOTE]
> **Heterogeneous Effects Hypothesis**: Simulation priors allow for heterogeneous treatment effects across complexity levels (e.g., varying containment, SARR, and CSAT lifts across Low, Medium, and High complexity), which will be evaluated empirically from the simulated experiment data.

---

## 5. Operational & Economic Assumptions

| Parameter | Value | Justification / Notes |
| :--- | :--- | :--- |
| **Human Agent Fully Loaded Cost** | $45.00 / hour ($0.75 / min) | Standard blended industry rate including tier 1 & 2 specialists. |
| **AI Inference & Infrastructure Cost**| $0.05 / interaction | Blended cost per session for LLM API calls and guardrails. |
| **Survey Response Rate (CSAT)** | 40% | Realistic creator response propensity. |
| **Human Handling Time - Low** | Gamma($\alpha=5, \beta=1.5$) ~ 7.5 min | Quick troubleshooting, password reset verification. |
| **Human Handling Time - Medium** | Gamma($\alpha=6, \beta=2.5$) ~ 15.0 min | Monetization appeals, payment threshold reconciliation. |
| **Human Handling Time - High** | Gamma($\alpha=7, \beta=4.0$) ~ 28.0 min | Copyright counter-notifications, account access restoration. |
