-- Insert sample data into candidate_matches table
INSERT INTO candidate_matches (
    id, candidate_id, position_id, overall_score, match_percentage, 
    criteria_scores, score_breakdown, calculated_at, methodology, metadata
) VALUES 
(
    gen_random_uuid(),
    gen_random_uuid(),
    gen_random_uuid(),
    0.85,
    85.5,
    '{"technical_skills": 0.9, "experience": 0.8, "education": 0.7}',
    '{"technical_skills": {"score": 0.9, "weight": 0.4}, "experience": {"score": 0.8, "weight": 0.3}, "education": {"score": 0.7, "weight": 0.3}}',
    NOW(),
    'AHP',
    '{"processing_time": 150, "confidence": 0.85}'
),
(
    gen_random_uuid(),
    gen_random_uuid(),
    gen_random_uuid(),
    0.78,
    78.2,
    '{"technical_skills": 0.8, "experience": 0.75, "education": 0.8}',
    '{"technical_skills": {"score": 0.8, "weight": 0.4}, "experience": {"score": 0.75, "weight": 0.3}, "education": {"score": 0.8, "weight": 0.3}}',
    NOW(),
    'AHP',
    '{"processing_time": 120, "confidence": 0.78}'
),
(
    gen_random_uuid(),
    gen_random_uuid(),
    gen_random_uuid(),
    0.92,
    92.3,
    '{"technical_skills": 0.95, "experience": 0.9, "education": 0.9}',
    '{"technical_skills": {"score": 0.95, "weight": 0.4}, "experience": {"score": 0.9, "weight": 0.3}, "education": {"score": 0.9, "weight": 0.3}}',
    NOW(),
    'AHP',
    '{"processing_time": 180, "confidence": 0.92}'
),
(
    gen_random_uuid(),
    gen_random_uuid(),
    gen_random_uuid(),
    0.68,
    68.7,
    '{"technical_skills": 0.7, "experience": 0.65, "education": 0.7}',
    '{"technical_skills": {"score": 0.7, "weight": 0.4}, "experience": {"score": 0.65, "weight": 0.3}, "education": {"score": 0.7, "weight": 0.3}}',
    NOW(),
    'AHP',
    '{"processing_time": 100, "confidence": 0.68}'
),
(
    gen_random_uuid(),
    gen_random_uuid(),
    gen_random_uuid(),
    0.74,
    74.1,
    '{"technical_skills": 0.75, "experience": 0.72, "education": 0.76}',
    '{"technical_skills": {"score": 0.75, "weight": 0.4}, "experience": {"score": 0.72, "weight": 0.3}, "education": {"score": 0.76, "weight": 0.3}}',
    NOW(),
    'AHP',
    '{"processing_time": 130, "confidence": 0.74}'
);
