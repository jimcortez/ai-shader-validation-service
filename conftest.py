"""
Pytest Configuration and Fixtures

This module provides pytest configuration and common fixtures
for the AI Shader Validator test suite.
"""

import pytest
import asyncio
import tempfile
import os
from typing import Dict, Any, Generator
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from src.api.main import app
from src.services.validation_service import get_validation_service
from src.services.visualization_service import get_visualization_service
from src.services.analysis_service import get_analysis_service


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def validation_service():
    """Get the validation service instance."""
    return get_validation_service()


@pytest.fixture
def visualization_service():
    """Get the visualization service instance."""
    return get_visualization_service()


@pytest.fixture
def analysis_service():
    """Get the analysis service instance."""
    return get_analysis_service()


@pytest.fixture
def sample_glsl_shader():
    """Sample GLSL fragment shader for testing."""
    return """
    #version 330 core
    
    uniform float time;
    uniform vec2 resolution;
    
    out vec4 fragColor;
    
    void main() {
        vec2 uv = gl_FragCoord.xy / resolution.xy;
        vec3 color = vec3(uv.x, uv.y, sin(time));
        fragColor = vec4(color, 1.0);
    }
    """


@pytest.fixture
def sample_isf_shader():
    """Sample ISF shader for testing."""
    return {
        "ISFVersion": "2",
        "DESCRIPTION": "Test ISF Shader",
        "INPUTS": [
            {
                "NAME": "time",
                "TYPE": "float",
                "DEFAULT": 0.0,
                "MIN": 0.0,
                "MAX": 100.0
            }
        ],
        "PASSES": [
            {
                "TARGET": "bufferVariableA",
                "PERSISTENT": True,
                "FLOAT": True
            }
        ],
        "IMPORTED": {},
        "CODE": [
            "vec4 renderMain() {",
            "    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy;",
            "    vec3 color = vec3(uv.x, uv.y, sin(TIME));",
            "    return vec4(color, 1.0);",
            "}"
        ]
    }


@pytest.fixture
def sample_madmapper_shader():
    """Sample MadMapper shader for testing."""
    return """
    // MadMapper Shader
    // @name Test Shader
    // @description A test shader for MadMapper
    // @author Test Author
    // @version 1.0
    
    uniform float time;
    uniform vec2 resolution;
    
    void main() {
        vec2 uv = gl_FragCoord.xy / resolution.xy;
        vec3 color = vec3(uv.x, uv.y, sin(time));
        gl_FragColor = vec4(color, 1.0);
    }
    """


@pytest.fixture
def mock_gl_context():
    """Mock OpenGL context for testing."""
    with patch('src.core.renderers.gl_context.OpenGLContext') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        mock_instance.__enter__ = Mock(return_value=mock_instance)
        mock_instance.__exit__ = Mock(return_value=None)
        yield mock_instance


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_cache_manager():
    """Mock cache manager for testing."""
    with patch('src.core.utils.cache_manager.get_cache_manager') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        mock_instance.get.return_value = None
        mock_instance.set.return_value = True
        mock_instance.exists.return_value = False
        yield mock_instance


@pytest.fixture
def mock_performance_monitor():
    """Mock performance monitor for testing."""
    with patch('src.core.utils.performance_monitor.get_performance_monitor') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        mock_instance.get_stats.return_value = {
            'cpu_usage': 50.0,
            'memory_usage': 60.0,
            'disk_usage': 70.0
        }
        yield mock_instance


@pytest.fixture
def mock_queue_service():
    """Mock queue service for testing."""
    with patch('src.services.queue_service.get_queue_service') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        mock_instance.submit_job.return_value = "test-job-id"
        mock_instance.get_job_status.return_value = {
            'id': 'test-job-id',
            'status': 'completed',
            'result': {'test': 'result'}
        }
        yield mock_instance


