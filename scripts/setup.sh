#!/bin/bash

# AI Shader Validation Tool - Setup Script
# This script sets up the development environment using Docker Compose

set -e  # Exit on any error

echo "🚀 Setting up AI Shader Validation Tool..."

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

# Check prerequisites
print_status "Checking prerequisites..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is required but not installed."
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is required but not installed."
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running."
    echo "Please start Docker and try again."
    exit 1
fi

print_success "Prerequisites check passed!"

# Create necessary directories
print_status "Creating directories..."
mkdir -p storage logs cache
print_success "Directories created!"

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    print_status "Creating .env file from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        print_success "Created .env file from template"
        print_warning "Please review and update .env configuration if needed"
    else
        print_warning "No .env.example found, creating basic .env file..."
        cat > .env << EOF
# AI Shader Validation Tool Configuration

# Database Configuration
DATABASE_URL=sqlite:///./storage/shader_validator.db

# Storage Configuration
STORAGE_PATH=./storage
LOG_LEVEL=INFO
DEBUG=true

# Security Configuration
ALLOW_REMOTE_ACCESS=false
SECRET_KEY=your-secret-key-change-this-in-production

# Performance Configuration
MAX_SHADER_SIZE=1048576
VALIDATION_TIMEOUT=30
RENDER_TIMEOUT=60

# Optional: PostgreSQL Configuration (uncomment to use)
# DATABASE_URL=postgresql://shader_user:shader_pass@postgres:5432/shadervalidator
EOF
        print_success "Created basic .env file"
    fi
else
    print_status ".env file already exists, skipping creation"
fi

# Check if we should use PostgreSQL
if grep -q "postgresql://" .env; then
    print_status "PostgreSQL configuration detected, will start with PostgreSQL"
    POSTGRES_PROFILE="--profile postgres"
else
    print_status "Using SQLite database (default)"
    POSTGRES_PROFILE=""
fi

# Build and start services
print_status "Building and starting services..."
docker-compose up --build -d $POSTGRES_PROFILE

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 10

# Check if the API is responding
print_status "Checking API health..."
for i in {1..30}; do
    if curl -f http://localhost:8000/api/v1/health &> /dev/null; then
        print_success "API is healthy and responding!"
        break
    fi
    
    if [ $i -eq 30 ]; then
        print_error "API failed to start within expected time"
        print_status "Checking logs..."
        docker-compose logs shader-validator
        exit 1
    fi
    
    print_status "Waiting for API to start... (attempt $i/30)"
    sleep 2
done

# Display setup information
echo ""
print_success "🎉 Setup complete!"
echo ""
echo "📋 Service Information:"
echo "  • API Server: http://localhost:8000"
echo "  • API Documentation: http://localhost:8000/docs"
echo "  • Health Check: http://localhost:8000/api/v1/health"
echo ""
echo "📁 Local Directories:"
echo "  • Storage: ./storage"
echo "  • Logs: ./logs"
echo "  • Cache: ./cache"
echo ""
echo "🔧 Useful Commands:"
echo "  • View logs: docker-compose logs -f"
echo "  • Stop services: docker-compose down"
echo "  • Restart services: docker-compose restart"
echo "  • Update and rebuild: docker-compose up --build -d"
echo ""
echo "📖 Next Steps:"
echo "  1. Visit http://localhost:8000/docs to see the API documentation"
echo "  2. Try the example API calls in the README.md"
echo "  3. Check the logs if you encounter any issues"
echo ""

# Optional: Show current status
print_status "Current service status:"
docker-compose ps 