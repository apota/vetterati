#!/bin/bash

# Test script for new Vetterati ATS services
# This script validates that the new microservices are working correctly

set -e

echo "🧪 Testing Vetterati ATS New Services"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Test service health
test_health() {
    local service_name=$1
    local port=$2
    
    print_status "Testing $service_name health..."
    
    if curl -f -s "http://localhost:$port/health" > /dev/null; then
        print_success "$service_name is healthy"
        return 0
    else
        print_error "$service_name health check failed"
        return 1
    fi
}

# Test service API
test_api() {
    local service_name=$1
    local port=$2
    local endpoint=$3
    
    print_status "Testing $service_name API: $endpoint"
    
    response=$(curl -s -w "%{http_code}" "http://localhost:$port$endpoint")
    status_code="${response: -3}"
    
    if [[ "$status_code" =~ ^[23] ]]; then
        print_success "$service_name API $endpoint responded with $status_code"
        return 0
    else
        print_error "$service_name API $endpoint failed with $status_code"
        return 1
    fi
}

# Test job service
test_job_service() {
    print_status "Testing Job Service..."
    
    # Health check
    test_health "Job Service" 8004 || return 1
    
    # Test endpoints
    test_api "Job Service" 8004 "/api/v1/jobs" || return 1
    test_api "Job Service" 8004 "/api/v1/templates" || return 1
    test_api "Job Service" 8004 "/api/v1/stats" || return 1
    test_api "Job Service" 8004 "/docs" || return 1
    
    print_success "Job Service tests passed"
}

# Test candidate service
test_candidate_service() {
    print_status "Testing Candidate Service..."
    
    # Health check
    test_health "Candidate Service" 8005 || return 1
    
    # Test endpoints
    test_api "Candidate Service" 8005 "/api/v1/candidates" || return 1
    test_api "Candidate Service" 8005 "/api/v1/applications" || return 1
    test_api "Candidate Service" 8005 "/api/v1/resumes" || return 1
    test_api "Candidate Service" 8005 "/api/v1/experiences" || return 1
    test_api "Candidate Service" 8005 "/api/v1/educations" || return 1
    test_api "Candidate Service" 8005 "/api/v1/skills" || return 1
    test_api "Candidate Service" 8005 "/api/v1/stats" || return 1
    test_api "Candidate Service" 8005 "/docs" || return 1
    
    print_success "Candidate Service tests passed"
}

# Test notification service
test_notification_service() {
    print_status "Testing Notification Service..."
    
    # Health check
    test_health "Notification Service" 8006 || return 1
    
    # Test endpoints
    test_api "Notification Service" 8006 "/api/v1/templates" || return 1
    test_api "Notification Service" 8006 "/api/v1/notifications" || return 1
    test_api "Notification Service" 8006 "/api/v1/stats" || return 1
    test_api "Notification Service" 8006 "/docs" || return 1
    
    print_success "Notification Service tests passed"
}

# Test database connectivity
test_database() {
    print_status "Testing database connectivity..."
    
    # Test PostgreSQL
    if docker-compose -f docker-compose.new-services.yml exec -T postgres pg_isready -U ats_user -d vetterati_ats > /dev/null 2>&1; then
        print_success "PostgreSQL is accessible"
    else
        print_error "PostgreSQL is not accessible"
        return 1
    fi
    
    # Test Redis
    if docker-compose -f docker-compose.new-services.yml exec -T redis redis-cli ping | grep -q "PONG"; then
        print_success "Redis is accessible"
    else
        print_error "Redis is not accessible"
        return 1
    fi
    
    # Test Elasticsearch
    if curl -f -s "http://localhost:9200" > /dev/null; then
        print_success "Elasticsearch is accessible"
    else
        print_error "Elasticsearch is not accessible"
        return 1
    fi
    
    # Test RabbitMQ
    if curl -f -s "http://localhost:15672" > /dev/null; then
        print_success "RabbitMQ Management is accessible"
    else
        print_error "RabbitMQ Management is not accessible"
        return 1
    fi
}

