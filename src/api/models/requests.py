"""
Request models for validation API endpoints
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class ShaderFormat(str, Enum):
    """Supported shader formats."""
    GLSL = "glsl"
    ISF = "isf"
    MADMAPPER = "madmapper"
    HLSL = "hlsl"


class ValidationLevel(str, Enum):
    """Validation levels."""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"


class Platform(str, Enum):
    """Target platforms."""
    DESKTOP = "desktop"
    MOBILE = "mobile"
    WEB = "web"
    ALL = "all"


class ValidationRequest(BaseModel):
    """Request model for single shader validation."""
    
    code: str = Field(..., description="Shader source code", min_length=1, max_length=100000)
    format: ShaderFormat = Field(..., description="Shader format")
    target_version: Optional[str] = Field("330", description="Target GLSL version (for GLSL shaders)")
    target_platforms: Optional[List[Platform]] = Field(
        default_factory=lambda: [Platform.DESKTOP, Platform.MOBILE, Platform.WEB],
        description="Target platforms for validation"
    )
    validation_level: ValidationLevel = Field(
        ValidationLevel.STANDARD,
        description="Validation level to apply"
    )
    enable_quality_analysis: bool = Field(True, description="Enable quality analysis")
    enable_portability_analysis: bool = Field(True, description="Enable portability analysis")
    enable_performance_analysis: bool = Field(True, description="Enable performance analysis")
    custom_parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Custom parameters for validation"
    )
    
    @validator('code')
    def validate_code_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Shader code cannot be empty')
        return v
    
    @validator('target_version')
    def validate_glsl_version(cls, v, values):
        if values.get('format') == ShaderFormat.GLSL and v:
            valid_versions = ['110', '120', '130', '140', '150', '330', '400', '410', '420', '430', '440', '450', '460']
            if v not in valid_versions:
                raise ValueError(f'Invalid GLSL version. Must be one of: {", ".join(valid_versions)}')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "code": "#version 330\n\nvoid main() {\n    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);\n}",
                "format": "glsl",
                "target_version": "330",
                "target_platforms": ["desktop", "mobile", "web"],
                "validation_level": "standard",
                "enable_quality_analysis": True,
                "enable_portability_analysis": True,
                "enable_performance_analysis": True
            }
        }


class BatchValidationRequest(BaseModel):
    """Request model for batch shader validation."""
    
    shaders: List[ValidationRequest] = Field(
        ...,
        description="List of shaders to validate"
    )
    parallel_processing: bool = Field(
        True,
        description="Enable parallel processing for batch validation"
    )
    batch_id: Optional[str] = Field(
        None,
        description="Optional batch identifier for tracking"
    )
    
    @validator('shaders')
    def validate_shaders_not_empty(cls, v):
        if not v:
            raise ValueError('At least one shader must be provided for batch validation')
        if len(v) > 100:
            raise ValueError('Maximum 100 shaders allowed per batch')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "shaders": [
                    {
                        "code": "#version 330\n\nvoid main() {\n    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);\n}",
                        "format": "glsl",
                        "target_version": "330"
                    },
                    {
                        "code": "#version 330\n\nvoid main() {\n    gl_FragColor = vec4(0.0, 1.0, 0.0, 1.0);\n}",
                        "format": "glsl",
                        "target_version": "330"
                    }
                ],
                "parallel_processing": True,
                "batch_id": "batch_001"
            }
        }


class ValidationHistoryRequest(BaseModel):
    """Request model for retrieving validation history."""
    
    user_id: Optional[str] = Field(None, description="User identifier")
    format: Optional[ShaderFormat] = Field(None, description="Filter by shader format")
    status: Optional[str] = Field(None, description="Filter by validation status")
    start_date: Optional[str] = Field(None, description="Start date for filtering (ISO format)")
    end_date: Optional[str] = Field(None, description="End date for filtering (ISO format)")
    limit: int = Field(50, description="Maximum number of results", ge=1, le=1000)
    offset: int = Field(0, description="Number of results to skip", ge=0)
    sort_by: str = Field("created_at", description="Field to sort by")
    sort_order: str = Field("desc", description="Sort order (asc/desc)")
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('Sort order must be either "asc" or "desc"')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        if v and v not in ['valid', 'invalid', 'warning', 'error']:
            raise ValueError('Status must be one of: valid, invalid, warning, error')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "format": "glsl",
                "status": "valid",
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-12-31T23:59:59Z",
                "limit": 50,
                "offset": 0,
                "sort_by": "created_at",
                "sort_order": "desc"
            }
        }


class ValidationStatusRequest(BaseModel):
    """Request model for checking validation status."""
    
    validation_id: str = Field(..., description="Validation identifier")
    
    class Config:
        schema_extra = {
            "example": {
                "validation_id": "val_123456789"
            }
        }


class ValidationParameters(BaseModel):
    """Model for validation parameters."""
    
    target_version: str = Field("330", description="Target GLSL version")
    target_platforms: List[Platform] = Field(
        default_factory=lambda: [Platform.DESKTOP, Platform.MOBILE, Platform.WEB],
        description="Target platforms"
    )
    validation_level: ValidationLevel = Field(
        ValidationLevel.STANDARD,
        description="Validation level"
    )
    enable_quality_analysis: bool = Field(True, description="Enable quality analysis")
    enable_portability_analysis: bool = Field(True, description="Enable portability analysis")
    enable_performance_analysis: bool = Field(True, description="Enable performance analysis")
    custom_parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom parameters"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for validation service."""
        return {
            "target_version": self.target_version,
            "target_platforms": [p.value for p in self.target_platforms],
            "validation_level": self.validation_level.value,
            "enable_quality_analysis": self.enable_quality_analysis,
            "enable_portability_analysis": self.enable_portability_analysis,
            "enable_performance_analysis": self.enable_performance_analysis,
            "custom_parameters": self.custom_parameters
        }


class ValidationFilter(BaseModel):
    """Model for validation filtering."""
    
    format: Optional[ShaderFormat] = None
    status: Optional[str] = None
    severity: Optional[str] = None
    has_errors: Optional[bool] = None
    has_warnings: Optional[bool] = None
    quality_score_min: Optional[float] = Field(None, ge=0.0, le=1.0)
    quality_score_max: Optional[float] = Field(None, ge=0.0, le=1.0)
    created_after: Optional[str] = None
    created_before: Optional[str] = None
    
    @validator('severity')
    def validate_severity(cls, v):
        if v and v not in ['error', 'warning', 'info']:
            raise ValueError('Severity must be one of: error, warning, info')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        if v and v not in ['valid', 'invalid', 'warning', 'error']:
            raise ValueError('Status must be one of: valid, invalid, warning, error')
        return v 