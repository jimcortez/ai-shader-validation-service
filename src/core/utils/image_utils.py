"""
Image Processing Utilities

This module provides image processing utilities for shader rendering.
"""

import logging
import io
from typing import Optional, Tuple, Union
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class ImageProcessingError(Exception):
    """Exception raised for image processing errors."""
    pass


def bytes_to_pil_image(image_data: bytes) -> Image.Image:
    """Convert image bytes to PIL Image."""
    try:
        return Image.open(io.BytesIO(image_data))
    except Exception as e:
        logger.error(f"Failed to convert bytes to PIL Image: {e}")
        raise ImageProcessingError(f"Failed to convert bytes to PIL Image: {e}")


def pil_image_to_bytes(image: Image.Image, format: str = 'PNG') -> bytes:
    """Convert PIL Image to bytes."""
    try:
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        return buffer.getvalue()
    except Exception as e:
        logger.error(f"Failed to convert PIL Image to bytes: {e}")
        raise ImageProcessingError(f"Failed to convert PIL Image to bytes: {e}")


def numpy_to_pil_image(array: np.ndarray) -> Image.Image:
    """Convert numpy array to PIL Image."""
    try:
        if array.dtype != np.uint8:
            if array.max() <= 1.0:
                array = (array * 255).astype(np.uint8)
            else:
                array = array.astype(np.uint8)
        
        if len(array.shape) == 2:
            return Image.fromarray(array, 'L')
        elif len(array.shape) == 3:
            if array.shape[2] == 1:
                return Image.fromarray(array[:, :, 0], 'L')
            elif array.shape[2] == 3:
                return Image.fromarray(array, 'RGB')
            elif array.shape[2] == 4:
                return Image.fromarray(array, 'RGBA')
        
        raise ImageProcessingError(f"Unsupported array shape: {array.shape}")
    except Exception as e:
        logger.error(f"Failed to convert numpy array to PIL Image: {e}")
        raise ImageProcessingError(f"Failed to convert numpy array to PIL Image: {e}")


def resize_image(image: Union[Image.Image, np.ndarray], 
                size: Tuple[int, int]) -> Union[Image.Image, np.ndarray]:
    """Resize an image."""
    try:
        if isinstance(image, np.ndarray):
            pil_image = numpy_to_pil_image(image)
            resized_pil = pil_image.resize(size, Image.LANCZOS)
            return np.array(resized_pil)
        else:
            return image.resize(size, Image.LANCZOS)
    except Exception as e:
        logger.error(f"Failed to resize image: {e}")
        raise ImageProcessingError(f"Failed to resize image: {e}")


def convert_format(image: Union[Image.Image, np.ndarray], 
                  mode: str) -> Union[Image.Image, np.ndarray]:
    """Convert image format/mode."""
    try:
        if isinstance(image, np.ndarray):
            pil_image = numpy_to_pil_image(image)
            converted_pil = pil_image.convert(mode)
            return np.array(converted_pil)
        else:
            return image.convert(mode)
    except Exception as e:
        logger.error(f"Failed to convert image format: {e}")
        raise ImageProcessingError(f"Failed to convert image format: {e}")


def get_image_info(image: Union[Image.Image, np.ndarray]) -> dict:
    """Get information about an image."""
    try:
        if isinstance(image, np.ndarray):
            return {
                'type': 'numpy_array',
                'shape': image.shape,
                'dtype': str(image.dtype),
                'size': image.size
            }
        else:
            return {
                'type': 'pil_image',
                'size': image.size,
                'mode': image.mode
            }
    except Exception as e:
        logger.error(f"Failed to get image info: {e}")
        return {'error': str(e)} 