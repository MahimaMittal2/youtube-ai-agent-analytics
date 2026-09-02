-- ==============================================================================
-- 09_operational_impact.sql
-- YouTube Creator Support AI Agent Analytics: Human Operations & Workload Impact
-- 
-- Business Purpose: Measure the total burden on human support operations,
-- differentiating direct non-AI routing, active escalations, and repeat failure demand.
-- ==============================================================================

WITH operational_summary AS (
    SELECT 
        CASE 
            WHEN eligible_for_ai = FALSE THEN '1. Ineligible (Direct Human Routing)'
            WHEN ai_used = FALSE THEN '2. Opted Out of AI (Direct Human Routing)'
            WHEN ai_contained = FALSE THEN '3. Live AI Escalation to Human'
            WHEN ai_contained = TRUE AND resolution_type = 'AI_Resolved' AND repeat_contact_7d = FALSE THEN '4. Durable AI Resolution (No Human Touch)'
            ELSE '5. False Containment (Unresolved/Abandoned AI)'
        END AS routing_outcome,
        
        COUNT(*) AS conversation_count,
        SUM(CASE WHEN human_escalated = TRUE THEN 1 ELSE 0 END) AS human_tickets_handled,
        SUM(human_handling_time_min) / 60.0 AS total_human_hours_spent,
        AVG(CASE WHEN human_escalated = TRUE THEN human_handling_time_min ELSE NULL END) AS avg_handling_time_min,
        SUM(CASE WHEN repeat_contact_7d = TRUE THEN 1 ELSE 0 END) AS repeat_tickets_generated
    FROM fact_conversations
    GROUP BY 
        CASE 
            WHEN eligible_for_ai = FALSE THEN '1. Ineligible (Direct Human Routing)'
            WHEN ai_used = FALSE THEN '2. Opted Out of AI (Direct Human Routing)'
            WHEN ai_contained = FALSE THEN '3. Live AI Escalation to Human'
            WHEN ai_contained = TRUE AND resolution_type = 'AI_Resolved' AND repeat_contact_7d = FALSE THEN '4. Durable AI Resolution (No Human Touch)'
            ELSE '5. False Containment (Unresolved/Abandoned AI)'
        END
)
SELECT 
    routing_outcome,
    conversation_count,
    ROUND(100.0 * conversation_count / SUM(conversation_count) OVER (), 2) AS share_of_total_inbound_pct,
    human_tickets_handled,
    ROUND(total_human_hours_spent, 1) AS total_human_hours,
    ROUND(100.0 * total_human_hours_spent / NULLIF(SUM(total_human_hours_spent) OVER (), 0), 2) AS share_of_human_labor_pct,
    ROUND(avg_handling_time_min, 2) AS avg_hht_min,
    repeat_tickets_generated,
    ROUND(100.0 * repeat_tickets_generated / conversation_count, 2) AS repeat_rate_pct
FROM operational_summary
ORDER BY routing_outcome;
