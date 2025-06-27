"""
Visualization API Request/Response Models

This module contains Pydantic models for visualization API endpoints.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum


class ImageFormat(str, Enum):
    """Supported image formats for visualization."""
    PNG = "PNG"
    JPEG = "JPEG"
    WEBP = "WEBP"


class ShaderType(str, Enum):
    """Supported shader types for visualization."""
    GLSL = "GLSL"
    ISF = "ISF"
    MADMAPPER = "MADMAPPER"


class VisualizationRequest(BaseModel):
    """Request model for shader visualization."""
    
    shader_type: ShaderType = Field(..., description="Type of shader to visualize")
    shader_source: str = Field(..., description="Shader source code or data")
    width: int = Field(default=512, ge=64, le=4096, description="Image width")
    height: int = Field(default=512, ge=64, le=4096, description="Image height")
    format: ImageFormat = Field(default=ImageFormat.PNG, description="Output image format")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Shader parameters")
    input_textures: Optional[Dict[str, str]] = Field(default=None, description="Input texture data (base64 encoded)")


class VisualizationResponse(BaseModel):
    """Response model for shader visualization."""
    
    image_id: str = Field(..., description="Unique identifier for the generated image")
    image_url: str = Field(..., description="URL to access the generated image")
    width: int = Field(..., description="Image width")
    height: int = Field(..., description="Image height")
    format: ImageFormat = Field(..., description="Image format")
    created_at: str = Field(..., description="Creation timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ImageInfo(BaseModel):
    """Model for image information."""
    
    id: str = Field(..., description="Image ID")
    width: int = Field(..., description="Image width")
    height: int = Field(..., description="Image height")
    format: ImageFormat = Field(..., description="Image format")
    created_at: str = Field(..., description="Creation timestamp")
    data_size: int = Field(..., description="Image data size in bytes")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ImageListResponse(BaseModel):
    """Response model for listing images."""
    
    images: List[ImageInfo] = Field(..., description="List of cached images")
    total_count: int = Field(..., description="Total number of images")
    page: int = Field(default=1, description="Current page number")
    page_size: int = Field(default=20, description="Number of images per page")


class ThumbnailRequest(BaseModel):
    """Request model for thumbnail generation."""
    
    image_id: str = Field(..., description="ID of the image to create thumbnail for")
    width: int = Field(default=128, ge=32, le=512, description="Thumbnail width")
    height: int = Field(default=128, ge=32, le=512, description="Thumbnail height")


class ResizeRequest(BaseModel):
    """Request model for image resizing."""
    
    image_id: str = Field(..., description="ID of the image to resize")
    width: int = Field(..., ge=64, le=4096, description="New width")
    height: int = Field(..., ge=64, le=4096, description="New height")


class FormatConversionRequest(BaseModel):
    """Request model for image format conversion."""
    
    image_id: str = Field(..., description="ID of the image to convert")
    format: ImageFormat = Field(..., description="Target format")
    quality: Optional[int] = Field(default=None, ge=1, le=100, description="Quality for JPEG (1-100)")


class BatchVisualizationRequest(BaseModel):
    """Request model for batch visualization."""
    
    shaders: List[VisualizationRequest] = Field(..., description="List of shaders to visualize")
    parallel: bool = Field(default=True, description="Process shaders in parallel")


class BatchVisualizationResponse(BaseModel):
    """Response model for batch visualization."""
    
    batch_id: str = Field(..., description="Unique identifier for the batch")
    total_shaders: int = Field(..., description="Total number of shaders")
    completed: int = Field(default=0, description="Number of completed visualizations")
    failed: int = Field(default=0, description="Number of failed visualizations")
    results: List[VisualizationResponse] = Field(default_factory=list, description="Visualization results")
    status: str = Field(default="processing", description="Batch status")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    code: Optional[str] = Field(default=None, description="Error code") 