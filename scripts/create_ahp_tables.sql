-- Create AHP tables for candidate matching dashboard

-- Create AhpCriteria table
CREATE TABLE IF NOT EXISTS ahp_criteria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_profile_id UUID NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    weight DECIMAL(10,6) NOT NULL DEFAULT 0,
    priority INTEGER NOT NULL DEFAULT 1,
    category VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(job_profile_id, name)
);

-- Create AhpComparisons table
CREATE TABLE IF NOT EXISTS ahp_comparisons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_profile_id UUID NOT NULL,
    criterion_a_id UUID NOT NULL,
    criterion_b_id UUID NOT NULL,
    value DECIMAL(10,6) NOT NULL DEFAULT 1,
    comparison_value DECIMAL(10,6) NOT NULL DEFAULT 1,
    justification TEXT,
    compared_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(job_profile_id, criterion_a_id, criterion_b_id)
);

-- Create CandidateScores table
CREATE TABLE IF NOT EXISTS candidate_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL,
    job_profile_id UUID NOT NULL,
    overall_score DECIMAL(10,6) NOT NULL DEFAULT 0,
    criteria_scores JSONB,
    score_breakdown JSONB,
    methodology VARCHAR(100) DEFAULT 'AHP',
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    scored_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(job_profile_id, candidate_id)
);

-- Create CandidateProfiles table
CREATE TABLE IF NOT EXISTS candidate_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL,
    profile_data JSONB,
    skills JSONB,
    experience JSONB,
    experience_years DECIMAL(4,2),
    education JSONB,
    certifications JSONB,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create JobProfiles table (if not exists)
CREATE TABLE IF NOT EXISTS job_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    requirements JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample job profiles
INSERT INTO job_profiles (id, job_id, name, description, requirements) VALUES
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', '11111111-2222-3333-4444-555555555555', 'Senior Software Engineer', 'Senior level software engineer position', '{"languages": ["Java", "Python", "JavaScript"], "experience": "5+ years"}'),
    ('b2c3d4e5-f6g7-8901-bcde-f23456789012', '22222222-3333-4444-5555-666666666666', 'Product Manager', 'Product manager for enterprise software', '{"experience": "3+ years", "skills": ["Product Strategy", "Data Analysis"]}'),
    ('c3d4e5f6-g7h8-9012-cdef-345678901234', '33333333-4444-5555-6666-777777777777', 'UX Designer', 'Senior UX designer for web applications', '{"experience": "4+ years", "skills": ["Figma", "User Research", "Prototyping"]}')
ON CONFLICT (id) DO NOTHING;

-- Insert sample AHP criteria for each job profile
INSERT INTO ahp_criteria (id, job_profile_id, name, description, weight, priority, category) VALUES
    -- Software Engineer criteria
    ('11111111-aaaa-bbbb-cccc-dddddddddddd', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'technical_skills', 'Technical programming skills', 0.4, 1, 'technical'),
    ('22222222-aaaa-bbbb-cccc-dddddddddddd', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'experience', 'Years of relevant experience', 0.3, 2, 'experience'),
    ('33333333-aaaa-bbbb-cccc-dddddddddddd', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'education', 'Educational background', 0.2, 3, 'education'),
    ('44444444-aaaa-bbbb-cccc-dddddddddddd', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'cultural_fit', 'Cultural fit and soft skills', 0.1, 4, 'soft_skills'),
    -- Product Manager criteria
    ('55555555-aaaa-bbbb-cccc-dddddddddddd', 'b2c3d4e5-f6g7-8901-bcde-f23456789012', 'product_experience', 'Product management experience', 0.35, 1, 'experience'),
    ('66666666-aaaa-bbbb-cccc-dddddddddddd', 'b2c3d4e5-f6g7-8901-bcde-f23456789012', 'analytical_skills', 'Data analysis and metrics', 0.3, 2, 'analytical'),
    ('77777777-aaaa-bbbb-cccc-dddddddddddd', 'b2c3d4e5-f6g7-8901-bcde-f23456789012', 'leadership', 'Leadership and communication', 0.25, 3, 'leadership'),
    ('88888888-aaaa-bbbb-cccc-dddddddddddd', 'b2c3d4e5-f6g7-8901-bcde-f23456789012', 'domain_knowledge', 'Industry domain knowledge', 0.1, 4, 'domain'),
    -- UX Designer criteria
    ('99999999-aaaa-bbbb-cccc-dddddddddddd', 'c3d4e5f6-g7h8-9012-cdef-345678901234', 'design_skills', 'Design tool proficiency', 0.4, 1, 'design'),
    ('aaaaaaaa-aaaa-bbbb-cccc-dddddddddddd', 'c3d4e5f6-g7h8-9012-cdef-345678901234', 'user_research', 'User research experience', 0.3, 2, 'research'),
    ('bbbbbbbb-aaaa-bbbb-cccc-dddddddddddd', 'c3d4e5f6-g7h8-9012-cdef-345678901234', 'portfolio', 'Portfolio quality and diversity', 0.2, 3, 'portfolio'),
    ('cccccccc-aaaa-bbbb-cccc-dddddddddddd', 'c3d4e5f6-g7h8-9012-cdef-345678901234', 'collaboration', 'Team collaboration skills', 0.1, 4, 'collaboration')
