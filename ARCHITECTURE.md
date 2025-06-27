# AI Shader Validation Tool - Technical Architecture

## 1. System Overview

### 1.1 High-Level Architecture
The AI Shader Validation Tool follows a simplified, developer-friendly architecture optimized for single-machine deployment with VVISF-GL as the core ISF execution engine:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Systems    │    │   Web Clients   │    │   Local Tools   │
│   (Cursor.ai)   │    │                 │    │                 │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │      FastAPI Server       │
                    │   (Local Development)     │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    Core Validation        │
                    │      Engine               │
                    └─────────────┬─────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
┌─────────▼─────────┐  ┌─────────▼─────────┐  ┌─────────▼─────────┐
│   Shader Parsers  │  │   Analyzers       │  │   Renderers       │
│                   │  │                   │  │                   │
└─────────┬─────────┘  └─────────┬─────────┘  └─────────┬─────────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │    C++ Bindings Layer     │
                    │   (pybind11 + VVISF-GL)   │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    VVISF-GL Engine        │
                    │   (ISF + GLSL Execution)  │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    Local Storage          │
                    │   (SQLite + File System)  │
                    └───────────────────────────┘
```

### 1.2 Core Components

#### 1.2.1 FastAPI Server
- **Technology**: FastAPI with WebSocket support
- **Purpose**: Single entry point for all client requests
- **Features**:
  - Request routing and validation
  - WebSocket connection management
  - Local authentication (optional)
  - Request/response logging
  - Auto-generated API documentation

#### 1.2.2 Core Validation Engine
- **Technology**: Python with C++ bindings
- **Purpose**: Central orchestration of validation processes
- **Features**:
  - Shader parsing and AST generation
  - Multi-stage validation pipeline
  - Error aggregation and reporting
  - Local performance optimization

#### 1.2.3 C++ Bindings Layer
- **Technology**: pybind11 + VVISF-GL
- **Purpose**: Bridge between Python API and C++ ISF engine
- **Features**:
  - ISF shader compilation and execution
  - GLSL validation and error reporting
  - Texture management and rendering
  - Performance-critical operations

#### 1.2.4 VVISF-GL Engine
- **Technology**: VVISF-GL C++ library
- **Purpose**: Native ISF and GLSL execution
- **Features**:
  - Full ISF protocol implementation
  - Cross-platform OpenGL support
  - Efficient texture operations
  - Real-time shader compilation

#### 1.2.5 Local Storage Layer
- **Primary Database**: SQLite
  - Shader metadata storage
  - Validation results history
  - Local usage analytics
- **File Storage**: Local file system
  - Generated images and assets
  - Temporary validation files
  - Configuration files

## 2. Data Flow Architecture

### 2.1 Validation Request Flow

```mermaid
sequenceDiagram
    participant AI as AI System
    participant API as FastAPI Server
    participant VAL as Validation Engine
    participant PARSER as Shader Parser
    participant ANALYZER as Analyzer
    participant BINDINGS as C++ Bindings
    participant VVISF as VVISF-GL Engine
    participant DB as SQLite DB
    participant FS as File System

    AI->>API: POST /validate (shader code)
    API->>VAL: Forward to validation engine
    VAL->>PARSER: Parse shader code
    PARSER-->>VAL: AST + syntax errors
    
    alt ISF Format
        VAL->>BINDINGS: Compile ISF shader
        BINDINGS->>VVISF: Execute ISF protocol
        VVISF-->>BINDINGS: Compilation results
        BINDINGS-->>VAL: ISF validation results
    else GLSL Format
        VAL->>ANALYZER: Analyze GLSL AST
        ANALYZER-->>VAL: Analysis results
    end
    
    VAL->>DB: Store validation results
    VAL->>FS: Store generated assets
    VAL-->>AI: Return validation results
