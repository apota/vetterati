-- Database initialization script for Vetterati ATS
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS ats_core;
CREATE SCHEMA IF NOT EXISTS ats_analytics;
CREATE SCHEMA IF NOT EXISTS ats_audit;

-- Users and Authentication
CREATE TABLE ats_core.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sso_provider VARCHAR(50),
    sso_id VARCHAR(255),
    roles JSONB NOT NULL DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ,
    preferences JSONB DEFAULT '{}'
);

-- Organizations
CREATE TABLE ats_core.organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255),
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User Organization Mapping
CREATE TABLE ats_core.user_organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES ats_core.users(id),
    organization_id UUID REFERENCES ats_core.organizations(id),
    role VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, organization_id)
);

-- Jobs and Positions
CREATE TABLE ats_core.jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES ats_core.organizations(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    department VARCHAR(100),
    location VARCHAR(255),
    job_level VARCHAR(50),
    employment_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'draft',
    created_by UUID REFERENCES ats_core.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    posted_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    requirements JSONB DEFAULT '{}',
    benefits JSONB DEFAULT '{}'
);

-- Candidates
CREATE TABLE ats_core.candidates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES ats_core.organizations(id),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    location JSONB,
    linkedin_url VARCHAR(500),
    portfolio_url VARCHAR(500),
    experience JSONB NOT NULL DEFAULT '[]',
    education JSONB NOT NULL DEFAULT '[]',
    skills JSONB NOT NULL DEFAULT '{}',
    career_metrics JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Resume Files
CREATE TABLE ats_core.resume_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID REFERENCES ats_core.candidates(id),
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size BIGINT,
    storage_path VARCHAR(500),
    upload_source VARCHAR(100),
    upload_date TIMESTAMPTZ DEFAULT NOW(),
    processing_status VARCHAR(50) DEFAULT 'pending',
    parsing_results JSONB DEFAULT '{}',
    quality_score DECIMAL(3,2)
);

-- AHP Hierarchies
CREATE TABLE ats_core.ahp_hierarchies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES ats_core.jobs(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    hierarchy JSONB NOT NULL,
    pairwise_matrices JSONB NOT NULL,
    consistency_ratios JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Ideal Candidate Profiles
CREATE TABLE ats_core.ideal_candidate_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES ats_core.jobs(id),
    ahp_hierarchy_id UUID REFERENCES ats_core.ahp_hierarchies(id),
    name VARCHAR(255) NOT NULL,
    archetype VARCHAR(100),
    weight INTEGER DEFAULT 100,
    target_values JSONB NOT NULL DEFAULT '{}',
    tolerances JSONB DEFAULT '{}',
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Candidate Scoring Results
CREATE TABLE ats_core.candidate_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID REFERENCES ats_core.candidates(id),
    job_id UUID REFERENCES ats_core.jobs(id),
    ahp_hierarchy_id UUID REFERENCES ats_core.ahp_hierarchies(id),
    overall_score DECIMAL(5,2),
    profile_matches JSONB DEFAULT '[]',
    attribute_scores JSONB DEFAULT '[]',
    explanation JSONB DEFAULT '{}',
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Workflow Definitions
CREATE TABLE ats_core.workflow_definitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES ats_core.organizations(id),
    name VARCHAR(255) NOT NULL,
    version VARCHAR(20) DEFAULT '1.0',
    stages JSONB NOT NULL,
    notifications JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Candidate Workflow Instances
CREATE TABLE ats_core.candidate_workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID REFERENCES ats_core.candidates(id),
    job_id UUID REFERENCES ats_core.jobs(id),
    workflow_definition_id UUID REFERENCES ats_core.workflow_definitions(id),
    current_stage VARCHAR(100),
    status VARCHAR(50) DEFAULT 'in_progress',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    stage_history JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}'
);

-- Interviews
CREATE TABLE ats_core.interviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_workflow_id UUID REFERENCES ats_core.candidate_workflows(id),
    candidate_id UUID REFERENCES ats_core.candidates(id),
    job_id UUID REFERENCES ats_core.jobs(id),
    stage_id VARCHAR(100),
    title VARCHAR(255),
    description TEXT,
    type VARCHAR(50), -- phone, video, onsite, panel
    status VARCHAR(50) DEFAULT 'scheduled',
    scheduling JSONB DEFAULT '{}',
    participants JSONB DEFAULT '{}',
    content JSONB DEFAULT '{}',
    evaluation JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Analytics Events (Partitioned by time)
CREATE TABLE ats_analytics.events (
    event_id UUID DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    user_id UUID,
    entity_type VARCHAR(50),
    entity_id UUID,
    action VARCHAR(100),
    context JSONB DEFAULT '{}',
    payload JSONB DEFAULT '{}',
    compliance_flags JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Create partitions for current and next month
CREATE TABLE ats_analytics.events_2025_07 
PARTITION OF ats_analytics.events 
FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');

CREATE TABLE ats_analytics.events_2025_08 
PARTITION OF ats_analytics.events 
FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');

-- Audit Trail
CREATE TABLE ats_audit.audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_users_email ON ats_core.users(email);
CREATE INDEX idx_users_sso ON ats_core.users(sso_provider, sso_id);
CREATE INDEX idx_jobs_org_status ON ats_core.jobs(organization_id, status);
CREATE INDEX idx_candidates_org ON ats_core.candidates(organization_id);
CREATE INDEX idx_candidates_email ON ats_core.candidates(email);
CREATE INDEX idx_candidate_scores_job ON ats_core.candidate_scores(job_id, overall_score DESC);
CREATE INDEX idx_events_type_timestamp ON ats_analytics.events(event_type, timestamp);
CREATE INDEX idx_events_entity ON ats_analytics.events(entity_type, entity_id);
CREATE INDEX idx_workflows_candidate_job ON ats_core.candidate_workflows(candidate_id, job_id);

-- Full text search indexes
CREATE INDEX idx_candidates_name_search ON ats_core.candidates USING gin(to_tsvector('english', coalesce(first_name, '') || ' ' || coalesce(last_name, '')));

-- Insert default organization
INSERT INTO ats_core.organizations (id, name, domain) 
VALUES ('00000000-0000-0000-0000-000000000001', 'Default Organization', 'localhost');

-- Insert default admin user
INSERT INTO ats_core.users (id, email, name, roles) 
VALUES ('00000000-0000-0000-0000-000000000001', 'admin@vetterati.com', 'System Admin', '["admin", "recruiter", "hiring_manager"]');

INSERT INTO ats_core.user_organizations (user_id, organization_id, role) 
VALUES ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'admin');
