#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start the core infrastructure services for local development

.DESCRIPTION
    This script starts PostgreSQL, Redis, Elasticsearch, RabbitMQ, and LocalStack
    These services are required for all development work

.EXAMPLE
    .\start-infrastructure.ps1
#>

Write-Host "🚀 Starting infrastructure services..." -ForegroundColor Green

# Navigate to the localtesting directory
Set-Location $PSScriptRoot\..

# Start infrastructure services
docker-compose -f docker-compose.infrastructure.yml up -d

Write-Host "⏳ Waiting for services to be healthy..." -ForegroundColor Yellow

# Wait for services to be ready
$maxAttempts = 30
$attempt = 0

do {
    $attempt++
    Write-Host "Checking service health... (Attempt $attempt/$maxAttempts)" -ForegroundColor Cyan
    
    # Check if all services are healthy
    $healthyServices = docker-compose -f docker-compose.infrastructure.yml ps --format json | ConvertFrom-Json | Where-Object { $_.Health -eq "healthy" }
    $totalServices = docker-compose -f docker-compose.infrastructure.yml ps --format json | ConvertFrom-Json
    
    if ($healthyServices.Count -eq $totalServices.Count) {
        Write-Host "✅ All infrastructure services are healthy!" -ForegroundColor Green
        break
    }
    
    Start-Sleep -Seconds 5
    
} while ($attempt -lt $maxAttempts)

if ($attempt -eq $maxAttempts) {
    Write-Host "⚠️  Some services may not be ready yet. Check with 'docker-compose -f docker-compose.infrastructure.yml ps'" -ForegroundColor Yellow
}

Write-Host "🎯 Infrastructure services started successfully!" -ForegroundColor Green
Write-Host "📊 Access services at:" -ForegroundColor Blue
Write-Host "  - PostgreSQL: localhost:5432" -ForegroundColor White
Write-Host "  - Redis: localhost:6379" -ForegroundColor White
Write-Host "  - Elasticsearch: localhost:9200" -ForegroundColor White
Write-Host "  - RabbitMQ Management: localhost:15672" -ForegroundColor White
Write-Host "  - LocalStack: localhost:4566" -ForegroundColor White
