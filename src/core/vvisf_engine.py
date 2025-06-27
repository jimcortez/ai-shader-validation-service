"""
Python interface for VVISF-GL C++ bindings
"""

import json
from typing import Dict, Any, Optional, Tuple, List, Union
import logging

try:
    from ai_shadermaker_bindings import VVISFEngine, ValidationResult, ImageData, create_engine, get_version
except ImportError:
    # Fallback for development/testing
    VVISFEngine = None
    ValidationResult = None
    ImageData = None
    create_engine = None
    get_version = None

logger = logging.getLogger(__name__)


class VVISFEngineWrapper:
    """Python wrapper for VVISF-GL C++ engine."""
    
    def __init__(self):
        """Initialize the VVISF engine."""
        if VVISFEngine is None:
            raise ImportError("VVISF-GL C++ bindings not available")
        
        if create_engine is None:
            raise ImportError("VVISF-GL create_engine function not available")
        
        self.engine = create_engine()
        if not self.engine.is_initialized():
            raise RuntimeError(f"Failed to initialize VVISF engine: {self.engine.get_last_error()}")
        
        version = get_version() if get_version else "unknown"
        logger.info(f"VVISF-GL engine initialized (version: {version})")
    
    def validate_isf(self, isf_json: str) -> Dict[str, Any]:
        """
        Validate ISF JSON and return validation result.
        
        Args:
            isf_json: ISF JSON string
            
        Returns:
            Dictionary with validation results
        """
        try:
            result = self.engine.validate_isf(isf_json)
            return {
                "is_valid": result.is_valid,
                "errors": result.errors,
                "warnings": result.warnings,
                "metadata": result.metadata
            }
        except Exception as e:
            logger.error(f"ISF validation failed: {e}")
            return {
                "is_valid": False,
                "errors": [str(e)],
                "warnings": [],
                "metadata": {}
            }
    
    def render_shader(self, isf_json: str, width: int, height: int, 
                     parameters: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Render ISF shader to image.
        
        Args:
            isf_json: ISF JSON string
            width: Image width
            height: Image height
            parameters: Shader parameters
            
        Returns:
            Dictionary with image data or None if failed
        """
        try:
            if parameters is None:
                parameters = {}
            
            # Convert parameters to C++ format
            cpp_params = {}
            for key, value in parameters.items():
                cpp_params[key] = value
            
            image = self.engine.render_shader(isf_json, width, height, cpp_params)
            
            return {
                "width": image.width,
                "height": image.height,
                "data": image.get_bytes(),
                "format": image.format,
                "size": image.get_size()
            }
        except Exception as e:
            logger.error(f"Shader rendering failed: {e}")
            return None
    
    def get_parameters(self, isf_json: str) -> Dict[str, Any]:
        """
        Extract parameters from ISF JSON.
        
        Args:
            isf_json: ISF JSON string
            
        Returns:
            Dictionary of parameters
        """
        try:
            params = self.engine.get_parameters(isf_json)
            return {k: v for k, v in params.items()}
        except Exception as e:
            logger.error(f"Parameter extraction failed: {e}")
            return {}
    
    def set_parameter(self, isf_json: str, param_name: str, value: Any) -> bool:
        """
        Set parameter in ISF.
        
        Args:
            isf_json: ISF JSON string
            param_name: Parameter name
            value: Parameter value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.engine.set_parameter(isf_json, param_name, value)
            return True
        except Exception as e:
            logger.error(f"Parameter setting failed: {e}")
            return False
    
    def create_texture(self, data: bytes, width: int, height: int, 
                      format: str = "RGBA") -> Optional[str]:
        """
        Create texture from image data.
        
        Args:
            data: Image data as bytes
            width: Image width
            height: Image height
            format: Image format
            
        Returns:
            Texture ID or None if failed
        """
        try:
            # Convert bytes to vector
            data_vector = list(data)
            texture_id = self.engine.create_texture(data_vector, width, height, format)
            return texture_id
        except Exception as e:
            logger.error(f"Texture creation failed: {e}")
            return None
    
    def destroy_texture(self, texture_id: str) -> bool:
        """
        Destroy texture by ID.
        
        Args:
            texture_id: Texture ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.engine.destroy_texture(texture_id)
            return True
        except Exception as e:
            logger.error(f"Texture destruction failed: {e}")
            return False
    
    def get_last_error(self) -> str:
        """Get last error message."""
        return self.engine.get_last_error()
    
    def reset_errors(self):
        """Reset error state."""
        self.engine.reset_errors()
    
    def is_initialized(self) -> bool:
        """Check if engine is initialized."""
        return self.engine.is_initialized()


class MockVVISFEngine:
    """Mock VVISF engine for testing when C++ bindings are not available."""
    
    def __init__(self):
        logger.warning("Using mock VVISF engine (C++ bindings not available)")
    
    def validate_isf(self, isf_json: str) -> Dict[str, Any]:
        """Mock ISF validation."""
        try:
            # Basic JSON validation
            json.loads(isf_json)
            return {
                "is_valid": True,
                "errors": [],
                "warnings": ["Using mock validation - C++ bindings not available"],
                "metadata": {"version": "mock", "type": "isf"}
            }
        except json.JSONDecodeError as e:
            return {
                "is_valid": False,
                "errors": [f"Invalid JSON: {e}"],
                "warnings": [],
                "metadata": {}
            }
    
    def render_shader(self, isf_json: str, width: int, height: int, 
                     parameters: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Mock shader rendering."""
        # Create a simple gradient image
        data = bytearray()
        for y in range(height):
            for x in range(width):
                r = int(255 * x / width)
                g = int(255 * y / height)
                b = 128
                a = 255
                data.extend([r, g, b, a])
        
        return {
            "width": width,
            "height": height,
            "data": bytes(data),
            "format": "RGBA",
            "size": [width, height]
        }
    
    def get_parameters(self, isf_json: str) -> Dict[str, Any]:
        """Mock parameter extraction."""
        return {
            "time": 0.0,
            "resolution": [512, 512],
            "mouse": [0.5, 0.5]
        }
    
    def set_parameter(self, isf_json: str, param_name: str, value: Any) -> bool:
        """Mock parameter setting."""
        return True
    
    def create_texture(self, data: bytes, width: int, height: int, 
                      format: str = "RGBA") -> Optional[str]:
        """Mock texture creation."""
        return f"mock_texture_{hash(data) % 1000000}"
    
    def destroy_texture(self, texture_id: str) -> bool:
        """Mock texture destruction."""
        return True
    
    def get_last_error(self) -> str:
        """Mock error message."""
        return "Mock engine - no errors"
    
    def reset_errors(self):
        """Mock error reset."""
        pass
    
    def is_initialized(self) -> bool:
        """Mock initialization check."""
        return True


def create_vvisf_engine() -> Union[VVISFEngineWrapper, MockVVISFEngine]:
    """Create a VVISF engine instance."""
    try:
        return VVISFEngineWrapper()
    except (ImportError, RuntimeError) as e:
        logger.warning(f"Failed to create VVISF engine: {e}")
        return MockVVISFEngine()


# Global engine instance
_vvisf_engine: Optional[Union[VVISFEngineWrapper, MockVVISFEngine]] = None

def get_vvisf_engine() -> Union[VVISFEngineWrapper, MockVVISFEngine]:
    """Get the global VVISF engine instance."""
    global _vvisf_engine
    if _vvisf_engine is None:
        _vvisf_engine = create_vvisf_engine()
    return _vvisf_engine 