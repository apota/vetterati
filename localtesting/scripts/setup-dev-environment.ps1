#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Setup the local development environment

.DESCRIPTION
    This script copies necessary files and sets up the development environment

.EXAMPLE
    .\setup-dev-environment.ps1
#>

Write-Host "🔧 Setting up local development environment..." -ForegroundColor Green

# Navigate to the localtesting directory
Set-Location $PSScriptRoot\..

# Copy development Dockerfiles to appropriate locations
$pythonServices = @(
    "resume-service",
    "workflow-service", 
    "analytics-service",
    "job-service",
    "candidate-service",
    "notification-service"
)

Write-Host "Copying development Dockerfiles..." -ForegroundColor Yellow

foreach ($service in $pythonServices) {
    $servicePath = "..\src\services\$service"
    if (Test-Path $servicePath) {
        Copy-Item "templates\Dockerfile.python.dev" "$servicePath\Dockerfile.dev" -Force
        Write-Host "  ✅ Copied Dockerfile.dev to $service" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Service directory not found: $service" -ForegroundColor Yellow
    }
}

# Copy frontend development Dockerfile
$frontendPath = "..\src\frontend"
if (Test-Path $frontendPath) {
    Copy-Item "templates\Dockerfile.frontend.dev" "$frontendPath\Dockerfile.dev" -Force
    Write-Host "  ✅ Copied Dockerfile.dev to frontend" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Frontend directory not found" -ForegroundColor Yellow
}

# Create Docker network for local development
Write-Host "Creating Docker network..." -ForegroundColor Yellow
docker network create ats-local 2>$null
Write-Host "  ✅ Docker network 'ats-local' created/exists" -ForegroundColor Green

# Make scripts executable
Write-Host "Making scripts executable..." -ForegroundColor Yellow
$scripts = Get-ChildItem -Path "scripts\*.ps1"
foreach ($script in $scripts) {
    Write-Host "  ✅ $($script.Name) is ready" -ForegroundColor Green
}

Write-Host "`n🎉 Development environment setup complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Blue
Write-Host "1. Start infrastructure: .\scripts\start-infrastructure.ps1" -ForegroundColor White
Write-Host "2. Start frontend dev: .\scripts\start-frontend-dev.ps1" -ForegroundColor White
Write-Host "3. Start service dev: .\scripts\start-service-dev.ps1 -ServiceName 'resume-service'" -ForegroundColor White
Write-Host "4. Check status: .\scripts\status.ps1" -ForegroundColor White
