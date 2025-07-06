#!/bin/bash

# Vetterati ATS - Service Deployment Script
# This script builds and deploys the new microservices

set -e  # Exit on any error

echo "🚀 Vetterati ATS - Deploying New Microservices"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    print_status "Checking Docker..."
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Build services
build_services() {
    print_status "Building microservices..."
    
    services=("job-service" "candidate-service" "notification-service")
    
    for service in "${services[@]}"; do
        print_status "Building $service..."
        
        if [ -d "src/services/$service" ]; then
            cd "src/services/$service"
            
            # Build Docker image
            if docker build -t "vetterati-$service" .; then
                print_success "$service built successfully"
            else
                print_error "Failed to build $service"
                cd ../../..
                exit 1
            fi
            
            cd ../../..
        else
            print_warning "Service directory not found: src/services/$service"
        fi
    done
}

# Create network if it doesn't exist
create_network() {
    print_status "Creating Docker network..."
    
    if ! docker network ls | grep -q "ats-network"; then
        docker network create ats-network
        print_success "Created ats-network"
    else
        print_success "ats-network already exists"
    fi
}

# Start infrastructure services
start_infrastructure() {
    print_status "Starting infrastructure services..."
    
    # Start only infrastructure services first
    docker-compose up -d postgres redis elasticsearch rabbitmq dynamodb
    
    print_status "Waiting for infrastructure services to be ready..."
    sleep 10
    
    # Check if PostgreSQL is ready
    print_status "Waiting for PostgreSQL to be ready..."
    for i in {1..30}; do
        if docker-compose exec -T postgres pg_isready -U ats_user -d vetterati_ats > /dev/null 2>&1; then
            print_success "PostgreSQL is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "PostgreSQL failed to start within timeout"
            exit 1
        fi
        sleep 2
    done
    
    # Check if Redis is ready
    print_status "Checking Redis..."
    for i in {1..10}; do
        if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
            print_success "Redis is ready"
            break
        fi
        if [ $i -eq 10 ]; then
            print_error "Redis failed to start within timeout"
            exit 1
        fi
        sleep 1
    done
    
    print_success "Infrastructure services are ready"
}

# Deploy services
deploy_services() {
    print_status "Deploying all services..."
    
    # Start all services
    docker-compose up -d
    
    print_status "Waiting for services to start..."
    sleep 15
    
    # Check service health
    check_service_health
}

# Check service health
check_service_health() {
    print_status "Checking service health..."
    
    services=(
        "job-service:8004"
        "candidate-service:8005" 
        "notification-service:8006"
    )
    
    for service_port in "${services[@]}"; do
        service=${service_port%:*}
        port=${service_port#*:}
        
        print_status "Checking $service health..."
        
        for i in {1..20}; do
            if curl -f "http://localhost:$port/health" > /dev/null 2>&1; then
                print_success "$service is healthy"
                break
            fi
            if [ $i -eq 20 ]; then
                print_warning "$service health check failed"
            fi
            sleep 3
        done
    done
}

# Show service status
show_status() {
    print_status "Service Status:"
    echo ""
    
    services=(
        "PostgreSQL:5432:/health"
        "Redis:6379"
        "Elasticsearch:9200"
        "RabbitMQ:15672"
        "Job Service:8004:/health"
        "Candidate Service:8005:/health"
        "Notification Service:8006:/health"
        "API Gateway:5000"
        "Frontend:3000"
    )
    
    for service_info in "${services[@]}"; do
        IFS=':' read -r name port endpoint <<< "$service_info"
        
        if [ -z "$endpoint" ]; then
            endpoint=""
        fi
        
        if curl -f "http://localhost:$port$endpoint" > /dev/null 2>&1; then
            echo -e "  ${GREEN}✓${NC} $name - http://localhost:$port"
        else
            echo -e "  ${RED}✗${NC} $name - http://localhost:$port (not responding)"
        fi
    done
    
    echo ""
    print_status "Service URLs:"
    echo "  📊 Job Service API:         http://localhost:8004/docs"
    echo "  👥 Candidate Service API:   http://localhost:8005/docs"
    echo "  📨 Notification Service API: http://localhost:8006/docs"
    echo "  🚪 API Gateway:             http://localhost:5000"
    echo "  🌐 Frontend:                http://localhost:3000"
    echo "  🗄️  Database Admin:          http://localhost:5432"
    echo "  🔍 Elasticsearch:           http://localhost:9200"
    echo "  🐰 RabbitMQ Management:     http://localhost:15672"
}

# Initialize sample data
init_sample_data() {
    print_status "Initializing sample data..."
    
    # Wait a bit more for services to be fully ready
    sleep 10
    
    # Create sample job templates
    print_status "Creating sample job templates..."
    curl -X POST "http://localhost:8004/api/v1/templates" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "Software Engineer Template",
            "description": "Standard template for software engineer positions",
            "title": "Software Engineer",
            "description_template": "We are seeking a {{experience_level}} Software Engineer to join our {{department}} team.",
            "department": "Engineering",
            "employment_type": "full_time",
            "required_skills": ["Programming", "Problem Solving", "Communication"],
            "is_active": true
        }' > /dev/null 2>&1 || print_warning "Failed to create job template"
    
    print_success "Sample data initialization complete"
}

# Cleanup function
cleanup() {
    print_status "Cleaning up..."
    docker-compose down
    print_success "Cleanup complete"
}

# Main execution
main() {
    case "$1" in
        "build")
            check_docker
            build_services
            print_success "Build complete!"
            ;;
        "deploy")
            check_docker
            create_network
            start_infrastructure
            deploy_services
            init_sample_data
            show_status
            print_success "Deployment complete!"
            echo ""
            print_status "Access the services using the URLs shown above."
            print_status "Use 'docker-compose logs <service-name>' to view logs."
            print_status "Use '$0 stop' to stop all services."
            ;;
        "start")
            check_docker
            print_status "Starting services..."
            docker-compose up -d
            sleep 10
            show_status
            ;;
        "stop")
            print_status "Stopping services..."
            docker-compose down
            print_success "All services stopped"
            ;;
        "restart")
            print_status "Restarting services..."
            docker-compose down
            sleep 5
            docker-compose up -d
            sleep 10
            show_status
            ;;
        "status")
            show_status
            ;;
        "logs")
            if [ -n "$2" ]; then
                docker-compose logs -f "$2"
            else
                docker-compose logs -f
            fi
            ;;
        "clean")
            print_status "Cleaning up everything..."
            docker-compose down -v
            docker system prune -f
            print_success "Cleanup complete"
            ;;
        *)
            echo "Vetterati ATS - Service Deployment Script"
            echo ""
            echo "Usage: $0 {build|deploy|start|stop|restart|status|logs|clean}"
            echo ""
            echo "Commands:"
            echo "  build    - Build all Docker images"
            echo "  deploy   - Full deployment (build + start + init)"
            echo "  start    - Start all services"
            echo "  stop     - Stop all services"
            echo "  restart  - Restart all services"
            echo "  status   - Show service status"
            echo "  logs     - Show logs (optionally for specific service)"
            echo "  clean    - Stop and remove all containers and volumes"
            echo ""
            echo "Examples:"
            echo "  $0 deploy              # Full deployment"
            echo "  $0 logs job-service    # Show job service logs"
            echo "  $0 restart             # Restart all services"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
