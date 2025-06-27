"""
AI Shader Validation Tool - Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from datetime import datetime
from typing import Dict, Any
import time

# Import configuration and logging
from src.config.settings import settings
from src.config.logging import setup_logging, get_logger

# Import middleware
from src.api.middleware.logging import LoggingMiddleware
from src.api.middleware.rate_limiting import RateLimitMiddleware

# Import exception handlers
from src.api.models.errors import (
    ValidationException,
    ShaderParseException,
    ProcessingException,
    ResourceNotFoundException,
    RateLimitException,
    validation_exception_handler,
    shader_parse_exception_handler,
    processing_exception_handler,
    resource_not_found_exception_handler,
    rate_limit_exception_handler,
    general_exception_handler
)

# Import response models
from src.api.models.responses import HealthResponse, ErrorResponse

# Import routes
from src.api.routes import health as health_routes
from src.api.routes import validation as validation_routes
from src.api.routes import visualization as visualization_routes

# Setup logging
logger = setup_logging(
    log_level=settings.log_level,
    log_format=settings.log_format
)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Advanced shader validation and analysis tool supporting GLSL, ISF, and MadMapper formats",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.allowed_credentials,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# Add exception handlers
app.add_exception_handler(ValidationException, validation_exception_handler)
app.add_exception_handler(ShaderParseException, shader_parse_exception_handler)
app.add_exception_handler(ProcessingException, processing_exception_handler)
app.add_exception_handler(ResourceNotFoundException, resource_not_found_exception_handler)
app.add_exception_handler(RateLimitException, rate_limit_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Track startup time
startup_time = None

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    global startup_time
    startup_time = time.time()
    
    logger.info(f"{settings.app_name} starting up...")
    logger.info(f"Version: {settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Startup time: {datetime.utcnow()}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info(f"{settings.app_name} shutting down...")
    logger.info(f"Shutdown time: {datetime.utcnow()}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "documentation": "/docs"
    }

@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Calculate uptime
        uptime = None
        if startup_time:
            uptime = time.time() - startup_time
        
        # Basic health checks
        health_status = HealthResponse(
            status="healthy",
            version=settings.app_version,
            timestamp=datetime.utcnow(),
            services={
                "api": "healthy",
                "database": "healthy",  # Will be updated in Step 3
                "validation_engine": "healthy"  # Will be updated in Step 4
            },
            uptime=uptime
        )
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/api/v1/info")
async def get_info():
    """Get application information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Advanced shader validation and analysis tool",
        "supported_formats": ["GLSL", "ISF", "MadMapper"],
        "features": [
            "Syntax validation",
            "Semantic analysis",
            "Logic flow analysis",
            "Performance analysis",
            "Visual analysis",
            "AI-powered optimization"
        ],
        "api_version": "v1",
        "documentation": "/docs",
        "configuration": {
            "debug": settings.debug,
            "log_level": settings.log_level,
            "rate_limit": settings.rate_limit_per_minute
        }
    }

@app.get("/api/v1/config")
async def get_config():
    """Get application configuration (non-sensitive)"""
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "debug": settings.debug,
        "log_level": settings.log_level,
        "rate_limit_per_minute": settings.rate_limit_per_minute,
        "max_shader_size": settings.max_shader_size,
        "max_batch_size": settings.max_batch_size,
        "validation_timeout": settings.validation_timeout,
        "default_image_width": settings.default_image_width,
        "default_image_height": settings.default_image_height,
        "max_image_size": settings.max_image_size
    }

# Include health routes
app.include_router(health_routes.router, prefix="/api/v1")

# Include validation routes
app.include_router(validation_routes.router, prefix="/api/v1")

# Include visualization routes
app.include_router(visualization_routes.router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    ) 