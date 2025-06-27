"""
Shader Renderer

This module provides shader rendering capabilities using OpenGL.
It handles shader compilation, linking, rendering, and image generation.
"""

import logging
import time
import ctypes
from typing import Optional, Dict, Any, Tuple, List
import numpy as np
from PIL import Image
import io

from .gl_context import GLContextManager, OpenGLContextError, get_global_context

logger = logging.getLogger(__name__)


class ShaderRenderError(Exception):
    """Exception raised for shader rendering errors."""
    pass


class ShaderRenderer:
    """
    Renders shaders using OpenGL and generates images.
    
    This class provides a high-level interface for shader rendering,
    including compilation, linking, parameter management, and image generation.
    """
    
    def __init__(self, context: Optional[GLContextManager] = None):
        """
        Initialize the shader renderer.
        
        Args:
            context: OpenGL context manager (uses global if None)
        """
        self.context = context or get_global_context()
        self._programs: Dict[str, int] = {}
        self._textures: Dict[str, int] = {}
        self._uniforms: Dict[str, Dict[str, Any]] = {}
        self._default_vertex_shader = """
        #version 330 core
        layout(location = 0) in vec2 position;
        layout(location = 1) in vec2 texCoord;
        
        out vec2 vTexCoord;
        
        void main() {
            gl_Position = vec4(position, 0.0, 1.0);
            vTexCoord = texCoord;
        }
        """
        
        self._quad_vertices = np.array([
            # position (x, y), texCoord (u, v)
            -1.0, -1.0,  0.0, 0.0,
             1.0, -1.0,  1.0, 0.0,
             1.0,  1.0,  1.0, 1.0,
            -1.0,  1.0,  0.0, 1.0
        ], dtype=np.float32)
        
        self._quad_indices = np.array([
            0, 1, 2,
            2, 3, 0
        ], dtype=np.uint32)
    
    def compile_shader(self, name: str, vertex_source: str, fragment_source: str) -> bool:
        """
        Compile a shader program.
        
        Args:
            name: Name for the shader program
            vertex_source: Vertex shader source code
            fragment_source: Fragment shader source code
            
        Returns:
            True if compilation was successful
            
        Raises:
            ShaderRenderError: If compilation fails
        """
        try:
            with self.context.context():
                # Import OpenGL here to avoid import issues
                import OpenGL.GL as gl
                
                # Compile vertex shader
                vertex_shader = self.context.compile_shader(
                    vertex_source, gl.GL_VERTEX_SHADER
                )
                
                # Compile fragment shader
                fragment_shader = self.context.compile_shader(
                    fragment_source, gl.GL_FRAGMENT_SHADER
                )
                
                # Create program
                program = self.context.create_program(vertex_shader, fragment_shader)
                
                # Store program
                self._programs[name] = program
                self._uniforms[name] = {}
                
                logger.info(f"Shader program '{name}' compiled successfully")
                return True
                
        except OpenGLContextError as e:
            error_msg = f"Failed to compile shader '{name}': {e}"
            logger.error(error_msg)
            raise ShaderRenderError(error_msg)
    
    def set_uniform(self, program_name: str, uniform_name: str, value: Any):
        """
        Set a uniform value for a shader program.
        
        Args:
            program_name: Name of the shader program
            uniform_name: Name of the uniform variable
            value: Value to set
        """
        if program_name not in self._programs:
            raise ShaderRenderError(f"Shader program '{program_name}' not found")
        
        self._uniforms[program_name][uniform_name] = value
    
    def create_texture(self, name: str, width: int, height: int, 
                      data: Optional[np.ndarray] = None) -> bool:
        """
        Create a texture.
        
        Args:
            name: Name for the texture
            width: Texture width
            height: Texture height
            data: Texture data (optional)
            
        Returns:
            True if creation was successful
        """
        try:
            with self.context.context():
                texture_id = self.context.create_texture(width, height, data)
                self._textures[name] = texture_id
                logger.info(f"Texture '{name}' created successfully")
                return True
                
        except OpenGLContextError as e:
            error_msg = f"Failed to create texture '{name}': {e}"
            logger.error(error_msg)
            raise ShaderRenderError(error_msg)
    
    def render_to_texture(self, program_name: str, output_texture: str, 
                         width: int, height: int, 
                         input_textures: Optional[Dict[str, str]] = None) -> bool:
        """
        Render a shader to a texture.
        
        Args:
            program_name: Name of the shader program to use
            output_texture: Name of the output texture
            width: Render width
            height: Render height
            input_textures: Dictionary mapping uniform names to texture names
            
        Returns:
            True if rendering was successful
        """
        if program_name not in self._programs:
            raise ShaderRenderError(f"Shader program '{program_name}' not found")
        
        try:
            with self.context.context():
                import OpenGL.GL as gl
                
                # Create framebuffer
                framebuffer_id, texture_id = self.context.create_framebuffer(width, height)
                
                # Bind framebuffer
                gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, framebuffer_id)
                
                # Set viewport
                self.context.set_viewport(width, height)
                
                # Clear
                self.context.clear()
                
                # Use program
                gl.glUseProgram(self._programs[program_name])
                
                # Bind input textures
                if input_textures:
                    for uniform_name, texture_name in input_textures.items():
                        if texture_name in self._textures:
                            texture_unit = len(input_textures) - 1
                            gl.glActiveTexture(gl.GL_TEXTURE0 + texture_unit)
                            gl.glBindTexture(gl.GL_TEXTURE_2D, self._textures[texture_name])
                            gl.glUniform1i(
                                gl.glGetUniformLocation(self._programs[program_name], uniform_name),
                                texture_unit
                            )
                
                # Set uniforms
                for uniform_name, value in self._uniforms[program_name].items():
                    self._set_uniform_value(program_name, uniform_name, value)
                
                # Render quad
                self._render_quad()
                
                # Read pixels
                pixels = self.context.read_pixels(0, 0, width, height)
                
                # Create output texture
                self.create_texture(output_texture, width, height, pixels)
                
                # Clean up framebuffer
                gl.glDeleteFramebuffers([framebuffer_id])
                
                logger.info(f"Rendered to texture '{output_texture}' successfully")
                return True
                
        except OpenGLContextError as e:
            error_msg = f"Failed to render to texture: {e}"
            logger.error(error_msg)
            raise ShaderRenderError(error_msg)
    
    def render_to_image(self, program_name: str, width: int, height: int,
                       input_textures: Optional[Dict[str, str]] = None,
                       format: str = 'PNG') -> bytes:
        """
        Render a shader to an image.
        
        Args:
            program_name: Name of the shader program to use
            width: Render width
            height: Render height
            input_textures: Dictionary mapping uniform names to texture names
            format: Image format ('PNG', 'JPEG', etc.)
            
        Returns:
            Image data as bytes
        """
        if program_name not in self._programs:
            raise ShaderRenderError(f"Shader program '{program_name}' not found")
        
        try:
            with self.context.context():
                import OpenGL.GL as gl
                
                # Create framebuffer
                framebuffer_id, texture_id = self.context.create_framebuffer(width, height)
                
                # Bind framebuffer
                gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, framebuffer_id)
                
                # Set viewport
                self.context.set_viewport(width, height)
                
                # Clear
                self.context.clear()
                
                # Use program
                gl.glUseProgram(self._programs[program_name])
                
                # Bind input textures
                if input_textures:
                    for uniform_name, texture_name in input_textures.items():
                        if texture_name in self._textures:
                            texture_unit = len(input_textures) - 1
                            gl.glActiveTexture(gl.GL_TEXTURE0 + texture_unit)
                            gl.glBindTexture(gl.GL_TEXTURE_2D, self._textures[texture_name])
                            gl.glUniform1i(
                                gl.glGetUniformLocation(self._programs[program_name], uniform_name),
                                texture_unit
                            )
                
                # Set uniforms
                for uniform_name, value in self._uniforms[program_name].items():
                    self._set_uniform_value(program_name, uniform_name, value)
                
                # Render quad
                self._render_quad()
                
                # Read pixels
                pixels = self.context.read_pixels(0, 0, width, height)
                
                # Convert to PIL Image
                image = Image.fromarray(pixels, 'RGBA')
                
                # Convert to bytes
                buffer = io.BytesIO()
                image.save(buffer, format=format)
                image_data = buffer.getvalue()
                
                # Clean up framebuffer
                gl.glDeleteFramebuffers([framebuffer_id])
                
                logger.info(f"Rendered image successfully ({width}x{height}, {format})")
                return image_data
                
        except OpenGLContextError as e:
            error_msg = f"Failed to render image: {e}"
            logger.error(error_msg)
            raise ShaderRenderError(error_msg)
    
    def _render_quad(self):
        """Render a full-screen quad."""
        import OpenGL.GL as gl
        
        # Create VBO for vertices
        vbo_vertices = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_vertices)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, 
            self._quad_vertices.nbytes, 
            self._quad_vertices, 
            gl.GL_STATIC_DRAW
        )
        
        # Create VBO for indices
        vbo_indices = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, vbo_indices)
        gl.glBufferData(
            gl.GL_ELEMENT_ARRAY_BUFFER,
            self._quad_indices.nbytes,
            self._quad_indices,
            gl.GL_STATIC_DRAW
        )
        
        # Set vertex attributes
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, False, 16, None)
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, False, 16, ctypes.c_void_p(8))
        gl.glEnableVertexAttribArray(1)
        
        # Draw
        gl.glDrawElements(
            gl.GL_TRIANGLES, 
            len(self._quad_indices), 
            gl.GL_UNSIGNED_INT, 
            None
        )
        
        # Clean up
        gl.glDeleteBuffers([vbo_vertices, vbo_indices])
    
    def _set_uniform_value(self, program_name: str, uniform_name: str, value: Any):
        """Set a uniform value with proper type handling."""
        import OpenGL.GL as gl
        
        program_id = self._programs[program_name]
        location = gl.glGetUniformLocation(program_id, uniform_name)
        
        if location == -1:
            logger.warning(f"Uniform '{uniform_name}' not found in program '{program_name}'")
            return
        
        if isinstance(value, (int, np.integer)):
            gl.glUniform1i(location, int(value))
        elif isinstance(value, (float, np.floating)):
            gl.glUniform1f(location, float(value))
        elif isinstance(value, (list, tuple, np.ndarray)):
            if len(value) == 2:
                gl.glUniform2f(location, float(value[0]), float(value[1]))
            elif len(value) == 3:
                gl.glUniform3f(location, float(value[0]), float(value[1]), float(value[2]))
            elif len(value) == 4:
                gl.glUniform4f(location, float(value[0]), float(value[1]), float(value[2]), float(value[3]))
        else:
            logger.warning(f"Unsupported uniform type for '{uniform_name}': {type(value)}")
    
    def cleanup(self):
        """Clean up shader renderer resources."""
        try:
            with self.context.context():
                import OpenGL.GL as gl
                
                # Clean up programs
                for program_id in self._programs.values():
                    if gl.glIsProgram(program_id):
                        gl.glDeleteProgram(program_id)
                
                # Clean up textures
                for texture_id in self._textures.values():
                    if gl.glIsTexture(texture_id):
                        gl.glDeleteTextures([texture_id])
                
                self._programs.clear()
                self._textures.clear()
                self._uniforms.clear()
                
                logger.info("Shader renderer cleaned up successfully")
                
        except Exception as e:
            logger.error(f"Error during shader renderer cleanup: {e}")
    
    def get_program_info(self, program_name: str) -> Dict[str, Any]:
        """
        Get information about a shader program.
        
        Args:
            program_name: Name of the shader program
            
        Returns:
            Dictionary with program information
        """
        if program_name not in self._programs:
            raise ShaderRenderError(f"Shader program '{program_name}' not found")
        
        program_id = self._programs[program_name]
        
        try:
            with self.context.context():
                import OpenGL.GL as gl
                
                info = {
                    'name': program_name,
                    'id': program_id,
                    'uniforms': self._uniforms[program_name],
                    'linked': gl.glGetProgramiv(program_id, gl.GL_LINK_STATUS),
                    'validated': gl.glGetProgramiv(program_id, gl.GL_VALIDATE_STATUS)
                }
                return info
                
        except OpenGLContextError as e:
            logger.error(f"Failed to get program info: {e}")
            return {'name': program_name, 'error': str(e)} 