"""
Request models for API endpoints
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum

class ShaderFormat(str, Enum):
    """Supported shader formats"""
    GLSL = "glsl"
    ISF = "isf"
    MADMAPPER = "madmapper"

class ValidationLevel(str, Enum):
    """Validation levels"""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"

class ValidationRequest(BaseModel):
    """Request model for shader validation"""
    
    shader_code: str = Field(..., description="Shader source code")
    format: ShaderFormat = Field(..., description="Shader format")
    validation_level: ValidationLevel = Field(
        default=ValidationLevel.STANDARD,
        description="Validation level"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Shader parameters for testing"
    )
    
    @validator('shader_code')
    def validate_shader_code(cls, v):
        if not v.strip():
            raise ValueError("Shader code cannot be empty")
        if len(v) > 1024 * 1024:  # 1MB limit
            raise ValueError("Shader code too large (max 1MB)")
        return v

class BatchValidationRequest(BaseModel):
    """Request model for batch shader validation"""
    
    shaders: List[ValidationRequest] = Field(..., description="List of shaders to validate")
    max_concurrent: Optional[int] = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum concurrent validations"
    )

class AnalysisRequest(BaseModel):
    """Request model for shader analysis"""
    
    shader_id: str = Field(..., description="ID of the shader to analyze")
    analysis_types: List[str] = Field(
        default=["syntax", "semantic", "performance"],
        description="Types of analysis to perform"
    )

class VisualizationRequest(BaseModel):
    """Request model for shader visualization"""
    
    shader_code: str = Field(..., description="Shader source code")
    format: ShaderFormat = Field(..., description="Shader format")
    width: int = Field(default=512, ge=64, le=2048, description="Image width")
    height: int = Field(default=512, ge=64, le=2048, description="Image height")
    parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Shader parameters"
    )
    image_format: str = Field(default="png", description="Output image format")

class ISFValidationRequest(BaseModel):
    """Request model for ISF-specific validation"""
    
    isf_json: str = Field(..., description="ISF JSON content")
    validate_glsl: bool = Field(default=True, description="Validate embedded GLSL")
    check_parameters: bool = Field(default=True, description="Validate parameter definitions")
    
    @validator('isf_json')
    def validate_isf_json(cls, v):
        if not v.strip():
            raise ValueError("ISF JSON cannot be empty")
        return v 