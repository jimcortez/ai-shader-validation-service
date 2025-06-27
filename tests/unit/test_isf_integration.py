"""
Tests for ISF validation integration
"""

import json
import pytest
from src.core.parsers.isf_parser import ISFParser, ISFDocument
from src.core.analyzers.isf_analyzer import ISFAnalyzer
from src.services.validation_service import ValidationService


class TestISFParser:
    """Test ISF parser functionality."""
    
    def test_parse_valid_isf(self):
        """Test parsing a valid ISF shader."""
        isf_json = """
        {
          "NAME": "Test Shader",
          "DESCRIPTION": "A test shader",
          "AUTHOR": "Test Author",
          "VERSION": "1.0.0",
          "CATEGORIES": ["Test"],
          "INPUTS": [
            {
              "NAME": "color",
              "TYPE": "color",
              "DEFAULT": [1.0, 0.0, 0.0, 1.0]
            }
          ],
          "FRAGMENT_SHADER": "void main() { gl_FragColor = vec4(1.0); }"
        }
        """
        
        parser = ISFParser()
        result = parser.parse(isf_json)
        
        assert isinstance(result, ISFDocument)
        assert result.name == "Test Shader"
        assert result.description == "A test shader"
        assert result.author == "Test Author"
        assert result.version == "1.0.0"
        assert result.categories == ["Test"]
        assert len(result.parameters or []) == 1
        assert (result.parameters or [])[0].name == "color"
        assert (result.parameters or [])[0].type.value == "color"
        assert result.fragment_shader == "void main() { gl_FragColor = vec4(1.0); }"
    
    def test_parse_invalid_json(self):
        """Test parsing invalid JSON."""
        invalid_json = "{ invalid json }"
        
        parser = ISFParser()
        with pytest.raises(ValueError):
            parser.parse(invalid_json)
    
    def test_validate_structure(self):
        """Test ISF structure validation."""
        parser = ISFParser()
        
        # Valid structure
        valid_isf = '{"NAME": "Test", "FRAGMENT_SHADER": "void main() {}"}'
        errors = parser.validate_structure(valid_isf)
        assert len(errors) == 0
        
        # Missing required fields
        invalid_isf = '{"NAME": "Test"}'
        errors = parser.validate_structure(invalid_isf)
        assert len(errors) > 0
        assert any("FRAGMENT_SHADER" in error for error in errors)


class TestISFAnalyzer:
    """Test ISF analyzer functionality."""
    
    def test_analyze_valid_isf(self):
        """Test analyzing a valid ISF shader."""
        isf_json = """
        {
          "NAME": "Test Shader",
          "DESCRIPTION": "A test shader",
          "AUTHOR": "Test Author",
          "VERSION": "1.0.0",
          "CATEGORIES": ["Test"],
          "INPUTS": [
            {
              "NAME": "color",
              "TYPE": "color",
              "DEFAULT": [1.0, 0.0, 0.0, 1.0]
            }
          ],
          "FRAGMENT_SHADER": "void main() { gl_FragColor = vec4(1.0); }"
        }
        """
        
        analyzer = ISFAnalyzer()
        result = analyzer.analyze(isf_json)
        
        assert result["is_valid"] == True
        assert len(result["errors"]) == 0
        assert "parsed_document" in result["metadata"]
    
    def test_analyze_invalid_isf(self):
        """Test analyzing an invalid ISF shader."""
        isf_json = """
        {
          "INPUTS": [
            {
              "NAME": "color",
              "TYPE": "color",
              "DEFAULT": [1.0, 0.0, 0.0, 1.0]
            }
          ]
        }
        """
        
        analyzer = ISFAnalyzer()
        result = analyzer.analyze(isf_json)
        
        assert result["is_valid"] == False
        assert len(result["errors"]) > 0
    
    def test_analyze_parameter_validation(self):
        """Test parameter validation."""
        isf_json = """
        {
          "NAME": "Test Shader",
          "FRAGMENT_SHADER": "void main() { gl_FragColor = vec4(1.0); }",
          "INPUTS": [
            {
              "NAME": "intensity",
              "TYPE": "float",
              "DEFAULT": 1.0,
              "MIN": 2.0,
              "MAX": 1.0
            }
          ]
        }
        """
        
        analyzer = ISFAnalyzer()
        result = analyzer.analyze(isf_json)
        
        # Should have error for min > max
        assert result["is_valid"] == False
        assert any("Min value greater than max value" in str(error) for error in result["errors"])


