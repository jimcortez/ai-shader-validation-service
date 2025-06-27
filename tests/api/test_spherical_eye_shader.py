"""
Tests for SphericalEye ISF Shader Validation

This module contains comprehensive tests for the SphericalEye ISF shader,
ensuring it passes all syntax, semantic, and quality validation checks.
"""

import pytest
import json
from fastapi.testclient import TestClient


@pytest.mark.api
class TestSphericalEyeShader:
    """Test cases for SphericalEye ISF shader validation."""
    
    def test_spherical_eye_isf_validation_success(self, client: TestClient, spherical_eye_shader: str):
        """Test successful validation of the SphericalEye ISF shader."""
        request_data = {
            "code": spherical_eye_shader,
            "format": "isf",
            "custom_parameters": {
                "eyeMovementSpeed": 0.8,
                "irisHue": 0.6,
                "pupilSize": 0.12,
                "reflectionIntensity": 0.9
            }
        }
        
        response = client.post("/api/v1/validate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Print the full response for debugging if the test fails
        if not data.get("is_valid", False):
            print("\nFull API response:")
            import pprint; pprint.pprint(data)
        
        # Check basic response structure
        assert "validation_id" in data
        assert "is_valid" in data
        assert "status" in data
        assert "format" in data
        assert "errors" in data
        assert "warnings" in data
        
        # The shader should be valid
        assert data["is_valid"] is True
        assert data["format"] == "isf"
        
        # Should have no critical errors
        assert len(data["errors"]) == 0
        
        # May have some warnings but should be minimal
        assert len(data["warnings"]) < 10  # Allow some warnings for complex shader
    
    def test_spherical_eye_syntax_validation(self, client: TestClient, spherical_eye_shader: str):
        """Test syntax validation of the SphericalEye shader."""
        request_data = {
            "code": spherical_eye_shader,
            "format": "isf",
            "custom_parameters": {}
        }
        
        response = client.post("/api/v1/validate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check for syntax-specific validation
        assert data["is_valid"] is True
        
        # Should not have syntax errors
        syntax_errors = [error for error in data.get("errors", []) 
                        if "syntax" in error.get("error_code", "").lower()]
        assert len(syntax_errors) == 0
    
    def test_spherical_eye_metadata_extraction(self, client: TestClient, spherical_eye_shader: str):
        """Test metadata extraction from the SphericalEye shader."""
        request_data = {
            "code": spherical_eye_shader,
            "format": "isf",
            "custom_parameters": {}
        }
        
        response = client.post("/api/v1/validate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Debug: print the actual response
        print("\nActual API response keys:", list(data.keys()))
        print("Has metadata:", "metadata" in data)
        
        # Should have metadata
        assert "metadata" in data
        metadata = data["metadata"]
        
        # Check for expected metadata fields
        assert "name" in metadata or "description" in metadata
        assert "author" in metadata or "credit" in metadata
        
        # Should have input parameters
        assert "parameters" in metadata
        parameters = metadata["parameters"]
        assert isinstance(parameters, list)
        assert len(parameters) > 0
        
        # Check for specific expected parameters
        param_names = [param.get("name", "") for param in parameters]
        expected_params = ["eyeMovementSpeed", "irisHue", "pupilSize", "reflectionIntensity"]
        for expected_param in expected_params:
            assert expected_param in param_names
