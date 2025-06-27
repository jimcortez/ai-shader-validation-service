# AI Shader Validation Tool - Project Structure

## Directory Organization

```
ai-shadermaker/
├── README.md                           # Project overview and quick start
├── REQUIREMENTS.md                     # Detailed requirements document
├── PROJECT_STRUCTURE.md               # This file - project organization
├── ARCHITECTURE.md                    # Technical architecture overview
├── API_SPECIFICATION.md               # API documentation
├── CONTRIBUTING.md                    # Development guidelines
├── LICENSE                            # Project license
│
├── src/                               # Main source code
│   ├── core/                          # Core validation engine
│   │   ├── __init__.py
│   │   ├── validator.py               # Main validation orchestrator
│   │   ├── parser/                    # Shader format parsers
│   │   │   ├── __init__.py
│   │   │   ├── glsl_parser.py         # GLSL parser
│   │   │   ├── isf_parser.py          # ISF parser
│   │   │   ├── madmapper_parser.py    # MadMapper parser
│   │   │   └── base_parser.py         # Base parser interface
│   │   ├── analyzers/                 # Analysis modules
│   │   │   ├── __init__.py
│   │   │   ├── syntax_analyzer.py     # Syntax validation
│   │   │   ├── semantic_analyzer.py   # Semantic analysis
│   │   │   ├── logic_analyzer.py      # Logic flow analysis
│   │   │   ├── portability_analyzer.py # Portability checking
│   │   │   └── quality_analyzer.py    # Code quality metrics
│   │   ├── renderers/                 # Visual analysis
│   │   │   ├── __init__.py
│   │   │   ├── shader_renderer.py     # Shader preview generation
│   │   │   ├── error_visualizer.py    # Error visualization
│   │   │   ├── performance_charts.py  # Performance visualization
│   │   │   └── dependency_graphs.py   # Dependency visualization
│   │   └── utils/                     # Utility functions
│   │       ├── __init__.py
│   │       ├── gl_utils.py            # OpenGL utilities
│   │       ├── image_utils.py         # Image processing utilities
│   │       └── validation_utils.py    # Validation helpers
│   │
│   ├── api/                           # API layer
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application
│   │   ├── routes/                    # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── validation.py          # Validation endpoints
│   │   │   ├── analysis.py            # Analysis endpoints
│   │   │   ├── visualization.py       # Visualization endpoints
│   │   │   └── health.py              # Health check endpoints
│   │   ├── models/                    # Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── requests.py            # Request models
│   │   │   ├── responses.py           # Response models
│   │   │   └── errors.py              # Error models
│   │   ├── middleware/                # API middleware
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                # Authentication
│   │   │   ├── rate_limiting.py       # Rate limiting
│   │   │   └── logging.py             # Request logging
│   │   └── websocket/                 # WebSocket handlers
│   │       ├── __init__.py
│   │       └── realtime.py            # Real-time validation
│   │
│   ├── database/                      # Database layer
│   │   ├── __init__.py
│   │   ├── models.py                  # Database models
│   │   ├── connection.py              # Database connection
│   │   └── migrations/                # Database migrations
│   │
│   ├── services/                      # Business logic services
│   │   ├── __init__.py
│   │   ├── validation_service.py      # Validation orchestration
│   │   ├── analysis_service.py        # Analysis coordination
│   │   ├── visualization_service.py   # Visual analysis
│   │   ├── ai_integration_service.py  # AI-specific features
│   │   └── reporting_service.py       # Report generation
│   │
│   └── config/                        # Configuration
│       ├── __init__.py
│       ├── settings.py                # Application settings
│       ├── logging.py                 # Logging configuration
│       └── environments/              # Environment-specific configs
│           ├── development.py
│           ├── production.py
│           └── testing.py
│
├── tests/                             # Test suite
│   ├── __init__.py
│   ├── unit/                          # Unit tests
│   │   ├── __init__.py
│   │   ├── test_parsers/              # Parser tests
│   │   ├── test_analyzers/            # Analyzer tests
│   │   ├── test_renderers/            # Renderer tests
│   │   └── test_services/             # Service tests
│   ├── integration/                   # Integration tests
│   │   ├── __init__.py
│   │   ├── test_api/                  # API integration tests
│   │   ├── test_validation/           # End-to-end validation tests
│   │   └── test_ai_integration/       # AI integration tests
│   ├── fixtures/                      # Test data
│   │   ├── shaders/                   # Sample shaders for testing
│   │   ├── expected_results/          # Expected validation results
│   │   └── mock_data/                 # Mock data for tests
│   └── conftest.py                    # Pytest configuration
│
├── docs/                              # Documentation
│   ├── api/                           # API documentation
│   │   ├── endpoints.md               # Detailed endpoint docs
│   │   ├── examples.md                # Usage examples
│   │   └── integration.md             # Integration guides
│   ├── development/                   # Development docs
│   │   ├── setup.md                   # Development setup
│   │   ├── architecture.md            # Technical architecture
│   │   ├── contributing.md            # Contribution guidelines
│   │   └── testing.md                 # Testing guidelines
│   ├── user/                          # User documentation
│   │   ├── getting_started.md         # Quick start guide
│   │   ├── shader_formats.md          # Supported formats
│   │   ├── validation_types.md        # Validation capabilities
│   │   └── troubleshooting.md         # Common issues
│   └── assets/                        # Documentation assets
│       ├── images/                    # Screenshots and diagrams
│       └── examples/                  # Example files
│
├── scripts/                           # Utility scripts
│   ├── setup.sh                       # Development environment setup
│   ├── deploy.sh                      # Deployment script
│   ├── test.sh                        # Test execution script
│   └── benchmark.sh                   # Performance benchmarking
│
├── docker/                            # Docker configuration
│   ├── Dockerfile                     # Main application Dockerfile
│   ├── docker-compose.yml             # Development environment
│   ├── docker-compose.prod.yml        # Production environment
│   └── nginx/                         # Nginx configuration
│       └── nginx.conf
│
├── kubernetes/                        # Kubernetes manifests
│   ├── deployment.yaml                # Application deployment
│   ├── service.yaml                   # Service definition
│   ├── ingress.yaml                   # Ingress configuration
│   └── configmap.yaml                 # Configuration
│
├── requirements/                      # Python dependencies
│   ├── requirements.txt               # Production dependencies
│   ├── requirements-dev.txt           # Development dependencies
│   └── requirements-test.txt          # Testing dependencies
│
├── .github/                           # GitHub configuration
│   ├── workflows/                     # CI/CD workflows
│   │   ├── ci.yml                     # Continuous integration
│   │   ├── cd.yml                     # Continuous deployment
│   │   └── security.yml               # Security scanning
│   ├── ISSUE_TEMPLATE/                # Issue templates
│   └── PULL_REQUEST_TEMPLATE.md       # PR template
│
├── .vscode/                           # VS Code configuration
│   ├── settings.json                  # Editor settings
│   ├── launch.json                    # Debug configuration
│   └── extensions.json                # Recommended extensions
│
├── .gitignore                         # Git ignore rules
├── pyproject.toml                     # Python project configuration
├── setup.py                           # Package setup
└── Makefile                           # Build automation
```

