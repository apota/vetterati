-- Vetterati ATS Database Initialization Script
-- This script sets up the basic database structure for the Vetterati ATS

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create basic schema structure
-- Note: Entity Framework migrations will handle the detailed table creation
-- This script ensures the database is ready for EF migrations

-- Create a basic health check function
CREATE OR REPLACE FUNCTION health_check() 
RETURNS TEXT AS $$
BEGIN
    RETURN 'Database is healthy at ' || NOW()::TEXT;
END;
$$ LANGUAGE plpgsql;

-- Create basic tables that EF expects to exist
CREATE TABLE IF NOT EXISTS "__EFMigrationsHistory" (
    "MigrationId" character varying(150) NOT NULL,
    "ProductVersion" character varying(32) NOT NULL,
    CONSTRAINT "PK___EFMigrationsHistory" PRIMARY KEY ("MigrationId")
);

-- Log initialization
INSERT INTO "__EFMigrationsHistory" ("MigrationId", "ProductVersion")
VALUES ('00000000000000_InitScript', '8.0.0')
ON CONFLICT DO NOTHING;

COMMENT ON DATABASE vetterati_ats IS 'Vetterati ATS Database - Initialized for Docker';

-- Create schema for auth service tables
-- These will be created properly by EF migrations, but this ensures basic structure

SELECT 'Database initialized successfully for Vetterati ATS' AS status;
