-- ==============================================================================
-- 06_complexity_analysis.sql
-- YouTube Creator Support AI Agent Analytics: Performance by Complexity Tier
-- 
-- Business Purpose: Demonstrate the interaction between problem complexity (Low,
-- Medium, High) and the wedge between Containment and Successful AI Resolution.
-- ==============================================================================

WITH complexity_stats AS (
    SELECT 
        f.issue_complexity,
        f.ai_version,
        COUNT(*) AS total_volume,
        SUM(CASE WHEN f.ai_used = TRUE THEN 1 ELSE 0 END) AS ai_volume,
        SUM(CASE WHEN f.ai_used = TRUE AND f.ai_contained = TRUE THEN 1 ELSE 0 END) AS ai_contained_volume,
        
        -- SARR Numerator
        SUM(CASE WHEN f.ai_used = TRUE 
                  AND f.ai_contained = TRUE 
                  AND f.resolution_type = 'AI_Resolved' 
                  AND f.repeat_contact_7d = FALSE 
                 THEN 1 ELSE 0 END) AS sarr_resolutions,
                 
        -- Quality & Escalation
        SUM(CASE WHEN f.ai_used = TRUE AND f.ai_error_flag = TRUE THEN 1 ELSE 0 END) AS ai_errors,
        SUM(CASE WHEN f.ai_used = TRUE AND f.repeat_contact_7d = TRUE THEN 1 ELSE 0 END) AS ai_repeat_contacts,
        SUM(CASE WHEN f.ai_used = TRUE AND f.human_escalated = TRUE THEN 1 ELSE 0 END) AS ai_escalations,
        
        -- CSAT
        COUNT(CASE WHEN f.ai_used = TRUE THEN f.csat_score ELSE NULL END) AS ai_csat_responses,
        SUM(CASE WHEN f.ai_used = TRUE AND f.csat_score >= 4 THEN 1 ELSE 0 END) AS ai_positive_csat,
        AVG(CASE WHEN f.ai_used = TRUE THEN f.csat_score * 1.0 ELSE NULL END) AS ai_mean_csat,
        
        -- Labor
        AVG(CASE WHEN f.human_escalated = TRUE THEN f.human_handling_time_min ELSE NULL END) AS mean_human_hht_min,
        SUM(f.human_handling_time_min) / 60.0 AS total_human_hours
    FROM fact_conversations f
    WHERE f.ai_version IN ('V1', 'V2')
    GROUP BY f.issue_complexity, f.ai_version
)
SELECT 
    issue_complexity,
    ai_version,
    ai_volume,
    
    -- Headline Containment vs SARR
    ROUND(100.0 * ai_contained_volume / ai_volume, 2) AS containment_rate_pct,
    ROUND(100.0 * sarr_resolutions / ai_volume, 2) AS sarr_pct,
    ROUND(100.0 * (ai_contained_volume - sarr_resolutions) / ai_volume, 2) AS false_containment_wedge_pct,
    
    -- Quality-Adjusted Containment (QAC)
    ROUND(100.0 * sarr_resolutions / ai_volume, 2) AS qac_pct,
    
    -- Quality & Friction
    ROUND(100.0 * ai_errors / ai_volume, 2) AS ai_error_pct,
    ROUND(100.0 * ai_repeat_contacts / ai_volume, 2) AS repeat_contact_7d_pct,
    ROUND(100.0 * ai_escalations / ai_volume, 2) AS escalation_pct,
    
    -- CSAT
    ROUND(100.0 * ai_positive_csat / NULLIF(ai_csat_responses, 0), 2) AS positive_csat_pct,
    ROUND(ai_mean_csat, 2) AS mean_csat,
    
    -- Human Workload
    ROUND(mean_human_hht_min, 2) AS avg_hht_min,
    ROUND(total_human_hours, 1) AS total_human_hours
FROM complexity_stats
ORDER BY 
    CASE issue_complexity 
        WHEN 'Low' THEN 1 
        WHEN 'Medium' THEN 2 
        WHEN 'High' THEN 3 
    END,
    ai_version;
