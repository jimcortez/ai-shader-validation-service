"""
Tests for MadMapper validation integration
"""

import pytest
from src.core.parsers.madmapper_parser import MadMapperParser, MadMapperDocument
from src.core.analyzers.madmapper_analyzer import MadMapperAnalyzer
from src.services.validation_service import ValidationService


class TestMadMapperParser:
    """Test MadMapper parser functionality."""
    
    def test_parse_valid_madmapper(self):
        """Test parsing a valid MadMapper shader."""
        madmapper_code = """
        // @name Test Shader
        // @description A test shader
        // @author Test Author
        // @version 1.0.0
        // @category Test

        // @param color color label:"Color" desc:"The color to display"
        // @param intensity float min:0.0 max:2.0 label:"Intensity" desc:"Color intensity multiplier"

        // @input texture inputTexture
        // @output vec4 outputColor

        // FRAGMENT_SHADER
        #version 330
        uniform vec4 color = vec4(1.0, 0.0, 0.0, 1.0);
        uniform float intensity = 1.0;
        
        void main() {
            gl_FragColor = color * intensity;
        }
        """
        
        parser = MadMapperParser()
        result = parser.parse(madmapper_code)
        
        assert isinstance(result, MadMapperDocument)
        assert result.name == "Test Shader"
        assert result.description == "A test shader"
        assert result.author == "Test Author"
        assert result.version == "1.0.0"
        assert result.category == "Test"
        assert len(result.parameters or []) == 2
        assert (result.parameters or [])[0].name == "color"
        assert (result.parameters or [])[0].type.value == "color"
        assert (result.parameters or [])[1].name == "intensity"
        assert (result.parameters or [])[1].type.value == "float"
        assert len(result.inputs or []) == 1
        assert (result.inputs or [])[0].name == "inputTexture"
        assert len(result.outputs or []) == 1
        assert (result.outputs or [])[0].name == "outputColor"
        assert "gl_FragColor = color * intensity" in result.fragment_shader
    
    def test_parse_invalid_madmapper(self):
        """Test parsing invalid MadMapper code."""
        invalid_code = "invalid madmapper code"
        
        parser = MadMapperParser()
        with pytest.raises(ValueError):
            parser.parse(invalid_code)
    
    def test_validate_structure(self):
        """Test MadMapper structure validation."""
        parser = MadMapperParser()
        
        # Valid structure
        valid_code = """
        // @name Test
        // FRAGMENT_SHADER
        void main() { gl_FragColor = vec4(1.0); }
        """
        errors = parser.validate_structure(valid_code)
        assert len(errors) == 0
        
        # Missing required sections
        invalid_code = """
        // @name Test
        // No fragment shader section
        """
        errors = parser.validate_structure(invalid_code)
        assert len(errors) > 0
        assert any("FRAGMENT_SHADER" in error for error in errors)


class TestMadMapperAnalyzer:
    """Test MadMapper analyzer functionality."""
    
    def test_analyze_valid_madmapper(self):
        """Test analyzing a valid MadMapper shader."""
        madmapper_code = """
        // @name Test Shader
        // @description A test shader
        // @author Test Author
        // @version 1.0.0
        // @category Test

        // @param color color label:"Color" desc:"The color to display"
        // @param intensity float min:0.0 max:2.0 label:"Intensity" desc:"Color intensity multiplier"

        // @input texture inputTexture
        // @output vec4 outputColor

        // FRAGMENT_SHADER
        #version 330
        uniform vec4 color = vec4(1.0, 0.0, 0.0, 1.0);
        uniform float intensity = 1.0;
        
        void main() {
            gl_FragColor = color * intensity;
        }
        """
        
        analyzer = MadMapperAnalyzer()
        result = analyzer.analyze(madmapper_code)
        
        assert result["is_valid"] == True
        assert len(result["errors"]) == 0
        assert "parsed_document" in result["metadata"]
    
    def test_analyze_invalid_madmapper(self):
        """Test analyzing an invalid MadMapper shader."""
        madmapper_code = """
        // @param color color
        // No fragment shader section
        """
        
        analyzer = MadMapperAnalyzer()
        result = analyzer.analyze(madmapper_code)
        
        assert result["is_valid"] == False
        assert len(result["errors"]) > 0
    
    def test_analyze_parameter_validation(self):
        """Test parameter validation."""
        madmapper_code = """
        // @name Test Shader
        // FRAGMENT_SHADER
        void main() { gl_FragColor = vec4(1.0); }
        // @param intensity float min:2.0 max:1.0
        """
        
        analyzer = MadMapperAnalyzer()
        result = analyzer.analyze(madmapper_code)
        
        # Should have error for min > max
        assert result["is_valid"] == False
        assert any("Min value greater than max value" in str(error) for error in result["errors"])