```

### 2.2 Visual Analysis Flow

```mermaid
sequenceDiagram
    participant AI as AI System
    participant API as FastAPI Server
    participant RENDER as Renderer Service
    participant BINDINGS as C++ Bindings
    participant VVISF as VVISF-GL Engine
    participant GL as OpenGL Context
    participant IMG as Image Processor
    participant FS as File System

    AI->>API: POST /visualize (shader + params)
    API->>RENDER: Forward visualization request
    RENDER->>BINDINGS: Render shader with VVISF-GL
    BINDINGS->>VVISF: Execute shader with parameters
    VVISF->>GL: Compile and execute shader
    GL-->>VVISF: Raw pixel data
    VVISF-->>BINDINGS: Rendered texture
    BINDINGS-->>RENDER: Processed image data
    RENDER->>IMG: Process and format image
    IMG-->>RENDER: Formatted image
    RENDER->>FS: Store generated image
    RENDER-->>AI: Return image path + metadata
```

## 3. Component Architecture

### 3.1 Parser Architecture

```python
# Base Parser Interface
class BaseShaderParser(ABC):
    @abstractmethod
    def parse(self, shader_code: str) -> ShaderAST:
        pass
    
    @abstractmethod
    def validate_syntax(self, ast: ShaderAST) -> List[SyntaxError]:
        pass

# ISF Parser Implementation (using VVISF-GL)
class ISFParser(BaseShaderParser):
    def __init__(self):
        self.vvisf_engine = VVISFEngine()  # C++ bindings
    
    def parse(self, shader_code: str) -> ShaderAST:
        # Use VVISF-GL to parse ISF JSON and extract GLSL
        isf_data = json.loads(shader_code)
        glsl_code = isf_data.get('PASSES', [{}])[0].get('CODE', '')
        return self.parse_glsl(glsl_code)
    
    def validate_syntax(self, ast: ShaderAST) -> List[SyntaxError]:
        # Use VVISF-GL for ISF-specific validation
        return self.vvisf_engine.validate_isf(ast)

# GLSL Parser Implementation
class GLSLParser(BaseShaderParser):
    def __init__(self):
        self.lexer = GLSLLexer()
        self.parser = GLSLParser()
    
    def parse(self, shader_code: str) -> ShaderAST:
        tokens = self.lexer.tokenize(shader_code)
        return self.parser.parse(tokens)
```

### 3.2 C++ Bindings Architecture

```cpp
// vvisf_bindings.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "VVISF/VVISF.hpp"

namespace py = pybind11;

class VVISFEngine {
private:
    VVISF::ISFSceneRef scene;
    VVISF::VVGL::GLBufferRef outputBuffer;
    
public:
    VVISFEngine() {
        // Initialize VVISF with OpenGL context
        scene = VVISF::CreateISFScene();
    }
    
    ValidationResult validate_isf(const std::string& isf_json) {
        try {
            // Parse ISF JSON and validate
            auto isf_doc = VVISF::CreateISFDocFromJSON(isf_json);
            auto validation_result = scene->validateISFDoc(isf_doc);
            
            return ValidationResult{
                .valid = validation_result.isValid,
                .errors = validation_result.errors,
                .warnings = validation_result.warnings
            };
        } catch (const std::exception& e) {
            return ValidationResult{
                .valid = false,
                .errors = {e.what()}
            };
        }
    }
    
    ImageData render_shader(const std::string& isf_json, 
                           const std::map<std::string, float>& params) {
        // Load ISF document
        auto isf_doc = VVISF::CreateISFDocFromJSON(isf_json);
        scene->loadISFDoc(isf_doc);
        
        // Set parameters
        for (const auto& [key, value] : params) {
            scene->setValueForKey(key, value);
        }
        
        // Render frame
        auto frame = scene->renderFrame();
        
        // Convert to image data
        return convert_frame_to_image(frame);
    }
};

PYBIND11_MODULE(vvisf_engine, m) {
    py::class_<VVISFEngine>(m, "VVISFEngine")
        .def(py::init<>())
        .def("validate_isf", &VVISFEngine::validate_isf)
        .def("render_shader", &VVISFEngine::render_shader);
}
```

### 3.3 Renderer Architecture

```python
# Enhanced Shader Renderer with VVISF-GL
class ShaderRenderer:
    def __init__(self):
        self.vvisf_engine = VVISFEngine()  # C++ bindings
        self.image_processor = ImageProcessor()
    
    def render_preview(self, shader_code: str, params: dict, format: str) -> Image:
        if format == 'isf':
            # Use VVISF-GL for ISF rendering
            image_data = self.vvisf_engine.render_shader(shader_code, params)
            return self.image_processor.process_from_data(image_data)
        else:
            # Use OpenGL for GLSL rendering
            program = self.gl_context.compile_shader(shader_code)
            pixels = self.gl_context.render(program, params)
            return self.image_processor.process(pixels)
