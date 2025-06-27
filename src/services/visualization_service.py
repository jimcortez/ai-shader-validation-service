"""
Visualization Service

This service provides shader visualization capabilities using the shader renderer
and image processing utilities.
"""

import logging
import uuid
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime
import numpy as np
from PIL import Image

from src.core.renderers.shader_renderer import ShaderRenderer, ShaderRenderError
from src.core.utils.image_utils import (
    bytes_to_pil_image, pil_image_to_bytes, numpy_to_pil_image,
    resize_image, convert_format, get_image_info, ImageProcessingError
)

logger = logging.getLogger(__name__)


class VisualizationError(Exception):
    """Exception raised for visualization errors."""
    pass


class VisualizationService:
    """
    Service for shader visualization and image generation.
    
    This service provides high-level methods for rendering shaders,
    generating images, and managing visualization results.
    """
    
    def __init__(self):
        """Initialize the visualization service."""
        self.renderer = ShaderRenderer()
        self._cache: Dict[str, bytes] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
    
    def render_shader(self, 
                     vertex_source: str, 
                     fragment_source: str,
                     width: int = 512, 
                     height: int = 512,
                     uniforms: Optional[Dict[str, Any]] = None,
                     input_textures: Optional[Dict[str, np.ndarray]] = None,
                     format: str = 'PNG') -> Tuple[str, bytes]:
        """
        Render a shader to an image.
        
        Args:
            vertex_source: Vertex shader source code
            fragment_source: Fragment shader source code
            width: Image width
            height: Image height
            uniforms: Uniform values to set
            input_textures: Input textures as numpy arrays
            format: Output image format
            
        Returns:
            Tuple of (image_id, image_data)
            
        Raises:
            VisualizationError: If rendering fails
        """
        try:
            # Generate unique ID for this render
            image_id = str(uuid.uuid4())
            
            # Compile shader
            shader_name = f"shader_{image_id}"
            if not self.renderer.compile_shader(shader_name, vertex_source, fragment_source):
                raise VisualizationError("Failed to compile shader")
            
            # Set uniforms
            if uniforms:
                for name, value in uniforms.items():
                    self.renderer.set_uniform(shader_name, name, value)
            
            # Create input textures
            texture_mapping = {}
            if input_textures:
                for texture_name, texture_data in input_textures.items():
                    texture_id = f"texture_{texture_name}_{image_id}"
                    if self.renderer.create_texture(texture_id, texture_data.shape[1], 
                                                   texture_data.shape[0], texture_data):
                        texture_mapping[texture_name] = texture_id
            
            # Render to image
            image_data = self.renderer.render_to_image(
                shader_name, width, height, texture_mapping, format
            )
            
            # Store in cache
            self._cache[image_id] = image_data
            self._metadata[image_id] = {
                'width': width,
                'height': height,
                'format': format,
                'created_at': datetime.utcnow().isoformat(),
                'shader_name': shader_name,
                'uniforms': uniforms or {},
                'input_textures': list(input_textures.keys()) if input_textures else []
            }
            
            logger.info(f"Rendered shader to image {image_id} ({width}x{height})")
            return image_id, image_data
            
        except (ShaderRenderError, ImageProcessingError) as e:
            error_msg = f"Failed to render shader: {e}"
            logger.error(error_msg)
            raise VisualizationError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during shader rendering: {e}"
            logger.error(error_msg)
            raise VisualizationError(error_msg)
    
    def render_isf_shader(self, 
                         isf_data: Dict[str, Any],
                         width: int = 512, 
                         height: int = 512,
                         parameters: Optional[Dict[str, Any]] = None,
                         format: str = 'PNG') -> Tuple[str, bytes]:
        """
        Render an ISF shader to an image.
        
        Args:
            isf_data: ISF shader data
            width: Image width
            height: Image height
            parameters: Shader parameters
            format: Output image format
            
        Returns:
            Tuple of (image_id, image_data)
            
        Raises:
            VisualizationError: If rendering fails
        """
        try:
            # Extract shader code from ISF data
            if 'PASSES' not in isf_data or not isf_data['PASSES']:
                raise VisualizationError("No passes found in ISF data")
            
            # Use the first pass for now
            pass_data = isf_data['PASSES'][0]
            
            # Get vertex and fragment shaders
            vertex_source = pass_data.get('TARGET', '')
            fragment_source = pass_data.get('FS', '')
            
            if not fragment_source:
                raise VisualizationError("No fragment shader found in ISF data")
            
            # Convert ISF parameters to uniforms
            uniforms = {}
            if parameters and 'INPUTS' in isf_data:
                for input_name, input_data in isf_data['INPUTS'].items():
                    if input_name in parameters:
                        uniforms[input_name] = parameters[input_name]
            
            # Render the shader
            return self.render_shader(
                vertex_source, fragment_source, width, height, uniforms, format=format
            )
            
        except Exception as e:
            error_msg = f"Failed to render ISF shader: {e}"
            logger.error(error_msg)
            raise VisualizationError(error_msg)
    
    def render_glsl_shader(self, 
                          glsl_source: str,
                          width: int = 512, 
                          height: int = 512,
                          uniforms: Optional[Dict[str, Any]] = None,
                          format: str = 'PNG') -> Tuple[str, bytes]:
        """
        Render a GLSL shader to an image.
        
        Args:
            glsl_source: GLSL shader source code
            width: Image width
            height: Image height
            uniforms: Uniform values
            format: Output image format
            
        Returns:
            Tuple of (image_id, image_data)
            
        Raises:
            VisualizationError: If rendering fails
        """
        try:
            # Simple vertex shader for full-screen quad
            vertex_source = """
            #version 330 core
            layout(location = 0) in vec2 position;
            layout(location = 1) in vec2 texCoord;
            
            out vec2 vTexCoord;
            
            void main() {
                gl_Position = vec4(position, 0.0, 1.0);
                vTexCoord = texCoord;
            }
            """
            
            # Use the provided GLSL as fragment shader
            fragment_source = glsl_source
            
            # Render the shader
            return self.render_shader(
                vertex_source, fragment_source, width, height, uniforms, format=format
            )
            
        except Exception as e:
            error_msg = f"Failed to render GLSL shader: {e}"
            logger.error(error_msg)
            raise VisualizationError(error_msg)
    
    def get_image(self, image_id: str) -> Optional[bytes]:
        """
        Get an image from cache.
        
        Args:
            image_id: Image ID
            
        Returns:
            Image data or None if not found
        """
        return self._cache.get(image_id)
    
    def get_image_metadata(self, image_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for an image.
        
        Args:
            image_id: Image ID
            
        Returns:
            Image metadata or None if not found
        """
        return self._metadata.get(image_id)
    
    def resize_image(self, image_id: str, width: int, height: int) -> Optional[bytes]:
        """
        Resize a cached image.
        
        Args:
            image_id: Image ID
            width: New width
            height: New height
            
        Returns:
            Resized image data or None if not found
        """
        try:
            image_data = self._cache.get(image_id)
            if not image_data:
                return None
            
            # Convert to PIL Image
            image = bytes_to_pil_image(image_data)
            
            # Resize
            resized_image = resize_image(image, (width, height))
            
            # Convert back to bytes
            return pil_image_to_bytes(resized_image)
            
        except Exception as e:
            logger.error(f"Failed to resize image {image_id}: {e}")
            return None
    
    def convert_image_format(self, image_id: str, format: str) -> Optional[bytes]:
        """
        Convert a cached image to a different format.
        
        Args:
            image_id: Image ID
            format: Target format
            
        Returns:
            Converted image data or None if not found
        """
        try:
            image_data = self._cache.get(image_id)
            if not image_data:
                return None
            
            # Convert to PIL Image
            image = bytes_to_pil_image(image_data)
            
            # Convert format
            converted_image = convert_format(image, format)
            
            # Convert back to bytes
            return pil_image_to_bytes(converted_image, format)
            
        except Exception as e:
            logger.error(f"Failed to convert image {image_id} to {format}: {e}")
            return None
    
    def create_thumbnail(self, image_id: str, size: Tuple[int, int] = (128, 128)) -> Optional[bytes]:
        """
        Create a thumbnail of a cached image.
        
        Args:
            image_id: Image ID
            size: Thumbnail size
            
        Returns:
            Thumbnail image data or None if not found
        """
        try:
            image_data = self._cache.get(image_id)
            if not image_data:
                return None
            
            # Convert to PIL Image
            image = bytes_to_pil_image(image_data)
            
            # Create thumbnail
            image.thumbnail(size, Image.LANCZOS)
            
            # Convert back to bytes
            return pil_image_to_bytes(image)
            
        except Exception as e:
            logger.error(f"Failed to create thumbnail for image {image_id}: {e}")
            return None
    
    def list_images(self) -> List[Dict[str, Any]]:
        """
        List all cached images with their metadata.
        
        Returns:
            List of image information dictionaries
        """
        images = []
        for image_id, metadata in self._metadata.items():
            image_info = {
                'id': image_id,
                'data_size': len(self._cache.get(image_id, b'')),
                **metadata
            }
            images.append(image_info)
        return images
    
    def clear_cache(self, image_id: Optional[str] = None):
        """
        Clear image cache.
        
        Args:
            image_id: Specific image ID to clear, or None to clear all
        """
        if image_id:
            self._cache.pop(image_id, None)
            self._metadata.pop(image_id, None)
            logger.info(f"Cleared image {image_id} from cache")
        else:
            self._cache.clear()
            self._metadata.clear()
            logger.info("Cleared all images from cache")
    
    def cleanup(self):
        """Clean up visualization service resources."""
        try:
            self.renderer.cleanup()
            self.clear_cache()
            logger.info("Visualization service cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during visualization service cleanup: {e}")


# Global visualization service instance
_global_visualization_service: Optional[VisualizationService] = None


def get_visualization_service() -> VisualizationService:
    """
    Get the global visualization service instance.
    
    Returns:
        Global visualization service instance
    """
    global _global_visualization_service
    if _global_visualization_service is None:
        _global_visualization_service = VisualizationService()
    return _global_visualization_service


def cleanup_visualization_service():
    """Clean up the global visualization service."""
    global _global_visualization_service
    if _global_visualization_service is not None:
        _global_visualization_service.cleanup()
        _global_visualization_service = None 