-- ==============================================================================
-- 05_creator_segmentation.sql
-- YouTube Creator Support AI Agent Analytics: Performance by Creator Tier
-- 
-- Business Purpose: Analyze differences in AI adoption, containment, friction,
-- and CSAT across Emerging (<10K), Growth (10K-100K), Established (100K-1M), and Large (>1M).
-- ==============================================================================

WITH creator_cohort_stats AS (
    SELECT 
        c.creator_segment,
        COUNT(DISTINCT c.creator_id) AS total_creators,
        COUNT(*) AS total_conversations,
        SUM(CASE WHEN f.eligible_for_ai = TRUE THEN 1 ELSE 0 END) AS eligible_volume,
        SUM(CASE WHEN f.ai_used = TRUE THEN 1 ELSE 0 END) AS ai_volume,
        SUM(CASE WHEN f.ai_used = TRUE AND f.ai_contained = TRUE THEN 1 ELSE 0 END) AS ai_contained_volume,
        
        -- SARR Numerator
        SUM(CASE WHEN f.ai_used = TRUE 
                  AND f.ai_contained = TRUE 
                  AND f.resolution_type = 'AI_Resolved' 
                  AND f.repeat_contact_7d = FALSE 
                 THEN 1 ELSE 0 END) AS sarr_resolutions,
                 
        -- Experience & Errors
        SUM(CASE WHEN f.ai_used = TRUE AND f.ai_error_flag = TRUE THEN 1 ELSE 0 END) AS ai_errors,
        SUM(CASE WHEN f.ai_used = TRUE AND f.repeat_contact_7d = TRUE THEN 1 ELSE 0 END) AS ai_repeat_contacts,
        COUNT(CASE WHEN f.ai_used = TRUE THEN f.csat_score ELSE NULL END) AS ai_csat_responses,
        SUM(CASE WHEN f.ai_used = TRUE AND f.csat_score >= 4 THEN 1 ELSE 0 END) AS ai_positive_csat,
        AVG(CASE WHEN f.ai_used = TRUE THEN f.csat_score * 1.0 ELSE NULL END) AS ai_mean_csat,
        
        -- Handling Time
        SUM(f.human_handling_time_min) / 60.0 AS total_human_hours
    FROM fact_conversations f
    JOIN dim_creator c ON f.creator_id = c.creator_id
    GROUP BY c.creator_segment
)
SELECT 
    creator_segment,
    total_creators,
    total_conversations,
    ROUND(total_conversations * 1.0 / total_creators, 2) AS avg_tickets_per_creator,
    
    -- Funnel Rates
    ROUND(100.0 * ai_volume / eligible_volume, 2) AS ai_adoption_pct,
    ROUND(100.0 * ai_contained_volume / ai_volume, 2) AS ai_containment_pct,
    ROUND(100.0 * sarr_resolutions / ai_volume, 2) AS sarr_pct,
    ROUND(100.0 * (ai_contained_volume - sarr_resolutions) / ai_volume, 2) AS false_containment_gap_pct,
    
    -- Quality & CSAT
    ROUND(100.0 * ai_errors / ai_volume, 2) AS ai_error_pct,
    ROUND(100.0 * ai_repeat_contacts / ai_volume, 2) AS repeat_contact_7d_pct,
    ROUND(100.0 * ai_positive_csat / NULLIF(ai_csat_responses, 0), 2) AS positive_csat_pct,
    ROUND(ai_mean_csat, 2) AS mean_csat,
    
    -- Workload
    ROUND(total_human_hours, 1) AS human_hours_consumed
FROM creator_cohort_stats
ORDER BY 
    CASE creator_segment 
        WHEN 'Emerging' THEN 1 
        WHEN 'Growth' THEN 2 
        WHEN 'Established' THEN 3 
        WHEN 'Large' THEN 4 
    END;
