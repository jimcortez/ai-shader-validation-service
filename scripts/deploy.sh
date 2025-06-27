#!/bin/bash

# AI Shader Validator Deployment Script
# This script handles deployment to different environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT=${1:-development}
ACTION=${2:-deploy}

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check kubectl for production
    if [ "$ENVIRONMENT" = "production" ]; then
        if ! command -v kubectl &> /dev/null; then
            log_error "kubectl is not installed"
            exit 1
        fi
    fi
    
    log_success "All dependencies are available"
}

build_image() {
    log_info "Building Docker image..."
    
    cd "$PROJECT_ROOT"
    
    # Build with appropriate target
    if [ "$ENVIRONMENT" = "production" ]; then
        docker build -t ai-shadervalidator:latest --target production .
    else
        docker build -t ai-shadervalidator:dev --target development .
    fi
    
    log_success "Docker image built successfully"
}

deploy_development() {
    log_info "Deploying to development environment..."
    
    cd "$PROJECT_ROOT"
    
    # Stop existing containers
    docker-compose down
    
    # Start services
    docker-compose up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 30
    
    # Check health
    if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        log_success "Development deployment successful"
    else
        log_error "Health check failed"
        exit 1
    fi
}

deploy_staging() {
    log_info "Deploying to staging environment..."
    
    cd "$PROJECT_ROOT"
    
    # Use staging configuration
    docker-compose -f docker-compose.staging.yml down
    docker-compose -f docker-compose.staging.yml up -d
    
    log_info "Waiting for services to be ready..."
    sleep 60
    
    # Check health
    if curl -f http://staging.shadervalidator.com/api/v1/health > /dev/null 2>&1; then
        log_success "Staging deployment successful"
    else
        log_error "Health check failed"
        exit 1
    fi
}

deploy_production() {
    log_info "Deploying to production environment..."
    
    # Check if we're on main branch
    if [ "$(git branch --show-current)" != "main" ]; then
        log_error "Production deployment must be from main branch"
        exit 1
    fi
    
    # Apply Kubernetes manifests
    kubectl apply -f kubernetes/
    
    # Wait for deployment to be ready
    log_info "Waiting for deployment to be ready..."
    kubectl rollout status deployment/ai-shadervalidator-app -n shadervalidator --timeout=300s
    
    # Check health
    if curl -f https://api.shadervalidator.com/api/v1/health > /dev/null 2>&1; then
        log_success "Production deployment successful"
    else
        log_error "Health check failed"
        exit 1
    fi
}

run_tests() {
    log_info "Running tests..."
    
    cd "$PROJECT_ROOT"
    
    # Run tests in container
    docker-compose run --rm app pytest tests/ -v
    
    log_success "Tests completed"
}

run_migrations() {
    log_info "Running database migrations..."
    
    cd "$PROJECT_ROOT"
    
    # Run migrations in container
    docker-compose run --rm app python -m alembic upgrade head
    
    log_success "Migrations completed"
}

backup_database() {
    log_info "Creating database backup..."
    
    cd "$PROJECT_ROOT"
    
    # Create backup
    docker-compose exec postgres pg_dump -U shader_user shadervalidator > "backup_$(date +%Y%m%d_%H%M%S).sql"
    
    log_success "Database backup created"
}

monitor_deployment() {
    log_info "Monitoring deployment..."
    
    # Monitor for 5 minutes
    for i in {1..30}; do
        if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
            log_success "Service is healthy"
            return 0
        else
            log_warning "Service not ready yet, waiting..."
            sleep 10
        fi
    done
    
    log_error "Service failed to become healthy"
    return 1
}

show_help() {
    echo "AI Shader Validator Deployment Script"
    echo ""
    echo "Usage: $0 [ENVIRONMENT] [ACTION]"
    echo ""
    echo "Environments:"
    echo "  development (default)"
    echo "  staging"
    echo "  production"
    echo ""
    echo "Actions:"
    echo "  deploy (default)"
    echo "  build"
    echo "  test"
    echo "  migrate"
    echo "  backup"
    echo "  monitor"
    echo "  stop"
    echo "  logs"
    echo ""
    echo "Examples:"
    echo "  $0                    # Deploy to development"
    echo "  $0 production deploy  # Deploy to production"
    echo "  $0 development test   # Run tests in development"
    echo "  $0 production backup  # Backup production database"
}

# Main script
main() {
    case "$ACTION" in
        "deploy")
            check_dependencies
            build_image
            case "$ENVIRONMENT" in
                "development")
                    deploy_development
                    ;;
                "staging")
                    deploy_staging
                    ;;
                "production")
                    deploy_production
                    ;;
                *)
                    log_error "Unknown environment: $ENVIRONMENT"
                    exit 1
                    ;;
            esac
            ;;
        "build")
            check_dependencies
            build_image
            ;;
        "test")
            run_tests
            ;;
        "migrate")
            run_migrations
            ;;
        "backup")
            backup_database
            ;;
        "monitor")
            monitor_deployment
            ;;
        "stop")
            cd "$PROJECT_ROOT"
            if [ "$ENVIRONMENT" = "production" ]; then
                kubectl delete -f kubernetes/
            else
                docker-compose down
            fi
            log_success "Services stopped"
            ;;
        "logs")
            cd "$PROJECT_ROOT"
            if [ "$ENVIRONMENT" = "production" ]; then
                kubectl logs -f deployment/ai-shadervalidator-app -n shadervalidator
            else
                docker-compose logs -f
            fi
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "Unknown action: $ACTION"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 