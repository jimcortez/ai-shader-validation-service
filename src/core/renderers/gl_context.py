"""
OpenGL Context Management

This module provides OpenGL context management for shader rendering.
It handles context creation, cleanup, and provides a safe interface for OpenGL operations.
"""

import logging
import threading
from contextlib import contextmanager
from typing import Optional, Tuple, Dict, Any
import numpy as np

try:
    import OpenGL.GL as gl
    import OpenGL.GLU as glu
    from OpenGL.GL import shaders
    from OpenGL.arrays import vbo
    from OpenGL.arrays import numpy as gl_numpy
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    logging.warning("PyOpenGL not available. OpenGL rendering will be disabled.")

logger = logging.getLogger(__name__)


class OpenGLContextError(Exception):
    """Exception raised for OpenGL context errors."""
    pass


class GLContextManager:
    """
    Manages OpenGL context for shader rendering.
    
    This class provides a thread-safe interface for OpenGL operations,
    handling context creation, cleanup, and resource management.
    """
    
    def __init__(self, width: int = 512, height: int = 512):
        """
        Initialize the OpenGL context manager.
        
        Args:
            width: Default viewport width
            height: Default viewport height
        """
        self.width = width
        self.height = height
        self._context_initialized = False
        self._lock = threading.RLock()
        self._shader_cache: Dict[str, int] = {}
        self._texture_cache: Dict[str, int] = {}
        
    def initialize_context(self) -> bool:
        """
        Initialize the OpenGL context.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        if not OPENGL_AVAILABLE:
            logger.error("PyOpenGL not available. Cannot initialize OpenGL context.")
            return False
            
        with self._lock:
            try:
                # Initialize OpenGL context
                gl.glEnable(gl.GL_DEPTH_TEST)
                gl.glEnable(gl.GL_BLEND)
                gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
                
                # Set viewport
                gl.glViewport(0, 0, self.width, self.height)
                
                # Set clear color
                gl.glClearColor(0.0, 0.0, 0.0, 1.0)
                
                self._context_initialized = True
                logger.info("OpenGL context initialized successfully")
                return True
                
            except Exception as e:
                logger.error(f"Failed to initialize OpenGL context: {e}")
                return False
    
    def cleanup(self):
        """Clean up OpenGL resources."""
        with self._lock:
            try:
                # Clean up shaders
                for shader_id in self._shader_cache.values():
                    if gl.glIsShader(shader_id):
                        gl.glDeleteShader(shader_id)
                
                # Clean up textures
                for texture_id in self._texture_cache.values():
                    if gl.glIsTexture(texture_id):
                        gl.glDeleteTextures([texture_id])
                
                self._shader_cache.clear()
                self._texture_cache.clear()
                self._context_initialized = False
                
                logger.info("OpenGL context cleaned up successfully")
                
            except Exception as e:
                logger.error(f"Error during OpenGL cleanup: {e}")
    
    @contextmanager
    def context(self):
        """
        Context manager for OpenGL operations.
        
        Yields:
            Self for chaining operations
        """
        if not self._context_initialized:
            if not self.initialize_context():
                raise OpenGLContextError("Failed to initialize OpenGL context")
        
        try:
            yield self
        except Exception as e:
            logger.error(f"Error in OpenGL context: {e}")
            raise
    
    def set_viewport(self, width: int, height: int):
        """
        Set the viewport dimensions.
        
        Args:
            width: Viewport width
            height: Viewport height
        """
        with self._lock:
            self.width = width
            self.height = height
            gl.glViewport(0, 0, width, height)
    
    def clear(self, color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)):
        """
        Clear the framebuffer.
        
        Args:
            color: Clear color (r, g, b, a)
        """
        with self._lock:
            gl.glClearColor(*color)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    
    def compile_shader(self, source: str, shader_type: int) -> int:
        """
        Compile a shader from source.
        
        Args:
            source: Shader source code
            shader_type: Type of shader (GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, etc.)
            
        Returns:
            Shader ID
            
        Raises:
            OpenGLContextError: If compilation fails
        """
        with self._lock:
            try:
                shader = shaders.compileShader(source, shader_type)
                return shader
            except Exception as e:
                error_msg = f"Shader compilation failed: {e}"
                logger.error(error_msg)
                raise OpenGLContextError(error_msg)
    
    def create_program(self, vertex_shader: int, fragment_shader: int) -> int:
        """
        Create a shader program from vertex and fragment shaders.
        
        Args:
            vertex_shader: Vertex shader ID
            fragment_shader: Fragment shader ID
            
        Returns:
            Program ID
            
        Raises:
            OpenGLContextError: If program creation fails
        """
        with self._lock:
            try:
                program = shaders.compileProgram(vertex_shader, fragment_shader)
                return program
            except Exception as e:
                error_msg = f"Program creation failed: {e}"
                logger.error(error_msg)
                raise OpenGLContextError(error_msg)
    
    def create_texture(self, width: int, height: int, data: Optional[np.ndarray] = None) -> int:
        """
        Create a texture.
        
        Args:
            width: Texture width
            height: Texture height
            data: Texture data (optional)
            
        Returns:
            Texture ID
        """
        with self._lock:
            texture_id = gl.glGenTextures(1)
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
            
            # Set texture parameters
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
            gl.glParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
            
            if data is not None:
                gl.glTexImage2D(
                    gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0,
                    gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, data
                )
            else:
                gl.glTexImage2D(
                    gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0,
                    gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None
                )
            
            return texture_id
    
    def create_framebuffer(self, width: int, height: int) -> Tuple[int, int]:
        """
        Create a framebuffer with a color texture attachment.
        
        Args:
            width: Framebuffer width
            height: Framebuffer height
            
        Returns:
            Tuple of (framebuffer_id, texture_id)
        """
        with self._lock:
            # Create framebuffer
            framebuffer_id = gl.glGenFramebuffers(1)
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, framebuffer_id)
            
            # Create texture attachment
            texture_id = self.create_texture(width, height)
            gl.glFramebufferTexture2D(
                gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, texture_id, 0
            )
            
            # Check framebuffer status
            if gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER) != gl.GL_FRAMEBUFFER_COMPLETE:
                raise OpenGLContextError("Framebuffer is not complete")
            
            return framebuffer_id, texture_id
    
    def read_pixels(self, x: int = 0, y: int = 0, width: Optional[int] = None, 
                   height: Optional[int] = None) -> np.ndarray:
        """
        Read pixels from the current framebuffer.
        
        Args:
            x: Starting x coordinate
            y: Starting y coordinate
            width: Width to read (defaults to viewport width)
            height: Height to read (defaults to viewport height)
            
        Returns:
            Pixel data as numpy array
        """
        with self._lock:
            if width is None:
                width = self.width
            if height is None:
                height = self.height
            
            pixels = gl.glReadPixels(x, y, width, height, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE)
            return np.frombuffer(pixels, dtype=np.uint8).reshape(height, width, 4)
    
    def get_error(self) -> Optional[str]:
        """
        Get the last OpenGL error.
        
        Returns:
            Error string or None if no error
        """
        error = gl.glGetError()
        if error != gl.GL_NO_ERROR:
            return f"OpenGL Error: {error}"
        return None


# Global context manager instance
_global_context: Optional[GLContextManager] = None


def get_global_context() -> GLContextManager:
    """
    Get the global OpenGL context manager.
    
    Returns:
        Global context manager instance
    """
    global _global_context
    if _global_context is None:
        _global_context = GLContextManager()
    return _global_context


def cleanup_global_context():
    """Clean up the global OpenGL context."""
    global _global_context
    if _global_context is not None:
        _global_context.cleanup()
        _global_context = None 