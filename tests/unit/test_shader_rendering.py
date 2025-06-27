"""
Tests for shader rendering system.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch

from src.core.renderers.shader_renderer import ShaderRenderer, ShaderRenderError
from src.core.renderers.gl_context import GLContextManager, OpenGLContextError
from src.services.visualization_service import VisualizationService, VisualizationError
from src.core.utils.image_utils import numpy_to_pil_image, get_image_info


class TestShaderRenderer:
    """Test cases for ShaderRenderer class."""
    
    def test_shader_renderer_initialization(self):
        """Test ShaderRenderer initialization."""
        renderer = ShaderRenderer()
        assert renderer is not None
        assert hasattr(renderer, '_programs')
        assert hasattr(renderer, '_textures')
        assert hasattr(renderer, '_uniforms')
    
    def test_shader_renderer_with_custom_context(self):
        """Test ShaderRenderer with custom context."""
        context = Mock(spec=GLContextManager)
        renderer = ShaderRenderer(context)
        assert renderer.context == context
    
    @patch('src.core.renderers.shader_renderer.OPENGL_AVAILABLE', False)
    def test_shader_renderer_without_opengl(self):
        """Test ShaderRenderer behavior when OpenGL is not available."""
        renderer = ShaderRenderer()
        # Should not raise an error during initialization
        assert renderer is not None
    
    def test_set_uniform(self):
        """Test setting uniform values."""
        renderer = ShaderRenderer()
        
        # Mock program
        renderer._programs['test_program'] = 1
        renderer._uniforms['test_program'] = {}
        
        # Test setting uniform
        renderer.set_uniform('test_program', 'test_uniform', 1.0)
        assert renderer._uniforms['test_program']['test_uniform'] == 1.0
    
    def test_set_uniform_invalid_program(self):
        """Test setting uniform with invalid program name."""
        renderer = ShaderRenderer()
        
        with pytest.raises(ShaderRenderError, match="Shader program 'invalid' not found"):
            renderer.set_uniform('invalid', 'test_uniform', 1.0)
    
    def test_cleanup(self):
        """Test shader renderer cleanup."""
        renderer = ShaderRenderer()
        
        # Mock programs and textures
        renderer._programs['test_program'] = 1
        renderer._textures['test_texture'] = 1
        renderer._uniforms['test_program'] = {'test_uniform': 1.0}
        
        # Test cleanup
        renderer.cleanup()
        
        assert len(renderer._programs) == 0
        assert len(renderer._textures) == 0
        assert len(renderer._uniforms) == 0


class TestVisualizationService:
    """Test cases for VisualizationService class."""
    
    def test_visualization_service_initialization(self):
        """Test VisualizationService initialization."""
        service = VisualizationService()
        assert service is not None
        assert hasattr(service, 'renderer')
        assert hasattr(service, '_cache')
        assert hasattr(service, '_metadata')
    
    def test_render_glsl_shader(self):
        """Test rendering GLSL shader."""
        service = VisualizationService()
        
        # Simple test fragment shader
        fragment_shader = """
        #version 330 core
        in vec2 vTexCoord;
        out vec4 fragColor;
        
        void main() {
            fragColor = vec4(vTexCoord, 0.0, 1.0);
        }
        """
        
        # Mock the renderer to avoid actual OpenGL calls
        with patch.object(service.renderer, 'compile_shader', return_value=True), \
             patch.object(service.renderer, 'render_to_image', return_value=b'test_image_data'):
            
            image_id, image_data = service.render_glsl_shader(fragment_shader)
            
            assert image_id is not None
            assert image_data == b'test_image_data'
            assert image_id in service._cache
            assert image_id in service._metadata
    
    def test_render_isf_shader(self):
        """Test rendering ISF shader."""
        service = VisualizationService()
        
        # Mock ISF data
        isf_data = {
            'PASSES': [{
                'TARGET': 'vertex_shader_code',
                'FS': 'fragment_shader_code'
            }],
            'INPUTS': {
                'test_param': {'TYPE': 'float', 'DEFAULT': 1.0}
            }
        }
        
        # Mock the renderer
        with patch.object(service.renderer, 'compile_shader', return_value=True), \
             patch.object(service.renderer, 'render_to_image', return_value=b'test_image_data'):
            
            image_id, image_data = service.render_isf_shader(isf_data)
            
            assert image_id is not None
            assert image_data == b'test_image_data'
    
    def test_render_isf_shader_no_passes(self):
        """Test rendering ISF shader with no passes."""
        service = VisualizationService()
        
        isf_data = {'PASSES': []}
        
        with pytest.raises(VisualizationError, match="No passes found in ISF data"):
            service.render_isf_shader(isf_data)
    
    def test_get_image(self):
        """Test getting image from cache."""
        service = VisualizationService()
        
        # Add test image to cache
        test_id = 'test_id'
        test_data = b'test_data'
        service._cache[test_id] = test_data
        
        # Test getting image
        result = service.get_image(test_id)
        assert result == test_data
        
        # Test getting non-existent image
        result = service.get_image('non_existent')
        assert result is None
    
    def test_get_image_metadata(self):
        """Test getting image metadata."""
        service = VisualizationService()
        
        # Add test metadata
        test_id = 'test_id'
        test_metadata = {'width': 512, 'height': 512}
        service._metadata[test_id] = test_metadata
        
        # Test getting metadata
        result = service.get_image_metadata(test_id)
        assert result == test_metadata
        
        # Test getting non-existent metadata
        result = service.get_image_metadata('non_existent')
        assert result is None
    
    def test_list_images(self):
        """Test listing cached images."""
        service = VisualizationService()
        
        # Add test images
        test_id1 = 'test_id1'
        test_id2 = 'test_id2'
        service._cache[test_id1] = b'data1'
        service._cache[test_id2] = b'data2'
        service._metadata[test_id1] = {'width': 512, 'height': 512}
        service._metadata[test_id2] = {'width': 256, 'height': 256}
        
        # Test listing images
        images = service.list_images()
        assert len(images) == 2
        
        # Check that both images are present
        image_ids = [img['id'] for img in images]
        assert test_id1 in image_ids
        assert test_id2 in image_ids
    
    def test_clear_cache(self):
        """Test clearing image cache."""
        service = VisualizationService()
        
        # Add test data
        test_id = 'test_id'
        service._cache[test_id] = b'test_data'
        service._metadata[test_id] = {'width': 512, 'height': 512}
        
        # Test clearing specific image
        service.clear_cache(test_id)
        assert test_id not in service._cache
        assert test_id not in service._metadata
        
        # Test clearing all images
        service._cache[test_id] = b'test_data'
        service._metadata[test_id] = {'width': 512, 'height': 512}
        
        service.clear_cache()
        assert len(service._cache) == 0
        assert len(service._metadata) == 0
    
    def test_cleanup(self):
        """Test visualization service cleanup."""
        service = VisualizationService()
        
        # Add test data
        service._cache['test_id'] = b'test_data'
        service._metadata['test_id'] = {'width': 512, 'height': 512}
        
        # Mock renderer cleanup
        with patch.object(service.renderer, 'cleanup'):
            service.cleanup()
            
            # Check that cache is cleared
            assert len(service._cache) == 0
            assert len(service._metadata) == 0


class TestImageUtils:
    """Test cases for image utilities."""
    
    def test_numpy_to_pil_image_conversion(self):
        """Test numpy array to PIL Image conversion."""
        # Test RGB array
        rgb_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        with patch('src.core.utils.image_utils.Image') as mock_image:
            mock_pil_image = Mock()
            mock_image.fromarray.return_value = mock_pil_image
            
            result = numpy_to_pil_image(rgb_array)
            
            assert result == mock_pil_image
            mock_image.fromarray.assert_called_once_with(rgb_array, 'RGB')
    
    def test_get_image_info(self):
        """Test getting image information."""
        # Test numpy array
        test_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        info = get_image_info(test_array)
        
        assert info['type'] == 'numpy_array'
        assert info['shape'] == (100, 100, 3)
        assert info['dtype'] == 'uint8'
        assert info['size'] == 30000  # 100 * 100 * 3 