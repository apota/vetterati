@echo off
REM Vetterati ATS - Docker Deployment Script for Windows
REM This script helps you deploy the Vetterati ATS with all authentication fixes

setlocal enabledelayedexpansion

echo 🚀 Vetterati ATS Deployment Script
echo ==================================

if "%1"=="start" goto start
if "%1"=="start-prod" goto start_prod
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="logs" goto logs
if "%1"=="status" goto status
if "%1"=="cleanup" goto cleanup
goto usage

:check_dependencies
echo 📋 Checking dependencies...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)
echo ✅ Dependencies check passed
goto :eof

:setup_development
echo 🔧 Setting up development environment...
if not exist .env (
    echo # Vetterati ATS Development Environment > .env
    echo COMPOSE_PROJECT_NAME=vetterati >> .env
    echo ASPNETCORE_ENVIRONMENT=Development >> .env
    echo JWT_SECRET_KEY=development-jwt-key-that-is-at-least-32-characters-long-for-security >> .env
    echo DATABASE_PASSWORD=ats_password >> .env
    echo SENDGRID_API_KEY=demo-development-key >> .env
    echo FRONTEND_URL=http://localhost:3000 >> .env
    echo API_GATEWAY_URL=http://localhost:5000 >> .env
    echo ✅ Created .env file with development defaults
)
goto :eof

:start
call :check_dependencies
call :setup_development
echo 🚀 Starting Vetterati ATS services...
echo 🛠️  Starting development environment...
docker-compose up -d --build
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul
echo 🏥 Checking service health...
docker-compose ps
call :show_info
goto :eof

:start_prod
call :check_dependencies
echo 🚀 Starting Vetterati ATS services...
echo 🏭 Starting production environment...
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul
echo 🏥 Checking service health...
docker-compose ps
call :show_info
goto :eof

:stop
echo 🛑 Stopping Vetterati ATS services...
docker-compose down
echo ✅ Services stopped
goto :eof

:restart
call :stop
call :start
goto :eof

:logs
if "%2"=="" (
    docker-compose logs -f
) else (
    docker-compose logs -f %2
)
goto :eof

:status
docker-compose ps
goto :eof

:cleanup
echo 🧹 Cleaning up all Vetterati ATS data...
set /p "confirm=This will remove all containers, volumes, and data. Are you sure? (y/N): "
if /i "!confirm!"=="y" (
    docker-compose down -v --remove-orphans
    docker-compose down --rmi local
    echo ✅ Cleanup completed
) else (
    echo ❌ Cleanup cancelled
)
goto :eof

:show_info
echo.
echo 🎉 Vetterati ATS is now running!
echo ===============================
echo.
echo 🌐 Service URLs:
echo    Frontend:      http://localhost:3000
echo    API Gateway:   http://localhost:5000
echo    Auth Service:  http://localhost:5001
echo.
echo 🔑 Demo Login:
echo    Visit http://localhost:3000/login
echo    Click any demo role chip to login instantly
echo    Available roles: admin, recruiter, hiring-manager, candidate, interviewer, hr
echo.
echo 🛠️  Development Tools:
echo    pgAdmin:       http://localhost:5050 (admin@vetterati.com / admin)
echo    Redis Commander: http://localhost:8081
echo    MailHog:       http://localhost:8025
echo    RabbitMQ:      http://localhost:15672 (ats_user / ats_password)
echo.
echo 📊 Health Checks:
echo    Auth Service:  http://localhost:5001/health
echo    API Gateway:   http://localhost:5000/health
echo.
echo 📝 Useful Commands:
echo    View logs:     deploy.bat logs [service-name]
echo    Stop services: deploy.bat stop
echo    Restart:       deploy.bat restart
echo.
goto :eof

:usage
echo Usage: %0 {start^|start-prod^|stop^|restart^|logs [service]^|status^|cleanup}
echo.
echo Commands:
echo   start      - Start development environment
echo   start-prod - Start production environment
echo   stop       - Stop all services
echo   restart    - Restart development environment
echo   logs       - View logs (optionally for specific service)
echo   status     - Show service status
echo   cleanup    - Remove all containers and data
echo.
echo Examples:
echo   %0 start                 # Start development environment
echo   %0 logs auth-service     # View auth service logs
echo   %0 status                # Check service status
exit /b 1
