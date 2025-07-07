# Test script for new Vetterati ATS services (PowerShell)
# This script validates that the new microservices are working correctly

param(
    [Parameter(Position=0)]
    [ValidateSet("start", "test", "stop")]
    [string]$Command
)

function Write-Status {
    param([string]$Message)
    Write-Host "[TEST] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[PASS] $Message" -ForegroundColor Green
}

function Write-TestError {
    param([string]$Message)
    Write-Host "[FAIL] $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

# Test service health
function Test-ServiceHealth {
    param(
        [string]$ServiceName,
        [int]$Port
    )
    
    Write-Status "Testing $ServiceName health..."
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$Port/health" -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Success "$ServiceName is healthy"
            return $true
        }
    }
    catch {
        Write-TestError "$ServiceName health check failed"
        return $false
    }
}

# Test service API
function Test-ServiceAPI {
    param(
        [string]$ServiceName,
        [int]$Port,
        [string]$Endpoint
    )
    
    Write-Status "Testing $ServiceName API: $Endpoint"
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$Port$Endpoint" -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 400) {
            Write-Success "$ServiceName API $Endpoint responded with $($response.StatusCode)"
            return $true
        }
        else {
            Write-TestError "$ServiceName API $Endpoint failed with $($response.StatusCode)"
            return $false
        }
    }
    catch {
        Write-TestError "$ServiceName API $Endpoint failed: $($_.Exception.Message)"
        return $false
    }
}

# Test job service
function Test-JobService {
    Write-Status "Testing Job Service..."
    
    if (-not (Test-ServiceHealth "Job Service" 8004)) { return $false }
    
    $endpoints = @("/api/v1/jobs", "/api/v1/templates", "/api/v1/stats", "/docs")
    foreach ($endpoint in $endpoints) {
        if (-not (Test-ServiceAPI "Job Service" 8004 $endpoint)) { return $false }
    }
    
    Write-Success "Job Service tests passed"
    return $true
}

# Test candidate service
function Test-CandidateService {
    Write-Status "Testing Candidate Service..."
    
    if (-not (Test-ServiceHealth "Candidate Service" 8005)) { return $false }
    
    $endpoints = @(
        "/api/v1/candidates", "/api/v1/applications", "/api/v1/resumes",
        "/api/v1/experiences", "/api/v1/educations", "/api/v1/skills",
        "/api/v1/stats", "/docs"
    )
    
    foreach ($endpoint in $endpoints) {
        if (-not (Test-ServiceAPI "Candidate Service" 8005 $endpoint)) { return $false }
    }
    
    Write-Success "Candidate Service tests passed"
    return $true
}

# Test notification service
function Test-NotificationService {
    Write-Status "Testing Notification Service..."
    
    if (-not (Test-ServiceHealth "Notification Service" 8006)) { return $false }
    
    $endpoints = @("/api/v1/templates", "/api/v1/notifications", "/api/v1/stats", "/docs")
    foreach ($endpoint in $endpoints) {
        if (-not (Test-ServiceAPI "Notification Service" 8006 $endpoint)) { return $false }
    }
    
    Write-Success "Notification Service tests passed"
    return $true
}

# Test database connectivity
function Test-Database {
    Write-Status "Testing database connectivity..."
    
    # Test PostgreSQL
    try {
        docker-compose -f docker-compose.new-services.yml exec -T postgres pg_isready -U ats_user -d vetterati_ats | Out-Null
        Write-Success "PostgreSQL is accessible"
    }
    catch {
        Write-TestError "PostgreSQL is not accessible"
        return $false
    }
    
    # Test Redis
    try {
        $redisResponse = docker-compose -f docker-compose.new-services.yml exec -T redis redis-cli ping
        if ($redisResponse -match "PONG") {
            Write-Success "Redis is accessible"
        }
        else {
            Write-TestError "Redis is not accessible"
            return $false
        }
    }
    catch {
        Write-TestError "Redis is not accessible"
        return $false
    }
    
    # Test Elasticsearch
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:9200" -TimeoutSec 10 -UseBasicParsing
        Write-Success "Elasticsearch is accessible"
    }
    catch {
        Write-TestError "Elasticsearch is not accessible"
        return $false
    }
    
    # Test RabbitMQ
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:15672" -TimeoutSec 10 -UseBasicParsing
        Write-Success "RabbitMQ Management is accessible"
    }
    catch {
        Write-TestError "RabbitMQ Management is not accessible"
        return $false
    }
    
    return $true
}

