#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start a specific service for local development

.DESCRIPTION
    This script starts the infrastructure services, dependencies, and allows running a specific service locally

.PARAMETER ServiceName
    The name of the service to develop (e.g., resume-service, job-service, etc.)

.PARAMETER RunLocal
    If specified, runs the service locally instead of in Docker

.EXAMPLE
    .\start-service-dev.ps1 -ServiceName "resume-service"
    .\start-service-dev.ps1 -ServiceName "resume-service" -RunLocal
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ServiceName,
    
    [switch]$RunLocal = $false,
    
    [switch]$SkipInfrastructure = $false
)

$validServices = @(
    "auth-service",
    "resume-service", 
    "ahp-service",
    "workflow-service",
    "analytics-service",
    "job-service",
    "candidate-service",
    "notification-service",
    "api-gateway"
)

if ($ServiceName -notin $validServices) {
    Write-Host "❌ Invalid service name. Valid services are:" -ForegroundColor Red
    $validServices | ForEach-Object { Write-Host "  - $_" -ForegroundColor White }
    exit 1
}

Write-Host "🔧 Starting development environment for $ServiceName..." -ForegroundColor Green

# Navigate to the localtesting directory
Set-Location $PSScriptRoot\..

# Start infrastructure if not skipped
if (-not $SkipInfrastructure) {
    Write-Host "Starting infrastructure services..." -ForegroundColor Yellow
    & .\scripts\start-infrastructure.ps1
}

# Define service dependencies
$dependencies = @{
    "auth-service" = @()
    "resume-service" = @("auth-service")
    "ahp-service" = @("auth-service")
    "workflow-service" = @("auth-service")
    "analytics-service" = @("auth-service")
    "job-service" = @("auth-service")
    "candidate-service" = @("auth-service")
    "notification-service" = @("auth-service")
    "api-gateway" = @("auth-service")
}

# Start dependencies
$deps = $dependencies[$ServiceName]
if ($deps.Count -gt 0) {
    Write-Host "Starting dependencies: $($deps -join ', ')..." -ForegroundColor Yellow
    docker-compose -f docker-compose.services.yml up -d $deps
}

if ($RunLocal) {
    Write-Host "🏃 Running $ServiceName locally..." -ForegroundColor Green
    
    # Navigate to service directory
    $servicePath = "..\src\services\$ServiceName"
    if (-not (Test-Path $servicePath)) {
        Write-Host "❌ Service directory not found: $servicePath" -ForegroundColor Red
        exit 1
    }
    
    Set-Location $servicePath
    
    # Check service type and run accordingly
    if (Test-Path "requirements.txt") {
        # Python service
        Write-Host "🐍 Starting Python service..." -ForegroundColor Blue
        
        # Check if virtual environment exists
        if (-not (Test-Path ".venv")) {
            Write-Host "Creating virtual environment..." -ForegroundColor Yellow
            python -m venv .venv
        }
        
        # Activate virtual environment
        & .\.venv\Scripts\Activate.ps1
        
        # Install dependencies
        Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
        pip install -r requirements.txt
        
        # Create local environment file
        $envContent = @"
DATABASE_URL=postgresql://ats_user:ats_password@localhost:5432/vetterati_ats
REDIS_URL=redis://localhost:6379
ELASTICSEARCH_URL=http://localhost:9200
RABBITMQ_URL=amqp://ats_user:ats_password@localhost:5672
AWS_ENDPOINT_URL=http://localhost:4566
AWS_DEFAULT_REGION=us-east-1
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
S3_BUCKET_NAME=vetterati-resumes
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:000000000000:vetterati-notifications
SQS_QUEUE_URL=http://localhost:4566/000000000000/vetterati-notifications
"@
        
        $envContent | Out-File -FilePath ".env.local" -Encoding utf8
        
        Write-Host "🚀 Starting Python service with auto-reload..." -ForegroundColor Green
        python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
        
    } elseif (Test-Path "*.csproj") {
        # .NET service
        Write-Host "⚙️  Starting .NET service..." -ForegroundColor Blue
        
        # Set environment variables
        $env:ASPNETCORE_ENVIRONMENT = "Development"
        $env:ConnectionStrings__DefaultConnection = "Host=localhost;Database=vetterati_ats;Username=ats_user;Password=ats_password"
        $env:ConnectionStrings__Redis = "localhost:6379"
        $env:Jwt__SecretKey = "your-super-secret-jwt-key-for-docker-that-is-at-least-32-characters-long-and-secure"
        $env:Jwt__Issuer = "vetterati-ats"
        $env:Jwt__Audience = "vetterati-ats"
        
        Write-Host "🚀 Starting .NET service with hot reload..." -ForegroundColor Green
        dotnet watch run
    } else {
        Write-Host "❌ Unknown service type for $ServiceName" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "🐳 Running $ServiceName in Docker..." -ForegroundColor Green
    docker-compose -f docker-compose.services.yml up $ServiceName
}

Write-Host "✅ Development environment for $ServiceName is ready!" -ForegroundColor Green
