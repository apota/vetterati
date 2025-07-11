# Vetterati ATS - Docker Deployment Guide

This guide covers how to deploy the Vetterati ATS using Docker Compose with all the authentication fixes integrated.

## 🚀 Quick Start

### Development Environment
```bash
# Clone the repository
git clone <repository-url>
cd vetterati

# Start all services in development mode
docker-compose up -d

# View logs
docker-compose logs -f auth-service
```

### Production Environment
```bash
# Set environment variables
export JWT_SECRET_KEY="your-super-secret-production-jwt-key-at-least-32-chars"
export DATABASE_PASSWORD="your-secure-database-password"
export SENDGRID_API_KEY="your-sendgrid-api-key"
export FRONTEND_URL="https://your-domain.com"
export API_GATEWAY_URL="https://api.your-domain.com"

# Start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 🏗️ Architecture

The Docker Compose setup includes:

### Core Services
- **PostgreSQL** (Database) - Port 5432
- **Redis** (Cache/Session Store) - Port 6379
- **Auth Service** (.NET 8) - Port 5001
- **API Gateway** (.NET 8) - Port 5000
- **Frontend** (React) - Port 3000

### Supporting Services
- **Elasticsearch** (Search) - Port 9200
- **RabbitMQ** (Message Queue) - Port 5672, Management: 15672
- **LocalStack** (AWS Local) - Port 4566

### Development Tools (dev only)
- **MailHog** (Email Testing) - Port 8025
- **pgAdmin** (Database Management) - Port 5050
- **Redis Commander** (Redis Management) - Port 8081

## 🔧 Authentication Service Features

The auth service includes all the fixes and features:

### ✅ Implemented Features
- **User Registration & Login** with email/password
- **JWT Token Management** with refresh tokens
- **Password Policy Enforcement** (8+ chars, uppercase, lowercase, digit, special char)
- **Rate Limiting** (100/hour anonymous, 1000/hour authenticated)
- **Demo Login System** with 6 predefined roles
- **Password Reset** functionality
- **User-Organization Relationships**
- **BCrypt Password Hashing**
- **Comprehensive Error Handling**

### 🎯 Demo Login Roles
The following demo users are available:
- **admin@vetterati.com** - Full administrator
- **recruiter@company.com** - Recruiter role
- **manager@company.com** - Hiring manager
- **candidate@email.com** - Job candidate
- **interviewer@company.com** - Technical interviewer
- **hr@company.com** - HR representative

## 🌐 Service Endpoints

### Auth Service (Port 5001)
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/email-login` - Email/password login
- `POST /api/v1/auth/demo-login` - Demo user login
- `GET /api/v1/auth/demo-users` - List demo users
- `POST /api/v1/auth/refresh` - Token refresh
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Current user info
- `POST /api/v1/auth/forgot-password` - Password reset request
- `POST /api/v1/auth/reset-password` - Password reset
- `GET /health` - Health check

### API Gateway (Port 5000)
- Routes requests to appropriate microservices
- Handles authentication middleware
- Rate limiting across all services

### Frontend (Port 3000)
- React application with demo login UI
- Login page with clickable demo role chips
- Responsive design with Material-UI

## 🔒 Security Configuration

### Environment Variables (Production)
```bash
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-production-jwt-key-at-least-32-chars
JWT_ISSUER=vetterati-ats
JWT_AUDIENCE=vetterati-ats

# Database
DATABASE_NAME=vetterati_ats
DATABASE_USER=ats_user
DATABASE_PASSWORD=your-secure-database-password

# Email
SENDGRID_API_KEY=your-sendgrid-api-key
SMTP_USERNAME=your-smtp-username
SMTP_PASSWORD=your-smtp-password

# URLs
FRONTEND_URL=https://your-domain.com
API_GATEWAY_URL=https://api.your-domain.com
```

### Password Policy
- Minimum 8 characters
- Requires uppercase letter
- Requires lowercase letter
- Requires digit
- Requires special character
- Maximum 5 failed attempts before lockout
- 15-minute lockout duration

### Rate Limiting
- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour
- Admin users: 5000 requests/hour

## 🚀 Deployment Commands

### Development
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up auth-service

# View logs
docker-compose logs -f auth-service

# Restart service
docker-compose restart auth-service

# Stop all services
docker-compose down

# Clean restart (removes volumes)
docker-compose down -v && docker-compose up -d
```

### Production
```bash
# Build and start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Check service health
docker-compose ps

# View production logs
docker-compose logs --tail=100 auth-service

# Scale services (if needed)
docker-compose up -d --scale auth-service=2
```

## 🏥 Health Checks

All services include health checks:
- **Database**: `pg_isready` command
- **Redis**: `redis-cli ping`
- **Auth Service**: `GET /health` endpoint
- **LocalStack**: Health endpoint check

Health check status:
```bash
docker-compose ps
```

## 📊 Monitoring

### Service Status
```bash
# Check all services
docker-compose ps

# View resource usage
docker stats

# Check service logs
docker-compose logs -f --tail=100
```

### Database Access
- **pgAdmin**: http://localhost:5050 (admin@vetterati.com / admin)
- **Direct Connection**: localhost:5432 (ats_user / ats_password)

### Redis Access
- **Redis Commander**: http://localhost:8081
- **Direct Connection**: localhost:6379

### Email Testing (Development)
- **MailHog UI**: http://localhost:8025

## 🔧 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check what's using ports
   netstat -tulpn | grep :5432
   # Change ports in docker-compose.yml if needed
   ```

2. **Database Connection Issues**
   ```bash
   # Check postgres logs
   docker-compose logs postgres
   # Restart database
   docker-compose restart postgres
   ```

3. **Auth Service Issues**
   ```bash
   # Check auth service logs
   docker-compose logs -f auth-service
   # Rebuild auth service
   docker-compose up -d --build auth-service
   ```

4. **Frontend Not Loading**
   ```bash
   # Check frontend logs
   docker-compose logs frontend
   # Clear browser cache and try again
   ```

### Reset Everything
```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v --remove-orphans

# Remove all images
docker-compose down --rmi all

# Start fresh
docker-compose up -d --build
```

## 📝 Notes

- All authentication fixes are integrated into the Docker setup
- Demo login works immediately after startup
- Database migrations run automatically
- Redis stores session data and rate limiting counters
- All services have proper health checks and restart policies
- Development and production configurations are separated

## 🆘 Support

If you encounter issues:
1. Check service logs: `docker-compose logs [service-name]`
2. Verify environment variables
3. Ensure ports are not in use
4. Check Docker daemon is running
5. Try rebuilding: `docker-compose up -d --build`
