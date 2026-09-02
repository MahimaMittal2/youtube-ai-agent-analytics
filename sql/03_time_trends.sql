-- ==============================================================================
-- 03_time_trends.sql
-- YouTube Creator Support AI Agent Analytics: Monthly & Weekly KPI Longitudinal Trends
-- 
-- Business Purpose: Track the temporal evolution of Containment, SARR, CSAT,
-- and Operational Workload across Baseline, Experiment, and Post-Experiment phases.
-- ==============================================================================

SELECT 
    d.year,
    d.month,
    d.month_name,
    CASE 
        WHEN d.month BETWEEN 1 AND 4 THEN '1. Baseline (V1)'
        WHEN d.month BETWEEN 5 AND 6 THEN '2. Controlled A/B Experiment (V1 vs V2)'
        ELSE '3. Post-Experiment Observation'
    END AS lifecycle_phase,
    
    COUNT(*) AS total_volume,
    SUM(CASE WHEN f.eligible_for_ai = TRUE THEN 1 ELSE 0 END) AS eligible_volume,
    SUM(CASE WHEN f.ai_used = TRUE THEN 1 ELSE 0 END) AS ai_volume,
    
    -- Funnel Rates
    ROUND(100.0 * SUM(CASE WHEN f.ai_used = TRUE THEN 1 ELSE 0 END) / 
          NULLIF(SUM(CASE WHEN f.eligible_for_ai = TRUE THEN 1 ELSE 0 END), 0), 2) AS ai_adoption_pct,
          
    ROUND(100.0 * SUM(CASE WHEN f.ai_used = TRUE AND f.ai_contained = TRUE THEN 1 ELSE 0 END) / 
          NULLIF(SUM(CASE WHEN f.ai_used = TRUE THEN 1 ELSE 0 END), 0), 2) AS ai_containment_pct,
          
    -- North Star SARR
    ROUND(100.0 * SUM(CASE WHEN f.ai_used = TRUE 
                             AND f.ai_contained = TRUE 
                             AND f.resolution_type = 'AI_Resolved' 
                             AND f.repeat_contact_7d = FALSE 
                            THEN 1 ELSE 0 END) / 
          NULLIF(SUM(CASE WHEN f.ai_used = TRUE THEN 1 ELSE 0 END), 0), 2) AS sarr_pct,
          
    -- False Containment Gap
    ROUND(100.0 * (SUM(CASE WHEN f.ai_used = TRUE AND f.ai_contained = TRUE THEN 1 ELSE 0 END) - 
                   SUM(CASE WHEN f.ai_used = TRUE AND f.ai_contained = TRUE AND f.resolution_type = 'AI_Resolved' AND f.repeat_contact_7d = FALSE THEN 1 ELSE 0 END)) / 
          NULLIF(SUM(CASE WHEN f.ai_used = TRUE THEN 1 ELSE 0 END), 0), 2) AS false_containment_gap_pct,
          
    -- Experience & Friction
    ROUND(100.0 * SUM(CASE WHEN f.csat_score >= 4 THEN 1 ELSE 0 END) / 
          NULLIF(COUNT(f.csat_score), 0), 2) AS positive_csat_pct,
    ROUND(AVG(f.csat_score * 1.0), 2) AS mean_csat,
    ROUND(100.0 * SUM(CASE WHEN f.ai_used = TRUE AND f.repeat_contact_7d = TRUE THEN 1 ELSE 0 END) / 
          NULLIF(SUM(CASE WHEN f.ai_used = TRUE THEN 1 ELSE 0 END), 0), 2) AS repeat_contact_7d_pct,
    ROUND(100.0 * SUM(CASE WHEN f.ai_used = TRUE AND f.ai_error_flag = TRUE THEN 1 ELSE 0 END) / 
          NULLIF(SUM(CASE WHEN f.ai_used = TRUE THEN 1 ELSE 0 END), 0), 2) AS ai_error_pct,
          
    -- Human Workload
    SUM(CASE WHEN f.human_escalated = TRUE THEN 1 ELSE 0 END) AS human_queue_volume,
    ROUND(SUM(f.human_handling_time_min) / 60.0, 1) AS total_human_hours
FROM fact_conversations f
JOIN dim_date d ON f.conversation_date = d.date
GROUP BY 
    d.year, 
    d.month, 
    d.month_name,
    CASE 
        WHEN d.month BETWEEN 1 AND 4 THEN '1. Baseline (V1)'
        WHEN d.month BETWEEN 5 AND 6 THEN '2. Controlled A/B Experiment (V1 vs V2)'
        ELSE '3. Post-Experiment Observation'
    END
ORDER BY d.year, d.month;
