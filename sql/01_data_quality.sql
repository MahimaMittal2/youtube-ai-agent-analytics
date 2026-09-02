-- ==============================================================================
-- 01_data_quality.sql
-- YouTube Creator Support AI Agent Analytics: Data Integrity & Quality Checks
-- 
-- Synthetic Data Disclosure: This script validates a synthetic simulation dataset.
-- ==============================================================================

-- 1. Primary Key Uniqueness & Nullability Assertions
WITH pk_check AS (
    SELECT 
        'fact_conversations' AS table_name,
        COUNT(*) AS total_rows,
        COUNT(DISTINCT conversation_id) AS unique_pks,
        COUNT(*) - COUNT(conversation_id) AS null_pks
    FROM fact_conversations
    UNION ALL
    SELECT 
        'dim_creator' AS table_name,
        COUNT(*) AS total_rows,
        COUNT(DISTINCT creator_id) AS unique_pks,
        COUNT(*) - COUNT(creator_id) AS null_pks
    FROM dim_creator
    UNION ALL
    SELECT 
        'dim_issue_type' AS table_name,
        COUNT(*) AS total_rows,
        COUNT(DISTINCT issue_type) AS unique_pks,
        COUNT(*) - COUNT(issue_type) AS null_pks
    FROM dim_issue_type
    UNION ALL
    SELECT 
        'dim_ai_version' AS table_name,
        COUNT(*) AS total_rows,
        COUNT(DISTINCT ai_version) AS unique_pks,
        COUNT(*) - COUNT(ai_version) AS null_pks
    FROM dim_ai_version
    UNION ALL
    SELECT 
        'dim_date' AS table_name,
        COUNT(*) AS total_rows,
        COUNT(DISTINCT date) AS unique_pks,
        COUNT(*) - COUNT(date) AS null_pks
    FROM dim_date
)
SELECT 
    table_name,
    total_rows,
    unique_pks,
    null_pks,
    CASE WHEN total_rows = unique_pks AND null_pks = 0 THEN 'PASS' ELSE 'FAIL' END AS pk_status
FROM pk_check;

-- 2. Foreign Key Referential Integrity Check
SELECT 
    'Orphan creator_ids' AS check_name,
    COUNT(*) AS orphan_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_conversations f
LEFT JOIN dim_creator c ON f.creator_id = c.creator_id
WHERE c.creator_id IS NULL

UNION ALL

SELECT 
    'Orphan issue_types' AS check_name,
    COUNT(*) AS orphan_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_conversations f
LEFT JOIN dim_issue_type i ON f.issue_type = i.issue_type
WHERE i.issue_type IS NULL

UNION ALL

SELECT 
    'Orphan dates' AS check_name,
    COUNT(*) AS orphan_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_conversations f
LEFT JOIN dim_date d ON f.conversation_date = d.date
WHERE d.date IS NULL;

-- 3. Business State Mutex & Logical Consistency Checks
SELECT 
    'Invalid AI/Human Mutex State' AS check_name,
    COUNT(*) AS violation_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_conversations
WHERE ai_used = TRUE 
  AND ai_contained = human_escalated

UNION ALL

SELECT 
    'Negative or Zero Handling Time on Escalation' AS check_name,
    COUNT(*) AS violation_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_conversations
WHERE human_escalated = TRUE 
  AND (human_handling_time_min IS NULL OR human_handling_time_min <= 0)

UNION ALL

SELECT 
    'Handling Time on Non-Escalated Conversation' AS check_name,
    COUNT(*) AS violation_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_conversations
WHERE human_escalated = FALSE 
  AND human_handling_time_min > 0

UNION ALL

SELECT 
    'CSAT Score Out of Range' AS check_name,
    COUNT(*) AS violation_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_conversations
WHERE csat_score IS NOT NULL 
  AND (csat_score < 1 OR csat_score > 5);
