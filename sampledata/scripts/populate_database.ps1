# Execute SQL scripts to populate database with sample data

$ErrorActionPreference = "Stop"

Write-Host "Populating database with sample data..."

# Wait for PostgreSQL to be ready
Start-Sleep -Seconds 5

# Execute the SQL scripts
Write-Host "Inserting candidate and position profiles..."
docker exec vetterati-postgres-1 psql -U ats_user -d vetterati_ats -f /tmp/populate_profiles.sql

Write-Host "Inserting candidate matches..."
docker exec vetterati-postgres-1 psql -U ats_user -d vetterati_ats -f /tmp/populate_candidate_matches.sql

Write-Host "Sample data populated successfully!"

# Verify data was inserted
Write-Host "Verifying data insertion..."
docker exec vetterati-postgres-1 psql -U ats_user -d vetterati_ats -c "SELECT COUNT(*) as candidate_profiles_count FROM candidate_profiles;"
docker exec vetterati-postgres-1 psql -U ats_user -d vetterati_ats -c "SELECT COUNT(*) as position_profiles_count FROM position_profiles;"
docker exec vetterati-postgres-1 psql -U ats_user -d vetterati_ats -c "SELECT COUNT(*) as candidate_matches_count FROM candidate_matches;"
