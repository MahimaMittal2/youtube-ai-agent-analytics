-- ==============================================================================
-- 07_ai_quality_analysis.sql
-- YouTube Creator Support AI Agent Analytics: AI Response Quality & Error Diagnostics
-- 
-- Business Purpose: Quantify the operational impact of AI errors and response quality
-- on CSAT destruction, 7-day failure demand (repeat contacts), and resolution rates.
-- ==============================================================================

-- 1. Performance Segmented by AI Error Occurrence
SELECT 
    f.ai_version,
    f.ai_error_flag,
    COUNT(*) AS ai_volume,
    
    -- Resolution Outcomes
    ROUND(100.0 * SUM(CASE WHEN f.resolution_status = 'Resolved' THEN 1 ELSE 0 END) / COUNT(*), 2) AS resolution_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN f.ai_contained = TRUE AND f.resolution_type = 'AI_Resolved' AND f.repeat_contact_7d = FALSE THEN 1 ELSE 0 END) / COUNT(*), 2) AS sarr_pct,
    
    -- Downstream Friction
    ROUND(100.0 * SUM(CASE WHEN f.repeat_contact_7d = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) AS repeat_contact_7d_pct,
    
    -- Satisfaction
    COUNT(f.csat_score) AS survey_responses,
    ROUND(100.0 * SUM(CASE WHEN f.csat_score >= 4 THEN 1 ELSE 0 END) / NULLIF(COUNT(f.csat_score), 0), 2) AS positive_csat_pct,
    ROUND(AVG(f.csat_score * 1.0), 2) AS mean_csat_score
FROM fact_conversations f
WHERE f.ai_used = TRUE
GROUP BY f.ai_version, f.ai_error_flag
ORDER BY f.ai_version, f.ai_error_flag DESC;

-- 2. Performance Segmented by Evaluated AI Response Quality Tier
SELECT 
    f.ai_response_quality,
    COUNT(*) AS evaluated_volume,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS quality_share_pct,
    
    -- Error Correlation
    ROUND(100.0 * SUM(CASE WHEN f.ai_error_flag = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) AS error_rate_pct,
    
    -- Containment & Resolution
    ROUND(100.0 * SUM(CASE WHEN f.ai_contained = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) AS containment_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN f.ai_contained = TRUE AND f.resolution_type = 'AI_Resolved' AND f.repeat_contact_7d = FALSE THEN 1 ELSE 0 END) / COUNT(*), 2) AS sarr_pct,
    
    -- Friction & CSAT
    ROUND(100.0 * SUM(CASE WHEN f.repeat_contact_7d = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) AS repeat_contact_7d_pct,
    ROUND(AVG(f.csat_score * 1.0), 2) AS mean_csat_score
FROM fact_conversations f
WHERE f.ai_used = TRUE AND f.ai_response_quality IS NOT NULL
GROUP BY f.ai_response_quality
ORDER BY 
    CASE f.ai_response_quality 
        WHEN 'High' THEN 1 
        WHEN 'Medium' THEN 2 
        WHEN 'Low' THEN 3 
    END;
