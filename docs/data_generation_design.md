# Synthetic Data Generation Design & Dependency Architecture

> [!IMPORTANT]
> **Synthetic Data Disclosure**: This document specifies the causal probabilistic Directed Acyclic Graph (DAG) and deterministic assignment rules used to generate synthetic support records for this case study.

---

## 1. Causal Probabilistic DAG

The simulation engine generates realistic data by executing a 12-stage conditional dependency graph:

```mermaid
flowchart TD
    D1[1. Creator Generation: Tier, Tenure, Region] --> D2[2. Conversation Date & Timestamp]
    D2 --> D3[3. Issue Type Sampling]
    D3 --> D4[4. Issue Complexity | Issue Type]
    D4 --> D5[5. AI Eligibility & Channel]
    D5 --> D6[6. AI Adoption | Segment & Eligibility]
    D6 --> D7[7. Experiment Group & AI Version]
    D7 --> D8[8. AI Error Flag | Version, Issue, Complexity]
    D7 --> D9[9. AI Response Quality & Latency]
    D8 & D9 --> D10[10. AI Containment & Escalation]
    D10 --> D11[11. Resolution Type & Status]
    D11 --> D12[12. Repeat Contact 7d & CSAT Score]
    D10 & D11 --> D13[13. Human Handling Time & Duration]
```

---

## 2. Mathematical Generation Functions

### Stage 1: Creator Universe (`dim_creator`)
- Sample $N_{\text{creators}} = 25,000$.
- Creator Segment: Emerging (45%), Growth (32%), Established (18%), Large (5%).
- Subscriber Size ($S$): Lognormal distribution parameterized by segment:
  - Emerging: $\text{Lognormal}(\mu=7.5, \sigma=0.8)$ clipped to $[100, 10{,}000)$.
  - Growth: $\text{Lognormal}(\mu=10.2, \sigma=0.5)$ clipped to $[10{,}000, 100{,}000)$.
  - Established: $\text{Lognormal}(\mu=12.2, \sigma=0.6)$ clipped to $[100{,}000, 1{,}000{,}000)$.
  - Large: $\text{Lognormal}(\mu=14.5, \sigma=0.7)$ clipped to $[1{,}000{,}000, 30{,}000{,}000]$.
- Creator Tenure: Uniform integer $[1, 120]$ months.

---

### Stage 2 & 3: Inbound Volume & Issue Sampling
- Inbound conversations per day: Poisson($\lambda \approx 494$) yielding $\approx 120,000$ conversations over 243 days.
- Inbound creator selected via ticket propensity weighted by segment (Emerging creators open slightly more basic tickets, Large creators open fewer but higher-stakes tickets).
- Issue types sampled from categorical distribution matching Section 12 specifications.

---

### Stage 4 & 5: Complexity & AI Eligibility
- Complexity (Low, Med, High) sampled per issue type using the transition matrix in `docs/assumptions.md`.
- Eligibility for AI: Sampled Bernoulli trial conditioned on Issue and Channel:
  $$P(\text{Eligible}) = \text{base}(0.85) + \delta_{\text{segment}} + \delta_{\text{issue}}$$
- Entry channel: Creator Studio (55%), Help Center (25%), Mobile App (15%), Email Form (5%).

---

### Stage 6 & 7: AI Adoption & Experiment Allocation
- If `eligible_for_ai = False` $\rightarrow$ `ai_used = False`, `ai_version = 'None'`, routes directly to human.
- If `eligible_for_ai = True` $\rightarrow$ `ai_used = True` with probability based on creator segment (Emerging 80%, Growth 77%, Established 72%, Large 68%).
- Experiment Group assignment based on `conversation_date`:
  - `Jan 1 – Apr 30`: `Pre_Experiment`, `ai_version = 'V1'`.
  - `May 1 – Jun 30`: Stratified 50/50 assignment $\rightarrow$ `Control_V1` (`ai_version = 'V1'`) vs `Treatment_V2` (`ai_version = 'V2'`).
  - `Jul 1 – Aug 31`: `Post_Experiment`, 80% `ai_version = 'V2'`, 20% `ai_version = 'V1'`.

---

### Stage 8 & 9: AI Error, Quality & Latency
- **AI Error Flag ($E$)**: Bernoulli trial with logit model:
  $$\text{logit}(P(E)) = \beta_0 + \beta_{\text{version}} + \beta_{\text{complexity}} + \beta_{\text{issue}}$$
  - High complexity + Copyright/Policy introduces error spikes.
  - V2 reduces error baseline from ~4.0% to ~2.9%.
- **Response Quality**: Categorical ('High', 'Medium', 'Low') conditioned on error flag and version. If $E = \text{True}$, $P(\text{Low}) = 80\%$.
- **AI Response Latency ($T_{\text{sec}}$)**:
  - V1: LogNormal($\mu=1.35, \sigma=0.45$) $\rightarrow$ Median $\approx 4.0\text{s}$, P90 $\approx 9.0\text{s}$.
  - V2: LogNormal($\mu=0.88, \sigma=0.38$) $\rightarrow$ Median $\approx 2.5\text{s}$, P90 $\approx 5.8\text{s}$.

---

### Stage 10 & 11: Containment & Resolution Logic
- **Containment Probability ($P_C$)**:
  $$P_C = \text{clip}\big(\text{base}(\text{version}, \text{complexity}) + \delta_{\text{issue}} + \delta_{\text{segment}} - 0.25 \cdot E, 0.10, 0.98\big)$$
  - *Key Dynamic*: V2 increases containment across all complexity tiers, but in high complexity it often contains without true resolution.
- **Resolution Classification**:
  - If `ai_contained = True`:
    - With probability $P(\text{True Resolved} \mid C, \text{version}, \text{complexity}, E)$, ticket is tagged `resolution_status = 'Resolved'`, `resolution_type = 'AI_Resolved'`.
    - Remaining contained tickets become `resolution_status = 'Unresolved'`, `resolution_type = 'Unresolved_Contained'` (false containment / deflection) or `'Abandoned'`.
  - If `ai_contained = False` (Escalated to Human):
    - Handled by human specialist $\rightarrow$ 92% `Human_Resolved`, 8% `Unresolved_Escalated`.

---

### Stage 12 & 13: CSAT, Repeat Contacts, and Human Labor
- **Repeat Contact 7d ($R_{7d}$)**:
  - Strongly elevated if unresolved (45%), if AI error occurred (35%), or if high complexity (22%).
  - Low if durably resolved (5–7%).
- **CSAT Score (1–5)**:
  - Latent satisfaction variable:
    $$S = 3.8 + 1.2 \cdot \mathbf{1}_{\text{Resolved}} + 0.5 \cdot \mathbf{1}_{\text{HighQual}} - 1.8 \cdot \mathbf{1}_{\text{Error}} - 1.2 \cdot \mathbf{1}_{R_{7d}} - 0.05 \cdot T_{\text{sec}} + \epsilon$$
  - Mapped to ordered cutpoints $\{1, 2, 3, 4, 5\}$. Survey response sampled at 40% probability (missing completely at random / missing at random).
- **Human Handling Time ($HHT_{\text{min}}$)**:
  - Generated via Gamma distributions parameterized by complexity: Low ($\sim 7.5\text{m}$), Medium ($\sim 15\text{m}$), High ($\sim 28\text{m}$).
