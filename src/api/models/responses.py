"""
Response models for API endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ValidationStatus(str, Enum):
    """Validation status"""
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"
    ERROR = "error"
    PROCESSING = "processing"

class ErrorSeverity(str, Enum):
    """Error severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class ValidationError(BaseModel):
    """Validation error model"""
    
    message: str = Field(..., description="Error message")
    line: int = Field(..., description="Line number where error occurred")
    column: int = Field(..., description="Column number where error occurred")
    severity: ErrorSeverity = Field(..., description="Error severity")
    error_code: str = Field(..., description="Error code for categorization")
    context: Optional[str] = Field(None, description="Additional context")
    suggestions: Optional[List[str]] = Field(None, description="Suggested fixes")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class ValidationResult(BaseModel):
    """Model for single validation result."""
    
    validation_id: str = Field(..., description="Unique validation identifier")
    is_valid: bool = Field(..., description="Whether the shader is valid")
    status: ValidationStatus = Field(..., description="Validation status")
    format: str = Field(..., description="Shader format")
    target_version: str = Field(..., description="Target GLSL version")
    target_platforms: List[str] = Field(..., description="Target platforms")
    
    # Analysis results
    errors: List[ValidationError] = Field(default_factory=list, description="Validation errors")
    warnings: List[ValidationError] = Field(default_factory=list, description="Validation warnings")
    info: List[ValidationError] = Field(default_factory=list, description="Informational messages")
    
    # Quality and performance
    quality_metrics: Optional[Dict[str, Any]] = Field(None, description="Quality analysis results")
    performance_analysis: Optional["PerformanceAnalysis"] = Field(None, description="Performance analysis")
    portability_issues: List["PortabilityIssue"] = Field(default_factory=list, description="Portability issues")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Shader metadata (e.g., ISF parameters, author, etc.)")
    created_at: datetime = Field(..., description="Validation timestamp")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    recommendations: List[str] = Field(default_factory=list, description="Overall recommendations")
    
    class Config:
        schema_extra = {
            "example": {
                "validation_id": "val_123456789",
                "is_valid": True,
                "status": "valid",
                "format": "glsl",
                "target_version": "330",
                "target_platforms": ["desktop", "mobile", "web"],
                "errors": [],
                "warnings": [
                    {
                        "message": "Variable 'unused_var' is declared but never used",
                        "line": 5,
                        "column": 10,
                        "severity": "warning",
                        "error_code": "UNUSED_VARIABLE",
                        "suggestions": ["Remove the unused variable or use it in your code"]
                    }
                ],
                "quality_metrics": {
                    "overall_score": 0.85,
                    "metrics": [
                        {
                            "name": "Cyclomatic Complexity",
                            "value": 3,
                            "unit": "",
                            "score": 0.9,
                            "description": "Measures the number of linearly independent paths"
                        }
                    ]
                },
                "created_at": "2024-01-15T10:30:00Z",
                "processing_time_ms": 125.5,
                "recommendations": ["Consider adding precision qualifiers for mobile platforms"]
            }
        }

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

class QualityMetric(BaseModel):
    """Model for quality metrics."""
    
    name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    unit: str = Field(..., description="Unit of measurement")
    score: float = Field(..., description="Normalized score (0.0 to 1.0)")
    description: str = Field(..., description="Metric description")
    recommendations: Optional[List[str]] = Field(None, description="Recommendations")

class PerformanceAnalysis(BaseModel):
    """Model for performance analysis results."""
    
    complexity_score: float = Field(..., description="Overall complexity score")
    instruction_count: int = Field(..., description="Estimated instruction count")
    texture_samples: int = Field(..., description="Number of texture samples")
    branch_count: int = Field(..., description="Number of conditional branches")
    recommendations: List[str] = Field(default_factory=list, description="Performance recommendations")

class PortabilityIssue(BaseModel):
    """Model for portability issues."""
    
    issue_type: str = Field(..., description="Type of portability issue")
    message: str = Field(..., description="Issue description")
    affected_platforms: List[str] = Field(..., description="Platforms affected by this issue")
    severity: ErrorSeverity = Field(..., description="Issue severity")
    suggestions: Optional[List[str]] = Field(None, description="Suggested solutions")

class BatchValidationResult(BaseModel):
    """Model for batch validation result."""
    
    batch_id: str = Field(..., description="Batch identifier")
    total_shaders: int = Field(..., description="Total number of shaders in batch")
    processed_shaders: int = Field(..., description="Number of shaders processed")
    successful_validations: int = Field(..., description="Number of successful validations")
    failed_validations: int = Field(..., description="Number of failed validations")
    
    results: List[ValidationResult] = Field(..., description="Individual validation results")
    
    # Batch statistics
    total_errors: int = Field(..., description="Total number of errors across all shaders")
    total_warnings: int = Field(..., description="Total number of warnings across all shaders")
    average_quality_score: float = Field(..., description="Average quality score")
    average_processing_time_ms: float = Field(..., description="Average processing time")
    
    # Metadata
    created_at: datetime = Field(..., description="Batch creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Batch completion timestamp")
    parallel_processing: bool = Field(..., description="Whether parallel processing was used")
    
    class Config:
        schema_extra = {
            "example": {
                "batch_id": "batch_001",
                "total_shaders": 5,
                "processed_shaders": 5,
                "successful_validations": 4,
                "failed_validations": 1,
                "results": [],
                "total_errors": 2,
                "total_warnings": 8,
                "average_quality_score": 0.78,
                "average_processing_time_ms": 150.2,
                "created_at": "2024-01-15T10:30:00Z",
                "completed_at": "2024-01-15T10:30:05Z",
                "parallel_processing": True
            }
        }

