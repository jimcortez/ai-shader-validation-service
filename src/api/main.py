"""
AI Shader Validation Tool - Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="AI Shader Validation Tool",
    description="Advanced shader validation and analysis tool supporting GLSL, ISF, and MadMapper formats",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("AI Shader Validation Tool starting up...")
    logger.info(f"Startup time: {datetime.utcnow()}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("AI Shader Validation Tool shutting down...")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Shader Validation Tool",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Basic health checks
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "services": {
                "api": "healthy",
                "database": "healthy",  # Will be updated in Step 3
                "validation_engine": "healthy"  # Will be updated in Step 4
            }
        }
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/api/v1/info")
async def get_info():
    """Get application information"""
    return {
        "name": "AI Shader Validation Tool",
        "version": "1.0.0",
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
        "documentation": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 