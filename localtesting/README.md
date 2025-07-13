# Local Testing Environment

This folder contains all the necessary artifacts for quick local development and testing without rebuilding all Docker containers.

## Quick Start

1. **Start Core Infrastructure**: `docker-compose -f docker-compose.infrastructure.yml up -d`
2. **Start Specific Services**: `docker-compose -f docker-compose.services.yml up [service-name]`
3. **Run Frontend Locally**: `npm run dev:local` (from src/frontend)
4. **Run Backend Service Locally**: Use the appropriate run script in `scripts/`

## Architecture

### Infrastructure Layer (Always Running)
- PostgreSQL Database
- Redis Cache
- Elasticsearch
- RabbitMQ
- LocalStack (AWS services)

### Application Layer (Selective)
- Frontend (React) - Can run locally with hot reload
- API Gateway - Can run locally or in Docker
- Individual microservices - Can run locally or in Docker

## Development Workflows

### Frontend Development
```bash
# Start infrastructure
docker-compose -f localtesting/docker-compose.infrastructure.yml up -d

# Start API Gateway and core services
docker-compose -f localtesting/docker-compose.services.yml up api-gateway auth-service

# Run frontend locally with hot reload
cd src/frontend
npm run dev:local
```

### Backend Service Development
```bash
# Start infrastructure
docker-compose -f localtesting/docker-compose.infrastructure.yml up -d

# Start dependencies (other services your service needs)
docker-compose -f localtesting/docker-compose.services.yml up api-gateway auth-service

# Run your service locally
cd src/services/your-service
python main.py  # or dotnet run
```

### Full Integration Testing
```bash
# Start everything
docker-compose -f localtesting/docker-compose.full.yml up
```

## Scripts

- `scripts/start-infrastructure.ps1` - Start only infrastructure services
- `scripts/start-frontend-dev.ps1` - Start frontend development environment
- `scripts/start-service-dev.ps1` - Start individual service development
- `scripts/reset-database.ps1` - Reset database to clean state
- `scripts/logs.ps1` - View logs from specific services

## Environment Configuration

Each service has a `.env.local` file with appropriate settings for local development.

## Port Mapping

### Infrastructure
- PostgreSQL: 5432
- Redis: 6379
- Elasticsearch: 9200
- RabbitMQ: 5672 (AMQP), 15672 (Management)
- LocalStack: 4566

### Services
- API Gateway: 5000
- Auth Service: 5001
- Resume Service: 8001
- AHP Service: 5002
- Workflow Service: 8002
- Analytics Service: 8003
- Job Service: 8004
- Candidate Service: 8005
- Notification Service: 8006
- Frontend: 3000

## Tips

1. **Use volume mounts** for source code to enable hot reload
2. **Start with infrastructure** then add services incrementally
3. **Use health checks** to ensure services are ready
4. **Monitor logs** using the provided scripts
5. **Reset database** when testing data migrations
