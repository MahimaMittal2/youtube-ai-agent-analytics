-- ==============================================================================
-- 10_forecasting_inputs.sql
-- YouTube Creator Support AI Agent Analytics: Funnel Conversion Parameters for Forecasting
-- 
-- Business Purpose: Extract empirical transition probabilities across the support funnel
-- to parameterize operational demand and capacity forecasts.
-- ==============================================================================

WITH monthly_funnel AS (
    SELECT 
        d.year,
        d.month,
        COUNT(*) AS total_inbound_volume,
        
        -- Funnel Stages
        SUM(CASE WHEN f.eligible_for_ai = TRUE THEN 1 ELSE 0 END) AS eligible_volume,
        SUM(CASE WHEN f.ai_used = TRUE THEN 1 ELSE 0 END) AS ai_used_volume,
        SUM(CASE WHEN f.ai_used = TRUE AND f.ai_contained = TRUE THEN 1 ELSE 0 END) AS ai_contained_volume,
        SUM(CASE WHEN f.ai_used = TRUE 
                  AND f.ai_contained = TRUE 
                  AND f.resolution_type = 'AI_Resolved' 
                  AND f.repeat_contact_7d = FALSE 
                 THEN 1 ELSE 0 END) AS sarr_resolutions,
        
        -- Escalations & Repeat Failure Demand
        SUM(CASE WHEN f.human_escalated = TRUE THEN 1 ELSE 0 END) AS direct_escalated_human_volume,
        SUM(CASE WHEN f.ai_used = TRUE AND f.ai_contained = TRUE AND f.repeat_contact_7d = TRUE THEN 1 ELSE 0 END) AS false_contained_repeat_volume,
        
        -- Human Handling Times
        AVG(CASE WHEN f.human_escalated = TRUE THEN f.human_handling_time_min ELSE NULL END) AS avg_hht_min,
        SUM(f.human_handling_time_min) / 60.0 AS total_human_hours
    FROM fact_conversations f
    JOIN dim_date d ON f.conversation_date = d.date
    GROUP BY d.year, d.month
)
SELECT 
    year,
    month,
    total_inbound_volume,
    
    -- Conversion Rates
    ROUND(1.0 * eligible_volume / total_inbound_volume, 4) AS p_eligibility,
    ROUND(1.0 * ai_used_volume / eligible_volume, 4) AS p_adoption_given_eligible,
    ROUND(1.0 * ai_contained_volume / ai_used_volume, 4) AS p_containment_given_used,
    ROUND(1.0 * sarr_resolutions / ai_contained_volume, 4) AS p_resolution_given_contained,
    ROUND(1.0 * false_contained_repeat_volume / NULLIF(ai_contained_volume, 0), 4) AS p_repeat_given_contained,
    
    -- Operations
    direct_escalated_human_volume,
    false_contained_repeat_volume,
    ROUND(avg_hht_min, 2) AS avg_handling_time_min,
    ROUND(total_human_hours, 1) AS human_support_hours
FROM monthly_funnel
ORDER BY year, month;