class TestMadMapperValidationService:
    """Test MadMapper validation service integration."""
    
    def test_validate_madmapper_shader(self):
        """Test MadMapper validation through the validation service."""
        madmapper_code = """
        // @name Test Shader
        // @description A test shader
        // @author Test Author
        // @version 1.0.0
        // @category Test

        // @param color color label:"Color" desc:"The color to display"
        // @param intensity float min:0.0 max:2.0 label:"Intensity" desc:"Color intensity multiplier"

        // @input texture inputTexture
        // @output vec4 outputColor

        // FRAGMENT_SHADER
        #version 330
        uniform vec4 color = vec4(1.0, 0.0, 0.0, 1.0);
        uniform float intensity = 1.0;
        
        void main() {
            gl_FragColor = color * intensity;
        }
        """
        
        service = ValidationService()
        result = service.validate(madmapper_code, "madmapper")
        
        assert result["is_valid"] == True
        assert result["format"] == "madmapper"
        assert "metadata" in result
        assert result["metadata"]["name"] == "Test Shader"
    
    def test_validate_madmapper_with_glsl_validation(self):
        """Test MadMapper validation including GLSL fragment shader validation."""
        madmapper_code = """
        // @name Test Shader
        // FRAGMENT_SHADER
        #version 330
        uniform vec4 color = vec4(1.0, 0.0, 0.0, 1.0);
        
        void main() {
            gl_FragColor = color;
        }
        """
        
        service = ValidationService()
        result = service.validate(madmapper_code, "madmapper", {
            "enable_quality_analysis": True,
            "enable_portability_analysis": True
        })
        
        assert result["is_valid"] == True
        assert result["format"] == "madmapper"
        # Should have quality metrics from GLSL analysis
        assert "quality_metrics" in result
    
    def test_validate_invalid_madmapper(self):
        """Test validation of invalid MadMapper shader."""
        invalid_madmapper = """
        // @param color color
        // No fragment shader section
        """
        
        service = ValidationService()
        result = service.validate(invalid_madmapper, "madmapper")
        
        assert result["is_valid"] == False
        assert len(result["errors"]) > 0


class TestMadMapperErrorHandling:
    """Test MadMapper error handling and edge cases."""
    
    def test_empty_fragment_shader(self):
        """Test MadMapper with empty fragment shader."""
        madmapper_code = """
        // @name Test Shader
        // FRAGMENT_SHADER
        
        """
        
        analyzer = MadMapperAnalyzer()
        result = analyzer.analyze(madmapper_code)
        
        assert result["is_valid"] == False
        assert any("Fragment shader is empty" in str(error) for error in result["errors"])
    
    def test_duplicate_input_names(self):
        """Test MadMapper with duplicate input names."""
        madmapper_code = """
        // @name Test Shader
        // FRAGMENT_SHADER
        void main() { gl_FragColor = vec4(1.0); }
        // @input texture inputA
        // @input texture inputA
        """
        
        analyzer = MadMapperAnalyzer()
        result = analyzer.analyze(madmapper_code)
        
        assert result["is_valid"] == False
        assert any("Duplicate input name" in str(error) for error in result["errors"])
    
    def test_reserved_parameter_names(self):
        """Test MadMapper with reserved parameter names."""
        madmapper_code = """
        // @name Test Shader
        // FRAGMENT_SHADER
        void main() { gl_FragColor = vec4(1.0); }
        // @param time float
        """
        
        analyzer = MadMapperAnalyzer()
        result = analyzer.analyze(madmapper_code)
        
        # Should have warning for reserved name
        assert any("conflicts with MadMapper reserved name" in str(warning) for warning in result["warnings"])
    
    def test_missing_gl_fragcolor_assignment(self):
        """Test MadMapper fragment shader without gl_FragColor assignment."""
        madmapper_code = """
        // @name Test Shader
        // FRAGMENT_SHADER
        void main() {
            // No gl_FragColor assignment
        }
        """
        
        analyzer = MadMapperAnalyzer()
        result = analyzer.analyze(madmapper_code)
        
        assert result["is_valid"] == False
        assert any("must assign to gl_FragColor" in str(error) for error in result["errors"]) 