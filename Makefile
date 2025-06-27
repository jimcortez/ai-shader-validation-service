# AI Shader Validation Tool - Makefile
# Convenient commands for development and deployment

.PHONY: help setup start stop restart build test clean logs status health docs

# Default target
help:
	@echo "AI Shader Validation Tool - Available Commands:"
	@echo ""
	@echo "Setup & Deployment:"
	@echo "  setup     - One-command setup using Docker Compose"
	@echo "  start     - Start services in background"
	@echo "  stop      - Stop all services"
	@echo "  restart   - Restart all services"
	@echo "  build     - Build and start services"
	@echo "  clean     - Clean up containers, images, and volumes"
	@echo ""
	@echo "Development:"
	@echo "  dev       - Start in development mode with hot reload"
	@echo "  logs      - View application logs"
	@echo "  status    - Show service status"
	@echo "  health    - Check API health"
	@echo "  docs      - Open API documentation in browser"
	@echo ""
	@echo "Testing:"
	@echo "  test      - Run all tests"
	@echo "  test-unit - Run unit tests only"
	@echo "  test-int  - Run integration tests only"
	@echo "  test-isf  - Run ISF-specific tests"
	@echo "  coverage  - Run tests with coverage report"
	@echo ""
	@echo "VVISF-GL (ISF Engine):"
	@echo "  build-bindings - Build C++ bindings for VVISF-GL"
	@echo "  test-isf      - Test ISF validation and rendering"
	@echo "  isf-example   - Run ISF example validation"
	@echo ""
	@echo "Database:"
	@echo "  db-reset  - Reset database (SQLite)"
	@echo "  db-backup - Backup database"
	@echo ""
	@echo "Production:"
	@echo "  prod      - Start production services"
	@echo "  prod-stop - Stop production services"

# Setup and deployment
setup:
	@echo "🚀 Setting up AI Shader Validation Tool..."
	@chmod +x scripts/setup.sh
	@./scripts/setup.sh

start:
	@echo "Starting services..."
	@docker-compose up -d
	@echo "Services started! API available at http://localhost:8000"

stop:
	@echo "Stopping services..."
	@docker-compose down
	@echo "Services stopped"

restart:
	@echo "Restarting services..."
	@docker-compose restart
	@echo "Services restarted"

build:
	@echo "Building and starting services..."
	@docker-compose up --build -d
	@echo "Services built and started!"

clean:
	@echo "Cleaning up..."
	@docker-compose down -v --remove-orphans
	@docker system prune -f
	@echo "Cleanup complete"

# Development
dev:
	@echo "Starting development mode with hot reload..."
	@docker-compose up

logs:
	@docker-compose logs -f

status:
	@docker-compose ps

health:
	@echo "Checking API health..."
	@curl -f http://localhost:8000/api/v1/health || echo "API not responding"

docs:
	@echo "Opening API documentation..."
	@if command -v open >/dev/null 2>&1; then \
		open http://localhost:8000/docs; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open http://localhost:8000/docs; \
	else \
		echo "Please open http://localhost:8000/docs in your browser"; \
	fi

# Testing
test:
	@echo "Running all tests..."
	@docker-compose exec -T shader-validator pytest

test-unit:
	@echo "Running unit tests..."
	@docker-compose exec -T shader-validator pytest tests/unit/

test-int:
	@echo "Running integration tests..."
	@docker-compose exec -T shader-validator pytest tests/integration/

test-isf:
	@echo "Running ISF-specific tests..."
	@docker-compose exec -T shader-validator pytest tests/test_isf/

coverage:
	@echo "Running tests with coverage..."
	@docker-compose exec -T shader-validator pytest --cov=src --cov-report=html tests/
	@echo "Coverage report generated in htmlcov/"

# VVISF-GL specific commands
build-bindings:
	@echo "Building C++ bindings for VVISF-GL..."
	@docker-compose exec -T shader-validator bash -c "cd /app/src/bindings && cmake .. && make"
	@echo "C++ bindings built successfully"

