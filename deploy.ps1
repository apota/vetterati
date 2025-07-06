# Vetterati ATS - Service Deployment Script (PowerShell)
# This script builds and deploys the new microservices on Windows

param(
    [Parameter(Position=0)]
    [ValidateSet("build", "deploy", "start", "stop", "restart", "status", "logs", "clean")]
    [string]$Command,
    
    [Parameter(Position=1)]
    [string]$ServiceName
)

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if Docker is running
function Test-Docker {
    Write-Status "Checking Docker..."
    try {
        docker info | Out-Null
        Write-Success "Docker is running"
        return $true
    }
    catch {
        Write-Error "Docker is not running. Please start Docker and try again."
        return $false
    }
}

# Build services
function Build-Services {
    Write-Status "Building microservices..."
    
    $services = @("job-service", "candidate-service", "notification-service")
    
    foreach ($service in $services) {
        Write-Status "Building $service..."
        
        $servicePath = "src\services\$service"
        if (Test-Path $servicePath) {
            Push-Location $servicePath
            
            try {
                docker build -t "vetterati-$service" .
                Write-Success "$service built successfully"
            }
            catch {
                Write-Error "Failed to build $service"
                Pop-Location
                exit 1
            }
            
            Pop-Location
        }
        else {
            Write-Warning "Service directory not found: $servicePath"
        }
    }
}

# Create network if it doesn't exist
function New-DockerNetwork {
    Write-Status "Creating Docker network..."
    
    $networkExists = docker network ls | Select-String "ats-network"
    if (-not $networkExists) {
        docker network create ats-network
        Write-Success "Created ats-network"
    }
    else {
        Write-Success "ats-network already exists"
    }
}

# Start infrastructure services
function Start-Infrastructure {
    Write-Status "Starting infrastructure services..."
    
    # Start only infrastructure services first
    docker-compose up -d postgres redis elasticsearch rabbitmq dynamodb
    
    Write-Status "Waiting for infrastructure services to be ready..."
    Start-Sleep -Seconds 10
    
    # Check if PostgreSQL is ready
    Write-Status "Waiting for PostgreSQL to be ready..."
    for ($i = 1; $i -le 30; $i++) {
        try {
            docker-compose exec -T postgres pg_isready -U ats_user -d vetterati_ats | Out-Null
            Write-Success "PostgreSQL is ready"
            break
        }
        catch {
            if ($i -eq 30) {
                Write-Error "PostgreSQL failed to start within timeout"
                exit 1
            }
            Start-Sleep -Seconds 2
        }
    }
    
    # Check if Redis is ready
    Write-Status "Checking Redis..."
    for ($i = 1; $i -le 10; $i++) {
        try {
            $redisResponse = docker-compose exec -T redis redis-cli ping
            if ($redisResponse -match "PONG") {
                Write-Success "Redis is ready"
                break
            }
        }
        catch {
            if ($i -eq 10) {
                Write-Error "Redis failed to start within timeout"
                exit 1
            }
            Start-Sleep -Seconds 1
        }
    }
    
    Write-Success "Infrastructure services are ready"
}

# Deploy services
function Deploy-Services {
    Write-Status "Deploying all services..."
    
    # Start all services
    docker-compose up -d
    
    Write-Status "Waiting for services to start..."
    Start-Sleep -Seconds 15
    
    # Check service health
    Test-ServiceHealth
}

# Check service health
function Test-ServiceHealth {
    Write-Status "Checking service health..."
    
    $services = @(
        @{Name="job-service"; Port=8004},
        @{Name="candidate-service"; Port=8005},
        @{Name="notification-service"; Port=8006}
    )
    
    foreach ($service in $services) {
        Write-Status "Checking $($service.Name) health..."
        
        for ($i = 1; $i -le 20; $i++) {
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:$($service.Port)/health" -TimeoutSec 5 -UseBasicParsing
                if ($response.StatusCode -eq 200) {
                    Write-Success "$($service.Name) is healthy"
                    break
                }
            }
            catch {
                if ($i -eq 20) {
                    Write-Warning "$($service.Name) health check failed"
                }
                Start-Sleep -Seconds 3
            }
        }
    }
}

