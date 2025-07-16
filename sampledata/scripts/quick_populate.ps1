Write-Host "Inserting sample candidate profiles..."
docker exec vetterati-postgres-1 psql -U ats_user -d vetterati_ats -c "
INSERT INTO candidate_profiles (
    id, first_name, last_name, email, phone, location, 
    skills, experience, education, certifications, 
    years_of_experience, current_position, availability, 
    preferred_salary, created_at, updated_at
) VALUES 
(
    gen_random_uuid(),
    'John',
    'Doe',
    'john.doe@example.com',
    '+1-555-0101',
    'New York, NY',
    '[\"Python\", \"JavaScript\", \"React\", \"Node.js\", \"SQL\"]',
    '{\"current_role\": \"Senior Software Engineer\", \"company\": \"Tech Corp\", \"duration\": \"3 years\"}',
    '{\"degree\": \"Bachelor of Science in Computer Science\", \"university\": \"State University\", \"graduation_year\": 2018}',
    '[\"AWS Certified Developer\", \"Certified Scrum Master\"]',
    5,
    'Senior Software Engineer',
    'Available in 2 weeks',
    75000,
    NOW(),
    NOW()
),
(
    gen_random_uuid(),
    'Jane',
    'Smith',
    'jane.smith@example.com',
    '+1-555-0102',
    'San Francisco, CA',
    '[\"Java\", \"Spring Boot\", \"Angular\", \"Docker\", \"Kubernetes\"]',
    '{\"current_role\": \"Full Stack Developer\", \"company\": \"StartupXYZ\", \"duration\": \"2 years\"}',
    '{\"degree\": \"Master of Science in Software Engineering\", \"university\": \"Tech University\", \"graduation_year\": 2020}',
    '[\"Oracle Certified Professional\", \"Docker Certified Associate\"]',
    3,
    'Full Stack Developer',
    'Available immediately',
    85000,
    NOW(),
    NOW()
);"

Write-Host "Inserting sample position profiles..."
docker exec vetterati-postgres-1 psql -U ats_user -d vetterati_ats -c "
INSERT INTO position_profiles (
    id, title, company, location, salary_range, 
    requirements, description, employment_type, 
    experience_level, posted_at, expires_at
) VALUES 
(
    gen_random_uuid(),
    'Senior Full Stack Developer',
    'TechCorp Inc.',
    'New York, NY',
    '80000-120000',
    '[\"5+ years experience\", \"React\", \"Node.js\", \"PostgreSQL\", \"AWS\"]',
    'We are seeking a Senior Full Stack Developer to join our growing team.',
    'Full-time',
    'Senior',
    NOW(),
    NOW() + INTERVAL '30 days'
),
(
    gen_random_uuid(),
    'DevOps Engineer', 
    'CloudTech Solutions',
    'San Francisco, CA',
    '90000-140000',
    '[\"3+ years DevOps experience\", \"Docker\", \"Kubernetes\", \"AWS\", \"CI/CD\"]',
    'Join our DevOps team to help build and maintain our cloud infrastructure.',
    'Full-time',
    'Mid-level',
    NOW(),
    NOW() + INTERVAL '45 days'
);"

Write-Host "Inserting sample candidate matches..."
docker exec vetterati-postgres-1 psql -U ats_user -d vetterati_ats -c "
INSERT INTO candidate_matches (
    id, candidate_id, position_id, overall_score, match_percentage, 
    criteria_scores, score_breakdown, calculated_at, methodology, metadata
) VALUES 
(
    gen_random_uuid(),
    (SELECT id FROM candidate_profiles WHERE email = 'john.doe@example.com'),
    (SELECT id FROM position_profiles WHERE title = 'Senior Full Stack Developer'),
    0.85,
    85.5,
    '{\"technical_skills\": 0.9, \"experience\": 0.8, \"education\": 0.7}',
    '{\"technical_skills\": {\"score\": 0.9, \"weight\": 0.4}, \"experience\": {\"score\": 0.8, \"weight\": 0.3}, \"education\": {\"score\": 0.7, \"weight\": 0.3}}',
    NOW(),
    'AHP',
    '{\"processing_time\": 150, \"confidence\": 0.85}'
),
(
    gen_random_uuid(),
    (SELECT id FROM candidate_profiles WHERE email = 'jane.smith@example.com'),
    (SELECT id FROM position_profiles WHERE title = 'DevOps Engineer'),
    0.92,
    92.3,
    '{\"technical_skills\": 0.95, \"experience\": 0.9, \"education\": 0.9}',
    '{\"technical_skills\": {\"score\": 0.95, \"weight\": 0.4}, \"experience\": {\"score\": 0.9, \"weight\": 0.3}, \"education\": {\"score\": 0.9, \"weight\": 0.3}}',
    NOW(),
    'AHP',
    '{\"processing_time\": 180, \"confidence\": 0.92}'
);"

Write-Host "Sample data inserted successfully!"