# Create sample data
function New-SampleData {
    Write-Status "Creating sample data..."
    
    try {
        # Create a job template
        $jobTemplateBody = @{
            name = "Test Software Engineer Template"
            description = "Test template for software engineer positions"
            title = "Software Engineer"
            description_template = "We are seeking a {{experience_level}} Software Engineer."
            department = "Engineering"
            employment_type = "full_time"
            required_skills = @("Programming", "Testing")
            is_active = $true
        } | ConvertTo-Json
        
        $jobTemplate = Invoke-RestMethod -Uri "http://localhost:8004/api/v1/templates" -Method Post -Body $jobTemplateBody -ContentType "application/json"
        Write-Success "Job template created successfully"
        
        # Create a job
        $jobBody = @{
            title = "Senior Software Engineer"
            description = "We are looking for a senior software engineer..."
            department = "Engineering"
            location = "San Francisco, CA"
            employment_type = "full_time"
            experience_level = "senior"
            status = "active"
            required_skills = @("Python", "JavaScript", "SQL")
            salary_range_min = 120000
            salary_range_max = 180000
        } | ConvertTo-Json
        
        $job = Invoke-RestMethod -Uri "http://localhost:8004/api/v1/jobs" -Method Post -Body $jobBody -ContentType "application/json"
        Write-Success "Job created successfully"
        
        # Create a candidate
        $candidateBody = @{
            first_name = "John"
            last_name = "Doe"
            email = "john.doe@example.com"
            phone = "+1-555-0123"
            location = "San Francisco, CA"
            status = "active"
        } | ConvertTo-Json
        
        $candidate = Invoke-RestMethod -Uri "http://localhost:8005/api/v1/candidates" -Method Post -Body $candidateBody -ContentType "application/json"
        Write-Success "Candidate created successfully"
        
        # Create a notification template
        $notificationTemplateBody = @{
            name = "Test Welcome Email"
            description = "Test welcome email template"
            channel = "email"
            subject_template = "Welcome {{candidate_name}}!"
            body_template = "Dear {{candidate_name}}, welcome to our system!"
            is_active = $true
        } | ConvertTo-Json
        
        $notificationTemplate = Invoke-RestMethod -Uri "http://localhost:8006/api/v1/templates" -Method Post -Body $notificationTemplateBody -ContentType "application/json"
        Write-Success "Notification template created successfully"
        
        Write-Success "Sample data creation completed"
        return $true
    }
    catch {
        Write-Warning "Sample data creation had issues: $($_.Exception.Message)"
        return $false
    }
}

# Main test execution
function Start-Tests {
    Write-Status "Starting service tests..."
    Write-Host ""
    
    # Wait for services to be ready
    Write-Status "Waiting for services to be ready..."
    Start-Sleep -Seconds 30
    
    # Test infrastructure
    if (-not (Test-Database)) { 
        Write-TestError "Database tests failed"
        return 
    }
    Write-Host ""
    
    # Test services
    if (-not (Test-JobService)) { 
        Write-TestError "Job Service tests failed"
        return 
    }
    Write-Host ""
    
    if (-not (Test-CandidateService)) { 
        Write-TestError "Candidate Service tests failed"
        return 
    }
    Write-Host ""
    
    if (-not (Test-NotificationService)) { 
        Write-TestError "Notification Service tests failed"
        return 
    }
    Write-Host ""
    
    # Create sample data
    New-SampleData | Out-Null
    Write-Host ""
    
    Write-Success "All tests completed successfully!"
    Write-Host ""
    Write-Status "Service URLs:"
    Write-Host "  📊 Job Service:         http://localhost:8004/docs"
    Write-Host "  👥 Candidate Service:   http://localhost:8005/docs"
    Write-Host "  📨 Notification Service: http://localhost:8006/docs"
    Write-Host "  🗄️  PostgreSQL:          http://localhost:5432"
    Write-Host "  🔍 Elasticsearch:       http://localhost:9200"
    Write-Host "  🐰 RabbitMQ:            http://localhost:15672"
}

# Main execution
switch ($Command) {
    "start" {
        Write-Status "Starting new services..."
        docker-compose -f docker-compose.new-services.yml up -d
        Start-Tests
    }
    "test" {
        Start-Tests
    }
    "stop" {
        Write-Status "Stopping services..."
        docker-compose -f docker-compose.new-services.yml down
        Write-Success "Services stopped"
    }
    default {
        Write-Host "Usage: .\test-services.ps1 {start|test|stop}"
        Write-Host ""
        Write-Host "Commands:"
        Write-Host "  start  - Start services and run tests"
        Write-Host "  test   - Run tests on running services"
        Write-Host "  stop   - Stop all services"
    }
}