## Key Components Description

### Core Validation Engine (`src/core/`)
The heart of the system containing:
- **Parsers**: Convert shader code into abstract syntax trees
- **Analyzers**: Perform various types of analysis (syntax, semantic, logic, etc.)
- **Renderers**: Generate visual outputs and analysis charts
- **Utilities**: Helper functions for OpenGL, image processing, and validation

### API Layer (`src/api/`)
RESTful API and WebSocket interfaces:
- **Routes**: HTTP endpoints for different operations
- **Models**: Request/response data structures
- **Middleware**: Authentication, rate limiting, logging
- **WebSocket**: Real-time validation feedback

### Services (`src/services/`)
Business logic coordination:
- **Validation Service**: Orchestrates the validation process
- **Analysis Service**: Coordinates different analysis types
- **Visualization Service**: Manages visual output generation
- **AI Integration Service**: AI-specific features and optimizations

### Database (`src/database/`)
Data persistence layer:
- **Models**: Database schema definitions
- **Connection**: Database connection management
- **Migrations**: Schema version control

### Configuration (`src/config/`)
Application configuration management:
- **Settings**: Centralized configuration
- **Logging**: Logging setup and configuration
- **Environments**: Environment-specific settings

## Development Workflow

1. **Setup**: Use `scripts/setup.sh` to initialize development environment
2. **Development**: Work in `src/` directory with appropriate tests
3. **Testing**: Run tests with `scripts/test.sh` or `make test`
4. **Documentation**: Update docs in `docs/` directory
5. **Deployment**: Use Docker/Kubernetes configurations for deployment

## File Naming Conventions

- **Python files**: snake_case (e.g., `shader_validator.py`)
- **Classes**: PascalCase (e.g., `ShaderValidator`)
- **Functions/Variables**: snake_case (e.g., `validate_shader`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_SHADER_SIZE`)
- **Configuration files**: lowercase with extensions (e.g., `settings.py`)
- **Test files**: `test_` prefix (e.g., `test_validator.py`)

## Module Dependencies

```
api/ → services/ → core/ → utils/
  ↓       ↓         ↓       ↓
database/ ← config/ ← requirements/
```

This structure ensures:
- Clear separation of concerns
- Modular and testable components
- Scalable architecture
- Easy maintenance and extension
- Comprehensive documentation
- Automated testing and deployment 