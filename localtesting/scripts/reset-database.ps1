#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Reset the database to a clean state

.DESCRIPTION
    This script stops the database, removes the volume, and starts it fresh

.EXAMPLE
    .\reset-database.ps1
#>

Write-Host "🗃️  Resetting database to clean state..." -ForegroundColor Yellow

# Navigate to the localtesting directory
Set-Location $PSScriptRoot\..

# Stop all services
Write-Host "Stopping all services..." -ForegroundColor Yellow
docker-compose -f docker-compose.infrastructure.yml down
docker-compose -f docker-compose.services.yml down

# Remove database volume
Write-Host "Removing database volume..." -ForegroundColor Yellow
docker volume rm localtesting_postgres_data 2>$null
docker volume rm localtesting_elasticsearch_data 2>$null

# Start infrastructure again
Write-Host "Starting fresh infrastructure..." -ForegroundColor Yellow
& .\scripts\start-infrastructure.ps1

Write-Host "✅ Database reset complete!" -ForegroundColor Green
