"""
Test Configuration and Fixtures

This module provides shared fixtures and configuration for all tests.
"""

import pytest
import json
import os
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from src.api.main import app
from src.services.validation_service import ValidationService
from src.services.visualization_service import VisualizationService
from src.services.analysis_service import AnalysisService


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def sample_glsl_shader() -> str:
    """Provide a sample GLSL shader for testing."""
    return """
    #version 330 core
    
    uniform float time;
    uniform vec2 resolution;
    uniform vec4 color = vec4(1.0, 0.0, 0.0, 1.0);
    
    out vec4 fragColor;
    
    void main() {
        vec2 uv = gl_FragCoord.xy / resolution;
        vec4 finalColor = color;
        
        // Simple animation
        finalColor.rgb *= 0.5 + 0.5 * sin(time + uv.x * 10.0);
        
        fragColor = finalColor;
    }
    """


@pytest.fixture
def sample_isf_shader() -> dict:
    """Provide a sample ISF shader for testing."""
    fixture_path = Path(__file__).parent / "fixtures" / "shaders" / "test_isf_shader.json"
    with open(fixture_path, 'r') as f:
        return json.load(f)


@pytest.fixture
def spherical_eye_shader() -> str:
    """Provide the SphericalEye ISF shader for testing."""
    fixture_path = Path(__file__).parent / "fixtures" / "shaders" / "spherical_eye.fs"
    with open(fixture_path, 'r') as f:
        return f.read()


@pytest.fixture
def sample_madmapper_shader() -> str:
    """Provide a sample MadMapper shader for testing."""
    fixture_path = Path(__file__).parent / "fixtures" / "shaders" / "test_madmapper_shader.mad"
    with open(fixture_path, 'r') as f:
        return f.read()


@pytest.fixture
def validation_service() -> ValidationService:
    """Provide a validation service instance for testing."""
    return ValidationService()


@pytest.fixture
def visualization_service() -> VisualizationService:
    """Provide a visualization service instance for testing."""
    return VisualizationService()


@pytest.fixture
def analysis_service() -> AnalysisService:
    """Provide an analysis service instance for testing."""
    return AnalysisService()


@pytest.fixture
def mock_gl_context():
    """Provide a mock OpenGL context for testing."""
    with patch('src.core.renderers.gl_context.GLContext') as mock_context:
        mock_context.return_value.initialize.return_value = True
        mock_context.return_value.make_current.return_value = True
        mock_context.return_value.cleanup.return_value = None
        yield mock_context.return_value


@pytest.fixture
def mock_shader_renderer():
    """Provide a mock shader renderer for testing."""
    with patch('src.core.renderers.shader_renderer.ShaderRenderer') as mock_renderer:
        mock_renderer.return_value.compile_shader.return_value = True
        mock_renderer.return_value.link_program.return_value = True
        mock_renderer.return_value.render.return_value = b'fake_image_data'
        mock_renderer.return_value.cleanup.return_value = None
        yield mock_renderer.return_value


@pytest.fixture
def mock_vvisf_engine():
    """Provide a mock VVISF engine for testing."""
    with patch('src.bindings.vvisf_bindings.VVISFEngine') as mock_engine:
        mock_engine.return_value.validate_isf.return_value = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        mock_engine.return_value.render_shader.return_value = {
            "success": True,
            "image_data": b'fake_image_data',
            "width": 256,
            "height": 256
        }
        yield mock_engine.return_value


@pytest.fixture
def sample_validation_request() -> Dict[str, Any]:
    """Provide a sample validation request for testing."""
    return {
        "code": """
        #version 330 core
        out vec4 fragColor;
        void main() {
            fragColor = vec4(1.0, 0.0, 0.0, 1.0);
        }
        """,
        "format": "glsl",
        "target_version": "330",
        "custom_parameters": {"time": 0.0}
    }


@pytest.fixture
def sample_visualization_request() -> Dict[str, Any]:
    """Provide a sample visualization request for testing."""
    return {
        "code": """
        #version 330 core
        out vec4 fragColor;
        void main() {
            fragColor = vec4(1.0, 0.0, 0.0, 1.0);
        }
        """,
        "format": "glsl",
        "width": 256,
        "height": 256,
        "output_format": "PNG",
        "custom_parameters": {"time": 0.0}
    }