class ValidationHistoryItem(BaseModel):
    """Model for validation history item."""
    
    validation_id: str = Field(..., description="Validation identifier")
    format: str = Field(..., description="Shader format")
    status: ValidationStatus = Field(..., description="Validation status")
    is_valid: bool = Field(..., description="Whether the shader was valid")
    
    # Summary statistics
    error_count: int = Field(..., description="Number of errors")
    warning_count: int = Field(..., description="Number of warnings")
    quality_score: Optional[float] = Field(None, description="Quality score")
    
    # Metadata
    created_at: datetime = Field(..., description="Validation timestamp")
    processing_time_ms: float = Field(..., description="Processing time")
    user_id: Optional[str] = Field(None, description="User identifier")
    
    class Config:
        schema_extra = {
            "example": {
                "validation_id": "val_123456789",
                "format": "glsl",
                "status": "valid",
                "is_valid": True,
                "error_count": 0,
                "warning_count": 2,
                "quality_score": 0.85,
                "created_at": "2024-01-15T10:30:00Z",
                "processing_time_ms": 125.5,
                "user_id": "user123"
            }
        }

class ValidationHistoryResponse(BaseModel):
    """Model for validation history response."""
    
    items: List[ValidationHistoryItem] = Field(..., description="Validation history items")
    total_count: int = Field(..., description="Total number of validations")
    page_count: int = Field(..., description="Total number of pages")
    current_page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    
    # Filtering information
    applied_filters: Dict[str, Any] = Field(default_factory=dict, description="Applied filters")
    
    class Config:
        schema_extra = {
            "example": {
                "items": [],
                "total_count": 150,
                "page_count": 3,
                "current_page": 1,
                "page_size": 50,
                "applied_filters": {
                    "format": "glsl",
                    "status": "valid"
                }
            }
        }

class ValidationStatusResponse(BaseModel):
    """Model for validation status response."""
    
    validation_id: str = Field(..., description="Validation identifier")
    status: ValidationStatus = Field(..., description="Current validation status")
    progress: Optional[float] = Field(None, description="Progress percentage (0.0 to 1.0)")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    
    # Result preview (if available)
    result_preview: Optional[Dict[str, Any]] = Field(None, description="Preview of validation results")
    
    # Metadata
    created_at: datetime = Field(..., description="Validation creation timestamp")
    updated_at: datetime = Field(..., description="Last status update timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "validation_id": "val_123456789",
                "status": "processing",
                "progress": 0.75,
                "estimated_completion": "2024-01-15T10:30:10Z",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:07Z"
            }
        }

class ValidationSummary(BaseModel):
    """Model for validation summary statistics."""
    
    total_validations: int = Field(..., description="Total number of validations")
    valid_shaders: int = Field(..., description="Number of valid shaders")
    invalid_shaders: int = Field(..., description="Number of invalid shaders")
    warning_shaders: int = Field(..., description="Number of shaders with warnings")
    
    # Error statistics
    total_errors: int = Field(..., description="Total number of errors")
    total_warnings: int = Field(..., description="Total number of warnings")
    most_common_errors: List[Dict[str, Any]] = Field(..., description="Most common error types")
    
    # Quality statistics
    average_quality_score: float = Field(..., description="Average quality score")
    quality_distribution: Dict[str, int] = Field(..., description="Quality score distribution")
    
    # Performance statistics
    average_processing_time_ms: float = Field(..., description="Average processing time")
    fastest_validation_ms: float = Field(..., description="Fastest validation time")
    slowest_validation_ms: float = Field(..., description="Slowest validation time")
    
    # Format statistics
    format_distribution: Dict[str, int] = Field(..., description="Distribution by shader format")
    
    class Config:
        schema_extra = {
            "example": {
                "total_validations": 1000,
                "valid_shaders": 850,
                "invalid_shaders": 100,
                "warning_shaders": 50,
                "total_errors": 250,
                "total_warnings": 500,
                "most_common_errors": [
                    {"error_code": "SYNTAX_ERROR", "count": 50},
                    {"error_code": "UNINITIALIZED_VARIABLE", "count": 30}
                ],
                "average_quality_score": 0.78,
                "quality_distribution": {
                    "excellent": 200,
                    "good": 400,
                    "fair": 300,
                    "poor": 100
                },
                "average_processing_time_ms": 150.5,
                "fastest_validation_ms": 25.0,
                "slowest_validation_ms": 500.0,
                "format_distribution": {
                    "glsl": 800,
                    "isf": 150,
                    "madmapper": 50
                }
            }
        } 