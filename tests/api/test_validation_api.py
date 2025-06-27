"""
API Tests for Validation Endpoints

This module contains comprehensive tests for the validation API endpoints.
"""

import pytest
import json
from fastapi.testclient import TestClient


@pytest.mark.api
class TestValidationAPI:
    """Test cases for validation API endpoints."""
    
    def test_validate_glsl_shader_success(self, client: TestClient, sample_glsl_shader: str):
        """Test successful GLSL shader validation."""
        request_data = {
            "shader_type": "GLSL",
            "shader_source": sample_glsl_shader,
            "parameters": {"time": 0.0}
        }
        
        response = client.post("/api/v1/validate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "validation_result" in data
        assert "errors" in data["validation_result"]
        assert "warnings" in data["validation_result"]
        assert "is_valid" in data["validation_result"]
    
    def test_validate_isf_shader_success(self, client: TestClient, sample_isf_shader: dict):
        """Test successful ISF shader validation."""
        request_data = {
            "shader_type": "ISF",
            "shader_source": json.dumps(sample_isf_shader),
            "parameters": {"time": 0.0}
        }
        
        response = client.post("/api/v1/validate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "validation_result" in data
        assert "errors" in data["validation_result"]
        assert "warnings" in data["validation_result"]
        assert "is_valid" in data["validation_result"]
    
    def test_validate_madmapper_shader_success(self, client: TestClient, sample_madmapper_shader: str):
        """Test successful MadMapper shader validation."""
        request_data = {
            "shader_type": "MADMAPPER",
            "shader_source": sample_madmapper_shader,
            "parameters": {"time": 0.0}
        }
        
        response = client.post("/api/v1/validate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "validation_result" in data
        assert "errors" in data["validation_result"]
        assert "warnings" in data["validation_result"]
        assert "is_valid" in data["validation_result"]
    
    def test_validate_invalid_shader_type(self, client: TestClient):
        """Test validation with invalid shader type."""
        request_data = {
            "shader_type": "INVALID_TYPE",
            "shader_source": "void main() {}",
            "parameters": {}
        }
        
        response = client.post("/api/v1/validate", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
    
    def test_validate_missing_shader_source(self, client: TestClient):
        """Test validation with missing shader source."""
        request_data = {
            "shader_type": "GLSL",
            "parameters": {}
        }
        
        response = client.post("/api/v1/validate", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_validate_empty_shader_source(self, client: TestClient):
        """Test validation with empty shader source."""
        request_data = {
            "shader_type": "GLSL",
            "shader_source": "",
            "parameters": {}
        }
        
        response = client.post("/api/v1/validate", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
    
    def test_validate_glsl_with_syntax_error(self, client: TestClient):
        """Test GLSL validation with syntax error."""
        invalid_shader = """
        #version 330 core
        uniform float time;
        out vec4 fragColor;
        void main() {
            fragColor = vec4(1.0, 0.0, 0.0, 1.0  // Missing semicolon
        }
        """
        
        request_data = {
            "shader_type": "GLSL",
            "shader_source": invalid_shader,
            "parameters": {"time": 0.0}
        }
        
        response = client.post("/api/v1/validate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "validation_result" in data
        assert len(data["validation_result"]["errors"]) > 0
        assert not data["validation_result"]["is_valid"]
    
    def test_validate_isf_with_invalid_json(self, client: TestClient):
        """Test ISF validation with invalid JSON."""
        request_data = {
            "shader_type": "ISF",
            "shader_source": "{ invalid json }",
            "parameters": {}
        }
        
        response = client.post("/api/v1/validate", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
    
    def test_validate_with_large_shader(self, client: TestClient):
        """Test validation with very large shader."""
        large_shader = "void main() { " + "fragColor = vec4(1.0); " * 10000 + "}"
        
        request_data = {
            "shader_type": "GLSL",
            "shader_source": large_shader,
            "parameters": {}
        }
        
        response = client.post("/api/v1/validate", json=request_data)
        
        # Should either succeed or return a specific error for large shaders
        assert response.status_code in [200, 413]
    
    def test_validate_with_special_characters(self, client: TestClient):
        """Test validation with special characters in shader."""
        shader_with_special_chars = """
        #version 330 core
        // Shader with special chars: éñçüöä
        uniform float time;
        out vec4 fragColor;
        void main() {
            fragColor = vec4(1.0, 0.0, 0.0, 1.0);
        }
        """
        
        request_data = {
            "shader_type": "GLSL",
            "shader_source": shader_with_special_chars,
            "parameters": {"time": 0.0}
        }
        
        response = client.post("/api/v1/validate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "validation_result" in data
    
    def test_validate_health_check(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
    
    def test_validate_info_endpoint(self, client: TestClient):
        """Test info endpoint."""
        response = client.get("/api/v1/info")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "supported_formats" in data
        assert "GLSL" in data["supported_formats"]
        assert "ISF" in data["supported_formats"]
        assert "MadMapper" in data["supported_formats"]
    
    def test_validate_config_endpoint(self, client: TestClient):
        """Test config endpoint."""
        response = client.get("/api/v1/config")
        
        assert response.status_code == 200
        data = response.json()
        assert "app_name" in data
        assert "app_version" in data
        assert "debug" in data
        assert "log_level" in data
    
    def test_validate_root_endpoint(self, client: TestClient):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert "documentation" in data


@pytest.mark.api
class TestValidationAPIErrorHandling:
    """Test cases for validation API error handling."""
    
    def test_validate_malformed_json(self, client: TestClient):
        """Test validation with malformed JSON."""
        response = client.post(
            "/api/v1/validate",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_validate_wrong_content_type(self, client: TestClient):
        """Test validation with wrong content type."""
        response = client.post(
            "/api/v1/validate",
            data="some data",
            headers={"Content-Type": "text/plain"}
        )
        
        assert response.status_code == 422
    
    def test_validate_missing_content_type(self, client: TestClient):
        """Test validation without content type header."""
        response = client.post("/api/v1/validate", data="{}")
        
        assert response.status_code == 422
    
    def test_validate_unsupported_method(self, client: TestClient):
        """Test validation with unsupported HTTP method."""
        response = client.put("/api/v1/validate", json={})
        
        assert response.status_code == 405
    
    def test_validate_nonexistent_endpoint(self, client: TestClient):
        """Test validation with nonexistent endpoint."""
        response = client.get("/api/v1/nonexistent")
        
        assert response.status_code == 404


@pytest.mark.api
class TestValidationAPIPerformance:
    """Test cases for validation API performance."""
    
    def test_validate_response_time(self, client: TestClient, sample_glsl_shader: str):
        """Test validation response time."""
        import time
        
        request_data = {
            "shader_type": "GLSL",
            "shader_source": sample_glsl_shader,
            "parameters": {"time": 0.0}
        }
        
        start_time = time.time()
        response = client.post("/api/v1/validate", json=request_data)
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 5.0  # Should complete within 5 seconds
    
    def test_validate_concurrent_requests(self, client: TestClient, sample_glsl_shader: str):
        """Test validation with concurrent requests."""
        import threading
        import time
        
        request_data = {
            "shader_type": "GLSL",
            "shader_source": sample_glsl_shader,
            "parameters": {"time": 0.0}
        }
        
        results = []
        errors = []
        
        def make_request():
            try:
                response = client.post("/api/v1/validate", json=request_data)
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Start 5 concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(errors) == 0
        assert len(results) == 5
        assert all(status == 200 for status in results) 