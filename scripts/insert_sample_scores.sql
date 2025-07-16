INSERT INTO candidate_scores (candidate_id, job_profile_id, overall_score, score_breakdown, methodology) 
SELECT 
    c.id, 
    j.id, 
    ROUND((RANDOM() * 0.4 + 0.6)::NUMERIC, 6), 
    '{"experience": 0.85, "skills": 0.92, "education": 0.78, "culture_fit": 0.88}', 
    'AHP' 
FROM candidates c 
CROSS JOIN jobs j 
ORDER BY RANDOM()
LIMIT 20;
