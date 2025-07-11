#!/bin/bash

# Vetterati ATS - Docker Deployment Script
# This script helps you deploy the Vetterati ATS with all authentication fixes

set -e

echo "🚀 Vetterati ATS Deployment Script"
echo "=================================="

# Function to check if docker and docker-compose are installed
check_dependencies() {
    echo "📋 Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    echo "✅ Dependencies check passed"
}

# Function to set up environment for development
setup_development() {
    echo "🔧 Setting up development environment..."
    
    # Copy environment template if it doesn't exist
    if [ ! -f .env ]; then
        cat > .env << EOF
# Vetterati ATS Development Environment
COMPOSE_PROJECT_NAME=vetterati
ASPNETCORE_ENVIRONMENT=Development
JWT_SECRET_KEY=development-jwt-key-that-is-at-least-32-characters-long-for-security
DATABASE_PASSWORD=ats_password
SENDGRID_API_KEY=demo-development-key
FRONTEND_URL=http://localhost:3000
API_GATEWAY_URL=http://localhost:5000
EOF
        echo "✅ Created .env file with development defaults"
    fi
}

# Function to start services
start_services() {
    local environment=$1
    
    echo "🚀 Starting Vetterati ATS services..."
    
    if [ "$environment" = "production" ]; then
        echo "🏭 Starting production environment..."
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
    else
        echo "🛠️  Starting development environment..."
        docker-compose up -d --build
    fi
    
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    # Check service health
    echo "🏥 Checking service health..."
    docker-compose ps
}

# Function to show service information
show_info() {
    echo ""
    echo "🎉 Vetterati ATS is now running!"
    echo "==============================="
    echo ""
    echo "🌐 Service URLs:"
    echo "   Frontend:      http://localhost:3000"
    echo "   API Gateway:   http://localhost:5000"
    echo "   Auth Service:  http://localhost:5001"
    echo ""
    echo "🔑 Demo Login:"
    echo "   Visit http://localhost:3000/login"
    echo "   Click any demo role chip to login instantly"
    echo "   Available roles: admin, recruiter, hiring-manager, candidate, interviewer, hr"
    echo ""
    echo "🛠️  Development Tools:"
    echo "   pgAdmin:       http://localhost:5050 (admin@vetterati.com / admin)"
    echo "   Redis Commander: http://localhost:8081"
    echo "   MailHog:       http://localhost:8025"
    echo "   RabbitMQ:      http://localhost:15672 (ats_user / ats_password)"
    echo ""
    echo "📊 Health Checks:"
    echo "   Auth Service:  http://localhost:5001/health"
    echo "   API Gateway:   http://localhost:5000/health"
    echo ""
    echo "📝 Useful Commands:"
    echo "   View logs:     docker-compose logs -f [service-name]"
    echo "   Stop services: docker-compose down"
    echo "   Restart:       docker-compose restart [service-name]"
    echo ""
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping Vetterati ATS services..."
    docker-compose down
    echo "✅ Services stopped"
}

# Function to clean up everything
cleanup() {
    echo "🧹 Cleaning up all Vetterati ATS data..."
    read -p "This will remove all containers, volumes, and data. Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v --remove-orphans
        docker-compose down --rmi local
        echo "✅ Cleanup completed"
    else
        echo "❌ Cleanup cancelled"
    fi
}

# Main script logic
case "$1" in
    "start")
        check_dependencies
        setup_development
        start_services "development"
        show_info
        ;;
    "start-prod")
        check_dependencies
        start_services "production"
        show_info
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        check_dependencies
        setup_development
        start_services "development"
        show_info
        ;;
    "logs")
        if [ -n "$2" ]; then
            docker-compose logs -f "$2"
        else
            docker-compose logs -f
        fi
        ;;
    "status")
        docker-compose ps
        ;;
    "cleanup")
        cleanup
        ;;
    *)
        echo "Usage: $0 {start|start-prod|stop|restart|logs [service]|status|cleanup}"
        echo ""
        echo "Commands:"
        echo "  start      - Start development environment"
        echo "  start-prod - Start production environment"
        echo "  stop       - Stop all services"
        echo "  restart    - Restart development environment"
        echo "  logs       - View logs (optionally for specific service)"
        echo "  status     - Show service status"
        echo "  cleanup    - Remove all containers and data"
        echo ""
        echo "Examples:"
        echo "  $0 start                 # Start development environment"
        echo "  $0 logs auth-service     # View auth service logs"
        echo "  $0 status                # Check service status"
        exit 1
        ;;
esac
