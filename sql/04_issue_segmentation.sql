-- ==============================================================================
-- 04_issue_segmentation.sql
-- YouTube Creator Support AI Agent Analytics: Performance Breakdown by Issue Type
-- 
-- Business Purpose: Identify issue categories with the highest failure demand,
-- lowest resolution rates, and largest containment vs resolution wedges.
-- ==============================================================================

WITH issue_stats AS (
    SELECT 
        f.issue_type,
        i.issue_category,
        i.default_complexity,
        COUNT(*) AS total_volume,
        SUM(CASE WHEN f.ai_used = TRUE THEN 1 ELSE 0 END) AS ai_volume,
        SUM(CASE WHEN f.ai_used = TRUE AND f.ai_contained = TRUE THEN 1 ELSE 0 END) AS ai_contained_volume,
        
        -- SARR Numerator
        SUM(CASE WHEN f.ai_used = TRUE 
                  AND f.ai_contained = TRUE 
                  AND f.resolution_type = 'AI_Resolved' 
                  AND f.repeat_contact_7d = FALSE 
                 THEN 1 ELSE 0 END) AS sarr_resolutions,
                 
        -- Quality & Friction
        SUM(CASE WHEN f.ai_used = TRUE AND f.ai_error_flag = TRUE THEN 1 ELSE 0 END) AS ai_errors,
        SUM(CASE WHEN f.ai_used = TRUE AND f.repeat_contact_7d = TRUE THEN 1 ELSE 0 END) AS ai_repeat_contacts,
        SUM(CASE WHEN f.ai_used = TRUE AND f.human_escalated = TRUE THEN 1 ELSE 0 END) AS ai_escalations,
        
        -- CSAT
        COUNT(CASE WHEN f.ai_used = TRUE THEN f.csat_score ELSE NULL END) AS ai_csat_responses,
        SUM(CASE WHEN f.ai_used = TRUE AND f.csat_score >= 4 THEN 1 ELSE 0 END) AS ai_positive_csat,
        AVG(CASE WHEN f.ai_used = TRUE THEN f.csat_score * 1.0 ELSE NULL END) AS ai_mean_csat,
        
        -- Human Handling
        SUM(f.human_handling_time_min) / 60.0 AS total_human_hours
    FROM fact_conversations f
    JOIN dim_issue_type i ON f.issue_type = i.issue_type
    GROUP BY f.issue_type, i.issue_category, i.default_complexity
)
SELECT 
    issue_type,
    issue_category,
    default_complexity,
    total_volume,
    ai_volume,
    
    -- Funnel & SARR
    ROUND(100.0 * ai_contained_volume / ai_volume, 2) AS containment_rate_pct,
    ROUND(100.0 * sarr_resolutions / ai_volume, 2) AS sarr_pct,
    ROUND(100.0 * (ai_contained_volume - sarr_resolutions) / ai_volume, 2) AS false_containment_gap_pct,
    
    -- Quality Metrics
    ROUND(100.0 * ai_errors / ai_volume, 2) AS ai_error_rate_pct,
    ROUND(100.0 * ai_repeat_contacts / ai_volume, 2) AS repeat_contact_7d_pct,
    ROUND(100.0 * ai_escalations / ai_volume, 2) AS escalation_rate_pct,
    
    -- CSAT
    ROUND(100.0 * ai_positive_csat / NULLIF(ai_csat_responses, 0), 2) AS positive_csat_pct,
    ROUND(ai_mean_csat, 2) AS mean_csat,
    
    -- Operations
    ROUND(total_human_hours, 1) AS human_hours_consumed
FROM issue_stats
ORDER BY sarr_pct ASC;
