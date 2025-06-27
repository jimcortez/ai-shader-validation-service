"""
Error models and exception handlers
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Union
from src.api.models.responses import ErrorResponse
from datetime import datetime

class ValidationException(HTTPException):
    """Custom exception for validation errors"""
    
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=detail)

class ShaderParseException(HTTPException):
    """Custom exception for shader parsing errors"""
    
    def __init__(self, detail: str, status_code: int = 422):
        super().__init__(status_code=status_code, detail=detail)

class ProcessingException(HTTPException):
    """Custom exception for processing errors"""
    
    def __init__(self, detail: str, status_code: int = 500):
        super().__init__(status_code=status_code, detail=detail)

class ResourceNotFoundException(HTTPException):
    """Custom exception for resource not found"""
    
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)

class RateLimitException(HTTPException):
    """Custom exception for rate limiting"""
    
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(status_code=429, detail=detail)

async def validation_exception_handler(request: Request, exc: ValidationException):
    """Handler for validation exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="Validation Error",
            detail=exc.detail,
            code="VALIDATION_ERROR",
            timestamp=datetime.utcnow()
        ).dict()
    )

async def shader_parse_exception_handler(request: Request, exc: ShaderParseException):
    """Handler for shader parsing exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="Shader Parse Error",
            detail=exc.detail,
            code="SHADER_PARSE_ERROR",
            timestamp=datetime.utcnow()
        ).dict()
    )

async def processing_exception_handler(request: Request, exc: ProcessingException):
    """Handler for processing exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="Processing Error",
            detail=exc.detail,
            code="PROCESSING_ERROR",
            timestamp=datetime.utcnow()
        ).dict()
    )

async def resource_not_found_exception_handler(request: Request, exc: ResourceNotFoundException):
    """Handler for resource not found exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="Resource Not Found",
            detail=exc.detail,
            code="RESOURCE_NOT_FOUND",
            timestamp=datetime.utcnow()
        ).dict()
    )

async def rate_limit_exception_handler(request: Request, exc: RateLimitException):
    """Handler for rate limit exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="Rate Limit Exceeded",
            detail=exc.detail,
            code="RATE_LIMIT_EXCEEDED",
            timestamp=datetime.utcnow()
        ).dict(),
        headers={"Retry-After": "60"}
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handler for general exceptions"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail="An unexpected error occurred",
            code="INTERNAL_ERROR",
            timestamp=datetime.utcnow()
        ).dict()
    ) 