class TestISFValidationService:
    """Test ISF validation service integration."""
    
    def test_validate_isf_shader(self):
        """Test ISF validation through the validation service."""
        isf_json = """
        {
          "NAME": "Test Shader",
          "DESCRIPTION": "A test shader",
          "AUTHOR": "Test Author",
          "VERSION": "1.0.0",
          "CATEGORIES": ["Test"],
          "INPUTS": [
            {
              "NAME": "color",
              "TYPE": "color",
              "DEFAULT": [1.0, 0.0, 0.0, 1.0]
            }
          ],
          "FRAGMENT_SHADER": "#version 330\\nvoid main() { gl_FragColor = vec4(1.0); }"
        }
        """
        
        service = ValidationService()
        result = service.validate(isf_json, "isf")
        
        assert result["is_valid"] == True
        assert result["format"] == "isf"
        assert "metadata" in result
        assert result["metadata"]["name"] == "Test Shader"
    
    def test_validate_isf_with_glsl_validation(self):
        """Test ISF validation including GLSL fragment shader validation."""
        isf_json = """
        {
          "NAME": "Test Shader",
          "FRAGMENT_SHADER": "#version 330\\nvoid main() { gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0); }"
        }
        """
        
        service = ValidationService()
        result = service.validate(isf_json, "isf", {
            "enable_quality_analysis": True,
            "enable_portability_analysis": True
        })
        
        assert result["is_valid"] == True
        assert result["format"] == "isf"
        # Should have quality metrics from GLSL analysis
        assert "quality_metrics" in result
    
    def test_validate_invalid_isf(self):
        """Test validation of invalid ISF shader."""
        invalid_isf = """
        {
          "INPUTS": [
            {
              "NAME": "color",
              "TYPE": "color",
              "DEFAULT": [1.0, 0.0, 0.0, 1.0]
            }
          ]
        }
        """
        
        service = ValidationService()
        result = service.validate(invalid_isf, "isf")
        
        assert result["is_valid"] == False
        assert len(result["errors"]) > 0


class TestISFErrorHandling:
    """Test ISF error handling and edge cases."""
    
    def test_empty_fragment_shader(self):
        """Test ISF with empty fragment shader."""
        isf_json = """
        {
          "NAME": "Test Shader",
          "FRAGMENT_SHADER": ""
        }
        """
        
        analyzer = ISFAnalyzer()
        result = analyzer.analyze(isf_json)
        
        assert result["is_valid"] == False
        assert any("Fragment shader is empty" in str(error) for error in result["errors"])
    
    def test_duplicate_target_names(self):
        """Test ISF with duplicate render target names."""
        isf_json = """
        {
          "NAME": "Test Shader",
          "FRAGMENT_SHADER": "void main() { gl_FragColor = vec4(1.0); }",
          "PASSES": [
            {"TARGET": "bufferA"},
            {"TARGET": "bufferA"}
          ]
        }
        """
        
        analyzer = ISFAnalyzer()
        result = analyzer.analyze(isf_json)
        
        assert result["is_valid"] == False
        assert any("Duplicate render target" in str(error) for error in result["errors"])
    
    def test_reserved_parameter_names(self):
        """Test ISF with reserved parameter names."""
        isf_json = """
        {
          "NAME": "Test Shader",
          "FRAGMENT_SHADER": "void main() { gl_FragColor = vec4(1.0); }",
          "INPUTS": [
            {
              "NAME": "time",
              "TYPE": "float",
              "DEFAULT": 0.0
            }
          ]
        }
        """
        
        analyzer = ISFAnalyzer()
        result = analyzer.analyze(isf_json)
        
        # Should have warning for reserved name
        assert any("conflicts with ISF reserved name" in str(warning) for warning in result["warnings"]) 