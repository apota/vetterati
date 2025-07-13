#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Stop all local development services

.DESCRIPTION
    This script stops all running Docker containers for local development

.EXAMPLE
    .\stop-all.ps1
#>

Write-Host "🛑 Stopping all development services..." -ForegroundColor Yellow

# Navigate to the localtesting directory
Set-Location $PSScriptRoot\..

# Stop all services
Write-Host "Stopping application services..." -ForegroundColor Yellow
docker-compose -f docker-compose.services.yml down

Write-Host "Stopping infrastructure services..." -ForegroundColor Yellow
docker-compose -f docker-compose.infrastructure.yml down

Write-Host "Stopping full stack (if running)..." -ForegroundColor Yellow
docker-compose -f docker-compose.full.yml down

Write-Host "✅ All services stopped!" -ForegroundColor Green