```

## 4. Database Schema

### 4.1 Core Tables (SQLite)

```sql
-- Shader metadata
CREATE TABLE shaders (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    format TEXT NOT NULL,
    version TEXT,
    isf_metadata TEXT,  -- JSON metadata for ISF shaders
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Validation results
CREATE TABLE validation_results (
    id TEXT PRIMARY KEY,
    shader_id TEXT REFERENCES shaders(id),
    validation_type TEXT NOT NULL,
    status TEXT NOT NULL,
    errors TEXT,  -- JSON string
    warnings TEXT, -- JSON string
    metrics TEXT,  -- JSON string
    isf_validation TEXT, -- ISF-specific validation results
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analysis results
CREATE TABLE analysis_results (
    id TEXT PRIMARY KEY,
    shader_id TEXT REFERENCES shaders(id),
    analysis_type TEXT NOT NULL,
    results TEXT NOT NULL,  -- JSON string
    performance_metrics TEXT, -- JSON string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Generated images
CREATE TABLE generated_images (
    id TEXT PRIMARY KEY,
    shader_id TEXT REFERENCES shaders(id),
    file_path TEXT NOT NULL,
    parameters TEXT,  -- JSON string
    format TEXT,
    size_x INTEGER,
    size_y INTEGER,
    render_time REAL, -- Rendering time in seconds
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 5. API Design

### 5.1 RESTful Endpoints

```python
# Validation endpoints
POST /api/v1/validate
GET /api/v1/validate/{validation_id}

# Analysis endpoints
POST /api/v1/analyze
GET /api/v1/analyze/{analysis_id}

# Visualization endpoints
POST /api/v1/visualize
GET /api/v1/visualize/{image_id}
GET /api/v1/images/{image_id}

# ISF-specific endpoints
POST /api/v1/isf/validate
POST /api/v1/isf/render
GET /api/v1/isf/metadata/{shader_id}

# Health and status
GET /api/v1/health
GET /api/v1/status

# Local management
GET /api/v1/storage/status
POST /api/v1/storage/cleanup
```

### 5.2 WebSocket Events

```python
# Real-time validation events
VALIDATION_STARTED = "validation_started"
VALIDATION_PROGRESS = "validation_progress"
VALIDATION_COMPLETED = "validation_completed"
VALIDATION_ERROR = "validation_error"

# ISF-specific events
ISF_COMPILATION_STARTED = "isf_compilation_started"
ISF_RENDERING_PROGRESS = "isf_rendering_progress"
ISF_METADATA_EXTRACTED = "isf_metadata_extracted"
```

## 6. Security Architecture

### 6.1 Local Security

```python
# Local-only access by default
class LocalSecurityMiddleware:
    def __init__(self, allow_remote: bool = False):
        self.allow_remote = allow_remote
    
    async def check_access(self, request: Request):
        if not self.allow_remote:
            client_ip = request.client.host
            if client_ip not in ['127.0.0.1', 'localhost', '::1']:
                raise HTTPException(status_code=403, detail="Local access only")
```

### 6.2 Input Validation & Sanitization

```python
# Enhanced shader code validation
class ShaderValidator:
    def validate_input(self, shader_code: str, format: str) -> ValidationResult:
        # Check for malicious patterns
        if self.contains_malicious_code(shader_code):
            raise SecurityException("Malicious code detected")
        
        # Check resource limits
        if len(shader_code) > MAX_SHADER_SIZE:
            raise ValidationException("Shader too large")
        
        # ISF-specific validation
        if format == 'isf':
            try:
                isf_data = json.loads(shader_code)
                if not self.validate_isf_structure(isf_data):
                    raise ValidationException("Invalid ISF structure")
            except json.JSONDecodeError:
                raise ValidationException("Invalid ISF JSON")
        
        return ValidationResult(valid=True)
```

## 7. Performance Architecture

### 7.1 Local Caching Strategy

```python
# Enhanced local caching with ISF support
class LocalCacheManager:
    def __init__(self, cache_dir: str = "./cache"):
        self.cache_dir = cache_dir
        self.memory_cache = LRUCache(maxsize=100)
        self.isf_cache = LRUCache(maxsize=50)  # ISF compilation cache
    
    async def get_isf_compilation(self, isf_hash: str):
        # Cache ISF compilation results
        result = self.isf_cache.get(isf_hash)
        if result:
            return result
        
        # Try file cache
        cache_file = os.path.join(self.cache_dir, f"isf_{isf_hash}.json")
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                result = json.load(f)
                self.isf_cache.set(isf_hash, result)
                return result
        
        return None
```

### 7.2 Resource Management

```python
# Enhanced resource management for ISF
class ResourceManager:
    def __init__(self):
        self.max_memory = 1024 * 1024 * 1024  # 1GB
        self.max_disk = 10 * 1024 * 1024 * 1024  # 10GB
        self.max_concurrent = 4  # Max concurrent validations
        self.max_isf_size = 5 * 1024 * 1024  # 5MB for ISF files
    
    def check_resources(self) -> bool:
        # Check available memory
        memory_usage = psutil.virtual_memory().used
        if memory_usage > self.max_memory:
            return False
        
        # Check available disk space
        disk_usage = psutil.disk_usage('/').used
        if disk_usage > self.max_disk:
            return False
        
        return True
    
    def validate_isf_resources(self, isf_data: dict) -> bool:
        # Check ISF-specific resource requirements
        passes = isf_data.get('PASSES', [])
        if len(passes) > 10:  # Limit number of passes
            return False
        
        # Check texture sizes
        for pass_data in passes:
            if 'TARGET' in pass_data:
                target = pass_data['TARGET']
                if target.get('WIDTH', 0) > 4096 or target.get('HEIGHT', 0) > 4096:
                    return False
        
        return True
```

## 8. Monitoring & Observability

### 8.1 Local Metrics Collection

```python
# Enhanced metrics with ISF support
class LocalMetricsCollector:
    def __init__(self, metrics_file: str = "./metrics.json"):
        self.metrics_file = metrics_file
        self.metrics = {
            'validations_total': 0,
            'validation_errors': 0,
            'isf_validations': 0,
            'isf_renders': 0,
            'average_validation_time': 0.0,
            'average_isf_render_time': 0.0,
            'storage_usage': 0.0
        }
    
    def record_isf_validation(self, duration: float, success: bool):
        self.metrics['isf_validations'] += 1
        self.metrics['validations_total'] += 1
        if not success:
            self.metrics['validation_errors'] += 1
        
        # Update average time
        current_avg = self.metrics['average_isf_render_time']
        total_isf = self.metrics['isf_validations']
        self.metrics['average_isf_render_time'] = (
            (current_avg * (total_isf - 1) + duration) / total_isf
        )
        
        self.save_metrics()
```

### 8.2 Logging Strategy

```python
# Enhanced logging with ISF support
class LocalLogger:
    def __init__(self, log_dir: str = "./logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'app.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log_isf_validation(self, shader_id: str, result: ValidationResult):
        self.logger.info("ISF validation completed", extra={
            "shader_id": shader_id,
            "format": "isf",
            "status": result.status,
            "error_count": len(result.errors),
            "warning_count": len(result.warnings),
            "isf_metadata": result.isf_metadata
        })
```

## 9. Deployment Architecture

### 9.1 Docker Compose Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  shader-validator:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app/src
      - ./storage:/app/storage
      - ./logs:/app/logs
      - ./cache:/app/cache
    environment:
      - DATABASE_URL=sqlite:///./storage/shader_validator.db
      - STORAGE_PATH=/app/storage
      - LOG_LEVEL=INFO
      - DEBUG=true
      - ALLOW_REMOTE_ACCESS=false
      - VVISF_GL_PATH=/usr/local/lib
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Optional: PostgreSQL for advanced users
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=shader_validator
      - POSTGRES_USER=shader_user
      - POSTGRES_PASSWORD=shader_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U shader_user -d shader_validator"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    profiles:
      - postgres

volumes:
  postgres_data:
```

### 9.2 Docker Production

```dockerfile
# Dockerfile with VVISF-GL support
FROM python:3.11-slim

# Install system dependencies for OpenGL and VVISF-GL
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglu1-mesa \
    libgles2-mesa \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Clone and build VVISF-GL
RUN git clone https://github.com/mrRay/VVISF-GL.git /tmp/vvisf-gl && \
    cd /tmp/vvisf-gl && \
    mkdir build && cd build && \
    cmake .. -DVVGL_SDK_GLFW=ON && \
    make -j$(nproc) && \
    make install && \
    cd /app && rm -rf /tmp/vvisf-gl

# Copy requirements and install Python dependencies
COPY requirements/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create necessary directories
RUN mkdir -p /app/storage /app/logs /app/cache

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 9.3 Local Development Setup

```bash
# setup.sh - One-command setup with VVISF-GL
#!/bin/bash

# AI Shader Validation Tool - Setup Script
# This script sets up the development environment using Docker Compose

set -e  # Exit on any error

echo "🚀 Setting up AI Shader Validation Tool with VVISF-GL..."

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
    if [ -f env.example ]; then
        cp env.example .env
        print_success "Created .env file from template"
        print_warning "Please review and update .env configuration if needed"
    else
        print_warning "No env.example found, creating basic .env file..."
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
MAX_CONCURRENT_VALIDATIONS=4

# VVISF-GL Configuration
VVISF_GL_PATH=/usr/local/lib
ENABLE_ISF_VALIDATION=true
ENABLE_ISF_RENDERING=true

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
print_status "Building and starting services (this may take a while for VVISF-GL compilation)..."
docker-compose up --build -d $POSTGRES_PROFILE

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

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

# Test ISF functionality
print_status "Testing ISF functionality..."
curl -X POST http://localhost:8000/api/v1/isf/validate \
    -H "Content-Type: application/json" \
    -d '{"shader_code": "{\"PASSES\": [{\"CODE\": \"void main() { gl_FragColor = vec4(1.0); }\"}]}", "format": "isf"}' \
    &> /dev/null && print_success "ISF validation working!" || print_warning "ISF validation test failed"

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
echo "🎨 ISF Support:"
echo "  • ISF validation: POST /api/v1/isf/validate"
echo "  • ISF rendering: POST /api/v1/isf/render"
echo "  • ISF metadata: GET /api/v1/isf/metadata/{shader_id}"
echo ""
echo "📖 Next Steps:"
echo "  1. Visit http://localhost:8000/docs to see the API documentation"
echo "  2. Try the example API calls in the README.md"
echo "  3. Test ISF shader validation and rendering"
echo "  4. Check the logs if you encounter any issues"
echo ""

# Optional: Show current status
print_status "Current service status:"
docker-compose ps
```

## 10. Local Development Considerations

### 10.1 Resource Optimization
- **Memory Management**: Efficient memory usage for local development
- **Disk Space**: Configurable storage limits and cleanup
- **CPU Usage**: Multi-core processing optimization
- **GPU Acceleration**: Optional GPU support for rendering
- **ISF Compilation**: Caching of ISF compilation results

### 10.2 Development Workflow
- **Hot Reloading**: Code changes without restart
- **Local Testing**: Comprehensive test suite for local development
- **Debug Mode**: Enhanced logging and error reporting
- **Development Tools**: Built-in development utilities
- **ISF Testing**: Built-in ISF validation and rendering tests

### 10.3 Data Persistence
- **SQLite Database**: Lightweight, file-based database
- **File Storage**: Local file system for generated assets
- **Backup Strategy**: Simple backup and restore procedures
- **Data Migration**: Easy database schema updates
- **ISF Metadata**: Storage of ISF-specific metadata and validation results

This architecture provides a robust, developer-friendly foundation for the AI shader validation tool, optimized for single-machine deployment while maintaining all the core functionality needed for effective shader validation and analysis, with enhanced ISF support through VVISF-GL. 