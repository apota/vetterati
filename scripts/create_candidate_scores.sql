-- Create candidate_scores table if it doesn't exist
CREATE TABLE IF NOT EXISTS candidate_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL,
    job_profile_id UUID NOT NULL,
    overall_score DECIMAL(10,6) NOT NULL DEFAULT 0,
    score_breakdown JSONB,
    methodology VARCHAR(100) DEFAULT 'AHP',
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    scored_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create AHP criteria table if it doesn't exist
CREATE TABLE IF NOT EXISTS ahp_criteria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    weight DECIMAL(5,4) NOT NULL DEFAULT 0.25,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert default AHP criteria
INSERT INTO ahp_criteria (name, weight, description) VALUES
('experience', 0.35, 'Years of relevant experience'),
('skills', 0.30, 'Technical skills matching'),
('education', 0.20, 'Educational background'),
('culture_fit', 0.15, 'Cultural fit assessment')
ON CONFLICT DO NOTHING;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_candidate_scores_candidate_id ON candidate_scores(candidate_id);
CREATE INDEX IF NOT EXISTS idx_candidate_scores_job_profile_id ON candidate_scores(job_profile_id);
CREATE INDEX IF NOT EXISTS idx_candidate_scores_overall_score ON candidate_scores(overall_score DESC);
CREATE INDEX IF NOT EXISTS idx_candidate_scores_scored_at ON candidate_scores(scored_at DESC);

-- Insert sample data (assuming we have some candidates and jobs)
-- First, let's check if we have any candidates and jobs
DO $$
DECLARE
    candidate_count INTEGER;
    job_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO candidate_count FROM candidates;
    SELECT COUNT(*) INTO job_count FROM jobs;
    
    IF candidate_count > 0 AND job_count > 0 THEN
        -- Insert sample scores for existing candidates and jobs
        INSERT INTO candidate_scores (candidate_id, job_profile_id, overall_score, score_breakdown, methodology)
        SELECT 
            c.id as candidate_id,
            j.id as job_profile_id,
            ROUND((RANDOM() * 0.4 + 0.6)::NUMERIC, 6) as overall_score,
            jsonb_build_object(
                'experience', ROUND((RANDOM() * 0.3 + 0.7)::NUMERIC, 4),
                'skills', ROUND((RANDOM() * 0.3 + 0.7)::NUMERIC, 4),
                'education', ROUND((RANDOM() * 0.3 + 0.7)::NUMERIC, 4),
                'culture_fit', ROUND((RANDOM() * 0.3 + 0.7)::NUMERIC, 4)
            ) as score_breakdown,
            'AHP' as methodology
        FROM candidates c
        CROSS JOIN jobs j
        ORDER BY RANDOM()
        LIMIT 20;
    END IF;
END $$;
