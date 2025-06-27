"""
Full System Integration Tests

This module contains comprehensive integration tests for the complete
AI Shader Validator system, testing all components working together.
"""

import pytest
import asyncio
import json
import time
from typing import Dict, Any
from fastapi.testclient import TestClient

from src.api.main import app
from src.services.validation_service import get_validation_service
from src.services.visualization_service import get_visualization_service
from src.services.analysis_service import get_analysis_service


@pytest.mark.integration
class TestFullSystemIntegration:
    """Test complete system integration."""
    
    def test_complete_validation_workflow(self, client: TestClient, sample_glsl_shader: str):
        """Test complete validation workflow from API to result."""
        # Step 1: Validate shader
        validation_request = {
            "shader_type": "GLSL",
            "shader_source": sample_glsl_shader,
            "parameters": {"time": 0.0}
        }
        
        response = client.post("/api/v1/validate", json=validation_request)
        assert response.status_code == 200
        
        validation_result = response.json()
        assert "validation_result" in validation_result
        assert "is_valid" in validation_result["validation_result"]
        
        # Step 2: Generate visualization
        visualization_request = {
            "shader_type": "GLSL",
            "shader_source": sample_glsl_shader,
            "width": 256,
            "height": 256,
            "format": "PNG",
            "parameters": {"time": 0.0}
        }
        
        response = client.post("/api/v1/visualize", json=visualization_request)
        assert response.status_code == 200
        
        visualization_result = response.json()
        assert "image_id" in visualization_result
        assert "image_url" in visualization_result
        
        # Step 3: Retrieve generated image
        image_id = visualization_result["image_id"]
        response = client.get(f"/api/v1/images/{image_id}")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        
        # Step 4: Analyze shader
        analysis_request = {
            "shader_type": "GLSL",
            "shader_source": sample_glsl_shader,
            "analysis_types": ["performance", "complexity"]
        }
        
        response = client.post("/api/v1/analyze", json=analysis_request)
        assert response.status_code == 200
        
        analysis_result = response.json()
        assert "analysis_result" in analysis_result
        assert "performance" in analysis_result["analysis_result"]
        assert "complexity" in analysis_result["analysis_result"]
    
    def test_isf_shader_complete_workflow(self, client: TestClient, sample_isf_shader: dict):
        """Test complete ISF shader workflow."""
        # Step 1: Validate ISF shader
        validation_request = {
            "shader_type": "ISF",
            "shader_source": json.dumps(sample_isf_shader),
            "parameters": {"time": 0.0}
        }
        
        response = client.post("/api/v1/validate", json=validation_request)
        assert response.status_code == 200
        
        validation_result = response.json()
        assert validation_result["validation_result"]["is_valid"] == True
        
        # Step 2: Generate ISF visualization
        visualization_request = {
            "shader_type": "ISF",
            "shader_source": json.dumps(sample_isf_shader),
            "width": 256,
            "height": 256,
            "format": "PNG",
            "parameters": {"time": 0.0}
        }
        
        response = client.post("/api/v1/visualize", json=visualization_request)
        assert response.status_code == 200
        
        # Step 3: Analyze ISF shader
        analysis_request = {
            "shader_type": "ISF",
            "shader_source": json.dumps(sample_isf_shader),
            "analysis_types": ["portability", "optimization"]
        }
        
        response = client.post("/api/v1/analyze", json=analysis_request)
        assert response.status_code == 200
    
    def test_madmapper_shader_complete_workflow(self, client: TestClient, sample_madmapper_shader: str):
        """Test complete MadMapper shader workflow."""
        # Step 1: Validate MadMapper shader
        validation_request = {
            "shader_type": "MADMAPPER",
            "shader_source": sample_madmapper_shader,
            "parameters": {"time": 0.0}
        }
        
        response = client.post("/api/v1/validate", json=validation_request)
        assert response.status_code == 200
        
        validation_result = response.json()
        assert validation_result["validation_result"]["is_valid"] == True
        
        # Step 2: Generate MadMapper visualization
        visualization_request = {
            "shader_type": "MADMAPPER",
            "shader_source": sample_madmapper_shader,
            "width": 256,
            "height": 256,
            "format": "PNG",
            "parameters": {"time": 0.0}
        }
        
        response = client.post("/api/v1/visualize", json=visualization_request)
        assert response.status_code == 200
    
    def test_batch_processing_workflow(self, client: TestClient):
        """Test batch processing workflow."""
        # Create multiple shaders for batch processing
        shaders = [
            {
                "id": "shader1",
                "shader_type": "GLSL",
                "shader_source": """
                #version 330 core
                out vec4 fragColor;
                void main() {
                    fragColor = vec4(1.0, 0.0, 0.0, 1.0);
                }
                """
            },
            {
                "id": "shader2",
                "shader_type": "GLSL",
                "shader_source": """
                #version 330 core
                out vec4 fragColor;
                void main() {
                    fragColor = vec4(0.0, 1.0, 0.0, 1.0);
                }
                """
            }
        ]
        
        # Batch validation
        batch_request = {
            "shaders": shaders,
            "options": {
                "parallel_processing": True,
                "include_warnings": True
            }
        }
        
        response = client.post("/api/v1/validate/batch", json=batch_request)
        assert response.status_code == 200
        
        batch_result = response.json()
        assert "results" in batch_result
        assert "summary" in batch_result
        assert batch_result["summary"]["total_shaders"] == 2
        assert batch_result["summary"]["valid_shaders"] == 2
        
        # Batch visualization
        batch_viz_request = {
            "requests": [
                {
                    "id": "req1",
                    "shader_type": "GLSL",
                    "shader_source": shaders[0]["shader_source"],
                    "width": 128,
                    "height": 128
                },
                {
                    "id": "req2",
                    "shader_type": "GLSL",
                    "shader_source": shaders[1]["shader_source"],
                    "width": 128,
                    "height": 128
                }
            ],
            "format": "PNG"
        }
        
        response = client.post("/api/v1/visualize/batch", json=batch_viz_request)
        assert response.status_code == 200
        
        batch_viz_result = response.json()
        assert "results" in batch_viz_result
        assert batch_viz_result["summary"]["total_requests"] == 2
        assert batch_viz_result["summary"]["successful"] == 2
    
    def test_error_handling_workflow(self, client: TestClient):
        """Test error handling workflow."""
        # Test with invalid shader
        invalid_shader = """
        #version 330 core
        out vec4 fragColor;
        void main() {
            fragColor = vec4(1.0, 0.0, 0.0, 1.0  // Missing semicolon
        }
        """
        
        validation_request = {
            "shader_type": "GLSL",
            "shader_source": invalid_shader,
            "parameters": {}
        }
        
        response = client.post("/api/v1/validate", json=validation_request)
        assert response.status_code == 200
        
        validation_result = response.json()
        assert not validation_result["validation_result"]["is_valid"]
        assert len(validation_result["validation_result"]["errors"]) > 0
        
        # Test error visualization
        error_viz_request = {
            "shader_type": "GLSL",
            "shader_source": invalid_shader,
            "errors": validation_result["validation_result"]["errors"]
        }
        
        response = client.post("/api/v1/analyze/errors", json=error_viz_request)
        assert response.status_code == 200
        
        error_result = response.json()
        assert "error_report_id" in error_result
        assert "error_report_url" in error_result
    
    def test_performance_monitoring_workflow(self, client: TestClient, sample_glsl_shader: str):
        """Test performance monitoring workflow."""
        # Perform multiple operations to generate performance data
        for i in range(5):
            validation_request = {
                "shader_type": "GLSL",
                "shader_source": sample_glsl_shader,
                "parameters": {"time": float(i)}
            }
            
            response = client.post("/api/v1/validate", json=validation_request)
            assert response.status_code == 200
        
        # Check performance metrics endpoint
        response = client.get("/api/v1/metrics")
        assert response.status_code == 200
        
        metrics = response.json()
        assert "system_metrics" in metrics
        assert "application_metrics" in metrics
        assert "performance_metrics" in metrics
    
    def test_caching_workflow(self, client: TestClient, sample_glsl_shader: str):
        """Test caching workflow."""
        # First request
        validation_request = {
            "shader_type": "GLSL",
            "shader_source": sample_glsl_shader,
            "parameters": {"time": 0.0}
        }
        
        start_time = time.time()
        response1 = client.post("/api/v1/validate", json=validation_request)
        first_request_time = time.time() - start_time
        
        assert response1.status_code == 200
        
        # Second request (should be cached)
        start_time = time.time()
        response2 = client.post("/api/v1/validate", json=validation_request)
        second_request_time = time.time() - start_time
        
        assert response2.status_code == 200
        
        # Cached request should be faster
        assert second_request_time < first_request_time
        
        # Results should be identical
        result1 = response1.json()
        result2 = response2.json()
        assert result1["validation_result"]["is_valid"] == result2["validation_result"]["is_valid"]
    
    def test_concurrent_requests_workflow(self, client: TestClient, sample_glsl_shader: str):
        """Test concurrent requests handling."""
        import threading
        import queue
        
        results = queue.Queue()
        errors = queue.Queue()
        
        def make_request(request_id):
            try:
                validation_request = {
                    "shader_type": "GLSL",
                    "shader_source": sample_glsl_shader,
                    "parameters": {"time": float(request_id)}
                }
                
                response = client.post("/api/v1/validate", json=validation_request)
                results.put((request_id, response.status_code))
            except Exception as e:
                errors.put((request_id, str(e)))
        
        # Start 10 concurrent requests
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert errors.empty(), f"Errors occurred: {[errors.get() for _ in range(errors.qsize())]}"
        
        successful_requests = 0
        while not results.empty():
            request_id, status_code = results.get()
            if status_code == 200:
                successful_requests += 1
        
        assert successful_requests == 10, f"Only {successful_requests}/10 requests succeeded"
    
    def test_api_endpoints_integration(self, client: TestClient):
        """Test all API endpoints work together."""
        # Test health endpoint
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] == "healthy"
        
        # Test info endpoint
        response = client.get("/api/v1/info")
        assert response.status_code == 200
        info_data = response.json()
        assert "supported_formats" in info_data
        assert "GLSL" in info_data["supported_formats"]
        assert "ISF" in info_data["supported_formats"]
        assert "MadMapper" in info_data["supported_formats"]
        
        # Test config endpoint
        response = client.get("/api/v1/config")
        assert response.status_code == 200
        config_data = response.json()
        assert "app_name" in config_data
        assert "app_version" in config_data
        
        # Test root endpoint
        response = client.get("/")
        assert response.status_code == 200
        root_data = response.json()
        assert "message" in root_data
        assert "version" in root_data
    
    def test_error_recovery_workflow(self, client: TestClient):
        """Test error recovery workflow."""
        # Test with various error conditions
        
        # 1. Invalid shader type
        response = client.post("/api/v1/validate", json={
            "shader_type": "INVALID_TYPE",
            "shader_source": "void main() {}"
        })
        assert response.status_code == 400
        
        # 2. Missing required fields
        response = client.post("/api/v1/validate", json={
            "shader_type": "GLSL"
        })
        assert response.status_code == 422
        
        # 3. Empty shader source
        response = client.post("/api/v1/validate", json={
            "shader_type": "GLSL",
            "shader_source": ""
        })
        assert response.status_code == 400
        
        # 4. Malformed JSON
        response = client.post(
            "/api/v1/validate",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
        
        # 5. Non-existent endpoint
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        
        # Verify system is still healthy after errors
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


@pytest.mark.integration
class TestServiceIntegration:
    """Test service-level integration."""
    
    def test_validation_service_integration(self, validation_service):
        """Test validation service integration."""
        shader_source = """
        #version 330 core
        uniform float time;
        out vec4 fragColor;
        void main() {
            vec2 uv = gl_FragCoord.xy / vec2(512.0, 512.0);
            fragColor = vec4(uv.x, uv.y, sin(time), 1.0);
        }
        """
        
        result = validation_service.validate_shader(
            shader_type="GLSL",
            shader_source=shader_source,
            parameters={"time": 0.0}
        )
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_visualization_service_integration(self, visualization_service, mock_gl_context):
        """Test visualization service integration."""
        shader_source = """
        #version 330 core
        out vec4 fragColor;
        void main() {
            fragColor = vec4(1.0, 0.0, 0.0, 1.0);
        }
        """
        
        result = visualization_service.generate_image(
            shader_type="GLSL",
            shader_source=shader_source,
            width=256,
            height=256,
            format="PNG",
            parameters={}
        )
        
        assert result.image_id is not None
        assert result.width == 256
        assert result.height == 256
        assert result.format == "PNG"
    
    def test_analysis_service_integration(self, analysis_service):
        """Test analysis service integration."""
        shader_source = """
        #version 330 core
        uniform float time;
        out vec4 fragColor;
        void main() {
            vec2 uv = gl_FragCoord.xy / vec2(512.0, 512.0);
            fragColor = vec4(uv.x, uv.y, sin(time), 1.0);
        }
        """
        
        result = analysis_service.analyze_shader(
            shader_type="GLSL",
            shader_source=shader_source,
            analysis_types=["performance", "complexity"]
        )
        
        assert "performance" in result
        assert "complexity" in result
        assert result["performance"]["score"] > 0
        assert result["complexity"]["cyclomatic_complexity"] > 0


@pytest.mark.integration
class TestPerformanceIntegration:
    """Test performance integration."""
    
    def test_system_performance_under_load(self, client: TestClient, sample_glsl_shader: str):
        """Test system performance under load."""
        import threading
        import time
        
        # Measure baseline performance
        start_time = time.time()
        response = client.post("/api/v1/validate", json={
            "shader_type": "GLSL",
            "shader_source": sample_glsl_shader,
            "parameters": {"time": 0.0}
        })
        baseline_time = time.time() - start_time
        
        assert response.status_code == 200
        
        # Perform load test
        results = []
        errors = []
        
        def load_test_request():
            try:
                start = time.time()
                response = client.post("/api/v1/validate", json={
                    "shader_type": "GLSL",
                    "shader_source": sample_glsl_shader,
                    "parameters": {"time": 0.0}
                })
                end = time.time()
                
                if response.status_code == 200:
                    results.append(end - start)
                else:
                    errors.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Start 20 concurrent requests
        threads = []
        for _ in range(20):
            thread = threading.Thread(target=load_test_request)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Analyze results
        assert len(errors) == 0, f"Errors during load test: {errors}"
        assert len(results) == 20, f"Only {len(results)}/20 requests completed"
        
        # Check performance degradation
        avg_response_time = sum(results) / len(results)
        max_response_time = max(results)
        
        # Average response time should not be more than 3x baseline
        assert avg_response_time < baseline_time * 3, f"Average response time {avg_response_time}s exceeds 3x baseline {baseline_time}s"
        
        # Max response time should not be more than 5x baseline
        assert max_response_time < baseline_time * 5, f"Max response time {max_response_time}s exceeds 5x baseline {baseline_time}s"
    
    def test_memory_usage_integration(self, client: TestClient):
        """Test memory usage during operations."""
        # Generate large shader
        large_shader = "void main() { " + "fragColor = vec4(1.0); " * 1000 + "}"
        
        # Perform multiple operations
        for i in range(10):
            response = client.post("/api/v1/validate", json={
                "shader_type": "GLSL",
                "shader_source": large_shader,
                "parameters": {"time": float(i)}
            })
            assert response.status_code == 200
        
        # Check system is still responsive
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy" 