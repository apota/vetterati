-- Insert sample candidates into candidate_profiles table
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
    '["Python", "JavaScript", "React", "Node.js", "SQL"]',
    '{"current_role": "Senior Software Engineer", "company": "Tech Corp", "duration": "3 years"}',
    '{"degree": "Bachelor of Science in Computer Science", "university": "State University", "graduation_year": 2018}',
    '["AWS Certified Developer", "Certified Scrum Master"]',
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
    '["Java", "Spring Boot", "Angular", "Docker", "Kubernetes"]',
    '{"current_role": "Full Stack Developer", "company": "StartupXYZ", "duration": "2 years"}',
    '{"degree": "Master of Science in Software Engineering", "university": "Tech University", "graduation_year": 2020}',
    '["Oracle Certified Professional", "Docker Certified Associate"]',
    3,
    'Full Stack Developer',
    'Available immediately',
    85000,
    NOW(),
    NOW()
),
(
    gen_random_uuid(),
    'Michael',
    'Johnson',
    'michael.johnson@example.com',
    '+1-555-0103',
    'Austin, TX',
    '["C#", ".NET Core", "Azure", "SQL Server", "DevOps"]',
    '{"current_role": "DevOps Engineer", "company": "Enterprise Solutions", "duration": "4 years"}',
    '{"degree": "Bachelor of Science in Information Technology", "university": "Tech Institute", "graduation_year": 2017}',
    '["Microsoft Certified Azure Developer", "ITIL Foundation"]',
    6,
    'DevOps Engineer',
    'Available in 1 month',
    95000,
    NOW(),
    NOW()
),
(
    gen_random_uuid(),
    'Sarah',
    'Williams',
    'sarah.williams@example.com',
    '+1-555-0104',
    'Chicago, IL',
    '["Python", "Django", "PostgreSQL", "Redis", "AWS"]',
    '{"current_role": "Backend Developer", "company": "DataCorp", "duration": "3 years"}',
    '{"degree": "Bachelor of Science in Computer Science", "university": "Midwest University", "graduation_year": 2019}',
    '["AWS Solutions Architect", "Python Institute Certified"]',
    4,
    'Backend Developer',
    'Available in 3 weeks',
    80000,
    NOW(),
    NOW()
),
(
    gen_random_uuid(),
    'David',
    'Brown',
    'david.brown@example.com',
    '+1-555-0105',
    'Seattle, WA',
    '["JavaScript", "TypeScript", "Vue.js", "Node.js", "MongoDB"]',
    '{"current_role": "Frontend Developer", "company": "WebSolutions", "duration": "2.5 years"}',
    '{"degree": "Bachelor of Science in Web Development", "university": "Pacific University", "graduation_year": 2020}',
    '["Google Cloud Professional", "MongoDB Certified Developer"]',
    3,
    'Frontend Developer',
    'Available immediately',
    70000,
    NOW(),
    NOW()
);

-- Insert sample positions
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
    '["5+ years experience", "React", "Node.js", "PostgreSQL", "AWS"]',
    'We are seeking a Senior Full Stack Developer to join our growing team. You will work on cutting-edge applications using modern technologies.',
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
    '["3+ years DevOps experience", "Docker", "Kubernetes", "AWS", "CI/CD"]',
    'Join our DevOps team to help build and maintain our cloud infrastructure. Experience with containerization and orchestration required.',
    'Full-time',
    'Mid-level',
    NOW(),
    NOW() + INTERVAL '45 days'
),
(
    gen_random_uuid(),
    'Backend Developer',
    'DataFlow Systems',
    'Austin, TX',
    '70000-100000',
    '["3+ years Python experience", "Django", "PostgreSQL", "Redis", "API development"]',
    'We need a Backend Developer to work on our data processing applications. Strong Python and database skills required.',
    'Full-time',
    'Mid-level',
    NOW(),
    NOW() + INTERVAL '60 days'
),
(
    gen_random_uuid(),
    'Frontend Developer',
    'WebInnovate',
    'Chicago, IL',
    '60000-90000',
    '["2+ years frontend experience", "Vue.js", "TypeScript", "CSS", "Responsive design"]',
    'Join our frontend team to create beautiful and responsive user interfaces. Vue.js experience preferred.',
    'Full-time',
    'Junior',
    NOW(),
    NOW() + INTERVAL '25 days'
),
(
    gen_random_uuid(),
    'Cloud Solutions Architect',
    'Enterprise Cloud',
    'Seattle, WA',
    '120000-180000',
    '["7+ years experience", "AWS", "Azure", "System design", "Architecture patterns"]',
    'We are looking for a Cloud Solutions Architect to design and implement scalable cloud solutions for our enterprise clients.',
    'Full-time',
    'Senior',
    NOW(),
    NOW() + INTERVAL '90 days'
);
