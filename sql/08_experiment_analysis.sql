-- ==============================================================================
-- 08_experiment_analysis.sql
-- YouTube Creator Support AI Agent Analytics: May-June Randomized A/B Test Results
-- 
-- Business Purpose: Formal experimental evaluation comparing Control (V1) and
-- Treatment (V2) across primary, secondary, and guardrail metrics.
-- ==============================================================================

WITH rct_stats AS (
    SELECT 
        f.experiment_group,
        f.ai_version,
        COUNT(*) AS total_interactions,
        SUM(CASE WHEN f.ai_contained = TRUE THEN 1 ELSE 0 END) AS contained_volume,
        
        -- SARR Numerator
        SUM(CASE WHEN f.ai_contained = TRUE 
                  AND f.resolution_type = 'AI_Resolved' 
                  AND f.repeat_contact_7d = FALSE 
                 THEN 1 ELSE 0 END) AS sarr_successful_resolutions,
                 
        -- Secondary Metrics
        SUM(CASE WHEN f.human_escalated = TRUE THEN 1 ELSE 0 END) AS human_escalations,
        SUM(CASE WHEN f.repeat_contact_7d = TRUE THEN 1 ELSE 0 END) AS repeat_contacts_7d,
        SUM(CASE WHEN f.ai_error_flag = TRUE THEN 1 ELSE 0 END) AS ai_errors,
        
        -- CSAT
        COUNT(f.csat_score) AS csat_responses,
        SUM(CASE WHEN f.csat_score >= 4 THEN 1 ELSE 0 END) AS positive_csat_responses,
        AVG(f.csat_score * 1.0) AS mean_csat,
        
        -- Efficiency
        AVG(f.ai_response_time_sec) AS mean_latency_sec,
        SUM(f.human_handling_time_min) / 60.0 AS total_human_hours
    FROM fact_conversations f
    WHERE f.experiment_group IN ('Control_V1', 'Treatment_V2')
    GROUP BY f.experiment_group, f.ai_version
)
SELECT 
    experiment_group,
    ai_version,
    total_interactions,
    
    -- Primary Metric: SARR
    ROUND(100.0 * sarr_successful_resolutions / total_interactions, 2) AS sarr_pct,
    
    -- Secondary Metrics
    ROUND(100.0 * contained_volume / total_interactions, 2) AS containment_pct,
    ROUND(100.0 * positive_csat_responses / NULLIF(csat_responses, 0), 2) AS positive_csat_pct,
    ROUND(mean_csat, 2) AS mean_csat,
    ROUND(100.0 * repeat_contacts_7d / total_interactions, 2) AS repeat_contact_7d_pct,
    ROUND(100.0 * human_escalations / total_interactions, 2) AS escalation_pct,
    
    -- Guardrail Metric
    ROUND(100.0 * ai_errors / total_interactions, 2) AS ai_error_pct,
    
    -- Efficiency & Operations
    ROUND(mean_latency_sec, 2) AS mean_latency_sec,
    ROUND(total_human_hours, 1) AS human_hours_consumed
FROM rct_stats
ORDER BY experiment_group;
