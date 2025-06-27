"""
Response models for API endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ValidationStatus(str, Enum):
    """Validation status"""
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    FAILED = "failed"

class ErrorSeverity(str, Enum):
    """Error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ValidationError(BaseModel):
    """Validation error model"""
    
    line: Optional[int] = Field(None, description="Line number where error occurred")
    column: Optional[int] = Field(None, description="Column number where error occurred")
    message: str = Field(..., description="Error message")
    severity: ErrorSeverity = Field(default=ErrorSeverity.ERROR, description="Error severity")
    code: Optional[str] = Field(None, description="Error code")
    suggestion: Optional[str] = Field(None, description="Suggested fix")

class ValidationResult(BaseModel):
    """Validation result model"""
    
    status: ValidationStatus = Field(..., description="Validation status")
    errors: List[ValidationError] = Field(default=[], description="Validation errors")
    warnings: List[ValidationError] = Field(default=[], description="Validation warnings")
    info: List[ValidationError] = Field(default=[], description="Information messages")
    performance_score: Optional[float] = Field(None, ge=0, le=100, description="Performance score")
    quality_score: Optional[float] = Field(None, ge=0, le=100, description="Quality score")
    suggestions: List[str] = Field(default=[], description="Improvement suggestions")

class ValidationResponse(BaseModel):
    """Response model for shader validation"""
    
    shader_id: str = Field(..., description="Unique shader identifier")
    format: str = Field(..., description="Shader format")
    validation_level: str = Field(..., description="Validation level used")
    result: ValidationResult = Field(..., description="Validation result")
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Validation timestamp")

class BatchValidationResponse(BaseModel):
    """Response model for batch validation"""
    
    batch_id: str = Field(..., description="Batch identifier")
    total_shaders: int = Field(..., description="Total number of shaders")
    completed: int = Field(..., description="Number of completed validations")
    failed: int = Field(..., description="Number of failed validations")
    results: List[ValidationResponse] = Field(..., description="Validation results")
    processing_time: float = Field(..., description="Total processing time")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Batch timestamp")

class AnalysisResponse(BaseModel):
    """Response model for shader analysis"""
    
    shader_id: str = Field(..., description="Shader identifier")
    analysis_types: List[str] = Field(..., description="Types of analysis performed")
    syntax_analysis: Optional[Dict[str, Any]] = Field(None, description="Syntax analysis results")
    semantic_analysis: Optional[Dict[str, Any]] = Field(None, description="Semantic analysis results")
    performance_analysis: Optional[Dict[str, Any]] = Field(None, description="Performance analysis results")
    security_analysis: Optional[Dict[str, Any]] = Field(None, description="Security analysis results")
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")

class VisualizationResponse(BaseModel):
    """Response model for shader visualization"""
    
    image_id: str = Field(..., description="Generated image identifier")
    image_url: str = Field(..., description="URL to access the generated image")
    width: int = Field(..., description="Image width")
    height: int = Field(..., description="Image height")
    format: str = Field(..., description="Image format")
    file_size: int = Field(..., description="File size in bytes")
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")

class ISFValidationResponse(BaseModel):
    """Response model for ISF validation"""
    
    isf_id: str = Field(..., description="ISF identifier")
    metadata: Dict[str, Any] = Field(..., description="ISF metadata")
    glsl_validation: Optional[ValidationResult] = Field(None, description="GLSL validation result")
    parameter_validation: Optional[ValidationResult] = Field(None, description="Parameter validation result")
    overall_status: ValidationStatus = Field(..., description="Overall validation status")
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Validation timestamp")

class HealthResponse(BaseModel):
    """Response model for health check"""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    services: Dict[str, str] = Field(..., description="Status of individual services")
    uptime: Optional[float] = Field(None, description="Service uptime in seconds")

class ErrorResponse(BaseModel):
    """Standard error response model"""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp") 