"""
Visualization API Routes

This module contains FastAPI routes for shader visualization and image management.
"""

import logging
import base64
import json
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from fastapi.responses import Response, StreamingResponse
import io

from src.api.models.visualization_requests import (
    VisualizationRequest, VisualizationResponse, ImageInfo, ImageListResponse,
    ThumbnailRequest, ResizeRequest, FormatConversionRequest,
    BatchVisualizationRequest, BatchVisualizationResponse, ErrorResponse,
    ImageFormat, ShaderType
)
from src.services.visualization_service import get_visualization_service, VisualizationError
from src.core.utils.image_utils import bytes_to_pil_image

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/visualize", tags=["visualization"])


@router.post("/", response_model=VisualizationResponse)
async def visualize_shader(request: VisualizationRequest):
    """
    Visualize a shader by rendering it to an image.
    
    Args:
        request: Visualization request with shader data and parameters
        
    Returns:
        Visualization response with image ID and metadata
    """
    try:
        service = get_visualization_service()
        
        # Convert input textures from base64 if provided
        input_textures = None
        if request.input_textures:
            input_textures = {}
            for name, data in request.input_textures.items():
                try:
                    # Decode base64 data
                    texture_bytes = base64.b64decode(data)
                    # Convert to PIL Image and then to numpy array
                    texture_image = bytes_to_pil_image(texture_bytes)
                    import numpy as np
                    input_textures[name] = np.array(texture_image)
                except Exception as e:
                    logger.warning(f"Failed to decode texture {name}: {e}")
                    continue
        
        # Render shader based on type
        if request.shader_type == ShaderType.GLSL:
            image_id, image_data = service.render_glsl_shader(
                request.shader_source,
                request.width,
                request.height,
                request.parameters,
                request.format.value
            )
        elif request.shader_type == ShaderType.ISF:
            # Parse ISF data
            try:
                isf_data = json.loads(request.shader_source)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid ISF JSON data")
            
            image_id, image_data = service.render_isf_shader(
                isf_data,
                request.width,
                request.height,
                request.parameters,
                request.format.value
            )
        elif request.shader_type == ShaderType.MADMAPPER:
            # For MadMapper, treat as GLSL fragment shader
            image_id, image_data = service.render_glsl_shader(
                request.shader_source,
                request.width,
                request.height,
                request.parameters,
                request.format.value
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported shader type: {request.shader_type}")
        
        # Get image metadata
        metadata = service.get_image_metadata(image_id) or {}
        
        return VisualizationResponse(
            image_id=image_id,
            image_url=f"/api/v1/images/{image_id}",
            width=request.width,
            height=request.height,
            format=request.format,
            created_at=metadata.get('created_at', ''),
            metadata=metadata
        )
        
    except VisualizationError as e:
        logger.error(f"Visualization error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during visualization: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/images/{image_id}", response_class=Response)
async def get_image(
    image_id: str = Path(..., description="Image ID"),
    format: Optional[ImageFormat] = Query(None, description="Requested image format")
):
    """
    Get a generated image by ID.
    
    Args:
        image_id: Unique identifier for the image
        format: Optional format conversion
        
    Returns:
        Image data as response
    """
    try:
        service = get_visualization_service()
        
        # Get image data
        image_data = service.get_image(image_id)
        if not image_data:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Convert format if requested
        if format:
            converted_data = service.convert_image_format(image_id, format.value)
            if not converted_data:
                raise HTTPException(status_code=400, detail="Failed to convert image format")
            image_data = converted_data
        
        # Get metadata for content type
        metadata = service.get_image_metadata(image_id) or {}
        image_format = metadata.get('format', 'PNG')
        
        content_type = f"image/{image_format.lower()}"
        
        return Response(
            content=image_data,
            media_type=content_type,
            headers={"Cache-Control": "public, max-age=3600"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving image {image_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/images", response_model=ImageListResponse)
async def list_images(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of images per page")
):
    """
    List cached images with pagination.
    
    Args:
        page: Page number (1-based)
        page_size: Number of images per page
        
    Returns:
        List of image information
    """
    try:
        service = get_visualization_service()
        
        # Get all images
        all_images = service.list_images()
        total_count = len(all_images)
        
        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_images = all_images[start_idx:end_idx]
        
        # Convert to ImageInfo models
        image_infos = []
        for img_data in paginated_images:
            image_infos.append(ImageInfo(
                id=img_data['id'],
                width=img_data['width'],
                height=img_data['height'],
                format=ImageFormat(img_data['format']),
                created_at=img_data['created_at'],
                data_size=img_data['data_size'],
                metadata=img_data.get('metadata', {})
            ))
        
        return ImageListResponse(
            images=image_infos,
            total_count=total_count,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"Error listing images: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/images/{image_id}/thumbnail", response_class=Response)
async def create_thumbnail(
    request: ThumbnailRequest,
    image_id: str = Path(..., description="Image ID")
):
    """
    Create a thumbnail of an image.
    
    Args:
        request: Thumbnail request with dimensions
        image_id: Image ID
        
    Returns:
        Thumbnail image data
    """
    try:
        service = get_visualization_service()
        
        # Create thumbnail
        thumbnail_data = service.create_thumbnail(
            image_id, 
            (request.width, request.height)
        )
        
        if not thumbnail_data:
            raise HTTPException(status_code=404, detail="Image not found")
        
        return Response(
            content=thumbnail_data,
            media_type="image/png",
            headers={"Cache-Control": "public, max-age=3600"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating thumbnail for {image_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/images/{image_id}/resize", response_class=Response)
async def resize_image(
    request: ResizeRequest,
    image_id: str = Path(..., description="Image ID")
):
    """
    Resize an image.
    
    Args:
        request: Resize request with new dimensions
        image_id: Image ID
        
    Returns:
        Resized image data
    """
    try:
        service = get_visualization_service()
        
        # Resize image
        resized_data = service.resize_image(
            image_id, 
            request.width, 
            request.height
        )
        
        if not resized_data:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Get metadata for content type
        metadata = service.get_image_metadata(image_id) or {}
        image_format = metadata.get('format', 'PNG')
        content_type = f"image/{image_format.lower()}"
        
        return Response(
            content=resized_data,
            media_type=content_type,
            headers={"Cache-Control": "public, max-age=3600"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resizing image {image_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/images/{image_id}/convert", response_class=Response)
async def convert_image_format(
    request: FormatConversionRequest,
    image_id: str = Path(..., description="Image ID")
):
    """
    Convert an image to a different format.
    
    Args:
        request: Format conversion request
        image_id: Image ID
        
    Returns:
        Converted image data
    """
    try:
        service = get_visualization_service()
        
        # Convert format
        converted_data = service.convert_image_format(
            image_id, 
            request.format.value
        )
        
        if not converted_data:
            raise HTTPException(status_code=404, detail="Image not found")
        
        content_type = f"image/{request.format.value.lower()}"
        
        return Response(
            content=converted_data,
            media_type=content_type,
            headers={"Cache-Control": "public, max-age=3600"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting image {image_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/batch", response_model=BatchVisualizationResponse)
async def batch_visualize(request: BatchVisualizationRequest):
    """
    Visualize multiple shaders in batch.
    
    Args:
        request: Batch visualization request
        
    Returns:
        Batch visualization response with results
    """
    try:
        service = get_visualization_service()
        
        # For now, process sequentially (can be enhanced with async processing)
        results = []
        completed = 0
        failed = 0
        
        for shader_request in request.shaders:
            try:
                # Convert to individual visualization request
                if shader_request.shader_type == ShaderType.GLSL:
                    image_id, _ = service.render_glsl_shader(
                        shader_request.shader_source,
                        shader_request.width,
                        shader_request.height,
                        shader_request.parameters,
                        shader_request.format.value
                    )
                elif shader_request.shader_type == ShaderType.ISF:
                    isf_data = json.loads(shader_request.shader_source)
                    image_id, _ = service.render_isf_shader(
                        isf_data,
                        shader_request.width,
                        shader_request.height,
                        shader_request.parameters,
                        shader_request.format.value
                    )
                else:
                    # Treat as GLSL
                    image_id, _ = service.render_glsl_shader(
                        shader_request.shader_source,
                        shader_request.width,
                        shader_request.height,
                        shader_request.parameters,
                        shader_request.format.value
                    )
                
                # Get metadata
                metadata = service.get_image_metadata(image_id) or {}
                
                results.append(VisualizationResponse(
                    image_id=image_id,
                    image_url=f"/api/v1/images/{image_id}",
                    width=shader_request.width,
                    height=shader_request.height,
                    format=shader_request.format,
                    created_at=metadata.get('created_at', ''),
                    metadata=metadata
                ))
                completed += 1
                
            except Exception as e:
                logger.error(f"Failed to visualize shader in batch: {e}")
                failed += 1
        
        return BatchVisualizationResponse(
            batch_id=f"batch_{len(results)}",
            total_shaders=len(request.shaders),
            completed=completed,
            failed=failed,
            results=results,
            status="completed" if failed == 0 else "partial"
        )
        
    except Exception as e:
        logger.error(f"Error in batch visualization: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/images/{image_id}")
async def delete_image(image_id: str = Path(..., description="Image ID")):
    """
    Delete a cached image.
    
    Args:
        image_id: Image ID to delete
        
    Returns:
        Success response
    """
    try:
        service = get_visualization_service()
        
        # Check if image exists
        if not service.get_image(image_id):
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Delete image
        service.clear_cache(image_id)
        
        return {"message": "Image deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting image {image_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/images")
async def clear_all_images():
    """
    Clear all cached images.
    
    Returns:
        Success response
    """
    try:
        service = get_visualization_service()
        service.clear_cache()
        
        return {"message": "All images cleared successfully"}
        
    except Exception as e:
        logger.error(f"Error clearing images: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 