#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Show the status of all development services

.DESCRIPTION
    This script shows the current status of all Docker containers

.EXAMPLE
    .\status.ps1
#>

Write-Host "📊 Development Services Status" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Gray

# Navigate to the localtesting directory
Set-Location $PSScriptRoot\..

Write-Host "Infrastructure Services:" -ForegroundColor Blue
docker-compose -f docker-compose.infrastructure.yml ps

Write-Host "`nApplication Services:" -ForegroundColor Blue
docker-compose -f docker-compose.services.yml ps

Write-Host "`nPort Usage:" -ForegroundColor Blue
Write-Host "Infrastructure:" -ForegroundColor Cyan
Write-Host "  - PostgreSQL: 5432" -ForegroundColor White
Write-Host "  - Redis: 6379" -ForegroundColor White
Write-Host "  - Elasticsearch: 9200" -ForegroundColor White
Write-Host "  - RabbitMQ: 5672 (AMQP), 15672 (Management)" -ForegroundColor White
Write-Host "  - LocalStack: 4566" -ForegroundColor White

Write-Host "`nApplication:" -ForegroundColor Cyan
Write-Host "  - API Gateway: 5000" -ForegroundColor White
Write-Host "  - Auth Service: 5001" -ForegroundColor White
Write-Host "  - Resume Service: 8001" -ForegroundColor White
Write-Host "  - AHP Service: 5002" -ForegroundColor White
Write-Host "  - Workflow Service: 8002" -ForegroundColor White
Write-Host "  - Analytics Service: 8003" -ForegroundColor White
Write-Host "  - Job Service: 8004" -ForegroundColor White
Write-Host "  - Candidate Service: 8005" -ForegroundColor White
Write-Host "  - Notification Service: 8006" -ForegroundColor White
Write-Host "  - Frontend: 3000" -ForegroundColor White