@pytest.fixture
def validation_request_data():
    """Sample validation request data."""
    return {
        "shader_type": "GLSL",
        "shader_source": """
        #version 330 core
        uniform float time;
        out vec4 fragColor;
        void main() {
            fragColor = vec4(1.0, 0.0, 0.0, 1.0);
        }
        """,
        "parameters": {
            "time": 0.0
        }
    }


@pytest.fixture
def visualization_request_data():
    """Sample visualization request data."""
    return {
        "shader_type": "GLSL",
        "shader_source": """
        #version 330 core
        uniform float time;
        out vec4 fragColor;
        void main() {
            vec2 uv = gl_FragCoord.xy / vec2(512.0, 512.0);
            fragColor = vec4(uv.x, uv.y, sin(time), 1.0);
        }
        """,
        "width": 512,
        "height": 512,
        "format": "PNG",
        "parameters": {
            "time": 0.0
        }
    }


@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection for testing."""
    mock_ws = Mock()
    mock_ws.send_text = Mock()
    mock_ws.receive_text = Mock()
    mock_ws.close = Mock()
    mock_ws.client.host = "127.0.0.1"
    return mock_ws


@pytest.fixture
def sample_validation_errors():
    """Sample validation errors for testing."""
    from src.core.models.errors import ValidationError, ErrorSeverity
    
    return [
        ValidationError(
            message="Undefined variable 'undefined_var'",
            severity=ErrorSeverity.ERROR,
            line_number=5,
            column_number=10
        ),
        ValidationError(
            message="Missing semicolon",
            severity=ErrorSeverity.WARNING,
            line_number=8,
            column_number=15
        )
    ]


@pytest.fixture
def sample_performance_data():
    """Sample performance data for testing."""
    return {
        "cpu_usage": 45.2,
        "memory_usage": 67.8,
        "texture_lookups": 15,
        "arithmetic_operations": 120,
        "conditional_statements": 8
    }


@pytest.fixture
def mock_ml_analyzer():
    """Mock ML analyzer for testing."""
    with patch('src.core.analyzers.ml_analyzer.MLAnalyzer') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        mock_instance.analyze_shader_ml.return_value = {
            'error_predictions': [],
            'optimization_suggestions': [],
            'quality_score': 0.85
        }
        yield mock_instance


@pytest.fixture
def mock_error_visualizer():
    """Mock error visualizer for testing."""
    with patch('src.core.renderers.error_visualizer.ErrorVisualizer') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        mock_instance.create_error_report_image.return_value = b"fake_image_data"
        yield mock_instance


@pytest.fixture
def mock_performance_charts():
    """Mock performance charts for testing."""
    with patch('src.core.renderers.performance_charts.PerformanceCharts') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        mock_instance.create_performance_bar_chart.return_value = b"fake_chart_data"
        yield mock_instance


@pytest.fixture
def mock_dependency_graphs():
    """Mock dependency graphs for testing."""
    with patch('src.core.renderers.dependency_graphs.DependencyGraphs') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        mock_instance.create_function_dependency_graph.return_value = b"fake_graph_data"
        yield mock_instance


@pytest.fixture
def test_settings():
    """Test settings configuration."""
    return {
        "app_name": "AI Shader Validator Test",
        "app_version": "1.0.0-test",
        "debug": True,
        "log_level": "DEBUG",
        "host": "127.0.0.1",
        "port": 8000,
        "rate_limit_per_minute": 100,
        "max_shader_size": 1024 * 1024,
        "max_batch_size": 10,
        "validation_timeout": 30,
        "default_image_width": 512,
        "default_image_height": 512,
        "max_image_size": 2048
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test."""
    # Set test environment variables
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DEBUG"] = "true"
    
    yield
    
    # Cleanup after test
    pass


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "security: mark test as a security test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add markers based on test file names
        if "test_api" in item.nodeid:
            item.add_marker(pytest.mark.api)
        elif "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "test_security" in item.nodeid:
            item.add_marker(pytest.mark.security)
        elif "test_performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)
        else:
            item.add_marker(pytest.mark.unit) 