ON CONFLICT (id) DO NOTHING;

-- Insert sample candidate scores
INSERT INTO candidate_scores (id, candidate_id, job_profile_id, overall_score, score_breakdown, methodology, calculated_at, scored_at) VALUES
    -- Software Engineer matches
    ('score001-1111-2222-3333-444444444444', 'cand0001-1111-2222-3333-444444444444', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 0.85, '{"technical_skills": 0.34, "experience": 0.27, "education": 0.16, "cultural_fit": 0.08}', 'AHP', CURRENT_TIMESTAMP - INTERVAL '2 hours', CURRENT_TIMESTAMP - INTERVAL '2 hours'),
    ('score002-1111-2222-3333-444444444444', 'cand0002-1111-2222-3333-444444444444', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 0.78, '{"technical_skills": 0.31, "experience": 0.24, "education": 0.14, "cultural_fit": 0.09}', 'AHP', CURRENT_TIMESTAMP - INTERVAL '1 hour', CURRENT_TIMESTAMP - INTERVAL '1 hour'),
    ('score003-1111-2222-3333-444444444444', 'cand0003-1111-2222-3333-444444444444', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 0.92, '{"technical_skills": 0.37, "experience": 0.29, "education": 0.18, "cultural_fit": 0.08}', 'AHP', CURRENT_TIMESTAMP - INTERVAL '30 minutes', CURRENT_TIMESTAMP - INTERVAL '30 minutes'),
    ('score004-1111-2222-3333-444444444444', 'cand0004-1111-2222-3333-444444444444', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 0.71, '{"technical_skills": 0.28, "experience": 0.21, "education": 0.12, "cultural_fit": 0.10}', 'AHP', CURRENT_TIMESTAMP - INTERVAL '45 minutes', CURRENT_TIMESTAMP - INTERVAL '45 minutes'),
    ('score005-1111-2222-3333-444444444444', 'cand0005-1111-2222-3333-444444444444', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 0.88, '{"technical_skills": 0.35, "experience": 0.26, "education": 0.17, "cultural_fit": 0.10}', 'AHP', CURRENT_TIMESTAMP - INTERVAL '15 minutes', CURRENT_TIMESTAMP - INTERVAL '15 minutes'),
    
    -- Product Manager matches
    ('score006-1111-2222-3333-444444444444', 'cand0006-1111-2222-3333-444444444444', 'b2c3d4e5-f6g7-8901-bcde-f23456789012', 0.83, '{"product_experience": 0.29, "analytical_skills": 0.25, "leadership": 0.21, "domain_knowledge": 0.08}', 'AHP', CURRENT_TIMESTAMP - INTERVAL '3 hours', CURRENT_TIMESTAMP - INTERVAL '3 hours'),
    ('score007-1111-2222-3333-444444444444', 'cand0007-1111-2222-3333-444444444444', 'b2c3d4e5-f6g7-8901-bcde-f23456789012', 0.76, '{"product_experience": 0.27, "analytical_skills": 0.23, "leadership": 0.19, "domain_knowledge": 0.07}', 'AHP', CURRENT_TIMESTAMP - INTERVAL '2.5 hours', CURRENT_TIMESTAMP - INTERVAL '2.5 hours'),
    ('score008-1111-2222-3333-444444444444', 'cand0008-1111-2222-3333-444444444444', 'b2c3d4e5-f6g7-8901-bcde-f23456789012', 0.90, '{"product_experience": 0.32, "analytical_skills": 0.27, "leadership": 0.22, "domain_knowledge": 0.09}', 'AHP', CURRENT_TIMESTAMP - INTERVAL '1.5 hours', CURRENT_TIMESTAMP - INTERVAL '1.5 hours'),
    
    -- UX Designer matches
    ('score009-1111-2222-3333-444444444444', 'cand0009-1111-2222-3333-444444444444', 'c3d4e5f6-g7h8-9012-cdef-345678901234', 0.87, '{"design_skills": 0.35, "user_research": 0.26, "portfolio": 0.17, "collaboration": 0.09}', 'AHP', CURRENT_TIMESTAMP - INTERVAL '4 hours', CURRENT_TIMESTAMP - INTERVAL '4 hours'),
    ('score010-1111-2222-3333-444444444444', 'cand0010-1111-2222-3333-444444444444', 'c3d4e5f6-g7h8-9012-cdef-345678901234', 0.79, '{"design_skills": 0.32, "user_research": 0.24, "portfolio": 0.15, "collaboration": 0.08}', 'AHP', CURRENT_TIMESTAMP - INTERVAL '3.5 hours', CURRENT_TIMESTAMP - INTERVAL '3.5 hours'),
    ('score011-1111-2222-3333-444444444444', 'cand0011-1111-2222-3333-444444444444', 'c3d4e5f6-g7h8-9012-cdef-345678901234', 0.94, '{"design_skills": 0.38, "user_research": 0.28, "portfolio": 0.19, "collaboration": 0.09}', 'AHP', CURRENT_TIMESTAMP - INTERVAL '20 minutes', CURRENT_TIMESTAMP - INTERVAL '20 minutes'),
    ('score012-1111-2222-3333-444444444444', 'cand0012-1111-2222-3333-444444444444', 'c3d4e5f6-g7h8-9012-cdef-345678901234', 0.72, '{"design_skills": 0.29, "user_research": 0.22, "portfolio": 0.14, "collaboration": 0.07}', 'AHP', CURRENT_TIMESTAMP - INTERVAL '1 hour', CURRENT_TIMESTAMP - INTERVAL '1 hour'),
    
    -- Additional mixed matches
    ('score013-1111-2222-3333-444444444444', 'cand0013-1111-2222-3333-444444444444', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 0.65, '{"technical_skills": 0.26, "experience": 0.20, "education": 0.11, "cultural_fit": 0.08}', 'AHP', CURRENT_TIMESTAMP - INTERVAL '5 hours', CURRENT_TIMESTAMP - INTERVAL '5 hours'),
    ('score014-1111-2222-3333-444444444444', 'cand0014-1111-2222-3333-444444444444', 'b2c3d4e5-f6g7-8901-bcde-f23456789012', 0.81, '{"product_experience": 0.28, "analytical_skills": 0.24, "leadership": 0.20, "domain_knowledge": 0.09}', 'AHP', CURRENT_TIMESTAMP - INTERVAL '6 hours', CURRENT_TIMESTAMP - INTERVAL '6 hours'),
    ('score015-1111-2222-3333-444444444444', 'cand0015-1111-2222-3333-444444444444', 'c3d4e5f6-g7h8-9012-cdef-345678901234', 0.86, '{"design_skills": 0.34, "user_research": 0.26, "portfolio": 0.17, "collaboration": 0.09}', 'AHP', CURRENT_TIMESTAMP - INTERVAL '10 minutes', CURRENT_TIMESTAMP - INTERVAL '10 minutes')
ON CONFLICT (id) DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_candidate_scores_job_profile ON candidate_scores(job_profile_id);
CREATE INDEX IF NOT EXISTS idx_candidate_scores_candidate ON candidate_scores(candidate_id);
CREATE INDEX IF NOT EXISTS idx_candidate_scores_overall_score ON candidate_scores(overall_score DESC);
CREATE INDEX IF NOT EXISTS idx_candidate_scores_calculated_at ON candidate_scores(calculated_at DESC);

-- Create composite index for pagination and filtering
CREATE INDEX IF NOT EXISTS idx_candidate_scores_composite ON candidate_scores(job_profile_id, overall_score DESC, calculated_at DESC);

COMMIT;