test-isf:
	@echo "Testing ISF functionality..."
	@curl -X POST http://localhost:8000/api/v1/isf/validate \
		-H "Content-Type: application/json" \
		-d '{"shader_code": "{\"PASSES\": [{\"CODE\": \"void main() { gl_FragColor = vec4(1.0); }\"}]}", "format": "isf"}' \
		| jq . 2>/dev/null || echo "ISF test failed"

isf-example:
	@echo "Running ISF example validation..."
	@curl -X POST http://localhost:8000/api/v1/isf/validate \
		-H "Content-Type: application/json" \
		-d @tests/fixtures/isf_example.json \
		| jq . 2>/dev/null || echo "ISF example test failed"

# Database operations
db-reset:
	@echo "Resetting database..."
	@docker-compose exec -T shader-validator python -c "import os; os.remove('storage/shader_validator.db') if os.path.exists('storage/shader_validator.db') else None"
	@docker-compose exec -T shader-validator python -m src.database.init
	@echo "Database reset complete"

db-backup:
	@echo "Creating database backup..."
	@cp storage/shader_validator.db storage/shader_validator.db.backup.$$(date +%Y%m%d_%H%M%S)
	@echo "Backup created"

# Production
prod:
	@echo "Starting production services..."
	@docker-compose -f docker-compose.prod.yml up -d
	@echo "Production services started!"

prod-stop:
	@echo "Stopping production services..."
	@docker-compose -f docker-compose.prod.yml down
	@echo "Production services stopped"

# Utility commands
shell:
	@echo "Opening shell in container..."
	@docker-compose exec shader-validator bash

storage-status:
	@echo "Storage usage:"
	@docker-compose exec -T shader-validator python -c "import os; print(f'Storage: {os.path.getsize(\"storage/shader_validator.db\")/1024:.1f}KB')"

storage-cleanup:
	@echo "Cleaning up storage..."
	@docker-compose exec -T shader-validator python -m src.storage.cleanup
	@echo "Storage cleanup complete"

# PostgreSQL profile commands
postgres:
	@echo "Starting with PostgreSQL..."
	@docker-compose --profile postgres up -d
	@echo "Services started with PostgreSQL!"

postgres-stop:
	@echo "Stopping PostgreSQL services..."
	@docker-compose --profile postgres down
	@echo "PostgreSQL services stopped"

# Monitoring
monitor:
	@echo "Monitoring services..."
	@watch -n 2 'docker-compose ps && echo "" && curl -s http://localhost:8000/api/v1/health | jq . 2>/dev/null || echo "API not responding"'

# Development utilities
lint:
	@echo "Running linting..."
	@docker-compose exec -T shader-validator flake8 src/
	@docker-compose exec -T shader-validator black --check src/

format:
	@echo "Formatting code..."
	@docker-compose exec -T shader-validator black src/
	@docker-compose exec -T shader-validator isort src/

# Quick validation test
quick-test:
	@echo "Running quick validation test..."
	@curl -X POST http://localhost:8000/api/v1/validate \
		-H "Content-Type: application/json" \
		-d '{"shader_code": "#version 330 core\nvoid main() { gl_FragColor = vec4(1.0); }", "format": "glsl"}' \
		| jq . 2>/dev/null || echo "API test failed"

# ISF quick test
isf-quick-test:
	@echo "Running quick ISF test..."
	@curl -X POST http://localhost:8000/api/v1/isf/validate \
		-H "Content-Type: application/json" \
		-d '{"shader_code": "{\"PASSES\": [{\"CODE\": \"void main() { gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0); }\"}]}", "format": "isf"}' \
		| jq . 2>/dev/null || echo "ISF test failed"

# Performance benchmarks
benchmark:
	@echo "Running performance benchmarks..."
	@docker-compose exec -T shader-validator pytest tests/benchmark/ -v

# VVISF-GL version check
vvisf-version:
	@echo "Checking VVISF-GL version..."
	@docker-compose exec -T shader-validator python -c "import vvisf_engine; print('VVISF-GL loaded successfully')" 2>/dev/null || echo "VVISF-GL not available"

# Full system test
system-test:
	@echo "Running full system test..."
	@make health
	@make quick-test
	@make isf-quick-test
	@make test-isf
	@echo "System test complete!" 