# Create sample data
create_sample_data() {
    print_status "Creating sample data..."
    
    # Create a job template
    job_template=$(curl -s -X POST "http://localhost:8004/api/v1/templates" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "Test Software Engineer Template",
            "description": "Test template for software engineer positions",
            "title": "Software Engineer",
            "description_template": "We are seeking a {{experience_level}} Software Engineer.",
            "department": "Engineering",
            "employment_type": "full_time",
            "required_skills": ["Programming", "Testing"],
            "is_active": true
        }')
    
    if echo "$job_template" | grep -q '"id"'; then
        print_success "Job template created successfully"
        job_template_id=$(echo "$job_template" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
    else
        print_warning "Failed to create job template"
        return 1
    fi
    
    # Create a job
    job=$(curl -s -X POST "http://localhost:8004/api/v1/jobs" \
        -H "Content-Type: application/json" \
        -d '{
            "title": "Senior Software Engineer",
            "description": "We are looking for a senior software engineer...",
            "department": "Engineering",
            "location": "San Francisco, CA",
            "employment_type": "full_time",
            "experience_level": "senior",
            "status": "active",
            "required_skills": ["Python", "JavaScript", "SQL"],
            "salary_range_min": 120000,
            "salary_range_max": 180000
        }')
    
    if echo "$job" | grep -q '"id"'; then
        print_success "Job created successfully"
        job_id=$(echo "$job" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
    else
        print_warning "Failed to create job"
        return 1
    fi
    
    # Create a candidate
    candidate=$(curl -s -X POST "http://localhost:8005/api/v1/candidates" \
        -H "Content-Type: application/json" \
        -d '{
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+1-555-0123",
            "location": "San Francisco, CA",
            "status": "active"
        }')
    
    if echo "$candidate" | grep -q '"id"'; then
        print_success "Candidate created successfully"
        candidate_id=$(echo "$candidate" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
    else
        print_warning "Failed to create candidate"
        return 1
    fi
    
    # Create a notification template
    notification_template=$(curl -s -X POST "http://localhost:8006/api/v1/templates" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "Test Welcome Email",
            "description": "Test welcome email template",
            "channel": "email",
            "subject_template": "Welcome {{candidate_name}}!",
            "body_template": "Dear {{candidate_name}}, welcome to our system!",
            "is_active": true
        }')
    
    if echo "$notification_template" | grep -q '"id"'; then
        print_success "Notification template created successfully"
    else
        print_warning "Failed to create notification template"
        return 1
    fi
    
    print_success "Sample data creation completed"
}

# Main test execution
main() {
    print_status "Starting service tests..."
    echo ""
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Test infrastructure
    test_database || exit 1
    echo ""
    
    # Test services
    test_job_service || exit 1
    echo ""
    
    test_candidate_service || exit 1
    echo ""
    
    test_notification_service || exit 1
    echo ""
    
    # Create sample data
    create_sample_data || print_warning "Sample data creation had issues"
    echo ""
    
    print_success "All tests completed successfully!"
    echo ""
    print_status "Service URLs:"
    echo "  📊 Job Service:         http://localhost:8004/docs"
    echo "  👥 Candidate Service:   http://localhost:8005/docs"
    echo "  📨 Notification Service: http://localhost:8006/docs"
    echo "  🗄️  PostgreSQL:          http://localhost:5432"
    echo "  🔍 Elasticsearch:       http://localhost:9200"
    echo "  🐰 RabbitMQ:            http://localhost:15672"
}

# Check if services are specified to start
if [ "$1" = "start" ]; then
    print_status "Starting new services..."
    docker-compose -f docker-compose.new-services.yml up -d
    main
elif [ "$1" = "test" ]; then
    main
elif [ "$1" = "stop" ]; then
    print_status "Stopping services..."
    docker-compose -f docker-compose.new-services.yml down
    print_success "Services stopped"
else
    echo "Usage: $0 {start|test|stop}"
    echo ""
    echo "Commands:"
    echo "  start  - Start services and run tests"
    echo "  test   - Run tests on running services"
    echo "  stop   - Stop all services"
fi