# Show service status
function Show-Status {
    Write-Status "Service Status:"
    Write-Host ""
    
    $services = @(
        @{Name="PostgreSQL"; Port=5432; Endpoint=""},
        @{Name="Redis"; Port=6379; Endpoint=""},
        @{Name="Elasticsearch"; Port=9200; Endpoint=""},
        @{Name="RabbitMQ"; Port=15672; Endpoint=""},
        @{Name="Job Service"; Port=8004; Endpoint="/health"},
        @{Name="Candidate Service"; Port=8005; Endpoint="/health"},
        @{Name="Notification Service"; Port=8006; Endpoint="/health"},
        @{Name="API Gateway"; Port=5000; Endpoint=""},
        @{Name="Frontend"; Port=3000; Endpoint=""}
    )
    
    foreach ($service in $services) {
        try {
            $url = "http://localhost:$($service.Port)$($service.Endpoint)"
            $response = Invoke-WebRequest -Uri $url -TimeoutSec 5 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Host "  ✓ $($service.Name) - http://localhost:$($service.Port)" -ForegroundColor Green
            }
            else {
                Write-Host "  ✗ $($service.Name) - http://localhost:$($service.Port) (not responding)" -ForegroundColor Red
            }
        }
        catch {
            Write-Host "  ✗ $($service.Name) - http://localhost:$($service.Port) (not responding)" -ForegroundColor Red
        }
    }
    
    Write-Host ""
    Write-Status "Service URLs:"
    Write-Host "  📊 Job Service API:         http://localhost:8004/docs"
    Write-Host "  👥 Candidate Service API:   http://localhost:8005/docs"
    Write-Host "  📨 Notification Service API: http://localhost:8006/docs"
    Write-Host "  🚪 API Gateway:             http://localhost:5000"
    Write-Host "  🌐 Frontend:                http://localhost:3000"
    Write-Host "  🗄️  Database Admin:          http://localhost:5432"
    Write-Host "  🔍 Elasticsearch:           http://localhost:9200"
    Write-Host "  🐰 RabbitMQ Management:     http://localhost:15672"
}

# Initialize sample data
function Initialize-SampleData {
    Write-Status "Initializing sample data..."
    
    # Wait a bit more for services to be fully ready
    Start-Sleep -Seconds 10
    
    # Create sample job template
    Write-Status "Creating sample job templates..."
    try {
        $body = @{
            name = "Software Engineer Template"
            description = "Standard template for software engineer positions"
            title = "Software Engineer"
            description_template = "We are seeking a {{experience_level}} Software Engineer to join our {{department}} team."
            department = "Engineering"
            employment_type = "full_time"
            required_skills = @("Programming", "Problem Solving", "Communication")
            is_active = $true
        } | ConvertTo-Json
        
        Invoke-RestMethod -Uri "http://localhost:8004/api/v1/templates" -Method Post -Body $body -ContentType "application/json" | Out-Null
    }
    catch {
        Write-Warning "Failed to create job template"
    }
    
    Write-Success "Sample data initialization complete"
}

# Main execution
function Main {
    switch ($Command) {
        "build" {
            if (Test-Docker) {
                Build-Services
                Write-Success "Build complete!"
            }
        }
        "deploy" {
            if (Test-Docker) {
                New-DockerNetwork
                Start-Infrastructure
                Deploy-Services
                Initialize-SampleData
                Show-Status
                Write-Success "Deployment complete!"
                Write-Host ""
                Write-Status "Access the services using the URLs shown above."
                Write-Status "Use 'docker-compose logs <service-name>' to view logs."
                Write-Status "Use '.\deploy.ps1 stop' to stop all services."
            }
        }
        "start" {
            if (Test-Docker) {
                Write-Status "Starting services..."
                docker-compose up -d
                Start-Sleep -Seconds 10
                Show-Status
            }
        }
        "stop" {
            Write-Status "Stopping services..."
            docker-compose down
            Write-Success "All services stopped"
        }
        "restart" {
            Write-Status "Restarting services..."
            docker-compose down
            Start-Sleep -Seconds 5
            docker-compose up -d
            Start-Sleep -Seconds 10
            Show-Status
        }
        "status" {
            Show-Status
        }
        "logs" {
            if ($ServiceName) {
                docker-compose logs -f $ServiceName
            }
            else {
                docker-compose logs -f
            }
        }
        "clean" {
            Write-Status "Cleaning up everything..."
            docker-compose down -v
            docker system prune -f
            Write-Success "Cleanup complete"
        }
        default {
            Write-Host "Vetterati ATS - Service Deployment Script (PowerShell)"
            Write-Host ""
            Write-Host "Usage: .\deploy.ps1 {build|deploy|start|stop|restart|status|logs|clean} [service-name]"
            Write-Host ""
            Write-Host "Commands:"
            Write-Host "  build    - Build all Docker images"
            Write-Host "  deploy   - Full deployment (build + start + init)"
            Write-Host "  start    - Start all services"
            Write-Host "  stop     - Stop all services"
            Write-Host "  restart  - Restart all services"
            Write-Host "  status   - Show service status"
            Write-Host "  logs     - Show logs (optionally for specific service)"
            Write-Host "  clean    - Stop and remove all containers and volumes"
            Write-Host ""
            Write-Host "Examples:"
            Write-Host "  .\deploy.ps1 deploy              # Full deployment"
            Write-Host "  .\deploy.ps1 logs job-service    # Show job service logs"
            Write-Host "  .\deploy.ps1 restart             # Restart all services"
        }
    }
}

# Run main function
Main