@pytest.fixture
def sample_analysis_request() -> Dict[str, Any]:
    """Provide a sample analysis request for testing."""
    return {
        "code": """
        #version 330 core
        out vec4 fragColor;
        void main() {
            fragColor = vec4(1.0, 0.0, 0.0, 1.0);
        }
        """,
        "format": "glsl",
        "analysis_types": ["performance", "complexity"]
    }


@pytest.fixture
def sample_batch_request() -> Dict[str, Any]:
    """Provide a sample batch validation request for testing."""
    return {
        "shaders": [
            {
                "code": """
                #version 330 core
                out vec4 fragColor;
                void main() {
                    fragColor = vec4(1.0, 0.0, 0.0, 1.0);
                }
                """,
                "format": "glsl",
                "target_version": "330"
            },
            {
                "code": """
                #version 330 core
                out vec4 fragColor;
                void main() {
                    fragColor = vec4(0.0, 1.0, 0.0, 1.0);
                }
                """,
                "format": "glsl",
                "target_version": "330"
            }
        ],
        "parallel_processing": True
    }


@pytest.fixture
def invalid_glsl_shader() -> str:
    """Provide an invalid GLSL shader for testing error handling."""
    return """
    #version 330 core
    out vec4 fragColor
    void main() {
        fragColor = vec4(1.0, 0.0, 0.0, 1.0  // Missing semicolon and closing parenthesis
    }
    """


@pytest.fixture
def invalid_isf_shader() -> str:
    """Provide an invalid ISF shader for testing error handling."""
    return "{ invalid json }"


@pytest.fixture
def invalid_madmapper_shader() -> str:
    """Provide an invalid MadMapper shader for testing error handling."""
    return """
    // Missing @name directive
    // FRAGMENT_SHADER
    void main() {
        // No gl_FragColor assignment
    }
    """


@pytest.fixture
def large_shader() -> str:
    """Provide a very large shader for testing performance."""
    base_shader = """
    #version 330 core
    out vec4 fragColor;
    void main() {
        fragColor = vec4(1.0, 0.0, 0.0, 1.0);
    }
    """
    return base_shader * 1000  # Repeat the shader 1000 times


@pytest.fixture
def complex_shader() -> str:
    """Provide a complex shader for testing analysis."""
    return """
    #version 330 core
    
    uniform float time;
    uniform vec2 resolution;
    uniform sampler2D texture0;
    uniform sampler2D texture1;
    
    out vec4 fragColor;
    
    vec3 palette(float t) {
        vec3 a = vec3(0.5, 0.5, 0.5);
        vec3 b = vec3(0.5, 0.5, 0.5);
        vec3 c = vec3(1.0, 1.0, 1.0);
        vec3 d = vec3(0.263, 0.416, 0.557);
        return a + b * cos(6.28318 * (c * t + d));
    }
    
    float map(vec3 p) {
        float d = 0.0;
        for(int i = 0; i < 8; i++) {
            float t = time * 0.1;
            p.xz *= mat2(cos(t), -sin(t), sin(t), cos(t));
            p = abs(p) - vec3(0.5, 0.5, 0.5);
            if(p.x < p.y) p.xy = p.yx;
            if(p.x < p.z) p.xz = p.zx;
            if(p.y < p.z) p.yz = p.zy;
            d = length(p) - 0.1;
        }
        return d;
    }
    
    void main() {
        vec2 uv = (gl_FragCoord.xy * 2.0 - resolution.xy) / resolution.y;
        vec3 ro = vec3(0.0, 0.0, -3.0);
        vec3 rd = normalize(vec3(uv, 1.0));
        
        float t = 0.0;
        vec3 p = ro;
        
        for(int i = 0; i < 100; i++) {
            float d = map(p);
            if(d < 0.001 || t > 20.0) break;
            t += d;
            p = ro + rd * t;
        }
        
        float c = t / 20.0;
        fragColor = vec4(palette(c), 1.0);
    }
    """


@pytest.fixture(scope="session")
def setup_test_database():
    """Set up test database with required tables."""
    from src.database.connection import engine
    from src.database.models import Base
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up tables after tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def setup_db(setup_test_database):
    """Auto-use database setup for all tests."""
    pass


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "api: mark test as API test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add default markers."""
    for item in items:
        # Add unit marker to tests that don't have any marker
        if not any(item.iter_markers()):
            item.add_marker(pytest.mark.unit) 