# Quick Reference Guide

## Common Commands

### Initial Setup
```powershell
cd localtesting
.\scripts\setup-dev-environment.ps1
```

### Frontend Development
```powershell
# Start infrastructure and frontend dev server
.\scripts\start-frontend-dev.ps1

# Frontend will be at: http://localhost:3000
# API Gateway at: http://localhost:5000
```

### Backend Service Development
```powershell
# Run service locally (with hot reload)
.\scripts\start-service-dev.ps1 -ServiceName "resume-service" -RunLocal

# Run service in Docker (with volume mount)
.\scripts\start-service-dev.ps1 -ServiceName "resume-service"
```

### Infrastructure Only
```powershell
# Start just the infrastructure services
.\scripts\start-infrastructure.ps1
```

### Monitoring & Debugging
```powershell
# Check status of all services
.\scripts\status.ps1

# View logs
.\scripts\logs.ps1 -Services "postgres","redis" -Follow

# Stop everything
.\scripts\stop-all.ps1

# Reset database
.\scripts\reset-database.ps1
```

## Service URLs

| Service | URL | Technology |
|---------|-----|------------|
| Frontend | http://localhost:3000 | React/TypeScript |
| API Gateway | http://localhost:5000 | C#/.NET |
| Auth Service | http://localhost:5001 | C#/.NET |
| Resume Service | http://localhost:8001 | Python/FastAPI |
| AHP Service | http://localhost:5002 | C#/.NET |
| Workflow Service | http://localhost:8002 | Python/FastAPI |
| Analytics Service | http://localhost:8003 | Python/FastAPI |
| Job Service | http://localhost:8004 | Python/FastAPI |
| Candidate Service | http://localhost:8005 | Python/FastAPI |
| Notification Service | http://localhost:8006 | Python/FastAPI |

## Infrastructure URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| PostgreSQL | localhost:5432 | ats_user / ats_password |
| Redis | localhost:6379 | - |
| Elasticsearch | http://localhost:9200 | - |
| RabbitMQ Management | http://localhost:15672 | ats_user / ats_password |
| LocalStack | http://localhost:4566 | - |

## Development Patterns

### 1. Frontend-Only Development
When working on UI/UX changes:
```powershell
.\scripts\start-frontend-dev.ps1
```
This starts infrastructure + API Gateway + Auth Service + Frontend with hot reload.

### 2. Single Service Development
When working on a specific microservice:
```powershell
.\scripts\start-service-dev.ps1 -ServiceName "resume-service" -RunLocal
```
This starts infrastructure + dependencies + your service locally with hot reload.

### 3. Integration Testing
When testing cross-service functionality:
```powershell
docker-compose -f docker-compose.full.yml up
```
This starts everything in Docker.

### 4. Selective Service Testing
Start only the services you need:
```powershell
.\scripts\start-infrastructure.ps1
docker-compose -f docker-compose.services.yml up api-gateway auth-service resume-service
```

## Tips

1. **Always start with infrastructure** - Other services depend on it
2. **Use -RunLocal for faster development** - Direct host execution is faster than Docker
3. **Volume mounts enable hot reload** - Code changes reflect immediately
4. **Check logs when services fail** - `.\scripts\logs.ps1 -Services "service-name"`
5. **Reset database for clean testing** - `.\scripts\reset-database.ps1`
