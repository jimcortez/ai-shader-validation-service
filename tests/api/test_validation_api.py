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
            "code": sample_glsl_shader,
            "format": "glsl",
            "target_version": "330",
            "custom_parameters": {"time": 0.0}
        }
        
        response = client.post("/api/v1/validate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "validation_id" in data
        assert "is_valid" in data
        assert "status" in data
        assert "format" in data
        assert "target_version" in data
        assert "errors" in data
        assert "warnings" in data
        assert "created_at" in data
        assert "processing_time_ms" in data
    
    def test_validate_isf_shader_success(self, client: TestClient, sample_isf_shader: dict):
        """Test successful ISF shader validation."""
        request_data = {
            "code": json.dumps(sample_isf_shader),
            "format": "isf",
            "custom_parameters": {"time": 0.0}
        }
        
        response = client.post("/api/v1/validate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "validation_id" in data
        assert "is_valid" in data
        assert "status" in data
        assert "format" in data
        assert "errors" in data
        assert "warnings" in data
    
    def test_validate_madmapper_shader_success(self, client: TestClient, sample_madmapper_shader: str):
        """Test successful MadMapper shader validation."""
        request_data = {
            "code": sample_madmapper_shader,
            "format": "madmapper",
            "custom_parameters": {"time": 0.0}
        }
        
        response = client.post("/api/v1/validate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "validation_id" in data
        assert "is_valid" in data
        assert "status" in data
        assert "format" in data
        assert "errors" in data
        assert "warnings" in data
    
    def test_validate_invalid_shader_type(self, client: TestClient):
        """Test validation with invalid shader type."""
        request_data = {
            "code": "void main() {}",
            "format": "invalid_format",
            "custom_parameters": {}
        }
        
        response = client.post("/api/v1/validate", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_validate_missing_shader_source(self, client: TestClient):
        """Test validation with missing shader source."""
        request_data = {
            "format": "glsl",
            "custom_parameters": {}
        }
        
        response = client.post("/api/v1/validate", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_validate_empty_shader_source(self, client: TestClient):
        """Test validation with empty shader source."""
        request_data = {
            "code": "",
            "format": "glsl",
            "custom_parameters": {}
        }
        
        response = client.post("/api/v1/validate", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
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
            "code": invalid_shader,
            "format": "glsl",
            "target_version": "330",
            "custom_parameters": {"time": 0.0}
        }
        
        response = client.post("/api/v1/validate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["errors"]) > 0
        assert not data["is_valid"]
    
    def test_validate_isf_with_invalid_json(self, client: TestClient):
        """Test ISF validation with invalid JSON."""
        request_data = {
            "code": "{ invalid json }",
            "format": "isf",
            "custom_parameters": {}
        }
        
        response = client.post("/api/v1/validate", json=request_data)
        
        assert response.status_code == 200  # Should validate but find errors
        data = response.json()
        assert len(data["errors"]) > 0
    
    def test_validate_with_large_shader(self, client: TestClient):
        """Test validation with very large shader."""
        large_shader = "void main() { " + "fragColor = vec4(1.0); " * 10000 + "}"
        
        request_data = {
            "code": large_shader,
            "format": "glsl",
            "custom_parameters": {}
        }
        
        response = client.post("/api/v1/validate", json=request_data)
        
        # Should either succeed or return a specific error for large shaders
        assert response.status_code in [200, 413, 422]  # Added 422 as valid response
    
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
            "code": shader_with_special_chars,
            "format": "glsl",
            "target_version": "330",
            "custom_parameters": {"time": 0.0}
        }
        
        response = client.post("/api/v1/validate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "validation_id" in data
        assert "is_valid" in data
    
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
            "code": sample_glsl_shader,
            "format": "glsl",
            "target_version": "330",
            "custom_parameters": {"time": 0.0}
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
            "code": sample_glsl_shader,
            "format": "glsl",
            "target_version": "330",
            "custom_parameters": {"time": 0.0}
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