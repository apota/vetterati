#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start the frontend development environment

.DESCRIPTION
    This script starts the infrastructure services, API Gateway, and runs the frontend locally with hot reload

.EXAMPLE
    .\start-frontend-dev.ps1
#>

param(
    [switch]$SkipInfrastructure = $false
)

Write-Host "🎨 Starting frontend development environment..." -ForegroundColor Green

# Navigate to the localtesting directory
Set-Location $PSScriptRoot\..

# Start infrastructure if not skipped
if (-not $SkipInfrastructure) {
    Write-Host "Starting infrastructure services..." -ForegroundColor Yellow
    & .\scripts\start-infrastructure.ps1
}

# Start API Gateway and Auth Service
Write-Host "Starting API Gateway and Auth Service..." -ForegroundColor Yellow
docker-compose -f docker-compose.services.yml up -d api-gateway auth-service

# Navigate to frontend directory
Set-Location ..\src\frontend

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
}

# Create local environment file
$envContent = @"
REACT_APP_API_URL=http://localhost:5000
REACT_APP_ENVIRONMENT=local
"@

$envContent | Out-File -FilePath ".env.local" -Encoding utf8

Write-Host "🚀 Starting frontend development server..." -ForegroundColor Green
Write-Host "📱 Frontend will be available at: http://localhost:3000" -ForegroundColor Blue
Write-Host "🔗 API Gateway available at: http://localhost:5000" -ForegroundColor Blue
Write-Host "" -ForegroundColor White
Write-Host "Press Ctrl+C to stop the development server" -ForegroundColor Yellow

# Start the development server
npm start
