# Metric Definitions & Measurement Framework

> [!IMPORTANT]
> **Synthetic Data Disclosure**: This measurement framework is developed for an independent analytics portfolio case study. It does not represent internal Google or YouTube performance metrics or proprietary algorithms.

---

## 1. North-Star Metric

### Successful AI Resolution Rate (SARR)

$$\text{SARR} = \frac{\sum \mathbf{1}\Big(\text{ai\_used} = \text{True} \land \text{ai\_contained} = \text{True} \land \text{resolution\_type} = \text{'AI\_Resolved'} \land \neg\text{repeat\_contact\_7d}\Big)}{\sum \mathbf{1}\Big(\text{ai\_used} = \text{True}\Big)}$$

- **Business Purpose**: Measures the true resolution performance of active AI conversations from initial containment through to durable problem resolution without human escalation or repeat contact within 7 days.
- **Explicit Metric Separation**:
  - **AI Adoption Rate**: Evaluates the routing/entry funnel ($\text{AI Used} / \text{AI Eligible}$).
  - **AI Containment Rate**: Evaluates in-session deflection ($\text{Contained} / \text{AI Used}$).
  - **SARR (North Star)**: Evaluates durable, friction-free problem resolution ($\text{Successful AI Resolutions} / \text{AI Used}$).

---

## 2. Core Operational & Product KPIs

### 1. AI Adoption Rate

$$\text{AI Adoption Rate} = \frac{\sum \mathbf{1}(\text{ai\_used} = \text{True})}{\sum \mathbf{1}(\text{eligible\_for\_ai} = \text{True})}$$

- **Denominator**: Total support conversations meeting AI routing eligibility criteria.
- **Numerator**: Conversations where the creator actively engaged with the AI agent.

---

### 2. AI Containment Rate

$$\text{AI Containment Rate} = \frac{\sum \mathbf{1}(\text{ai\_used} = \text{True} \land \text{ai\_contained} = \text{True})}{\sum \mathbf{1}(\text{ai\_used} = \text{True})}$$

- **Business Purpose**: Measures the proportion of AI interactions that conclude without an escalation to a human specialist during the active session.
- **Analytical Caution**: High containment does **not** equal resolution. Contained conversations include `AI_Resolved`, `Unresolved_Contained` (deflection/abandonment), and sessions with undetected hallucinations.

---

### 3. Resolution Rate (Raw AI Resolution)

$$\text{AI Resolution Rate} = \frac{\sum \mathbf{1}(\text{ai\_used} = \text{True} \land \text{resolution\_status} = \text{'Resolved'})}{\sum \mathbf{1}(\text{ai\_used} = \text{True})}$$

- **Business Purpose**: Tracks self-reported or system-tagged resolution status regardless of whether a subsequent contact occurs.

---

### 4. Positive CSAT Rate (Top-2 Box CSAT)

$$\text{Positive CSAT Rate} = \frac{\sum \mathbf{1}(\text{csat\_score} \in \{4, 5\})}{\sum \mathbf{1}(\text{csat\_score} \text{ is not NULL})}$$

- **Business Purpose**: Tracks user satisfaction among creators who responded to the post-interaction survey (1-5 Likert scale).
- **Secondary Metric**: Mean CSAT = $\frac{\sum \text{csat\_score}}{\sum \mathbf{1}(\text{csat\_score} \text{ is not NULL})}$.

---

### 5. Repeat Contact Rate (7-Day Friction)

$$\text{Repeat Contact Rate (7d)} = \frac{\sum \mathbf{1}(\text{ai\_used} = \text{True} \land \text{repeat\_contact\_7d} = \text{True})}{\sum \mathbf{1}(\text{ai\_used} = \text{True})}$$

- **Business Purpose**: Quantifies unresolved friction. If a creator contacts support again within 7 days, the prior interaction is deemed to have failed in providing a complete resolution.

---

### 6. Human Escalation Rate

$$\text{Human Escalation Rate} = \frac{\sum \mathbf{1}(\text{ai\_used} = \text{True} \land \text{human\_escalated} = \text{True})}{\sum \mathbf{1}(\text{ai\_used} = \text{True})}$$

- **Business Purpose**: Measures the rate at which AI transfers conversations to human support queues. High escalation in high-risk categories (e.g., account takeover, severe policy) may be healthy and desirable.

---

### 7. AI Error / Hallucination Rate

$$\text{AI Error Rate} = \frac{\sum \mathbf{1}(\text{ai\_used} = \text{True} \land \text{ai\_error\_flag} = \text{True})}{\sum \mathbf{1}(\text{ai\_used} = \text{True})}$$

- **Business Purpose**: Measures the proportion of AI interactions containing materially incorrect guidance, broken policy references, or hallucinations.

---

### 8. Efficiency & Latency Metrics

- **Median AI Response Time ($T_{50}$)**: Median time (seconds) to first AI response.
- **P90 AI Response Time ($T_{90}$)**: 90th percentile latency (seconds).
- **Human Handling Time ($HHT$)**: Active agent minutes spent on escalated tickets.
- **Total Human Support Hours**: $\frac{\sum \text{human\_handling\_time\_min}}{60}$.

---

## 3. Proposed Analytical Frameworks

### Framework A: Quality-Adjusted Containment (QAC)

$$\text{QAC} = \text{AI Containment Rate} \times \text{Resolution Rate among Contained Conversations} \times (1 - \text{Repeat Contact Rate among Contained})$$

- **Conceptual Formula**:
  $$\text{QAC} = \frac{\sum \mathbf{1}(\text{ai\_used} = \text{True} \land \text{ai\_contained} = \text{True} \land \text{resolution\_type} = \text{'AI\_Resolved'} \land \text{repeat\_contact\_7d} = \text{False})}{\sum \mathbf{1}(\text{ai\_used} = \text{True})}$$
- **Why It Matters**: QAC penalizes "false containment" (where conversations are closed or abandoned without actual resolution) and reflects true net deflective value.

---

### Framework B: AI Resolution Quality Score (ARQS)

An independent, proposed composite score on a 0–100 index evaluated per conversation:

$$\text{ARQS} = 40 \times \mathbf{1}_{\text{SARR}} + 25 \times (1 - \mathbf{1}_{\text{Error}}) + 20 \times (1 - \mathbf{1}_{\text{Repeat7d}}) + 15 \times \left(\frac{\text{CSAT} - 1}{4}\right)$$

*(When CSAT is null, the remaining 85 points are normalized to a 100-point scale).*

---

## 4. KPI Measurement Matrix

| KPI Name | Target Horizon | Granularity | Owner | Primary Analytical Use |
| :--- | :--- | :--- | :--- | :--- |
| **SARR (North Star)** | Weekly / Monthly | Global, Issue, Segment | Product & Analytics | Core Go/No-Go release criterion |
| **Containment Rate** | Daily / Weekly | Global, Issue, Region | Operations | Capacity planning |
| **Positive CSAT** | Weekly | Segment, Issue | CX Lead | Creator experience health |
| **Repeat Contact Rate** | Weekly | Issue, Complexity | Quality Lead | Failure demand identification |
| **AI Error Rate** | Weekly | Model Version, Issue | AI Engineering / Safety | Hallucination guardrail |
| **Human Support Hours** | Monthly | Global, Tier | Workforce Planning | Operational cost impact |
