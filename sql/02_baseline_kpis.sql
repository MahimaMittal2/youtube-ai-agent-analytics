-- ==============================================================================
-- 02_baseline_kpis.sql
-- YouTube Creator Support AI Agent Analytics: Baseline V1 Performance (Jan-Apr 2026)
-- 
-- Business Purpose: Establish pre-experiment benchmarks for V1 across Adoption,
-- Containment, SARR, CSAT, Repeat Contacts, and Latency.
-- ==============================================================================

WITH baseline_data AS (
    SELECT 
        conversation_id,
        creator_id,
        eligible_for_ai,
        ai_used,
        ai_contained,
        resolution_status,
        resolution_type,
        human_escalated,
        ai_error_flag,
        csat_score,
        repeat_contact_7d,
        ai_response_time_sec,
        human_handling_time_min,
        conversation_duration_min
    FROM fact_conversations
    WHERE conversation_date >= '2026-01-01' 
      AND conversation_date <= '2026-04-30'
),
kpi_summary AS (
    SELECT 
        -- Funnel Volumes
        COUNT(*) AS total_conversations,
        SUM(CASE WHEN eligible_for_ai = TRUE THEN 1 ELSE 0 END) AS eligible_conversations,
        SUM(CASE WHEN ai_used = TRUE THEN 1 ELSE 0 END) AS ai_used_conversations,
        SUM(CASE WHEN ai_used = TRUE AND ai_contained = TRUE THEN 1 ELSE 0 END) AS ai_contained_conversations,
        
        -- North Star SARR Numerator (among active AI conversations)
        SUM(CASE WHEN ai_used = TRUE 
                  AND ai_contained = TRUE 
                  AND resolution_type = 'AI_Resolved' 
                  AND repeat_contact_7d = FALSE 
                 THEN 1 ELSE 0 END) AS sarr_successful_resolutions,
                 
        -- Escalations & Errors
        SUM(CASE WHEN ai_used = TRUE AND human_escalated = TRUE THEN 1 ELSE 0 END) AS ai_escalations,
        SUM(CASE WHEN ai_used = TRUE AND ai_error_flag = TRUE THEN 1 ELSE 0 END) AS ai_errors,
        SUM(CASE WHEN ai_used = TRUE AND repeat_contact_7d = TRUE THEN 1 ELSE 0 END) AS ai_repeat_contacts,
        
        -- CSAT Metrics
        COUNT(csat_score) AS valid_csat_responses,
        SUM(CASE WHEN csat_score >= 4 THEN 1 ELSE 0 END) AS positive_csat_responses,
        AVG(csat_score * 1.0) AS mean_csat_score,
        
        -- Latency & Handling Time
        AVG(ai_response_time_sec) AS mean_ai_response_time_sec,
        AVG(CASE WHEN human_escalated = TRUE THEN human_handling_time_min ELSE NULL END) AS mean_human_handling_time_min,
        SUM(human_handling_time_min) / 60.0 AS total_human_support_hours
    FROM baseline_data
)
SELECT 
    total_conversations,
    eligible_conversations,
    ai_used_conversations,
    
    -- Funnel Rates
    ROUND(100.0 * eligible_conversations / total_conversations, 2) AS ai_eligibility_pct,
    ROUND(100.0 * ai_used_conversations / eligible_conversations, 2) AS ai_adoption_pct,
    ROUND(100.0 * ai_contained_conversations / ai_used_conversations, 2) AS ai_containment_pct,
    
    -- North Star SARR
    ROUND(100.0 * sarr_successful_resolutions / ai_used_conversations, 2) AS sarr_pct,
    
    -- False Containment Wedge
    ROUND(100.0 * (ai_contained_conversations - sarr_successful_resolutions) / ai_used_conversations, 2) AS false_containment_wedge_pct,
    
    -- Experience & Quality
    ROUND(100.0 * positive_csat_responses / valid_csat_responses, 2) AS positive_csat_pct,
    ROUND(mean_csat_score, 2) AS mean_csat,
    ROUND(100.0 * ai_repeat_contacts / ai_used_conversations, 2) AS repeat_contact_7d_pct,
    ROUND(100.0 * ai_errors / ai_used_conversations, 2) AS ai_error_pct,
    ROUND(100.0 * ai_escalations / ai_used_conversations, 2) AS human_escalation_pct,
    
    -- Efficiency
    ROUND(mean_ai_response_time_sec, 2) AS mean_ai_latency_sec,
    ROUND(mean_human_handling_time_min, 2) AS mean_human_handle_time_min,
    ROUND(total_human_support_hours, 1) AS total_human_hours
FROM kpi_summary;
